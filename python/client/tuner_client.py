#!/usr/bin/env python3
#
# tuner_client.py
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

import os, sys
import threading
import socket
import pickle
import platform
import subprocess
import traceback
from time import sleep

# PyQt5 imports
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QFont
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFrame, QGroupBox, QMessageBox, QLabel, QSlider, QLineEdit, QTextEdit, QComboBox, QPushButton, QCheckBox, QRadioButton, QSpinBox, QAction, QWidget, QGridLayout

CMD_PORT = 10002
SERVER_IP = '192.168.1.110'

class TunerClient(QMainWindow):
    
    def __init__(self, qt_app):
        
        super(TunerClient, self).__init__()
        
        # Create a datagram socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # The application
        self.__qt_app = qt_app
        
        # Set the back colour
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtGui.QColor(195,195,195,255))
        self.setPalette(palette)

        # Initialise the GUI
        self.initUI()
    
    #========================================================================================    
    # UI initialisation and window event handlers
    def initUI(self):
        """ Configure the GUI interface """
        
        self.setToolTip('Remote Auto-Tuner')
        
        # Arrange window
        self.setGeometry(300,300,300,200)
                         
        self.setWindowTitle('Remote Auto-Tuner')
        
        #=======================================================
        # Set main layout
        w = QWidget()
        self.setCentralWidget(w)
        self.__grid = QGridLayout()
        w.setLayout(self.__grid)
        
        # Add sliders
        tx_lbl = QLabel("TX Cap")
        self.__grid.addWidget(tx_lbl, 0,0)
        self.__tx = QSlider(QtCore.Qt.Horizontal)
        self.__tx.setMinimum(0)
        self.__tx.setMaximum(180)
        self.__tx.setValue(0)
        self.__grid.addWidget(self.__tx, 0,1)
        self.__tx.valueChanged.connect(self.__tx_changed)
        self.__tx_val = QLabel("0")
        self.__tx_val.setMinimumWidth(30)
        self.__tx_val.setStyleSheet("color: green; font: 14px")
        self.__grid.addWidget(self.__tx_val, 0,2)
        
        ant_lbl = QLabel("Ant Cap")
        self.__grid.addWidget(ant_lbl, 1,0)
        self.__ant = QSlider(QtCore.Qt.Horizontal)
        self.__ant.setMinimum(0)
        self.__ant.setMaximum(180)
        self.__ant.setValue(0)
        self.__grid.addWidget(self.__ant, 1,1)
        self.__ant.valueChanged.connect(self.__ant_changed)
        self.__ant_val = QLabel("0")
        self.__ant_val.setMinimumWidth(30)
        self.__ant_val.setStyleSheet("color: green; font: 14px")
        self.__grid.addWidget(self.__ant_val, 1,2)
        
        # Add buttons
        self.__btngrid = QGridLayout()
        w1 = QWidget()
        w1.setLayout(self.__btngrid)
        self.__grid.addWidget(w1, 2,0,1,2)
        self.__home = QPushButton("Home")
        self.__btngrid.addWidget(self.__home, 0,0)
        self.__home.clicked.connect(self.__do_home)
        self.__reset = QPushButton("Reset")
        self.__btngrid.addWidget(self.__reset, 0,1)
        self.__reset.clicked.connect(self.__do_reset)
        self.__exit = QPushButton("Exit")
        self.__btngrid.addWidget(self.__exit, 0,2)
        self.__exit.clicked.connect(self.__do_exit)
        
    #========================================================================================
    # Run application
    def run(self, ):
        """ Run the application """
        
        # Start idle processing
        #QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
        
        # Returns when application exits
        # Show the GUI
        self.show()
        self.repaint()
        
        
        # Enter event loop
        return self.__qt_app.exec_()    
    
    #=======================================================
    # Window events
    def closeEvent(self, event):

        self.__close()
    
    def __close(self):
        # close socket
        self.__sock.close()
    
    def __do_home(self):
        self.__sock.sendto(pickle.dumps(['CMD_HOME']), (SERVER_IP, CMD_PORT))
    
    def __do_reset(self):
        self.__sock.sendto(pickle.dumps(['CMD_RESET']), (SERVER_IP, CMD_PORT))

    def __do_exit(self):
        self.__close()
        sys.exit()
        
    #=======================================================
    # Track TX Tuning
    def __tx_changed(self):
    
        # Value ranges 0 - 180
        val = self.__tx.value()
        self.__sock.sendto(pickle.dumps(['CMD_MOVE', 0, val]), (SERVER_IP, CMD_PORT))
        self.__tx_val.setText(str(val))
        
    #=======================================================
    # Track Ant Tuning
    def __ant_changed(self):
    
        # Value ranges 0 - 180
        val = self.__ant.value()
        self.__sock.sendto(pickle.dumps(['CMD_MOVE', 1, val]), (SERVER_IP, CMD_PORT))
        self.__ant_val.setText(str(val))
        
#======================================================================================================================
# Main code
def main():
    
    try:
        # The one and only QApplication 
        qt_app = QApplication(sys.argv)
        # Crete instance
        client = TunerClient(qt_app)
        # Run application loop
        sys.exit(client.run())
       
    except Exception as e:
        print ('Exception [%s][%s]' % (str(e), traceback.format_exc()))
 
# Entry point       
if __name__ == '__main__':
    main()