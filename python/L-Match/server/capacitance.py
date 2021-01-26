#!/usr/bin/env python3
#
# capacitance.py
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
Capacitance is formed from double sided PCB.
There are two PCB slabs that sandwich the components between them.
Thus the PCB is both a structure to hold the components (relays and coils)
and is itself the capacitance.

Each slab is approx 1000pf, so maximum capacitance is around 2000pf.
One slab is carved into 6 segments in a divide by 2 manner. Thus the
segments are, if they were accurately made and ignoring discounted parts:

Rounding up to power of 2 is the idealised progression. 
    1024pf
    512pf
    256pf
    128pf
    64pf
    32pf
    16pf

Measured values are:

    1010pf
    504pf
    281pf
    139pf
    79pf
    43pf
    24pf

These will be trimmed down to closer to the idealised values.

This gives capacitance values from (idealised) 16pf to 2024pf in 16pf steps (VERY APPROXIMATELY).
This means there are 128 capacitance steps.

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
# Corresponding to relays 0 - 6 where 0 == 16pf and 6 == 1024pf
pinArray = [4,17,27,22,5,6,13]

# Cap value of each division
# Relay 0 = 16pf to relay 6 = 1024pf
capArray = [16,32,64,128,256,512,1024]

# calculated map of capacitance to relay activations
# This map should be 128 elements long.
# i.e. [[cap-value, [rel, rel, ..]], [cap-value, [...]], ...}
actMap = []

#----------------------------------------------------
def makeActMap():
    
    # Iterate every capacitance size
    for c in range(16,2048,16):
        if c in capArray:
            # Exact value
            rly = capArray.index(c)
            actMap.append([c,[rly,]])
        else:
            # Find combination to give correct capacitance
            acc = []
            remC = c
            while True:
                
                # Find the highest capacitance value which is an integral
                nextC = highCap(remC)
                if nextC == 0:
                    break
                else:
                    acc.append(nextC)
                    remC = remC-nextC
            rlys = []
            for v in acc:
                rlys.append(capArray.index(v))
            actMap.append([c,rlys])

#----------------------------------------------------    
def highCap(c):
    if c == 0: return 0
    # Find highest value cap for this C
    last = 0
    for v in reversed(capArray):
        if v/c <= 1.0:
            return v
    return 0

#----------------------------------------------------
def init_pins():
    for pin in pinArray:
        GPIO.setup(pin, GPIO.OUT)

#----------------------------------------------------    
def all_off():
    for pin in pinArray:
        GPIO.output(pin, GPIO.LOW)

#----------------------------------------------------
def rly_on(rly):
    GPIO.output(pinArray[rly], GPIO.HIGH)

#----------------------------------------------------
def init():
    makeActMap()
    if not testing:
        # Initialise relays
        GPIO.setmode(GPIO.BCM)
        init_pins()
        all_off()
        
#----------------------------------------------------
def set_value(index):
    # Index 0-127 as there are 128 values in the matrix
    item = actMap[index]
    print("Setting relays for %dpf" % item[0])
    if not testing:
        all_off()
        for rly in item[1]:
            rly_on(rly) 

            
    