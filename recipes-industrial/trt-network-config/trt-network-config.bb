SUMMARY = "TRT Industrial Network Configuration"
DESCRIPTION = "Network configuration scripts and tools for TRT industrial systems"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://trt-network-config.sh"

S = "${WORKDIR}"

do_install() {
    install -d ${D}${bindir}
    install -d ${D}${sysconfdir}/trt
    install -d ${D}${systemd_system_unitdir}
    
    install -m 0755 ${WORKDIR}/trt-network-config.sh ${D}${bindir}/
    
    # Create systemd service
    cat > ${D}${systemd_system_unitdir}/trt-network-config.service << EOF
[Unit]
Description=TRT Industrial Network Configuration
After=network.target
Wants=network.target

[Service]
Type=oneshot
ExecStart=${bindir}/trt-network-config.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
}

inherit systemd

SYSTEMD_SERVICE_${PN} = "trt-network-config.service"
SYSTEMD_AUTO_ENABLE = "enable"

FILES_${PN} += "${systemd_system_unitdir}/trt-network-config.service"
FILES_${PN} += "${bindir}/trt-network-config.sh"

RDEPENDS_${PN} = "bash systemd iptables chrony"