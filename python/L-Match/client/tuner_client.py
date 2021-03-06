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
        
        # Manage configuration
        self.__configured = True
        app_config = persist.getSavedCfg(CONFIG_PATH)
        if app_config == None:
            print ('Configuration not found, using defaults')
            persist.saveCfg(CONFIG_PATH, model.auto_tune_model)
            self.__configured = False
        else:
            # Use persisted version
            model.auto_tune_model = app_config   
        # Create a datagram socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind(('', model.auto_tune_model[CONFIG][RPi][EVNT_PORT]))
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

        # Set the tooltip style
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setStyleSheet('''QToolTip { 
                           background-color: darkgray; 
                           color: black; 
                           border: #8ad4ff solid 1px
                           }''')
        
        # Initialise the GUI
        self.initUI()
        
        # Start monitor thread
        self.__monitor = Monitor(self.__sock, self.__monitor_callback)
        self.__monitor.start()
        
        # Create the configuration window
        self.__config_win = config.Config(self.__config_callback)
    
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
            
        # Band area
        self.__bandgrid = QGridLayout()
        w1 = QWidget()
        w1.setLayout(self.__bandgrid)
        self.__grid.addWidget(w1, 0,0)
        
        # Band
        band_lbl = QLabel("Band")
        band_lbl.setMaximumWidth(40)
        self.__cb_band = QComboBox()
        self.__cb_band.setMaximumWidth(60)
        self.__cb_band.addItems(g_band_values)
        self.__cb_band.setToolTip('Select band')
        self.__bandgrid.addWidget(band_lbl, 0,0)
        self.__bandgrid.addWidget(self.__cb_band, 0,1)
        self.__set_band = QPushButton("Set")
        self.__set_band.setMaximumWidth(60)
        self.__set_band.setToolTip('Set band values')
        self.__bandgrid.addWidget(self.__set_band, 0,2)
        self.__set_band.clicked.connect(self.__do_set_band)
        
        # Capacitor area
        self.__capgrid = QGridLayout()
        w1 = QWidget()
        w1.setLayout(self.__capgrid)
        self.__grid.addWidget(w1, 1,0)
        
        # Slider labels
        setpoint_tag = QLabel("Set")
        self.__capgrid.addWidget(setpoint_tag, 0,2)
        actual_tag = QLabel("Act")
        self.__capgrid.addWidget(actual_tag, 0,3)
        
        # Add sliders
        cap_lbl = QLabel("Variable Cap")
        self.__capgrid.addWidget(cap_lbl, 1,0)
        self.__cap = QSlider(QtCore.Qt.Horizontal)
        self.__cap.setToolTip('Adjust value')
        self.__cap.setMinimum(0)
        self.__cap.setMaximum(180)
        self.__cap.setValue(0)
        self.__capgrid.addWidget(self.__cap, 1,1)
        self.__cap.valueChanged.connect(self.__cap_changed)
        self.__cap_val = QLabel("0")
        self.__cap_val.setToolTip('Requested value')
        self.__cap_val.setMinimumWidth(30)
        self.__cap_val.setStyleSheet("color: green; font: 14px")
        self.__capgrid.addWidget(self.__cap_val, 1,2)
        self.__cap_actual = QLabel("0")
        self.__cap_actual.setToolTip('Actual value - may lag requested')
        self.__cap_actual.setMinimumWidth(30)
        self.__cap_actual.setStyleSheet("color: red; font: 14px")
        self.__capgrid.addWidget(self.__cap_actual, 1,3)
        
        # Add buttons
        self.__btngrid = QGridLayout()
        w3 = QWidget()
        w3.setLayout(self.__btngrid)
        self.__grid.addWidget(w3, 2,0)
        self.__config = QPushButton("Config")
        self.__config.setToolTip('Show configuration window...')
        self.__btngrid.addWidget(self.__config, 0,0)
        self.__config.clicked.connect(self.__do_config)
        self.__exit = QPushButton("Exit")
        self.__exit.setToolTip('Exit application...')
        self.__btngrid.addWidget(self.__exit, 0,1)
        self.__exit.clicked.connect(self.__do_exit)
        
    #========================================================================================
    # Run application
    def run(self, ):
        """ Run the application """
        
        # Start idle processing
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
        
        # Returns when application exits
        # Show the GUI
        self.show()
        self.repaint()
        
        if not self.__configured:
            self.__config_win.show()
            
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
        
        # Close config win
        self.__config_win.close()
        
        # Close socket
        self.__sock.close()

    def __do_config(self):
        
        # Show the configuration window
        self.__config_win.show_window()
        
    def __do_exit(self):
        
        self.__close()
        sys.exit()
        
    #=======================================================
    # Set server to new capacitor degrees
    def __cap_changed(self):
    
        # Value ranges 0 - 180
        val = self.__cap.value()
        self.__net_send([CMD_MOVE, [0, val]])
        self.__cap_val.setText(str(val))
    
    #=======================================================
    # Set server to band paramters
    def __do_set_band(self):
        # Do a complete relay init
        self.__net_send([CMD_RELAYS_INIT, (model.auto_tune_model[CONFIG][CAP_PINMAP][3000])])
        self.__net_send([CMD_RELAYS_INIT, list((model.auto_tune_model[CONFIG][IND_PINMAP].values()))])
        self.__net_send([CMD_RELAYS_INIT, [model.auto_tune_model[CONFIG][IND_TOGGLE],]])
        # Get parameters
        band = self.__cb_band.currentText()
        cap, extra, tap = model.auto_tune_model[CONFIG][BAND][int(band)]
        # Set parameters
        self.__net_send([CMD_RELAYS_SET, model.auto_tune_model[CONFIG][CAP_PINMAP][int(extra)]])
        self.__net_send([CMD_RELAYS_SET, [model.auto_tune_model[CONFIG][IND_PINMAP][int(tap)],]])
        self.__net_send([CMD_SERVO_MOVE, (cap,)])
       
    #======================================================= 
    def __monitor_callback(self, data):
        
        self.__progress = data
        self.__config_win.progress(data)
        
    #======================================================= 
    def __idleProcessing   (self):
        
        # Update UI with actual progress
        self.__cap_actual.setText(str(self.__progress))
        # Set timer
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)

    #======================================================= 
    # Callbacks
    def __config_callback(self, cmd, params):
        
        self.__net_send([cmd, params])

    #======================================================= 
    # Net send
    def __net_send(self, data):
        self.__sock.sendto(pickle.dumps(data), (model.auto_tune_model[CONFIG][RPi][IP], model.auto_tune_model[CONFIG][RPi][RQST_PORT]))
    
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