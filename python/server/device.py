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
class Device(threading.Thread):
    
    def __init__(self, callback):
        """
        Constructor
        
        Arguments:
            callback    -- callback here with progress
            
        """
        
        super(Device, self).__init__()
        
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
        
        # Create the servo instances.
        self.__tx_tune_servo = servo.Servo(self.__dev.channels[0],min_pulse=self.__servo_min, max_pulse=self.__servo_max)
        self.__ant_tune_servo = servo.Servo(self.__dev.channels[1],min_pulse=self.__servo_min, max_pulse=self.__servo_max)
    
        # Send home
        self.__q.append((CMD_HOME, ()))
    
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
            while len(self.__q) > 1:
                cmd, params = self.__q.popleft()
                if cmd == CMD_HOME:
                    self.__home()
            if len(self.__q) > 0:
                cmd, params = self.__q.popleft()
                if cmd == CMD_HOME:
                    self.__home()
                elif cmd == CMD_MOVE:
                    ch, angle = params
                    self.__move(ch, angle)
            
    def __home(self):
        """
        Move servos to the home position.
        
        Arguments:
        
        """
        
        # Send home
        self.__tx_tune_servo.angle = 0
        self.__ant_tune_servo.angle = 0
        self.__tx_last_angle = 0
        self.__ant_last_angle = 0
        self.__callback({'TX': 0, 'ANT': 0})
        
    def __move(self, ch, angle):
        """
        Move tx-servo or ant-servo to the given position.
        
        Arguments:
        ch      --  TX_TUNE or ANT_TUNE
        angle   --  degrees to move to (0 - 180)

        """
        
        if ch == TX_TUNE:
            if angle > self.__tx_last_angle:
                step = 1
            else:
                step = -1
            for next_angle in range(self.__tx_last_angle, angle, step):
                self.__tx_tune_servo.angle = next_angle
                self.__tx_last_angle = next_angle
                self.__callback({'TX': next_angle, 'ANT': self.__ant_last_angle})
                sleep(0.03)
        elif ch == ANT_TUNE:
            if angle > self.__ant_last_angle:
                step = 1
            else:
                step = -1
            for next_angle in range(self.__ant_last_angle, angle, step):
                self.__ant_tune_servo.angle = next_angle
                self.__ant_last_angle = next_angle
                self.__callback({'TX': self.__tx_last_angle, 'ANT': next_angle})
                sleep(0.03)

#------------------------------------------------------------------
# Test Entry point            
if __name__ == '__main__':
    dev = Device()
    print('Moving home')
    dev.home()
    print('Move TX - 90')
    dev.move(0,90)
    sleep(1)
    print('Move ANT - 90')
    dev.move(1,90)
    sleep(3)
    print('Move TX - 180')
    dev.move(0,180)
    sleep(1)
    print('Move ANT - 180')
    dev.move(1,180)
    sleep(3)
    print('Move TX - 0')
    dev.move(0,0)
    sleep(1)
    print('Move ANT - 0')
    dev.move(1,0)
    
