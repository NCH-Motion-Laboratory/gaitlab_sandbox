# -*- coding: utf-8 -*-
"""
Tabbed form for input of liikelaajuus (movement range) data.
Tested with PyQt 4.8 and Python 2.7.

TODO:
handle missing/extra items on json save/load
add 'ok' option for catch (and degs?) (not measured/no catch/catch in degrees)
-or degs to free text fields
make main window smaller (comment box?)
line inputs that take a number -> spinboxes?
don't update whole dict on value change event


@author: Jussi (jnu@iki.fi)
"""

from __future__ import print_function

from PyQt4 import QtGui, uic, QtCore
import sys
import io
import os
import json
import ll_reporter
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
        self.data_empty = self.data.copy()
        # whether to save to temp file whenever input widget data changes
        self.save_to_tmp = True
        # whether data was saved into a patient-specific file
        self.saved_to_file = False
        # load tmp file if it exists
        if os.path.isfile(self.tmpfile):
            self.message_dialog(ll_msgs.temp_found)            
            self.load_temp()
        # TODO: set locale and options if needed
        #loc = QtCore.QLocale()
        #loc.setNumberOptions(loc.OmitGroupSeparator | loc.RejectGroupSeparator)
        # special text written out for non-measured variables

    def set_constants(self):
        self.not_measured_text = u'Ei mitattu'
        self.checkbox_yestext = u'Kyllä'
        self.checkbox_notext = u'Ei'
        # Set dirs according to platform
        if sys.platform == 'win32':
            self.tmp_fldr = '/Temp'
            self.data_root_fldr = 'C:/'
        else:  # Linux
            self.tmp_fldr = '/tmp'
            self.data_root_fldr = '/'
        self.tmpfile = self.tmp_fldr + '/liikelaajuus_tmp.json'
        # exceptions that might be generated when parsing json file
        self.json_load_exceptions = (UnicodeDecodeError, EOFError, IOError)
        self.json_filter = u'JSON files (*.json)'
        
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
                
        def checkbox_getval(w, yestext, notext):
            val = int(w.checkState())
            if val == 0:
                return notext
            elif val == 2:
                return yestext
            else:
                raise Exception('Unexpected checkbox value')
                
        def checkbox_setval(w, val, yestext, notext):
            if val == yestext:
                w.setCheckState(2)
            elif val == notext:
                w.setCheckState(0)
            else:
                raise Exception('Unexpected checkbox entry value')

	# TODO: pass w to values_changed and read only the changed
	# widget value into self.data
            
        for w in self.findChildren((QtGui.QSpinBox,QtGui.QLineEdit,QtGui.QComboBox,QtGui.QCheckBox,QtGui.QTextEdit)):
            wname = str(w.objectName())
            #print(wname,'\t\t\t', w.__class__)
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
                # This is to avoid performing conversions on reporting, saving etc.
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
                w.setVal = lambda val, w=w: checkbox_setval(w, val, self.checkbox_yestext, self.checkbox_notext)
                w.getVal = lambda w=w: checkbox_getval(w, self.checkbox_yestext, self.checkbox_notext)
            else:
                wsave = False
            if wsave:
                self.input_widgets[wname] = w
                # specified whether input value is 'mandatory' or not
                w.important = False
        # link buttons
        self.btnSave.clicked.connect(self.save_dialog)
        self.btnLoad.clicked.connect(self.load_dialog)
        self.btnClear.clicked.connect(self.clear_forms_dialog)
        self.btnReport.clicked.connect(self.make_report)
        self.btnQuit.clicked.connect(self.close)
        # save into temp file on tab change
        self.maintab.currentChanged.connect(self.page_change)
        # set validators for line input widgets that only take a number
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
        on page change so that data can be entered immediately. Only needed for 
        spinbox / lineedit widgets. """
        self.firstwidget = {}
        # TODO: check/fix
        self.firstwidget[self.tabTiedot] = self.lnTiedotNimi
        self.firstwidget[self.tabAntrop] = self.lnAntropAlaraajaOik
        self.firstwidget[self.tabLonkka] = self.spLonkkaFleksioOik
        self.firstwidget[self.tabNilkka] = self.spNilkkaSoleusCatchOik
        self.firstwidget[self.tabPolvi] = self.spPolviEkstensioVapOik
        self.firstwidget[self.tabVirheas] = self.spVirheasAnteversioOik
        self.firstwidget[self.tabTasap] = self.lnTasapOik
        self.total_widgets = len(self.input_widgets)
        self.statusbar.showMessage(ll_msgs.ready.format(n=self.total_widgets))
        # TODO: set 'important' widgets (mandatory values) .important = True
     
    def confirm_dialog(self, msg):
        """ Show yes/no dialog """
        dlg = QtGui.QMessageBox()
        dlg.setText(msg)
        dlg.setWindowTitle(ll_msgs.message_title)
        dlg.addButton(QtGui.QPushButton(ll_msgs.yes_button), QtGui.QMessageBox.YesRole)
        dlg.addButton(QtGui.QPushButton(ll_msgs.no_button), QtGui.QMessageBox.NoRole)        
        dlg.exec_()
        return dlg.buttonRole(dlg.clickedButton())
        
    def message_dialog(self, msg):
        """ Show message with an 'OK' button """
        dlg = QtGui.QMessageBox()
        dlg.setWindowTitle(ll_msgs.message_title)
        dlg.setText(msg)
        dlg.addButton(QtGui.QPushButton(ll_msgs.ok_button), QtGui.QMessageBox.YesRole)        
        dlg.exec_()
        
    def closeEvent(self, event):
        """ Confirm and close application. """
        if not self.saved_to_file:
            reply = self.confirm_dialog(ll_msgs.quit_not_saved)
        else:
            reply = self.confirm_dialog(ll_msgs.quit_)
        if reply == QtGui.QMessageBox.YesRole:
            self.rm_temp()
            event.accept()
        else:
            event.ignore()
            
    def make_report(self):
        """ Make report using the input data. """
        self.read_forms()
        report = ll_reporter.report(self.data)
        report_txt = report.make_text_list()
        fname = 'report_koe.txt'
        with io.open(fname,'w',encoding='utf-8') as f:
            f.write(report_txt)
        self.statusbar.showMessage(ll_msgs.wrote_report.format(filename=fname))
        
    def values_changed(self):
        self.saved_to_file = False
        if self.save_to_tmp:
            self.save_temp()
        
    def load_file(self, fname):
        """ Load data from given file and restore forms. """
        if os.path.isfile(fname):
            with io.open(fname, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.restore_forms()
            self.statusbar.showMessage(ll_msgs.status_loaded.format(filename=fname, n=self.n_modified()))

    def save_file(self, fname):
        """ Save data into given file in utf-8 encoding. """
        self.read_forms()
        with io.open(fname, 'w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(self.data, ensure_ascii=False)))

    def load_dialog(self):
        """ Bring up load dialog and load selected file. """
        fname = QtGui.QFileDialog.getOpenFileName(self, ll_msgs.open_title, self.data_root_fldr,
                                                  self.json_filter)
        if fname:
            fname = unicode(fname)
            try:
                self.load_file(fname)
            except self.json_load_exceptions:
                self.message_dialog(ll_msgs.cannot_open+fname)

    def save_dialog(self):
        """ Bring up save dialog and save data. """
        fname = QtGui.QFileDialog.getSaveFileName(self, ll_msgs.save_title, self.data_root_fldr,
                                                  self.json_filter)
        if fname:
            fname = unicode(fname)
            try:
                self.save_file(fname)
                self.saved_to_file = True
                self.statusbar.showMessage(ll_msgs.status_saved+fname)
            except (IOError):
                self.message_dialog(ll_msgs.cannot_save+fname)
                
    def n_modified(self):
        """ Count modified values. """
        return len([x for x in self.data if self.data[x] != self.data_empty[x]])
            
    def page_change(self):
        """ Method called whenever page (tab) changes """
        newpage = self.maintab.currentWidget()
        # focus / selectAll on 1st widget of new tab
        if newpage in self.firstwidget:
            self.firstwidget[newpage].selectAll()
            self.firstwidget[newpage].setFocus()
        
    def save_temp(self):
        """ Save form input data into temporary backup file. """
        self.save_file(self.tmpfile)
        self.statusbar.showMessage(ll_msgs.status_value_change.format(n=self.n_modified(), tmpfile=self.tmpfile))
                
    def load_temp(self):
        """ Load form input data from temporary backup file. """
        try:
            self.load_file(self.tmpfile)
        except self.json_load_exceptions:
            self.message_dialog(ll_msgs.cannot_open_tmp)
        
    def rm_temp(self):
        """ Remove temp file.  """
        if os.path.isfile(self.tmpfile):
            os.remove(self.tmpfile)
        
    def clear_forms_dialog(self):
        """ Ask whether to clear forms. If yes, set widget inputs to default values. """
        if self.saved_to_file:
            reply = self.confirm_dialog(ll_msgs.clear)
        else:
            reply = self.confirm_dialog(ll_msgs.clear_not_saved)
        if reply == QtGui.QMessageBox.YesRole:
            self.data = self.data_empty.copy()
            self.restore_forms()
            self.statusbar.showMessage(ll_msgs.status_cleared)
    
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
    
    


    
