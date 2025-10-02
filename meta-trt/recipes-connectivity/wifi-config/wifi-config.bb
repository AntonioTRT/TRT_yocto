SUMMARY = "TRT WiFi Configuration"
DESCRIPTION = "Pre-configured WiFi settings for TRT devices"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

SRC_URI = "file://wpa_supplicant.conf"

S = "${WORKDIR}"

do_install() {
    install -d ${D}${sysconfdir}/wpa_supplicant
    install -m 0600 ${WORKDIR}/wpa_supplicant.conf ${D}${sysconfdir}/wpa_supplicant/
    
    # También crear un backup en /boot para fácil acceso
    install -d ${D}/boot
    install -m 0644 ${WORKDIR}/wpa_supplicant.conf ${D}/boot/wpa_supplicant.conf.backup
}

FILES_${PN} = "${sysconfdir}/wpa_supplicant/wpa_supplicant.conf /boot/wpa_supplicant.conf.backup"

# Asegurar que se instalen los paquetes necesarios
RDEPENDS_${PN} = "wpa-supplicant"