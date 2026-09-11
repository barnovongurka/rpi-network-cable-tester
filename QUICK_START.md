# Quick Start Guide

## 1. Hardware Setup

### Connect LEDs to GPIO
- **Green LED**: GPIO 17 (Pin 11) with 330Ω resistor to GND
- **Red LED**: GPIO 27 (Pin 13) with 330Ω resistor to GND

See `GPIO_SETUP.md` for detailed wiring instructions.

### Connect Network Cables
- Connect Ethernet cable to built-in network interface
- Connect Ethernet cable to USB-to-RJ45 adapter
- Connect the two cables together through a switch/router or directly via crossover cable

## 2. Network Configuration

### Configure Network Interfaces

Ensure both interfaces have IP addresses:

```bash
# Check current interfaces
ip link show

# Check IP addresses
ip addr show
```

If no IPs are assigned, configure them:

```bash
# Option A: Using DHCP (automatic)
sudo nano /etc/network/interfaces
```

Add:
```
auto eth0
iface eth0 inet dhcp

auto eth1
iface eth1 inet dhcp
```

Or use static IPs:
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

Restart networking:
```bash
sudo systemctl restart networking
```

See `NETWORK_CONFIG.md` for more configuration options.

## 3. Installation

### Quick Install

```bash
# Clone repository
git clone https://github.com/barnovongurka/rpi-network-cable-tester.git
cd rpi-network-cable-tester

# Run automated installer
chmod +x install.sh
sudo ./install.sh
```

The installer will:
- Install Python dependencies
- Copy files to `/home/pi/rpi-network-cable-tester`
- Install systemd service for boot startup
- Enable auto-start

## 4. Configuration (Optional)

If you're not using GPIO 17 and 27, or have different interface names:

```bash
# Edit configuration
sudo nano /home/pi/rpi-network-cable-tester/network_cable_tester.py
```

Change these variables:
```python
GREEN_LED_PIN = 17          # Your green LED GPIO pin
RED_LED_PIN = 27            # Your red LED GPIO pin
PRIMARY_INTERFACE = "eth0"  # Your primary interface name
USB_ADAPTER_INTERFACE = "eth1"  # Your USB adapter interface name
PRIMARY_IP = "192.168.1.10"     # Primary interface IP
USB_ADAPTER_IP = "192.168.1.11" # USB adapter IP
```

## 5. Start Testing

### Start the Service

```bash
# Start immediately
sudo systemctl start network-cable-tester.service

# Check status
sudo systemctl status network-cable-tester.service

# View live logs
sudo journalctl -u network-cable-tester.service -f
```

### Manual Testing (Before Boot Startup)

```bash
# Run manually to test
cd /home/pi/rpi-network-cable-tester
sudo python3 network_cable_tester.py
```

## 6. Expected Output

When running successfully, you should see:

```
============================================================
RASPBERRY PI NETWORK CABLE TESTER
============================================================
[INIT] GPIO pins configured successfully
[INIT] Green LED: GPIO 17
[INIT] Red LED: GPIO 27

============================================================
NETWORK INTERFACE INFORMATION
============================================================
(interface details)

[CONFIG] Primary Interface: eth0
[CONFIG] USB Adapter Interface: eth1
[CONFIG] Primary IP: 192.168.1.10
[CONFIG] USB Adapter IP: 192.168.1.11
[CONFIG] Test Interval: 2s
[INFO] Starting continuous network test...
[INFO] Press Ctrl+C to stop
============================================================

[TEST #1] 2026-09-11 14:30:45
[TEST] Pinging 192.168.1.11 from eth0...
[PASS] ✓ Successfully pinged 192.168.1.11 from eth0
[STATS] Pass: 1 | Fail: 0 | Total: 1
```

**LED Behavior:**
- **Green LED lights**: Ping successful - cable is working
- **Red LED blinks then stays lit**: Ping failed - cable issue detected

## 7. Troubleshooting

### Problem: Interfaces Not Found

```bash
# Check available interfaces
ip link show

# Update interface names in config
sudo nano /home/pi/rpi-network-cable-tester/network_cable_tester.py
```

### Problem: No IP Addresses Assigned

```bash
# Check IP configuration
ip addr show

# Configure interfaces (see Network Configuration above)
```

### Problem: LEDs Not Lighting

1. Check GPIO pins are correct
2. Test GPIO with:
   ```bash
   sudo gpio -g mode 17 out
   sudo gpio -g write 17 1
   ```
3. Check LED polarity (longer leg = positive)
4. Check resistor installation

### Problem: Ping Fails

1. Check cable is connected
2. Test manually:
   ```bash
   ping -I eth0 192.168.1.11
   ```
3. Check firewall isn't blocking:
   ```bash
   sudo iptables -L
   ```

### Use Troubleshooting Script

```bash
chmod +x troubleshoot.sh
./troubleshoot.sh
```

This interactive script provides:
- Interface checking
- IP address verification
- GPIO pin testing
- Service status monitoring
- Permission diagnostics

## 8. Service Management

```bash
# Start service
sudo systemctl start network-cable-tester.service

# Stop service
sudo systemctl stop network-cable-tester.service

# Restart service
sudo systemctl restart network-cable-tester.service

# Check status
sudo systemctl status network-cable-tester.service

# View logs
sudo journalctl -u network-cable-tester.service -f

# Disable auto-start
sudo systemctl disable network-cable-tester.service

# Enable auto-start
sudo systemctl enable network-cable-tester.service
```

## 9. Uninstall

```bash
sudo systemctl stop network-cable-tester.service
sudo systemctl disable network-cable-tester.service
sudo rm /etc/systemd/system/network-cable-tester.service
sudo systemctl daemon-reload
sudo rm -rf /home/pi/rpi-network-cable-tester
```

## Next Steps

- Read `GPIO_SETUP.md` for detailed GPIO information
- Read `NETWORK_CONFIG.md` for advanced network configuration
- Check GitHub repository for issues and updates

## Support

For help, see:
- README.md - Full documentation
- GitHub Issues - Report bugs and ask questions
- troubleshoot.sh - Interactive troubleshooting tool
