# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 18:56:52 2016

@author: jussi
"""

from __future__ import print_function
import sys
from PyQt4 import QtGui, QtCore
from liikelaajuus import CheckDegSpinBox


        

class spindemo(QtGui.QWidget):
   def __init__(self, parent = None):
      super(spindemo, self).__init__(parent)
      
      layout = QtGui.QVBoxLayout()
      self.sp1 = CheckDegSpinBox()
      self.sp2 = CheckDegSpinBox()
      #self.sp1.defaultText = u'foo'
      self.btn = QtGui.QPushButton('test')
      #layout.addWidget(self.sp1)
      layout.addWidget(self.btn)
      layout.addWidget(self.sp1)
      layout.addWidget(self.sp2)
      self.btn.clicked.connect(self.settest)
      #self.sp1.valueChanged.connect(self.printval)
      #self.sp1.setSuffix(u'mm')
      self.setLayout(layout)
      self.setWindowTitle("SpinBox demo")
		
   def printval(self):
      print("current value:"+str(self.sp1.value()))
      
   def exc(self):
       raise Exception
       
   def settest(self):
       #try:
       pass
       #self.exc()
       #except Exception:
        #   print('caught')
       

       
       #print(self.sp1.defaultText())
       #print(self.sp1.getSuffix())       
       

def main():

    app = QtGui.QApplication(sys.argv)
    ex = spindemo()

    def my_excepthook(type, value, tback):
        print('Horrible things have happened:', type, value)
        sys.__excepthook__(type, value, tback) 
        app.quit()
        
    sys.excepthook = my_excepthook
    
    ex.show()
    app.exec_()
	
if __name__ == '__main__':
   main()



   