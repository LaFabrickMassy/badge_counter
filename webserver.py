"""
WiFi Web Server for Badge Counter
Displays attendance figures on a web page accessible from the WiFi hotspot
"""

import socket
import time
import os
import json
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

def get_current_time():
    """Get current time in HH:MM:SS format"""
    current_datetime = rtc.datetime()
    return f"{current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d}"

# ==================== API Data Endpoint ====================
def get_api_data():
    """Generate JSON data for API endpoint"""
    today_count = count_attendance_today()
    total_count = count_attendance_total()
    latest = get_latest_entries(10)
    
    current_date = get_current_date()
    current_time = get_current_time()
    
    # Strip whitespace and reverse to show newest first
    entries = [entry.strip() for entry in reversed(latest)]
    
    data = {
        "today_count": today_count,
        "total_count": total_count,
        "current_date": current_date,
        "current_time": current_time,
        "latest_entries": entries
    }
    
    return json.dumps(data)

# ==================== File Serving ====================
def read_file(filepath):
    """Read file content from filesystem"""
    try:
        with open(filepath, "r") as f:
            return f.read()
    except:
        return None

def get_mime_type(filepath):
    """Determine MIME type based on file extension"""
    if filepath.endswith('.html'):
        return 'text/html'
    elif filepath.endswith('.css'):
        return 'text/css'
    elif filepath.endswith('.js'):
        return 'application/javascript'
    elif filepath.endswith('.json'):
        return 'application/json'
    else:
        return 'text/plain'

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

def parse_request(request_str):
    """Parse HTTP request and extract the path"""
    try:
        lines = request_str.split('\r\n')
        request_line = lines[0]
        parts = request_line.split(' ')
        if len(parts) >= 2:
            path = parts[1]
            return path
    except:
        pass
    return '/'

def handle_request(client_socket):
    """Handle incoming HTTP request"""
    try:
        request = client_socket.recv(1024).decode()
        path = parse_request(request)
        
        # Route handling
        if path == '/' or path == '/index.html':
            content = read_file('index.html')
            if content:
                mime_type = 'text/html'
                response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}; charset=utf-8\r\nContent-Length: {len(content)}\r\n\r\n"
                client_socket.sendall(response.encode() + content.encode())
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\nindex.html not found"
                client_socket.sendall(response.encode())
        
        elif path == '/style.css':
            content = read_file('style.css')
            if content:
                mime_type = 'text/css'
                response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(content)}\r\n\r\n"
                client_socket.sendall(response.encode() + content.encode())
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\nstyle.css not found"
                client_socket.sendall(response.encode())
        
        elif path == '/api/data':
            data = get_api_data()
            mime_type = 'application/json'
            response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(data)}\r\n\r\n"
            client_socket.sendall(response.encode() + data.encode())
        
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\nNot found"
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
