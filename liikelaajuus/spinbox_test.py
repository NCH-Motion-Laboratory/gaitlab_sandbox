# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 18:56:52 2016

@author: jussi
"""

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MyQSpinBox(QSpinBox):

    def __init__(self):
        super(self.__class__, self).__init__()
        print('jee!')
    
    def Enter(self, event):
        print('enter')
        self.clear()
        QSpinBox.Enter(self, event)

class spindemo(QWidget):
   def __init__(self, parent = None):
      super(spindemo, self).__init__(parent)
      
      layout = QVBoxLayout()
      self.l1 = QLabel("current value:")
      self.l1.setAlignment(Qt.AlignCenter)
      layout.addWidget(self.l1)
      self.sp = MyQSpinBox()
      self.btn = QPushButton()
      #self.btn.clicked.connect(self.sp.selectAll)
      self.sp.setValue(1)
      layout.addWidget(self.sp)
      layout.addWidget(self.btn)
      self.sp.valueChanged.connect(self.valuechange)
      self.setLayout(layout)
      self.setWindowTitle("SpinBox demo")
		
   def valuechange(self):
      self.l1.setText("current value:"+str(self.sp.value()))

def main():
   app = QApplication(sys.argv)
   ex = spindemo()
   ex.show()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()
   