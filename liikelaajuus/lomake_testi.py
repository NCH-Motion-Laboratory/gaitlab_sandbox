# -*- coding: utf-8 -*-
"""
Tabbed form for input of liikelaajuus (movement range) data.
Tested with PyQt 4.8 and Python 2.7.

@author: Jussi (jnu@iki.fi)
"""

from __future__ import print_function

from PyQt4 import QtGui, uic
import sys
import os
import report_templates
import pickle
import copy


class EntryApp(QtGui.QMainWindow):
    """ Main window of application. """
    
    def __init__(self):
        super(self.__class__, self).__init__()
        # load user interface made with designer
        uic.loadUi('tabbed_design.ui', self)
        self.data = {}
        # save empty form (default states for widgets)
        self.read_forms()
        self.data_empty = copy.deepcopy(self.data)
        # link buttons
        self.btnSave.clicked.connect(self.save)  #TODO: link to save/load dialog
        self.btnLoad.clicked.connect(self.load)
        self.btnClear.clicked.connect(self.clear_forms_dialog)
        self.btnReport.clicked.connect(self.make_report)
        self.btnQuit.clicked.connect(self.close)
        # whether data was saved into temporary file after editing
        self.tmp_saved = True
        # whether data was saved into a patient-specific file
        self.saved = False
        # TODO: set validators for line edit objects
        # enable "not saved" state whenever widget values change
        for sp in self.findChildren(QtGui.QSpinBox):        
            sp.valueChanged.connect(self.set_not_saved)
        for ln in self.findChildren(QtGui.QLineEdit):
            ln.textChanged.connect(self.set_not_saved)
        for cb in self.findChildren(QtGui.QComboBox):
            cb.currentIndexChanged.connect(self.set_not_saved)
        for te in self.findChildren(QtGui.QTextEdit):
            te.textChanged.connect(self.set_not_saved)
        for xb in self.findChildren(QtGui.QCheckBox):
            xb.stateChanged.connect(self.set_not_saved)
        # save into temp file on tab change
        self.maintab.currentChanged.connect(self.save_temp)
        # name of temp save file
        self.set_dirs()
        self.tmpfile = self.tmp_fldr + '/liikelaajuus_tmp.p'
        # TODO: load tmp file if it exists
        #if os.path.isfile(self.tmpfile):
         #   print('temp file exists! restoring...')
          #  self.load_temp()
        
    def set_dirs(self):
        """ Set dirs according to platform """
        if sys.platform == 'win32':
            self.tmp_fldr = '/Temp'
            self.data_root_fldr = 'C:/'
        else:  # Linux
            self.tmp_fldr = '/tmp'
            self.data_root_fldr = '/'
        
    def confirm_dialog(self, msg):
        dlg = QtGui.QMessageBox()
        dlg.setText(msg)
        dlg.addButton(QtGui.QPushButton(u'Kyllä'), QtGui.QMessageBox.YesRole)
        dlg.addButton(QtGui.QPushButton(u'Ei'), QtGui.QMessageBox.NoRole)        
        dlg.exec_()
        return dlg.buttonRole(dlg.clickedButton())
        
    def message_dialog(self, msg):
        pass
        
    def closeEvent(self, event):
        """ Closing dialog. """
        quit_msg = u'Haluatko varmasti sulkea ohjelman?'
        reply = self.confirm_dialog(quit_msg)
        if reply == QtGui.QMessageBox.YesRole:
            self.rm_temp()
            event.accept()
        else:
            event.ignore()
            
    def make_report(self):
        """ Make report using the input data. """
        NOT_MEASURED = 'EI MITATTU'
        self.read_forms()
        data_ = copy.deepcopy(self.data)
        # translate special default (unmeasured) values
        for key in self.data:
            if self.data[key] == self.data_empty[key]:
                data_[key] = NOT_MEASURED
        report = report_templates.html(data_)
        report_html = report.make()
        print(report_html)
        with open('report_koe.html','wb') as f:
            f.write(report_html)
        
    def set_not_saved(self):
        self.tmp_saved = False
        
    def load_file(self, fname):
        """ Load data from given file and restore forms. """
        if os.path.isfile(fname):
            with open(fname, 'rb') as f:
                self.data = pickle.load(f)
                self.restore_forms()

    def save_file(self, fname):
        """ Save data into given file. """
        with open(fname, 'wb') as f:
            self.read_forms()
            pickle.dump(self.data, f)

    def load(self):
        """ Bring up load dialog and load selected file. """
        fname = QtGui.QFileDialog.getOpenFileName(self, u'Avaa tiedosto', self.data_root_fldr)
        if fname:
            self.load_file(fname)

    def save(self):
        """ Bring up save dialog and save data. """
        fname = QtGui.QFileDialog.getSaveFileName(self, u'Tallenna tiedosto', self.data_root_fldr)
        if fname:
            self.save_file(fname)
            self.saved = True
        
    def save_temp(self):
        """ Save form input data into temporary backup file. """
        if not self.saved:
            self.save_file(self.tmpfile)
                
    def load_temp(self):
        """ Load form input data from temporary backup file. """
        self.load_file(self.tmpfile)
        
    def rm_temp(self):
        """ TODO: Remove temp file.  """
        
    def clear_forms_dialog(self):
        """ Ask whether to clear forms. """
        clear_msg = u'Haluatko varmasti tyhjentää kaikki tiedot?'
        reply = self.confirm_dialog(clear_msg)
        if reply == QtGui.QMessageBox.YesRole:
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
                val = unicode(ln.text()).strip()  # rm leading/trailing whitespace
                self.data[name] = val
        for sp in self.findChildren(QtGui.QSpinBox):
            val = int(sp.value())
            self.data[str(sp.objectName())] = val
        for cb in self.findChildren(QtGui.QComboBox):
            val = unicode(cb.currentText())
            self.data[str(cb.objectName())] = val
        for xb in self.findChildren(QtGui.QCheckBox):
            val = xb.checkState()
            self.data[str(xb.objectName())] = val
        for te in self.findChildren(QtGui.QTextEdit):
            val = unicode(te.toPlainText()).strip()
            self.data[str(te.objectName())] = val  # rm leading/trailing whitespace

def main():
    app = QtGui.QApplication(sys.argv)
    form = EntryApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
    


    