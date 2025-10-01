#!/bin/bash

# TRT Industrial Network Configuration Script
# This script configures network interfaces for industrial use

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="/opt/trt/config"
LOG_FILE="/var/log/trt/network-config.log"

# Ensure directories exist
mkdir -p "$CONFIG_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Starting TRT Industrial Network Configuration"

# Configure static IP for industrial network
configure_industrial_network() {
    local interface="eth0"
    local ip="192.168.100.10"
    local netmask="255.255.255.0"
    local gateway="192.168.100.1"
    
    log "Configuring industrial network interface $interface"
    
    cat > /etc/systemd/network/10-industrial.network << EOF
[Match]
Name=$interface

[Network]
Address=$ip/24
Gateway=$gateway
DNS=8.8.8.8
DNS=8.8.4.4

[Route]
Destination=192.168.0.0/16
Gateway=$gateway
EOF

    systemctl restart systemd-networkd
    log "Industrial network configured: $ip"
}

# Configure WiFi for maintenance access
configure_maintenance_wifi() {
    local ssid="TRT-Maintenance"
    local psk="TRT@2025!"
    
    log "Configuring maintenance WiFi: $ssid"
    
    cat > /etc/wpa_supplicant/wpa_supplicant-wlan0.conf << EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="$ssid"
    psk="$psk"
    key_mgmt=WPA-PSK
    priority=1
}

network={
    ssid="TRT-Field"
    psk="FieldAccess2025"
    key_mgmt=WPA-PSK
    priority=2
}
EOF

    chmod 600 /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
    systemctl enable wpa_supplicant@wlan0
    systemctl start wpa_supplicant@wlan0
    
    log "Maintenance WiFi configured"
}

# Configure industrial protocols
configure_industrial_protocols() {
    log "Configuring industrial protocols"
    
    # Configure Modbus
    cat > "$CONFIG_DIR/modbus.conf" << EOF
# Modbus TCP Configuration
port=502
max_connections=10
timeout=5

# Modbus RTU Configuration
device=/dev/ttyUSB0
baudrate=9600
parity=N
databits=8
stopbits=1
EOF

    # Configure MQTT
    cat > "$CONFIG_DIR/mqtt.conf" << EOF
# MQTT Broker Configuration
listener 1883
protocol mqtt

# Authentication
allow_anonymous false
password_file /opt/trt/config/passwd

# Logging
log_dest file /var/log/trt/mosquitto.log
log_type all

# Persistence
persistence true
persistence_location /opt/trt/data/
EOF

    # Configure OPC-UA
    cat > "$CONFIG_DIR/opcua.conf" << EOF
# OPC-UA Server Configuration
port=4840
max_clients=100
security_policy=None

# Certificate configuration
certificate=/opt/trt/config/server-cert.pem
private_key=/opt/trt/config/server-key.pem

# Endpoints
endpoint_url=opc.tcp://0.0.0.0:4840/
EOF

    log "Industrial protocols configured"
}

# Configure firewall for industrial use
configure_firewall() {
    log "Configuring industrial firewall"
    
    # Reset iptables
    iptables -F
    iptables -X
    iptables -t nat -F
    iptables -t nat -X
    iptables -t mangle -F
    iptables -t mangle -X
    
    # Default policies
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT
    
    # Allow loopback
    iptables -A INPUT -i lo -j ACCEPT
    
    # Allow established connections
    iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    
    # Allow SSH (port 22)
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    
    # Allow industrial protocols
    iptables -A INPUT -p tcp --dport 502 -j ACCEPT    # Modbus TCP
    iptables -A INPUT -p tcp --dport 1883 -j ACCEPT   # MQTT
    iptables -A INPUT -p tcp --dport 4840 -j ACCEPT   # OPC-UA
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT     # HTTP
    iptables -A INPUT -p tcp --dport 443 -j ACCEPT    # HTTPS
    
    # Allow ICMP (ping)
    iptables -A INPUT -p icmp -j ACCEPT
    
    # Allow DHCP client
    iptables -A INPUT -p udp --sport 67 --dport 68 -j ACCEPT
    
    # Save iptables rules
    iptables-save > /etc/iptables/rules.v4
    
    log "Firewall configured for industrial use"
}

# Configure time synchronization
configure_time_sync() {
    log "Configuring time synchronization"
    
    cat > /etc/chrony/chrony.conf << EOF
# Use public NTP servers
server 0.pool.ntp.org iburst
server 1.pool.ntp.org iburst
server 2.pool.ntp.org iburst
server 3.pool.ntp.org iburst

# Industrial time server (if available)
# server 192.168.100.1 iburst prefer

# Configuration options
driftfile /var/lib/chrony/chrony.drift
rtcsync
makestep 1 3
maxupdateskew 100.0

# Logging
logdir /var/log/chrony
log measurements statistics tracking
EOF

    systemctl enable chronyd
    systemctl restart chronyd
    
    log "Time synchronization configured"
}

# Main configuration function
main() {
    log "TRT Industrial Network Configuration Started"
    
    configure_industrial_network
    configure_maintenance_wifi
    configure_industrial_protocols
    configure_firewall
    configure_time_sync
    
    log "TRT Industrial Network Configuration Completed"
    log "System ready for industrial operation"
    
    # Display network status
    echo ""
    echo "Network Configuration Summary:"
    echo "=============================="
    ip addr show | grep -E "(inet|state UP)"
    echo ""
    echo "Industrial services status:"
    systemctl status mosquitto chronyd | grep Active
}

# Run main function
main "$@"