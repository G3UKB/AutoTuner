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
        self.__tx_progress = 0
        self.__tx_actual = 0
        self.__ant_progress = 0
        self.__ant_actual = 0
        
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
        
        # Set default range
        self.__servo_min = model.auto_tune_model[CONFIG][ANT_LOW_PWM]
        self.__servo_max = model.auto_tune_model[CONFIG][ANT_HIGH_PWM]
        self.__net_send((CMD_TX_SERVO_SET_PWM, (self.__servo_min, self.__servo_max)))

        self.__servo_min = model.auto_tune_model[CONFIG][TX_LOW_PWM]
        self.__servo_max = model.auto_tune_model[CONFIG][TX_HIGH_PWM]
        self.__net_send((CMD_ANT_SERVO_SET_PWM, (self.__servo_min, self.__servo_max)))
        
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
        
        # -------------------------------------------
        # Button area
        self.__btngrid = QGridLayout()
        w1 = QGroupBox('Function')
        w1.setLayout(self.__btngrid)
        self.__grid.addWidget(w1, 0,0)
        
        self.__mem = QPushButton("Memories")
        self.__mem.setToolTip('Show memory window...')
        self.__btngrid.addWidget(self.__mem, 0,0)
        self.__mem.clicked.connect(self.__do_mem)
        
        self.__config = QPushButton("Config")
        self.__config.setToolTip('Show configuration window...')
        self.__btngrid.addWidget(self.__config, 0,1)
        self.__config.clicked.connect(self.__do_config)
        
        self.__exit = QPushButton("Exit")
        self.__exit.setToolTip('Exit application...')
        self.__btngrid.addWidget(self.__exit, 0,2)
        self.__exit.clicked.connect(self.__do_exit)
        
        #=======================================================
        # Range selection area
        self.__rangegrid = QGridLayout()
        w2 = QGroupBox('Inductor')
        w2.setLayout(self.__rangegrid)
        self.__grid.addWidget(w2, 1,0)
        
        # Radio buttons for inductor taps
        range_lbl = QLabel("Select Range")
        self.__rangegrid.addWidget(range_lbl, 0,0)
        
        self.__chb_low_range = QRadioButton(model.auto_tune_model[CONFIG][LOW_RANGE][LABEL])
        self.__chb_low_range.setToolTip('Check box to select low frequency range')
        self.__rangegrid.addWidget(self.__chb_low_range, 0,1)
        self.__chb_high_range = QRadioButton(model.auto_tune_model[CONFIG][HIGH_RANGE][LABEL])
        self.__chb_high_range.setToolTip('Check box to select high frequency range')
        self.__rangegrid.addWidget(self.__chb_high_range, 0,2)
        self.__chb_low_range.toggled.connect(lambda:self.__do_range_changed(self.__chb_low_range))
        self.__chb_high_range.toggled.connect(lambda:self.__do_range_changed(self.__chb_high_range))
        
        #=======================================================
        # Capacitor area
        self.__capgrid = QGridLayout()
        w3 = QGroupBox('Capacitors')
        w3.setLayout(self.__capgrid)
        self.__grid.addWidget(w3, 2,0)
        
        # Slider labels
        tx_setpoint_tag = QLabel("Set")
        self.__capgrid.addWidget(tx_setpoint_tag, 0,2)
        tx_actual_tag = QLabel("Act")
        self.__capgrid.addWidget(tx_actual_tag, 0,3)
        
        # -------------------------------------------
        # TX Capacitor
        # Add sliders
        tx_cap_lbl = QLabel("TX Tune")
        self.__capgrid.addWidget(tx_cap_lbl, 1,0)
        self.__tx_cap = QSlider(QtCore.Qt.Horizontal)
        self.__tx_cap.setToolTip('Adjust value')
        self.__tx_cap.setMinimum(0)
        self.__tx_cap.setMaximum(180)
        self.__tx_cap.setValue(0)
        self.__capgrid.addWidget(self.__tx_cap, 1,1)
        self.__tx_cap.valueChanged.connect(self.__tx_cap_changed)
        self.__tx_cap_val = QLabel("0")
        self.__tx_cap_val.setToolTip('Requested value')
        self.__tx_cap_val.setMinimumWidth(30)
        self.__tx_cap_val.setStyleSheet("color: green; font: 14px")
        self.__capgrid.addWidget(self.__tx_cap_val, 1,2)
        self.__tx_cap_actual = QLabel("0")
        self.__tx_cap_actual.setToolTip('Actual value - may lag requested')
        self.__tx_cap_actual.setMinimumWidth(30)
        self.__tx_cap_actual.setStyleSheet("color: red; font: 14px")
        self.__capgrid.addWidget(self.__tx_cap_actual, 1,3)
        
        # -------------------------------------------
        # Ant Capacitor
        # Add sliders
        ant_cap_lbl = QLabel("Ant Tune")
        self.__capgrid.addWidget(ant_cap_lbl, 2,0)
        self.__ant_cap = QSlider(QtCore.Qt.Horizontal)
        self.__ant_cap.setToolTip('Adjust value')
        self.__ant_cap.setMinimum(0)
        self.__ant_cap.setMaximum(180)
        self.__ant_cap.setValue(0)
        self.__capgrid.addWidget(self.__ant_cap, 2,1)
        self.__ant_cap.valueChanged.connect(self.__ant_cap_changed)
        self.__ant_cap_val = QLabel("0")
        self.__ant_cap_val.setToolTip('Requested value')
        self.__ant_cap_val.setMinimumWidth(30)
        self.__ant_cap_val.setStyleSheet("color: green; font: 14px")
        self.__capgrid.addWidget(self.__ant_cap_val, 2,2)
        self.__ant_cap_actual = QLabel("0")
        self.__ant_cap_actual.setToolTip('Actual value - may lag requested')
        self.__ant_cap_actual.setMinimumWidth(30)
        self.__ant_cap_actual.setStyleSheet("color: red; font: 14px")
        self.__capgrid.addWidget(self.__ant_cap_actual, 2,3)
        
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
    
    def __do_mem(self):
        
        # Show the memory window
        #self.__mem_win.show_window()
        pass

    def __do_exit(self):
        
        self.__close()
        sys.exit()
        
    #=======================================================
    # Set server to new capacitor degrees
    def __tx_cap_changed(self):
    
        # Value ranges 0 - 180
        val = self.__tx_cap.value()
        self.__net_send([CMD_TX_SERVO_MOVE, [val]])
        self.__tx_cap_val.setText(str(val))
    
    def __ant_cap_changed(self):
    
        # Value ranges 0 - 180
        val = self.__ant_cap.value()
        self.__net_send([CMD_ANT_SERVO_MOVE, [val]])
        self.__ant_cap_val.setText(str(val))

    #=======================================================
    # Set server to band paramters
    def __do_range_changed(self, rb):
        
        # Collect parameters
        params = []
        inv = model.auto_tune_model[CONFIG][RELAY_INVERSE]
        for pin in model.auto_tune_model[CONFIG][INDUCTOR_PINMAP]:
            params.append((pin, inv))
            
        # Do a complete relay init
        self.__net_send([CMD_RELAYS_INIT, params])
        
        # Set relays for bands
        if rb.text() == model.auto_tune_model[CONFIG][LOW_RANGE][LABEL]:
            if rb.isChecked() == True:
                self.__net_send([CMD_RELAYS_RESET, params])
        if rb.text() == model.auto_tune_model[CONFIG][HIGH_RANGE][LABEL]:
            if rb.isChecked() == True:
                self.__net_send([CMD_RELAYS_SET, params])
       
    #======================================================= 
    def __monitor_callback(self, data):
        if data[0] == 'tx':    
            self.__tx_progress = data[1]
        else:
            self.__ant_progress = data[1]
        
    #======================================================= 
    def __idleProcessing(self):
        # Update UI with actual progress
        self.__tx_cap_actual.setText(str(self.__tx_progress))
        self.__ant_cap_actual.setText(str(self.__ant_progress))
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