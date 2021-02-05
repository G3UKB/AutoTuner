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

# Applicaion imports
from imports import *

#======================================================================================
# Main application window
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
        self.__progress = 0
        self.__actual = 0
        
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
            
        # Control area
        self.__ctrgrid = QGridLayout()
        w1 = QWidget()
        w1.setLayout(self.__ctrgrid)
        self.__grid.addWidget(w1, 1,0)
        
        # Band
        band_lbl = QLabel("Band")
        self.__cb_band = QComboBox()
        self.__cb_band.addItems(g_cap_values)
        self.__ctrgrid.addWidget(band_lbl, 0,0)
        self.__ctrgrid.addWidget(self.__cb_band, 0,1)
        self.__set_band = QPushButton("Set")
        self.__ctrgrid.addWidget(self.__set_band, 0,2)
        self.__set_band.clicked.connect(self.__do_set_band)
        
        # Slider labels
        slider_tag = QLabel("Adjust")
        self.__ctrgrid.addWidget(slider_tag, 0,1)
        setpoint_tag = QLabel("Set")
        self.__ctrgrid.addWidget(setpoint_tag, 0,2)
        actual_tag = QLabel("Act")
        self.__ctrgrid.addWidget(actual_tag, 0,3)
        
        # Add sliders
        cap_lbl = QLabel("Variable Cap")
        self.__ctrgrid.addWidget(cap_lbl, 1,0)
        self.__cap = QSlider(QtCore.Qt.Horizontal)
        self.__cap.setMinimum(0)
        self.__cap.setMaximum(180)
        self.__cap.setValue(0)
        self.__ctrgrid.addWidget(self.__cap, 1,1)
        self.__cap.valueChanged.connect(self.__cap_changed)
        self.__cap_val = QLabel("0")
        self.__cap_val.setMinimumWidth(30)
        self.__cap_val.setStyleSheet("color: green; font: 14px")
        self.__ctrgrid.addWidget(self.__cap_val, 1,2)
        self.__cap_actual = QLabel("0")
        self.__cap_actual.setMinimumWidth(30)
        self.__cap_actual.setStyleSheet("color: red; font: 14px")
        self.__ctrgrid.addWidget(self.__cap_actual, 1,3)
        
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
    # Set server to new capacitor degrees
    def __cap_changed(self):
    
        # Value ranges 0 - 180
        val = self.__cap.value()
        self.__sock.sendto(pickle.dumps(['CMD_MOVE', 0, val]), (SERVER_IP, CMD_PORT))
        self.__cap.setText(str(val))
    
    #=======================================================
    # Set server to band paramters
    def __do_set_band(self):
        pass
       
    #======================================================= 
    def __monitor_callback(self, data):
        
        self.__progress = data
        
    #======================================================= 
    def __idleProcessing   (self):
        
        # Update UI with actual progress
        self.__cap_actual.setText(str(self.__progress))
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