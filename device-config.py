import os
import subprocess
import json

def apply_settings(config):
    for item in config["configurations"]:
        description = item.get("description", "")
        settings = item.get("settings", {})
        
        if "closePings" in settings and settings["closePings"]:
            subprocess.run(["sysctl", "-w", "net.ipv4.icmp_echo_ignore_all=1"], check=True)
        
        if "locationEnabled" in settings:
            subprocess.run(["settings", "put", "secure", "location_mode", "0" if not settings["locationEnabled"] else "3"], check=True)
        
        if "primaryDNSServerAddress" in settings and "secondaryDNSServerAddress" in settings:
            primary_dns = settings["primaryDNSServerAddress"]
            secondary_dns = settings["secondaryDNSServerAddress"]
            subprocess.run(["setprop", "net.dns1", primary_dns], check=True)
            subprocess.run(["setprop", "net.dns2", secondary_dns], check=True)
        
        if "cacheEnabled" in settings:
            cache_enabled = settings["cacheEnabled"]
            if not cache_enabled:
                subprocess.run(["sync"], check=True)
                subprocess.run(["echo", "3", ">", "/proc/sys/vm/drop_caches"], shell=True, check=True)
        
        if "cookieEnabled" in settings:
            paths = item.get("paths", {})
            for browser, path in paths.items():
                if os.path.exists(path):
                    os.remove(path)
        
        if "hostname" in settings:
            new_hostname = settings["hostname"]
            subprocess.run(["hostnamectl", "set-hostname", new_hostname], check=True)
        
        if "ipv4Address" in settings:
            new_ipv4 = settings["ipv4Address"]
            subprocess.run(["ifconfig", "lo", new_ipv4, "netmask", "255.0.0.0"], check=True)
        
        if "ipv6Address" in settings:
            new_ipv6 = settings["ipv6Address"]
            subprocess.run(["ifconfig", "lo", "inet6", "add", new_ipv6], check=True)
        
        if "macAddress" in settings:
            new_mac = settings["macAddress"]
            subprocess.run(["ifconfig", "eth0", "hw", "ether", new_mac], check=True)
        
        if "bluetoothAddress" in settings:
            new_bt = settings["bluetoothAddress"]
            subprocess.run(["hciconfig", "hci0", "reset"], check=True)
            subprocess.run(["bdaddr", "hci0", new_bt], check=True)

if __name__ == "__main__":
    config_path = "./config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    apply_settings(config)