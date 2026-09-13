#!/usr/bin/env python3
"""
Raspberry Pi Network Cable Tester - Two Pi Setup
Tests network connectivity between two Raspberry Pis via a single network cable
One Pi acts as the tester (with LEDs), the other as the target (provides IP to ping)
Raspbian Trixie with NetworkManager
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
from configparser import ConfigParser
from pathlib import Path

# GPIO Pin Configuration
GREEN_LED_PIN = 17  # GPIO 17 for success indicator
RED_LED_PIN = 27    # GPIO 27 for failure indicator

# Test Configuration
PING_COUNT = 1              # Number of ping packets per test
PING_TIMEOUT = 2            # Timeout in seconds per ping
TEST_INTERVAL = 2           # Seconds between tests
BLINK_DURATION = 0.1        # LED blink duration in seconds

# Configuration file
CONFIG_FILE = "/home/pi/rpi-network-cable-tester/config.ini"


class ConfigurationManager:
    """Manage configuration for the network cable tester"""
    
    @staticmethod
    def load_config():
        """Load configuration from config.ini"""
        try:
            config = ConfigParser()
            if os.path.exists(CONFIG_FILE):
                config.read(CONFIG_FILE)
                return config
            else:
                print(f"[WARN] Config file not found: {CONFIG_FILE}")
                print("[INFO] Please create config.ini with target Pi IP address")
                return None
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            return None
    
    @staticmethod
    def get_target_ip(config):
        """Get target Pi IP address from config"""
        try:
            if config and config.has_option('network', 'target_ip'):
                return config.get('network', 'target_ip')
        except Exception as e:
            print(f"[ERROR] Failed to get target IP from config: {e}")
        return None


class NetworkCableTester:
    """Test network connectivity between two Raspberry Pis"""
    
    def __init__(self, target_ip):
        self.running = True
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.target_ip = target_ip
        
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
    
    def ping_target(self):
        """
        Ping target Pi
        Returns True if ping successful, False otherwise
        """
        try:
            cmd = [
                'ping',
                '-c', str(PING_COUNT),
                '-W', str(PING_TIMEOUT),
                self.target_ip
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
        """Test connectivity to target Pi"""
        self.test_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n[TEST #{self.test_count}] {timestamp}")
        print(f"[TEST] Pinging target Pi at {self.target_ip}...")
        
        try:
            success = self.ping_target()
            
            if success:
                self.pass_count += 1
                print(f"[PASS] ✓ Successfully pinged {self.target_ip}")
                print(f"[STATS] Pass: {self.pass_count} | Fail: {self.fail_count} | Total: {self.test_count}")
                
                # Light green LED
                self.turn_off_all_leds()
                self.light_led(GREEN_LED_PIN)
            else:
                self.fail_count += 1
                print(f"[FAIL] ✗ Failed to ping {self.target_ip}")
                print(f"[STATS] Pass: {self.pass_count} | Fail: {self.fail_count} | Total: {self.test_count}")
                
                # Blink red LED
                self.turn_off_all_leds()
                self.blink_led(RED_LED_PIN, count=3)
                self.light_led(RED_LED_PIN)
                
        except Exception as e:
            self.fail_count += 1
            print(f"[ERROR] Test error: {e}")
            self.turn_off_all_leds()
            self.blink_led(RED_LED_PIN, count=3)
            self.light_led(RED_LED_PIN)
    
    def print_welcome_header(self):
        """Print welcome header"""
        print("\n" + "="*60)
        print("RASPBERRY PI NETWORK CABLE TESTER")
        print("Two-Pi Configuration (Raspbian Trixie)")
        print("="*60)
        print(f"[INFO] Target Pi IP: {self.target_ip}")
    
    def run(self):
        """Main test loop"""
        self.print_welcome_header()
        
        print(f"\n[CONFIG] Test Interval: {TEST_INTERVAL}s")
        print("[INFO] Starting continuous network test...")
        print("[INFO] Press Ctrl+C to stop")
        print(f"[INFO] Green LED = Ping successful")
        print(f"[INFO] Red LED = Ping failed")
        print("="*60)
        
        try:
            while self.running:
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
    # Load configuration
    config = ConfigurationManager.load_config()
    
    if not config:
        print("[ERROR] Failed to load configuration")
        sys.exit(1)
    
    # Get target IP
    target_ip = ConfigurationManager.get_target_ip(config)
    
    if not target_ip:
        print("[ERROR] Target Pi IP address not configured")
        print(f"[INFO] Please add target_ip to {CONFIG_FILE}")
        print("[INFO] Example:")
        print("       [network]")
        print("       target_ip = 192.168.1.101")
        sys.exit(1)
    
    # Start tester
    tester = NetworkCableTester(target_ip)
    tester.run()


if __name__ == "__main__":
    main()
