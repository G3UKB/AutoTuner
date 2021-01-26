#!/usr/bin/env python3
#
# inductance.py
# 
# Copyright (C) 2021 by G3UKB Bob Cowdery
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#    
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#    
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#    
#  The author can be reached by email at:   
#     bob@bobcowdery.plus.com
#

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
actMap = [
    [4, [1,]],
    [8, [2,]],
    [15, [3,]],
    [28, [4,]],
    [42, [5,]],
]

def init_pins():
    for pin in pinArray:
        GPIO.setup(pin, GPIO.OUT)
    
def all_off():
    for pin in pinArray:
        GPIO.output(pin, GPIO.LOW)

def rly_on(rly):
    GPIO.output(pinArray[rly], GPIO.HIGH)

#----------------------------------------------------
def init():
    if not testing:
        # Initialise relays
        GPIO.setmode(GPIO.BCM)
        init_pins()
        all_off()
        
#----------------------------------------------------
def set_value(index):
    # Index 0-4 as there are 5 values in the matrix
    item = actMap[index]
    print("Setting inductor for %duH" % item[0])
    if not testing:
        for rly in item[1]:
            rly_on(rly)


            
    