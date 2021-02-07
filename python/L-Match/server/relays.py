#!/usr/bin/env python3
#
# relays.py
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

# System imports
import os, sys
from time import sleep

# Library imports
gpio_test_mode = False
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("GPIO - not running on RPi, using test mode!")
    gpio_test_mode = True

# Application imports

class Relays:

    #----------------------------------------------------
    def init(self):
        if not gpio_test_mode:
            # Initialise relays
            GPIO.setmode(GPIO.BCM)
            self.__pinArray = []
    
    #----------------------------------------------------
    def init_pins(self, pin_array):
        self.__pinArray = pin_array
        if not gpio_test_mode:
            # Initialise pins
            for pin in pin_array:
                GPIO.setup(pin, GPIO.OUT)

    #----------------------------------------------------
    def set_pins(self, pin_array):
        # Energise all relys in the array
        if not gpio_test_mode:
            self.__rlys_on(self.__pinArray, pin_array)
    
    #----------------------------------------------------
    def close(self):
        # Cleanup before exit
        if not gpio_test_mode:
            GPIO.cleanup()
    
    # =================================================================================
    # PRIVATE
    def __rlys_on(self, all_pins, energise_pins):
        self.__all_off(all_pins)
        for pin in energise_pins:
            GPIO.output(pin, GPIO.HIGH)
        
    def __all_off(self, all_pins):
        for pin in all_pins:
            GPIO.output(pin, GPIO.LOW)
        