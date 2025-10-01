SUMMARY = "BeagleBone specific industrial packages"
DESCRIPTION = "Packages optimized for BeagleBone industrial applications"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

PROVIDES = "${PACKAGES}"
PACKAGES = "\
    ${PN} \
    ${PN}-cape \
    ${PN}-pru \
    ${PN}-industrial \
    ${PN}-motor-control \
"

RDEPENDS_${PN} = "\
    ${PN}-cape \
    ${PN}-pru \
    ${PN}-industrial \
    ${PN}-motor-control \
"

# Cape and overlay support
RDEPENDS_${PN}-cape = "\
    bb-cape-overlays \
    cape-universal-overlays \
    dtc \
    device-tree-compiler \
    beaglebone-universal-io \
    config-tools \
"

# PRU (Programmable Real-time Unit) support
RDEPENDS_${PN}-pru = "\
    pru-software-support \
    pru-icss \
    ti-pru-sw \
    am335x-pru-package \
    pruss-bindings \
"

# Industrial I/O and communication
RDEPENDS_${PN}-industrial = "\
    can-utils \
    libsocketcan \
    socketcan-isotp \
    iio-utils \
    i2c-tools \
    spi-tools \
    gpio-utils \
    industrial-io \
    modbus-tools \
    libmodbus \
    python3-pymodbus \
"

# Motor control and PWM
RDEPENDS_${PN}-motor-control = "\
    pwm-utils \
    servo-control \
    stepper-motor-control \
    python3-adafruit-circuitpython-motor \
    python3-adafruit-circuitpython-servo \
"