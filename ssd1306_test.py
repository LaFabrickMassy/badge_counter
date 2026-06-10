from machine import Pin, I2C
import SSD1306


i2c = I2C(sda=Pin(20), scl=Pin(21), freq=400000)

#i2c = I2C(1, scl=Pin(7), sda=Pin(6))

print('Scan i2c bus...')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))

  for device in devices:  
    print("Decimal address: ",device," | Hexa address: ",hex(device))



display = SSD1306.SSD1306_I2C(128, 64, i2c)

display.text('Hello, World!', 0, 0, 1)
display.show()