SUMMARY = "TRT Industrial Image - Full industrial Linux image"
DESCRIPTION = "Complete image with industrial tools, protocols, and monitoring capabilities"

require trt-base-image.bb

IMAGE_INSTALL += "\
    packagegroup-trt-base-industrial \
    mi-programa-control \
    modbus-tools \
    nodejs \
    node-red \
    influxdb \
    grafana \
    docker \
    lxc \
    openvpn \
    strongswan \
    nginx \
    postgresql \
    sqlite3 \
    redis \
    python3-django \
    python3-flask \
    python3-modbus-tk \
    python3-opcua \
    collectd \
    telegraf \
    fail2ban \
    ufw \
"

# Additional space for industrial software
IMAGE_ROOTFS_SIZE = "16384"

# Industrial-specific configurations
configure_industrial() {
    # Configure watchdog
    echo 'watchdog-device = /dev/watchdog' >> ${IMAGE_ROOTFS}/etc/watchdog.conf
    echo 'interval = 10' >> ${IMAGE_ROOTFS}/etc/watchdog.conf
    
    # Enable services
    systemctl --root=${IMAGE_ROOTFS} enable watchdog
    systemctl --root=${IMAGE_ROOTFS} enable ssh
    systemctl --root=${IMAGE_ROOTFS} enable chronyd
    systemctl --root=${IMAGE_ROOTFS} enable mosquitto
    
    # Create industrial directories
    install -d ${IMAGE_ROOTFS}/opt/trt
    install -d ${IMAGE_ROOTFS}/opt/trt/data
    install -d ${IMAGE_ROOTFS}/opt/trt/config
    install -d ${IMAGE_ROOTFS}/opt/trt/logs
    install -d ${IMAGE_ROOTFS}/var/log/trt
    
    # Configure log rotation
    echo '/var/log/trt/*.log {
        daily
        missingok
        rotate 52
        compress
        delaycompress
        notifempty
        create 644 root root
    }' > ${IMAGE_ROOTFS}/etc/logrotate.d/trt
}

ROOTFS_POSTPROCESS_COMMAND += "configure_industrial; "