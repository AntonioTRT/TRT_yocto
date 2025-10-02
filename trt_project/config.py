# config.py - System constants

# Basic configuration
NOMBRE_PROGRAMA = "TRT Project"
VERSION = "1.0"
PUERTO = 8080

# Parameters
TEMPERATURA_MAXIMA = 25
NUMERO_X = 10
NUMERO_Y = 20

# WiFi configuration
WIFI_SCAN_INTERVAL = 30  # seconds
WIFI_RETRY_ATTEMPTS = 3
WIFI_CONNECTION_TIMEOUT = 10  # seconds

# Default WiFi networks (will be included in Yocto image)
DEFAULT_WIFI_NETWORKS = [
    {
        "ssid": "TRT_FACTORY",
        "password": "factory123",
        "priority": 1
    },
    {
        "ssid": "TRT_OFFICE", 
        "password": "office456",
        "priority": 2
    },
    {
        "ssid": "TRT_GUEST",
        "password": "guest789",
        "priority": 3
    }
]