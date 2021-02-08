#!/usr/bin/env python3
#
# model.py
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

# Applicaion imports
from imports import *

# The application model contains persisted configuration and state data

# -----------------------------------------------------------
# IP helper
import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

auto_tune_model = {
    CONFIG: {
        RPi: {IP: get_ip(), RQST_PORT: 10002, EVNT_PORT: 10003},
        LOW_PWM: 500,
        HIGH_PWM: 1000,
        CAP_PINMAP: {1000: [4,], 2000: [4,17], 3000: [4,17,27]},
        IND_PINMAP: {1: 22, 2: 5, 3: 6, 4: 13, 5: 26, 6: 23, 7: 24, 8: 25, 9: 12, 10: 16},
        IND_TOGGLE: 20,
        BAND: {
            160: [0, 0, 1],
            80: [0, 0, 1],
            60: [0, 0, 1],
            40: [0, 0, 1],
            30: [0, 0, 1],
            20: [0, 0, 1],
            17: [0, 0, 1],
            12: [0, 0, 1],
            10: [0, 0, 1]
        }
    },
        STATE: {}
}
