#!/usr/bin/env python3
#
# servo.py
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
----------------------------------------------------------------------
 Controls the remote auto-tuner servo.
 There is one variable capacitor for the L-Match controlled by a servo.
 
    Servo motor:   Any 180 degree, model control servos, metal gears.
    Controller:     Adafruit 16-Channel 12-bit PWM/Servo Driver - I2C interface - PCA9685
 
 Note, you can't slow down a servo, they will go full pelt so the strategy is to move
 incrementally with a delay. With small increments this can appear smooth.
----------------------------------------------------------------------
"""

# System imports
import threading
from collections import deque
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
class Servo(threading.Thread):
    
    def __init__(self, callback):
        """
        Constructor
        
        Arguments:
            callback    -- callback here with progress
            
        """
        
        super(Servo, self).__init__()
        
        self.__callback = callback
        
        # Initialise the library
        i2c_bus = busio.I2C(SCL, SDA)
        self.__dev = PCA9685(i2c_bus)
        
        # Flags
        self.__terminate = False
        
        # Queue to post on
        self.__q = deque()
        
        # Tweek for the correct range
        self.__servo_min = 600
        self.__servo_max = 2000
        
        # Best for servos
        self.__dev.frequency = 60
        self.__dev.channels[0].duty_cycle = 0x7FFF
        self.__dev.channels[1].duty_cycle = 0x7FFF
        
        # Create the servo instance.
        self.__servo = servo.Servo(self.__dev.channels[0],min_pulse=self.__servo_min, max_pulse=self.__servo_max)
        
        # Send home
        self.__q.append((CMD_SERVO, (0)))
    
    #------------------------------------------------------------------
    # PUBLIC
    
    def terminate(self):
        
        self.__terminate = True
        self.__dev = None
    
    def post(self, cmd):
        
        self.__q.append(cmd)
        
    #------------------------------------------------------------------
    # PRIVATE
    
    def run(self):
        
        while not self.__terminate:
            home, angle = self.__rationalise()
            if home != None:
               self.__home()
            if angle != None:
                self.__move(angle)
    
    def __rationalise(self):
        """
        Rationalise the commands to HOME and MOVE
        such that we pick up one home if present and the last move
        
        Arguments:
        
        """
        home = None
        angle = None
        
        while len(self.__q) > 0:
            cmd, params = self.__q.popleft()
            if cmd == CMD_SERVO_HOME:
                home = params
            elif cmd == CMD_SERVO_MOVE:
                angle = params
        return home, angle
               
    def __home(self):
        """
        Move servos to the home position.
        
        Arguments:
        
        """
        
        # Send home
        self.__servo.angle = 0
        self.__last_angle = 0
        self.__callback(0)
        
    def __move(self, angle):
        """
        Move servo to the given position.
        
        Arguments:
        angle   --  degrees to move to (0 - 180)

        """
        
        if angle > self.__last_angle:
            step = 1
        else:
            step = -1
        for next_angle in range(self.__last_angle, angle, step):
            self.__servo.angle = next_angle
            self.__last_angle = next_angle
            self.__callback(next_angle)
            sleep(0.02)
        self.__last_angle = angle
        self.__callback(angle)

    