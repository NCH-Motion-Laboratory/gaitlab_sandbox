# -*- coding: utf-8 -*-
"""
Tabbed form for input of liikelaajuus (movement range) data.
Tested with PyQt 4.8 and Python 2.7.

@author: Jussi (jnu@iki.fi)
"""

from __future__ import print_function

from PyQt4 import QtGui, uic, QtCore
import sys
import io
import os
import json
import copy
import reporter
import ll_msgs



class EntryApp(QtGui.QMainWindow):
    """ Main window of application. """
    
    def __init__(self):
        super(self.__class__, self).__init__()
        # load user interface made with designer
        uic.loadUi('tabbed_design.ui', self)
        self.set_constants()
        self.init_widgets()
        self.data = {}
        # save empty form (default states for widgets)
        self.read_forms()
        self.data_empty = copy.deepcopy(self.data)
        # whether data was saved into temporary file after editing
        self.tmp_saved = True
        # whether to save on data change
        self.save_to_tmp = True
        # whether data was saved into a patient-specific file
        self.saved = False
        # load tmp file if it exists
        if os.path.isfile(self.tmpfile):
            self.message_dialog(ll_msgs.temp_found)            
            self.load_temp()
        # TODO: set locale and options if needed
        #loc = QtCore.QLocale()
        #loc.setNumberOptions(loc.OmitGroupSeparator | loc.RejectGroupSeparator)
        # special text written out for non-measured variables

    def set_constants(self):
        self.not_measured_text = 'Ei mitattu'
        # Set dirs according to platform
        if sys.platform == 'win32':
            self.tmp_fldr = '/Temp'
            self.data_root_fldr = 'C:/'
        else:  # Linux
            self.tmp_fldr = '/tmp'
            self.data_root_fldr = '/'
        self.tmpfile = self.tmp_fldr + '/liikelaajuus_tmp.p'
        
    def init_widgets(self):
        """ Make a dict of our input widgets and install some callbacks and 
        convenience methods etc. """
        self.input_widgets = {}

        """ Spinbox minimum value is used to indicate "not measured".
        Therefore special getter and setter methods are required. """
        def spinbox_getval(w, mintext):
            val = int(w.value())
            if val == w.minimum():
                return mintext
            else:
                return val
        def spinbox_setval(w, val, mintext):
            if val == mintext:
                w.setValue(w.minimum())
            else:
                w.setValue(val)
            
        for w in self.findChildren((QtGui.QSpinBox,QtGui.QLineEdit,QtGui.QComboBox,QtGui.QCheckBox,QtGui.QTextEdit)):
            wname = str(w.objectName())
            print(wname,'\t\t\t', w.__class__)
            wsave = True
            if wname[:2] == 'sp':
                assert(w.__class__ == QtGui.QSpinBox)
                w.valueChanged.connect(self.values_changed)
                # lambdas need default arguments because of late binding
                w.setVal = lambda val, w=w: spinbox_setval(w, val, self.not_measured_text)
                w.getVal = lambda w=w: spinbox_getval(w, self.not_measured_text)
            elif wname[:2] == 'ln':
                assert(w.__class__ == QtGui.QLineEdit)
                w.textChanged.connect(self.values_changed)
                w.setVal = w.setText
                # Getter methods convert the data instantly to unicode.
                # This is to avoid performing conversions later (when saving etc.)
                # Qt setter methods can take unicode without type conversions.
                w.getVal = lambda w=w: unicode(w.text()).strip()
            elif wname[:2] == 'cb':
                assert(w.__class__ == QtGui.QComboBox)
                w.currentIndexChanged.connect(self.values_changed)
                w.setVal = lambda str, w=w: w.setCurrentIndex(w.findText(str))
                w.getVal = lambda w=w: unicode(w.currentText())
            elif wname[:3] == 'cmt':
                assert(w.__class__ == QtGui.QTextEdit)
                w.textChanged.connect(self.values_changed)
                w.setVal = w.setPlainText
                w.getVal = lambda w=w: unicode(w.toPlainText()).strip()
            elif wname[:2] == 'xb':
                assert(w.__class__ == QtGui.QCheckBox)
                w.stateChanged.connect(self.values_changed)
                w.setVal = w.setCheckState
                w.getVal = lambda w=w: int(w.checkState())
            else:
                wsave = False
            if wsave:
                self.input_widgets[wname] = w
        # link buttons
        self.btnSave.clicked.connect(self.save)  #TODO: link to save/load dialog
        self.btnLoad.clicked.connect(self.load)
        self.btnClear.clicked.connect(self.clear_forms_dialog)
        self.btnReport.clicked.connect(self.make_report)
        self.btnQuit.clicked.connect(self.close)
        # save into temp file on tab change
        self.maintab.currentChanged.connect(self.page_change)
        # set validators for line input widgets that take a number
        dblPosValidator = QtGui.QDoubleValidator()  # positive double
        # 1 decimals, positive value, no scientific notation
        dblPosValidator.setDecimals(1)
        dblPosValidator.setBottom(0)
        dblPosValidator.setNotation(dblPosValidator.StandardNotation)
        for wname in ['lnAntropAlaraajaOik','lnAntropAlaraajaVas','lnAntropPolviOik',
                  'lnAntropPolviVas','lnAntropNilkkaOik','lnAntropNilkkaVas',
                  'lnAntropSIAS','lnAntropPituus','lnAntropPaino','lnTasapOik','lnTasapVas']:
            self.input_widgets[wname].setValidator(dblPosValidator)
        """ First widget of each page. This is used to do focus/selectall on the 1st widget
        on page change. Only for spinbox / lineedit widgets. """
        self.firstwidget = {}
        self.firstwidget[self.tabTiedot] = self.lnTiedotNimi
        self.firstwidget[self.tabAntrop] = self.lnAntropAlaraajaOik
        self.firstwidget[self.tabLonkka] = self.spLonkkaFleksioCatchOik
        self.firstwidget[self.tabNilkka] = self.spNilkkaSoleusCatchOik
        self.firstwidget[self.tabPolvi] = self.spPolviEkstensioVapOik
        #self.firstwidget[self.tabJalkat] = self.cbJalkatSubtalarOik
        self.firstwidget[self.tabVirheas] = self.spVirheasAnteversioOik
        #self.firstwidget[self.tabRyhti] = self.cbRyhtiVoimaVatsaSuorat
        self.firstwidget[self.tabTasap] = self.lnTasapOik
     
    def confirm_dialog(self, msg):
        dlg = QtGui.QMessageBox()
        dlg.setText(msg)
        dlg.setWindowTitle(ll_msgs.message_title)
        dlg.addButton(QtGui.QPushButton(ll_msgs.yes_button), QtGui.QMessageBox.YesRole)
        dlg.addButton(QtGui.QPushButton(ll_msgs.no_button), QtGui.QMessageBox.NoRole)        
        dlg.exec_()
        return dlg.buttonRole(dlg.clickedButton())
        
    def message_dialog(self, msg):
        dlg = QtGui.QMessageBox()
        dlg.setWindowTitle(ll_msgs.message_title)
        dlg.setText(msg)
        dlg.addButton(QtGui.QPushButton(ll_msgs.ok_button), QtGui.QMessageBox.YesRole)        
        dlg.exec_()
        
    def closeEvent(self, event):
        """ Closing dialog. """
        reply = self.confirm_dialog(ll_msgs.quit_)
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
        report = reporter.html(data_)
        report_html = report.make()
        print(report_html)
        with open('report_koe.html','wb') as f:
            # Unicode object into utf8-encoded string
            f.write(report_html.encode('utf-8'))
        
    def values_changed(self):
        if self.save_to_tmp:
            self.save_temp()
        
    def load_file(self, fname):
        """ Load data from given file and restore forms. """
        if os.path.isfile(fname):
            with io.open(fname, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.restore_forms()

    def save_file(self, fname):
        """ Save data into given file in utf-8 encoding. """
        self.read_forms()
        with io.open(fname, 'w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(self.data, ensure_ascii=False)))

    def load(self):
        """ Bring up load dialog and load selected file. """
        fname = QtGui.QFileDialog.getOpenFileName(self, ll_msgs.open_title, self.data_root_fldr)
        if fname:
            try:
                self.load_file(fname)
                # TODO: JSON exceptions
            except (AttributeError, SystemError, IndexError, ImportError, EOFError, KeyError):
                self.message_dialog(ll_msgs.cannot_open+fname)

    def save(self):
        """ Bring up save dialog and save data. """
        fname = QtGui.QFileDialog.getSaveFileName(self, ll_msgs.save_title, self.data_root_fldr)
        if fname:
            # TODO: JSON exceptions
            self.save_file(fname)
            self.saved = True
            
    def page_change(self):
        """ Method called whenever page (tab) changes """
        self.save_temp()
        newpage = self.maintab.currentWidget()
        # focus / selectAll on 1st widget of new tab
        if newpage in self.firstwidget:
            self.firstwidget[newpage].selectAll()
            self.firstwidget[newpage].setFocus()
        
    def save_temp(self):
        """ Save form input data into temporary backup file. """
        self.save_file(self.tmpfile)
                
    def load_temp(self):
        """ Load form input data from temporary backup file. """
        try:
            self.load_file(self.tmpfile)
        except (SystemError, IndexError, EOFError, KeyError):
            self.message_dialog(ll_msgs.cannot_open_tmp)
            self.rm_temp()
        
    def rm_temp(self):
        """ Remove temp file.  """
        if os.path.isfile(self.tmpfile):
            os.remove(self.tmpfile)
        
    def clear_forms_dialog(self):
        """ Ask whether to clear forms. If yes, set widget inputs to default values. """
        reply = self.confirm_dialog(ll_msgs.clear)
        if reply == QtGui.QMessageBox.YesRole:
            self.data = copy.deepcopy(self.data_empty)
            self.restore_forms()
    
    def restore_forms(self):
        """ Restore widget input values from self.data """
        # don't make backup saves while widgets are being restored
        self.save_to_tmp = False
        for wname in self.input_widgets:
            self.input_widgets[wname].setVal(self.data[wname])
        self.save_to_tmp = True
            
    def read_forms(self):
        """ Read self.data from widget inputs """
        for wname in self.input_widgets:
            self.data[wname] = self.input_widgets[wname].getVal()

def main():
    app = QtGui.QApplication(sys.argv)
    form = EntryApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
    


    