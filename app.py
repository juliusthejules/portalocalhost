from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

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
        
        if "clearAllCookies" in settings and settings["clearAllCookies"]:
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

@app.route('/apply-config', methods=['POST'])
def apply_config():
    config = request.json
    apply_settings(config)
    return jsonify({"status": "Configuration applied successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
