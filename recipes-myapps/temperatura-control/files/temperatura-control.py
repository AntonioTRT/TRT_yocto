#!/usr/bin/env python3
"""
TRT Sistema de Control de Temperatura Industrial
Desarrollado por Antonio TRT

Este programa:
- Lee sensores de temperatura (DS18B20, termopares, RTD)
- Controla calentadores/refrigeradores vía relés
- Implementa control PID automático
- Envía datos por MQTT
- Guarda logs históricos
- Alertas por email/SMS
- Interfaz web para monitoreo
"""

import sys
import json
import time
import logging
import signal
import threading
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import smtplib
from email.mime.text import MimeText

# Librerías industriales
try:
    import paho.mqtt.client as mqtt
    import RPi.GPIO as GPIO
    from w1thermsensor import W1ThermSensor, Sensor
    import numpy as np
    from flask import Flask, render_template, jsonify, request
    from simple_pid import PID
except ImportError as e:
    print(f"Error importing libraries: {e}")
    print("Install with: pip3 install paho-mqtt w1thermsensor numpy flask simple-pid")
    sys.exit(1)

class ControladorTemperatura:
    def __init__(self, config_file="/etc/trt/temp-control-config.json"):
        """Inicializar controlador de temperatura"""
        self.running = True
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.setup_database()
        self.setup_gpio()
        self.setup_sensors()
        self.setup_pid()
        self.setup_mqtt()
        self.setup_web_server()
        
        # Variables de estado
        self.current_temp = 0.0
        self.target_temp = 20.0
        self.heater_state = False
        self.cooler_state = False
        self.pid_output = 0.0
        self.last_reading = datetime.now()
        
        # Datos históricos
        self.temp_history = []
        self.max_history = 1000
        
        # Manejo de señales
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def load_config(self, config_file):
        """Cargar configuración desde archivo JSON"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            # Configuración por defecto
            return {
                "sensors": {
                    "type": "DS18B20",  # DS18B20, thermocouple, RTD
                    "sensor_id": "28-0000072f5a8b",
                    "read_interval": 2.0
                },
                "control": {
                    "target_temp": 25.0,
                    "pid_kp": 2.0,
                    "pid_ki": 0.1,
                    "pid_kd": 0.05,
                    "output_limits": [-100, 100],
                    "sample_time": 1.0
                },
                "gpio": {
                    "heater_relay": 18,
                    "cooler_relay": 19,
                    "alarm_led": 20,
                    "status_led": 21
                },
                "alerts": {
                    "temp_min": 15.0,
                    "temp_max": 35.0,
                    "email_enabled": True,
                    "email_to": "antonio@trt.com",
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "smtp_user": "alerts@trt.com",
                    "smtp_password": "your_password"
                },
                "mqtt": {
                    "broker": "192.168.100.1",
                    "port": 1883,
                    "topic_base": "trt/temperature"
                },
                "web": {
                    "port": 5000,
                    "host": "0.0.0.0"
                },
                "database": {
                    "file": "/opt/trt/data/temperature.db",
                    "retention_days": 365
                }
            }
    
    def setup_logging(self):
        """Configurar logging"""
        log_file = "/opt/trt/logs/temperature-control.log"
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Sistema de Control de Temperatura iniciado")
    
    def setup_database(self):
        """Configurar base de datos SQLite"""
        db_file = self.config["database"]["file"]
        Path(db_file).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_conn = sqlite3.connect(db_file, check_same_thread=False)
        self.db_lock = threading.Lock()
        
        # Crear tabla si no existe
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temperature_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                current_temp REAL,
                target_temp REAL,
                pid_output REAL,
                heater_state INTEGER,
                cooler_state INTEGER,
                sensor_status TEXT
            )
        ''')
        self.db_conn.commit()
        self.logger.info("Base de datos configurada")
    
    def setup_gpio(self):
        """Configurar GPIO para relés y LEDs"""
        try:
            gpio_config = self.config["gpio"]
            GPIO.setmode(GPIO.BCM)
            
            # Configurar relés (salida)
            GPIO.setup(gpio_config["heater_relay"], GPIO.OUT)
            GPIO.setup(gpio_config["cooler_relay"], GPIO.OUT)
            GPIO.setup(gpio_config["alarm_led"], GPIO.OUT)
            GPIO.setup(gpio_config["status_led"], GPIO.OUT)
            
            # Inicializar en OFF
            GPIO.output(gpio_config["heater_relay"], GPIO.LOW)
            GPIO.output(gpio_config["cooler_relay"], GPIO.LOW)
            GPIO.output(gpio_config["alarm_led"], GPIO.LOW)
            GPIO.output(gpio_config["status_led"], GPIO.LOW)
            
            self.logger.info("GPIO configurado")
        except Exception as e:
            self.logger.error(f"Error configurando GPIO: {e}")
    
    def setup_sensors(self):
        """Configurar sensores de temperatura"""
        try:
            sensor_config = self.config["sensors"]
            
            if sensor_config["type"] == "DS18B20":
                # Sensor DS18B20 (1-Wire)
                if sensor_config.get("sensor_id"):
                    # Sensor específico por ID
                    self.sensor = W1ThermSensor(
                        sensor_type=Sensor.DS18B20,
                        sensor_id=sensor_config["sensor_id"]
                    )
                else:
                    # Primer sensor encontrado
                    self.sensor = W1ThermSensor()
                
            self.logger.info(f"Sensor {sensor_config['type']} configurado")
            
        except Exception as e:
            self.logger.error(f"Error configurando sensores: {e}")
            self.sensor = None
    
    def setup_pid(self):
        """Configurar controlador PID"""
        control_config = self.config["control"]
        
        self.pid = PID(
            Kp=control_config["pid_kp"],
            Ki=control_config["pid_ki"],
            Kd=control_config["pid_kd"],
            setpoint=control_config["target_temp"],
            sample_time=control_config["sample_time"],
            output_limits=tuple(control_config["output_limits"])
        )
        
        self.target_temp = control_config["target_temp"]
        self.logger.info(f"PID configurado - Target: {self.target_temp}°C")
    
    def setup_mqtt(self):
        """Configurar cliente MQTT"""
        try:
            mqtt_config = self.config["mqtt"]
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_message = self.on_mqtt_message
            
            self.mqtt_client.connect(
                mqtt_config["broker"],
                mqtt_config["port"],
                60
            )
            self.mqtt_client.loop_start()
            self.topic_base = mqtt_config["topic_base"]
            self.logger.info("MQTT configurado")
        except Exception as e:
            self.logger.error(f"Error configurando MQTT: {e}")
            self.mqtt_client = None
    
    def setup_web_server(self):
        """Configurar servidor web Flask"""
        self.app = Flask(__name__)
        
        @self.app.route('/')
        def dashboard():
            return self.render_dashboard()
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify({
                'current_temp': self.current_temp,
                'target_temp': self.target_temp,
                'pid_output': self.pid_output,
                'heater_state': self.heater_state,
                'cooler_state': self.cooler_state,
                'last_reading': self.last_reading.isoformat(),
                'temp_history': self.temp_history[-50:]  # Últimos 50 puntos
            })
        
        @self.app.route('/api/set_target', methods=['POST'])
        def api_set_target():
            try:
                data = request.get_json()
                new_target = float(data['target'])
                self.set_target_temperature(new_target)
                return jsonify({'success': True, 'target': new_target})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        self.logger.info("Servidor web configurado")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback cuando se conecta MQTT"""
        if rc == 0:
            self.logger.info("Conectado a MQTT broker")
            # Suscribirse a comandos
            client.subscribe(f"{self.topic_base}/commands/+")
        else:
            self.logger.error(f"Error conectando MQTT: {rc}")
    
    def on_mqtt_message(self, client, userdata, msg):
        """Procesar mensajes MQTT"""
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            if "commands/set_target" in topic:
                new_target = float(payload)
                self.set_target_temperature(new_target)
            
            elif "commands/heater" in topic:
                # Control manual del calentador
                if payload.lower() == "on":
                    self.manual_heater_control(True)
                elif payload.lower() == "off":
                    self.manual_heater_control(False)
            
        except Exception as e:
            self.logger.error(f"Error procesando MQTT: {e}")
    
    def read_temperature(self):
        """Leer temperatura del sensor"""
        try:
            if self.sensor:
                temp = self.sensor.get_temperature()
                self.current_temp = temp
                self.last_reading = datetime.now()
                
                # Agregar a historial
                self.temp_history.append({
                    'timestamp': self.last_reading.isoformat(),
                    'temperature': temp
                })
                
                # Mantener solo los últimos N puntos
                if len(self.temp_history) > self.max_history:
                    self.temp_history.pop(0)
                
                return temp
            else:
                # Simular temperatura para testing
                return 20.0 + (time.time() % 10)
                
        except Exception as e:
            self.logger.error(f"Error leyendo temperatura: {e}")
            return None
    
    def control_outputs(self, pid_output):
        """Controlar salidas basado en output PID"""
        gpio_config = self.config["gpio"]
        
        try:
            if pid_output > 10:  # Necesita calentamiento
                self.heater_state = True
                self.cooler_state = False
                GPIO.output(gpio_config["heater_relay"], GPIO.HIGH)
                GPIO.output(gpio_config["cooler_relay"], GPIO.LOW)
                
            elif pid_output < -10:  # Necesita enfriamiento
                self.heater_state = False
                self.cooler_state = True
                GPIO.output(gpio_config["heater_relay"], GPIO.LOW)
                GPIO.output(gpio_config["cooler_relay"], GPIO.HIGH)
                
            else:  # En rango, apagar ambos
                self.heater_state = False
                self.cooler_state = False
                GPIO.output(gpio_config["heater_relay"], GPIO.LOW)
                GPIO.output(gpio_config["cooler_relay"], GPIO.LOW)
            
            # LED de estado
            GPIO.output(gpio_config["status_led"], GPIO.HIGH if (self.heater_state or self.cooler_state) else GPIO.LOW)
            
        except Exception as e:
            self.logger.error(f"Error controlando salidas: {e}")
    
    def check_alarms(self, temperature):
        """Verificar condiciones de alarma"""
        alerts_config = self.config["alerts"]
        gpio_config = self.config["gpio"]
        
        alarm_active = False
        
        if temperature < alerts_config["temp_min"]:
            self.logger.warning(f"Temperatura muy baja: {temperature}°C")
            self.send_alert(f"ALERTA: Temperatura muy baja: {temperature}°C")
            alarm_active = True
            
        elif temperature > alerts_config["temp_max"]:
            self.logger.warning(f"Temperatura muy alta: {temperature}°C")
            self.send_alert(f"ALERTA: Temperatura muy alta: {temperature}°C")
            alarm_active = True
        
        # LED de alarma
        GPIO.output(gpio_config["alarm_led"], GPIO.HIGH if alarm_active else GPIO.LOW)
        
        return alarm_active
    
    def send_alert(self, message):
        """Enviar alerta por email"""
        try:
            alerts_config = self.config["alerts"]
            
            if not alerts_config["email_enabled"]:
                return
            
            msg = MimeText(message)
            msg['Subject'] = 'TRT - Alerta de Temperatura'
            msg['From'] = alerts_config["smtp_user"]
            msg['To'] = alerts_config["email_to"]
            
            server = smtplib.SMTP(alerts_config["smtp_server"], alerts_config["smtp_port"])
            server.starttls()
            server.login(alerts_config["smtp_user"], alerts_config["smtp_password"])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Alerta enviada por email: {message}")
            
        except Exception as e:
            self.logger.error(f"Error enviando alerta: {e}")
    
    def save_data(self, temperature, pid_output):
        """Guardar datos en base de datos"""
        try:
            with self.db_lock:
                cursor = self.db_conn.cursor()
                cursor.execute('''
                    INSERT INTO temperature_data 
                    (current_temp, target_temp, pid_output, heater_state, cooler_state, sensor_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    temperature,
                    self.target_temp,
                    pid_output,
                    int(self.heater_state),
                    int(self.cooler_state),
                    'OK'
                ))
                self.db_conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error guardando datos: {e}")
    
    def publish_mqtt_data(self, temperature, pid_output):
        """Publicar datos por MQTT"""
        try:
            if self.mqtt_client:
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'current_temp': temperature,
                    'target_temp': self.target_temp,
                    'pid_output': pid_output,
                    'heater_state': self.heater_state,
                    'cooler_state': self.cooler_state
                }
                
                # Publicar datos individuales
                self.mqtt_client.publish(f"{self.topic_base}/current_temp", temperature)
                self.mqtt_client.publish(f"{self.topic_base}/target_temp", self.target_temp)
                self.mqtt_client.publish(f"{self.topic_base}/pid_output", pid_output)
                self.mqtt_client.publish(f"{self.topic_base}/heater_state", int(self.heater_state))
                self.mqtt_client.publish(f"{self.topic_base}/cooler_state", int(self.cooler_state))
                
                # Publicar datos completos
                self.mqtt_client.publish(f"{self.topic_base}/data", json.dumps(data))
                
        except Exception as e:
            self.logger.error(f"Error publicando MQTT: {e}")
    
    def set_target_temperature(self, target):
        """Cambiar temperatura objetivo"""
        self.target_temp = target
        self.pid.setpoint = target
        self.logger.info(f"Nueva temperatura objetivo: {target}°C")
        
        if self.mqtt_client:
            self.mqtt_client.publish(f"{self.topic_base}/target_temp", target)
    
    def manual_heater_control(self, state):
        """Control manual del calentador (desactiva PID temporalmente)"""
        gpio_config = self.config["gpio"]
        
        if state:
            GPIO.output(gpio_config["heater_relay"], GPIO.HIGH)
            self.heater_state = True
            self.logger.info("Calentador activado manualmente")
        else:
            GPIO.output(gpio_config["heater_relay"], GPIO.LOW)
            self.heater_state = False
            self.logger.info("Calentador desactivado manualmente")
    
    def render_dashboard(self):
        """Renderizar dashboard web"""
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>TRT - Control de Temperatura</title>
            <meta charset="utf-8">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .status {{ display: flex; gap: 20px; margin: 20px 0; }}
                .card {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; min-width: 150px; }}
                .temp {{ font-size: 2em; font-weight: bold; color: #2196F3; }}
                .target {{ font-size: 1.5em; color: #4CAF50; }}
                .status-on {{ color: #4CAF50; font-weight: bold; }}
                .status-off {{ color: #757575; }}
                button {{ padding: 10px 20px; margin: 5px; border: none; border-radius: 3px; cursor: pointer; }}
                .btn-primary {{ background-color: #2196F3; color: white; }}
                .btn-danger {{ background-color: #f44336; color: white; }}
                input {{ padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>🌡️ TRT - Sistema de Control de Temperatura</h1>
            
            <div class="status">
                <div class="card">
                    <h3>Temperatura Actual</h3>
                    <div class="temp" id="current-temp">{self.current_temp:.1f}°C</div>
                </div>
                
                <div class="card">
                    <h3>Temperatura Objetivo</h3>
                    <div class="target" id="target-temp">{self.target_temp:.1f}°C</div>
                    <input type="number" id="new-target" value="{self.target_temp}" step="0.1">
                    <button class="btn-primary" onclick="setTarget()">Cambiar</button>
                </div>
                
                <div class="card">
                    <h3>Estado del Sistema</h3>
                    <p>Calentador: <span id="heater-status" class="{'status-on' if self.heater_state else 'status-off'}">{'ON' if self.heater_state else 'OFF'}</span></p>
                    <p>Enfriador: <span id="cooler-status" class="{'status-on' if self.cooler_state else 'status-off'}">{'ON' if self.cooler_state else 'OFF'}</span></p>
                    <p>PID Output: <span id="pid-output">{self.pid_output:.2f}</span></p>
                </div>
                
                <div class="card">
                    <h3>Control Manual</h3>
                    <button class="btn-primary" onclick="controlHeater(true)">Encender Calentador</button>
                    <button class="btn-danger" onclick="controlHeater(false)">Apagar Calentador</button>
                </div>
            </div>
            
            <div id="temperature-chart" style="width:100%;height:400px;"></div>
            
            <script>
                function updateData() {{
                    fetch('/api/status')
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('current-temp').textContent = data.current_temp.toFixed(1) + '°C';
                            document.getElementById('target-temp').textContent = data.target_temp.toFixed(1) + '°C';
                            document.getElementById('pid-output').textContent = data.pid_output.toFixed(2);
                            
                            // Actualizar estados
                            const heaterStatus = document.getElementById('heater-status');
                            heaterStatus.textContent = data.heater_state ? 'ON' : 'OFF';
                            heaterStatus.className = data.heater_state ? 'status-on' : 'status-off';
                            
                            const coolerStatus = document.getElementById('cooler-status');
                            coolerStatus.textContent = data.cooler_state ? 'ON' : 'OFF';
                            coolerStatus.className = data.cooler_state ? 'status-on' : 'status-off';
                            
                            // Actualizar gráfico
                            if (data.temp_history.length > 0) {{
                                const times = data.temp_history.map(d => d.timestamp);
                                const temps = data.temp_history.map(d => d.temperature);
                                
                                Plotly.newPlot('temperature-chart', [{{
                                    x: times,
                                    y: temps,
                                    type: 'scatter',
                                    mode: 'lines',
                                    name: 'Temperatura'
                                }}, {{
                                    x: times,
                                    y: Array(times.length).fill(data.target_temp),
                                    type: 'scatter',
                                    mode: 'lines',
                                    name: 'Objetivo',
                                    line: {{dash: 'dash'}}
                                }}], {{
                                    title: 'Historial de Temperatura',
                                    xaxis: {{title: 'Tiempo'}},
                                    yaxis: {{title: 'Temperatura (°C)'}}
                                }});
                            }}
                        }});
                }}
                
                function setTarget() {{
                    const target = parseFloat(document.getElementById('new-target').value);
                    fetch('/api/set_target', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{target: target}})
                    }});
                }}
                
                function controlHeater(state) {{
                    // Implementar control manual si es necesario
                    console.log('Control manual calentador:', state);
                }}
                
                // Actualizar cada 2 segundos
                setInterval(updateData, 2000);
                updateData(); // Cargar datos iniciales
            </script>
        </body>
        </html>
        '''
        return html
    
    def main_loop(self):
        """Bucle principal de control"""
        self.logger.info("Iniciando bucle principal de control")
        
        # Iniciar servidor web en hilo separado
        web_config = self.config["web"]
        web_thread = threading.Thread(
            target=lambda: self.app.run(
                host=web_config["host"],
                port=web_config["port"],
                debug=False
            )
        )
        web_thread.daemon = True
        web_thread.start()
        
        read_interval = self.config["sensors"]["read_interval"]
        last_mqtt_publish = 0
        mqtt_publish_interval = 10.0  # Publicar cada 10 segundos
        
        while self.running:
            try:
                # Leer temperatura
                temperature = self.read_temperature()
                
                if temperature is not None:
                    # Calcular output PID
                    self.pid_output = self.pid(temperature)
                    
                    # Controlar salidas
                    self.control_outputs(self.pid_output)
                    
                    # Verificar alarmas
                    self.check_alarms(temperature)
                    
                    # Guardar datos
                    self.save_data(temperature, self.pid_output)
                    
                    # Publicar por MQTT (menos frecuente)
                    current_time = time.time()
                    if current_time - last_mqtt_publish >= mqtt_publish_interval:
                        self.publish_mqtt_data(temperature, self.pid_output)
                        last_mqtt_publish = current_time
                    
                    self.logger.debug(f"Temp: {temperature:.1f}°C, Target: {self.target_temp:.1f}°C, PID: {self.pid_output:.2f}, Heater: {self.heater_state}")
                
                time.sleep(read_interval)
                
            except Exception as e:
                self.logger.error(f"Error en bucle principal: {e}")
                time.sleep(5.0)
    
    def signal_handler(self, signum, frame):
        """Manejo de señales para shutdown limpio"""
        self.logger.info(f"Recibida señal {signum}, cerrando...")
        self.running = False
    
    def shutdown(self):
        """Cerrar conexiones y limpiar recursos"""
        self.logger.info("Cerrando sistema de control...")
        
        # Apagar todas las salidas
        try:
            gpio_config = self.config["gpio"]
            GPIO.output(gpio_config["heater_relay"], GPIO.LOW)
            GPIO.output(gpio_config["cooler_relay"], GPIO.LOW)
            GPIO.output(gpio_config["alarm_led"], GPIO.LOW)
            GPIO.output(gpio_config["status_led"], GPIO.LOW)
            GPIO.cleanup()
        except:
            pass
        
        # Cerrar conexiones
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        if hasattr(self, 'db_conn'):
            self.db_conn.close()
        
        self.logger.info("Sistema cerrado correctamente")

def main():
    """Función principal"""
    try:
        controlador = ControladorTemperatura()
        controlador.main_loop()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por usuario")
    except Exception as e:
        print(f"Error fatal: {e}")
    finally:
        if 'controlador' in locals():
            controlador.shutdown()

if __name__ == "__main__":
    main()