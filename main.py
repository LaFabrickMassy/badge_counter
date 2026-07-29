from machine import Pin, I2C, SPI
import SSD1306
import urtc
import time
import sdcard
import uos
import NFC_PN532 as nfc
from music import play, imperial_march, hello_world, game_over, bipbip
from attendancemodel import AttendanceModel, BadgingStatus

class BadgeCounter:
    
    def __init__(self, 
                 display_i2c=0, display_sda=20, display_scl=21,
                 rtc_i2c=1, rtc_sda=6, rtc_scl=7,
                 sd_spi=0, sd_mosi=3, sd_miso=4, sd_sck=2, sd_cs=1,
                 nfc_spi=1, nfc_mosi=11, nfc_miso=12, nfc_sck=10, nfc_rst=16, nfc_cs=13, nfc_irq=17,
                 buzzer=15):
        
        # display communication
        self.display_i2c = I2C(id=display_i2c, sda=Pin(display_sda), scl=Pin(display_scl), freq=400000)
        
        # rtc communication
        self.rtc_i2c = I2C(id=rtc_i2c, scl=Pin(rtc_scl), sda=Pin(rtc_sda))
        
        # sd card communication
        self.sd_spi = machine.SPI(sd_spi,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(sd_sck),
                  mosi=machine.Pin(sd_mosi),
                  miso=machine.Pin(sd_miso))
        self.sd_cs = sd_cs
        
        # nfc communication
        self.nfc_rst = nfc_rst
        self.nfc_cs = nfc_cs
        self.nfc_irq = nfc_irq
        self.nfc_spi = SPI(nfc_spi, baudrate=400000, sck=Pin(nfc_sck), mosi=Pin(nfc_mosi), miso=Pin(nfc_miso))
        
        # buzzer
        self.buzzer = buzzer

        
    def init_display(self):
        self.display = SSD1306.SSD1306_I2C(128, 64, self.display_i2c)
        
    def init_rtc(self):
        self.rtc = urtc.DS3231(self.rtc_i2c)
        
    def init_sd(self):
        # Configure the Chip Select pin
        CS_SD = machine.Pin(self.sd_cs, machine.Pin.OUT)

        # Initialize the SD card object
        sd = sdcard.SDCard(self.sd_spi, CS_SD)

        # Mount the FAT filesystem
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, "/sd")
        
    def init_nfc(self):
        rst = Pin(self.nfc_rst, Pin.OUT)
        rst.value(0)
        cs = Pin(self.nfc_cs, Pin.OUT)
        cs.on()
        ir = Pin(self.nfc_irq, Pin.IN)

        time.sleep(0.1)
        rst.value(1)
        time.sleep(0.5)  # Wait for PN532 to boot into SPI mode

        # SENSOR INIT
        self.pn532 = nfc.PN532(self.nfc_spi, cs, irq=ir, debug=False)
        ic, ver, rev, support = self.pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        self.pn532.SAM_configuration()
        
        # TODO: proprifier music
    def init_buzzer(self):
        play(hello_world)
        
    def init_data(self):
        # initialiser les données
        # le modele doit etre initialisé après rtc
        self.model = AttendanceModel(rtc=self.rtc, datafilename='/sd/data.txt')
        self.model.read_data()
        self.model.export_stats_to_csv()
        return
        
    def refresh_display(self):
        
        current_datetime = self.rtc.datetime()
        sdate = f"{current_datetime.year:04d}-{current_datetime.month:02d}-{current_datetime.day:02d}"
        stime = f"{current_datetime.hour:02d}:{current_datetime.minute:02d}:{current_datetime.second:02d}"
        nvisits = f"Visites: {self.model.visits()}"

        self.display.fill(0) 
        self.display.text(sdate, 0,0, 1)
        self.display.text(stime, 0,10, 1)
        self.display.text(nvisits, 0, 24, 1)
        self.display.show()       
        
    def read_badge(self):
        uid, length = self.pn532.read_passive_target_fablab(timeout=1000) 
        if uid is not None:
            numbers = [i for i in uid]
            print(f"UID: {numbers}, frame_length: {length}")
            # play(imperial_march)
            result = self.model.handle_event(uid, length)
            print(f"Result : {result}")
            if result == BadgingStatus.PASSBACK:
                play(game_over)
                self.refresh_display()
            elif result == BadgingStatus.NOT_THALES:
                play(bipbip)
                self.refresh_display()
            elif result == BadgingStatus.OK:
                play(imperial_march)
                self.refresh_display()
                self.model.export_stats_to_csv()
        
    def start(self):
        self.init_display()
        self.init_rtc()
        self.init_sd()
        self.init_nfc()
        self.init_buzzer()
        self.init_data()
        self.refresh_display()
        
        while(True):
            self.read_badge()
            self.refresh_display()
        
if __name__ == "__main__":
    counter = BadgeCounter()
    counter.start()
        