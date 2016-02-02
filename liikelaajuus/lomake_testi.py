# -*- coding: utf-8 -*-
"""
Liikelaajuus e-form.

TODO:
save/restore data for backup/internal use (pickle?)
save on tab change?
ascii report
excel/tabular report (?)


"""

from __future__ import print_function


from PyQt4 import QtGui, uic
import sys
import report_templates
import pickle


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
        print(self.data)
        #report = report_templates.movement_report(self.data)
        #print(report.textual())
        
    def save_forms(self):
        """ Save form input data. """
        self.gather()
        pickle.dump()
    
    def restore_forms(self):
        """ Restore saved data into the input form. """
        pass
        
    def gather(self):
        """ Gather all entered data into a dict. Dict keys will be set
        according to input widget names (strip the two leading characters
        that describe the widget type) """
        # these are magic values for entries not measured (default)
        LN_NONE = ''
        SP_NONE = -181
        CB_NONE = "Ei mitattu"
        for ln in self.findChildren(QtGui.QLineEdit):
            name = str(ln.objectName())
            if name[:2] == 'ln':  # exclude spinboxes line edit objects
                val = str(ln.text())
                if val == LN_NONE:
                    val = None
                self.data[name[2:]] = val
        for sp in self.findChildren(QtGui.QSpinBox):
            val = int(sp.value())
            if val == SP_NONE:
                val = None
            self.data[str(sp.objectName())[2:]] = val
        for cb in self.findChildren(QtGui.QComboBox):
            val = str(cb.currentText())
            if val == CB_NONE:
                val = None
            self.data[str(cb.objectName())[2:]] = val

    def quit(self):
        pass
      

def main():
    app = QtGui.QApplication(sys.argv)
    form = EntryApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
    


    