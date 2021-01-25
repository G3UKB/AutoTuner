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
from PyQt5.QtWidgets import QInputDialog, QFrame, QGroupBox, QMessageBox, QLabel, QSlider, QLineEdit, QTextEdit, QComboBox, QPushButton, QCheckBox, QRadioButton, QSpinBox, QAction, QWidget, QGridLayout

CMD_PORT = 10002
SERVER_IP = '192.168.1.110'
IDLE_TICKER = 100

class TunerClient(QMainWindow):
    
    def __init__(self, qt_app):
        
        super(TunerClient, self).__init__()
        
        # Create a datagram socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind(('', 10002))
        self.__sock.settimeout(3)

        # The application
        self.__qt_app = qt_app
        
        # Track progress
        self.__progress = {'TX': 0, 'ANT': 0}
        
        # Macro store
        self.__macros = {}
        
        # Set the back colour
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtGui.QColor(195,195,195,255))
        self.setPalette(palette)

        # Initialise the GUI
        self.initUI()
        
        # Start monitor thread
        self.__monitor = Monitor(self.__sock, self.__monitor_callback)
        self.__monitor.start()
        
        # Start idle processing
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
    
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
        
        # Macro buttons
        self.__m0 = self.__m1 = self.__m2 = self.__m3 = self.__m4 = self.__m5 = None
        self.__m6 = self.__m7 = self.__m8 = self.__m9 = self.__m10 = self.__m11 = None
        self.__macrogrid = QGridLayout()
        w1 = QWidget()
        w1.setLayout(self.__macrogrid)
        self.__grid.addWidget(w1, 0,0)
        self.__macro_btns1 = [self.__m0,self.__m1,self.__m2,self.__m3,self.__m4,self.__m5]
        macro_procs1 = [self.__m0_proc,self.__m1_proc,self.__m2_proc,self.__m3_proc,self.__m4_proc,self.__m5_proc]
        index = 0
        for macro_btn in self.__macro_btns1:
            #macro_btn = QPushButton("Set")
            macro_btn = QComboBox()
            macro_btn.addItem("Set")
            #macro_btn.addItem("Run")
            self.__macrogrid.addWidget(macro_btn, 0,index)
            #macro_btn.clicked.connect(macro_procs1[index])
            macro_btn.activated[str].connect(macro_procs1[index])
            self.__macro_btns1[index] = macro_btn
            index += 1
        self.__macro_btns2 = [self.__m6,self.__m7,self.__m8,self.__m9,self.__m10,self.__m11]
        macro_procs2 = [self.__m6_proc,self.__m7_proc,self.__m8_proc,self.__m9_proc,self.__m10_proc,self.__m11_proc]
        index = 0
        for macro_btn in self.__macro_btns2:
            #macro_btn = QPushButton("Set")
            macro_btn = QComboBox()
            macro_btn.addItem("Set")
            #macro_btn.addItem("Run")
            self.__macrogrid.addWidget(macro_btn, 1,index)
            #macro_btn.clicked.connect(macro_procs2[index])
            macro_btn.activated[str].connect(macro_procs2[index])
            self.__macro_btns2[index] = macro_btn
            index += 1
        # Control area
        self.__ctrgrid = QGridLayout()
        w2 = QWidget()
        w2.setLayout(self.__ctrgrid)
        self.__grid.addWidget(w2, 1,0)
        
        # Top labels
        slider_tag = QLabel("Adjust")
        self.__ctrgrid.addWidget(slider_tag, 0,1)
        setpoint_tag = QLabel("Set")
        self.__ctrgrid.addWidget(setpoint_tag, 0,2)
        actual_tag = QLabel("Act")
        self.__ctrgrid.addWidget(actual_tag, 0,3)
        
        # Add sliders
        tx_lbl = QLabel("TX Cap")
        self.__ctrgrid.addWidget(tx_lbl, 1,0)
        self.__tx = QSlider(QtCore.Qt.Horizontal)
        self.__tx.setMinimum(0)
        self.__tx.setMaximum(180)
        self.__tx.setValue(0)
        self.__ctrgrid.addWidget(self.__tx, 1,1)
        self.__tx.valueChanged.connect(self.__tx_changed)
        self.__tx_val = QLabel("0")
        self.__tx_val.setMinimumWidth(30)
        self.__tx_val.setStyleSheet("color: green; font: 14px")
        self.__ctrgrid.addWidget(self.__tx_val, 1,2)
        self.__tx_actual = QLabel("0")
        self.__tx_actual.setMinimumWidth(30)
        self.__tx_actual.setStyleSheet("color: red; font: 14px")
        self.__ctrgrid.addWidget(self.__tx_actual, 1,3)
        
        ant_lbl = QLabel("Ant Cap")
        self.__ctrgrid.addWidget(ant_lbl, 2,0)
        self.__ant = QSlider(QtCore.Qt.Horizontal)
        self.__ant.setMinimum(0)
        self.__ant.setMaximum(180)
        self.__ant.setValue(0)
        self.__ctrgrid.addWidget(self.__ant, 2,1)
        self.__ant.valueChanged.connect(self.__ant_changed)
        self.__ant_val = QLabel("0")
        self.__ant_val.setMinimumWidth(30)
        self.__ant_val.setStyleSheet("color: green; font: 14px")
        self.__ctrgrid.addWidget(self.__ant_val, 2,2)
        self.__ant_actual = QLabel("0")
        self.__ant_actual.setMinimumWidth(30)
        self.__ant_actual.setStyleSheet("color: red; font: 14px")
        self.__ctrgrid.addWidget(self.__ant_actual, 2,3)
        
        # Add buttons
        self.__btngrid = QGridLayout()
        w3 = QWidget()
        w3.setLayout(self.__btngrid)
        self.__grid.addWidget(w3, 2,0)
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
        
        # Stop monitor
        self.__monitor.terminate()
        self.__monitor.join()
        
        # Close socket
        self.__sock.close()
    
    def __do_home(self):
        
        self.__sock.sendto(pickle.dumps(['CMD_HOME']), (SERVER_IP, CMD_PORT))
        self.__tx.setValue(0)
        self.__tx_val.setText('0')
        self.__ant.setValue(0)
        self.__ant_val.setText('0')
        
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
    
    #=======================================================
    # macro buttons
    def __m0_proc(self, action):
        self.__do_set_macro(0, action)
    def __m1_proc(self, action):
        self.__do_set_macro(1, action)
    def __m2_proc(self, action):
        self.__do_set_macro(2, action)
    def __m3_proc(self, action):
        self.__do_set_macro(3, action)
    def __m4_proc(self, action):
        self.__do_set_macro(4, action)
    def __m5_proc(self, action):
        self.__do_set_macro(5, action)
    def __m6_proc(self, action):
        self.__do_set_macro(6, action)
    def __m7_proc(self, action):
        self.__do_set_macro(7, action)
    def __m8_proc(self, action):
        self.__do_set_macro(8, action)
    def __m9_proc(self, action):
        self.__do_set_macro(9, action)
    def __m10_proc(self, action):
        self.__do_set_macro(10, action)
    def __m11_proc(self, action):
        self.__do_set_macro(11, action)
    
    def __do_set_macro(self, id, action):
        # Do we have a macro to run

        if id in self.__macros and action != 'Set':
            # Yup
            name, tx, ant = self.__macros[id]
            print(tx, ant)
            self.__tx.setValue(tx)
            self.__tx_changed()
            self.__ant.setValue(ant)
            self.__ant_changed()
        else:
            # No entry or update
            if id in self.__macros:
                del self.__macros[id]
            if id <=5:
                while self.__macro_btns1[id].count() > 0:
                    self.__macro_btns1[id].removeItem(0)
                self.__macro_btns1[id].addItem('Set')
            else:
                while self.__macro_btns2[id].count() > 0:
                    self.__macro_btns2[id].removeItem(0)
                self.__macro_btns2[id].addItem('Set')
            name, ok = QInputDialog.getText(self, "Configure Macro", "Name ")
            if ok and len(name) > 0:
                self.__macros[id] = [name, self.__tx.value(), self.__ant.value()]
                if id <=5:
                    self.__macro_btns1[id].addItem(name)
                else:
                    self.__macro_btns2[id].addItem(name)
        
    #======================================================= 
    def __monitor_callback(self, data):
        
        self.__progress = data
        
    #======================================================= 
    def __idleProcessing   (self):
        
        # Update UI with actual progress
        self.__tx_actual.setText(str(self.__progress['TX']))
        self.__ant_actual.setText(str(self.__progress['ANT']))
        # Set timer
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)

#======================================================================================================================
# Monitor thread
class Monitor(threading.Thread):
    
    def __init__(self, sock, callback):
        """
        Constructor
        
        Arguments:
            sock        -- socket to listen on
            callback    -- callback with data
        """
        
        super(Monitor, self).__init__()#
        
        self.__sock = sock
        self.__callback = callback
        self.__terminate = False
        
    def terminate(self):
        
        self.__terminate = True
        
    def run(self):
        
        while not self.__terminate:
            try:
                data, self.__address = self.__sock.recvfrom(100)
                self.__callback(pickle.loads(data))
            except socket.timeout:
                continue
            
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