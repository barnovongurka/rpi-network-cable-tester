#!/bin/bash
# Installation script for Raspberry Pi Network Cable Tester - Two Pi Setup
# Raspbian Trixie with NetworkManager
# Run this script with sudo on both Pis

set -e

echo "Installing Raspberry Pi Network Cable Tester (Raspbian Trixie)..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "This script must be run with sudo"
   exit 1
fi

# Define paths
INSTALL_DIR="/home/pi/rpi-network-cable-tester"
SERVICE_FILE="/etc/systemd/system/network-cable-tester.service"
SCRIPT_FILE="network_cable_tester.py"
CONFIG_FILE="config.ini"

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
chown pi:pi "$INSTALL_DIR"

# Copy main script
echo "Copying main script..."
cp "$SCRIPT_FILE" "$INSTALL_DIR/"
chown pi:pi "$INSTALL_DIR/$SCRIPT_FILE"
chmod 755 "$INSTALL_DIR/$SCRIPT_FILE"

# Copy systemd service
echo "Installing systemd service..."
cp network-cable-tester.service "$SERVICE_FILE"
chmod 644 "$SERVICE_FILE"

# Install Python requirements
echo "Installing Python requirements..."
apt-get update
apt-get install -y python3-rpi.gpio

# Ensure NetworkManager is installed and enabled
echo ""
echo "Checking NetworkManager..."
apt-get install -y network-manager

# Enable and start NetworkManager
echo "Enabling NetworkManager..."
systemctl enable NetworkManager
systemctl restart NetworkManager

# Wait for NetworkManager to be ready
echo "Waiting for NetworkManager to initialize..."
sleep 3

# Create default config.ini if it doesn't exist
if [ ! -f "$INSTALL_DIR/$CONFIG_FILE" ]; then
    echo "Creating default configuration file..."
    cat > "$INSTALL_DIR/$CONFIG_FILE" <<'EOF'
[network]
# IP address of the target Raspberry Pi to ping
# Set this to the IP address of the other Pi
target_ip = 192.168.1.101

[led]
# GPIO pin numbers (adjust to match your wiring)
green_led_pin = 17
red_led_pin = 27

[test]
# Test configuration
ping_count = 1
ping_timeout = 2
test_interval = 2
blink_duration = 0.1
EOF
    chown pi:pi "$INSTALL_DIR/$CONFIG_FILE"
    chmod 644 "$INSTALL_DIR/$CONFIG_FILE"
fi

# Configure network using nmcli
echo ""
echo "Configuring network connection using NetworkManager..."

# Prompt user for network configuration
echo ""
echo "Choose network configuration:"
echo "1. Tester Pi (will run tests, has LEDs)"
echo "2. Target Pi (will be pinged)"
read -p "Which Pi is this? (1 or 2): " pi_role

if [ "$pi_role" = "1" ]; then
    PI_IP="192.168.1.100"
    OTHER_PI_IP="192.168.1.101"
    echo "Configuring as TESTER Pi with IP: $PI_IP"
    echo "Target Pi IP will be: $OTHER_PI_IP"
    
    # Update config with target IP
    sed -i "s/target_ip = .*/target_ip = $OTHER_PI_IP/" "$INSTALL_DIR/$CONFIG_FILE"
    
elif [ "$pi_role" = "2" ]; then
    PI_IP="192.168.1.101"
    OTHER_PI_IP="192.168.1.100"
    echo "Configuring as TARGET Pi with IP: $PI_IP"
    echo "Tester Pi will use IP: $OTHER_PI_IP"
    echo ""
    echo "⚠️  TARGET PI NOTE: This Pi does NOT need the systemd service running."
    echo "   Just needs to have an IP address configured and be reachable."
else
    echo "Invalid selection. Exiting."
    exit 1
fi

# Configure network connection using nmcli
echo "Creating network connection for eth0..."

# Delete existing connection if it exists
nmcli connection delete "Wired connection 1" 2>/dev/null || true
nmcli connection delete "eth0-static" 2>/dev/null || true

# Create new connection with static IP
nmcli connection add \
    type ethernet \
    ifname eth0 \
    con-name "eth0-static" \
    autoconnect yes \
    autoconnect-priority 0

# Configure IPv4 settings
nmcli connection modify "eth0-static" \
    ipv4.addresses "$PI_IP/24" \
    ipv4.gateway "192.168.1.1" \
    ipv4.dns "8.8.8.8 8.8.4.4" \
    ipv4.method manual

# Apply the connection
echo "Applying network configuration..."
nmcli connection up "eth0-static" 2>/dev/null || true

echo "Network connection configured: $PI_IP/24"

# Enable the service (only on Tester Pi)
if [ "$pi_role" = "1" ]; then
    echo ""
    echo "Enabling service for boot startup (Tester Pi only)..."
    systemctl daemon-reload
    systemctl enable network-cable-tester.service
else
    echo ""
    echo "Skipping systemd service (Target Pi doesn't need it)"
fi

echo ""
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""
echo "Network Configuration (NetworkManager):"
echo "  Connection Name: eth0-static"
echo "  This Pi IP: $PI_IP/24"
echo "  Other Pi IP: $OTHER_PI_IP/24"
echo "  Gateway: 192.168.1.1"
echo "  DNS: 8.8.8.8, 8.8.4.4"
echo ""
echo "Next steps:"
echo ""
echo "1. Verify network configuration:"
echo "   nmcli device show eth0"
echo "   or"
echo "   ip addr show eth0"
echo ""
echo "2. Connect the network cable between the two Pis"
echo ""
echo "3. On TARGET Pi - Verify connectivity:"
echo "   ping -c 1 <this-tester-pi-ip>"
echo ""
if [ "$pi_role" = "1" ]; then
    echo "4. On TESTER Pi - Start the service:"
    echo "   sudo systemctl start network-cable-tester.service"
    echo ""
    echo "5. View live logs:"
    echo "   sudo journalctl -u network-cable-tester.service -f"
    echo ""
    echo "6. To adjust target IP, edit:"
    echo "   sudo nano $INSTALL_DIR/$CONFIG_FILE"
    echo "   Then restart: sudo systemctl restart network-cable-tester.service"
    echo ""
    echo "7. To view/modify network settings:"
    echo "   nmcli connection show eth0-static"
    echo "   nmcli connection modify eth0-static ipv4.addresses <NEW_IP>/24"
    echo "   nmcli connection up eth0-static"
else
    echo "4. No further action needed on TARGET Pi"
    echo "   (Keep it running and reachable at $PI_IP)"
    echo ""
    echo "5. To view/modify network settings:"
    echo "   nmcli connection show eth0-static"
    echo "   nmcli connection modify eth0-static ipv4.addresses <NEW_IP>/24"
    echo "   nmcli connection up eth0-static"
fi
echo ""
echo "============================================"
