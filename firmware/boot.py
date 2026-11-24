# boot.py - Startup initialization for ESP8266 Power Monitor
import gc
import network
import time
import ujson

gc.enable()

def load_config():
    try:
        with open("config.json", "r") as f:
            return ujson.load(f)
    except Exception as e:
        print("[BOOT] Warning: Could not load config.json:", e)
        return {}

config = load_config()
wifi_cfg = config.get("wifi", {})
ssid = wifi_cfg.get("ssid", "")
password = wifi_cfg.get("password", "")

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

if ssid and ssid != "YOUR_WIFI_SSID":
    print("[BOOT] Connecting to Wi-Fi SSID:", ssid)
    sta_if.connect(ssid, password)
    start_time = time.time()
    while not sta_if.isconnected() and (time.time() - start_time) < 10:
        time.sleep(0.5)

if sta_if.isconnected():
    ip_info = sta_if.ifconfig()
    print("[BOOT] Wi-Fi Connected! IP Address:", ip_info[0])
else:
    print("[BOOT] Wi-Fi STA not connected. Starting Access Point mode...")
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    ap_ssid = wifi_cfg.get("ap_ssid", "ESP8266-PowerMonitor")
    ap_pass = wifi_cfg.get("ap_password", "")
    if ap_pass:
        ap_if.config(essid=ap_ssid, password=ap_pass, authmode=network.AUTH_WPA_WPA2_PSK)
    else:
        ap_if.config(essid=ap_ssid, authmode=network.AUTH_OPEN)
    print("[BOOT] AP Started! SSID:", ap_ssid, "IP: 192.168.4.1")
