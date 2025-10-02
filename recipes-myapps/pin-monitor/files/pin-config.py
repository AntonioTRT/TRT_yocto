#!/usr/bin/env python3
"""
TRT Hardware Pin Configuration
Configuraciones específicas de pines para cada plataforma

Soporta:
- Raspberry Pi (todos los modelos)
- BeagleBone Black/Industrial  
- NXP i.MX7

Autor: Antonio TRT
"""

import sys
import json
from pathlib import Path

class PinConfig:
    """Clase para manejar configuraciones de pines específicas por plataforma"""
    
    def __init__(self):
        self.platform = self.detect_platform()
        self.config = self.load_platform_config()
    
    def detect_platform(self):
        """Detectar automáticamente la plataforma"""
        try:
            # Detectar Raspberry Pi
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'BCM' in cpuinfo and 'Raspberry Pi' in cpuinfo:
                    # Detectar modelo específico
                    if 'Pi 4' in cpuinfo:
                        return 'raspberry_pi_4'
                    elif 'Pi 3' in cpuinfo:
                        return 'raspberry_pi_3'
                    else:
                        return 'raspberry_pi_generic'
            
            # Detectar BeagleBone
            if Path('/sys/devices/platform/bone_capemgr').exists():
                return 'beaglebone_black'
            
            # Detectar i.MX7
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                if 'i.MX7' in model:
                    return 'imx7'
            
            # Si no se detecta, usar genérico
            return 'generic'
            
        except Exception as e:
            print(f"Error detectando plataforma: {e}")
            return 'generic'
    
    def load_platform_config(self):
        """Cargar configuración específica de la plataforma"""
        configs = {
            'raspberry_pi_4': {
                'platform_name': 'Raspberry Pi 4',
                'gpio_library': 'RPi.GPIO',
                'total_pins': 40,
                'voltage': 3.3,
                'digital_inputs': {
                    'input_1': {'pin': 22, 'pull': 'up', 'description': 'Sensor digital 1'},
                    'input_2': {'pin': 23, 'pull': 'up', 'description': 'Sensor digital 2'},
                    'input_3': {'pin': 24, 'pull': 'up', 'description': 'Sensor digital 3'},
                    'input_4': {'pin': 25, 'pull': 'up', 'description': 'Sensor digital 4'},
                    'emergency_stop': {'pin': 27, 'pull': 'up', 'description': 'Paro de emergencia'},
                },
                'digital_outputs': {
                    'relay_1': {'pin': 18, 'initial': 'low', 'description': 'Relé de control 1'},
                    'relay_2': {'pin': 19, 'initial': 'low', 'description': 'Relé de control 2'},
                    'relay_3': {'pin': 20, 'initial': 'low', 'description': 'Relé de control 3'},
                    'relay_4': {'pin': 21, 'initial': 'low', 'description': 'Relé de control 4'},
                    'alarm_led': {'pin': 16, 'initial': 'low', 'description': 'LED de alarma'},
                    'status_led': {'pin': 26, 'initial': 'low', 'description': 'LED de estado'},
                },
                'analog_inputs': {
                    'sensor_1': {'channel': 0, 'description': 'Sensor analógico 1 (0-10V)'},
                    'sensor_2': {'channel': 1, 'description': 'Sensor analógico 2 (4-20mA)'},
                },
                'pwm_outputs': {
                    'motor_1': {'pin': 12, 'frequency': 1000, 'description': 'Control motor 1'},
                    'motor_2': {'pin': 13, 'frequency': 1000, 'description': 'Control motor 2'},
                },
                'interfaces': {
                    'i2c': {'sda': 2, 'scl': 3, 'enabled': True},
                    'spi': {'mosi': 10, 'miso': 9, 'sclk': 11, 'ce0': 8, 'enabled': True},
                    'uart': {'tx': 14, 'rx': 15, 'enabled': True},
                }
            },
            
            'raspberry_pi_3': {
                'platform_name': 'Raspberry Pi 3',
                'gpio_library': 'RPi.GPIO',
                'total_pins': 40,
                'voltage': 3.3,
                'digital_inputs': {
                    'input_1': {'pin': 22, 'pull': 'up', 'description': 'Sensor digital 1'},
                    'input_2': {'pin': 23, 'pull': 'up', 'description': 'Sensor digital 2'},
                    'input_3': {'pin': 24, 'pull': 'up', 'description': 'Sensor digital 3'},
                    'input_4': {'pin': 25, 'pull': 'up', 'description': 'Sensor digital 4'},
                },
                'digital_outputs': {
                    'relay_1': {'pin': 18, 'initial': 'low', 'description': 'Relé de control 1'},
                    'relay_2': {'pin': 19, 'initial': 'low', 'description': 'Relé de control 2'},
                    'relay_3': {'pin': 20, 'initial': 'low', 'description': 'Relé de control 3'},
                    'relay_4': {'pin': 21, 'initial': 'low', 'description': 'Relé de control 4'},
                },
                'interfaces': {
                    'i2c': {'sda': 2, 'scl': 3, 'enabled': True},
                    'spi': {'mosi': 10, 'miso': 9, 'sclk': 11, 'ce0': 8, 'enabled': True},
                    'uart': {'tx': 14, 'rx': 15, 'enabled': True},
                }
            },
            
            'beaglebone_black': {
                'platform_name': 'BeagleBone Black',
                'gpio_library': 'Adafruit_BBIO.GPIO',
                'total_pins': 92,  # P8 y P9 headers
                'voltage': 3.3,
                'digital_inputs': {
                    'input_1': {'pin': 'P8_7', 'pull': 'up', 'description': 'Sensor digital 1'},
                    'input_2': {'pin': 'P8_8', 'pull': 'up', 'description': 'Sensor digital 2'},
                    'input_3': {'pin': 'P8_9', 'pull': 'up', 'description': 'Sensor digital 3'},
                    'input_4': {'pin': 'P8_10', 'pull': 'up', 'description': 'Sensor digital 4'},
                    'emergency_stop': {'pin': 'P8_11', 'pull': 'up', 'description': 'Paro de emergencia'},
                    'limit_switch_1': {'pin': 'P8_12', 'pull': 'up', 'description': 'Final de carrera 1'},
                },
                'digital_outputs': {
                    'relay_1': {'pin': 'P8_13', 'initial': 'low', 'description': 'Relé de control 1'},
                    'relay_2': {'pin': 'P8_14', 'initial': 'low', 'description': 'Relé de control 2'},
                    'relay_3': {'pin': 'P8_15', 'initial': 'low', 'description': 'Relé de control 3'},
                    'relay_4': {'pin': 'P8_16', 'initial': 'low', 'description': 'Relé de control 4'},
                    'valve_1': {'pin': 'P8_17', 'initial': 'low', 'description': 'Válvula neumática 1'},
                    'valve_2': {'pin': 'P8_18', 'initial': 'low', 'description': 'Válvula neumática 2'},
                },
                'analog_inputs': {
                    'sensor_1': {'pin': 'P9_39', 'channel': 'AIN0', 'description': 'Sensor presión (0-10V)'},
                    'sensor_2': {'pin': 'P9_40', 'channel': 'AIN1', 'description': 'Sensor temperatura (4-20mA)'},
                    'sensor_3': {'pin': 'P9_37', 'channel': 'AIN2', 'description': 'Sensor nivel (0-5V)'},
                    'sensor_4': {'pin': 'P9_38', 'channel': 'AIN3', 'description': 'Sensor flujo (4-20mA)'},
                },
                'pwm_outputs': {
                    'motor_1': {'pin': 'P8_19', 'frequency': 1000, 'description': 'Control velocidad motor 1'},
                    'motor_2': {'pin': 'P8_13', 'frequency': 1000, 'description': 'Control velocidad motor 2'},
                    'servo_1': {'pin': 'P9_14', 'frequency': 50, 'description': 'Servo posicionador'},
                },
                'interfaces': {
                    'i2c': {'sda': 'P9_20', 'scl': 'P9_19', 'bus': 2, 'enabled': True},
                    'spi': {'mosi': 'P9_18', 'miso': 'P9_21', 'sclk': 'P9_22', 'cs': 'P9_17', 'enabled': True},
                    'uart': {'tx': 'P9_24', 'rx': 'P9_26', 'enabled': True},
                    'can': {'tx': 'P9_24', 'rx': 'P9_26', 'enabled': True},
                },
                'pru_pins': {
                    'pru0_r30_0': {'pin': 'P9_31', 'description': 'PRU0 output 0'},
                    'pru0_r30_1': {'pin': 'P9_29', 'description': 'PRU0 output 1'},
                    'pru0_r31_0': {'pin': 'P9_30', 'description': 'PRU0 input 0'},
                    'pru0_r31_1': {'pin': 'P9_28', 'description': 'PRU0 input 1'},
                }
            },
            
            'imx7': {
                'platform_name': 'NXP i.MX7',
                'gpio_library': 'custom',
                'total_pins': 'variable',
                'voltage': 3.3,
                'digital_inputs': {
                    'input_1': {'pin': 1, 'gpio': 'gpio1_1', 'pull': 'up', 'description': 'Sensor digital 1'},
                    'input_2': {'pin': 2, 'gpio': 'gpio1_2', 'pull': 'up', 'description': 'Sensor digital 2'},
                    'input_3': {'pin': 3, 'gpio': 'gpio1_3', 'pull': 'up', 'description': 'Sensor digital 3'},
                    'input_4': {'pin': 4, 'gpio': 'gpio1_4', 'pull': 'up', 'description': 'Sensor digital 4'},
                },
                'digital_outputs': {
                    'relay_1': {'pin': 5, 'gpio': 'gpio1_5', 'initial': 'low', 'description': 'Relé de control 1'},
                    'relay_2': {'pin': 6, 'gpio': 'gpio1_6', 'initial': 'low', 'description': 'Relé de control 2'},
                    'relay_3': {'pin': 7, 'gpio': 'gpio1_7', 'initial': 'low', 'description': 'Relé de control 3'},
                    'relay_4': {'pin': 8, 'gpio': 'gpio1_8', 'initial': 'low', 'description': 'Relé de control 4'},
                },
                'analog_inputs': {
                    'sensor_1': {'channel': 0, 'description': 'Sensor analógico 1'},
                    'sensor_2': {'channel': 1, 'description': 'Sensor analógico 2'},
                },
                'interfaces': {
                    'i2c': {'bus': 1, 'enabled': True},
                    'spi': {'bus': 1, 'enabled': True},
                    'uart': {'device': '/dev/ttymxc0', 'enabled': True},
                    'can': {'device': 'can0', 'enabled': True},
                }
            },
            
            'generic': {
                'platform_name': 'Generic Linux',
                'gpio_library': 'sysfs',
                'total_pins': 'unknown',
                'voltage': 3.3,
                'digital_inputs': {
                    'input_1': {'pin': 'gpio22', 'pull': 'up', 'description': 'Sensor digital 1'},
                },
                'digital_outputs': {
                    'relay_1': {'pin': 'gpio18', 'initial': 'low', 'description': 'Relé de control 1'},
                },
                'interfaces': {
                    'i2c': {'device': '/dev/i2c-1', 'enabled': False},
                    'spi': {'device': '/dev/spidev0.0', 'enabled': False},
                    'uart': {'device': '/dev/ttyS0', 'enabled': False},
                }
            }
        }
        
        return configs.get(self.platform, configs['generic'])
    
    def get_input_pin(self, input_name):
        """Obtener configuración de pin de entrada"""
        return self.config['digital_inputs'].get(input_name, None)
    
    def get_output_pin(self, output_name):
        """Obtener configuración de pin de salida"""
        return self.config['digital_outputs'].get(output_name, None)
    
    def get_analog_input(self, input_name):
        """Obtener configuración de entrada analógica"""
        return self.config.get('analog_inputs', {}).get(input_name, None)
    
    def get_pwm_output(self, output_name):
        """Obtener configuración de salida PWM"""
        return self.config.get('pwm_outputs', {}).get(output_name, None)
    
    def get_interface_config(self, interface_name):
        """Obtener configuración de interfaz (I2C, SPI, UART)"""
        return self.config['interfaces'].get(interface_name, None)
    
    def list_available_pins(self):
        """Listar todos los pines disponibles"""
        pins = {
            'digital_inputs': list(self.config['digital_inputs'].keys()),
            'digital_outputs': list(self.config['digital_outputs'].keys()),
            'analog_inputs': list(self.config.get('analog_inputs', {}).keys()),
            'pwm_outputs': list(self.config.get('pwm_outputs', {}).keys()),
        }
        return pins
    
    def save_custom_config(self, filename):
        """Guardar configuración actual a archivo"""
        config_data = {
            'platform': self.platform,
            'detected_platform': self.config['platform_name'],
            'configuration': self.config
        }
        
        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def print_platform_info(self):
        """Mostrar información de la plataforma detectada"""
        print(f"═══════════════════════════════════════════════════════")
        print(f"         TRT - CONFIGURACIÓN DE PLATAFORMA")
        print(f"═══════════════════════════════════════════════════════")
        print(f"Plataforma detectada: {self.config['platform_name']}")
        print(f"Librería GPIO: {self.config['gpio_library']}")
        print(f"Total de pines: {self.config['total_pins']}")
        print(f"Voltaje: {self.config['voltage']}V")
        print(f"")
        
        print(f"📥 ENTRADAS DIGITALES:")
        for name, config in self.config['digital_inputs'].items():
            print(f"  {name}: Pin {config['pin']} - {config['description']}")
        
        print(f"")
        print(f"📤 SALIDAS DIGITALES:")
        for name, config in self.config['digital_outputs'].items():
            print(f"  {name}: Pin {config['pin']} - {config['description']}")
        
        if 'analog_inputs' in self.config:
            print(f"")
            print(f"📊 ENTRADAS ANALÓGICAS:")
            for name, config in self.config['analog_inputs'].items():
                channel_info = config.get('channel', config.get('pin', 'N/A'))
                print(f"  {name}: {channel_info} - {config['description']}")
        
        if 'pwm_outputs' in self.config:
            print(f"")
            print(f"🌊 SALIDAS PWM:")
            for name, config in self.config['pwm_outputs'].items():
                print(f"  {name}: Pin {config['pin']} ({config['frequency']}Hz) - {config['description']}")
        
        print(f"")
        print(f"🔌 INTERFACES:")
        for name, config in self.config['interfaces'].items():
            status = "✅ Habilitada" if config.get('enabled', False) else "❌ Deshabilitada"
            print(f"  {name.upper()}: {status}")
        
        print(f"═══════════════════════════════════════════════════════")

def main():
    """Función principal para testing"""
    pin_config = PinConfig()
    pin_config.print_platform_info()
    
    # Guardar configuración
    pin_config.save_custom_config(f"/opt/trt/config/{pin_config.platform}_pins.json")
    print(f"\n💾 Configuración guardada en: /opt/trt/config/{pin_config.platform}_pins.json")

if __name__ == "__main__":
    main()