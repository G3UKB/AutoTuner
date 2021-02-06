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
    
    def __init__(self):
        
        super(Config, self).__init__()
        
        # Set the back colour
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtGui.QColor(195,195,195,255))
        self.setPalette(palette)
        
        # Initialise the GUI
        self.initUI()
        self.show()
        self.repaint()
    
    #========================================================================================    
    # UI initialisation and window event handlers
    def initUI(self):
        """ Configure the GUI interface """
        
        self.setToolTip('Configuration')
        
        # Arrange window
        self.setGeometry(300,300,300,200)
                         
        self.setWindowTitle('Configure Auto-Tuner')
        
        #=======================================================
        # Set main layout
        w = QWidget()
        self.setCentralWidget(w)
        self.__grid = QGridLayout()
        w.setLayout(self.__grid)
        
        # Within this we need 3 sub-layouts
        self.__span_grid = QGridLayout()
        w1 = QWidget()
        w1.setLayout(self.__span_grid)
        self.__grid.addWidget(w1, 0,0)
        
        self.__map_grid = QGridLayout()
        w2 = QWidget()
        w2.setLayout(self.__map_grid)
        self.__grid.addWidget(w2, 1,0)
        
        self.__op_grid = QGridLayout()
        w3 = QWidget()
        w3.setLayout(self.__op_grid)
        self.__grid.addWidget(w3, 2,0)
        
        # Populate grids
        self.__pop_span(self.__span_grid)
        self.__pop_map(self.__map_grid)
        self.__pop_op(self.__op_grid)
        
    #-------------------------------------------------------------
    # Set the servo limits to achieve 0-180 degrees rotation
    def __pop_span(self, g):
        
        # We need two fields for PWM values
        # and two buttons for execution
        
        # Values for PWM upper and lower
        lower_lbl = QLabel("Low PWM")
        upper_lbl = QLabel("High PWM")
        self.__sb_lower = QSpinBox()
        self.__sb_lower.setRange(500, 3000)
        self.__sb_lower.setValue(0)
        self.__sb_upper = QSpinBox()
        self.__sb_upper.setRange(500, 3000)
        self.__sb_upper.setValue(1000)
        g.addWidget(lower_lbl, 0,0)
        g.addWidget(self.__sb_lower, 0,1)
        g.addWidget(upper_lbl, 1,0)
        g.addWidget(self.__sb_upper, 1,1)
        # Activation buttons
        self.__btn_set_pwm = QPushButton("Set")
        g.addWidget(self.__btn_set_pwm, 2,0)
        self.__btn_set_pwm.clicked.connect(self.__do_set_pwm)
        self.__btn_tst_pwm = QPushButton("Test")
        g.addWidget(self.__btn_tst_pwm, 2,1)
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
        g.addWidget(cap_lbl, 0,0)
        g.addWidget(self.__cb_cap, 0,1)
        g.addWidget(self.__cb_capmap, 0,2)
        g.addWidget(self.__btn_cap, 0,3)
        self.__btn_cap.clicked.connect(self.__do_set_cap)
        
        # Inductor
        ind_lbl = QLabel("Ind Pinmap")
        self.__cb_ind = QComboBox()
        self.__cb_ind.addItems(g_ind_values)
        self.__cb_indmap = QComboBox()
        self.__cb_indmap.addItems(g_pins)
        self.__btn_ind = QPushButton("Set")
        g.addWidget(ind_lbl, 1,0)
        g.addWidget(self.__cb_ind, 1,1)
        g.addWidget(self.__cb_indmap, 1,2)
        g.addWidget(self.__btn_ind, 1,3)
        self.__btn_ind.clicked.connect(self.__do_set_ind)
        
        # Inductor separator
        sep_lbl = QLabel("Ind Sep")
        self.__cb_indsep = QComboBox()
        self.__cb_indsep.addItems(g_pins)
        self.__btn_sep = QPushButton("Set")
        g.addWidget(sep_lbl, 2,0)
        g.addWidget(self.__cb_indsep, 2,1)
        g.addWidget(self.__btn_sep, 2,3)
        self.__btn_ind.clicked.connect(self.__do_set_sep)
        
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
        g.addWidget(self.__cb_band, 0,1)
        
        # Variable capacitor
        #variable_cap_lbl = QLabel("Variable degrees")
        #g.addWidget(variable_cap_lbl, 1,0)
        #self.__sb_cap_degrees = QSpinBox()
        #self.__sb_cap_degrees.setRange(0, 180)
        #self.__sb_cap_degrees.setValue(90)
        #g.addWidget(self.__sb_cap_degrees, 1,1)
        
        # Variable capacitor
        cap_lbl = QLabel("Variable Cap")
        g.addWidget(cap_lbl, 1,0)
        self.__sld_cap = QSlider(QtCore.Qt.Horizontal)
        self.__sld_cap.setMinimum(0)
        self.__sld_cap.setMaximum(180)
        self.__sld_cap.setValue(0)
        g.addWidget(self.__sld_cap, 1,1)
        self.__sld_cap.valueChanged.connect(self.__cap_changed)
        self.__sld_cap_val = QLabel("0")
        self.__sld_cap_val.setMinimumWidth(30)
        self.__sld_cap_val.setStyleSheet("color: green; font: 14px")
        g.addWidget(self.__sld_cap_val, 1,2)
        self.__sld_cap_actual = QLabel("0")
        self.__sld_cap_actual.setMinimumWidth(30)
        self.__sld_cap_actual.setStyleSheet("color: red; font: 14px")
        g.addWidget(self.__sld_cap_actual, 1,3)
        
        # Extra capacitance
        variable_cap_lbl = QLabel("Extra capacitance")
        g.addWidget(variable_cap_lbl, 2,0)
        self.__cb_cap_extra = QComboBox()
        self.__cb_cap_extra.addItems(g_cap_extra_values)
        g.addWidget(self.__cb_cap_extra, 2,1)
        
        
        # Inductor tap
        variable_ind_lbl = QLabel("Inductor tap")
        g.addWidget(variable_ind_lbl, 3,0)
        self.__cb_ind_tap = QComboBox()
        self.__cb_ind_tap.addItems(g_ind_values)
        g.addWidget(self.__cb_ind_tap, 3,1)
    
        self.__btn_tst_band = QPushButton("Test")
        g.addWidget(self.__btn_tst_band, 4,0)
        self.__btn_tst_band.clicked.connect(self.__do_band_test)
        
        self.__btn_save = QPushButton("Save")
        g.addWidget(self.__btn_save, 4,1)
        self.__btn_save.clicked.connect(self.__do_save)
    
    
    #========================================================================================
    # Event procs
    def __do_set_pwm(self):
        print ("__do_set_pwm")
    
    def __do_test_range(self):
        print ("__do_test_range")
        
    def __cap_changed(self):
        print ("__do_test_range")    
    
    def __do_set_cap(self):
        print ("__do_set_cap")
    
    def __do_set_ind(self):
        print ("__do_set_ind")
    
    def __do_set_sep(self):
        print ("__do_set_sep")
        
    def __do_band_test(self):
        print ("__do_band_set")
    
    def __do_save(self):
        print ("__do_save")
        
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