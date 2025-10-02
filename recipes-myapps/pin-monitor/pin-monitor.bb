SUMMARY = "TRT Pin Monitor - Monitor de pines industrial multiplataforma"
DESCRIPTION = "Sistema de monitoreo de pines GPIO con soporte para Raspberry Pi, BeagleBone y i.MX7"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "\
    file://pin-config.py \
    file://monitor-pins.py \
    file://pin-monitor-config.json \
    file://pin-monitor.service \
    file://pin-config.service \
"

S = "${WORKDIR}"

# Dependencias específicas por plataforma
RDEPENDS_${PN} = "\
    python3 \
    python3-flask \
    python3-paho-mqtt \
    python3-json \
    python3-sqlite3 \
    python3-threading \
    python3-datetime \
    python3-pathlib \
"

# Dependencias específicas para Raspberry Pi
RDEPENDS_${PN}_append_raspberrypi = "\
    python3-rpi-gpio \
    python3-spidev \
    python3-smbus \
"

# Dependencias específicas para BeagleBone
RDEPENDS_${PN}_append_beaglebone = "\
    python3-adafruit-bbio \
    python3-adafruit-gpio \
"

# Dependencias específicas para i.MX7
RDEPENDS_${PN}_append_imx = "\
    python3-periphery \
    python3-gpiod \
"

do_install() {
    # Crear directorios
    install -d ${D}${bindir}
    install -d ${D}${sysconfdir}/trt
    install -d ${D}${systemd_system_unitdir}
    install -d ${D}/opt/trt/pin-monitor
    install -d ${D}/opt/trt/logs
    install -d ${D}/opt/trt/data
    install -d ${D}/opt/trt/config
    
    # Instalar archivos Python
    install -m 0755 ${WORKDIR}/pin-config.py ${D}${bindir}/
    install -m 0755 ${WORKDIR}/monitor-pins.py ${D}${bindir}/
    
    # Crear enlaces simbólicos para importar
    ln -sf ${bindir}/pin-config.py ${D}/opt/trt/pin-monitor/pin_config.py
    
    # Instalar configuración
    install -m 0644 ${WORKDIR}/pin-monitor-config.json ${D}${sysconfdir}/trt/
    
    # Instalar servicios systemd
    install -m 0644 ${WORKDIR}/pin-monitor.service ${D}${systemd_system_unitdir}/
    install -m 0644 ${WORKDIR}/pin-config.service ${D}${systemd_system_unitdir}/
    
    # Crear script de inicio
    cat > ${D}${bindir}/start-pin-monitor.sh << 'EOF'
#!/bin/bash

# TRT Pin Monitor Startup Script

echo "🔌 Iniciando TRT Pin Monitor..."

# Detectar plataforma y mostrar configuración
echo "📋 Detectando plataforma..."
python3 ${bindir}/pin-config.py

# Esperar un momento
sleep 2

# Iniciar monitor principal
echo "🚀 Iniciando monitor de pines..."
cd /opt/trt/pin-monitor
export PYTHONPATH=/opt/trt/pin-monitor:$PYTHONPATH
python3 ${bindir}/monitor-pins.py

EOF
    
    chmod +x ${D}${bindir}/start-pin-monitor.sh
    
    # Crear script de configuración interactiva
    cat > ${D}${bindir}/configure-pins.sh << 'EOF'
#!/bin/bash

# TRT Pin Configuration Interactive Script

echo "═══════════════════════════════════════════════════════"
echo "         TRT - CONFIGURACIÓN INTERACTIVA DE PINES"
echo "═══════════════════════════════════════════════════════"

# Detectar plataforma
python3 ${bindir}/pin-config.py

echo ""
echo "Configuración guardada en /opt/trt/config/"
echo ""
echo "Para monitorear pines en tiempo real:"
echo "  systemctl start pin-monitor"
echo ""
echo "Para ver el dashboard web:"
echo "  http://$(hostname -I | awk '{print $1}'):5001"
echo ""
echo "Para ver logs:"
echo "  journalctl -u pin-monitor -f"

EOF
    
    chmod +x ${D}${bindir}/configure-pins.sh
}

inherit systemd

SYSTEMD_SERVICE_${PN} = "pin-monitor.service pin-config.service"
SYSTEMD_AUTO_ENABLE = "enable"

FILES_${PN} += "\
    ${bindir}/pin-config.py \
    ${bindir}/monitor-pins.py \
    ${bindir}/start-pin-monitor.sh \
    ${bindir}/configure-pins.sh \
    ${sysconfdir}/trt/pin-monitor-config.json \
    ${systemd_system_unitdir}/pin-monitor.service \
    ${systemd_system_unitdir}/pin-config.service \
    /opt/trt/pin-monitor \
    /opt/trt/logs \
    /opt/trt/data \
    /opt/trt/config \
"

# Crear usuario específico para el servicio
USERADD_PACKAGES = "${PN}"
USERADD_PARAM_${PN} = "--system --home /opt/trt --shell /bin/false --user-group trt"

pkg_postinst_${PN}() {
    if [ -n "$D" ]; then
        exit 1
    fi
    
    # Establecer permisos
    chown -R trt:trt /opt/trt
    chmod -R 755 /opt/trt
    
    # Habilitar servicios
    systemctl daemon-reload
    systemctl enable pin-config.service
    systemctl enable pin-monitor.service
    
    echo "TRT Pin Monitor instalado correctamente"
    echo "Comandos disponibles:"
    echo "  configure-pins.sh  - Configuración interactiva"
    echo "  start-pin-monitor.sh - Inicio manual"
    echo "  systemctl start pin-monitor - Inicio como servicio"
}