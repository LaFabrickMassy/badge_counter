"""
WiFi Web Server for Badge Counter
Displays attendance figures on a web page accessible from the WiFi hotspot
"""

import socket
import time
import os
from machine import Pin, I2C, SPI
import SSD1306
import urtc
import NFC_PN532 as nfc
import network

# ==================== WiFi Configuration ====================
SSID = "badge_counter_hotspot"  # Change this to your desired hotspot name
PASSWORD = "fablab2024"  # Change this to a secure password

# ==================== Initialize WiFi ====================
wlan = network.WLAN(network.AP_IF)  # Access Point mode
wlan.config(essid=SSID, password=PASSWORD)
wlan.active(True)

print(f"WiFi Hotspot '{SSID}' is active")
print(f"IP Address: {wlan.ifconfig()[0]}")

# ==================== Initialize Hardware ====================
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Initialize RTC (connected to I2C)
i2c1 = I2C(1, scl=Pin(7), sda=Pin(6))
rtc = urtc.DS3231(i2c1)

# Display initialization
i2c0 = I2C(sda=Pin(20), scl=Pin(21), freq=400000)
display = SSD1306.SSD1306_I2C(128, 64, i2c0)

# NFC initialization
rst = Pin(16, Pin.OUT)
rst.value(0)
time.sleep(0.1)
rst.value(1)
time.sleep(0.5)

spi_dev = SPI(1, baudrate=400000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
cs = Pin(13, Pin.OUT)
cs.on()

ir = Pin(17, Pin.IN)
pn532 = nfc.PN532(spi_dev, cs, irq=ir, debug=False)
pn532.SAM_configuration()

# ==================== Data File Management ====================
DATA_FILE = "data.txt"

def count_attendance_today():
    """Count how many badges were scanned today"""
    try:
        current_date = get_current_date()
        count = 0
        with open(DATA_FILE, "r") as file:
            for line in file:
                if line.startswith(current_date):
                    count += 1
        return count
    except:
        return 0

def count_attendance_total():
    """Count total badges scanned"""
    try:
        with open(DATA_FILE, "r") as file:
            count = len(file.readlines())
        return count
    except:
        return 0

def get_latest_entries(limit=10):
    """Get the last N entries from the data file"""
    try:
        with open(DATA_FILE, "r") as file:
            lines = file.readlines()
        return lines[-limit:] if lines else []
    except:
        return []

def get_current_date():
    """Get current date in YYYY-MM-DD format"""
    current_datetime = rtc.datetime()
    return f"{current_datetime.year:04d}-{current_datetime.month:02d}-{current_datetime.day:02d}"

# ==================== HTML Page Generation ====================
def generate_html():
    """Generate the HTML page with attendance data"""
    today_count = count_attendance_today()
    total_count = count_attendance_total()
    latest = get_latest_entries(10)
    
    current_date = get_current_date()
    current_datetime = rtc.datetime()
    current_time = f"{current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d}"
    
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fréquentation FabLab</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                text-align: center;
            }}
            .timestamp {{
                text-align: center;
                color: #999;
                font-size: 14px;
                margin-bottom: 30px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .stat h2 {{
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat p {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .entries {{
                background: #f5f5f5;
                padding: 20px;
                border-radius: 10px;
                max-height: 300px;
                overflow-y: auto;
            }}
            .entries h3 {{
                color: #333;
                margin-bottom: 15px;
                font-size: 16px;
            }}
            .entry {{
                padding: 10px;
                background: white;
                margin-bottom: 8px;
                border-radius: 5px;
                font-size: 13px;
                color: #555;
                border-left: 4px solid #667eea;
            }}
            .entry strong {{
                color: #333;
            }}
            .refresh {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #999;
            }}
        </style>
        <meta http-equiv="refresh" content="10">
    </head>
    <body>
        <div class="container">
            <h1>📊 Fréquentation FabLab</h1>
            <div class="timestamp">Mise à jour: {date} à {time}</div>
            
            <div class="stats">
                <div class="stat">
                    <h2>{today}</h2>
                    <p>Aujourd'hui</p>
                </div>
                <div class="stat">
                    <h2>{total}</h2>
                    <p>Total</p>
                </div>
            </div>
            
            <div class="entries">
                <h3>Derniers passages:</h3>
                {entries_html}
            </div>
            
            <div class="refresh">Page actualisée automatiquement tous les 10 secondes</div>
        </div>
    </body>
    </html>
    """.format(
        date=current_date,
        time=current_time,
        today=today_count,
        total=total_count,
        entries_html="".join([f'<div class="entry"><strong>{entry.strip()}</strong></div>' for entry in reversed(latest)])
    )
    return html

# ==================== Web Server ====================
def start_web_server(port=80):
    """Start the web server"""
    socket_addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(socket_addr)
    server_socket.listen(1)
    
    print(f"Web server started on http://{wlan.ifconfig()[0]}:{port}")
    print("Open this URL in your browser to view attendance")
    
    display.fill(0)
    display.text("WiFi: " + SSID, 0, 0, 1)
    display.text("IP: " + wlan.ifconfig()[0], 0, 16, 1)
    display.text("Port: 80", 0, 32, 1)
    display.text("Server active!", 0, 48, 1)
    display.show()
    
    return server_socket

def handle_request(client_socket):
    """Handle incoming HTTP request"""
    try:
        request = client_socket.recv(1024).decode()
        
        # Send HTTP response
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
        response += generate_html()
        
        client_socket.sendall(response.encode())
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()

def read_nfc(dev, tmot):
    """Read NFC badge"""
    uid = dev.read_passive_target(timeout=tmot)
    if uid is not None:
        numbers = [i for i in uid]
        badge_ID = '{}-{}-{}-{}'.format(*numbers)
        
        current_datetime = rtc.datetime()
        sdate = f"{current_datetime.year:04d}-{current_datetime.month:02d}-{current_datetime.day:02d}"
        stime = f"{current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d}"
        ture = rtc.get_temperature()
        
        display.fill(0)
        display.text(badge_ID, 0, 0, 1)
        display.text(sdate, 0, 16, 1)
        display.text(stime, 0, 32, 1)
        display.text(f"{ture} deg C", 0, 48, 1)
        display.show()
        
        with open(DATA_FILE, "a") as file:
            file.write(f"{sdate} {stime}, {badge_ID}\r\n")
        
        print(f"Badge scanned: {badge_ID} at {sdate} {stime}")

# ==================== Main Loop ====================
if __name__ == "__main__":
    server_socket = start_web_server(80)
    
    try:
        while True:
            # Accept incoming connection
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            handle_request(client_socket)
            
            # Non-blocking NFC read
            read_nfc(pn532, 100)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Server stopped")
        server_socket.close()
