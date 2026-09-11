# GPIO and Hardware Setup Guide

## GPIO Pin Configuration

This guide explains how to connect LEDs to your Raspberry Pi using GPIO pins.

### Default Pin Configuration

The program uses the following GPIO pins by default:

| Component | GPIO Pin | BCM Pin | Physical Pin | Description |
|-----------|----------|---------|--------------|-------------|
| Green LED | 17       | 17      | 11           | Success indicator |
| Red LED   | 27       | 27      | 13           | Failure indicator |
| Common    | GND      | -       | 6, 9, 14, 20, 25, 30, 34, 39 | Ground |

### Raspberry Pi GPIO Pinout

```
    +-----+-----+---------+------+---+---Pi 4B+--+---+------+---------+-----+-----+
    | BCM | wPi |   Name  | Mode | V | Physical | V | Mode |  Name   | wPi | BCM |
    +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
    |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
    |   2 |   8 |   SDA.1 | IN   | 1 |  3 || 4  |   |      | 5v      |     |     |
    |   3 |   9 |   SCL.1 | IN   | 1 |  5 || 6  |   |      | 0v      |     |     |
    |   4 |   7 | GPIO. 7 | IN   | 1 |  7 || 8  | 1 | ALT5 | TxD     | 15  | 14  |
    |     |     |      0v |      |   |  9 || 10 | 1 | ALT5 | RxD     | 16  | 15  |
    |  17 |   0 | GPIO. 0 | OUT  | 0 | 11 || 12 | 0 | OUT  | GPIO. 1 | 1   | 18  |
    |  27 |   2 | GPIO. 2 | OUT  | 0 | 13 || 14 |   |      | 0v      |     |     |
    |  22 |   3 | GPIO. 3 | IN   | 1 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
    |     |     |    3.3v |      |   | 17 || 18 | 0 | IN   | GPIO. 5 | 5   | 24  |
    |  10 |  12 |    MOSI | IN   | 1 | 19 || 20 |   |      | 0v      |     |     |
    |   9 |  13 |    MISO | IN   | 1 | 21 || 22 | 0 | IN   | GPIO. 6 | 6   | 25  |
    |  11 |  14 |    SCLK | IN   | 1 | 23 || 24 | 1 | IN   | CE0     | 10  | 8   |
    |     |     |      0v |      |   | 25 || 26 | 1 | IN   | CE1     | 11  | 7   |
    |   0 |  30 |   SDA.0 | IN   | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
    |   5 |  21 | GPIO.21 | IN   | 1 | 29 || 30 |   |      | 0v      |     |     |
    |   6 |  22 | GPIO.22 | IN   | 1 | 31 || 32 | 0 | OUT  | GPIO.12 | 26  | 12  |
    |  13 |  23 | GPIO.23 | IN   | 1 | 33 || 34 |   |      | 0v      |     |     |
    |  19 |  24 | GPIO.24 | IN   | 1 | 35 || 36 | 0 | IN   | GPIO.27 | 27  | 16  |
    |  26 |  25 | GPIO.25 | OUT  | 0 | 37 || 38 | 1 | IN   | GPIO.28 | 28  | 20  |
    |     |     |      0v |      |   | 39 || 40 | 1 | IN   | GPIO.29 | 29  | 21  |
    +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
```

## LED Circuit Diagram

### Green LED (GPIO 17) Circuit
```
        GPIO 17 (Pin 11)
             |
             v
        [LED Anode]
             |
        [LED Cathode]
             |
        [330Ω Resistor]
             |
            GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
```

### Red LED (GPIO 27) Circuit
```
        GPIO 27 (Pin 13)
             |
             v
        [LED Anode]
             |
        [LED Cathode]
             |
        [330Ω Resistor]
             |
            GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
```

