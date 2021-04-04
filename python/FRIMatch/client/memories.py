#!/usr/bin/env python3
#
# memories.py
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

# Applicaion imports
from imports import *

# ======================================================================================
# Memories window
class Memories(QMainWindow):
    
    def __init__(self, callback):
        
        super(Memories, self).__init__()
        
        self.__callback = callback
        
        # Assume tuner off-line
        self.__tuner_status = False
        
        # Set the back colour
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtGui.QColor(195,195,195,255))
        self.setPalette(palette)
        
        # Set the tooltip font
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setStyleSheet('''QToolTip { 
                           background-color: darkgray; 
                           color: black; 
                           border: #8ad4ff solid 1px
                           }''')
        
        # Initialise the GUI
        self.initUI()
    
    #========================================================================================    
    # UI initialisation and window event handlers
    def initUI(self):
        """ Configure the GUI interface """
        
        self.setToolTip('Memories')
        
        # Arrange window
        self.setGeometry(300,300,300,300)
                         
        self.setWindowTitle('Memories')
        
        #=======================================================
        # Set main layout
        w = QWidget()
        self.setCentralWidget(w)
        self.__grid = QGridLayout()
        w.setLayout(self.__grid)
        
        # Table area
        self.__table = QTableWidget()
        self.__table.setColumnCount(5)
        #self.__table.setRowCount(1)
        self.__table.setHorizontalHeaderLabels(('Name','Freq','Inductor','TX Cap','Ant Cap'))
        self.__grid.addWidget(self.__table,0,0)
    
    #========================================================================================
    # PUBLIC procs
    
    def show_window(self):
        # Show our window
        self.show()
        self.repaint()    