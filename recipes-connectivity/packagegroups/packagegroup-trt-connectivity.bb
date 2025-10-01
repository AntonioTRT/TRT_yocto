SUMMARY = "Industrial IoT connectivity tools and libraries"
DESCRIPTION = "Package group for industrial IoT connectivity including MQTT, Modbus, OPC-UA"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

PROVIDES = "${PACKAGES}"
PACKAGES = "\
    ${PN} \
    ${PN}-mqtt \
    ${PN}-modbus \
    ${PN}-opcua \
    ${PN}-ethernet \
"

RDEPENDS_${PN} = "\
    ${PN}-mqtt \
    ${PN}-modbus \
    ${PN}-opcua \
    ${PN}-ethernet \
"

RDEPENDS_${PN}-mqtt = "\
    mosquitto \
    mosquitto-clients \
    mosquitto-dev \
    paho-mqtt-c \
    python3-paho-mqtt \
"

RDEPENDS_${PN}-modbus = "\
    libmodbus \
    libmodbus-dev \
    python3-pymodbus \
    modbus-tools \
"

RDEPENDS_${PN}-opcua = "\
    open62541 \
    python3-opcua \
    python3-asyncua \
"

RDEPENDS_${PN}-ethernet = "\
    ethtool \
    bridge-utils \
    vlan \
    net-tools \
    tcpdump \
    wireshark-cli \
    iperf3 \
    netcat \
    socat \
"