"""
Inductance is formed from 6 inductors.
Two full bobbins then 3/4, 1/2 an 1/4 wound bobbins.
These are switched in series giving 15 different inductance values.

Measured inductance.
    Full bobbin - 100uH
    3/4 bobbin - 75uH
    1/2 bobbin - 50uH
    1/4 bobbin - 25uH

This gives inductance values from 25uH to 300uH in approx 25uH steps

"""

# System imports
import os, sys
from time import sleep

# Library imports
testing = False
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("Error importing RPi.GPIO! Using test mode.")
    testing = True

# Application imports

# Maps relay to GPIO pins in BCM numbering scheme.
# Corresponding to relays 1 - 5
pinArray = [26,16,12,25,24]

# Inductance map
# This map should be 12 elements long.
# i.e. {inductor-value : [rel, rel, ..], inductor-value ...}
actMap = {
    4 : [1,],
    8 : [2,],
    15 : [3,],
    28 : [4,],
    42 : [5,],
}

def init_pins():
    for pin in pinArray:
        GPIO.setup(pin, GPIO.OUT)
    
def all_off():
    for pin in pinArray:
        GPIO.output(pin, GPIO.LOW)

def rly_on(rly):
    GPIO.output(pinArray[rly], GPIO.HIGH)
    
# Entry point
if __name__ == '__main__':
    
    if not testing:
        GPIO.setmode(GPIO.BCM)
        init_pins()
        all_off()
        
    # Run through all values
    print('Series values...')
    for n in (4,8,15,28,42):
        rlys = actMap[n]
        if testing:
            print("Array for %duH is %s" % (n, str(rlys)))
        else:
            print("Array for %duH is %s" % (n, str(rlys)))
            all_off()
            for rly in rlys:
                if testing:
                    print("Set rly: ", rly-1)
                else:
                    rly_on(rly-1)
        sleep(3)

            
    