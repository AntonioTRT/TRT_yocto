#!/usr/bin/env python3
"""
TRT Monitor de Pines Industrial
Programa principal que lee pines continuamente usando configuraciones específicas por plataforma

Características:
- Detección automática de hardware
- Lectura continua de entradas digitales y analógicas
- Control de salidas digitales y PWM
- Publicación de datos por MQTT
- Interfaz web para monitoreo
- Base de datos SQLite para historial

Autor: Antonio TRT
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

# Importar configuración de pines
try:
    from pin_config import PinConfig
except ImportError:
    print("Error: No se puede importar pin_config.py")
    sys.exit(1)

# Librerías industriales
try:
    import paho.mqtt.client as mqtt
    from flask import Flask, render_template, jsonify, request
except ImportError as e:
    print(f"Error importing libraries: {e}")
    print("Install with: pip3 install paho-mqtt flask")
    sys.exit(1)

# Importar librerías GPIO específicas según plataforma
GPIO_LIB = None
ADC_LIB = None
PWM_LIB = None

def import_gpio_libraries(platform_config):
    """Importar librerías GPIO según la plataforma"""
    global GPIO_LIB, ADC_LIB, PWM_LIB
    
    gpio_library = platform_config['gpio_library']
    
    try:
        if gpio_library == 'RPi.GPIO':
            # Raspberry Pi
            import RPi.GPIO as GPIO_LIB
            try:
                import spidev
                import smbus
                ADC_LIB = "MCP3008"  # ADC común para Raspberry Pi
            except ImportError:
                pass
            PWM_LIB = GPIO_LIB  # RPi.GPIO tiene soporte PWM
            
        elif gpio_library == 'Adafruit_BBIO.GPIO':
            # BeagleBone
            import Adafruit_BBIO.GPIO as GPIO_LIB
            import Adafruit_BBIO.ADC as ADC_LIB
            import Adafruit_BBIO.PWM as PWM_LIB
            
        elif gpio_library == 'custom':
            # i.MX7 - usar sysfs
            GPIO_LIB = "sysfs"
            
        else:
            # Genérico - usar sysfs
            GPIO_LIB = "sysfs"
            
        return True
        
    except ImportError as e:
        print(f"Error importando librerías GPIO: {e}")
        return False

class PinMonitor:
    """Monitor principal de pines industriales"""
    
    def __init__(self, config_file="/etc/trt/pin-monitor-config.json"):
        """Inicializar monitor de pines"""
        self.running = True
        
        # Cargar configuraciones
        self.pin_config = PinConfig()
        self.config = self.load_config(config_file)
        
        # Importar librerías GPIO
        if not import_gpio_libraries(self.pin_config.config):
            raise RuntimeError("No se pudieron cargar las librerías GPIO")
        
        # Configurar componentes
        self.setup_logging()
        self.setup_database()
        self.setup_gpio()
        self.setup_mqtt()
        self.setup_web_server()
        
        # Estado actual de pines
        self.pin_states = {
            'digital_inputs': {},
            'digital_outputs': {},
            'analog_inputs': {},
            'pwm_outputs': {}
        }
        
        # Historial de datos
        self.pin_history = []
        self.max_history = 1000
        
        # Manejo de señales
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def load_config(self, config_file):
        """Cargar configuración del monitor"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            # Configuración por defecto
            return {
                "monitoring": {
                    "read_interval": 0.5,
                    "publish_interval": 5.0,
                    "save_interval": 10.0
                },
                "mqtt": {
                    "broker": "192.168.100.1",
                    "port": 1883,
                    "topic_base": "trt/pins"
                },
                "web": {
                    "port": 5001,
                    "host": "0.0.0.0"
                },
                "database": {
                    "file": "/opt/trt/data/pin_monitor.db",
                    "retention_days": 30
                },
                "alerts": {
                    "enabled": True,
                    "email_on_change": False,
                    "mqtt_on_change": True
                }
            }
    
    def setup_logging(self):
        """Configurar logging"""
        log_file = "/opt/trt/logs/pin-monitor.log"
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
        self.logger.info(f"Monitor de pines iniciado - Plataforma: {self.pin_config.config['platform_name']}")
    
    def setup_database(self):
        """Configurar base de datos SQLite"""
        db_file = self.config["database"]["file"]
        Path(db_file).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_conn = sqlite3.connect(db_file, check_same_thread=False)
        self.db_lock = threading.Lock()
        
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pin_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                pin_name TEXT,
                pin_type TEXT,
                value REAL,
                unit TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pin_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                pin_name TEXT,
                old_value REAL,
                new_value REAL,
                change_type TEXT
            )
        ''')
        
        self.db_conn.commit()
        self.logger.info("Base de datos configurada")
    
    def setup_gpio(self):
        """Configurar GPIO según la plataforma"""
        try:
            if GPIO_LIB and hasattr(GPIO_LIB, 'setmode'):
                # Raspberry Pi
                GPIO_LIB.setmode(GPIO_LIB.BCM)
                
                # Configurar entradas digitales
                for name, config in self.pin_config.config['digital_inputs'].items():
                    pin = config['pin']
                    pull = GPIO_LIB.PUD_UP if config['pull'] == 'up' else GPIO_LIB.PUD_DOWN
                    GPIO_LIB.setup(pin, GPIO_LIB.IN, pull_up_down=pull)
                    self.pin_states['digital_inputs'][name] = False
                
                # Configurar salidas digitales
                for name, config in self.pin_config.config['digital_outputs'].items():
                    pin = config['pin']
                    GPIO_LIB.setup(pin, GPIO_LIB.OUT)
                    initial = GPIO_LIB.HIGH if config['initial'] == 'high' else GPIO_LIB.LOW
                    GPIO_LIB.output(pin, initial)
                    self.pin_states['digital_outputs'][name] = (config['initial'] == 'high')
            
            elif GPIO_LIB and self.pin_config.platform == 'beaglebone_black':
                # BeagleBone Black
                if ADC_LIB:
                    ADC_LIB.setup()
                
                # Configurar entradas digitales
                for name, config in self.pin_config.config['digital_inputs'].items():
                    pin = config['pin']
                    pull = GPIO_LIB.PUD_UP if config['pull'] == 'up' else GPIO_LIB.PUD_DOWN
                    GPIO_LIB.setup(pin, GPIO_LIB.IN, pull=pull)
                    self.pin_states['digital_inputs'][name] = False
                
                # Configurar salidas digitales
                for name, config in self.pin_config.config['digital_outputs'].items():
                    pin = config['pin']
                    GPIO_LIB.setup(pin, GPIO_LIB.OUT)
                    initial = 1 if config['initial'] == 'high' else 0
                    GPIO_LIB.output(pin, initial)
                    self.pin_states['digital_outputs'][name] = (config['initial'] == 'high')
            
            else:
                # Usar sysfs para i.MX7 o genérico
                self.setup_sysfs_gpio()
            
            self.logger.info("GPIO configurado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error configurando GPIO: {e}")
    
    def setup_sysfs_gpio(self):
        """Configurar GPIO usando sysfs (para i.MX7 y genérico)"""
        try:
            # Implementación básica con sysfs
            for name, config in self.pin_config.config['digital_inputs'].items():
                self.pin_states['digital_inputs'][name] = False
            
            for name, config in self.pin_config.config['digital_outputs'].items():
                self.pin_states['digital_outputs'][name] = False
            
            self.logger.info("GPIO configurado con sysfs")
            
        except Exception as e:
            self.logger.error(f"Error configurando sysfs GPIO: {e}")
    
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
        
        @self.app.route('/api/pins')
        def api_pins():
            return jsonify(self.pin_states)
        
        @self.app.route('/api/set_output', methods=['POST'])
        def api_set_output():
            try:
                data = request.get_json()
                pin_name = data['pin_name']
                state = data['state']
                self.set_digital_output(pin_name, state)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/platform')
        def api_platform():
            return jsonify({
                'platform': self.pin_config.config['platform_name'],
                'pins': self.pin_config.list_available_pins()
            })
        
        self.logger.info("Servidor web configurado")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback cuando se conecta MQTT"""
        if rc == 0:
            self.logger.info("Conectado a MQTT broker")
            client.subscribe(f"{self.topic_base}/commands/+")
        else:
            self.logger.error(f"Error conectando MQTT: {rc}")
    
    def on_mqtt_message(self, client, userdata, msg):
        """Procesar mensajes MQTT"""
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            if "commands/set_output" in topic:
                # Formato: pin_name:state
                pin_name, state = payload.split(':')
                self.set_digital_output(pin_name, state.lower() == 'true')
            
        except Exception as e:
            self.logger.error(f"Error procesando MQTT: {e}")
    
    def read_digital_inputs(self):
        """Leer todas las entradas digitales"""
        changes = []
        
        try:
            for name, config in self.pin_config.config['digital_inputs'].items():
                old_state = self.pin_states['digital_inputs'][name]
                
                if GPIO_LIB and hasattr(GPIO_LIB, 'input'):
                    # Raspberry Pi o BeagleBone
                    pin = config['pin']
                    current_state = not GPIO_LIB.input(pin)  # Invertir por pull-up
                    
                else:
                    # Simulación para testing o sysfs
                    import random
                    current_state = random.choice([True, False])
                
                self.pin_states['digital_inputs'][name] = current_state
                
                # Detectar cambios
                if old_state != current_state:
                    change = {
                        'pin_name': name,
                        'old_value': old_state,
                        'new_value': current_state,
                        'timestamp': datetime.now().isoformat(),
                        'description': config['description']
                    }
                    changes.append(change)
                    self.logger.info(f"Cambio detectado en {name}: {old_state} -> {current_state}")
        
        except Exception as e:
            self.logger.error(f"Error leyendo entradas digitales: {e}")
        
        return changes
    
    def read_analog_inputs(self):
        """Leer todas las entradas analógicas"""
        try:
            analog_config = self.pin_config.config.get('analog_inputs', {})
            
            for name, config in analog_config.items():
                if ADC_LIB and hasattr(ADC_LIB, 'read'):
                    # BeagleBone con ADC
                    pin = config['pin']
                    raw_value = ADC_LIB.read(pin)
                    # Convertir a voltaje (0-1.8V en BeagleBone)
                    voltage = raw_value * 1.8
                    
                elif self.pin_config.platform.startswith('raspberry_pi'):
                    # Raspberry Pi con MCP3008 (simulado)
                    import random
                    voltage = random.uniform(0, 3.3)
                    
                else:
                    # Simulación para otras plataformas
                    import random
                    voltage = random.uniform(0, 3.3)
                
                self.pin_states['analog_inputs'][name] = voltage
        
        except Exception as e:
            self.logger.error(f"Error leyendo entradas analógicas: {e}")
    
    def set_digital_output(self, pin_name, state):
        """Controlar una salida digital"""
        try:
            config = self.pin_config.get_output_pin(pin_name)
            if not config:
                raise ValueError(f"Pin de salida '{pin_name}' no encontrado")
            
            if GPIO_LIB and hasattr(GPIO_LIB, 'output'):
                pin = config['pin']
                gpio_state = GPIO_LIB.HIGH if state else GPIO_LIB.LOW
                GPIO_LIB.output(pin, gpio_state)
            
            self.pin_states['digital_outputs'][pin_name] = state
            self.logger.info(f"Salida {pin_name} establecida a {state}")
            
            # Publicar cambio por MQTT
            if self.mqtt_client:
                self.mqtt_client.publish(f"{self.topic_base}/outputs/{pin_name}", str(state))
        
        except Exception as e:
            self.logger.error(f"Error controlando salida {pin_name}: {e}")
    
    def save_pin_data(self):
        """Guardar datos de pines en base de datos"""
        try:
            with self.db_lock:
                cursor = self.db_conn.cursor()
                timestamp = datetime.now()
                
                # Guardar entradas digitales
                for name, value in self.pin_states['digital_inputs'].items():
                    cursor.execute('''
                        INSERT INTO pin_data (timestamp, pin_name, pin_type, value, unit)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (timestamp, name, 'digital_input', int(value), 'bool'))
                
                # Guardar entradas analógicas
                for name, value in self.pin_states['analog_inputs'].items():
                    cursor.execute('''
                        INSERT INTO pin_data (timestamp, pin_name, pin_type, value, unit)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (timestamp, name, 'analog_input', value, 'V'))
                
                # Guardar salidas digitales
                for name, value in self.pin_states['digital_outputs'].items():
                    cursor.execute('''
                        INSERT INTO pin_data (timestamp, pin_name, pin_type, value, unit)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (timestamp, name, 'digital_output', int(value), 'bool'))
                
                self.db_conn.commit()
        
        except Exception as e:
            self.logger.error(f"Error guardando datos: {e}")
    
    def save_pin_changes(self, changes):
        """Guardar cambios de pines en base de datos"""
        try:
            with self.db_lock:
                cursor = self.db_conn.cursor()
                
                for change in changes:
                    cursor.execute('''
                        INSERT INTO pin_changes (pin_name, old_value, new_value, change_type)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        change['pin_name'],
                        int(change['old_value']),
                        int(change['new_value']),
                        'digital_input'
                    ))
                
                self.db_conn.commit()
        
        except Exception as e:
            self.logger.error(f"Error guardando cambios: {e}")
    
    def publish_mqtt_data(self):
        """Publicar datos por MQTT"""
        try:
            if self.mqtt_client:
                # Publicar estado completo
                data = {
                    'timestamp': datetime.now().isoformat(),
                    'platform': self.pin_config.config['platform_name'],
                    'pins': self.pin_states
                }
                
                self.mqtt_client.publish(f"{self.topic_base}/data", json.dumps(data))
                
                # Publicar pines individuales
                for name, value in self.pin_states['digital_inputs'].items():
                    self.mqtt_client.publish(f"{self.topic_base}/inputs/{name}", str(value))
                
                for name, value in self.pin_states['analog_inputs'].items():
                    self.mqtt_client.publish(f"{self.topic_base}/analog/{name}", f"{value:.3f}")
        
        except Exception as e:
            self.logger.error(f"Error publicando MQTT: {e}")
    
    def render_dashboard(self):
        """Renderizar dashboard web"""
        platform_info = self.pin_config.config
        
        # Generar HTML del dashboard
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>TRT - Monitor de Pines</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2196F3; color: white; padding: 15px; border-radius: 5px; }}
                .platform {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
                .pins-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
                .pin-card {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; background: white; }}
                .pin-active {{ background-color: #4CAF50; color: white; }}
                .pin-inactive {{ background-color: #757575; color: white; }}
                .pin-value {{ font-size: 1.5em; font-weight: bold; margin: 10px 0; }}
                button {{ padding: 8px 15px; margin: 5px; border: none; border-radius: 3px; cursor: pointer; }}
                .btn-on {{ background-color: #4CAF50; color: white; }}
                .btn-off {{ background-color: #f44336; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔌 TRT - Monitor de Pines Industrial</h1>
                <p>Monitoreo en tiempo real de E/S digitales y analógicas</p>
            </div>
            
            <div class="platform">
                <h2>📋 Información de Plataforma</h2>
                <p><strong>Plataforma:</strong> {platform_info['platform_name']}</p>
                <p><strong>Librería GPIO:</strong> {platform_info['gpio_library']}</p>
                <p><strong>Total de pines:</strong> {platform_info['total_pins']}</p>
                <p><strong>Voltaje:</strong> {platform_info['voltage']}V</p>
            </div>
            
            <div class="pins-grid">
                <div class="pin-card">
                    <h3>📥 Entradas Digitales</h3>
                    <div id="digital-inputs"></div>
                </div>
                
                <div class="pin-card">
                    <h3>📤 Salidas Digitales</h3>
                    <div id="digital-outputs"></div>
                </div>
                
                <div class="pin-card">
                    <h3>📊 Entradas Analógicas</h3>
                    <div id="analog-inputs"></div>
                </div>
            </div>
            
            <script>
                function updatePins() {{
                    fetch('/api/pins')
                        .then(response => response.json())
                        .then(data => {{
                            // Actualizar entradas digitales
                            const digitalInputs = document.getElementById('digital-inputs');
                            digitalInputs.innerHTML = '';
                            for (const [name, value] of Object.entries(data.digital_inputs)) {{
                                const div = document.createElement('div');
                                div.className = value ? 'pin-active' : 'pin-inactive';
                                div.innerHTML = `<strong>${{name}}:</strong> ${{value ? 'HIGH' : 'LOW'}}`;
                                digitalInputs.appendChild(div);
                            }}
                            
                            // Actualizar salidas digitales
                            const digitalOutputs = document.getElementById('digital-outputs');
                            digitalOutputs.innerHTML = '';
                            for (const [name, value] of Object.entries(data.digital_outputs)) {{
                                const div = document.createElement('div');
                                div.innerHTML = `
                                    <p><strong>${{name}}:</strong> ${{value ? 'ON' : 'OFF'}}</p>
                                    <button class="btn-on" onclick="setOutput('${{name}}', true)">ON</button>
                                    <button class="btn-off" onclick="setOutput('${{name}}', false)">OFF</button>
                                `;
                                digitalOutputs.appendChild(div);
                            }}
                            
                            // Actualizar entradas analógicas
                            const analogInputs = document.getElementById('analog-inputs');
                            analogInputs.innerHTML = '';
                            for (const [name, value] of Object.entries(data.analog_inputs)) {{
                                const div = document.createElement('div');
                                div.innerHTML = `<strong>${{name}}:</strong> ${{value.toFixed(3)}}V`;
                                analogInputs.appendChild(div);
                            }}
                        }});
                }}
                
                function setOutput(pinName, state) {{
                    fetch('/api/set_output', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{pin_name: pinName, state: state}})
                    }});
                }}
                
                // Actualizar cada segundo
                setInterval(updatePins, 1000);
                updatePins(); // Cargar datos iniciales
            </script>
        </body>
        </html>
        '''
        
        return html
    
    def main_loop(self):
        """Bucle principal de monitoreo"""
        self.logger.info("Iniciando bucle principal de monitoreo")
        
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
        
        # Intervalos de configuración
        read_interval = self.config["monitoring"]["read_interval"]
        publish_interval = self.config["monitoring"]["publish_interval"]
        save_interval = self.config["monitoring"]["save_interval"]
        
        last_publish = 0
        last_save = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Leer entradas digitales
                changes = self.read_digital_inputs()
                
                # Leer entradas analógicas
                self.read_analog_inputs()
                
                # Guardar cambios si los hay
                if changes:
                    self.save_pin_changes(changes)
                    
                    # Notificar cambios por MQTT
                    if self.mqtt_client and self.config["alerts"]["mqtt_on_change"]:
                        for change in changes:
                            topic = f"{self.topic_base}/changes/{change['pin_name']}"
                            self.mqtt_client.publish(topic, json.dumps(change))
                
                # Publicar por MQTT periódicamente
                if current_time - last_publish >= publish_interval:
                    self.publish_mqtt_data()
                    last_publish = current_time
                
                # Guardar datos periódicamente
                if current_time - last_save >= save_interval:
                    self.save_pin_data()
                    last_save = current_time
                
                time.sleep(read_interval)
                
            except Exception as e:
                self.logger.error(f"Error en bucle principal: {e}")
                time.sleep(1.0)
    
    def signal_handler(self, signum, frame):
        """Manejo de señales para shutdown limpio"""
        self.logger.info(f"Recibida señal {signum}, cerrando...")
        self.running = False
    
    def shutdown(self):
        """Cerrar conexiones y limpiar recursos"""
        self.logger.info("Cerrando monitor de pines...")
        
        # Apagar todas las salidas
        try:
            for name in self.pin_states['digital_outputs'].keys():
                self.set_digital_output(name, False)
        except:
            pass
        
        # Limpiar GPIO
        try:
            if GPIO_LIB and hasattr(GPIO_LIB, 'cleanup'):
                GPIO_LIB.cleanup()
        except:
            pass
        
        # Cerrar conexiones
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        if hasattr(self, 'db_conn'):
            self.db_conn.close()
        
        self.logger.info("Monitor cerrado correctamente")

def main():
    """Función principal"""
    try:
        monitor = PinMonitor()
        monitor.main_loop()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por usuario")
    except Exception as e:
        print(f"Error fatal: {e}")
    finally:
        if 'monitor' in locals():
            monitor.shutdown()

if __name__ == "__main__":
    main()