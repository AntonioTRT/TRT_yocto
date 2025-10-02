#!/bin/bash
# setup-wifi.sh - Automated WiFi setup script for TRT devices

WIFI_CONFIG="/etc/wpa_supplicant/wpa_supplicant.conf"
BACKUP_CONFIG="/boot/wpa_supplicant.conf.backup"

echo "TRT WiFi Setup Script"
echo "===================="

# Function to generate wpa_supplicant.conf
generate_wifi_config() {
    cat > "$WIFI_CONFIG" << EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

# TRT Factory Network (Priority 1)
network={
    ssid="TRT_FACTORY"
    psk="factory123"
    priority=1
}

# TRT Office Network (Priority 2) 
network={
    ssid="TRT_OFFICE"
    psk="office456"
    priority=2
}

# TRT Guest Network (Priority 3)
network={
    ssid="TRT_GUEST"
    psk="guest789"
    priority=3
}

# Customer WiFi (Priority 4) - To be configured by user
network={
    ssid="CUSTOMER_WIFI"
    psk="customer_password"
    priority=4
    disabled=1
}
EOF
}

# Check if WiFi config exists
if [ ! -f "$WIFI_CONFIG" ]; then
    echo "Creating WiFi configuration..."
    generate_wifi_config
    chmod 600 "$WIFI_CONFIG"
    echo "WiFi configuration created."
else
    echo "WiFi configuration already exists."
fi

# Create backup
if [ -f "$WIFI_CONFIG" ]; then
    cp "$WIFI_CONFIG" "$BACKUP_CONFIG"
    echo "Backup created at $BACKUP_CONFIG"
fi

# Enable and start WiFi services
echo "Enabling WiFi services..."
systemctl enable wpa_supplicant
systemctl enable networking
systemctl enable dhcpcd

# Start services
echo "Starting WiFi services..."
systemctl restart wpa_supplicant
systemctl restart networking
systemctl restart dhcpcd

echo "WiFi setup completed!"
echo "Available commands:"
echo "  iwconfig - Check WiFi status"
echo "  iwlist scan - Scan for networks" 
echo "  wpa_cli - Manage WiFi connections"