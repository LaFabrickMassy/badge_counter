# Objectif : intégrer l'ensemble des périphs : rtc, écran, buzzer, lecteur de badge, lecteur de carte sd

from machine import Pin, I2C, SPI
import SSD1306
import time
import urtc
import NFC_PN532 as nfc


days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Initialize RTC (connected to I2C)
i2c1 = I2C(1, scl=Pin(7), sda=Pin(6))
rtc = urtc.DS3231(i2c1)

# display initialisation
i2c0 = I2C(sda=Pin(20), scl=Pin(21), freq=400000)
print('Scan i2c bus...')
devices = i2c0.scan()

print('Scan i2c bus...')
devices = i2c0.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))

  for device in devices:  
    print("Decimal address: ",device," | Hexa address: ",hex(device))

display = SSD1306.SSD1306_I2C(128, 64, i2c0)
display.text('Hello, World!', 0, 0, 1)
display.show()


# nfc initialisation
rst = Pin(16, Pin.OUT)
rst.value(0)
time.sleep(0.1)
rst.value(1)
time.sleep(0.5)  # Wait for PN532 to boot into SPI mode

# SPI
spi_dev = SPI(1, baudrate=400000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
cs = Pin(13, Pin.OUT)
cs.on()

ir = Pin(17, Pin.IN)
# SENSOR INIT
pn532 = nfc.PN532(spi_dev,cs, irq=ir, debug=False)
ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

# FUNCTION TO READ 
def read_nfc(dev, tmot):
    """Accepts a device and a timeout in millisecs """
    # print('Reading...')
    uid = dev.read_passive_target(timeout=tmot)
    if uid is None:
        print('.', end='')
    else:
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
        
        with open("data.txt", "a") as file:
            file.write(f"{sdate} {stime}, {badge_ID}\r\n")
        
        print('Found card with UID:', [hex(i) for i in uid])
        print('Number_id: {}'.format(badge_ID))
        
while True:
    read_nfc(pn532, 2000)
    time.sleep(0.1)