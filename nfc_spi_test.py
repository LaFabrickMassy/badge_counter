import NFC_PN532 as nfc
from machine import Pin, SPI
from machine import Pin
import time

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
        print('.', end=' ')
    else:
        numbers = [i for i in uid]
        string_ID = '{}-{}-{}-{}'.format(*numbers)
        print('Found card with UID:', [hex(i) for i in uid])
        print('Number_id: {}'.format(string_ID))

while True:
    read_nfc(pn532, 2000)