# Raspberry Pi Network Cable Tester

A comprehensive Python application to test network connectivity between a Raspberry Pi's built-in network interface and a USB-to-RJ45 adapter. The program automatically detects interfaces, performs continuous ping tests, and provides visual feedback via LED indicators.

## Features

- **Automatic Interface Detection**: Automatically identifies the built-in network interface and USB adapter
- **Continuous Testing**: Performs continuous ping tests between the two interfaces
- **LED Indicators**: 
  - Green LED lights when ping is successful
  - Red LED blinks and stays lit when ping fails
- **Auto-Restart on Hardware Changes**: Automatically restarts when USB adapter is removed or inserted into a different USB port
- **Console Logging**: Detailed test results and statistics printed to console
- **Boot Startup**: Configured to start automatically at system boot via systemd
- **Graceful Shutdown**: Properly cleans up GPIO on exit (Ctrl+C)

## Hardware Requirements

- Raspberry Pi (tested on Pi 3/4/5)
- Built-in Ethernet interface or USB Ethernet adapter as primary interface
- USB-to-RJ45 Ethernet adapter (secondary interface)
- Green LED with current-limiting resistor (~330Ω)
- Red LED with current-limiting resistor (~330Ω)
- 2x Network cables (one for primary, one for USB adapter)

## GPIO Wiring

Default GPIO pin assignments (can be modified in the script):

```
GPIO 17 (BCM 17, Pin 11) ──[330Ω resistor]──> Green LED ──> GND
GPIO 27 (BCM 27, Pin 13) ──[330Ω resistor]──> Red LED ──> GND
```

### Raspberry Pi GPIO Layout
```
3V3  (1) (2)  5V
GPIO 2 (SDA) (3) (4)  5V
GPIO 3 (SCL) (5) (6)  GND
GPIO 4 (7) (8)  GPIO 14 (TXD)
GND  (9) (10) GPIO 15 (RXD)
GPIO 17 (11) (12) GPIO 18 (PWM0)
GPIO 27 (13) (14) GND
GPIO 22 (15) (16) GPIO 23
3V3  (17) (18) GPIO 24
GPIO 10 (MOSI) (19) (20) GND
GPIO 9 (MISO) (21) (22) GPIO 25
GPIO 11 (SCLK) (23) (24) GPIO 8 (CE0)
GND  (25) (26) GPIO 7 (CE1)
ID_SD (27) (28) ID_SC
GPIO 5 (29) (30) GND
GPIO 6 (31) (32) GPIO 12 (PWM0)
GPIO 13 (PWM1) (33) (34) GND
GPIO 19 (PWM1) (35) (36) GPIO 16
GPIO 26 (37) (38) GPIO 20
GND  (39) (40) GPIO 21
```

## Network Configuration

The program requires both network interfaces to have IP addresses configured. Configure them via:

### Using netplan (Ubuntu/Debian)
```yaml
# /etc/netplan/01-netcfg.yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
    eth1:
      dhcp4: true
```

### Using /etc/network/interfaces (Raspbian)
```
auto eth0
iface eth0 inet dhcp

auto eth1
iface eth1 inet dhcp
```

Or for static IPs:
```
auto eth0
iface eth0 inet static
    address 192.168.1.10
    netmask 255.255.255.0

auto eth1
iface eth1 inet static
    address 192.168.1.11
    netmask 255.255.255.0
```

## Installation

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/barnovongurka/rpi-network-cable-tester.git
cd rpi-network-cable-tester

# Make the install script executable
chmod +x install.sh

# Run the installer with sudo
sudo ./install.sh
```

### Option 2: Manual Installation

1. **Install dependencies:**
   ```bash
   sudo pip3 install -r requirements.txt
   ```

2. **Copy files:**
   ```bash
   sudo mkdir -p /home/pi/rpi-network-cable-tester
   sudo cp network_cable_tester.py /home/pi/rpi-network-cable-tester/
   sudo chown -R pi:pi /home/pi/rpi-network-cable-tester
   sudo chmod 755 /home/pi/rpi-network-cable-tester/network_cable_tester.py
   ```

3. **Install systemd service:**
   ```bash
   sudo cp network-cable-tester.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable network-cable-tester.service
   ```

## Usage

### Start the Service
```bash
sudo systemctl start network-cable-tester.service
```

### View Live Logs
```bash
sudo journalctl -u network-cable-tester.service -f
```

### Stop the Service
```bash
sudo systemctl stop network-cable-tester.service
```

### Disable Auto-start
```bash
sudo systemctl disable network-cable-tester.service
```

### Run Manually (for testing)
```bash
cd /home/pi/rpi-network-cable-tester
python3 network_cable_tester.py
```

## Configuration

Edit the configuration in `network_cable_tester.py`:

```python
# GPIO Pin Configuration
GREEN_LED_PIN = 17  # Change to your GPIO pin
RED_LED_PIN = 27    # Change to your GPIO pin

