#!/usr/bin/env python3
#
# netif.py
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

import os, sys
import threading
import socket
import pickle

from server_defs import *

# Net interface
RQST_IP = ''
RQST_PORT = 10002
EVNT_PORT = 10003

"""
Interface to the Remote Auto-Tuner client application:
"""

class NetIF(threading.Thread):
    
    def __init__(self, callback):
        """
        Constructor
        
        Arguments:
            callback    --  callback here when data arrives
            
        """

        super(NetIF, self).__init__()
        self.__callback = callback
        
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((RQST_IP, RQST_PORT))
        self.__sock.settimeout(3)
        
        self.__address = None
        self.__terminate = False
    
    def terminate(self):
        """ Terminate thread """
        
        self.__terminate = True
    
    def do_heartbeat(self):
        """
        Send a heartbeat
        
        Arguments:
           
        """
        
        if self.__address != None:
            try:
                pickledData = pickle.dumps(('heartbeat', ()))
                self.__sock.sendto(pickledData, (self.__address[0], EVNT_PORT))
                
            except Exception as e:
                print('Exception on heartbeat send %s' % (str(e)))

    def do_tx_progress(self, data):
        """
        Send progress data
        
        Arguments:
            data    --  opaque data to send
        
        """
        
        if self.__address != None:
            try:
                pickledData = pickle.dumps(('tx', data))
                self.__sock.sendto(pickledData, (self.__address[0], EVNT_PORT))
                
            except Exception as e:
                print('Exception on tx progress send %s' % (str(e)))
    
    def do_ant_progress(self, data):
        """
        Send progress data
        
        Arguments:
            data    --  opaque data to send
        
        """
        
        if self.__address != None:
            try:
                pickledData = pickle.dumps(('ant', data))
                self.__sock.sendto(pickledData, (self.__address[0], EVNT_PORT))
                
            except Exception as e:
                print('Exception on antenna progress send %s' % (str(e)))

    def run(self):
        """ Listen for requests """
        
        while not self.__terminate:
            try:
                data, self.__address = self.__sock.recvfrom(512)
                self.__callback(data)
            except socket.timeout:
                continue
            