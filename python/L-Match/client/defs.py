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

# Network
CMD_PORT = 10002
SERVER_IP = '192.168.1.110'

# UI
IDLE_TICKER = 100

# Configuration
CONFIG_PATH = '../config/auto_tuner.cfg'
g_pins = ['4','17','27','22','5','13','26','23','24','25','12','16']
g_cap_values = ('1000','2000','3000')
g_cap_extra_values = ('0','1000','2000','3000')
g_ind_values = ('1','2','3','4','5','6','7','8','9','10')
g_band_values = ('160','80','60','40','30','20','17','15','12','10')