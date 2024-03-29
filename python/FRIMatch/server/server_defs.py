#!/usr/bin/env python3
#
# defs.py
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

# Command types
# External servo specific commands
CMD_WAKEUP = 'CMD_WAKEUP'
CMD_TX_SERVO_SET_PWM = 'CMD_TX_SERVO_SET_PWM'
CMD_TX_SERVO_TEST = 'CMD_TX_SERVO_TEST'
CMD_TX_SERVO_HOME = 'CMD_TX_SERVO_HOME'
CMD_TX_SERVO_MOVE = 'CMD_TX_SERVO_MOVE'
CMD_ANT_SERVO_SET_PWM = 'CMD_ANT_SERVO_SET_PWM'
CMD_ANT_SERVO_TEST = 'CMD_ANT_SERVO_TEST'
CMD_ANT_SERVO_HOME = 'CMD_ANT_SERVO_HOME'
CMD_ANT_SERVO_MOVE = 'CMD_ANT_SERVO_MOVE'
# External servo general settings
CMD_SERVO_SETTINGS = 'CMD_SERVO_SETTINGS'

# Internal servo commands
CMD_SERVO_TEST = 'CMD_SERVO_TEST'
CMD_SERVO_HOME = 'CMD_SERVO_HOME'
CMD_SERVO_MOVE = 'CMD_SERVO_MOVE'

# External relay commands
CMD_RELAYS_INIT = 'CMD_RELAYS_INIT'
CMD_RELAYS_SET = 'CMD_RELAYS_SET'
CMD_RELAYS_RESET = 'CMD_RELAYS_RESET'
CMD_RELAYS_CYCLE = 'CMD_RELAYS_CYCLE'

CMD_RESET = 'CMD_RESET'

