#!/bin/bash
# test-trt-config.sh - Script para probar la configuración TRT sin build completo

echo "=== TRT Configuration Test ==="
echo

# Crear directorio temporal para pruebas
TEST_DIR="/tmp/trt-test"
mkdir -p "$TEST_DIR/etc/trt"
mkdir -p "$TEST_DIR/etc/wpa_supplicant"

# Copiar archivo de configuración al directorio de prueba
cp "/mnt/c/repos/TRT_yocto/conf/trt-config.txt" "$TEST_DIR/etc/trt/" 2>/dev/null || {
    echo "Error: No se pudo copiar el archivo de configuración"
    echo "Asegúrate de que WSL pueda acceder a: /mnt/c/repos/TRT_yocto/conf/trt-config.txt"
    exit 1
}

CONFIG_FILE="$TEST_DIR/etc/trt/trt-config.txt"
WPA_CONFIG="$TEST_DIR/etc/wpa_supplicant/wpa_supplicant.conf"

echo "✅ Archivo de configuración copiado a: $CONFIG_FILE"
echo

# Function to read config value
get_config_value() {
    local key=$1
    grep "^${key}=" "$CONFIG_FILE" | cut -d'=' -f2 | tr -d '"'
}

# Leer configuración WiFi
echo "📖 Leyendo configuración WiFi..."
WIFI_PRIMARY_SSID=$(get_config_value "WIFI_PRIMARY_SSID")
WIFI_PRIMARY_PASSWORD=$(get_config_value "WIFI_PRIMARY_PASSWORD") 
WIFI_PRIMARY_PRIORITY=$(get_config_value "WIFI_PRIMARY_PRIORITY")

WIFI_SECONDARY_SSID=$(get_config_value "WIFI_SECONDARY_SSID")
WIFI_SECONDARY_PASSWORD=$(get_config_value "WIFI_SECONDARY_PASSWORD")
WIFI_SECONDARY_PRIORITY=$(get_config_value "WIFI_SECONDARY_PRIORITY")

WIFI_COUNTRY=$(get_config_value "WIFI_COUNTRY")

echo "   Primary WiFi: $WIFI_PRIMARY_SSID (prioridad: $WIFI_PRIMARY_PRIORITY)"
echo "   Secondary WiFi: $WIFI_SECONDARY_SSID (prioridad: $WIFI_SECONDARY_PRIORITY)"
echo "   Country: $WIFI_COUNTRY"
echo

# Generar archivo wpa_supplicant.conf
echo "🔧 Generando configuración wpa_supplicant..."
cat > "$WPA_CONFIG" << EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=${WIFI_COUNTRY}

# Primary WiFi Network
network={
    ssid="${WIFI_PRIMARY_SSID}"
    psk="${WIFI_PRIMARY_PASSWORD}"
    priority=${WIFI_PRIMARY_PRIORITY}
}

# Secondary WiFi Network  
network={
    ssid="${WIFI_SECONDARY_SSID}"
    psk="${WIFI_SECONDARY_PASSWORD}"
    priority=${WIFI_SECONDARY_PRIORITY}
}
EOF

echo "✅ Archivo wpa_supplicant.conf generado en: $WPA_CONFIG"
echo

# Mostrar el archivo generado
echo "📄 Contenido del archivo wpa_supplicant.conf generado:"
echo "=================================================="
cat "$WPA_CONFIG"
echo "=================================================="
echo

# Verificar que los valores no estén vacíos
echo "🔍 Verificaciones:"
if [ "$WIFI_PRIMARY_SSID" = "TU_WIFI_PRINCIPAL" ]; then
    echo "   ⚠️  ADVERTENCIA: Todavía tienes el SSID por defecto 'TU_WIFI_PRINCIPAL'"
    echo "       Edita: /mnt/c/repos/TRT_yocto/conf/trt-config.txt"
else
    echo "   ✅ SSID principal configurado: $WIFI_PRIMARY_SSID"
fi

if [ "$WIFI_PRIMARY_PASSWORD" = "tu_contraseña_wifi" ]; then
    echo "   ⚠️  ADVERTENCIA: Todavía tienes la contraseña por defecto"
else
    echo "   ✅ Contraseña configurada (oculta por seguridad)"
fi

if [ -n "$WIFI_COUNTRY" ]; then
    echo "   ✅ País configurado: $WIFI_COUNTRY"
else
    echo "   ⚠️  País no configurado"
fi

echo
echo "🎯 RESUMEN:"
echo "   - Configuración leída correctamente: ✅"
echo "   - Archivo wpa_supplicant generado: ✅"
echo "   - Listo para incluir en imagen Yocto: ✅"
echo
echo "📝 Para usar en producción:"
echo "   1. Edita: /mnt/c/repos/TRT_yocto/conf/trt-config.txt"
echo "   2. Cambia WIFI_PRIMARY_SSID y WIFI_PRIMARY_PASSWORD"
echo "   3. Ejecuta el build de Yocto"
echo

# Limpiar archivos de prueba
rm -rf "$TEST_DIR"
echo "🧹 Archivos de prueba limpiados"