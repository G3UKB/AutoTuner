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
        
        # Populate grids
        self.__rpi(self.__rpi_grid)
        self.__pop_span(self.__span_grid)
        self.__pop_map(self.__map_grid)
        
        # Control buttons
        self.__cntrl_grid = QGridLayout()
        w4 = QWidget()
        w4.setLayout(self.__cntrl_grid)
        self.__grid.addWidget(w4, 4,0)
        
        self.__btn_save = QPushButton("Save")
        self.__cntrl_grid.addWidget(self.__btn_save, 0,0)
        self.__btn_save.setToolTip('Save configuration and close window')
        self.__btn_save.clicked.connect(self.__do_save)
        self.__btn_cancel = QPushButton("Cancel")
        self.__btn_cancel.setToolTip('Cancel changes and close window')
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
        
        # Values for PWM upper and lower
        lower_lbl = QLabel("Low PWM")
        upper_lbl = QLabel("High PWM")
        self.__sb_lower = QSpinBox()
        self.__sb_lower.setRange(0, 3000)
        self.__sb_lower.setToolTip('Lower bound of PWM range')
        self.__sb_upper = QSpinBox()
        self.__sb_upper.setRange(0, 3000)
        self.__sb_upper.setToolTip('Upper bound of PWM range')
        g.addWidget(lower_lbl, 0,0)
        g.addWidget(self.__sb_lower, 0,1)
        g.addWidget(upper_lbl, 0,2)
        g.addWidget(self.__sb_upper, 0,3)
        # Activation buttons
        self.__btn_set_pwm = QPushButton("Set")
        self.__btn_set_pwm.setMaximumWidth(60)
        self.__btn_set_pwm.setToolTip('Set range')
        g.addWidget(self.__btn_set_pwm, 0,4)
        self.__btn_set_pwm.clicked.connect(self.__do_set_pwm)
        self.__btn_tst_pwm = QPushButton("Test")
        self.__btn_tst_pwm.setToolTip('Test range, moves 0-180-0')
        self.__btn_tst_pwm.setMaximumWidth(60)
        g.addWidget(self.__btn_tst_pwm, 0,5)
        self.__btn_tst_pwm.clicked.connect(self.__do_test_range)
        
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
    # Initialise all fields
    def __init_fields(self):
        self.__iptxt.setText(model.auto_tune_model[CONFIG][RPi][IP])
        self.__txt_rqst_port.setText(str(model.auto_tune_model[CONFIG][RPi][RQST_PORT]))
        self.__txt_evnt_port.setText(str(model.auto_tune_model[CONFIG][RPi][EVNT_PORT]))
        self.__sb_lower.setValue(model.auto_tune_model[CONFIG][LOW_PWM])
        self.__sb_upper.setValue(model.auto_tune_model[CONFIG][HIGH_PWM])
        
        self.__cb_ind.setCurrentIndex(0)
        self.__cb_indmap.setCurrentIndex(self.__cb_indmap.findText(str(model.auto_tune_model[CONFIG][INDUCTOR_PINMAP][0])))
        
        self.__cb_inv.setChecked(model.auto_tune_model[CONFIG][RELAY_INVERSE])
        
    #========================================================================================
    # PUBLIC procs
    
    def show_window(self):
        
        # Make a copy of the current model
        model.copy_model()
        
        # (Re)populate everything
        self.__init_fields()
        
        # Show our window
        self.show()
        self.repaint()
        
    def progress(self, progress):
        self.__progress = progress
        
    #========================================================================================
    # Event procs
    
    def __do_save(self):
        # Save the model
        persist.saveCfg(CONFIG_PATH, model.auto_tune_model)
        self.hide()
        
    def __do_cancel(self):
        model.restore_model()
        self.hide()
        
    #======================================================= 
    def __idleProcessing   (self):
        # Update UI with actual progress
        #self.__sld_cap_actual.setText(str(self.__progress))
        # Set timer
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
        
    def __ip_changed(self):
        model.auto_tune_model[CONFIG][RPi][IP] = self.__iptxt.text()
        
    def __rqst_port_changed(self):
        model.auto_tune_model[CONFIG][RPi][RQST_PORT] = int(self.__txt_rqst_port.text())
    
    def __evnt_port_changed(self):
        model.auto_tune_model[CONFIG][RPi][EVNT_PORT] = int(self.__txt_evnt_port.text())
        
    def __do_set_pwm(self):
        model.auto_tune_model[CONFIG][LOW_PWM] = self.__sb_lower.value()
        model.auto_tune_model[CONFIG][HIGH_PWM] = self.__sb_upper.value()
    
    def __do_test_range(self):
        self.__callback(CMD_SERVO_SET_PWM, (self.__sb_lower.value(), self.__sb_upper.value()))
        self.__callback(CMD_SERVO_TEST, ())
                            
    def __ind_changed(self):
        ind = self.__cb_ind.currentText()
        self.__cb_indmap.setCurrentIndex(self.__cb_indmap.findText(str(model.auto_tune_model[CONFIG][IND_PINMAP][int(ind)][0])))    
        self.__chb_indmap.setChecked(model.auto_tune_model[CONFIG][IND_PINMAP][int(ind)][1])
        
    def __do_set_ind(self):
        # Set pinmap for this inductor tap
        tap = self.__cb_ind.currentText()
        pin = self.__cb_indmap.currentText()
        inv = self.__cb_inv.isChecked()
        model.auto_tune_model[CONFIG][INDUCTOR_PINMAP][int(tap)] = int(pin)
        model.auto_tune_model[CONFIG][RELAY_INVERSE] = inv
    
    def __do_test_ind(self):
        pass
    
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