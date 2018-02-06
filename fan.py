#!/usr/bin python3

import RPi.GPIO as GPIO
from time import sleep
import psutil
from subprocess import PIPE, Popen

# https://www.raspberrypi.org/forums/viewtopic.php?t=22180
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

# https://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_id, GPIO.OUT, initial=GPIO.LOW)

pin_id = 25
max_temp = 60 # https://www.raspberrypi.org/forums/viewtopic.php?t=39953
pooling_time = 60 

while True:
	cpu_temperature = get_cpu_temperature()
	print(cpu_temperature)
	if cpu_temperature > max_temp:
		GPIO.output(pin_id, GPIO.HIGH)
	else:
		GPIO.output(pin_id, GPIO.LOW)
	sleep(pooling_time)
