#!/bin/bash
# Installation script for Raspberry Pi Network Cable Tester
# Run this script with sudo to install the service

set -e

echo "Installing Raspberry Pi Network Cable Tester..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "This script must be run with sudo"
   exit 1
fi

# Define paths
INSTALL_DIR="/home/pi/rpi-network-cable-tester"
SERVICE_FILE="/etc/systemd/system/network-cable-tester.service"
SCRIPT_FILE="network_cable_tester.py"

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Creating installation directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    chown pi:pi "$INSTALL_DIR"
fi

# Copy main script
echo "Copying main script..."
cp "$SCRIPT_FILE" "$INSTALL_DIR/"
chown pi:pi "$INSTALL_DIR/$SCRIPT_FILE"
chmod 755 "$INSTALL_DIR/$SCRIPT_FILE"

# Copy and install systemd service
echo "Installing systemd service..."
cp network-cable-tester.service "$SERVICE_FILE"
chmod 644 "$SERVICE_FILE"

# Install Python requirements
echo "Installing Python requirements..."
apt-get update
apt-get install -y python3-rpi.gpio

# Configure static IP addresses
echo ""
echo "Configuring static IP addresses..."
echo "Adding dhcpcd configuration for static IPs..."

# Backup the original dhcpcd.conf if not already backed up
if [ ! -f /etc/dhcpcd.conf.bak ]; then
    cp /etc/dhcpcd.conf /etc/dhcpcd.conf.bak
    echo "Original dhcpcd.conf backed up to /etc/dhcpcd.conf.bak"
fi

# Remove any existing network cable tester configuration
sed -i '/# Network Cable Tester Configuration/,/^$/d' /etc/dhcpcd.conf

# Add static IP configuration
cat >> /etc/dhcpcd.conf <<'EOF'

# Network Cable Tester Configuration
# Primary interface (built-in ethernet)
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4

# Secondary interface (USB adapter)
interface eth1
static ip_address=192.168.1.101/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
EOF

echo "Static IP configuration added:"
echo "  eth0: 192.168.1.100/24"
echo "  eth1: 192.168.1.101/24"

# Enable the service
echo ""
echo "Enabling service for boot startup..."
systemctl daemon-reload
systemctl enable network-cable-tester.service

echo ""
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""
echo "Network Configuration:"
echo "  eth0 (Primary): 192.168.1.100/24"
echo "  eth1 (USB Adapter): 192.168.1.101/24"
echo ""
echo "⚠️  IMPORTANT: Review and adjust IP addresses if needed!"
echo "   Edit: /etc/dhcpcd.conf (search for 'Network Cable Tester')"
echo "   Or restore backup: sudo cp /etc/dhcpcd.conf.bak /etc/dhcpcd.conf"
echo ""
echo "Next steps:"
echo "1. (Optional) Edit IP addresses in /etc/dhcpcd.conf"
echo ""
echo "2. (Optional) Edit GPIO pin numbers if needed:"
echo "   - GREEN_LED_PIN in $INSTALL_DIR/$SCRIPT_FILE"
echo "   - RED_LED_PIN in $INSTALL_DIR/$SCRIPT_FILE"
echo ""
echo "3. Reboot to apply network configuration:"
echo "   sudo reboot"
echo ""
echo "4. After reboot, verify network configuration:"
echo "   ip addr show"
echo ""
echo "5. Start the service:"
echo "   sudo systemctl start network-cable-tester.service"
echo ""
echo "6. View live logs:"
echo "   sudo journalctl -u network-cable-tester.service -f"
echo ""
echo "7. Stop the service:"
echo "   sudo systemctl stop network-cable-tester.service"
echo ""
echo "8. Disable auto-start:"
echo "   sudo systemctl disable network-cable-tester.service"
echo ""
echo "============================================"
