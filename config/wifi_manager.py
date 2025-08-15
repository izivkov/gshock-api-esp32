import network
import socket
import time
import json
import os
import machine

CONFIG_FILE = "config.json"

# ---------------------------
# Helper: Save & Load Config
# ---------------------------
def save_config(ssid, password):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"ssid": ssid, "password": password}, f)

def load_config():
    if CONFIG_FILE in os.listdir():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None

# ---------------------------
# Try connecting to Wi-Fi
# ---------------------------
def connect_station(ssid, password, timeout=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print(f"Connecting to {ssid}...")
    for _ in range(timeout * 2):  # wait in 0.5 sec steps
        if wlan.isconnected():
            print("Connected:", wlan.ifconfig())
            return True
        time.sleep(0.5)

    print("Connection failed.")
    return False

# ---------------------------
# Start Captive Portal AP
# ---------------------------
def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="ESP32_Setup", authmode=network.AUTH_OPEN)
    print("AP started, connect to 'ESP32_Setup' and go to http://192.168.4.1")
    return ap

# ---------------------------
# Captive Portal Web Page
# ---------------------------
def portal_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Web server listening on port 80...")

    while True:
        cl, addr = s.accept()
        req = cl.recv(1024).decode()
        if "GET / " in req:
            html = """\
HTTP/1.1 200 OK

<html>
  <head><title>ESP32 WiFi Setup</title></head>
  <body>
    <h2>WiFi Setup</h2>
    <form action="/connect" method="get">
      SSID: <input type="text" name="ssid"><br>
      Password: <input type="password" name="password"><br>
      <input type="submit" value="Connect">
    </form>
  </body>
</html>
"""
            cl.send(html)
        elif "GET /connect?" in req:
            # Parse SSID and password
            try:
                params = req.split(" ")[1].split("?")[1]
                query = {}
                for pair in params.split("&"):
                    k, v = pair.split("=")
                    query[k] = v.replace("%20", " ")
                ssid = query.get("ssid")
                password = query.get("password")
                save_config(ssid, password)
                cl.send("HTTP/1.1 200 OK\r\n\r\nSaved! Rebooting...")
                cl.close()
                machine.reset()
            except Exception as e:
                print("Error parsing request:", e)
        cl.close()

# ---------------------------
# Main Wi-Fi Manager
# ---------------------------
def wifi_manager():
    cfg = load_config()
    if cfg and connect_station(cfg["ssid"], cfg["password"]):
        return True  # Connected with saved credentials

    # Start AP + Captive Portal
    ap = start_ap()
    portal_server()

# ---------------------------
# Run if main
# ---------------------------
if __name__ == "__main__":
    wifi_manager()
