# Network Configuration Examples for Raspberry Pi

## Option 1: DHCP Configuration (Automatic IP Assignment)

### Using netplan (Ubuntu/Debian-based systems)

File: `/etc/netplan/01-netcfg.yaml`

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: true
      dhcp4-overrides:
        route-metric: 100
    eth1:
      dhcp4: true
      dhcp4-overrides:
        route-metric: 200
```

Apply with:
```bash
sudo netplan apply
```

### Using /etc/network/interfaces (Classic Raspbian)

File: `/etc/network/interfaces`

```
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp

auto eth1
iface eth1 inet dhcp
```

Restart networking:
```bash
sudo systemctl restart networking
```

## Option 2: Static IP Configuration

### Using netplan

File: `/etc/netplan/01-netcfg.yaml`

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.1.10/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
    eth1:
      dhcp4: false
      addresses:
        - 192.168.1.11/24
```

Apply with:
```bash
sudo netplan apply
```

### Using /etc/network/interfaces

File: `/etc/network/interfaces`

```
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 192.168.1.10
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 8.8.4.4

auto eth1
iface eth1 inet static
    address 192.168.1.11
    netmask 255.255.255.0
```

Restart networking:
```bash
sudo systemctl restart networking
```

## Verification

After configuration, verify the setup:

```bash
# Check all interfaces
ip link show

# Check IP addresses
ip addr show

# Test connectivity between interfaces
ping -I eth0 192.168.1.11
ping -I eth1 192.168.1.10

# Check routing table
ip route show
```

## Troubleshooting Network Configuration

### Check if interfaces are up
```bash
ip link show
```

### Bring interface up/down
```bash
sudo ip link set eth0 up
sudo ip link set eth0 down
```

### Manually assign temporary IP
```bash
sudo ip addr add 192.168.1.10/24 dev eth0
```

### Remove temporary IP
```bash
sudo ip addr del 192.168.1.10/24 dev eth0
```

### View network connections
```bash
netstat -an | grep LISTEN
```

### Check DNS resolution
```bash
nslookup google.com
```

### View systemd network status
```bash
systemctl status systemd-networkd
journalctl -u systemd-networkd -f
```
