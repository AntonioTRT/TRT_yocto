SUMMARY = "TRT base package group"
DESCRIPTION = "Basic packages for TRT industrial systems"

PACKAGE_ARCH = "${MACHINE_ARCH}"

inherit packagegroup

PROVIDES = "${PACKAGES}"
PACKAGES = "\
    ${PN} \
    ${PN}-base \
    ${PN}-connectivity \
    ${PN}-industrial \
    ${PN}-development \
"

RDEPENDS_${PN} = "\
    ${PN}-base \
    ${PN}-connectivity \
    ${PN}-industrial \
"

RDEPENDS_${PN}-base = "\
    base-files \
    base-passwd \
    busybox \
    init-ifupdown \
    initscripts \
    kernel-modules \
    modutils-initscripts \
    netbase \
    update-alternatives \
    sysvinit \
    tinylogin \
    udev \
    util-linux \
    systemd \
    systemd-compat-units \
    dbus \
"

RDEPENDS_${PN}-connectivity = "\
    openssh \
    openssh-sftp-server \
    wpa-supplicant \
    iw \
    wireless-tools \
    bluez5 \
    can-utils \
    ethtool \
    iptables \
    curl \
    wget \
    mosquitto \
    mosquitto-clients \
    bridge-utils \
    dhcp-client \
    ntp \
    avahi-daemon \
    avahi-utils \
"

RDEPENDS_${PN}-industrial = "\
    watchdog \
    i2c-tools \
    spi-tools \
    gpio-utils \
    devmem2 \
    memtester \
    stress-ng \
    htop \
    iotop \
    tcpdump \
    strace \
    gdb \
    python3 \
    python3-pip \
    python3-pyserial \
    python3-paho-mqtt \
    python3-numpy \
    python3-requests \
    logrotate \
    rsyslog \
    chrony \
"

RDEPENDS_${PN}-development = "\
    gcc \
    g++ \
    make \
    cmake \
    git \
    vim \
    nano \
    tree \
    file \
    lsof \
    screen \
    tmux \
    valgrind \
    perf \
    binutils \
    glibc-utils \
    python3-dev \
    python3-setuptools \
    pkg-config \
"