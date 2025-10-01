# Changelog

## [1.0.0] - 2025-10-01

### Added
- Initial release of TRT Yocto Project meta-layer
- Support for Raspberry Pi (all models)
- Support for BeagleBone Black/Industrial
- Support for NXP i.MX7
- Custom TRT distribution configuration
- Three image variants:
  - `trt-base-image`: Minimal industrial Linux
  - `trt-industrial-image`: Full industrial tools and protocols
  - `trt-development-image`: Development and debugging tools
- Industrial connectivity packages:
  - MQTT (Mosquitto)
  - Modbus (libmodbus, pymodbus)
  - OPC-UA (open62541, python-opcua)
- Network configuration scripts for industrial use
- Build automation scripts for all platforms
- Comprehensive documentation and setup guides
- WSL2 configuration examples for Windows users

### Features
- Systemd-based init system
- SSH access with configurable authentication
- WiFi and Bluetooth support
- Industrial I/O support (I2C, SPI, GPIO, CAN)
- Real-time kernel features
- Hardware watchdog configuration
- Time synchronization with Chrony
- Firewall configuration for industrial protocols
- Package management with RPM
- Build history and error reporting
- Security hardening with compiler flags

### Documentation
- Complete setup instructions for Linux and Windows
- Platform-specific configuration details
- Troubleshooting guide
- Build optimization recommendations
- Security considerations for production use

### Scripts
- `setup-environment.sh`: Automated environment setup
- `build-all-platforms.sh`: Multi-platform build automation
- `trt-network-config.sh`: Industrial network configuration