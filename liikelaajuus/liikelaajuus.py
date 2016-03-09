# -*- coding: utf-8 -*-
"""
Tabbed form for input of movement range data.
Tested with PyQt 4.8 and Python 2.7.


design:
-separate ui file with all the widgets is made with Qt Designer and loaded 
 using uic
-custom widget (check+spinbox), plugin file should be made available to Qt
designer (checkspinbox_plugin.py)
-widget naming: first 2-3 chars indicate widget type, next word indicates 
 variable category or page where widget resides, the rest indicates the 
 variable (e.g. lnTiedotNimi)
-widget inputs are updated into internal dict immediately when any value
 changes
-dict keys are taken automatically from widget names by removing first 2-3
chars (widget type)
-for saving, dict data is turned into json unicode and written out in utf-8
-data is saved into temp directory whenever any values are changed by user


TODO:

catcheja ei raportoida jos arvona 'Ei'. ok?
-erit. soleus catch = 'Ei'+ klonus 'Kyllä' näyt. pelkän klonuksen
kommenttimuuttujien ryhmittely raporttiin?


exception handling
tab order
click+enter? (spinboxes)



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
import liikelaajuus




class CheckDegSpinBox(QtGui.QWidget):
    """ Custom widget: Spinbox (degrees) with checkbox signaling "default value".
    If checkbox is checked, disable spinbox -> value() returns the default value
    shown next to checkbox (defaultText property)
    Otherwise value() returns spinbox value. 
    setValue() takes either the default value, the 'special value' (not measured) or 
    integer.
    """
    # signal has to be defined here for unclear reasons
    # note that currently the value is not returned by the signal
    # (unlike in the Qt spinbox)
    valueChanged = QtCore.pyqtSignal()  
    
    # for Qt designer
    __pyqtSignals__ = ('valueChanged')
    
    def __init__(self, parent=None):
      
        super(self.__class__, self).__init__(parent)

        #self.normalText = u'NR'            
        self.normalCheckBox = QtGui.QCheckBox()
        self.normalCheckBox.stateChanged.connect(lambda st: self.toggleSpinBox(st))
        
        self.degSpinBox = QtGui.QSpinBox()
        # these should be implemented as qt properties w/ getter and setter methods,
        # so they could be e.g. changed within Qt Designer
        self.degSpinBox.setRange(-181, 180.0)
        self.degSpinBox.setValue(-181)
        #self.degSpinBox.setSuffix(u'°')
        self.specialtext = u'Ei mitattu'

        self.degSpinBox.setSpecialValueText(self.specialtext)
        self.degSpinBox.valueChanged.connect(self.valueChanged.emit)
        self.degSpinBox.setMinimumSize(100,0)

        # default text
        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.addWidget(normalLabel, 0, 0)
        layout.addWidget(self.degSpinBox)
        layout.addWidget(self.normalCheckBox)

        # needed for tab order
        self.setFocusPolicy(QtCore.Qt.TabFocus)
        
        self.setDefaultText(u'NR')
        self.setSuffix(u'°')
        
    def setDefaultText(self, text):
        self.normalCheckBox.setText(text)
        
    def getDefaultText(self):
        return self.normalCheckBox.text()
        
    def setSuffix(self, text):
        self.degSpinBox.setSuffix(text)
        
    def getSuffix(self):
        return self.degSpinBox.suffix()

    # set properties
    defaultText = QtCore.pyqtProperty('QString', getDefaultText, setDefaultText)
    suffix = QtCore.pyqtProperty('QString', getSuffix, setSuffix)

    def value(self):
        if self.normalCheckBox.checkState() == 0:
            val = self.degSpinBox.value()
            if val == self.degSpinBox.minimum():
                return unicode(self.specialtext)
            else:
                return val
        elif self.normalCheckBox.checkState() == 2:
            return unicode(self.getDefaultText())

    def setValue(self, val):
        if val == self.getDefaultText():
            self.degSpinBox.setEnabled(False)
            self.normalCheckBox.setCheckState(2)
        else:
            self.normalCheckBox.setCheckState(0)
            if val == self.specialtext:
                self.degSpinBox.setValue(self.degSpinBox.minimum())
            else:
                self.degSpinBox.setValue(val)
                
    def selectAll(self):
        self.degSpinBox.selectAll()
        
    def setFocus(self):
        self.degSpinBox.setFocus()
    
    def toggleSpinBox(self, st):
        """ Enables or disables spinbox input according to st. Also emit
        valueChanged signal """
        self.degSpinBox.setEnabled(not st)
        self.valueChanged.emit()
        
    #def sizeHint(self):
    #    return QSize(150,20)



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
        # whether to update internal dict of variables
        self.update_dict = True
        # load tmp file if it exists
        if os.path.isfile(self.tmpfile):
            self.message_dialog(ll_msgs.temp_found)            
            self.load_temp()
        # TODO: set locale and options if needed
        #loc = QtCore.QLocale()
        #loc.setNumberOptions(loc.OmitGroupSeparator | loc.RejectGroupSeparator)
        # special text written out for non-measured variables
        for key in sorted(self.data.keys()):
            print('{%s}'%key)
        #print(self.units)
        
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
        self.json_exceptions = (UnicodeDecodeError, EOFError, IOError, TypeError)
        self.json_filter = u'JSON files (*.json)'
        self.text_filter = u'Text files (*.txt)'
        self.global_fontsize = 13
        
    def init_widgets(self):
        """ Make a dict of our input widgets and install some callbacks and 
        convenience methods etc. """
        self.input_widgets = {}

        def spinbox_getval(w, mintext):
            val = w.value()
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

        """ Create getter/setter methods that convert the data immediately to
        desired form. On value change, call self.values_changed which updates
        the self.data dict at the correspoding widget. """
        #for w in self.findChildren((CheckDegSpinBox,QtGui.QSpinBox,QtGui.QDoubleSpinBox,QtGui.QLineEdit,QtGui.QComboBox,QtGui.QCheckBox,QtGui.QTextEdit)):
        for w in self.findChildren(QtGui.QWidget):            
            wname = unicode(w.objectName())
            wsave = True
            w.unit = ''  # if a widget input has units, set it below
            if wname[:2] == 'sp':
                assert(w.__class__ == QtGui.QSpinBox or w.__class__ == QtGui.QDoubleSpinBox)
                # -lambdas need default arguments because of late binding
                # -lambda expression needs to consume unused 'new value' argument,
                # therefore two parameters (except for QTextEdit...)
                w.valueChanged.connect(lambda x, w=w: self.values_changed(w))
                w.setVal = lambda val, w=w: spinbox_setval(w, val, self.not_measured_text)
                w.getVal = lambda w=w: spinbox_getval(w, self.not_measured_text)
                w.unit = w.suffix()
            elif wname[:2] == 'ln':
                assert(w.__class__ == QtGui.QLineEdit)
                w.textChanged.connect(lambda x, w=w: self.values_changed(w))
                w.setVal = w.setText
                w.getVal = lambda w=w: unicode(w.text()).strip()
            elif wname[:2] == 'cb':
                assert(w.__class__ == QtGui.QComboBox)
                w.currentIndexChanged.connect(lambda x, w=w: self.values_changed(w))
                w.setVal = lambda str, w=w: w.setCurrentIndex(w.findText(str))
                w.getVal = lambda w=w: unicode(w.currentText())
            elif wname[:3] == 'cmt':
                assert(w.__class__ == QtGui.QTextEdit)
                w.textChanged.connect(lambda w=w: self.values_changed(w))
                w.setVal = w.setPlainText
                w.getVal = lambda w=w: unicode(w.toPlainText()).strip()
            elif wname[:2] == 'xb':
                assert(w.__class__ == QtGui.QCheckBox)
                w.stateChanged.connect(lambda x, w=w: self.values_changed(w))
                w.setVal = lambda val, w=w: checkbox_setval(w, val, self.checkbox_yestext, self.checkbox_notext)
                w.getVal = lambda w=w: checkbox_getval(w, self.checkbox_yestext, self.checkbox_notext)
            elif wname[:3] == 'csb':
                print(w.__class__)
                assert(w.__class__ == liikelaajuus.CheckDegSpinBox)
                w.valueChanged.connect(lambda w=w: self.values_changed(w))
                w.getVal = w.value
                w.setVal = w.setValue
                w.unit = w.getSuffix()  # this works differently from the Qt spinbox
            else:
                wsave = False
            if wsave:
                self.input_widgets[wname] = w
                # TODO: specify whether input value is 'mandatory' or not
                w.important = False
        # link buttons
        self.btnSave.clicked.connect(self.save_dialog)
        self.btnLoad.clicked.connect(self.load_dialog)
        self.btnClear.clicked.connect(self.clear_forms_dialog)
        self.btnReport.clicked.connect(self.make_report)
        #self.btnReport.clicked.connect(self.save_report_dialog)
        self.btnQuit.clicked.connect(self.close)
        # method call on tab change
        self.maintab.currentChanged.connect(self.page_change)
        """ First widget of each page. This is used to do focus/selectall on the 1st widget
        on page change so that data can be entered immediately. Only needed for 
        spinbox / lineedit widgets. """
        self.firstwidget = {}
        # TODO: check/fix
        self.firstwidget[self.tabTiedot] = self.lnTiedotNimi
        self.firstwidget[self.tabAntrop] = self.spAntropAlaraajaOik
        self.firstwidget[self.tabLonkka] = self.csbLonkkaFleksioOik
        self.firstwidget[self.tabNilkka] = self.csbNilkkaSoleusCatchOik
        self.firstwidget[self.tabPolvi] = self.csbPolviEkstensioVapOik
        self.firstwidget[self.tabVirheas] = self.spVirheasAnteversioOik
        self.firstwidget[self.tabTasap] = self.spTasapOik
        self.total_widgets = len(self.input_widgets)
        self.statusbar.showMessage(ll_msgs.ready.format(n=self.total_widgets))
        # TODO: set 'important' widgets (mandatory values) .important = True
        """ Set up widget -> varname translation dict. Currently variable names
        are derived by removing 2 first characters from widget names (except
        for comment box variables cmt* which are identical with widget names). """
        self.widget_to_var = {}
        for wname in self.input_widgets:
            if wname[:3] == 'cmt':
                varname = wname
            elif wname[:3] == 'csb':  # custom widget
                varname = wname[3:]
            else:
                varname = wname[2:]
            self.widget_to_var[wname] = varname
        # collect variable units into a dict
        self.units = {}
        for wname in self.input_widgets:
            self.units[self.widget_to_var[wname]] = self.input_widgets[wname].unit
        # try to increase font size
        #self.maintab.setStyleSheet('QTabBar { font-size: 14pt;}')
        #self.maintab.setStyleSheet('QWidget { font-size: 14pt;}')
        self.setStyleSheet('QWidget { font-size: %dpt;}'%self.global_fontsize)
       
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
        report = ll_reporter.text(self.data, self.units)
        report_txt = report.make_text_report()
        print(report_txt)
        fname = 'report_koe.txt'
        with io.open(fname,'w',encoding='utf-8') as f:
            f.write(report_txt)
        self.statusbar.showMessage(ll_msgs.wrote_report.format(filename=fname))

    def values_changed(self, w):
        if self.update_dict:
            print('updating dict for:', w.objectName(),'new value:',w.getVal())
            wname = unicode(w.objectName())
            self.data[self.widget_to_var[wname]] = w.getVal()
            # DEBUG: print report
            self.make_report()
            ###
        self.saved_to_file = False
        if self.save_to_tmp:
            self.save_temp()
        
    def load_file(self, fname):
        """ Load data from given file and restore forms. """
        if os.path.isfile(fname):
            with io.open(fname, 'r', encoding='utf-8') as f:
                data_loaded = json.load(f)
            keys, loaded_keys = set(self.data), set(data_loaded)
            if not keys == loaded_keys:  # keys mismatch
                self.keyerror_dialog(keys, loaded_keys)
            for key in data_loaded:
                if key in self.data:
                    self.data[key] = data_loaded[key]
            self.restore_forms()
            self.statusbar.showMessage(ll_msgs.status_loaded.format(filename=fname, n=self.n_modified()))

    def keyerror_dialog(self, origkeys, newkeys):
        """ Report missing / extra keys to user. """
        cmnkeys = origkeys.intersection(newkeys)
        extra_in_new = newkeys - cmnkeys
        not_in_new = origkeys - cmnkeys
        li = [ll_msgs.keyerror_msg]
        if extra_in_new:
            li.append(ll_msgs.keys_extra.format(keys=', '.join(extra_in_new)))
        if not_in_new:
            li.append(ll_msgs.keys_not_found.format(keys=', '.join(not_in_new)))
        self.message_dialog(''.join(li))

    def save_file(self, fname):
        """ Save data into given file in utf-8 encoding. """
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
            except self.json_exceptions:
                self.message_dialog(ll_msgs.cannot_open+fname)

    def save_dialog(self):
        """ Bring up save dialog and save data. """
        fname = QtGui.QFileDialog.getSaveFileName(self, ll_msgs.save_report_title, self.data_root_fldr,
                                                  self.json_filter)
        if fname:
            fname = unicode(fname)
            try:
                self.save_file(fname)
                self.saved_to_file = True
                self.statusbar.showMessage(ll_msgs.status_saved+fname)
            except self.json_exceptions:
                self.message_dialog(ll_msgs.cannot_save+fname)

    def save_report_dialog(self):
        """ Bring up save dialog and save report. """
        fname = QtGui.QFileDialog.getSaveFileName(self, ll_msgs.save_title, self.data_root_fldr,
                                                  self.text_filter)
        if fname:
            fname = unicode(fname)
            try:
                report = ll_reporter.text(self.data, self.units)
                report_txt = report.make_text_report()
                with io.open(fname, 'w', encoding='utf-8') as f:
                    f.write(report_txt)
                self.statusbar.showMessage(ll_msgs.status_report_saved+fname)
            except (IOError):
                self.message_dialog(ll_msgs.cannot_save+fname)
                
    def n_modified(self):
        """ Count modified values. """
        return len([x for x in self.data if self.data[x] != self.data_empty[x]])
            
    def page_change(self):
        """ Method called whenever page (tab) changes. Currently only does
        focus / selectall on the first widget of page. """
        newpage = self.maintab.currentWidget()
        # focus / selectAll on 1st widget of new tab
        if newpage in self.firstwidget:
            self.firstwidget[newpage].selectAll()
            self.firstwidget[newpage].setFocus()
        
    def save_temp(self):
        """ Save form input data into temporary backup file. """
        #try:
        self.save_file(self.tmpfile)
        self.statusbar.showMessage(ll_msgs.status_value_change.format(n=self.n_modified(), tmpfile=self.tmpfile))
        #except self.json_exceptions:
            #self.message_dialog(ll_msgs.cannot_save+self.tmpfile)
                
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
        """ Restore widget input values from self.data. Need to disable widget callbacks
        and automatic data saving while programmatic updating of widgets is taking place. """
        self.save_to_tmp = False
        self.update_dict = False
        for wname in self.input_widgets:
            self.input_widgets[wname].setVal(self.data[self.widget_to_var[wname]])
        self.save_to_tmp = True
        self.update_dict = True
            
    def read_forms(self):
        """ Read self.data from widget inputs. """
        for wname in self.input_widgets:
            self.data[self.widget_to_var[wname]] = self.input_widgets[wname].getVal()

def main():
    app = QtGui.QApplication(sys.argv)
    form = EntryApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
    


    
