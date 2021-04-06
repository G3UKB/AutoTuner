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
        RPi: {
            IP: get_ip(),
            RQST_PORT: 10002,
            EVNT_PORT: 10003,
        },
        SERVO: {
            TX_LOW_PWM: 1000,
            TX_HIGH_PWM: 1000,
            ANT_LOW_PWM: 1000,
            ANT_HIGH_PWM: 1000,
            MODE: MODE_TRACK,
            NUDGE_INC: DEFAULT_NUDGE_INC,
            TRACK_INC: DEFAULT_TRACK_INC,
            TRACK_DELAY: DEFAULT_TRACK_DELAY,
            SCAN_INC: DEFAULT_SCAN_INC,
            SCAN_DELAY: DEFAULT_SCAN_DELAY,
        },
        RELAY: {
            INDUCTOR_PINMAP: [16, 19, 20, 21],
            RELAY_INVERSE: False,
            LOW_RANGE: {
                FREQ: (1.8, 10.15),
                LABEL: '160m - 30m',
                ENERGISE: True,
            },
            HIGH_RANGE: {
                FREQ: (14.0, 30),
                LABEL: '20m - 10m',
                ENERGISE: False,
            }
        }
    },
    MEMORIES: [],
    STATE: {
        MAIN_WIN: [300,300,300,200],
        CONFIG_WIN: [300,300,300,300],
        MEM_WIN: [300,300,520,300]
    }
}

# Manage model
auto_tune_model_clone = None

def copy_model():
    global auto_tune_model
    global auto_tune_model_clone
    auto_tune_model_clone = copy.deepcopy(auto_tune_model)
    
def restore_model():
    global auto_tune_model
    global auto_tune_model_clone
    if auto_tune_model_clone != None:
        auto_tune_model = copy.deepcopy(auto_tune_model_clone)
