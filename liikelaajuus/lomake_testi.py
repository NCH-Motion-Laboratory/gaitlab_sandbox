# -*- coding: utf-8 -*-
"""
Qt designer / PyQt test
first generate python code from design.ui by:
pyuic4 design.ui >design.py

see:
https://nikolak.com/pyqt-qt-designer-getting-started/

"""

from PyQt4 import QtGui, uic
import sys


class ExampleApp(QtGui.QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        uic.loadUi('tabbed_design.ui', self)
        

def main():
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
    


    