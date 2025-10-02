#!/bin/bash
# configure-hardware.sh - Configure hardware drivers based on trt-config.txt

CONFIG_FILE="/etc/trt/trt-config.txt"
MODULES_FILE="/etc/modules-load.d/trt-hardware.conf"

echo "TRT Hardware Configuration"
echo "=========================="

# Function to read config value
get_config_value() {
    local key=$1
    grep "^${key}=" "$CONFIG_FILE" | cut -d'=' -f2 | tr -d '"'
}

# Read hardware configuration
ARDUINO_ENABLE=$(get_config_value "ARDUINO_ENABLE")
SPI_ENABLE=$(get_config_value "SPI_ENABLE")
I2C_ENABLE=$(get_config_value "I2C_ENABLE")
CUSTOM_DRIVERS_ENABLE=$(get_config_value "CUSTOM_DRIVERS_ENABLE")

echo "Hardware configuration:"
echo "  Arduino support: $ARDUINO_ENABLE"
echo "  SPI support: $SPI_ENABLE"
echo "  I2C support: $I2C_ENABLE"
echo "  Custom drivers: $CUSTOM_DRIVERS_ENABLE"

# Create modules configuration
echo "# TRT Hardware Modules" > "$MODULES_FILE"

# Enable Arduino drivers
if [ "$ARDUINO_ENABLE" = "true" ]; then
    echo "Enabling Arduino/USB-Serial drivers..."
    cat >> "$MODULES_FILE" << EOF
# Arduino and USB-Serial drivers
ftdi_sio
cp210x
ch341
pl2303
cdc_acm
usbserial
EOF
fi

# Enable SPI
if [ "$SPI_ENABLE" = "true" ]; then
    echo "Enabling SPI support..."
    cat >> "$MODULES_FILE" << EOF
# SPI support
spi_bcm2835
spidev
EOF
    
    # Enable SPI in boot config (Raspberry Pi)
    if [ -f /boot/config.txt ]; then
        if ! grep -q "dtparam=spi=on" /boot/config.txt; then
            echo "dtparam=spi=on" >> /boot/config.txt
        fi
    fi
fi

# Enable I2C
if [ "$I2C_ENABLE" = "true" ]; then
    echo "Enabling I2C support..."
    cat >> "$MODULES_FILE" << EOF
# I2C support
i2c_bcm2835
i2c_dev
EOF
    
    # Enable I2C in boot config (Raspberry Pi)
    if [ -f /boot/config.txt ]; then
        if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
            echo "dtparam=i2c_arm=on" >> /boot/config.txt
        fi
    fi
fi

# Load custom drivers
if [ "$CUSTOM_DRIVERS_ENABLE" = "true" ]; then
    echo "Enabling custom drivers..."
    cat >> "$MODULES_FILE" << EOF
# Custom TRT drivers
custom-driver
EOF
fi

# Load all modules
echo "Loading hardware modules..."
systemctl reload systemd-modules-load

# Set permissions for hardware access
echo "Setting hardware permissions..."
usermod -a -G dialout,spi,i2c,gpio trt 2>/dev/null || true

echo "Hardware configuration completed!"
echo
echo "Available devices:"
echo "  Serial: $(ls /dev/tty{USB,ACM}* 2>/dev/null | tr '\n' ' ')"
echo "  I2C: $(ls /dev/i2c-* 2>/dev/null | tr '\n' ' ')"
echo "  SPI: $(ls /dev/spidev* 2>/dev/null | tr '\n' ' ')"
echo
echo "Test commands:"
echo "  Arduino: detect-arduino"
echo "  I2C scan: i2cdetect -y 1"
echo "  GPIO: gpioinfo"