#boot.py
import network
import time

# --- WIFI SETTINGS ---
SSID = "......"
PASSWORD = "......"

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(SSID, PASSWORD)
        
        # Wait for connection
        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)

    if wlan.isconnected():
        print('Connected! Network config:', wlan.ifconfig())
    else:
        print('WiFi connection failed.')

# Automatically run the connection
do_connect()