### Complete Wiring Table
| GPIO Pin | Physical Pin | To | Resistor | To | GND Pin |
|----------|--------------|-----|----------|-----|---------|
| 17       | 11           | → LED Anode | 330Ω | ← LED Cathode | Pin 6/9/14/20/25/30/34/39 |
| 27       | 13           | → LED Anode | 330Ω | ← LED Cathode | Pin 6/9/14/20/25/30/34/39 |

## Component Specifications

### LEDs
- **Forward Voltage (Vf)**: 
  - Red: 1.8-2.2V
  - Green: 2.0-2.5V
- **Maximum Current**: 20mA
- **Recommended Current**: 5-10mA

### Resistor Calculation
Using Ohm's Law: R = (Vcc - Vf - Vgpio) / I

For 5V supply with 10mA current and 2.2V LED forward voltage:
```
R = (5V - 2.2V - 0.6V) / 10mA = 220Ω
```

Common values: 220Ω, 330Ω, or 470Ω

### Recommended Components
- **LEDs**: Standard 5mm through-hole LEDs (diffuse or clear)
- **Resistors**: 1/4W metal film resistors (220Ω or 330Ω)
- **Jumper Wires**: 22AWG male-to-female jumper cables

## GPIO Configuration in Python

To use different GPIO pins, edit the Python script:

```python
# GPIO Pin Configuration
GREEN_LED_PIN = 17  # Change this to your GPIO pin
RED_LED_PIN = 27    # Change this to your GPIO pin
```

### Finding Available GPIO Pins

```bash
# Install GPIO utilities
sudo apt-get install python3-gpiozero

# Check GPIO status
gpioinfo
```

### Available GPIO Pins (Pi 4B)
Safe to use (typically unreserved):
- GPIO 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27

Reserved/Used:
- GPIO 2, 3 (I2C SDA, SCL)
- GPIO 14, 15 (UART TXD, RXD)

## Testing LED Connections

### Using GPIO Control Utility

Install wiringPi:
```bash
sudo apt-get install wiringpi
```

Test GPIO 17 (Green LED):
```bash
sudo gpio -g mode 17 out
sudo gpio -g write 17 1  # LED ON
sudo gpio -g write 17 0  # LED OFF
```

Test GPIO 27 (Red LED):
```bash
sudo gpio -g mode 27 out
sudo gpio -g write 27 1  # LED ON
sudo gpio -g write 27 0  # LED OFF
```

### Using Python

```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

# Test green LED
GPIO.output(17, GPIO.HIGH)
time.sleep(2)
GPIO.output(17, GPIO.LOW)

# Test red LED
GPIO.output(27, GPIO.HIGH)
time.sleep(2)
GPIO.output(27, GPIO.LOW)

GPIO.cleanup()
```

## Troubleshooting Hardware

### LED Not Lighting Up
1. **Check polarity**: Long leg (anode) goes to GPIO, short leg (cathode) goes to resistor
2. **Check resistor**: Use multimeter to verify resistance value
3. **Check GPIO pin**: Test with a known working LED
4. **Check power**: Measure voltage at GPIO pin when set HIGH

### Dim or Flickering LED
1. Check resistor value (may be too high)
2. Check for poor connections
3. Check GPIO pin current drive (Raspberry Pi GPIO is limited to 16mA per pin)

### GPIO Permission Issues
Run the program with sudo:
```bash
sudo python3 network_cable_tester.py
```

Or add user to gpio group:
```bash
sudo usermod -aG gpio $USER
sudo usermod -aG dialout $USER
```

## Safety Considerations

1. **Maximum GPIO Voltage**: 3.3V
2. **Maximum GPIO Current per Pin**: 16mA
3. **Total GPIO Current (all pins)**: 50mA
4. **Never connect GPIO directly to 5V**
5. **Always use current-limiting resistors with LEDs**
6. **Ensure proper GND connections**

## Additional GPIO Resources

- Official Raspberry Pi GPIO Documentation: https://www.raspberrypi.org/documentation/usage/gpio/
- GPIO Zero Library: https://gpiozero.readthedocs.io/
- RPi.GPIO Library: https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/
