#!/usr/bin/env python3
#
# tunerlib.py
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

# An embeddable API for setting a tuner memory

# System imports
import sys
import traceback
from time import sleep
import socket
import pickle

# Application imports
from defs import *
import model
import persist

"""
    The Tuner API class
"""
class Tuner_API:
    
    def __init__(self):
        # Retrieve model
        self.__model = persist.getSavedCfg(CONFIG_PATH)
        if self.__model == None:
            print ('Tuner configuration not found. Please run full tuner application to configure.')
            return
        
        # Create a datagram socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    #=======================================================
    # Run tuner to given memory
    def set_memory(self, memory_id):
        # Retrieve memory data
        if memory_id < len(self.__model[MEMORIES]):
            name, freq, inductor, tx_cap, ant_cap = self.__model[MEMORIES][memory_id]
        else:
            print("Invalid memory id: %d" % memory_id)
            return False
        
        # Retrieve inverse flag
        inv = self.__model[CONFIG][RELAY][RELAY_INVERSE]
        
        # Collect parameters for relays
        params = []
        for pin in self.__model[CONFIG][RELAY][INDUCTOR_PINMAP]:
            params.append((pin, inv))
        # Set relays
        self.__net_send([CMD_RELAYS_INIT, params])
        if inductor == 'low-range':
            self.__net_send([CMD_RELAYS_RESET, params])
        if inductor == 'high-range':
            self.__net_send([CMD_RELAYS_SET, params])
            
        # Set capacitors
        tx_cap = int(tx_cap)
        if tx_cap >= 0 and tx_cap <=180:
            self.__net_send([CMD_TX_SERVO_MOVE, [tx_cap]])
        ant_cap = int(ant_cap)
        if ant_cap >= 0 and ant_cap <=180:
            self.__net_send([CMD_ANT_SERVO_MOVE, [ant_cap]])
            
        print("Set memory %s at frequency %s" %(name, freq))

    #======================================================= 
    # Net send
    def __net_send(self, data):
        self.__sock.sendto(pickle.dumps(data), (self.__model[CONFIG][RPi][IP], self.__model[CONFIG][RPi][RQST_PORT]))
    
#======================================================================================================================
# Test code
def main():
    
    try:
        # Crete instance
        api = Tuner_API()
        # Run application loop
        for n in range(0, 11):
            api.set_memory(n)
            sleep(5)
       
    except Exception as e:
        print ('Exception [%s][%s]' % (str(e), traceback.format_exc()))
 
# Entry point       
if __name__ == '__main__':
    main()           