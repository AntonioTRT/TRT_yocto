SUMMARY = "TRT BeagleBone Industrial Image - Optimized for BeagleBone Industrial applications"
DESCRIPTION = "Specialized image for BeagleBone with industrial I/O, CAN bus, and real-time capabilities"

require trt-industrial-image.bb

# BeagleBone specific packages
IMAGE_INSTALL += "\
    beaglebone-getting-started \
    bonescript \
    bb-cape-overlays \
    dtc \
    can-utils \
    libsocketcan \
    socketcan-isotp \
    pru-software-support \
    pru-icss \
    ti-pru-sw \
    am335x-pru-package \
    cape-universal-overlays \
    adafruit-beaglebone-io-python \
    beaglebone-universal-io \
    mi-programa-control \
"

# Real-time kernel for industrial applications
PREFERRED_PROVIDER_virtual/kernel = "linux-ti-staging-rt"

# BeagleBone specific optimizations
IMAGE_ROOTFS_SIZE = "12288"

# BeagleBone specific configurations
configure_beaglebone_industrial() {
    # Enable CAN interfaces by default
    echo 'auto can0' >> ${IMAGE_ROOTFS}/etc/network/interfaces
    echo 'iface can0 inet manual' >> ${IMAGE_ROOTFS}/etc/network/interfaces
    echo '    pre-up /sbin/ip link set can0 type can bitrate 125000' >> ${IMAGE_ROOTFS}/etc/network/interfaces
    echo '    up /sbin/ifconfig can0 up' >> ${IMAGE_ROOTFS}/etc/network/interfaces
    echo '    down /sbin/ifconfig can0 down' >> ${IMAGE_ROOTFS}/etc/network/interfaces
    
    # Configure PRU (Programmable Real-time Units)
    echo 'uio_pruss' >> ${IMAGE_ROOTFS}/etc/modules
    echo 'pruss' >> ${IMAGE_ROOTFS}/etc/modules
    
    # Configure industrial I/O
    mkdir -p ${IMAGE_ROOTFS}/opt/trt/beaglebone
    
    # Industrial GPIO configuration script
    cat > ${IMAGE_ROOTFS}/opt/trt/beaglebone/setup-industrial-gpio.sh << 'EOF'
#!/bin/bash
# BeagleBone Industrial GPIO Setup

# Configure P8 and P9 headers for industrial use
config-pin P8.07 gpio    # GPIO 36 - Digital Input 1
config-pin P8.08 gpio    # GPIO 37 - Digital Input 2
config-pin P8.09 gpio    # GPIO 39 - Digital Output 1
config-pin P8.10 gpio    # GPIO 38 - Digital Output 2

# Configure PWM outputs for motor control
config-pin P8.13 pwm     # PWM2A - Motor 1
config-pin P8.19 pwm     # PWM2B - Motor 2

# Configure ADC inputs for sensors
config-pin P9.39 ain     # AIN0 - Analog Input 1
config-pin P9.40 ain     # AIN1 - Analog Input 2

# Configure I2C for sensor communication
config-pin P9.19 i2c     # I2C2_SCL
config-pin P9.20 i2c     # I2C2_SDA

# Configure SPI for industrial communication
config-pin P9.17 spi_cs  # SPI0_CS0
config-pin P9.18 spi_sclk # SPI0_SCLK
config-pin P9.21 spi     # SPI0_D0
config-pin P9.22 spi     # SPI0_D1

echo "BeagleBone Industrial I/O configured"
EOF

    chmod +x ${IMAGE_ROOTFS}/opt/trt/beaglebone/setup-industrial-gpio.sh
    
    # Auto-configure on boot
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/beaglebone-industrial-setup.service << 'EOF'
[Unit]
Description=BeagleBone Industrial I/O Setup
After=bone-setup.service

[Service]
Type=oneshot
ExecStart=/opt/trt/beaglebone/setup-industrial-gpio.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

    systemctl --root=${IMAGE_ROOTFS} enable beaglebone-industrial-setup.service
    
    # Configure CAN bus service
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/can-setup.service << 'EOF'
[Unit]
Description=CAN Bus Setup for Industrial Communication
After=network.target

[Service]
Type=oneshot
ExecStart=/sbin/ip link set can0 type can bitrate 125000
ExecStart=/sbin/ip link set up can0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

    systemctl --root=${IMAGE_ROOTFS} enable can-setup.service
    
    # Industrial monitoring script
    cat > ${IMAGE_ROOTFS}/opt/trt/beaglebone/industrial-monitor.py << 'EOF'
#!/usr/bin/env python3
"""
BeagleBone Industrial Monitoring System
Monitors I/O, temperature, and system status
"""

import time
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/trt/beaglebone-monitor.log'),
        logging.StreamHandler()
    ]
)

class BeagleBoneMonitor:
    def __init__(self):
        self.status = {
            'system': 'BeagleBone Industrial',
            'version': '1.0',
            'last_update': None
        }
    
    def read_system_status(self):
        """Read system temperature, load, memory"""
        try:
            # CPU temperature
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000.0
            
            # System load
            with open('/proc/loadavg', 'r') as f:
                load = f.read().strip().split()[0]
            
            # Memory usage
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                total = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1])
                free = int([line for line in meminfo.split('\n') if 'MemFree' in line][0].split()[1])
                used_percent = ((total - free) / total) * 100
            
            return {
                'temperature': temp,
                'load': float(load),
                'memory_usage': used_percent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error reading system status: {e}")
            return None
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logging.info("Starting BeagleBone Industrial Monitor")
        
        while True:
            try:
                status = self.read_system_status()
                if status:
                    self.status.update(status)
                    self.status['last_update'] = datetime.now().isoformat()
                    
                    # Log critical conditions
                    if status['temperature'] > 70:
                        logging.warning(f"High temperature: {status['temperature']}°C")
                    
                    if status['load'] > 2.0:
                        logging.warning(f"High system load: {status['load']}")
                    
                    if status['memory_usage'] > 90:
                        logging.warning(f"High memory usage: {status['memory_usage']:.1f}%")
                    
                    # Save status to file
                    with open('/opt/trt/data/system_status.json', 'w') as f:
                        json.dump(self.status, f, indent=2)
                
                time.sleep(30)  # Monitor every 30 seconds
                
            except KeyboardInterrupt:
                logging.info("Monitor stopped by user")
                break
            except Exception as e:
                logging.error(f"Monitor error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    monitor = BeagleBoneMonitor()
    monitor.monitor_loop()
EOF

    chmod +x ${IMAGE_ROOTFS}/opt/trt/beaglebone/industrial-monitor.py
    
    # Create systemd service for monitoring
    cat > ${IMAGE_ROOTFS}/etc/systemd/system/beaglebone-monitor.service << 'EOF'
[Unit]
Description=BeagleBone Industrial Monitor
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/trt/beaglebone/industrial-monitor.py
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF

    systemctl --root=${IMAGE_ROOTFS} enable beaglebone-monitor.service
}

ROOTFS_POSTPROCESS_COMMAND += "configure_beaglebone_industrial; "