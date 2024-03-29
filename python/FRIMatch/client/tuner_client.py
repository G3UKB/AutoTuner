#!/usr/bin/env python3
#
# tuner_client.py
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

#======================================================================================
# Main application window
class TunerClient(QMainWindow):
    
    def __init__(self, path, qt_app):
        
        super(TunerClient, self).__init__()
        
        # Manage configuration
        self.__configured = True
        CONFIG_PATH = path
        self.__model = persist.getSavedCfg(CONFIG_PATH)
        if self.__model == None:
            print ('Configuration not found, using defaults')
            self.__model = model.auto_tune_model
            self.__configured = False
        # Create a datagram socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind(('', model.auto_tune_model[CONFIG][RPi][EVNT_PORT]))
        self.__sock.settimeout(3)
        
        # The application
        self.__qt_app = qt_app
        
        # Heartbeat from server
        self.__heartbeat = False
        self.__heartbeat_timer = HEARTBEAT_TIMER
        
        # Server
        self.__alive = False
        self.__settings = False
        
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
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.__connect_status = QLabel("Tuner: offline")
        self.statusBar.insertPermanentWidget(0, self.__connect_status)
        self.__connect_status.setStyleSheet("color: red; font: 14px; font-family: Courier;")

        # Initialise the GUI
        self.__initUI()
        
        # Populate
        self.__populate()
        
        # Start monitor thread
        self.__monitor = Monitor(self.__sock, self.__monitor_callback)
        self.__monitor.start()
        
        # Create the configuration window
        self.__config_win = config.Config(self.__model, self.__config_callback)
        
        # Create the memories window
        self.__mem_win = memories.Memories(self.__model, self.settings, self.__mem_callback)
        
        # Set default range
        self.__servo_min = self.__model[CONFIG][SERVO][ANT_LOW_PWM]
        self.__servo_max = self.__model[CONFIG][SERVO][ANT_HIGH_PWM]
        self.__net_send((CMD_ANT_SERVO_SET_PWM, (self.__servo_min, self.__servo_max)))

        self.__servo_min = self.__model[CONFIG][SERVO][TX_LOW_PWM]
        self.__servo_max = self.__model[CONFIG][SERVO][TX_HIGH_PWM]
        self.__net_send((CMD_TX_SERVO_SET_PWM, (self.__servo_min, self.__servo_max)))
        
    #========================================================================================    
    # UI initialisation and window event handlers
    def __initUI(self):
        """ Configure the GUI interface """
        
        self.setToolTip('Remote Auto-Tuner')
        
        # Arrange window
        x,y,w,h = self.__model[STATE][MAIN_WIN]
        self.setGeometry(x,y,w,h)
                         
        self.setWindowTitle('Remote Auto-Tuner')
        
        #=======================================================
        # Set main layout
        w = QWidget()
        self.setCentralWidget(w)
        self.__grid = QGridLayout()
        w.setLayout(self.__grid)
        self.__grid.setColumnStretch(0,0)
        self.__grid.setColumnStretch(1,1)
        
        # -------------------------------------------
        # Button area
        self.__btngrid = QGridLayout()
        w1 = QGroupBox('Function')
        w1.setLayout(self.__btngrid)
        self.__grid.addWidget(w1, 0,0,2,1)
        
        self.__mem = QPushButton("Memories...")
        self.__mem.setToolTip('Show memory window...')
        self.__btngrid.addWidget(self.__mem, 0,0)
        self.__mem.clicked.connect(self.__do_mem)
        self.__mem.setMaximumHeight(20)

        self.__config = QPushButton("Config...")
        self.__config.setToolTip('Show configuration window...')
        self.__btngrid.addWidget(self.__config, 1,0)
        self.__config.clicked.connect(self.__do_config)
        
        self.__spacer = QWidget()
        self.__btngrid.addWidget(self.__spacer, 2,0)
        
        self.__exit = QPushButton("Exit")
        self.__exit.setToolTip('Exit application...')
        self.__btngrid.addWidget(self.__exit, 3,0)
        self.__exit.clicked.connect(self.__do_exit)
        
        self.__btngrid.setColumnStretch(0,0)
        self.__btngrid.setColumnStretch(1,0)
        self.__btngrid.setColumnStretch(2,0)
        self.__btngrid.setColumnStretch(3,1)
        
        #=======================================================
        # Range selection area
        self.__rangegrid = QGridLayout()
        self.__w2 = QGroupBox('Inductor')
        self.__w2.setLayout(self.__rangegrid)
        self.__grid.addWidget(self.__w2, 0,1)
        
        # Radio buttons for inductor taps
        range_lbl = QLabel("Select Range")
        self.__rangegrid.addWidget(range_lbl, 0,0)
        
        self.__crb_low_range = QRadioButton(self.__model[CONFIG][RELAY][LOW_RANGE][LABEL])
        self.__crb_low_range.setToolTip('Check box to select low frequency range')
        self.__rangegrid.addWidget(self.__crb_low_range, 0,1)
        self.__crb_high_range = QRadioButton(self.__model[CONFIG][RELAY][HIGH_RANGE][LABEL])
        self.__crb_high_range.setToolTip('Check box to select high frequency range')
        self.__rangegrid.addWidget(self.__crb_high_range, 0,2)
        self.__crb_low_range.toggled.connect(lambda:self.__do_range_changed(self.__crb_low_range))
        self.__crb_high_range.toggled.connect(lambda:self.__do_range_changed(self.__crb_high_range))
        
        #=======================================================
        # Capacitor area
        self.__capgrid = QGridLayout()
        self.__w3 = QGroupBox('Capacitors')
        self.__w3.setLayout(self.__capgrid)
        self.__grid.addWidget(self.__w3, 1,1)
        
        self.__captypegrid = QGridLayout()
        w4 = QGroupBox('Servo')
        w4.setLayout(self.__captypegrid)
        self.__capgrid.addWidget(w4, 0,0,1,6)
        
        # Move type
        move_type_tag = QLabel("Move Type")
        self.__captypegrid.addWidget(move_type_tag, 0,0)
        self.__crb_track = QRadioButton("Track")
        self.__crb_track.setToolTip('Track movement of slider')
        self.__captypegrid.addWidget(self.__crb_track, 0,1)
        self.__crb_wait = QRadioButton("Wait")
        self.__crb_wait.setToolTip('Wait for slider release')
        self.__captypegrid.addWidget(self.__crb_wait, 0,2)
        
        # Slider labels
        tx_setpoint_tag = QLabel("Set")
        self.__capgrid.addWidget(tx_setpoint_tag, 1,4)
        tx_actual_tag = QLabel("Act")
        self.__capgrid.addWidget(tx_actual_tag, 1,5)
        
        # -------------------------------------------
        # TX Capacitor
        # Add sliders
        tx_cap_lbl = QLabel("TX Tune")
        self.__capgrid.addWidget(tx_cap_lbl, 2,0)
        self.__tx_cap = QSlider(QtCore.Qt.Horizontal)
        self.__tx_cap.setToolTip('Adjust value')
        self.__tx_cap.setMinimum(0)
        self.__tx_cap.setMaximum(180)
        self.__tx_cap.setValue(0)
        self.__capgrid.addWidget(self.__tx_cap, 2,1)
        self.__tx_cap.valueChanged.connect(self.__tx_cap_changed)
        self.__tx_cap.sliderReleased.connect(self.__tx_cap_released)
        
        # Add nudge buttons
        self.__tx_nudge_down = QPushButton("<")
        self.__tx_nudge_down.setMaximumWidth(20)
        self.__tx_nudge_down.setToolTip('Increase capacitance a tad')
        self.__capgrid.addWidget(self.__tx_nudge_down, 2,2)
        self.__tx_nudge_down.clicked.connect(self.__do_tx_nudge_down)
        self.__tx_nudge_up = QPushButton(">")
        self.__tx_nudge_up.setMaximumWidth(20)
        self.__tx_nudge_up.setToolTip('Decrease capacitance a tad')
        self.__capgrid.addWidget(self.__tx_nudge_up, 2,3)
        self.__tx_nudge_up.clicked.connect(self.__do_tx_nudge_up)
        
        # Add requested and actual values
        self.__tx_cap_val = QLabel("0")
        self.__tx_cap_val.setToolTip('Requested value')
        self.__tx_cap_val.setMinimumWidth(30)
        self.__tx_cap_val.setStyleSheet("color: green; font: 14px")
        self.__capgrid.addWidget(self.__tx_cap_val, 2,4)
        self.__tx_cap_actual = QLabel("0")
        self.__tx_cap_actual.setToolTip('Actual value - may lag requested')
        self.__tx_cap_actual.setMinimumWidth(30)
        self.__tx_cap_actual.setStyleSheet("color: red; font: 14px")
        self.__capgrid.addWidget(self.__tx_cap_actual, 2,5)
             
        # -------------------------------------------
        # Ant Capacitor
        # Add sliders
        ant_cap_lbl = QLabel("Ant Tune")
        self.__capgrid.addWidget(ant_cap_lbl, 3,0)
        self.__ant_cap = QSlider(QtCore.Qt.Horizontal)
        self.__ant_cap.setToolTip('Adjust value')
        self.__ant_cap.setMinimum(0)
        self.__ant_cap.setMaximum(180)
        self.__ant_cap.setValue(0)
        self.__capgrid.addWidget(self.__ant_cap, 3,1)
        self.__ant_cap.valueChanged.connect(self.__ant_cap_changed)
        self.__ant_cap.sliderReleased.connect(self.__ant_cap_released)
        
        # Add nudge buttons
        self.__ant_nudge_down = QPushButton("<")
        self.__ant_nudge_down.setMaximumWidth(20)
        self.__ant_nudge_down.setToolTip('Increase capacitance a tad')
        self.__capgrid.addWidget(self.__ant_nudge_down, 3,2)
        self.__ant_nudge_down.clicked.connect(self.__do_ant_nudge_down)
        self.__ant_nudge_up = QPushButton(">")
        self.__ant_nudge_up.setMaximumWidth(20)
        self.__ant_nudge_up.setToolTip('Decrease capacitance a tad')
        self.__capgrid.addWidget(self.__ant_nudge_up, 3,3)
        self.__ant_nudge_up.clicked.connect(self.__do_ant_nudge_up)
        
        # Add requested and actual values
        self.__ant_cap_val = QLabel("0")
        self.__ant_cap_val.setToolTip('Requested value')
        self.__ant_cap_val.setMinimumWidth(30)
        self.__ant_cap_val.setStyleSheet("color: green; font: 14px")
        self.__capgrid.addWidget(self.__ant_cap_val, 3,4)
        self.__ant_cap_actual = QLabel("0")
        self.__ant_cap_actual.setToolTip('Actual value - may lag requested')
        self.__ant_cap_actual.setMinimumWidth(30)
        self.__ant_cap_actual.setStyleSheet("color: red; font: 14px")
        self.__capgrid.addWidget(self.__ant_cap_actual, 3,5)
    
    #========================================================================================
    # Populate UI
    def __populate(self, ):
        
        if self.__model[CONFIG][RELAY][LOW_RANGE][ENERGISE]:
            self.__crb_low_range.setChecked(True)
        else:
            self.__crb_high_range.setChecked(True)
            
        if self.__model[CONFIG][SERVO][MODE] == MODE_TRACK:
            self.__crb_track.setChecked(True)
        else:
            self.__crb_wait.setChecked(True)
        
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
            self.statusBar.showMessage('Please run configuration')
            
        # Enter event loop
        return self.__qt_app.exec_()    
    
    #========================================================================================
    # Get settings
    def settings(self, ):
        low = self.__crb_low_range.isChecked()
        high = self.__crb_low_range.isChecked()
        tx = self.__tx_cap.value()
        ant = self.__ant_cap.value()
        
        return (low, high, tx, ant)

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
        
        # Close memory win
        self.__mem_win.close()

        # Close socket
        self.__sock.close()
        
        # Save model
        persist.saveCfg(CONFIG_PATH, self.__model)

    def resizeEvent(self, event):
        # Update config
        x,y,w,h = self.__model[STATE][MAIN_WIN]
        self.__model[STATE][MAIN_WIN] = [x,y,event.size().width(),event.size().height()]
        
    def moveEvent(self, event):
        # Update config
        x,y,w,h = self.__model[STATE][MAIN_WIN]
        self.__model[STATE][MAIN_WIN] = [event.pos().x(),event.pos().y(),w,h]
        
    #=======================================================
    # Button events
    def __do_config(self):
        # Show the configuration window
        self.__config_win.show_window()
        self.statusBar.clearMessage()
    
    def __do_mem(self):
        # Show the memory window
        self.__mem_win.show_window()
    
    def __do_exit(self):
        # Close application
        self.__close()
        sys.exit()
        
    #=======================================================
    # Set server to new capacitor degrees
    def __tx_cap_changed(self):
        # Value ranges 0 - 180
        val = self.__tx_cap.value()
        if self.__crb_track.isChecked():
            self.__net_send([CMD_TX_SERVO_MOVE, [val]])
        self.__tx_cap_val.setText(str(val))
    
    def __tx_cap_released(self):
        # Value ranges 0 - 180
        val = self.__tx_cap.value()
        if self.__crb_wait.isChecked():
            self.__net_send([CMD_TX_SERVO_MOVE, [val]])
        self.__tx_cap_val.setText(str(val))

    def __ant_cap_changed(self):
        # Value ranges 0 - 180
        val = self.__ant_cap.value()
        if self.__crb_track.isChecked():
            self.__net_send([CMD_ANT_SERVO_MOVE, [val]])
        self.__ant_cap_val.setText(str(val))

    def __ant_cap_released(self):
        # Value ranges 0 - 180
        val = self.__ant_cap.value()
        if self.__crb_wait.isChecked():
            self.__net_send([CMD_ANT_SERVO_MOVE, [val]])
        self.__ant_cap_val.setText(str(val))
        
    # Do nudge up/down
    def __do_tx_nudge_down(self):
        val = self.__tx_cap.value() - self.__get_inc()
        self.__do_nudge(self.__tx_cap, self.__tx_cap_val, CMD_TX_SERVO_MOVE, val)
    
    def __do_tx_nudge_up(self):
        val = self.__tx_cap.value() + self.__get_inc()
        self.__do_nudge(self.__tx_cap, self.__tx_cap_val, CMD_TX_SERVO_MOVE, val)
    
    def __do_ant_nudge_down(self):
        val = self.__ant_cap.value() - self.__get_inc()
        self.__do_nudge(self.__ant_cap, self.__ant_cap_val, CMD_ANT_SERVO_MOVE, val)
    
    def __do_ant_nudge_up(self):
        val = self.__ant_cap.value() + self.__get_inc()
        self.__do_nudge(self.__ant_cap, self.__ant_cap_val, CMD_ANT_SERVO_MOVE, val)
    
    def __get_inc(self):
        return self.__model[CONFIG][SERVO][NUDGE_INC]
        
    def __do_nudge(self, w_slider, w_value, cmd, val):
        if val >= 0 and val <=180:
            self.__net_send([cmd, [val]])
            w_value.setText(str(val))
            w_slider.setValue(val)
        
    #=======================================================
    # Set server to band paramters
    def __do_range_changed(self, rb):
        # Collect parameters
        params = []
        inv = self.__model[CONFIG][RELAY][RELAY_INVERSE]
        for pin in self.__model[CONFIG][RELAY][INDUCTOR_PINMAP]:
            params.append((pin, inv))
            
        # Do a complete relay init
        self.__net_send([CMD_RELAYS_INIT, params])
        
        # Set relays for bands
        if rb.text() == self.__model[CONFIG][RELAY][LOW_RANGE][LABEL]:
            if rb.isChecked() == True:
                self.__net_send([CMD_RELAYS_RESET, params])
        if rb.text() == self.__model[CONFIG][RELAY][HIGH_RANGE][LABEL]:
            if rb.isChecked() == True:
                self.__net_send([CMD_RELAYS_SET, params])
        
    #======================================================= 
    def __idleProcessing(self):
        # Update UI with actual progress
        self.__tx_cap_actual.setText(str(self.__tx_progress))
        self.__ant_cap_actual.setText(str(self.__ant_progress))
        
        # Check heartbeat
        self.__heartbeat_timer -= 1
        if self.__heartbeat_timer <= 0:
            # Check now      
            if self.__heartbeat:
                self.__alive = True
                self.__heartbeat = False
                self.__connect_status.setText("Tuner: online")
                self.__connect_status.setStyleSheet("color: green; font: 14px; font-family: Courier;")
                self.__set_enabled(True)
                self.__config_win.tuner_status(True)
                if not self.__settings:
                    self.__send_settings()
                    self.__settings = True
            else:
                # Send wakeup
                self.__net_send([CMD_WAKEUP, ()])
                # Alert
                self.__connect_status.setText("Tuner: offline")
                self.__connect_status.setStyleSheet("color: red; font: 14px; font-family: Courier;")
                self.__alive = False
                self.__settings = False
                self.__set_enabled(False)
                self.__config_win.tuner_status(False)
            self.__heartbeat_timer = HEARTBEAT_TIMER
        
        # Set timer
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)

    def __set_enabled(self, online):
        if online and self.__configured:
            self.__w2.setEnabled(True)
            self.__w3.setEnabled(True)
            self.__mem.setEnabled(True)
        else:
            self.__w2.setEnabled(False)
            self.__w3.setEnabled(False)
            self.__mem.setEnabled(False)
        
    def __send_settings(self):
        params = (
            self.__model[CONFIG][SERVO][TRACK_INC],
            self.__model[CONFIG][SERVO][TRACK_DELAY],
            self.__model[CONFIG][SERVO][SCAN_INC],
            self.__model[CONFIG][SERVO][SCAN_DELAY]
        )
        self.__net_send([CMD_SERVO_SETTINGS, params])
        # Send the servos home
        self.__net_send([CMD_TX_SERVO_HOME, []])
        sleep(2)
        self.__net_send([CMD_ANT_SERVO_HOME, []])
        
    #======================================================= 
    # Callbacks
    #======================================================= 
    def __monitor_callback(self, data):
        if data[0] == 'heartbeat':
            self.__heartbeat = True
        elif data[0] == 'tx':    
            self.__tx_progress = data[1]
        elif data[0] == 'ant':
            self.__ant_progress = data[1]
            
    def __config_callback(self, cmd, params):
        self.__net_send([cmd, params])

    def __mem_callback(self, ind, tx, ant):
        # Execute settings, set interface
        
        # Collect parameters for relays
        params = []
        inv = self.__model[CONFIG][RELAY][RELAY_INVERSE]
        for pin in self.__model[CONFIG][RELAY][INDUCTOR_PINMAP]:
            params.append((pin, inv))
        # Set relays and adjust UI
        if ind == 'low-range':
            self.__crb_low_range.setChecked(True)
            self.__net_send([CMD_RELAYS_RESET, params])
        if ind == 'high-range':
            self.__crb_high_range.setChecked(True)
            self.__net_send([CMD_RELAYS_SET, params])
        # Set caps and adjust UI
        tx = int(tx)
        if tx >= 0 and tx <=180:
            self.__net_send([CMD_TX_SERVO_MOVE, [tx]])
            self.__tx_cap.setValue(tx)
            self.__tx_cap_val.setText(str(tx))
        ant = int(ant)
        if ant >= 0 and ant <=180:
            self.__net_send([CMD_ANT_SERVO_MOVE, [ant]])
            self.__ant_cap.setValue(ant)
            self.__ant_cap_val.setText(str(ant))
            
    #======================================================= 
    # Net send
    def __net_send(self, data):
        self.__sock.sendto(pickle.dumps(data), (self.__model[CONFIG][RPi][IP], self.__model[CONFIG][RPi][RQST_PORT]))
    
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
            except ConnectionResetError:
                continue
            except:
                print("Unexpected error on socket.recvFrom():", sys.exc_info()[0])
                
#======================================================================================================================
# Main code
def main():
    
    if len(sys.argv) != 2:
        print("Please supply a configuration filename!")
        print("python tuner_client.py <path>/filename")
    else:
        try:
            # The one and only QApplication 
            qt_app = QApplication(sys.argv)
            # Crete instance
            client = TunerClient(sys.argv[1], qt_app)
            # Run application loop
            sys.exit(client.run())
           
        except Exception as e:
            print ('Exception [%s][%s]' % (str(e), traceback.format_exc()))
 
# Entry point       
if __name__ == '__main__':
    main()