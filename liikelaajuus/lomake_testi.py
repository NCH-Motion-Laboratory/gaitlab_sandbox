# -*- coding: utf-8 -*-
"""
Liikelaajuus e-form.

TODO:

fix numeric input boxes
save/restore data for backup/internal use (pickle?) to Temp dir?
save into specific file + restore?
autosave on tab change?
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
        # these are magic values for entries not measured (default)
        self.LN_NONE = ''
        self.SP_NONE = -181
        self.CB_NONE = "Ei mitattu"
        self.TE_NONE = ''
        # link buttons
        self.btnSave.clicked.connect(self.save)
        self.btnLoad.clicked.connect(self.load)
        self.btnReport.clicked.connect(self.make_report)
        self.btnQuit.clicked.connect(self.quit)
        # TODO: set validators
        
    def closeEvent(self, event):
        """ TODO: check whether user wants to exit, call event.reject() if not """
        event.accept()
            
    def make_report(self):
        """ Make report using the input data. """
        self.read_forms()
        for key in self.data:
            print(key, ':', self.data[key])
        report = report_templates.movement_report(self.data)
        print(report.textual())
        
    def save(self):
        """ Save form input data. """
        self.read_forms()
        fh = open('save.p', 'wb')
        pickle.dump(self.data, fh)
        
    def load(self):
        """ Load form input data. """
        fh = open('save.p', 'rb')
        self.data = pickle.load(fh)
        self.restore_forms()
    
    def restore_forms(self):
        """ Restore saved data into the input form. """
        for wname in self.data:
            val = self.data[wname]
            widget = self.findChildren(QtGui.QWidget, wname)[0]
            if wname[:2] == 'ln':
                widget.setText(self.data[wname])
            if wname[:2] == 'sp':
                widget.setValue(self.data[wname])
            if wname[:2] == 'cb':
                widget.setCurrentIndex(widget.findData(self.data[wname]))
        
    def read_forms(self):
        """ Gather all entered data into a dict, converting
        to Python types. Dict keys will be set according to 
        input widget names. """
        for ln in self.findChildren(QtGui.QLineEdit):
            name = str(ln.objectName())
            if name[:2] == 'ln':  # exclude spinboxes line edit objects
                val = str(ln.text())
                if val == self.LN_NONE:
                    val = None
                self.data[name] = val
        for sp in self.findChildren(QtGui.QSpinBox):
            val = int(sp.value())
            if val == self.SP_NONE:
                val = None
            self.data[str(sp.objectName())] = val
        for cb in self.findChildren(QtGui.QComboBox):
            val = str(cb.currentText())
            if val == self.CB_NONE:
                val = None
            self.data[str(cb.objectName())] = val
        for xb in self.findChildren(QtGui.QCheckBox):
            val = xb.checkState()
            if val:
                val = True
            else:
                val = False
            self.data[str(xb.objectName())] = val
        for te in self.findChildren(QtGui.QTextEdit):
            val = te.toPlainText()
            self.data[str(te.objectName())] = val
            

    def quit(self):
        pass
      

def main():
    app = QtGui.QApplication(sys.argv)
    form = EntryApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
    


    