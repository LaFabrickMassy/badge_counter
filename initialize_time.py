# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-ds3231-rtc-micropython/

import time
import urtc
from machine import I2C, Pin

# Set the current time using a specified time tuple
# Time tuple: (year, month, day, day of week, hour, minute, seconds, milliseconds)
initial_time_tuple = (2026, 6, 16, 13, 26, 0, 0, 0)



# Initialize RTC (connected to I2C)
i2c = I2C(1, scl=Pin(7), sda=Pin(6))
rtc = urtc.DS3231(i2c)


# Or get the local time from the system
#initial_time_tuple = time.localtime()  # tuple (microPython)
initial_time_seconds = time.mktime(initial_time_tuple)  # local time in seconds

# Convert to tuple compatible with the library
initial_time = urtc.seconds2tuple(initial_time_seconds)

# Sync the RTC
rtc.datetime(initial_time)

current_datetime = rtc.datetime()
temperature = rtc.get_temperature()

# Display time details
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
print('Current date and time:')
print('Year:', current_datetime.year)
print('Month:', current_datetime.month)
print('Day:', current_datetime.day)
print('Hour:', current_datetime.hour)
print('Minute:', current_datetime.minute)
print('Second:', current_datetime.second)
print('Day of the Week:', days_of_week[current_datetime.weekday])
print(f"Current temperature: {temperature}°C")    
