# wifi_manager.py - WiFi management for TRT devices

import os
import subprocess
import json

class WiFiManager:
    def __init__(self):
        self.config_file = "/etc/wpa_supplicant/wpa_supplicant.conf"
        self.backup_config = "/boot/wpa_supplicant.conf.backup"
        
    def get_available_networks(self):
        """Scan for available WiFi networks"""
        try:
            result = subprocess.run(['iwlist', 'scan'], 
                                  capture_output=True, text=True)
            # Parse scan results (simplified)
            networks = []
            lines = result.stdout.split('\n')
            for line in lines:
                if 'ESSID:' in line:
                    ssid = line.split('ESSID:')[1].strip().strip('"')
                    if ssid and ssid != '':
                        networks.append(ssid)
            return networks
        except Exception as e:
            print(f"Error scanning networks: {e}")
            return []
    
    def get_saved_networks(self):
        """Get list of saved WiFi networks from config"""
        networks = []
        try:
            with open(self.config_file, 'r') as f:
                content = f.read()
                # Simple parsing of wpa_supplicant.conf
                lines = content.split('\n')
                current_network = {}
                for line in lines:
                    line = line.strip()
                    if line.startswith('network={'):
                        current_network = {}
                    elif line.startswith('ssid='):
                        current_network['ssid'] = line.split('=')[1].strip('"')
                    elif line.startswith('priority='):
                        current_network['priority'] = int(line.split('=')[1])
                    elif line == '}' and current_network:
                        networks.append(current_network)
                        current_network = {}
        except Exception as e:
            print(f"Error reading WiFi config: {e}")
        
        return sorted(networks, key=lambda x: x.get('priority', 0))
    
    def add_network(self, ssid, password, priority=5):
        """Add a new WiFi network to configuration"""
        try:
            network_block = f"""
network={{
    ssid="{ssid}"
    psk="{password}"
    priority={priority}
}}
"""
            with open(self.config_file, 'a') as f:
                f.write(network_block)
            
            # Restart wpa_supplicant to apply changes
            subprocess.run(['systemctl', 'restart', 'wpa_supplicant'])
            return True
        except Exception as e:
            print(f"Error adding network: {e}")
            return False
    
    def connect_to_network(self, ssid):
        """Attempt to connect to a specific network"""
        try:
            # Use wpa_cli to connect
            subprocess.run(['wpa_cli', 'select_network', ssid])
            return True
        except Exception as e:
            print(f"Error connecting to {ssid}: {e}")
            return False
    
    def get_current_connection(self):
        """Get currently connected network info"""
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'ESSID:' in line:
                    ssid = line.split('ESSID:')[1].strip().strip('"')
                    if ssid and ssid != 'off/any':
                        return ssid
            return None
        except Exception as e:
            print(f"Error getting current connection: {e}")
            return None
    
    def get_signal_strength(self):
        """Get WiFi signal strength"""
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Signal level=' in line:
                    # Extract signal level
                    signal = line.split('Signal level=')[1].split()[0]
                    return signal
            return "Unknown"
        except Exception as e:
            print(f"Error getting signal strength: {e}")
            return "Unknown"
    
    def restore_backup_config(self):
        """Restore WiFi config from backup"""
        try:
            if os.path.exists(self.backup_config):
                subprocess.run(['cp', self.backup_config, self.config_file])
                subprocess.run(['systemctl', 'restart', 'wpa_supplicant'])
                return True
            return False
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False