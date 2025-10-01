SUMMARY = "Mi programa de control industrial personalizado"
DESCRIPTION = "Programa desarrollado por Antonio TRT para control de procesos industriales"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

# Archivos fuente de tu programa
SRC_URI = "\
    file://mi-programa-control.py \
    file://config.json \
    file://mi-programa.service \
    file://start-programa.sh \
"

S = "${WORKDIR}"

# Dependencias de tu programa
RDEPENDS_${PN} = "\
    python3 \
    python3-pymodbus \
    python3-paho-mqtt \
    python3-requests \
    python3-json \
"

do_install() {
    # Instalar tu programa
    install -d ${D}${bindir}
    install -d ${D}${sysconfdir}/trt
    install -d ${D}${systemd_system_unitdir}
    install -d ${D}/opt/trt/mi-programa
    
    # Copiar archivos
    install -m 0755 ${WORKDIR}/mi-programa-control.py ${D}${bindir}/
    install -m 0755 ${WORKDIR}/start-programa.sh ${D}${bindir}/
    install -m 0644 ${WORKDIR}/config.json ${D}${sysconfdir}/trt/
    install -m 0644 ${WORKDIR}/mi-programa.service ${D}${systemd_system_unitdir}/
    
    # Crear directorios de trabajo
    install -d ${D}/opt/trt/mi-programa/logs
    install -d ${D}/opt/trt/mi-programa/data
}

inherit systemd

SYSTEMD_SERVICE_${PN} = "mi-programa.service"
SYSTEMD_AUTO_ENABLE = "enable"

FILES_${PN} += "\
    ${bindir}/mi-programa-control.py \
    ${bindir}/start-programa.sh \
    ${sysconfdir}/trt/config.json \
    ${systemd_system_unitdir}/mi-programa.service \
    /opt/trt/mi-programa \
"