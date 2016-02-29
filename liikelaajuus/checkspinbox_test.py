# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 18:56:52 2016

@author: jussi
"""

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore

class MyQSpinBox(QSpinBox):

    def __init__(self):
        super(self.__class__, self).__init__()
        print('jee!')
    
    def Enter(self, event):
        print('enter')
        self.clear()
        QSpinBox.Enter(self, event)


class CheckDegSpinBox(QtGui.QWidget):
    """ Custom widget: Spinbox (degrees) with checkbox signaling "normal value".
    If checkbox is checked, disable spinbox -> value() returns 'NR'
    If not, value() returns spinbox value. 
    setValue() takes either NR, the 'special value' (not measured) or integer.
    """
    # signal has to be defined here for unclear reasons
    # note that currently the value is not returned by the signal
    # (unlike in the Qt spinbox)
    valueChanged = QtCore.pyqtSignal()  
    
    def __init__(self):
      
        super(self.__class__, self).__init__()
            
        normalLabel = QtGui.QLabel(u'NR')
        self.normalCheckBox = QtGui.QCheckBox()
        self.normalval = u'NR'
        self.normalCheckBox.stateChanged.connect(lambda st: self.toggleSpinBox(st))
        
        self.degSpinBox = QtGui.QSpinBox()
        self.degSpinBox.setRange(-1, 180.0)
        self.degSpinBox.setValue(-1)
        self.degSpinBox.setSuffix(u'°')
        self.specialtext = u'Ei mitattu'
        self.degSpinBox.setSpecialValueText(self.specialtext)
        self.degSpinBox.valueChanged.connect(self.valueChanged.emit)
        self.degSpinBox.setMinimumSize(100,0)
        # default text
         
        layout = QtGui.QGridLayout(self)
        layout.addWidget(normalLabel, 0, 0)
        layout.addWidget(self.normalCheckBox, 0, 1)
        layout.addWidget(self.degSpinBox, 0, 2)

    def value(self):
        if self.normalCheckBox.checkState() == 0:
            val = self.degSpinBox.value()
            if val == self.degSpinBox.minimum():
                return self.specialtext
            else:
                return val
        elif self.normalCheckBox.checkState() == 2:
            return self.normalval

    def setValue(self, val):
        if val == self.normalval:
            self.degSpinBox.setEnabled(False)
            self.normalCheckBox.setCheckState(2)
        else:
            self.normalCheckBox.setCheckState(0)
            if val == self.specialtext:
                self.degSpinBox.setValue(self.degSpinBox.minimum())
            else:
                self.degSpinBox.setValue(val)
    
    def toggleSpinBox(self, st):
        """ Enables or disables spinbox input according to st. Also emit
        valueChanged signal """
        self.degSpinBox.setEnabled(not st)
        self.valueChanged.emit()
        
    #def sizeHint(self):
    #    return QSize(150,20)
        

class spindemo(QWidget):
   def __init__(self, parent = None):
      super(spindemo, self).__init__(parent)
      
      layout = QVBoxLayout()
      self.sp1 = CheckDegSpinBox()
      self.sp2 = CheckDegSpinBox()
      self.btn = QPushButton()
      layout.addWidget(self.sp1)
      layout.addWidget(self.sp2)
      layout.addWidget(self.btn)
      self.btn.clicked.connect(self.settest)
      self.sp1.valueChanged.connect(self.printval)      
      self.sp2.valueChanged.connect(self.printval)      
      self.setLayout(layout)
      self.setWindowTitle("SpinBox demo")
		
   def printval(self):
      print("current value:"+str(self.sp1.value()))

   def settest(self):
       self.sp1.setValue(u'Ei mitattu')
       


def main():
   app = QApplication(sys.argv)
   ex = spindemo()
   ex.show()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()



   