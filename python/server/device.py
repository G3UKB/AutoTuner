#!/usr/bin/env python3
#
# device.py
# 
# Copyright (C) 2017 by G3UKB Bob Cowdery
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
----------------------------------------------------------------------
 Controls the remote auto-tuner servos. There are only two controls for dual gang
 capacitors. The inductor is fixed.
 
    Servo motors:   Any 180 degree, model control servos, metal gears.
    Controller:     Adafruit 16-Channel 12-bit PWM/Servo Driver - I2C interface - PCA9685
 
 Note, you can't slow down a servo, they will go full pelt so the strategy is to move
 incrementally with a delay. With small increments this can appear smooth.
----------------------------------------------------------------------
"""

# System imports
from time import sleep

# Application imports
from defs import *

# Import the Adafruit libs
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

"""
Device class implements low level servo interface
"""
class Device:
    
    def __init__(self):
        """
        Constructor
        
        Arguments:
        
        """
        
        # Initialise the library
        i2c_bus = busio.I2C(SCL, SDA)
        self.__dev = PCA9685(i2c_bus)
        
        # Tweek for the correct range
        self.__servo_min = 600
        self.__servo_max = 2000
        
        # Home is minimum capacitance
        self.__home = self.__servo_min
        # Increment per degree 
        self.__value_per_degree = (self.__servo_max - self.__servo_min) / RANGE
        
        # Best for servos
        self.__dev.frequency = 60
        self.__dev.channels[0].duty_cycle = 0x7FFF
        self.__dev.channels[1].duty_cycle = 0x7FFF
        
        # Create the servo instances.
        self.__tx_tune_servo = servo.Servo(self.__dev.channels[0],min_pulse=self.__servo_min, max_pulse=self.__servo_max)
        self.__ant_tune_servo = servo.Servo(self.__dev.channels[1],min_pulse=self.__servo_min, max_pulse=self.__servo_max)
    
        # Send home
        self.__home()
        
    def terminate(self):
        
        software_reset()
        self.__dev = None
        
    #------------------------------------------------------------------
    # PUBLIC
    def home(self):
        """
        Move servos to the home position.
        
        Arguments:
        
        """
        
        # Send home
        self.__tx_tune_servo.angle = 0
        self.__ant_tune_servo.angle = 0
        self.__tx_last_angle = 0
        self.__ant_last_angle = 0
        
    def move(self, ch, angle):
        """
        Move tx-servo or ant-servo to the given position.
        
        Arguments:
        ch      --  TX_TUNE or ANT_TUNE
        angle   --  degrees to move to (0 - 180)

        """
        
        for next_angle in range(self.__tx_last_angle, angle):
            if ch == TX_TUNE:
                self.__tx_tune_servo.angle = next_angle
                self.__tx_last_angle = next_angle
            elif ch == ANT_TUNE:
                self.__ant_tune_servo.angle = next_angle
                self.__ant_last_angle = next_angle
            sleep(0.01)

#------------------------------------------------------------------
# Test Entry point            
if __name__ == '__main__':
    dev = Device()
    dev.home()
    dev.move(0,90)
    dev.move(1,90)
    sleep(3)
    dev.move(0,180)
    dev.move(1,180)
    sleep(3)
    dev.move(0,0)
    dev.move(1,0)
    
