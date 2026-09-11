#!/usr/bin/env python3
"""
Raspberry Pi Network Cable Tester
Tests connectivity between built-in network interface and USB-to-RJ45 adapter
Displays results via LED indicators and console output
Auto-detects network interfaces and restarts when USB adapter is changed
"""

import RPi.GPIO as GPIO
import subprocess
import time
import sys
import json
from datetime import datetime
import signal
import os
import re
from pathlib import Path

# GPIO Pin Configuration
GREEN_LED_PIN = 17  # GPIO 17 for success indicator
RED_LED_PIN = 27    # GPIO 27 for failure indicator

# Test Configuration
PING_COUNT = 1              # Number of ping packets per test
PING_TIMEOUT = 2            # Timeout in seconds per ping
TEST_INTERVAL = 2           # Seconds between tests
BLINK_DURATION = 0.1        # LED blink duration in seconds
INTERFACE_CHECK_INTERVAL = 5  # Check for interface changes every N tests


class NetworkInterfaceDetector:
    """Automatically detect network interfaces and their IP addresses"""
    
    @staticmethod
    def get_all_interfaces():
        """Get all active network interfaces excluding loopback"""
        try:
            result = subprocess.run(
                ['ip', 'link', 'show'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            
            interfaces = []
            for line in result.stdout.split('\n'):
                match = re.match(r'^\d+:\s+([a-zA-Z0-9\-]+):', line)
                if match:
                    iface = match.group(1)
                    if iface not in ['lo', 'docker0', 'veth'] and not iface.startswith('br-'):
                        interfaces.append(iface)
            
            return interfaces
        except Exception as e:
            print(f"[ERROR] Failed to get interfaces: {e}")
            return []
    
    @staticmethod
    def get_interface_ip(interface):
        """Get IP address for a specific interface"""
        try:
            result = subprocess.run(
                ['ip', 'addr', 'show', interface],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                match = re.search(r'inet\s+([0-9.]+)/\d+', line)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            print(f"[ERROR] Failed to get IP for {interface}: {e}")
            return None
    
    @staticmethod
    def get_interface_driver(interface):
        """Get the driver name for an interface"""
        try:
            result = subprocess.run(
                ['ethtool', '-i', interface],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if line.startswith('driver:'):
                    return line.split(':', 1)[1].strip()
            
            return None
        except Exception as e:
            return None
    
    @staticmethod
    def is_usb_interface(interface):
        """Check if interface is connected via USB"""
        try:
            # Check sysfs for USB device info
            sys_path = f"/sys/class/net/{interface}/device"
            if os.path.islink(sys_path):
                real_path = os.path.realpath(sys_path)
                return '/usb' in real_path or 'usb' in real_path.lower()
            
            # Alternative check using ethtool
            driver = NetworkInterfaceDetector.get_interface_driver(interface)
            return driver is not None and driver.lower() in ['asix', 'ax88179_178a', 'usbnet']
        except Exception as e:
            return False
    
    @staticmethod
    def is_builtin_ethernet(interface):
        """Check if interface is built-in ethernet"""
        try:
            # Built-in interfaces typically use drivers like smsc95xx, lan78xx
            driver = NetworkInterfaceDetector.get_interface_driver(interface)
            if driver:
                return driver.lower() in ['smsc95xx', 'lan78xx', 'bcmgenet', 'dwc_ether']
            
            # If no USB path, likely built-in
            sys_path = f"/sys/class/net/{interface}/device"
            if os.path.islink(sys_path):
                real_path = os.path.realpath(sys_path)
                return '/usb' not in real_path and 'usb' not in real_path.lower()
            
            return True
        except Exception as e:
            return False
    
    @classmethod
    def auto_detect_interfaces(cls):
        """
        Automatically detect primary (built-in) and USB adapter interfaces
        Returns tuple: (primary_interface, usb_adapter_interface)
        """
        interfaces = cls.get_all_interfaces()
        
        if not interfaces:
            return None, None
        
        primary = None
        usb_adapter = None
        
        for iface in interfaces:
            if cls.is_builtin_ethernet(iface):
                primary = iface
            elif cls.is_usb_interface(iface):
                usb_adapter = iface
        
        return primary, usb_adapter
    
    @classmethod
    def get_interface_details(cls):
        """Get detailed information about detected interfaces"""
        primary, usb_adapter = cls.auto_detect_interfaces()
        
        details = {
            'primary_interface': primary,
            'primary_ip': cls.get_interface_ip(primary) if primary else None,
            'usb_adapter_interface': usb_adapter,
            'usb_adapter_ip': cls.get_interface_ip(usb_adapter) if usb_adapter else None,
            'all_interfaces': cls.get_all_interfaces()
        }
        
        return details


class NetworkCableTester:
    """Test network connectivity between two network interfaces"""
    
    def __init__(self):
        self.running = True
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.interface_check_counter = 0
        self.last_interface_config = None
        
        self.primary_interface = None
        self.usb_adapter_interface = None
        self.primary_ip = None
        self.usb_adapter_ip = None
        
        self.setup_gpio()
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def setup_gpio(self):
        """Initialize GPIO pins for LED control"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
            GPIO.setup(RED_LED_PIN, GPIO.OUT)
            
            # Ensure LEDs are off initially
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            GPIO.output(RED_LED_PIN, GPIO.LOW)
            
            print("[INIT] GPIO pins configured successfully")
            print(f"[INIT] Green LED: GPIO {GREEN_LED_PIN}")
            print(f"[INIT] Red LED: GPIO {RED_LED_PIN}")
        except Exception as e:
            print(f"[ERROR] Failed to setup GPIO: {e}")
            sys.exit(1)
    
    def detect_interfaces(self):
        """Auto-detect network interfaces"""
        print("[DETECT] Scanning for network interfaces...")
        
        details = NetworkInterfaceDetector.get_interface_details()
        
        self.primary_interface = details['primary_interface']
        self.primary_ip = details['primary_ip']
        self.usb_adapter_interface = details['usb_adapter_interface']
        self.usb_adapter_ip = details['usb_adapter_ip']
        
        # Store current configuration for change detection
        current_config = json.dumps({
            'primary': self.primary_interface,
            'usb_adapter': self.usb_adapter_interface
        }, sort_keys=True)
        
        if self.last_interface_config and self.last_interface_config != current_config:
            print("[WARN] Network interface configuration changed!")
            return False  # Configuration changed
        
        self.last_interface_config = current_config
        
        return True
    
    def interfaces_available(self):
        """Check if both required interfaces are available"""
        if not self.primary_interface or not self.usb_adapter_interface:
            return False
        if not self.primary_ip or not self.usb_adapter_ip:
            return False
        return True
    
    def print_interface_info(self):
        """Print detected interface information"""
        print("\n" + "="*60)
        print("DETECTED NETWORK INTERFACES")
        print("="*60)
        
        if self.primary_interface:
            driver = NetworkInterfaceDetector.get_interface_driver(self.primary_interface)
            print(f"Primary (Built-in): {self.primary_interface}")
            print(f"  IP Address: {self.primary_ip}")
            print(f"  Driver: {driver}")
        else:
            print("Primary (Built-in): NOT FOUND")
        
        if self.usb_adapter_interface:
            driver = NetworkInterfaceDetector.get_interface_driver(self.usb_adapter_interface)
            print(f"\nUSB Adapter: {self.usb_adapter_interface}")
            print(f"  IP Address: {self.usb_adapter_ip}")
            print(f"  Driver: {driver}")
        else:
            print("\nUSB Adapter: NOT FOUND")
        
        print(f"\nAll Interfaces: {', '.join(NetworkInterfaceDetector.get_all_interfaces())}")
        print("="*60 + "\n")
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n[INFO] Shutting down...")
        self.running = False
        self.cleanup()
        print("[INFO] Test terminated by user")
        sys.exit(0)
    
    def cleanup(self):
        """Clean up GPIO and resources"""
        try:
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            GPIO.output(RED_LED_PIN, GPIO.LOW)
            GPIO.cleanup()
            print("[CLEANUP] GPIO cleaned up")
        except Exception as e:
            print(f"[ERROR] Cleanup error: {e}")
    
    def blink_led(self, pin, count=1, duration=None):
        """Blink an LED"""
        if duration is None:
            duration = BLINK_DURATION
        
        for _ in range(count):
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(duration)
    
    def light_led(self, pin):
        """Keep LED continuously lit"""
        GPIO.output(pin, GPIO.HIGH)
    
    def turn_off_all_leds(self):
        """Turn off all LEDs"""
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        GPIO.output(RED_LED_PIN, GPIO.LOW)
    
    def ping_interface(self, target_ip, source_interface):
        """
        Ping target IP from source interface
        Returns True if ping successful, False otherwise
        """
        try:
            # Use ping command with interface binding
            cmd = [
                'ping',
                '-I', source_interface,
                '-c', str(PING_COUNT),
                '-W', str(PING_TIMEOUT),
                target_ip
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=PING_TIMEOUT + 2
            )
            
            return result.returncode == 0
        
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            print(f"[ERROR] Ping error: {e}")
            return False
    
    def test_connectivity(self):
        """Test connectivity between the two network interfaces"""
        self.test_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n[TEST #{self.test_count}] {timestamp}")
        print(f"[TEST] Pinging {self.usb_adapter_ip} from {self.primary_interface}...")
        
        try:
            # Test: Ping USB adapter from primary interface
            success = self.ping_interface(self.usb_adapter_ip, self.primary_interface)
            
            if success:
                self.pass_count += 1
                print(f"[PASS] ✓ Successfully pinged {self.usb_adapter_ip} from {self.primary_interface}")
                print(f"[STATS] Pass: {self.pass_count} | Fail: {self.fail_count} | Total: {self.test_count}")
                
                # Light green LED continuously
                self.turn_off_all_leds()
                self.light_led(GREEN_LED_PIN)
            else:
                self.fail_count += 1
                print(f"[FAIL] ✗ Failed to ping {self.usb_adapter_ip} from {self.primary_interface}")
                print(f"[STATS] Pass: {self.pass_count} | Fail: {self.fail_count} | Total: {self.test_count}")
                
                # Blink red LED continuously
                self.turn_off_all_leds()
                self.blink_led(RED_LED_PIN, count=3)
                self.light_led(RED_LED_PIN)
                
        except Exception as e:
            self.fail_count += 1
            print(f"[ERROR] Test error: {e}")
            self.turn_off_all_leds()
            self.blink_led(RED_LED_PIN, count=3)
            self.light_led(RED_LED_PIN)
    
    def check_interface_changes(self):
        """Periodically check if interfaces have changed"""
        self.interface_check_counter += 1
        
        if self.interface_check_counter >= INTERFACE_CHECK_INTERVAL:
            self.interface_check_counter = 0
            
            if not self.detect_interfaces():
                print("\n[ALERT] Network interface configuration changed - RESTARTING")
                self.turn_off_all_leds()
                time.sleep(1)
                return False  # Signal restart needed
            
            if not self.interfaces_available():
                print("\n[ALERT] Required network interface not available - RESTARTING")
                self.turn_off_all_leds()
                time.sleep(1)
                return False  # Signal restart needed
        
        return True
    
    def print_welcome_header(self):
        """Print welcome header"""
        print("\n" + "="*60)
        print("RASPBERRY PI NETWORK CABLE TESTER")
        print("="*60)
        print("[INFO] Auto-detecting network interfaces...")
    
    def run(self):
        """Main test loop with auto-restart on interface changes"""
        while self.running:
            self.print_welcome_header()
            
            # Detect interfaces
            if not self.detect_interfaces():
                print("[ERROR] Failed to detect interfaces. Retrying...")
                time.sleep(5)
                continue
            
            if not self.interfaces_available():
                print("[ERROR] Required interfaces not available:")
                self.print_interface_info()
                print("[INFO] Waiting for interfaces to become available...")
                self.turn_off_all_leds()
                time.sleep(10)
                continue
            
            # Interfaces found
            self.print_interface_info()
            
            print(f"[CONFIG] Test Interval: {TEST_INTERVAL}s")
            print(f"[CONFIG] Interface Check Interval: {INTERFACE_CHECK_INTERVAL} tests")
            print("[INFO] Starting continuous network test...")
            print("[INFO] Press Ctrl+C to stop")
            print("[INFO] USB adapter removal/change will trigger restart")
            print("="*60)
            
            # Reset test counters for this session
            self.test_count = 0
            self.pass_count = 0
            self.fail_count = 0
            self.interface_check_counter = 0
            
            # Test loop
            try:
                while self.running:
                    # Check for interface changes
                    if not self.check_interface_changes():
                        break  # Restart outer loop
                    
                    self.test_connectivity()
                    time.sleep(TEST_INTERVAL)
                    
            except KeyboardInterrupt:
                self.signal_handler(None, None)
            except Exception as e:
                print(f"[ERROR] Unexpected error in test loop: {e}")
                self.turn_off_all_leds()
                time.sleep(5)


def main():
    """Entry point"""
    tester = NetworkCableTester()
    tester.run()


if __name__ == "__main__":
    main()
