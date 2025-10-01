SUMMARY = "Industrial monitoring and control software"
DESCRIPTION = "Package group for industrial monitoring, control systems, and data acquisition"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

PROVIDES = "${PACKAGES}"
PACKAGES = "\
    ${PN} \
    ${PN}-monitoring \
    ${PN}-control \
    ${PN}-data \
"

RDEPENDS_${PN} = "\
    ${PN}-monitoring \
    ${PN}-control \
    ${PN}-data \
"

RDEPENDS_${PN}-monitoring = "\
    collectd \
    telegraf \
    node-exporter \
    snmp \
    net-snmp \
    net-snmp-client \
    net-snmp-server \
    zabbix-agent \
    nagios-nrpe \
"

RDEPENDS_${PN}-control = "\
    python3-rpi-gpio \
    python3-gpiozero \
    python3-pyserial \
    socat \
    minicom \
    picocom \
    screen \
"

RDEPENDS_${PN}-data = "\
    sqlite3 \
    influxdb \
    redis \
    postgresql \
    mysql \
    mongodb \
    grafana \
    chronograf \
"