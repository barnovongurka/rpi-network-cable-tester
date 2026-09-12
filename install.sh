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

# Install NetworkManager and nmcli
echo ""
echo "Installing NetworkManager..."
apt-get install -y network-manager

# Enable NetworkManager
echo "Enabling NetworkManager..."
systemctl enable NetworkManager
systemctl start NetworkManager

# Wait for NetworkManager to be ready
echo "Waiting for NetworkManager to initialize..."
sleep 3

# Configure static IP addresses using nmcli
echo ""
echo "Configuring static IP addresses using nmcli..."

# Configure eth0 (primary interface)
echo "Configuring eth0 (192.168.1.100)..."
nmcli connection delete "Wired connection 1" 2>/dev/null || true
nmcli connection add type ethernet ifname eth0 con-name "eth0-static"
nmcli connection modify "eth0-static" ipv4.addresses 192.168.1.100/24
nmcli connection modify "eth0-static" ipv4.gateway 192.168.1.1
nmcli connection modify "eth0-static" ipv4.dns "8.8.8.8 8.8.4.4"
nmcli connection modify "eth0-static" ipv4.method manual
nmcli connection up "eth0-static"

# Configure eth1 (USB adapter interface)
echo "Configuring eth1 (192.168.1.101)..."
nmcli connection delete "Wired connection 2" 2>/dev/null || true
nmcli connection add type ethernet ifname eth1 con-name "eth1-static"
nmcli connection modify "eth1-static" ipv4.addresses 192.168.1.101/24
nmcli connection modify "eth1-static" ipv4.gateway 192.168.1.1
nmcli connection modify "eth1-static" ipv4.dns "8.8.8.8 8.8.4.4"
nmcli connection modify "eth1-static" ipv4.method manual
nmcli connection up "eth1-static"

echo "Network interfaces configured successfully!"

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
echo "   View connection: nmcli connection show"
echo "   View devices: nmcli device show"
echo ""
echo "   Edit eth0 connection:"
echo "   nmcli connection modify eth0-static ipv4.addresses <NEW_IP>/24"
echo "   nmcli connection up eth0-static"
echo ""
echo "   Edit eth1 connection:"
echo "   nmcli connection modify eth1-static ipv4.addresses <NEW_IP>/24"
echo "   nmcli connection up eth1-static"
echo ""
echo "Next steps:"
echo "1. (Optional) Edit IP addresses using nmcli if needed"
echo ""
echo "2. (Optional) Edit GPIO pin numbers if needed:"
echo "   - GREEN_LED_PIN in $INSTALL_DIR/$SCRIPT_FILE"
echo "   - RED_LED_PIN in $INSTALL_DIR/$SCRIPT_FILE"
echo ""
echo "3. Verify network configuration:"
echo "   ip addr show"
echo ""
echo "4. Start the service:"
echo "   sudo systemctl start network-cable-tester.service"
echo ""
echo "5. View live logs:"
echo "   sudo journalctl -u network-cable-tester.service -f"
echo ""
echo "6. Stop the service:"
echo "   sudo systemctl stop network-cable-tester.service"
echo ""
echo "7. Disable auto-start:"
echo "   sudo systemctl disable network-cable-tester.service"
echo ""
echo "============================================"