# Test Configuration
PING_COUNT = 1              # Number of ping packets per test
PING_TIMEOUT = 2            # Timeout in seconds per ping
TEST_INTERVAL = 2           # Seconds between tests
BLINK_DURATION = 0.1        # LED blink duration in seconds
INTERFACE_CHECK_INTERVAL = 5  # Check for interface changes every N tests
```

## Output Example

```
============================================================
RASPBERRY PI NETWORK CABLE TESTER
============================================================
[INFO] Auto-detecting network interfaces...

============================================================
DETECTED NETWORK INTERFACES
============================================================
Primary (Built-in): eth0
  IP Address: 192.168.1.10
  Driver: smsc95xx

USB Adapter: eth1
  IP Address: 192.168.1.11
  Driver: asix

All Interfaces: eth0, eth1
============================================================

[CONFIG] Test Interval: 2s
[CONFIG] Interface Check Interval: 5 tests
[INFO] Starting continuous network test...
[INFO] Press Ctrl+C to stop
[INFO] USB adapter removal/change will trigger restart
============================================================

[TEST #1] 2026-09-11 14:30:45
[TEST] Pinging 192.168.1.11 from eth0...
[PASS] ✓ Successfully pinged 192.168.1.11 from eth0
[STATS] Pass: 1 | Fail: 0 | Total: 1

[TEST #2] 2026-09-11 14:30:47
[TEST] Pinging 192.168.1.11 from eth0...
[PASS] ✓ Successfully pinged 192.168.1.11 from eth0
[STATS] Pass: 2 | Fail: 0 | Total: 2
```

## Troubleshooting

### Interfaces Not Detected
1. Check interface names: `ip link show`
2. Verify IP addresses are assigned: `ip addr show`
3. Ensure USB adapter is properly connected

### GPIO Permission Errors
Ensure the script runs with sufficient permissions. The systemd service should handle this, but if running manually:
```bash
sudo python3 network_cable_tester.py
```

### LEDs Not Lighting
1. Verify GPIO pin numbers match your wiring
2. Check LED polarity (longer leg is positive)
3. Ensure resistors are properly installed
4. Test GPIO pins: `gpio -g mode 17 out && gpio -g write 17 1`

### Ping Failures
1. Check network cable connections
2. Verify IP addresses are configured: `ip addr show`
3. Test connectivity manually: `ping -I eth0 192.168.1.11`
4. Check firewall rules: `sudo iptables -L`

## Service Management

### View Service Status
```bash
sudo systemctl status network-cable-tester.service
```

### View Full Logs
```bash
sudo journalctl -u network-cable-tester.service -n 50
```

### View Logs Since Last Boot
```bash
sudo journalctl -u network-cable-tester.service -b
```

### Restart Service
```bash
sudo systemctl restart network-cable-tester.service
```

## Uninstallation

```bash
# Stop the service
sudo systemctl stop network-cable-tester.service

# Disable auto-start
sudo systemctl disable network-cable-tester.service

# Remove service file
sudo rm /etc/systemd/system/network-cable-tester.service
sudo systemctl daemon-reload

# Remove installation directory
sudo rm -rf /home/pi/rpi-network-cable-tester
```

## Technical Details

### Interface Detection Algorithm
1. Queries all active network interfaces
2. Checks driver information using `/sys/class/net`
3. Identifies built-in Ethernet (smsc95xx, lan78xx, bcmgenet drivers)
4. Identifies USB adapters (asix, ax88179_178a drivers or USB path detection)

### Auto-Restart Mechanism
- Checks interface configuration every N tests (default: 5)
- Compares current interface setup with previous configuration
- If USB adapter is removed/changed, automatically restarts detection
- Allows reconnection to different USB ports without manual restart

### LED Status Indicators
- **Green Solid**: Ping successful
- **Red Blinking then Solid**: Ping failed
- **Both Off**: Initialization or waiting for interfaces

## License

MIT License - See LICENSE file for details

## Author

barnovongurka (2026)

## Support

For issues, questions, or contributions, please visit:
https://github.com/barnovongurka/rpi-network-cable-tester
