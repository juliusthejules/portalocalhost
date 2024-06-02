import json
import os
import subprocess

# Path to the configuration file
config_path = "./config.json"

# Function to read the JSON configuration file
def load_config(path):
    with open(path, 'r') as file:
        return json.load(file)

# Function to apply the configuration settings
def apply_settings(config):
    for item in config["configurations"]:
        description = item.get("description", "")
        settings = item.get("settings", {})
        
        if "closePings" in settings and settings["closePings"]:
            # Command to disable pings (example)
            subprocess.run(["sysctl", "-w", "net.ipv4.icmp_echo_ignore_all=1"], check=True)
        
        if "locationEnabled" in settings:
            # Command to disable location (example)
            subprocess.run(["settings", "put", "secure", "location_mode", "0" if not settings["locationEnabled"] else "3"], check=True)
        
        if "primaryDNSServerAddress" in settings and "secondaryDNSServerAddress" in settings:
            # Command to set DNS (example)
            primary_dns = settings["primaryDNSServerAddress"]
            secondary_dns = settings["secondaryDNSServerAddress"]
            subprocess.run(["setprop", "net.dns1", primary_dns], check=True)
            subprocess.run(["setprop", "net.dns2", secondary_dns], check=True)
        
        if "cacheEnabled" in settings:
            # Command to disable cache (example)
            cache_enabled = settings["cacheEnabled"]
            if not cache_enabled:
                subprocess.run(["sync"], check=True)
                subprocess.run(["echo", "3", ">", "/proc/sys/vm/drop_caches"], shell=True, check=True)
        
        if "cookieEnabled" in settings:
            # Example of clearing cookies
            if not settings["cookieEnabled"]:
                paths = item.get("paths", {})
                for browser, path in paths.items():
                    if os.path.exists(path):
                        os.remove(path)
        
        if "clearAllCookies" in settings and settings["clearAllCookies"]:
            # Clear all cookies
            paths = item.get("paths", {})
            for browser, path in paths.items():
                if os.path.exists(path):
                    os.remove(path)
        
        if "hostname" in settings:
            # Command to change hostname to localhost IP address
            new_hostname = settings["hostname"]
            subprocess.run(["hostnamectl", "set-hostname", new_hostname], check=True)
        
        if "ipv4Address" in settings:
            # Command to hide IPv4 address
            new_ipv4 = settings["ipv4Address"]
            subprocess.run(["ifconfig", "lo", new_ipv4, "netmask", "255.0.0.0"], check=True)
        
        if "ipv6Address" in settings:
            # Command to hide IPv6 address
            new_ipv6 = settings["ipv6Address"]
            subprocess.run(["ifconfig", "lo", "inet6", "add", new_ipv6], check=True)

# Load and apply the configuration
config = load_config(config_path)
apply_settings(config)
