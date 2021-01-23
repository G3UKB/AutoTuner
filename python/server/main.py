#!/usr/bin/env python3
#
# main.py
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

# System imports
import os, sys
from time import sleep
import pickle
import subprocess

# Application imports
from defs import *
import netif
import device

"""
    Main program for the Remote Auto_Tuner.
"""

class RemoteTuner:
    
    def __init__(self):
        
        # Run the net interface as this is the active thread.
        self.__netif = netif.NetIF(self.__netCallback)
        self.__netif.start()
        
        # Create device
        self.__dev = device.Device()
        
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
            # Terminate the netif thread and wait for it to close
            self.__netif.terminate()
            self.__netif.join()
            
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
            type = cmd[0]
            if type == CMD_HOME:
                if len(cmd) != 1:
                    print('Command %s requires 0 parameters, received %d' % (type, len(request)-1))
                    return
                self.__dev.home()
            elif type == CMD_MOVE:
                if len(cmd) != 3:
                    print('Command %s requires 2 parameters, received %d' % (type, len(request)-1))
                    return
                self.__dev.move(cmd[1], cmd[2])
            elif type == CMD_RESET:
                if len(cmd) != 1:
                    print('Command %s requires 0 parameters, received %d' % (type, len(request)-1))
                    return
                # Restart the net interface
                self.__netif.terminate()
                self.__netif.join()
                sleep(1)
                self.__netif = netif.NetIF(self.__netCallback)
                self.__netif.start()
                # Restart the device
                self.__device.terminate()
                self.__dev = device.Device()
            else:
                print('Unknown request type %s!' % (type))
            
        except pickle.UnpicklingError:
            print('Failed to unpickle request data!')

# ===========================================================================                
# Entry point            
if __name__ == '__main__':
    main = RemoteTuner()
    main.mainLoop()        
    