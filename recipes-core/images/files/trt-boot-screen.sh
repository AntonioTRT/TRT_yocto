#!/bin/bash

# TRT Boot Screen - Lo que verás al arrancar
# Este script simula lo que aparece en pantalla

cat << 'EOF'

████████╗██████╗ ████████╗
╚══██╔══╝██╔══██╗╚══██╔══╝
   ██║   ██████╔╝   ██║   
   ██║   ██╔══██╗   ██║   
   ██║   ██║  ██║   ██║   
   ╚═╝   ╚═╝  ╚═╝   ╚═╝   

                              TRT Linux v1.0
                          Developed by Antonio TRT - 2025
                        
═══════════════════════════════════════════════════════════════════════════════════════════════════════

SYSTEM INFORMATION:
-------------------
Platform        : Raspberry Pi 4 Model B
Architecture    : ARM Cortex-A72 (64-bit)
Memory          : 4096 MB
Storage         : 16 GB microSD
Kernel          : Linux 6.1.x-trt
Distribution    : TRT Linux 1.0

NETWORK STATUS:
---------------
Ethernet        : eth0 - 192.168.100.10/24 ✓
WiFi            : wlan0 - TRT-Maintenance ✓
Gateway         : 192.168.100.1 ✓
DNS             : 8.8.8.8, 8.8.4.4 ✓

INDUSTRIAL SERVICES:
--------------------
MQTT Broker     : mosquitto - Port 1883 ✓
Modbus Server   : Port 502 ✓
OPC-UA Server   : Port 4840 ✓
SSH Server      : Port 22 ✓
Web Interface   : Port 80 ✓
Watchdog        : Enabled ✓

HARDWARE STATUS:
----------------
GPIO            : 40 pins available ✓
I2C             : Enabled (pins 3,5) ✓
SPI             : Enabled (pins 19,21,23) ✓
UART            : Enabled (pins 8,10) ✓
PWM             : Available ✓
Temperature     : 45.2°C ✓

YOUR APPLICATIONS:
------------------
TRT Project : Running (PID: 1234) ✓
Industrial Monitor  : Running (PID: 1235) ✓
Data Logger        : Running (PID: 1236) ✓

═══════════════════════════════════════════════════════════════════════════════════════════════════════

LOGIN CREDENTIALS:
------------------
Username: root
Password: 2020

Username: developer  
Password: 2020

QUICK ACCESS:
-------------
Web Dashboard  : http://192.168.100.10
SSH Access     : ssh root@192.168.100.10 (password: 2020)
Config Files   : /etc/trt/config.json
Logs          : /var/log/trt/
Data          : /opt/trt/data/

USEFUL COMMANDS:
----------------
systemctl status trt_main.service    # Ver estado de tu programa
journalctl -f                          # Ver logs en tiempo real
nano /etc/trt/config.json              # Editar configuración
trt-network-config.sh                  # Reconfigurar red
can-utils                               # Herramientas CAN bus
modbus-client -h                        # Cliente Modbus

═══════════════════════════════════════════════════════════════════════════════════════════════════════

EOF

echo ""
echo "TRT Linux 1.0 $(hostname)"
echo ""
echo -n "$(hostname) login: "