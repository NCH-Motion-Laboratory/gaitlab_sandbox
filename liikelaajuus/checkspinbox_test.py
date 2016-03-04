# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 18:56:52 2016

@author: jussi
"""

import sys
from PyQt4 import QtGui, QtCore
from liikelaajuus import CheckDegSpinBox


        

class spindemo(QtGui.QWidget):
   def __init__(self, parent = None):
      super(spindemo, self).__init__(parent)
      
      layout = QtGui.QVBoxLayout()
      self.sp1 = CheckDegSpinBox()
      self.sp1.defaultText = u'foo'
      self.btn = QtGui.QPushButton()
      layout.addWidget(self.sp1)
      layout.addWidget(self.btn)
      self.btn.clicked.connect(self.settest)
      self.sp1.valueChanged.connect(self.printval)      
      self.setLayout(layout)
      self.setWindowTitle("SpinBox demo")
		
   def printval(self):
      print("current value:"+str(self.sp1.value()))

   def settest(self):
       self.sp1.setValue(u'Ei mitattu')
       


def main():
   app =QtGui.QApplication(sys.argv)
   ex = spindemo()
   ex.show()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()



   