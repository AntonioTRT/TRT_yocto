#!/bin/bash

# Script de inicio para Mi Programa de Control Industrial
# Desarrollado por Antonio TRT

set -e

# Configuración
PROGRAM_NAME="Mi Programa de Control TRT"
PYTHON_SCRIPT="/usr/bin/mi-programa-control.py"
CONFIG_FILE="/etc/trt/config.json"
LOG_DIR="/opt/trt/mi-programa/logs"
DATA_DIR="/opt/trt/mi-programa/data"
PID_FILE="/var/run/trt-control.pid"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar prerequisitos
check_prerequisites() {
    log "Verificando prerequisitos..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 no encontrado"
        exit 1
    fi
    
    # Verificar librerías Python
    for lib in pymodbus paho.mqtt.client; do
        if ! python3 -c "import $lib" &> /dev/null; then
            error "Librería Python '$lib' no encontrada"
            exit 1
        fi
    done
    
    # Verificar archivo de configuración
    if [ ! -f "$CONFIG_FILE" ]; then
        error "Archivo de configuración no encontrado: $CONFIG_FILE"
        exit 1
    fi
    
    # Crear directorios necesarios
    mkdir -p "$LOG_DIR" "$DATA_DIR"
    
    success "Prerequisitos verificados"
}

# Configurar hardware
setup_hardware() {
    log "Configurando hardware..."
    
    # Configurar GPIO (si es Raspberry Pi)
    if [ -f /proc/device-tree/model ] && grep -q "Raspberry Pi" /proc/device-tree/model; then
        log "Detectado Raspberry Pi"
        # Habilitar interfaces
        if [ -f /boot/config.txt ]; then
            grep -q "dtparam=spi=on" /boot/config.txt || echo "dtparam=spi=on" >> /boot/config.txt
            grep -q "dtparam=i2c_arm=on" /boot/config.txt || echo "dtparam=i2c_arm=on" >> /boot/config.txt
        fi
    fi
    
    # Configurar CAN (si existe)
    if [ -d /sys/class/net/can0 ]; then
        log "Configurando interfaz CAN..."
        ip link set can0 type can bitrate 125000 || warning "Error configurando CAN"
        ip link set up can0 || warning "Error activando CAN"
    fi
    
    success "Hardware configurado"
}

# Verificar conectividad
check_connectivity() {
    log "Verificando conectividad..."
    
    # Leer configuración
    modbus_host=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config['modbus']['host'])")
    mqtt_broker=$(python3 -c "import json; config=json.load(open('$CONFIG_FILE')); print(config['mqtt']['broker'])")
    
    # Verificar Modbus
    if timeout 5 nc -z "$modbus_host" 502 &> /dev/null; then
        success "Modbus server accesible: $modbus_host:502"
    else
        warning "Modbus server no accesible: $modbus_host:502"
    fi
    
    # Verificar MQTT
    if timeout 5 nc -z "$mqtt_broker" 1883 &> /dev/null; then
        success "MQTT broker accesible: $mqtt_broker:1883"
    else
        warning "MQTT broker no accesible: $mqtt_broker:1883"
    fi
}

# Iniciar programa
start_program() {
    log "Iniciando $PROGRAM_NAME..."
    
    # Verificar si ya está ejecutándose
    if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
        error "El programa ya está ejecutándose (PID: $(cat $PID_FILE))"
        exit 1
    fi
    
    # Iniciar programa
    nohup python3 "$PYTHON_SCRIPT" > "$LOG_DIR/startup.log" 2>&1 &
    echo $! > "$PID_FILE"
    
    # Verificar que inició correctamente
    sleep 2
    if kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
        success "$PROGRAM_NAME iniciado (PID: $(cat $PID_FILE))"
    else
        error "Error iniciando $PROGRAM_NAME"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Función principal
main() {
    log "=== Iniciando $PROGRAM_NAME ==="
    
    check_prerequisites
    setup_hardware
    check_connectivity
    start_program
    
    log "=== Inicio completado ==="
}

# Ejecutar función principal
main "$@"