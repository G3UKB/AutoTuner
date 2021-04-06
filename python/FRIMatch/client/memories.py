#!/usr/bin/env python3
#
# memories.py
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
# Memories window
class Memories(QMainWindow):
    
    def __init__(self, settings, callback):
        
        super(Memories, self).__init__()
        
        # Callback here to run memory
        self.__callback = callback
        # Call here to get current settings
        self.__settings = settings
        
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
        # Init table
        self.__restore_from_model()
        
        # Start idle processing
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
        
    #========================================================================================    
    # UI initialisation and window event handlers
    def initUI(self):
        """ Configure the GUI interface """
        
        self.setToolTip('Memories')
        
        # Arrange window
        x,y,w,h = model.auto_tune_model[STATE][MEM_WIN]
        self.setGeometry(x,y,w,h)
                         
        self.setWindowTitle('Memories')
        
        #=======================================================
        # Set main layout
        w = QWidget()
        self.setCentralWidget(w)
        self.__grid = QGridLayout()
        w.setLayout(self.__grid)
        
        # Table area
        self.__table = QTableWidget()
        self.__table.setColumnCount(5)
        self.__table.setHorizontalHeaderLabels(('Name','Freq','Inductor','TX Cap','Ant Cap'))
        self.__grid.addWidget(self.__table,0,0)
        self.__table.currentItemChanged.connect(self.__row_click)
        self.__table.doubleClicked.connect(self.__row_double_click)
    
        # Control area
        self.__ctrlgrid = QGridLayout()
        w1 = QGroupBox()
        w1.setLayout(self.__ctrlgrid)
        self.__grid.addWidget(w1, 1,0)
        
        # Run and remove
        self.__auxgrid = QGridLayout()
        w2 = QGroupBox()
        w2.setLayout(self.__auxgrid)
        self.__ctrlgrid.addWidget(w2, 0,0)

        self.__run = QPushButton("Run")
        self.__run.setToolTip('Execute memory')
        self.__auxgrid.addWidget(self.__run, 0,0)
        self.__run.clicked.connect(self.__do_run_mem)
        self.__run.setMaximumHeight(20)
        
        self.__remove = QPushButton("Remove")
        self.__remove.setToolTip('Remove memory')
        self.__auxgrid.addWidget(self.__remove, 0,1)
        self.__remove.clicked.connect(self.__do_remove_mem)
        self.__remove.setMaximumHeight(20)
        
        # Add with name and freq
        self.__detgrid = QGridLayout()
        w2 = QGroupBox()
        w2.setLayout(self.__detgrid)
        self.__ctrlgrid.addWidget(w2, 1,0)
        
        name_tag = QLabel("Name")
        self.__detgrid.addWidget(name_tag, 0,0)
        self.__nametxt = QLineEdit()
        self.__nametxt.setMinimumWidth(70)
        self.__detgrid.addWidget(self.__nametxt, 0,1)
        
        freq_tag = QLabel("Freq")
        self.__detgrid.addWidget(freq_tag, 0,2)
        self.__freqtxt = QLineEdit()
        self.__freqtxt.setMaximumWidth(50)
        self.__detgrid.addWidget(self.__freqtxt, 0,3)
        
        self.__add = QPushButton("Add")
        self.__add.setToolTip('Add new memory')
        self.__detgrid.addWidget(self.__add, 0,4)
        self.__add.clicked.connect(self.__do_add_mem)
        self.__add.setMaximumHeight(20)
        
        self.__update = QPushButton("Update")
        self.__update.setToolTip('Update memory')
        self.__detgrid.addWidget(self.__update, 0,5)
        self.__update.clicked.connect(self.__do_update_mem)
        self.__update.setMaximumHeight(20)
        
        # Exit
        self.__add = QPushButton("Exit")
        self.__add.setToolTip('Exit memories')
        self.__ctrlgrid.addWidget(self.__add, 2,0)
        self.__add.clicked.connect(self.__do_exit)
        self.__add.setMaximumHeight(20)
        
        
    #========================================================================================
    # PUBLIC procs
    
    def show_window(self):
        # Show our window
        self.show()
        self.repaint()
    
    def closeEvent(self, event):
        self.hide()

    #========================================================================================
    # EVENT procs
    
    def __idleProcessing(self):
        QtCore.QTimer.singleShot(IDLE_TICKER, self.__idleProcessing)
        
        if len(self.__nametxt.text()) > 0 and len(self.__freqtxt.text()) > 0:
            self.__nametxt.setEnabled(True)
            self.__freqtxt.setEnabled(True)
            
    def __do_add_mem(self):
        # Get data
        name = self.__nametxt.text()
        freq = self.__freqtxt.text()
        low,high,tx,ant = self.__settings()
        if low: ind = 'low-range'
        else: ind = 'high-range'
        # Create new row
        rowPosition = self.__table.rowCount()
        self.__table.insertRow(rowPosition)
        self.__table.setItem(rowPosition, 0, QTableWidgetItem(name))
        self.__table.setItem(rowPosition, 1, QTableWidgetItem(freq))
        self.__table.setItem(rowPosition, 2, QTableWidgetItem(ind))
        self.__table.setItem(rowPosition, 3, QTableWidgetItem(str(tx)))
        self.__table.setItem(rowPosition, 4, QTableWidgetItem(str(ant)))
        # Add to model
        self.__update_model()
    
    def __do_update_mem(self):
        # Get data
        name = self.__nametxt.text()
        freq = self.__freqtxt.text()
        low,high,tx,ant = self.__settings()
        if low: ind = 'low-range'
        else: ind = 'high-range'
        # Update row
        rowPosition = self.__table.currentRow()
        self.__table.setItem(rowPosition, 0, QTableWidgetItem(name))
        self.__table.setItem(rowPosition, 1, QTableWidgetItem(freq))
        self.__table.setItem(rowPosition, 2, QTableWidgetItem(ind))
        self.__table.setItem(rowPosition, 3, QTableWidgetItem(str(tx)))
        self.__table.setItem(rowPosition, 4, QTableWidgetItem(str(ant)))
        # Update model
        self.__update_model()
        
    def __do_run_mem(self):
        r = self.__table.currentRow()
        ind = self.__table.item(r, 2).text()
        tx = self.__table.item(r, 3).text()
        ant = self.__table.item(r, 4).text()
        # Execute tuner commands
        self.__callback(ind, tx, ant)
            
    def __do_remove_mem(self):
        r = self.__table.currentRow()
        self.__table.removeRow(r)
        # Remove from model
        self.__update_model()
    
    def __row_click(self):
        r = self.__table.currentRow()
        if r != -1:
            self.__nametxt.setText(self.__table.item(r, 0).text())
            self.__freqtxt.setText(self.__table.item(r, 1).text())
        
    def __row_double_click(self):
        self.__do_run_mem
        
    def __do_exit(self):
        self.hide()
        
    #========================================================================================
    # PRIVATE procs
    
    def __restore_from_model(self):
        # Populate table from model
        table_data = model.auto_tune_model[MEMORIES]
        for item in table_data:
            rowPosition = self.__table.rowCount()
            self.__table.insertRow(rowPosition)
            self.__table.setItem(rowPosition, 0, QTableWidgetItem(item[0]))
            self.__table.setItem(rowPosition, 1, QTableWidgetItem(item[1]))
            self.__table.setItem(rowPosition, 2, QTableWidgetItem(item[2]))
            self.__table.setItem(rowPosition, 3, QTableWidgetItem(item[3]))
            self.__table.setItem(rowPosition, 4, QTableWidgetItem(item[4]))
        
    def __update_model(self):
        # Clear and re-populate from table
        model.auto_tune_model[MEMORIES].clear()
        entry = []
        rowCount = self.__table.rowCount()
        for row in range(rowCount):
            entry = [
                self.__table.item(row, 0).text(),
                self.__table.item(row, 1).text(),
                self.__table.item(row, 2).text(),
                self.__table.item(row, 3).text(),
                self.__table.item(row, 4).text(),
            ]
            model.auto_tune_model[MEMORIES].append(entry)
        