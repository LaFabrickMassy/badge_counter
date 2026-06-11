# WiFi Web Server Setup Guide

## Overview
This guide explains how to set up your Raspberry Pi Pico 2W as a WiFi hotspot that serves attendance figures on a web page.

## Requirements
- Raspberry Pi Pico 2W (with WiFi capability)
- MicroPython firmware installed
- Your existing hardware: RTC, display, NFC reader, SD card

## Step 1: Flash MicroPython on Pico 2W

1. Download MicroPython firmware for Pico 2W from: https://micropython.org/download/
2. Put your Pico in bootloader mode (hold BOOTSEL while connecting USB)
3. Copy the `.uf2` file to the `RPI-RP2` drive
4. Wait for the device to reboot

## Step 2: Configure WiFi Credentials

Edit `webserver.py` and modify these lines:

```python
SSID = "badge_counter_hotspot"  # Your WiFi hotspot name
PASSWORD = "fablab2024"  # Your WiFi password
```

## Step 3: Upload Files to Pico

1. Use Thonny IDE or rshell to upload:
   - `webserver.py`
   - Your existing files: `integration.py`, libraries, etc.

2. Set `webserver.py` as the main script (rename to `main.py` or configure startup)

## Step 4: Run the Server

1. Power on your Pico 2W
2. It will create a WiFi hotspot with the name you configured
3. The OLED display will show:
   - WiFi hotspot name
   - IP address (usually `192.168.4.1`)
   - Server status

## Step 5: Access the Web Interface

### From any device on the network:
1. Connect to the WiFi hotspot (SSID: `badge_counter_hotspot`)
2. Open a browser and go to: `http://192.168.4.1`
3. You'll see a dashboard with:
   - **Today's count**: Number of badges scanned today
   - **Total count**: All-time badge scans
   - **Recent entries**: Last 10 scanned badges with timestamps

## Features

✅ **Real-time attendance display**  
✅ **Auto-refreshing page** (updates every 10 seconds)  
✅ **Beautiful responsive design** (works on mobile)  
✅ **Date/time display** (from RTC)  
✅ **Badge scanning** (continues while serving web requests)  

## Troubleshooting

### WiFi not appearing
- Check if Pico 2W has WiFi antenna connected
- Verify MicroPython version supports WiFi
- Restart the Pico

### Can't connect to IP address
- Try `192.168.4.1` (default AP IP)
- Check Pico's OLED display for the actual IP
- Ensure you're connected to the correct WiFi

### Web page not loading
- Check browser console (F12) for errors
- Verify data.txt file exists with proper format
- Check Pico terminal for error messages

### Performance issues
- Reduce web requests (increase refresh interval in HTML)
- Optimize file operations (cache frequently accessed data)
- Consider adding pagination to large data files

## Optional Enhancements

### 1. Add Daily Statistics
```python
def get_statistics_by_day():
    # Returns attendance count per day
    pass
```

### 2. Export Data as CSV
```python
# Add endpoint for CSV download
@server.route('/export')
def export_csv():
    # Serve data.txt with CSV headers
    pass
```

### 3. Add Authentication
```python
# Protect the dashboard with a simple password
if request.headers.get('Authorization') != 'Basic ...':
    return 401 Unauthorized
```

### 4. Log to Cloud
```python
# Send data to external service (Google Sheets, InfluxDB, etc.)
```

## File Format

The `data.txt` file uses this format:
```
YYYY-MM-DD HH:MM:SS, XX-XX-XX-XX
2026-06-11 14:30:45, 12-34-56-78
2026-06-11 14:35:22, 87-65-43-21
```

## Additional Resources

- MicroPython docs: https://docs.micropython.org/
- Pico W Documentation: https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html
- Socket programming: https://docs.micropython.org/en/latest/library/socket.html
