#!/bin/bash
# Troubleshooting and Testing Script for Network Cable Tester

echo "============================================"
echo "Network Cable Tester - Troubleshooting Tool"
echo "============================================"
echo ""

# Function to display menu
show_menu() {
    echo "Select an option:"
    echo "1. Check network interfaces"
    echo "2. Check IP addresses"
    echo "3. Test GPIO pins"
    echo "4. Manual ping test"
    echo "5. View service status"
    echo "6. View service logs"
    echo "7. Restart service"
    echo "8. Check GPIO permissions"
    echo "9. Exit"
    echo ""
}

# Function to check interfaces
check_interfaces() {
    echo "Network Interfaces:"
    echo "==================="
    ip link show
    echo ""
}

# Function to check IPs
check_ips() {
    echo "IP Addresses:"
    echo "============="
    ip addr show
    echo ""
}

# Function to test GPIO
test_gpio() {
    echo "GPIO Testing (requires gpio utility)"
    echo "===================================="
    echo "Testing GPIO 17 (Green LED)..."
    if command -v gpio &> /dev/null; then
        sudo gpio -g mode 17 out
        sudo gpio -g write 17 1
        echo "GPIO 17 ON - Check if green LED lights up"
        sleep 2
        sudo gpio -g write 17 0
        echo "GPIO 17 OFF"
        
        echo ""
        echo "Testing GPIO 27 (Red LED)..."
        sudo gpio -g mode 27 out
        sudo gpio -g write 27 1
        echo "GPIO 27 ON - Check if red LED lights up"
        sleep 2
        sudo gpio -g write 27 0
        echo "GPIO 27 OFF"
    else
        echo "gpio utility not found. Install with:"
        echo "sudo apt-get install wiringpi"
    fi
    echo ""
}

# Function to test ping
test_ping() {
    echo "Manual Ping Test"
    echo "================"
    read -p "Enter source interface (e.g., eth0): " src_iface
    read -p "Enter target IP (e.g., 192.168.1.11): " target_ip
    
    echo "Pinging $target_ip from $src_iface..."
    ping -I "$src_iface" -c 4 -W 2 "$target_ip"
    echo ""
}

# Function to check service status
check_service_status() {
    echo "Service Status:"
    echo "==============="
    sudo systemctl status network-cable-tester.service
    echo ""
}

# Function to view logs
view_logs() {
    echo "Recent Service Logs (last 20 lines):"
    echo "===================================="
    sudo journalctl -u network-cable-tester.service -n 20
    echo ""
    echo "Press Ctrl+C to stop following logs..."
    echo "Following logs (Ctrl+C to exit):"
    sudo journalctl -u network-cable-tester.service -f
}

# Function to restart service
restart_service() {
    echo "Restarting service..."
    sudo systemctl restart network-cable-tester.service
    echo "Service restarted"
    sleep 2
    sudo systemctl status network-cable-tester.service
    echo ""
}

# Function to check GPIO permissions
check_gpio_perms() {
    echo "GPIO Permissions Check:"
    echo "======================"
    
    if [ -d "/sys/class/gpio" ]; then
        echo "GPIO directory exists"
        ls -la /sys/class/gpio/
    else
        echo "GPIO directory not found"
    fi
    
    echo ""
    echo "Current user: $(whoami)"
    echo "User groups: $(id)"
    echo ""
    
    if groups | grep -q "gpio"; then
        echo "✓ User is in 'gpio' group"
    else
        echo "✗ User is NOT in 'gpio' group"
        echo "  Add with: sudo usermod -aG gpio $(whoami)"
    fi
    
    if groups | grep -q "sudo"; then
        echo "✓ User can use sudo"
    else
        echo "✗ User cannot use sudo"
    fi
    echo ""
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice: " choice
    
    case $choice in
        1) check_interfaces ;;
        2) check_ips ;;
        3) test_gpio ;;
        4) test_ping ;;
        5) check_service_status ;;
        6) view_logs ;;
        7) restart_service ;;
        8) check_gpio_perms ;;
        9) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid option. Please try again." ;;
    esac
done
