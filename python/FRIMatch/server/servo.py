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
 
    Servo motor:   Any 180 degree capable, model control servos.
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
from server_defs import *

# Import the Adafruit libs
servo_test_mode = False
try:
    from adafruit_servokit import ServoKit
except ModuleNotFoundError:
    print("Servo - not running on RPi, using test mode!")
    servo_test_mode = True

"""
Device class implements low level servo interface
"""
class Servo(threading.Thread):
    
    def __init__(self, id, callback):
        """
        Constructor
        
        Arguments:
            callback    -- callback here with progress
            
        """
        
        super(Servo, self).__init__()
        
        self.__id = id
        self.__callback = callback
        
        # Flags
        self.__terminate = False
        
        # Queue to post on
        self.__q = deque()
        
        # Set the default range
        self.__servo_min = 600
        self.__servo_max = 2000
        self.__last_angle = 0
        
        # Best for servos
        if not servo_test_mode:
            self.__kit = ServoKit(channels=16)
    
    #------------------------------------------------------------------
    # PUBLIC
    
    def terminate(self):
        
        self.__terminate = True
        self.__dev = None
    
    def settings(self, track_inc, track_delay, scan_inc, scan_delay):
        
        self.__track_inc = int(track_inc)
        self.__track_delay = int(track_delay)
        self.__scan_inc = int(scan_inc)
        self.__scan_delay = int(scan_delay)
        
        
    def set_pwm_range(self, low, high):
        self.__servo_min = low
        self.__servo_max = high
        if servo_test_mode:
            print ("Setting min,max to: %d, %d" % (low,high))
        else:
            # Create instance
            self.__kit.servo[self.__id].set_pulse_width_range(low,high)
    
    def test_range(self):
        self.__q.append((CMD_SERVO_TEST, ()))
        
    def post(self, cmd):
        self.__q.append(cmd)
        
    #------------------------------------------------------------------
    # PRIVATE
    
    def run(self):
        
        while not self.__terminate:
            home, angle, test = self.__rationalise()
            if home != None:
               self.__home()
            if angle != None:
                self.__move(angle)
            if test != None:
                self.__test()
            sleep(0.1)
    
    def __rationalise(self):
        """
        Rationalise the commands to HOME and MOVE
        such that we pick up one home if present and the last move
        
        Arguments:
        
        """
        home = None
        angle = None
        test = None
        
        while len(self.__q) > 0:
            cmd, params = self.__q.popleft()
            if cmd == CMD_SERVO_HOME:
                home = params
            elif cmd == CMD_SERVO_MOVE:
                angle = params
            elif cmd == CMD_SERVO_TEST:
                test = params
        return home, angle, test
               
    def __home(self):
        """
        Move servos to the home position.
        
        Arguments:
        
        """
        
        # Send home
        if servo_test_mode:
            print("Servo home")
        else:
            self.__kit.servo[self.__id].angle = 0
            self.__last_angle = 0
        self.__callback(0)
        
    def __move(self, angle):
        """
        Move servo to the given position.
        
        Arguments:
        angle   --  degrees to move to (0 - 180)

        """
        
        if servo_test_mode:
            print('Servo move to %d' % angle)
        if angle > self.__last_angle:
            step = 1
        else:
            step = -1
        for next_angle in range(self.__last_angle, angle, step):
            if not servo_test_mode:  
                self.__kit.servo[self.__id].angle = next_angle
            self.__last_angle = next_angle
            self.__callback(next_angle)
            sleep(0.02)
        self.__last_angle = angle
        self.__callback(angle)

    
    def __test(self):
        self.__move(0)
        sleep(2)
        self.__move(180)