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

# Install requirements
echo "Installing Python requirements..."
pip3 install RPi.GPIO

# Enable the service
echo "Enabling service for boot startup..."
systemctl daemon-reload
systemctl enable network-cable-tester.service

echo ""
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit GPIO pin numbers if needed:"
echo "   - GREEN_LED_PIN in $INSTALL_DIR/$SCRIPT_FILE"
echo "   - RED_LED_PIN in $INSTALL_DIR/$SCRIPT_FILE"
echo ""
echo "2. Ensure your network interfaces are configured with IP addresses"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl start network-cable-tester.service"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u network-cable-tester.service -f"
echo ""
echo "5. Stop the service:"
echo "   sudo systemctl stop network-cable-tester.service"
echo ""
echo "6. Disable auto-start:"
echo "   sudo systemctl disable network-cable-tester.service"
echo ""
echo "============================================"
