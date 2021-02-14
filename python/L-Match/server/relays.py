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
            # Set mode
            GPIO.setmode(GPIO.BCM)
            # Will hold current array of all configured pins
            self.__pinArray = []
    
    #----------------------------------------------------
    def init_pins(self, pin_array):
        # Initialise all pins in the pin array
        #           pin,invert
        # Form is: [[4, False], [17, False], [18, False]]
        for pin in pin_array:
            if pin not in self.__pinArray:
                self.__pinArray.append(pin)
        if gpio_test_mode:
            print ('Initialise pins %s' % str(pin_array))
        else:
            # Initialise pins
            for pin in pin_array:
                GPIO.setup(int(pin[0]), GPIO.OUT)

    #----------------------------------------------------
    def set_pins(self, pin_array):
        # Energise all relays in the array
        #           pin,invert
        # Form is: [[4, False], [17, False], [18, False]]
        if gpio_test_mode:
            print ('Energise pins %s' % str(pin_array))
        else:
            self.__all_off(self.__pinArray)
            self.__rlys_on(self.__pinArray, pin_array)
    
    #----------------------------------------------------
    def cycle_pins(self, pin_array):
        # Cycle relays in the map for a test
        #           pin,invert
        # Form is: [[4, False], [17, False], [18, False]]
        if gpio_test_mode:
            print ('Cycle pins %s' % str(pin_array))
        else:
            self.__all_off(self.__pinArray)
        for n in range(len(pin_array)):
            if gpio_test_mode:
                print('Pin %d on' % pin_array[n])
            else:
                self.__rlys_on([pin_array[n]])
            sleep(2.0)
        pins_reversed = list(reversed(pin_array))
        for n in range(len(pins_reversed)):
            if gpio_test_mode:
                print('Pin %d off' % pin_array[n])
            else:
                self.__rlys_off([pins_reversed[n]])
            sleep(2.0)
                
    #----------------------------------------------------
    def close(self):
        # Cleanup before exit
        if not gpio_test_mode:
            GPIO.cleanup()
    
    # =================================================================================
    # PRIVATE
    def __rlys_on(self, energise_pins):
        #           pin,invert
        # Form is: [[4, False], [17, False], [18, False]]
        for pin in energise_pins:
            if pin[1] : level = GPIO.LOW
            else: level = GPIO.HIGH
            GPIO.output(int(pin[0]), level)
    
    def __rlys_off(self, deenergise_pins): 
        #           pin,invert
        # Form is: [[4, False], [17, False], [18, False]]
        for pin in deenergise_pins:
            if pin[1] : level = GPIO.HIGH
            else: level = GPIO.LOW
            GPIO.output(int(pin[0]), level)
            
    def __all_off(self, all_pins):
        #           pin,invert
        # Form is: [[4, False], [17, False], [18, False]]
        for pin in all_pins:
            if pin[1] : level = GPIO.HIGH
            else: level = GPIO.LOW
            GPIO.output(int(pin[0]), level)
        