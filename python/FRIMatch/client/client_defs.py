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

#=======================================================================
# Model defs
CONFIG = 'CONFIG'
MEMORIES = 'MEMORIES'
# RPi section
RPi = 'RPi'
IP = 'IP'
RQST_PORT = 'RQST-PORT'
EVNT_PORT = 'EVNT-PORT'
# Servo section
SERVO = 'SERVO'
MODE = 'MODE'
TX_LOW_PWM = 'TX-LOW-PWM'
TX_HIGH_PWM = 'TX-HIGH-PWM'
ANT_LOW_PWM = 'ANT-LOW-PWM'
ANT_HIGH_PWM = 'ANT-HIGH-PWM'
MODE: 'MODE'
NUDGE_INC = 'NUDGE_INC'
TRACK_INC = 'TRACK_INC'
TRACK_DELAY = 'TRACK_DELAY'
SCAN_INC = 'SCAN_INC'
SCAN_DELAY = 'SCAN_DELAY'
# Relay section
RELAY = 'RELAY'
INDUCTOR_PINMAP = 'IND-PINMAP'
RELAY_INVERSE = 'RELAY_INVERSE'
LOW_RANGE = 'LOW-RANGE'
HIGH_RANGE = 'HIGH-RANGE'
FREQ = 'FREQ'
LABEL = 'LABEL'
ENERGISE = 'ENERGISE'
# Values and defaults
MODE_TRACK = 'MODE_TRACK'
MODE_SCAN = 'MODE_SCAN'
DEFAULT_NUDGE_INC = 2
DEFAULT_TRACK_INC = 1
DEFAULT_TRACK_DELAY = 20    # ms
DEFAULT_SCAN_INC = 1
DEFAULT_SCAN_DELAY = 20     # ms

#=======================================================================
# UI
CONFIG_PATH = '../config/auto_tuner.cfg'
IDLE_TICKER = 100
HEARTBEAT_TIMER = 10 # 10 * IDLE_TICKER = 1s ; heartbeats should be every 0.5s

# To populate relay dropdowns
g_pins = ['4','17','18','27','22','23','24','25','6','12','13','16','19','20','21']
g_ind_values = ['1','2','3','4']


