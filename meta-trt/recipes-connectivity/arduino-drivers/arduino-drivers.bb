SUMMARY = "Arduino and USB Serial Drivers Package"
DESCRIPTION = "Drivers and tools for Arduino, USB-Serial devices and development boards"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

inherit allarch

# Arduino and USB Serial drivers
RDEPENDS_${PN} = "\
    kernel-module-ftdi-sio \
    kernel-module-cp210x \
    kernel-module-ch341 \
    kernel-module-pl2303 \
    kernel-module-cdc-acm \
    kernel-module-usbserial \
    udev-rules-arduino \
    python3-pyserial \
"

# Optional development tools
RRECOMMENDS_${PN} = "\
    avrdude \
    minicom \
    screen \
    python3-pip \
    gcc \
    make \
"

do_install() {
    # Create udev rules for Arduino devices
    install -d ${D}${sysconfdir}/udev/rules.d
    
    cat > ${D}${sysconfdir}/udev/rules.d/99-arduino.rules << 'EOF'
# Arduino Uno/Nano (FTDI FT232)
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout", SYMLINK+="ttyArduino%n"

# Arduino Uno R3 (Atmega16U2)
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", MODE="0666", GROUP="dialout", SYMLINK+="ttyArduinoUno%n"

# Arduino Nano (CH340)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="dialout", SYMLINK+="ttyArduinoNano%n"

# Arduino Mega 2560
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0042", MODE="0666", GROUP="dialout", SYMLINK+="ttyArduinoMega%n"

# ESP32 development boards
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout", SYMLINK+="ttyESP32%n"

# Generic USB-Serial converters
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF

    # Create Arduino detection script
    install -d ${D}${bindir}
    cat > ${D}${bindir}/detect-arduino << 'EOF'
#!/bin/bash
# detect-arduino - Script to detect connected Arduino devices

echo "Scanning for Arduino and compatible devices..."
echo "=============================================="

# List USB devices
echo "USB Devices:"
lsusb | grep -i "arduino\|ftdi\|ch340\|cp210\|prolific"

echo
echo "Serial devices:"
ls -la /dev/tty* | grep -E "(USB|ACM|Arduino)"

echo
echo "Available serial ports:"
for port in /dev/ttyUSB* /dev/ttyACM* /dev/ttyArduino*; do
    if [ -e "$port" ]; then
        echo "  $port"
        # Try to get device info
        udevadm info --name="$port" --attribute-walk | head -20
        echo "  ---"
    fi
done 2>/dev/null

echo
echo "To connect to Arduino:"
echo "  minicom -D /dev/ttyUSB0 -b 9600"
echo "  screen /dev/ttyUSB0 9600"
echo "  python3 -c 'import serial; print(serial.Serial(\"/dev/ttyUSB0\", 9600))'"
EOF

    chmod +x ${D}${bindir}/detect-arduino
}

FILES_${PN} = "\
    ${sysconfdir}/udev/rules.d/99-arduino.rules \
    ${bindir}/detect-arduino \
"