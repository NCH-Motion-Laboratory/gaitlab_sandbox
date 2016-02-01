# -*- coding: utf-8 -*-
"""

"""

from __future__ import print_function


from PyQt4 import QtGui, uic
import sys
import report_templates


class EntryApp(QtGui.QMainWindow):
    """ Main window of application """
    
    def __init__(self):
        super(self.__class__, self).__init__()
        uic.loadUi('tabbed_design.ui', self)
        self.data = {}
        # link buttons
        self.btnReport.clicked.connect(self.make_report)
        self.btnQuit.clicked.connect(self.quit)
        
    def closeEvent(self, event):
        """ TODO: check whether user wants to exit, call event.reject() if not """
        print("closing")
        event.accept()
            
    def make_report(self):
        """ Make report using the input data. """
        self.gather()
        report = report_templates.movement_report(self.data)
        print(report.textual())
        
    def gather(self):
        """ Gather all entered data into a dict. Dict keys will be set
        according to input widget names. """
        for ln in self.findChildren(QtGui.QLineEdit):
            self.data[str(ln.objectName())] = str(ln.text())
        for sp in self.findChildren(QtGui.QSpinBox):
            self.data[str(ln.objectName())] = str(ln.text())

    def quit(self):
        pass
        

def main():
    app = QtGui.QApplication(sys.argv)
    form = EntryApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
    


    