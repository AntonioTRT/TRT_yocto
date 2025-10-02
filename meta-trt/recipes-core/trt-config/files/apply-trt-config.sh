#!/bin/bash
# apply-trt-config.sh - Script to apply TRT configuration from trt-config.txt

CONFIG_FILE="/etc/trt/trt-config.txt"
WPA_CONFIG="/etc/wpa_supplicant/wpa_supplicant.conf"

echo "TRT Configuration Applying..."

# Function to read config value
get_config_value() {
    local key=$1
    grep "^${key}=" "$CONFIG_FILE" | cut -d'=' -f2 | tr -d '"'
}

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

echo "Reading configuration from $CONFIG_FILE"

# Read WiFi configuration
WIFI_PRIMARY_SSID=$(get_config_value "WIFI_PRIMARY_SSID")
WIFI_PRIMARY_PASSWORD=$(get_config_value "WIFI_PRIMARY_PASSWORD") 
WIFI_PRIMARY_PRIORITY=$(get_config_value "WIFI_PRIMARY_PRIORITY")

WIFI_SECONDARY_SSID=$(get_config_value "WIFI_SECONDARY_SSID")
WIFI_SECONDARY_PASSWORD=$(get_config_value "WIFI_SECONDARY_PASSWORD")
WIFI_SECONDARY_PRIORITY=$(get_config_value "WIFI_SECONDARY_PRIORITY")

WIFI_GUEST_SSID=$(get_config_value "WIFI_GUEST_SSID")
WIFI_GUEST_PASSWORD=$(get_config_value "WIFI_GUEST_PASSWORD")
WIFI_GUEST_PRIORITY=$(get_config_value "WIFI_GUEST_PRIORITY")

WIFI_COUNTRY=$(get_config_value "WIFI_COUNTRY")

# Generate wpa_supplicant.conf
echo "Generating WiFi configuration..."
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

# Guest WiFi Network
network={
    ssid="${WIFI_GUEST_SSID}"
    psk="${WIFI_GUEST_PASSWORD}"
    priority=${WIFI_GUEST_PRIORITY}
}
EOF

chmod 600 "$WPA_CONFIG"
echo "WiFi configuration written to $WPA_CONFIG"

# Apply timezone
TIMEZONE=$(get_config_value "TIMEZONE")
if [ -n "$TIMEZONE" ]; then
    echo "Setting timezone to $TIMEZONE"
    timedatectl set-timezone "$TIMEZONE" 2>/dev/null || true
fi

# Configure hostname
DEVICE_NAME=$(get_config_value "DEVICE_NAME")
if [ -n "$DEVICE_NAME" ]; then
    echo "Setting hostname to $DEVICE_NAME"
    hostnamectl set-hostname "$DEVICE_NAME" 2>/dev/null || true
fi

# Enable/disable services based on config
SSH_ENABLE=$(get_config_value "SSH_ENABLE")
if [ "$SSH_ENABLE" = "true" ]; then
    echo "Enabling SSH service"
    systemctl enable ssh 2>/dev/null || true
else
    echo "Disabling SSH service"
    systemctl disable ssh 2>/dev/null || true
fi

AUTOSTART_WIFI=$(get_config_value "AUTOSTART_WIFI")
if [ "$AUTOSTART_WIFI" = "true" ]; then
    echo "Enabling WiFi services"
    systemctl enable wpa_supplicant 2>/dev/null || true
    systemctl enable networking 2>/dev/null || true
fi

# Restart WiFi services to apply new configuration
echo "Restarting WiFi services..."
systemctl restart wpa_supplicant 2>/dev/null || true
systemctl restart networking 2>/dev/null || true

echo "TRT configuration applied successfully!"
echo "WiFi networks configured:"
echo "  Primary: $WIFI_PRIMARY_SSID (priority $WIFI_PRIMARY_PRIORITY)"
echo "  Secondary: $WIFI_SECONDARY_SSID (priority $WIFI_SECONDARY_PRIORITY)" 
echo "  Guest: $WIFI_GUEST_SSID (priority $WIFI_GUEST_PRIORITY)"