# -*- coding: utf-8 -*-
"""
Liikelaajuus e-form.



"""
from __future__ import print_function


from PyQt4 import QtGui, uic
import sys
import os
import report_templates
import pickle
import copy

class EntryApp(QtGui.QMainWindow):
    """ Main window of application """
    
    def __init__(self):
        super(self.__class__, self).__init__()
        uic.loadUi('tabbed_design.ui', self)
        self.data = {}
        # save empty form (default states for widgets)
        self.read_forms()
        self.data_empty = copy.deepcopy(self.data)
        # link buttons
        self.btnSave.clicked.connect(self.save)
        self.btnLoad.clicked.connect(self.load)
        self.btnClear.clicked.connect(self.clear_forms_dialog)
        self.btnReport.clicked.connect(self.make_report)
        self.btnQuit.clicked.connect(self.close)
        # whether data was saved after editing
        self.saved = True
        # TODO: set validators for line edit objects
        # enable "not saved" state whenever widget values change
        for sp in self.findChildren(QtGui.QSpinBox):        
            sp.valueChanged.connect(self.set_not_saved)
        for ln in self.findChildren(QtGui.QLineEdit):
            ln.textChanged.connect(self.set_not_saved)
        for cb in self.findChildren(QtGui.QComboBox):
            cb.currentIndexChanged.connect(self.set_not_saved)
        for te in self.findChildren(QtGui.QTextEdit):
            cb.textChanged.connect(self.set_not_saved)
        for xb in self.findChildren(QtGui.QCheckBox):
            xb.stateChanged.connect(self.set_not_saved)
        # save into temp file on tab change
        self.maintab.currentChanged.connect(self.save_temp)
        # figure out suitable tmp dir
        if sys.platform == 'win32':
            tmp_fldr = '/Temp'
        else:  # Linux
            tmp_fldr = '/tmp'
        self.tmpfile = tmp_fldr + '/liikelaajuus_tmp.p'
        #if os.path.isfile(self.tmpfile):
        #    print('temp file exists! restoring...')
        #    self.load_temp()
        self.tempfh = open(self.tmpfile, 'wb')        
        
    def closeEvent(self, event):
        """ Close dialog. TODO: Finnish buttons """
        quit_msg = 'Haluatko varmasti sulkea ohjelman?'
        if not self.saved:
            quit_msg = quit_msg + ' Tietoja ei ole tallennettu!'
        reply = QtGui.QMessageBox.question(self, '', 
                     quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.rm_temp()
            event.accept()
        else:
            event.ignore()
            
    def make_report(self):
        """ Make report using the input data. """
        self.read_forms()
        for key in self.data:
            print(key, ':', self.data[key])
        report = report_templates.movement_report(self.data)
        print(report.textual())
        
    def set_not_saved(self):
        self.saved = False
        
    def save(self):
        """ Bring up save dialog. """

    def load(self):
        """ Bring up load dialog. """
        
    def save_temp(self):
        """ Save form input data into temporary backup file. """
        if not self.saved:
            print('backup save...')
            self.read_forms()
            pickle.dump(self.data, self.tempfh)
            self.saved = True
        
    def load_temp(self):
        """ Load form input data from temporary backup file. """
        self.data = pickle.load(self.tempfh)
        self.restore_forms()
        
    def rm_temp(self):
        """ Remove temp file """
        
    def clear_forms_dialog(self):
        """ Clear dialog. """
        clear_msg = 'Haluatko varmasti tyhjentää kaikki tiedot?'
        reply = QtGui.QMessageBox.question(self, '', clear_msg,
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.data = copy.deepcopy(self.data_empty)
            self.restore_forms()
    
    def restore_forms(self):
        """ Restore data from dict into the input form. """
        for ln in self.findChildren(QtGui.QLineEdit):
            name = str(ln.objectName())
            if name[:2] == 'ln':  # exclude spinboxes line edit objects
                ln.setText(self.data[name])            
        for sp in self.findChildren(QtGui.QSpinBox):
            name = str(sp.objectName())
            sp.setValue(self.data[name])
        for cb in self.findChildren(QtGui.QComboBox):
            name = str(cb.objectName())            
            cb.setCurrentIndex(cb.findText(self.data[name]))        
        for xb in self.findChildren(QtGui.QCheckBox):
            name = str(xb.objectName())
            xb.setCheckState(self.data[name])
        for te in self.findChildren(QtGui.QTextEdit):
            name = str(te.objectName())
            te.setPlainText(self.data[name])
        
    def read_forms(self):
        """ Read all entered data into a dict, converting
        to Python types. Dict keys will be set according to 
        input widget names. """
        for ln in self.findChildren(QtGui.QLineEdit):
            name = str(ln.objectName())
            if name[:2] == 'ln':  # exclude spinboxes line edit objects
                val = str(ln.text())
                self.data[name] = val
        for sp in self.findChildren(QtGui.QSpinBox):
            val = int(sp.value())
            self.data[str(sp.objectName())] = val
        for cb in self.findChildren(QtGui.QComboBox):
            val = str(cb.currentText())
            self.data[str(cb.objectName())] = val
        for xb in self.findChildren(QtGui.QCheckBox):
            val = xb.checkState()
            self.data[str(xb.objectName())] = val
        for te in self.findChildren(QtGui.QTextEdit):
            val = te.toPlainText()
            self.data[str(te.objectName())] = val

def main():
    app = QtGui.QApplication(sys.argv)
    form = EntryApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
    


    