#!/usr/bin/env python3
#
# defs.py
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

# Model defs
CONFIG = 'CONFIG'
RPi = 'RPi'
IP = 'IP'
RQST_PORT = 'RQST_PORT'
EVNT_PORT = 'EVNT_PORT'
LOW_PWM = 'LOW-PWM'
HIGH_PWM = 'HIGH-PWM'
INDUCTOR_PINMAP = 'IND-PINMAP'
RELAY_INVERSE = 'RELAY_INVERSE'
LOW_RANGE = 'LOW_RANGE'
HIGH_RANGE = 'HIGH_RANGE'
FREQ = 'FREQ'
LABEL = 'LABEL'
ENERGISE = 'ENERGISE'
STATE = 'STATE'

# UI
IDLE_TICKER = 100

# Configuration
CONFIG_PATH = '../config/auto_tuner.cfg'
g_pins = ['16','19','20','21']
g_ind_values = ['1','2','3','4']
