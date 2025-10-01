#!/usr/bin/env python3
"""
Mi Programa de Control Industrial
Desarrollado por Antonio TRT

Este programa controla procesos industriales usando:
- Modbus para PLCs
- MQTT para IoT
- GPIO para control directo
"""

import sys
import json
import time
import logging
import signal
from pathlib import Path
from datetime import datetime

# Importar librerías industriales
try:
    from pymodbus.client.sync import ModbusTcpClient
    import paho.mqtt.client as mqtt
    import RPi.GPIO as GPIO  # Para Raspberry Pi
except ImportError as e:
    print(f"Error importing libraries: {e}")
    print("Install with: pip3 install pymodbus paho-mqtt RPi.GPIO")
    sys.exit(1)

class MiControladorIndustrial:
    def __init__(self, config_file="/etc/trt/config.json"):
        """Inicializar controlador con configuración"""
        self.running = True
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.setup_modbus()
        self.setup_mqtt()
        self.setup_gpio()
        
        # Manejo de señales para shutdown limpio
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def load_config(self, config_file):
        """Cargar configuración desde archivo JSON"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            # Configuración por defecto
            return {
                "modbus": {
                    "host": "192.168.100.50",
                    "port": 502,
                    "unit_id": 1
                },
                "mqtt": {
                    "broker": "192.168.100.1",
                    "port": 1883,
                    "topic_base": "trt/industrial"
                },
                "gpio": {
                    "output_pins": [18, 19, 20, 21],
                    "input_pins": [22, 23, 24, 25]
                },
                "intervals": {
                    "read_sensors": 5.0,
                    "publish_data": 30.0
                }
            }
    
    def setup_logging(self):
        """Configurar logging"""
        log_file = "/opt/trt/mi-programa/logs/control.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Mi Controlador Industrial iniciado")
    
    def setup_modbus(self):
        """Configurar cliente Modbus"""
        try:
            modbus_config = self.config["modbus"]
            self.modbus_client = ModbusTcpClient(
                host=modbus_config["host"],
                port=modbus_config["port"]
            )
            self.unit_id = modbus_config["unit_id"]
            self.logger.info(f"Modbus configurado: {modbus_config['host']}:{modbus_config['port']}")
        except Exception as e:
            self.logger.error(f"Error configurando Modbus: {e}")
            self.modbus_client = None
    
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
            self.logger.info(f"MQTT configurado: {mqtt_config['broker']}:{mqtt_config['port']}")
        except Exception as e:
            self.logger.error(f"Error configurando MQTT: {e}")
            self.mqtt_client = None
    
    def setup_gpio(self):
        """Configurar GPIO (para Raspberry Pi/BeagleBone)"""
        try:
            gpio_config = self.config["gpio"]
            GPIO.setmode(GPIO.BCM)
            
            # Configurar pines de salida
            for pin in gpio_config["output_pins"]:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
            
            # Configurar pines de entrada
            for pin in gpio_config["input_pins"]:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            self.logger.info("GPIO configurado")
        except Exception as e:
            self.logger.error(f"Error configurando GPIO: {e}")
    
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
            self.logger.info(f"MQTT recibido: {topic} = {payload}")
            
            # Procesar comandos
            if "commands/relay" in topic:
                relay_num = int(topic.split("/")[-1])
                state = payload.lower() == "on"
                self.control_relay(relay_num, state)
            
        except Exception as e:
            self.logger.error(f"Error procesando MQTT: {e}")
    
    def read_modbus_data(self):
        """Leer datos del PLC vía Modbus"""
        try:
            if not self.modbus_client:
                return None
            
            # Conectar si no está conectado
            if not self.modbus_client.is_socket_open():
                self.modbus_client.connect()
            
            # Leer registros holding (ejemplo: registros 0-9)
            result = self.modbus_client.read_holding_registers(0, 10, unit=self.unit_id)
            
            if result.isError():
                self.logger.error("Error leyendo Modbus")
                return None
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "registers": result.registers,
                "temperature": result.registers[0] / 10.0,  # Ejemplo: temp en reg 0
                "pressure": result.registers[1] / 100.0,   # Ejemplo: presión en reg 1
                "flow": result.registers[2],               # Ejemplo: flujo en reg 2
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error leyendo Modbus: {e}")
            return None
    
    def read_gpio_inputs(self):
        """Leer estado de entradas digitales"""
        try:
            gpio_config = self.config["gpio"]
            inputs = {}
            
            for i, pin in enumerate(gpio_config["input_pins"]):
                state = GPIO.input(pin)
                inputs[f"input_{i+1}"] = not state  # Invertir por pull-up
            
            return inputs
            
        except Exception as e:
            self.logger.error(f"Error leyendo GPIO: {e}")
            return {}
    
    def control_relay(self, relay_num, state):
        """Controlar relé de salida"""
        try:
            gpio_config = self.config["gpio"]
            if 0 <= relay_num < len(gpio_config["output_pins"]):
                pin = gpio_config["output_pins"][relay_num]
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
                self.logger.info(f"Relé {relay_num+1} {'ON' if state else 'OFF'}")
                
                # Publicar estado por MQTT
                if self.mqtt_client:
                    topic = f"{self.topic_base}/status/relay/{relay_num+1}"
                    self.mqtt_client.publish(topic, "ON" if state else "OFF")
            
        except Exception as e:
            self.logger.error(f"Error controlando relé: {e}")
    
    def publish_data(self, data):
        """Publicar datos por MQTT"""
        try:
            if self.mqtt_client and data:
                topic = f"{self.topic_base}/data"
                payload = json.dumps(data)
                self.mqtt_client.publish(topic, payload)
                self.logger.debug(f"Datos publicados: {topic}")
        except Exception as e:
            self.logger.error(f"Error publicando datos: {e}")
    
    def save_data(self, data):
        """Guardar datos localmente"""
        try:
            if data:
                data_file = f"/opt/trt/mi-programa/data/{datetime.now().strftime('%Y-%m-%d')}.json"
                
                # Crear directorio si no existe
                Path(data_file).parent.mkdir(parents=True, exist_ok=True)
                
                # Agregar datos al archivo
                with open(data_file, 'a') as f:
                    f.write(json.dumps(data) + '\n')
                    
        except Exception as e:
            self.logger.error(f"Error guardando datos: {e}")
    
    def main_loop(self):
        """Bucle principal del programa"""
        self.logger.info("Iniciando bucle principal")
        
        last_read = 0
        last_publish = 0
        read_interval = self.config["intervals"]["read_sensors"]
        publish_interval = self.config["intervals"]["publish_data"]
        
        while self.running:
            try:
                current_time = time.time()
                
                # Leer sensores cada X segundos
                if current_time - last_read >= read_interval:
                    # Leer datos de Modbus
                    modbus_data = self.read_modbus_data()
                    
                    # Leer entradas GPIO
                    gpio_data = self.read_gpio_inputs()
                    
                    # Combinar datos
                    if modbus_data:
                        modbus_data.update({"gpio_inputs": gpio_data})
                        self.current_data = modbus_data
                        
                        # Guardar datos localmente
                        self.save_data(modbus_data)
                        
                        last_read = current_time
                
                # Publicar datos cada Y segundos
                if current_time - last_publish >= publish_interval:
                    if hasattr(self, 'current_data'):
                        self.publish_data(self.current_data)
                        last_publish = current_time
                
                # Esperar un poco antes del siguiente ciclo
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error en bucle principal: {e}")
                time.sleep(5.0)
    
    def signal_handler(self, signum, frame):
        """Manejo de señales para shutdown limpio"""
        self.logger.info(f"Recibida señal {signum}, cerrando...")
        self.running = False
    
    def shutdown(self):
        """Cerrar conexiones y limpiar recursos"""
        self.logger.info("Cerrando controlador...")
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        if self.modbus_client:
            self.modbus_client.close()
        
        GPIO.cleanup()
        self.logger.info("Controlador cerrado")

def main():
    """Función principal"""
    try:
        controlador = MiControladorIndustrial()
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