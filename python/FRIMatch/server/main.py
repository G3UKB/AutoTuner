#!/usr/bin/env python3
#
# main.py
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
import pickle
import subprocess

# Application imports
from server_defs import *
import netif
import servo
import relays

"""
    Main program for the Remote Auto_Tuner.
"""

class RemoteTuner:
    
    def __init__(self):
            
        # Run the net interface as this is the active thread.
        self.__netif = netif.NetIF(self.__netCallback)
        self.__netif.start()
        
        # Create servos
        self.__tx_servo = servo.Servo(0, self.__TxServoCallback)
        self.__tx_servo.start()
        self.__ant_servo = servo.Servo(1, self.__AntServoCallback)
        self.__ant_servo.start()
        
        # Create relays
        self.__relays = relays.Relays()
        self.__relays.init()
        
    #------------------------------------------------------------------    
    def mainLoop(self):
        """
        Wait for termination
        
        """
        
        print('Remote Auto-Tuner server running ...')
        try:
            # Main loop for ever
            while True:
                sleep(1)                
                
        except KeyboardInterrupt:
            
            # User requested exit
            
            # Cleanup GPIO
            self.__relays.close()
            
            # Terminate the netif and servo threads and wait for thread exit
            self.__netif.terminate()
            self.__netif.join()
            self.__tx_servo.terminate()
            self.__tx_servo.join()
            self.__ant_servo.terminate()
            self.__ant_servo.join()
            
            print('Interrupt - exiting...')
    
    #------------------------------------------------------------------        
    def __netCallback(self, data):
        
        """
        Callback from net interface
        
        Arguments:
            data    -- the command data
        """
        
        # Data arrived from caller
        try:
            cmd = pickle.loads(data)
            # Command is an array of type followed by one or more parameters
            rqst = cmd[0]
            if rqst == CMD_TX_SERVO_SET_PWM:
                if len(cmd[1]) != 2:
                    print('Command %s requires 2 parameters, received %d' % (rqst, len(cmd[1])))
                    return
                self.__tx_servo.set_pwm_range(cmd[1][0], cmd[1][1])
                
            elif rqst == CMD_TX_SERVO_TEST:
                if len(cmd[1]) != 0:
                    print('Command %s requires 0 parameters, received %d' % (rqst, len(cmd[1])))
                    return
                self.__tx_servo.test_range()
                
            elif rqst == CMD_TX_SERVO_HOME:
                if len(cmd[1]) != 0:
                    print('Command %s requires 0 parameters, received %d' % (rqst, len(cmd[1])))
                    return
                self.__tx_servo.post((CMD_SERVO_HOME, ()))
                
            elif rqst == CMD_TX_SERVO_MOVE:
                if len(cmd[1]) != 1:
                    print('Command %s requires 1 parameters, received %d' % (rqst, len(cmd[1])))
                    return
                self.__ant_servo.post((CMD_SERVO_MOVE, (cmd[1][0])))
            
            elif rqst == CMD_ANT_SERVO_SET_PWM:
                if len(cmd[1]) != 2:
                    print('Command %s requires 2 parameters, received %d' % (rqst, len(cmd[1])))
                    return
                self.__ant_servo.set_pwm_range(cmd[1][0], cmd[1][1])
                
            elif rqst == CMD_ANT_SERVO_TEST:
                if len(cmd[1]) != 0:
                    print('Command %s requires 0 parameters, received %d' % (rqst, len(cmd[1])))
                    return
                self.__ant_servo.test_range()
                
            elif rqst == CMD_ANT_SERVO_HOME:
                if len(cmd[1]) != 0:
                    print('Command %s requires 0 parameters, received %d' % (rqst, len(cmd[1])))
                    return
                self.__ant_servo.post((CMD_SERVO_HOME, ()))
                
            elif rqst == CMD_ANT_SERVO_MOVE:
                if len(cmd[1]) != 1:
                    print('Command %s requires 1 parameters, received %d' % (rqst, len(cmd[1])))
                    return
                self.__ant_servo.post((CMD_SERVO_MOVE, (cmd[1][0])))
                
            elif rqst == CMD_RELAYS_INIT:
                if len(cmd[1]) == 0:
                    print('Command %s requires variable parameter list, received %d' % (rqst, len(cmd[1])))
                    return
                self.__relays.init_pins(cmd[1])
            
            elif rqst == CMD_RELAYS_SET:
                if len(cmd[1]) == 0:
                    print('Command %s requires variable parameter list, received %d' % (rqst, len(cmd[1])))
                    return
                self.__relays.set_pins(cmd[1])
            
            elif rqst == CMD_RELAYS_CYCLE:
                if len(cmd[1]) == 0:
                    print('Command %s requires variable parameter list, received %d' % (rqst, len(cmd[1])))
                    return
                self.__relays.cycle_pins(cmd[1][0], cmd[1][1])
                
            elif rqst == CMD_RESET:
                if len(cmd[1]) != 0:
                    print('Command %s requires 0 parameters, received %d' % (rqst, len(cmd[1])))
                    return
                # Restart the net interface
                self.__netif.terminate()
                self.__netif.join()
                sleep(1)
                self.__netif = netif.NetIF(self.__netCallback)
                self.__netif.start()
                # Restart the servo
                self.__device.terminate()
                self.__servo = servo.Device()
                self.__relays.close()
                self.__relays = relay.Relay()
            else:
                print('Unknown request type %s!' % (rqst))
            
        except pickle.UnpicklingError:
            print('Failed to unpickle request data!')

    #------------------------------------------------------------------        
    def __TxServoCallback(self, data):
        
        """
        Callback from servo interface for progress reports
        
        Arguments:
            data    -- the progress data
        """
        
        self.__netif.do_tx_progress(data) 
    
    def __AntServoCallback(self, data):
        
        """
        Callback from servo interface for progress reports
        
        Arguments:
            data    -- the progress data
        """
        
        self.__netif.do_ant_progress(data)
        
# ===========================================================================                
# Entry point            
if __name__ == '__main__':
    main = RemoteTuner()
    main.mainLoop()        
    