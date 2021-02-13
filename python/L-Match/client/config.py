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
    
    def __init__(self, callback):
        
        super(Config, self).__init__()
        
        self.__callback = callback
        self.__progress = 0
        
        # Set the back colour
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtGui.QColor(195,195,195,255))
        self.setPalette(palette)
        
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
        self.setGeometry(300,300,300,300)
                         
        self.setWindowTitle('Configure Auto-Tuner')
        
        #=======================================================
        # Set main layout
        w = QWidget()
        self.setCentralWidget(w)
        self.__grid = QGridLayout()
        w.setLayout(self.__grid)
        
        # Within this we need 4 sub-layouts
        self.__rpi_grid = QGridLayout()
        w1 = QGroupBox('RPi Config')
        w1.setLayout(self.__rpi_grid)
        self.__grid.addWidget(w1, 0,0)
        
        self.__span_grid = QGridLayout()
        w2 = QGroupBox('Servo Config')
        w2.setLayout(self.__span_grid)
        self.__grid.addWidget(w2, 1,0)
        
        self.__map_grid = QGridLayout()
        w3 = QGroupBox('GPIO Config')
        w3.setLayout(self.__map_grid)
        self.__grid.addWidget(w3, 2,0)
        
        self.__op_grid = QGridLayout()
        w4 = QGroupBox('Tuner Config')
        w4.setLayout(self.__op_grid)
        self.__grid.addWidget(w4, 3,0)
        
        # Populate grids
        self.__rpi(self.__rpi_grid)
        self.__pop_span(self.__span_grid)
        self.__pop_map(self.__map_grid)
        self.__pop_op(self.__op_grid)
        
        # Close
        self.__btn_close = QPushButton("Close")
        self.__grid.addWidget(self.__btn_close, 4,0)
        self.__btn_close.clicked.connect(self.__do_close)
    
    #-------------------------------------------------------------
    # Set the RPi network config
    def __rpi(self, g):
        
        # We need the Ip and port
        
        ip_lbl = QLabel("RPi IP Address")
        g.addWidget(ip_lbl, 0, 0)
        port_lbl = QLabel("Listen on port")
        g.addWidget(port_lbl, 1, 0)
        
        self.__iptxt = QLineEdit()
        self.__iptxt.setInputMask('000.000.000.000;_')
        self.__iptxt.setMaximumWidth(100)
        g.addWidget(self.__iptxt, 0, 1)
        self.__iptxt.setText(model.auto_tune_model[CONFIG][RPi][IP])
        self.__iptxt.editingFinished.connect(self.__ip_changed)
        
        self.__porttxt = QLineEdit()
        self.__porttxt.setInputMask('00000;_')
        self.__porttxt.setMaximumWidth(100)
        g.addWidget(self.__porttxt, 1, 1)
        self.__porttxt.setText(str(model.auto_tune_model[CONFIG][RPi][RQST_PORT]))
        self.__porttxt.editingFinished.connect(self.__port_changed)
        
    #-------------------------------------------------------------
    # Set the servo limits to achieve 0-180 degrees rotation
    def __pop_span(self, g):
        
        # We need two fields for PWM values
        # and two buttons for execution
        
        # Values for PWM upper and lower
        lower_lbl = QLabel("Low PWM")
        upper_lbl = QLabel("High PWM")
        self.__sb_lower = QSpinBox()
        self.__sb_lower.setRange(0, 3000)
        self.__sb_lower.setValue(model.auto_tune_model[CONFIG][LOW_PWM])
        self.__sb_upper = QSpinBox()
        self.__sb_upper.setRange(0, 3000)
        self.__sb_upper.setValue(model.auto_tune_model[CONFIG][HIGH_PWM])
        g.addWidget(lower_lbl, 0,0)
        g.addWidget(self.__sb_lower, 0,1,1,2)
        g.addWidget(upper_lbl, 1,0)
        g.addWidget(self.__sb_upper, 1,1,1,2)
        # Activation buttons
        self.__btn_set_pwm = QPushButton("Set")
        g.addWidget(self.__btn_set_pwm, 2,1)
        self.__btn_set_pwm.clicked.connect(self.__do_set_pwm)
        self.__btn_tst_pwm = QPushButton("Test")
        g.addWidget(self.__btn_tst_pwm, 2,2)
        self.__btn_tst_pwm.clicked.connect(self.__do_test_range)
        
    #-------------------------------------------------------------
    # Set the pin maps for capacitor values and inductor taps
    def __pop_map(self, g):
        
        # We need two sets of pin allocations
        # for capacitor and inductor connections
        
        # Capacitor
        cap_lbl = QLabel("Cap pinmap")
        self.__cb_cap = QComboBox()
        self.__cb_cap.addItems(g_cap_values)
        self.__cb_capmap = QComboBox()
        self.__cb_capmap.addItems(g_pins)
        self.__btn_cap = QPushButton("Set")
        self.__btn_cap.setMaximumWidth(60)
        self.__btn_cap_test = QPushButton("Test")
        self.__btn_cap_test.setMaximumWidth(60)
        g.addWidget(cap_lbl, 0,0)
        g.addWidget(self.__cb_cap, 0,1)
        g.addWidget(self.__cb_capmap, 0,2)
        g.addWidget(self.__btn_cap, 0,3)
        g.addWidget(self.__btn_cap_test, 0,4)
        self.__cb_cap.currentIndexChanged.connect(self.__cap_changed)
        self.__btn_cap.clicked.connect(self.__do_set_cap)
        self.__btn_cap_test.clicked.connect(self.__do_test_extra_cap)
        self.__cb_cap.setCurrentIndex(0)
        self.__cb_capmap.setCurrentIndex(self.__cb_capmap.findText(str(model.auto_tune_model[CONFIG][CAP_PINMAP][1000][0])))
        
        # Inductor
        ind_lbl = QLabel("Ind Pinmap")
        self.__cb_ind = QComboBox()
        self.__cb_ind.addItems(g_ind_values)
        self.__cb_indmap = QComboBox()
        self.__cb_indmap.addItems(g_pins)
        self.__btn_ind = QPushButton("Set")
        self.__btn_ind.setMaximumWidth(60)
        self.__btn_ind_test = QPushButton("Test")
        self.__btn_ind_test.setMaximumWidth(60)
        g.addWidget(ind_lbl, 1,0)
        g.addWidget(self.__cb_ind, 1,1)
        g.addWidget(self.__cb_indmap, 1,2)
        g.addWidget(self.__btn_ind, 1,3)
        g.addWidget(self.__btn_ind_test, 1,4)
        self.__cb_ind.currentIndexChanged.connect(self.__ind_changed)
        self.__btn_ind.clicked.connect(self.__do_set_ind)
        self.__btn_ind_test.clicked.connect(self.__do_test_ind)
        self.__cb_ind.setCurrentIndex(0)
        self.__cb_indmap.setCurrentIndex(self.__cb_indmap.findText(str(model.auto_tune_model[CONFIG][IND_PINMAP][1])))
        
        # Inductor separator
        sep_lbl = QLabel("Ind Sep")
        self.__cb_indsep = QComboBox()
        self.__cb_indsep.addItems(g_pins)
        self.__btn_sep = QPushButton("Set")
        self.__btn_sep.setMaximumWidth(60)
        self.__btn___cb_indsep_test = QPushButton("Test")
        self.__btn___cb_indsep_test.setMaximumWidth(60)
        g.addWidget(sep_lbl, 2,0)
        g.addWidget(self.__cb_indsep, 2,2)
        g.addWidget(self.__btn_sep, 2,3)
        g.addWidget(self.__btn___cb_indsep_test, 2,4)
        self.__btn_ind.clicked.connect(self.__do_set_sep)
        self.__btn_ind_test.clicked.connect(self.__do_test_indsep)
        self.__cb_indsep.setCurrentIndex(self.__cb_indsep.findText(str(model.auto_tune_model[CONFIG][IND_TOGGLE])))
        
    #-------------------------------------------------------------
    # Set the inductor tap and capacitor value for each band
    def __pop_op(self, g):
        
        # We need a band combo against capacitor degrees and extra pf
        # plus the inductor tap
        
        # Bands
        band_lbl = QLabel("Band")
        self.__cb_band = QComboBox()
        self.__cb_band.addItems(g_band_values)
        g.addWidget(band_lbl, 0,0)
        g.addWidget(self.__cb_band, 0,1,1,2)
        self.__cb_band.currentIndexChanged.connect(self.__band_changed)
        
        # Slider labels
        setpoint_tag = QLabel("Set")
        g.addWidget(setpoint_tag, 1,4)
        actual_tag = QLabel("Act")
        g.addWidget(actual_tag, 1,5)
        
        # Variable capacitor
        cap_lbl = QLabel("Var Cap")
        g.addWidget(cap_lbl, 2,0)
        self.__sld_cap = QSlider(QtCore.Qt.Horizontal)
        self.__sld_cap.setMinimum(0)
        self.__sld_cap.setMaximum(180)
        self.__sld_cap.setValue(0)
        g.addWidget(self.__sld_cap, 2,1,1,2)
        
        self.__chb_cap = QCheckBox('Live')
        g.addWidget(self.__chb_cap, 2,3)
        
        self.__sld_cap.valueChanged.connect(self.__cap_var_changed)
        self.__sld_cap_val = QLabel("0")
        self.__sld_cap_val.setMinimumWidth(25)
        self.__sld_cap_val.setStyleSheet("color: green; font: 14px")
        g.addWidget(self.__sld_cap_val, 2,4)
        self.__sld_cap_actual = QLabel("0")
        self.__sld_cap_actual.setMinimumWidth(25)
        self.__sld_cap_actual.setStyleSheet("color: red; font: 14px")
        g.addWidget(self.__sld_cap_actual, 2,5)
        
        # Extra capacitance
        variable_cap_lbl = QLabel("Plus Cap")
        g.addWidget(variable_cap_lbl, 3,0)
        self.__cb_cap_extra = QComboBox()
        self.__cb_cap_extra.addItems(g_cap_extra_values)
        g.addWidget(self.__cb_cap_extra, 3,1,1,2)
        self.__cb_cap_extra.setCurrentIndex(0)
        
        # Inductor tap
        variable_ind_lbl = QLabel("Ind tap")
        g.addWidget(variable_ind_lbl, 4,0)
        self.__cb_ind_tap = QComboBox()
        self.__cb_ind_tap.addItems(g_ind_values)
        g.addWidget(self.__cb_ind_tap, 4,1,1,2)
        self.__cb_ind_tap.setCurrentIndex(0)
        
        cap, extra, tap = model.auto_tune_model[CONFIG][BAND][160]
        self.__sld_cap.setValue(cap)
        self.__cb_cap_extra.setCurrentIndex(self.__cb_cap_extra.findText(str(extra)))
        self.__cb_ind_tap.setCurrentIndex(self.__cb_ind_tap.findText(str(tap)))
        
        self.__btn_tst_band = QPushButton("Set")
        g.addWidget(self.__btn_tst_band, 5,1)
        self.__btn_tst_band.clicked.connect(self.__do_band_set)
        
        self.__btn_save = QPushButton("Test")
        g.addWidget(self.__btn_save, 5,2)
        self.__btn_save.clicked.connect(self.__do_band_test)
    
    #========================================================================================
    # Event procs
    def progress(self, progress):
        self.__progress = progress
        
    #========================================================================================
    # Event procs
    
    #======================================================= 
    def __idleProcessing   (self):
        # Update UI with actual progress
        self.__sld_cap_actual.setText(str(self.__progress))
        # Set timer
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
        
    def __ip_changed(self):
        model.auto_tune_model[CONFIG][RPi][IP] = self.__iptxt.text()
        
    def __port_changed(self):
        model.auto_tune_model[CONFIG][RPi][RQST_PORT] = int(self.__porttxt.text())
        
    def __do_set_pwm(self):
        self.__callback(CMD_SERVO_SET_PWM, (self.__sb_lower.value(), self.__sb_upper.value()))
        model.auto_tune_model[CONFIG][LOW_PWM] = self.__sb_lower.value()
        model.auto_tune_model[CONFIG][HIGH_PWM] = self.__sb_upper.value()
    
    def __do_test_range(self):
        self.__callback(CMD_SERVO_TEST, ())
        
    def __cap_changed(self):
        cap = self.__cb_cap.currentText()
        self.__cb_capmap.setCurrentIndex(self.__cb_capmap.findText(str(model.auto_tune_model[CONFIG][CAP_PINMAP][int(cap)][-1])))    
    
    def __do_set_cap(self):
        # Set pinmap for this capacitor value
        cap = self.__cb_cap.currentText()
        pin = self.__cb_capmap.currentText()
        pin_1000 = model.auto_tune_model[CONFIG][CAP_PINMAP][1000]
        pin_2000 = model.auto_tune_model[CONFIG][CAP_PINMAP][2000]
        if cap == '1000':
            model.auto_tune_model[CONFIG][CAP_PINMAP][1000] = [int(pin),]
        elif cap == '2000':
            model.auto_tune_model[CONFIG][CAP_PINMAP][2000] = pin_1000 + [int(pin),]
        elif cap == '3000':
            model.auto_tune_model[CONFIG][CAP_PINMAP][3000] = pin_2000 + [int(pin),]
            
    def __do_test_extra_cap(self):
        self.__callback(CMD_RELAYS_INIT, (model.auto_tune_model[CONFIG][CAP_PINMAP][3000]))
        self.__callback(CMD_RELAYS_CYCLE, (model.auto_tune_model[CONFIG][CAP_PINMAP][3000]))
                        
    def __ind_changed(self):
        ind = self.__cb_ind.currentText()
        self.__cb_indmap.setCurrentIndex(self.__cb_indmap.findText(str(model.auto_tune_model[CONFIG][IND_PINMAP][int(ind)])))    
    
    def __do_set_ind(self):
        # Set pinmap for this inductor tap
        tap = self.__cb_ind.currentText()
        pin = self.__cb_indmap.currentText()
        model.auto_tune_model[CONFIG][IND_PINMAP][int(tap)] = int(pin)
        
    def __do_test_ind(self):
        self.__callback(CMD_RELAYS_INIT, list((model.auto_tune_model[CONFIG][IND_PINMAP].values())))
        self.__callback(CMD_RELAYS_CYCLE, list((model.auto_tune_model[CONFIG][IND_PINMAP].values())))
    
    def __do_set_sep(self):
        # Set pinmap for the inductor separator
        pin = self.__cb_indsep.currentText()
        model.auto_tune_model[CONFIG][IND_TOGGLE] = int(pin)
    
    def __do_test_indsep(self):
        self.__callback(CMD_RELAYS_SET, (model.auto_tune_model[CONFIG][IND_TOGGLE]))
    
    def __cap_var_changed(self):
        val = self.__sld_cap.value()
        self.__sld_cap_val.setText(str(val))
        if self.__chb_cap.isChecked():
            self.__callback(CMD_SERVO_MOVE, (int(val),)) 
    
    def __band_changed(self):
        band = self.__cb_band.currentText()
        cap, extra, tap = model.auto_tune_model[CONFIG][BAND][int(band)]
        self.__sld_cap.setValue(cap)
        self.__cb_cap_extra.setCurrentIndex(self.__cb_cap_extra.findText(str(extra)))
        self.__cb_ind_tap.setCurrentIndex(self.__cb_ind_tap.findText(str(tap)))
        
    def __do_band_set(self):
        band = self.__cb_band.currentText()
        cap = self.__sld_cap.value()
        extra = self.__cb_cap_extra.currentText()
        tap = self.__cb_ind_tap.currentText()
        model.auto_tune_model[CONFIG][BAND][int(band)] = [int(cap),int(extra),int(tap)]
        
    def __do_band_test(self):
        # Test for the current band
        # Do a complete relay init
        self.__callback(CMD_RELAYS_INIT, (model.auto_tune_model[CONFIG][CAP_PINMAP][3000]))
        self.__callback(CMD_RELAYS_INIT, list((model.auto_tune_model[CONFIG][IND_PINMAP].values())))
        self.__callback(CMD_RELAYS_INIT, [model.auto_tune_model[CONFIG][IND_TOGGLE],])
        # Get parameters
        band = self.__cb_band.currentText()
        cap = self.__sld_cap.value()
        extra = self.__cb_cap_extra.currentText()
        tap = self.__cb_ind_tap.currentText()
        # Set parameters
        self.__callback(CMD_RELAYS_SET, model.auto_tune_model[CONFIG][CAP_PINMAP][int(extra)])
        self.__callback(CMD_RELAYS_SET, [model.auto_tune_model[CONFIG][IND_PINMAP][int(tap)],])
        self.__callback(CMD_SERVO_MOVE, (cap,))
    
    def __do_close(self):
        self.hide()
        
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