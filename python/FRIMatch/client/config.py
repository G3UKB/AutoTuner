#!/usr/bin/env python3
#
# config.py
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
# Configuration window
class Config(QMainWindow):
    
    def __init__(self, model, callback):
        
        super(Config, self).__init__()
        
        self.__model = model
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
    
        # Start idle processing
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
        
    #========================================================================================    
    # UI initialisation and window event handlers
    def initUI(self):
        """ Configure the GUI interface """
        
        self.setToolTip('Configuration')
        
        # Arrange window
        x,y,w,h = self.__model[STATE][CONFIG_WIN]
        self.setGeometry(x,y,w,h)
                         
        self.setWindowTitle('Configure Auto-Tuner')
        
        #=======================================================
        # Set main layout
        w = QWidget()
        self.setCentralWidget(w)
        self.__grid = QGridLayout()
        w.setLayout(self.__grid)
        
        # Within this we need 4 sub-layouts
        self.__rpi_grid = QGridLayout()
        w1 = QGroupBox('RPi Network Config')
        w1.setLayout(self.__rpi_grid)
        self.__grid.addWidget(w1, 0,0)
        
        self.__span_grid = QGridLayout()
        w2 = QGroupBox('Servo Config')
        w2.setLayout(self.__span_grid)
        self.__grid.addWidget(w2, 1,0)
        
        self.__map_grid = QGridLayout()
        w3 = QGroupBox('RPi GPIO Config')
        w3.setLayout(self.__map_grid)
        self.__grid.addWidget(w3, 2,0)
        
        self.__set_grid = QGridLayout()
        w4 = QGroupBox('Servo Parameters')
        w4.setLayout(self.__set_grid)
        self.__grid.addWidget(w4, 3,0)
        
        # Populate grids
        self.__rpi(self.__rpi_grid)
        self.__pop_span(self.__span_grid)
        self.__pop_map(self.__map_grid)
        self.__set_params(self.__set_grid)
        
        # Control buttons
        self.__cntrl_grid = QGridLayout()
        w5 = QWidget()
        w5.setLayout(self.__cntrl_grid)
        self.__grid.addWidget(w5, 4,0)
        
        self.__btn_save = QPushButton("Save")
        self.__cntrl_grid.addWidget(self.__btn_save, 0,0)
        self.__btn_save.setToolTip('Configuration will be saved and window closed')
        self.__btn_save.clicked.connect(self.__do_save)
        self.__btn_cancel = QPushButton("Cancel")
        self.__btn_cancel.setToolTip('Changes will be canceled and window closed')
        self.__cntrl_grid.addWidget(self.__btn_cancel, 0,1)
        self.__btn_cancel.clicked.connect(self.__do_cancel)
    
        # Populate everything
        self.__init_fields()
        
    #-------------------------------------------------------------
    # Set the RPi network config
    def __rpi(self, g):
        
        # We need the Ip and port
        ip_lbl = QLabel("IP")
        g.addWidget(ip_lbl, 0, 0)
        rqst_port_lbl = QLabel("Rqst port")
        g.addWidget(rqst_port_lbl, 0, 2)
        evnt_port_lbl = QLabel("Envt port")
        g.addWidget(evnt_port_lbl, 0, 4)
        
        self.__iptxt = QLineEdit()
        self.__iptxt.setMinimumWidth(70)
        self.__iptxt.setInputMask('000.000.000.000;_')
        self.__iptxt.setToolTip('IP Address of RPi')
        g.addWidget(self.__iptxt, 0, 1)
        self.__iptxt.editingFinished.connect(self.__ip_changed)
        
        self.__txt_rqst_port = QLineEdit()
        self.__txt_rqst_port.setMaximumWidth(30)
        self.__txt_rqst_port.setInputMask('00000;_')
        self.__txt_rqst_port.setMaximumWidth(100)
        self.__txt_rqst_port.setToolTip('Port RPi listens on')
        g.addWidget(self.__txt_rqst_port, 0, 3)
        self.__txt_rqst_port.editingFinished.connect(self.__rqst_port_changed)
        
        self.__txt_evnt_port = QLineEdit()
        self.__txt_evnt_port.setMaximumWidth(30)
        self.__txt_evnt_port.setInputMask('00000;_')
        self.__txt_evnt_port.setMaximumWidth(100)
        self.__txt_evnt_port.setToolTip('Port RPi sends events on')
        g.addWidget(self.__txt_evnt_port, 0, 5)
        self.__txt_evnt_port.editingFinished.connect(self.__evnt_port_changed)
        
    #-------------------------------------------------------------
    # Set the servo limits to achieve 0-180 degrees rotation
    def __pop_span(self, g):
        
        # We need two fields for PWM values
        # and two buttons for execution
        
        # TX
        # Values for PWM upper and lower
        lower_tx_lbl = QLabel("TX Low PWM")
        upper_tx_lbl = QLabel("TX High PWM")
        self.__sb_tx_lower = QSpinBox()
        self.__sb_tx_lower.setRange(0, 3000)
        self.__sb_tx_lower.setToolTip('Lower bound of TX PWM range')
        self.__sb_tx_upper = QSpinBox()
        self.__sb_tx_upper.setRange(0, 3000)
        self.__sb_tx_upper.setToolTip('Upper bound of TX PWM range')
        g.addWidget(lower_tx_lbl, 0,0)
        g.addWidget(self.__sb_tx_lower, 0,1)
        g.addWidget(upper_tx_lbl, 0,2)
        g.addWidget(self.__sb_tx_upper, 0,3)
        # Activation buttons
        self.__btn_tx_set_pwm = QPushButton("Set")
        self.__btn_tx_set_pwm.setMaximumWidth(60)
        self.__btn_tx_set_pwm.setToolTip('Set TX range')
        g.addWidget(self.__btn_tx_set_pwm, 0,4)
        self.__btn_tx_set_pwm.clicked.connect(self.__do_tx_set_pwm)
        self.__btn_tx_tst_pwm = QPushButton("Test")
        self.__btn_tx_tst_pwm.setToolTip('Test TX range, moves 0-180-0')
        self.__btn_tx_tst_pwm.setMaximumWidth(60)
        g.addWidget(self.__btn_tx_tst_pwm, 0,5)
        self.__btn_tx_tst_pwm.clicked.connect(self.__do_tx_test_range)
        
        # Antenna
        # Values for PWM upper and lower
        lower_ant_lbl = QLabel("Ant Low PWM")
        upper_ant_lbl = QLabel("Ant High PWM")
        self.__sb_ant_lower = QSpinBox()
        self.__sb_ant_lower.setRange(0, 3000)
        self.__sb_ant_lower.setToolTip('Lower bound of Ant PWM range')
        self.__sb_ant_upper = QSpinBox()
        self.__sb_ant_upper.setRange(0, 3000)
        self.__sb_ant_upper.setToolTip('Upper bound of Ant PWM range')
        g.addWidget(lower_ant_lbl, 1,0)
        g.addWidget(self.__sb_ant_lower, 1,1)
        g.addWidget(upper_ant_lbl, 1,2)
        g.addWidget(self.__sb_ant_upper, 1,3)
        # Activation buttons
        self.__btn_ant_set_pwm = QPushButton("Set")
        self.__btn_ant_set_pwm.setMaximumWidth(60)
        self.__btn_ant_set_pwm.setToolTip('Set range')
        g.addWidget(self.__btn_ant_set_pwm, 1,4)
        self.__btn_ant_set_pwm.clicked.connect(self.__do_ant_set_pwm)
        self.__btn_ant_tst_pwm = QPushButton("Test")
        self.__btn_ant_tst_pwm.setToolTip('Test range, moves 0-180-0')
        self.__btn_ant_tst_pwm.setMaximumWidth(60)
        g.addWidget(self.__btn_ant_tst_pwm, 1,5)
        self.__btn_ant_tst_pwm.clicked.connect(self.__do_ant_test_range)
        
    #-------------------------------------------------------------
    # Set the pin maps for capacitor values and inductor taps
    def __pop_map(self, g):
        
        # Set the pins for inductor switching
        ind_lbl = QLabel("Inductor Pinmap")
        self.__cb_ind = QComboBox()
        self.__cb_ind.addItems(g_ind_values)
        self.__cb_ind.setToolTip('Select inductor tap')
        self.__cb_indmap = QComboBox()
        self.__cb_indmap.addItems(g_pins)
        self.__cb_indmap.setToolTip('Select pin for tap')
        self.__btn_ind = QPushButton("Set")
        self.__btn_ind.setToolTip('Set tap pin')
        self.__btn_ind.setMaximumWidth(60)
        self.__btn_ind_test = QPushButton("Test")
        self.__btn_ind_test.setToolTip('Cycle all inductor taps - separately')
        self.__btn_ind_test.setMaximumWidth(60)
        g.addWidget(ind_lbl, 1,0)
        g.addWidget(self.__cb_ind, 1,1)
        
        # Set the inverse flag
        inv_lbl = QLabel("Active low")
        self.__cb_inv = QCheckBox()
        self.__cb_inv.setToolTip('Check for relays active low')
        g.addWidget(inv_lbl, 2,0)
        g.addWidget(self.__cb_inv, 2,1)
        
        # Add buttons
        g.addWidget(self.__cb_indmap, 1,2)
        g.addWidget(self.__btn_ind, 1,4)
        g.addWidget(self.__btn_ind_test, 1,5)
        self.__cb_ind.currentIndexChanged.connect(self.__ind_changed)
        self.__btn_ind.clicked.connect(self.__do_set_ind)
        self.__btn_ind_test.clicked.connect(self.__do_test_ind)
    
    #-------------------------------------------------------------
    # Set the servo params
    def __set_params(self, g):
        # Set the following
        # NUDGE_INC
        # TRACK_INC
        # TRACK_DELAY
        # SCAN_INC
        # SCAN_DELAY

        # Labels
        nudge_inc_lbl = QLabel("Nudge inc")
        track_inc_lbl = QLabel("Track inc")
        track_delay_lbl = QLabel("Track delay")
        scan_inc_lbl = QLabel("Scan inc")
        scan_delay_lbl = QLabel("Scan delay")
        g.addWidget(nudge_inc_lbl, 0,0)
        g.addWidget(track_inc_lbl, 1,0)
        g.addWidget(track_delay_lbl, 1,2)
        g.addWidget(scan_inc_lbl, 2,0)
        g.addWidget(scan_delay_lbl, 2,2)
        
        # Entry fields
        self.__sb_nudge_inc = QSpinBox()
        self.__sb_nudge_inc.setRange(1, 10)
        self.__sb_nudge_inc.setToolTip('Degrees increment for nudge buttons')
        
        self.__sb_track_inc = QSpinBox()
        self.__sb_track_inc.setRange(1, 5)
        self.__sb_track_inc.setToolTip('Degrees increment while tracking')
        
        self.__sb_track_delay = QSpinBox()
        self.__sb_track_delay.setRange(1, 100)
        self.__sb_track_delay.setToolTip('Wait time between track increments in ms')
        
        self.__sb_scan_inc = QSpinBox()
        self.__sb_scan_inc.setRange(1, 5)
        self.__sb_scan_inc.setToolTip('Degrees increment on wait scan mode')
        
        self.__sb_scan_delay = QSpinBox()
        self.__sb_scan_delay.setRange(1, 100)
        self.__sb_scan_delay.setToolTip('Wait time between wait increments in ms')
        
        g.addWidget(self.__sb_nudge_inc, 0,1)
        g.addWidget(self.__sb_track_inc, 1,1)
        g.addWidget(self.__sb_track_delay, 1,3)
        g.addWidget(self.__sb_scan_inc, 2,1)
        g.addWidget(self.__sb_scan_delay, 2,3)
        
        # Activation button
        self.__btn_servo_params = QPushButton("Set")
        self.__btn_servo_params.setToolTip('Set servo parameters')
        g.addWidget(self.__btn_servo_params, 3,3)
        self.__btn_servo_params.clicked.connect(self.__do_servo_params)
        
    #-------------------------------------------------------------
    # Initialise all fields
    def __init_fields(self):
        self.__iptxt.setText(self.__model[CONFIG][RPi][IP])
        self.__txt_rqst_port.setText(str(self.__model[CONFIG][RPi][RQST_PORT]))
        self.__txt_evnt_port.setText(str(self.__model[CONFIG][RPi][EVNT_PORT]))
        self.__sb_tx_lower.setValue(self.__model[CONFIG][SERVO][TX_LOW_PWM])
        self.__sb_tx_upper.setValue(self.__model[CONFIG][SERVO][TX_HIGH_PWM])
        self.__sb_ant_lower.setValue(self.__model[CONFIG][SERVO][ANT_LOW_PWM])
        self.__sb_ant_upper.setValue(self.__model[CONFIG][SERVO][ANT_HIGH_PWM])
        
        self.__cb_ind.setCurrentIndex(0)
        self.__cb_indmap.setCurrentIndex(self.__cb_indmap.findText(str(self.__model[CONFIG][RELAY][INDUCTOR_PINMAP][0])))
        
        self.__cb_inv.setChecked(self.__model[CONFIG][RELAY][RELAY_INVERSE])
        
        self.__sb_nudge_inc.setValue(self.__model[CONFIG][SERVO][NUDGE_INC])
        self.__sb_track_inc.setValue(self.__model[CONFIG][SERVO][TRACK_INC])
        self.__sb_track_delay.setValue(self.__model[CONFIG][SERVO][TRACK_DELAY])
        self.__sb_scan_inc.setValue(self.__model[CONFIG][SERVO][SCAN_INC])
        self.__sb_scan_delay.setValue(self.__model[CONFIG][SERVO][SCAN_DELAY])
        
    #========================================================================================
    # PUBLIC procs
    
    def show_window(self):
        
        # Make a copy of the current model
        model.copy_model(self.__model)
        
        # (Re)populate everything
        self.__init_fields()
        
        # Show our window
        self.show()
        self.repaint()
    
    def tuner_status(self, status):
        self.__tuner_status = status
        
    #========================================================================================
    # Event procs
    
    def closeEvent(self, event):
        model.restore_model(self.__model)
        self.hide()
    
    def resizeEvent(self, event):
        # Update config
        x,y,w,h = self.__model[STATE][CONFIG_WIN]
        self.__model[STATE][CONFIG_WIN] = [x,y,event.size().width(),event.size().height()]
        
    def moveEvent(self, event):
        # Update config
        x,y,w,h = self.__model[STATE][CONFIG_WIN]
        self.__model[STATE][CONFIG_WIN] = [event.pos().x(),event.pos().y(),w,h]
        
    def __do_save(self):
        # Save model
        persist.saveCfg(CONFIG_PATH, self.__model)
        # and hide window
        self.hide()
        
    def __do_cancel(self):
        # Reinstate model
        model.restore_model(self.__model)
        # and hide window
        self.hide()
        
    #======================================================= 
    def __idleProcessing   (self):
        # Update UI with actual progress
        if self.__tuner_status:
            self.__btn_tx_tst_pwm.setEnabled(True)
            self.__btn_ant_tst_pwm.setEnabled(True)
            self.__btn_ind_test.setEnabled(True)
        else:
            self.__btn_tx_tst_pwm.setEnabled(False)
            self.__btn_ant_tst_pwm.setEnabled(False)
            self.__btn_ind_test.setEnabled(False)
            
        # Set timer
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
        
    def __ip_changed(self):
        self.__model[CONFIG][RPi][IP] = self.__iptxt.text()
        
    def __rqst_port_changed(self):
        self.__model[CONFIG][RPi][RQST_PORT] = int(self.__txt_rqst_port.text())
    
    def __evnt_port_changed(self):
        self.__model[CONFIG][RPi][EVNT_PORT] = int(self.__txt_evnt_port.text())
        
    def __do_tx_set_pwm(self):
        self.__model[CONFIG][SERVO][TX_LOW_PWM] = self.__sb_tx_lower.value()
        self.__model[CONFIG][SERVO][TX_HIGH_PWM] = self.__sb_tx_upper.value()
    
    def __do_tx_test_range(self):
        self.__callback(CMD_TX_SERVO_SET_PWM, (self.__sb_tx_lower.value(), self.__sb_tx_upper.value()))
        self.__callback(CMD_TX_SERVO_TEST, ())
    
    def __do_ant_set_pwm(self):
        self.__model[CONFIG][SERVO][ANT_LOW_PWM] = self.__sb_ant_lower.value()
        self.__model[CONFIG][SERVO][ANT_HIGH_PWM] = self.__sb_ant_upper.value()
    
    def __do_ant_test_range(self):
        self.__callback(CMD_ANT_SERVO_SET_PWM, (self.__sb_ant_lower.value(), self.__sb_ant_upper.value()))
        self.__callback(CMD_ANT_SERVO_TEST, ())
            
    def __ind_changed(self):
        ind = self.__cb_ind.currentText()
        self.__cb_indmap.setCurrentIndex(self.__cb_indmap.findText(str(self.__model[CONFIG][RELAY][INDUCTOR_PINMAP][int(ind)-1])))    
        
    def __do_set_ind(self):
        # Set pinmap for this inductor tap
        tap = self.__cb_ind.currentText()
        pin = self.__cb_indmap.currentText()
        inv = self.__cb_inv.isChecked()
        self.__model[CONFIG][RELAY][INDUCTOR_PINMAP][int(tap)-1] =  int(pin)
        self.__model[CONFIG][RELAY][RELAY_INVERSE] = inv
    
    def __do_test_ind(self):
        # Test pinmap
        params = []
        inv = self.__model[CONFIG][RELAY][RELAY_INVERSE]
        for pin in self.__model[CONFIG][RELAY][INDUCTOR_PINMAP]:
            params.append((pin, inv))
            
        self.__callback(CMD_RELAYS_INIT, params)
        self.__callback(CMD_RELAYS_CYCLE, (params, 'exclusive'))
    
    def __do_servo_params(self):
        params = (
            self.__model[CONFIG][SERVO][TRACK_INC],
            self.__model[CONFIG][SERVO][TRACK_DELAY],
            self.__model[CONFIG][SERVO][SCAN_INC],
            self.__model[CONFIG][SERVO][SCAN_DELAY]
        )
        self.__callback(CMD_SERVO_SETTINGS, params)
    
#======================================================================================================================
# Test code
def main():
    
    try:
        # The one and only QApplication 
        qt_app = QApplication(sys.argv)
        # Crete instance
        config = Config()
        # Run application loop
        config.run()
        # Enter event loop
        qt_app.exec_()
               
    except Exception as e:
        print ('Exception [%s][%s]' % (str(e), traceback.format_exc()))
 
# Entry point       
if __name__ == '__main__':
    main()