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
CAP_PINMAP ='CAP-PINMAP'
IND_PINMAP = 'IND-PINMAP'
IND_TOGGLE = 'IND_TOGGLE'
BAND = 'BAND'
STATE = 'STATE'

# UI
IDLE_TICKER = 100

# Configuration
CONFIG_PATH = '../config/auto_tuner.cfg'
g_pins = ['4','5','6','12','13','16','17','18','19','20','22','23','24','25','26','27']
g_cap_values = ('1000','2000','3000')
g_cap_extra_values = ('0','1000','2000','3000')
g_ind_values = ('1','2','3','4','5','6','7','8','9','10')
g_band_values = ('160','80','60','40','30','20','17','15','12','10')