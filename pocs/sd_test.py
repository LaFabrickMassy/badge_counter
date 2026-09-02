import machine
import sdcard
import uos

# Configure the Chip Select pin
CS = machine.Pin(1, machine.Pin.OUT)

# Initialize SPI1 with the specified pins and baud rate
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4))

# Initialize the SD card object
sd = sdcard.SDCard(spi, CS)

# Mount the FAT filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

print("SD card mounted successfully!")
print("Files on SD card:", uos.listdir("/sd"))

# Create a file and write data to it
with open("/sd/data.txt", "w") as file:
    print("Writing to data.txt...")
    file.write("Welcome to microcontrollerslab!\r\n")
    file.write("This is a test\r\n")

print("Write complete.")

# Open the file and read the data back
with open("/sd/data.txt", "r") as file:
    print("Reading data.txt...")
    data = file.read()
    print(data)
    