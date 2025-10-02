SUMMARY = "TRT System Configuration Package"
DESCRIPTION = "Reads TRT configuration file and applies system settings"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

SRC_URI = "file://trt-config.txt \
           file://apply-trt-config.sh \
           file://configure-hardware.sh \
           file://trt-config.service"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE_${PN} = "trt-config.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_install() {
    # Install configuration file
    install -d ${D}${sysconfdir}/trt
    install -m 0644 ${WORKDIR}/trt-config.txt ${D}${sysconfdir}/trt/
    
    # Install configuration script
    install -d ${D}${bindir}
    install -m 0755 ${WORKDIR}/apply-trt-config.sh ${D}${bindir}/
    install -m 0755 ${WORKDIR}/configure-hardware.sh ${D}${bindir}/
    
    # Install systemd service
    install -d ${D}${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/trt-config.service ${D}${systemd_unitdir}/system/
    
    # Create WiFi config directory
    install -d ${D}${sysconfdir}/wpa_supplicant
    
    # Create application directories
    install -d ${D}/opt/trt/data
    install -d ${D}/opt/trt/config
}

FILES_${PN} = "${sysconfdir}/trt/trt-config.txt \
               ${bindir}/apply-trt-config.sh \
               ${bindir}/configure-hardware.sh \
               ${systemd_unitdir}/system/trt-config.service \
               /opt/trt/data \
               /opt/trt/config"

RDEPENDS_${PN} = "wpa-supplicant systemd bash arduino-drivers"