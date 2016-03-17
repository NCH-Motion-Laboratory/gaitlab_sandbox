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

lis. luiden virheasennot -> polven valgus (myöhemmin)

tab order

click+enter? (spinboxes) see:
http://stackoverflow.com/questions/1891744/pyqt4-qspinbox-selectall-not-working-as-expected




@author: Jussi (jnu@iki.fi)
"""


from __future__ import print_function

from PyQt4 import QtGui, uic, QtCore
import sys
import traceback
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

        self.normalCheckBox = QtGui.QCheckBox()
        self.normalCheckBox.stateChanged.connect(lambda st: self.toggleSpinBox(st))

        # default text
        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        #layout.addWidget(normalLabel, 0, 0)
        layout.addWidget(self.degSpinBox)
        layout.addWidget(self.normalCheckBox)

        # needed for tab order
        self.degSpinBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.normalCheckBox.setFocusPolicy(QtCore.Qt.NoFocus)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocusProxy(self.degSpinBox)
        
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
        self.set_taborder()
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
            
    def set_taborder(self):
        """ Set tab focus order. This is set also by the ui file loaded
        above, but needs to be redone because Qt does not handle focus correctly
        for custom (compound) widgets (QTBUG-10907). For custom widgets, the focus proxy
        needs to be explicitly inserted into focus chain. The below code can
        be generated by running:
        pyuic4 tabbed_design.ui | grep TabOrder | sed "s/csb[a-zA-Z0-9]*/&.focusProxy()/g"
       
        """
        
        self.setTabOrder(self.lnTiedotNimi, self.lnTiedotPvm)
        self.setTabOrder(self.lnTiedotPvm, self.lnTiedotDiag)
        self.setTabOrder(self.lnTiedotDiag, self.lnTiedotID)
        self.setTabOrder(self.lnTiedotID, self.lnTiedotHetu)
        self.setTabOrder(self.lnTiedotHetu, self.lnTiedotMittaajat)
        self.setTabOrder(self.lnTiedotMittaajat, self.spAntropAlaraajaOik)
        self.setTabOrder(self.spAntropAlaraajaOik, self.spAntropAlaraajaVas)
        self.setTabOrder(self.spAntropAlaraajaVas, self.spAntropPolviOik)
        self.setTabOrder(self.spAntropPolviOik, self.spAntropPolviVas)
        self.setTabOrder(self.spAntropPolviVas, self.spAntropNilkkaOik)
        self.setTabOrder(self.spAntropNilkkaOik, self.spAntropNilkkaVas)
        self.setTabOrder(self.spAntropNilkkaVas, self.spAntropSIAS)
        self.setTabOrder(self.spAntropSIAS, self.spAntropPituus)
        self.setTabOrder(self.spAntropPituus, self.spAntropPaino)
        self.setTabOrder(self.spAntropPaino, self.csbLonkkaFleksioOik.focusProxy())
        self.setTabOrder(self.csbLonkkaFleksioOik.focusProxy(), self.csbLonkkaFleksioVas.focusProxy())
        self.setTabOrder(self.csbLonkkaFleksioVas.focusProxy(), self.cbLonkkaFleksioModAOik)
        self.setTabOrder(self.cbLonkkaFleksioModAOik, self.cbLonkkaFleksioModAVas)
        self.setTabOrder(self.cbLonkkaFleksioModAVas, self.csbLonkkaEkstensioVapOik.focusProxy())
        self.setTabOrder(self.csbLonkkaEkstensioVapOik.focusProxy(), self.csbLonkkaEkstensioAvOik.focusProxy())
        self.setTabOrder(self.csbLonkkaEkstensioAvOik.focusProxy(), self.csbLonkkaEkstensioPolvi90Oik.focusProxy())
        self.setTabOrder(self.csbLonkkaEkstensioPolvi90Oik.focusProxy(), self.csbLonkkaEkstensioVapVas.focusProxy())
        self.setTabOrder(self.csbLonkkaEkstensioVapVas.focusProxy(), self.csbLonkkaEkstensioAvVas.focusProxy())
        self.setTabOrder(self.csbLonkkaEkstensioAvVas.focusProxy(), self.csbLonkkaEkstensioPolvi90Vas.focusProxy())
        self.setTabOrder(self.csbLonkkaEkstensioPolvi90Vas.focusProxy(), self.cbLonkkaEkstensioModAOik)
        self.setTabOrder(self.cbLonkkaEkstensioModAOik, self.cbLonkkaEkstensioModAVas)
        self.setTabOrder(self.cbLonkkaEkstensioModAVas, self.csbLonkkaExtLagOik.focusProxy())
        self.setTabOrder(self.csbLonkkaExtLagOik.focusProxy(), self.csbLonkkaExtLagVas.focusProxy())
        self.setTabOrder(self.csbLonkkaExtLagVas.focusProxy(), self.csbLonkkaAbduktioLonkka0Polvi90Oik.focusProxy())
        self.setTabOrder(self.csbLonkkaAbduktioLonkka0Polvi90Oik.focusProxy(), self.csbLonkkaAbduktioLonkka0Polvi90Vas.focusProxy())
        self.setTabOrder(self.csbLonkkaAbduktioLonkka0Polvi90Vas.focusProxy(), self.csbLonkkaAdduktoritCatchOik.focusProxy())
        self.setTabOrder(self.csbLonkkaAdduktoritCatchOik.focusProxy(), self.csbLonkkaAdduktoritCatchVas.focusProxy())
        self.setTabOrder(self.csbLonkkaAdduktoritCatchVas.focusProxy(), self.csbLonkkaAbduktioLonkka0Oik.focusProxy())
        self.setTabOrder(self.csbLonkkaAbduktioLonkka0Oik.focusProxy(), self.csbLonkkaAbduktioLonkka0Vas.focusProxy())
        self.setTabOrder(self.csbLonkkaAbduktioLonkka0Vas.focusProxy(), self.cbLonkkaAdduktoritModAOik)
        self.setTabOrder(self.cbLonkkaAdduktoritModAOik, self.cbLonkkaAdduktoritModAVas)
        self.setTabOrder(self.cbLonkkaAdduktoritModAVas, self.csbLonkkaAbduktioLonkkaFleksOik.focusProxy())
        self.setTabOrder(self.csbLonkkaAbduktioLonkkaFleksOik.focusProxy(), self.csbLonkkaAbduktioLonkkaFleksVas.focusProxy())
        self.setTabOrder(self.csbLonkkaAbduktioLonkkaFleksVas.focusProxy(), self.csbLonkkaAdduktioOik.focusProxy())
        self.setTabOrder(self.csbLonkkaAdduktioOik.focusProxy(), self.csbLonkkaAdduktioVas.focusProxy())
        self.setTabOrder(self.csbLonkkaAdduktioVas.focusProxy(), self.lnLonkkaOberOik)
        self.setTabOrder(self.lnLonkkaOberOik, self.lnLonkkaOberVas)
        self.setTabOrder(self.lnLonkkaOberVas, self.csbLonkkaSisakiertoOik.focusProxy())
        self.setTabOrder(self.csbLonkkaSisakiertoOik.focusProxy(), self.csbLonkkaSisakiertoVas.focusProxy())
        self.setTabOrder(self.csbLonkkaSisakiertoVas.focusProxy(), self.cbLonkkaSisakiertoModAOik)
        self.setTabOrder(self.cbLonkkaSisakiertoModAOik, self.cbLonkkaSisakiertoModAVas)
        self.setTabOrder(self.cbLonkkaSisakiertoModAVas, self.csbLonkkaUlkokiertoOik.focusProxy())
        self.setTabOrder(self.csbLonkkaUlkokiertoOik.focusProxy(), self.csbLonkkaUlkokiertoVas.focusProxy())
        self.setTabOrder(self.csbLonkkaUlkokiertoVas.focusProxy(), self.cbLonkkaUlkokiertoModAOik)
        self.setTabOrder(self.cbLonkkaUlkokiertoModAOik, self.cbLonkkaUlkokiertoModAVas)
        self.setTabOrder(self.cbLonkkaUlkokiertoModAVas, self.csbPolviEkstensioVapOik.focusProxy())
        self.setTabOrder(self.csbPolviEkstensioVapOik.focusProxy(), self.csbPolviEkstensioAvOik.focusProxy())
        self.setTabOrder(self.csbPolviEkstensioAvOik.focusProxy(), self.csbPolviEkstensioVapVas.focusProxy())
        self.setTabOrder(self.csbPolviEkstensioVapVas.focusProxy(), self.csbPolviEkstensioAvVas.focusProxy())
        self.setTabOrder(self.csbPolviEkstensioAvVas.focusProxy(), self.csbPolviFleksioSelinmakuuOik.focusProxy())
        self.setTabOrder(self.csbPolviFleksioSelinmakuuOik.focusProxy(), self.csbPolviFleksioSelinmakuuVas.focusProxy())
        self.setTabOrder(self.csbPolviFleksioSelinmakuuVas.focusProxy(), self.csbPolviFleksioVatsamakuuOik.focusProxy())
        self.setTabOrder(self.csbPolviFleksioVatsamakuuOik.focusProxy(), self.csbPolviFleksioVatsamakuuVas.focusProxy())
        self.setTabOrder(self.csbPolviFleksioVatsamakuuVas.focusProxy(), self.csbPolviRectusCatchOik.focusProxy())
        self.setTabOrder(self.csbPolviRectusCatchOik.focusProxy(), self.csbPolviRectusCatchVas.focusProxy())
        self.setTabOrder(self.csbPolviRectusCatchVas.focusProxy(), self.cbPolviRectusModAOik)
        self.setTabOrder(self.cbPolviRectusModAOik, self.cbPolviRectusModAVas)
        self.setTabOrder(self.cbPolviRectusModAVas, self.csbPolviHamstringCatchOik.focusProxy())
        self.setTabOrder(self.csbPolviHamstringCatchOik.focusProxy(), self.csbPolviPopliteaVastakkLonkka0Oik.focusProxy())
        self.setTabOrder(self.csbPolviPopliteaVastakkLonkka0Oik.focusProxy(), self.csbPolviPopliteaVastakkLonkka90Oik.focusProxy())
        self.setTabOrder(self.csbPolviPopliteaVastakkLonkka90Oik.focusProxy(), self.csbPolviHamstringCatchVas.focusProxy())
        self.setTabOrder(self.csbPolviHamstringCatchVas.focusProxy(), self.csbPolviPopliteaVastakkLonkka0Vas.focusProxy())
        self.setTabOrder(self.csbPolviPopliteaVastakkLonkka0Vas.focusProxy(), self.csbPolviPopliteaVastakkLonkka90Vas.focusProxy())
        self.setTabOrder(self.csbPolviPopliteaVastakkLonkka90Vas.focusProxy(), self.cbPolviHamstringModAOik)
        self.setTabOrder(self.cbPolviHamstringModAOik, self.cbPolviHamstringModAVas)
        self.setTabOrder(self.cbPolviHamstringModAVas, self.csbNilkkaSoleusCatchOik.focusProxy())
        self.setTabOrder(self.csbNilkkaSoleusCatchOik.focusProxy(), self.xbNilkkaSoleusKlonusOik)
        self.setTabOrder(self.xbNilkkaSoleusKlonusOik, self.csbNilkkaDorsifPolvi90PROMOik.focusProxy())
        self.setTabOrder(self.csbNilkkaDorsifPolvi90PROMOik.focusProxy(), self.csbNilkkaDorsifPolvi90AROMOik.focusProxy())
        self.setTabOrder(self.csbNilkkaDorsifPolvi90AROMOik.focusProxy(), self.xbNilkkaDorsifPolvi90AROMEversioOik)
        self.setTabOrder(self.xbNilkkaDorsifPolvi90AROMEversioOik, self.cbNilkkaSoleusModAOik)
        self.setTabOrder(self.cbNilkkaSoleusModAOik, self.csbNilkkaGastroCatchOik.focusProxy())
        self.setTabOrder(self.csbNilkkaGastroCatchOik.focusProxy(), self.xbNilkkaGastroKlonusOik)
        self.setTabOrder(self.xbNilkkaGastroKlonusOik, self.csbNilkkaDorsifPolvi0PROMOik.focusProxy())
        self.setTabOrder(self.csbNilkkaDorsifPolvi0PROMOik.focusProxy(), self.csbNilkkaDorsifPolvi0AROMOik.focusProxy())
        self.setTabOrder(self.csbNilkkaDorsifPolvi0AROMOik.focusProxy(), self.xbNilkkaDorsifPolvi0AROMEversioOik)
        self.setTabOrder(self.xbNilkkaDorsifPolvi0AROMEversioOik, self.cbNilkkaGastroModAOik)
        self.setTabOrder(self.cbNilkkaGastroModAOik, self.csbNilkkaPlantaarifleksioPROMOik.focusProxy())
        self.setTabOrder(self.csbNilkkaPlantaarifleksioPROMOik.focusProxy(), self.csbNilkkaPlantaarifleksioAROMOik.focusProxy())
        self.setTabOrder(self.csbNilkkaPlantaarifleksioAROMOik.focusProxy(), self.csbNilkkaSoleusCatchVas.focusProxy())
        self.setTabOrder(self.csbNilkkaSoleusCatchVas.focusProxy(), self.xbNilkkaSoleusKlonusVas)
        self.setTabOrder(self.xbNilkkaSoleusKlonusVas, self.csbNilkkaDorsifPolvi90PROMVas.focusProxy())
        self.setTabOrder(self.csbNilkkaDorsifPolvi90PROMVas.focusProxy(), self.csbNilkkaDorsifPolvi90AROMVas.focusProxy())
        self.setTabOrder(self.csbNilkkaDorsifPolvi90AROMVas.focusProxy(), self.xbNilkkaDorsifPolvi90AROMEversioVas)
        self.setTabOrder(self.xbNilkkaDorsifPolvi90AROMEversioVas, self.cbNilkkaSoleusModAVas)
        self.setTabOrder(self.cbNilkkaSoleusModAVas, self.csbNilkkaGastroCatchVas.focusProxy())
        self.setTabOrder(self.csbNilkkaGastroCatchVas.focusProxy(), self.xbNilkkaGastroKlonusVas)
        self.setTabOrder(self.xbNilkkaGastroKlonusVas, self.csbNilkkaDorsifPolvi0PROMVas.focusProxy())
        self.setTabOrder(self.csbNilkkaDorsifPolvi0PROMVas.focusProxy(), self.csbNilkkaDorsifPolvi0AROMVas.focusProxy())
        self.setTabOrder(self.csbNilkkaDorsifPolvi0AROMVas.focusProxy(), self.xbNilkkaDorsifPolvi0AROMEversioVas)
        self.setTabOrder(self.xbNilkkaDorsifPolvi0AROMEversioVas, self.cbNilkkaGastroModAVas)
        self.setTabOrder(self.cbNilkkaGastroModAVas, self.csbNilkkaPlantaarifleksioPROMVas.focusProxy())
        self.setTabOrder(self.csbNilkkaPlantaarifleksioPROMVas.focusProxy(), self.csbNilkkaPlantaarifleksioAROMVas.focusProxy())
        self.setTabOrder(self.csbNilkkaPlantaarifleksioAROMVas.focusProxy(), self.lnNilkkaConfusionOik)
        self.setTabOrder(self.lnNilkkaConfusionOik, self.lnNilkkaConfusionVas)
        self.setTabOrder(self.lnNilkkaConfusionVas, self.cbJalkatSubtalarOik)
        self.setTabOrder(self.cbJalkatSubtalarOik, self.cbJalkatTakaosanAsentoOik)
        self.setTabOrder(self.cbJalkatTakaosanAsentoOik, self.cbJalkatTakaosanLiikeEversioOik)
        self.setTabOrder(self.cbJalkatTakaosanLiikeEversioOik, self.cbJalkatTakaosanLiikeInversioOik)
        self.setTabOrder(self.cbJalkatTakaosanLiikeInversioOik, self.cbJalkatHolvikaariOik)
        self.setTabOrder(self.cbJalkatHolvikaariOik, self.cbJalkatKeskiosanliikeOik)
        self.setTabOrder(self.cbJalkatKeskiosanliikeOik, self.cbJalkatEtuosanAsento1Oik)
        self.setTabOrder(self.cbJalkatEtuosanAsento1Oik, self.cbJalkatEtuosanAsento2Oik)
        self.setTabOrder(self.cbJalkatEtuosanAsento2Oik, self.cbJalkat1sadeOik)
        self.setTabOrder(self.cbJalkat1sadeOik, self.spJalkat1MTPojennusOik)
        self.setTabOrder(self.spJalkat1MTPojennusOik, self.cbJalkatVaivaisenluuOik)
        self.setTabOrder(self.cbJalkatVaivaisenluuOik, self.lnJalkatKovettumatOik)
        self.setTabOrder(self.lnJalkatKovettumatOik, self.cbJalkatSubtalarVas)
        self.setTabOrder(self.cbJalkatSubtalarVas, self.cbJalkatTakaosanAsentoVas)
        self.setTabOrder(self.cbJalkatTakaosanAsentoVas, self.cbJalkatTakaosanLiikeEversioVas)
        self.setTabOrder(self.cbJalkatTakaosanLiikeEversioVas, self.cbJalkatTakaosanLiikeInversioVas)
        self.setTabOrder(self.cbJalkatTakaosanLiikeInversioVas, self.cbJalkatHolvikaariVas)
        self.setTabOrder(self.cbJalkatHolvikaariVas, self.cbJalkatKeskiosanliikeVas)
        self.setTabOrder(self.cbJalkatKeskiosanliikeVas, self.cbJalkatEtuosanAsento1Vas)
        self.setTabOrder(self.cbJalkatEtuosanAsento1Vas, self.cbJalkatEtuosanAsento2Vas)
        self.setTabOrder(self.cbJalkatEtuosanAsento2Vas, self.cbJalkat1sadeVas)
        self.setTabOrder(self.cbJalkat1sadeVas, self.spJalkat1MTPojennusVas)
        self.setTabOrder(self.spJalkat1MTPojennusVas, self.cbJalkatVaivaisenluuVas)
        self.setTabOrder(self.cbJalkatVaivaisenluuVas, self.lnJalkatKovettumatVas)
        self.setTabOrder(self.lnJalkatKovettumatVas, self.cbJalkatTakaosanAsentoKuormOik)
        self.setTabOrder(self.cbJalkatTakaosanAsentoKuormOik, self.cbJalkatTakaosanKiertoKuormOik)
        self.setTabOrder(self.cbJalkatTakaosanKiertoKuormOik, self.cbJalkatKeskiosanAsentoKuormOik)
        self.setTabOrder(self.cbJalkatKeskiosanAsentoKuormOik, self.cbJalkatEtuosanAsento1KuormOik)
        self.setTabOrder(self.cbJalkatEtuosanAsento1KuormOik, self.cbJalkatEtuosanAsento2KuormOik)
        self.setTabOrder(self.cbJalkatEtuosanAsento2KuormOik, self.cbJalkatFeissinLinjaOik)
        self.setTabOrder(self.cbJalkatFeissinLinjaOik, self.lnJalkatColemanOik)
        self.setTabOrder(self.lnJalkatColemanOik, self.xbPainelevy)
        self.setTabOrder(self.xbPainelevy, self.cbJalkatTakaosanAsentoKuormVas)
        self.setTabOrder(self.cbJalkatTakaosanAsentoKuormVas, self.cbJalkatTakaosanKiertoKuormVas)
        self.setTabOrder(self.cbJalkatTakaosanKiertoKuormVas, self.cbJalkatKeskiosanAsentoKuormVas)
        self.setTabOrder(self.cbJalkatKeskiosanAsentoKuormVas, self.cbJalkatEtuosanAsento1KuormVas)
        self.setTabOrder(self.cbJalkatEtuosanAsento1KuormVas, self.cbJalkatEtuosanAsento2KuormVas)
        self.setTabOrder(self.cbJalkatEtuosanAsento2KuormVas, self.cbJalkatFeissinLinjaVas)
        self.setTabOrder(self.cbJalkatFeissinLinjaVas, self.lnJalkatColemanVas)
        self.setTabOrder(self.lnJalkatColemanVas, self.cbVoimaLonkkaEkstensioPolvi0Oik)
        self.setTabOrder(self.cbVoimaLonkkaEkstensioPolvi0Oik, self.cbVoimaLonkkaEkstensioPolvi0Vas)
        self.setTabOrder(self.cbVoimaLonkkaEkstensioPolvi0Vas, self.cbSelLonkkaEkstensioPolvi0Oik)
        self.setTabOrder(self.cbSelLonkkaEkstensioPolvi0Oik, self.cbSelLonkkaEkstensioPolvi0Vas)
        self.setTabOrder(self.cbSelLonkkaEkstensioPolvi0Vas, self.cbVoimaLonkkaEkstensioPolvi90Oik)
        self.setTabOrder(self.cbVoimaLonkkaEkstensioPolvi90Oik, self.cbVoimaLonkkaEkstensioPolvi90Vas)
        self.setTabOrder(self.cbVoimaLonkkaEkstensioPolvi90Vas, self.cbSelLonkkaEkstensioPolvi90Oik)
        self.setTabOrder(self.cbSelLonkkaEkstensioPolvi90Oik, self.cbSelLonkkaEkstensioPolvi90Vas)
        self.setTabOrder(self.cbSelLonkkaEkstensioPolvi90Vas, self.cbVoimaPolviFleksioOik)
        self.setTabOrder(self.cbVoimaPolviFleksioOik, self.cbVoimaPolviFleksioVas)
        self.setTabOrder(self.cbVoimaPolviFleksioVas, self.cbSelPolviFleksioOik)
        self.setTabOrder(self.cbSelPolviFleksioOik, self.cbSelPolviFleksioVas)
        self.setTabOrder(self.cbSelPolviFleksioVas, self.cbVoimaLonkkaAbduktioLonkka0Oik)
        self.setTabOrder(self.cbVoimaLonkkaAbduktioLonkka0Oik, self.cbVoimaLonkkaAbduktioLonkka0Vas)
        self.setTabOrder(self.cbVoimaLonkkaAbduktioLonkka0Vas, self.cbSelLonkkaAbduktioLonkka0Oik)
        self.setTabOrder(self.cbSelLonkkaAbduktioLonkka0Oik, self.cbSelLonkkaAbduktioLonkka0Vas)
        self.setTabOrder(self.cbSelLonkkaAbduktioLonkka0Vas, self.cbVoimaLonkkaAbduktioLonkkaFleksOik)
        self.setTabOrder(self.cbVoimaLonkkaAbduktioLonkkaFleksOik, self.cbVoimaLonkkaAbduktioLonkkaFleksVas)
        self.setTabOrder(self.cbVoimaLonkkaAbduktioLonkkaFleksVas, self.cbVoimaLonkkaAdduktioOik)
        self.setTabOrder(self.cbVoimaLonkkaAdduktioOik, self.cbVoimaLonkkaAdduktioVas)
        self.setTabOrder(self.cbVoimaLonkkaAdduktioVas, self.cbSelLonkkaAdduktioOik)
        self.setTabOrder(self.cbSelLonkkaAdduktioOik, self.cbSelLonkkaAdduktioVas)
        self.setTabOrder(self.cbSelLonkkaAdduktioVas, self.cbVoimaSelka)
        self.setTabOrder(self.cbVoimaSelka, self.cbVoimaVatsaSuorat)
        self.setTabOrder(self.cbVoimaVatsaSuorat, self.cbVoimaVatsaVinotOik)
        self.setTabOrder(self.cbVoimaVatsaVinotOik, self.cbVoimaVatsaVinotVas)
        self.setTabOrder(self.cbVoimaVatsaVinotVas, self.cbVoimaLonkkaFleksioOik)
        self.setTabOrder(self.cbVoimaLonkkaFleksioOik, self.cbVoimaLonkkaFleksioVas)
        self.setTabOrder(self.cbVoimaLonkkaFleksioVas, self.cbSelLonkkaFleksioOik)
        self.setTabOrder(self.cbSelLonkkaFleksioOik, self.cbSelLonkkaFleksioVas)
        self.setTabOrder(self.cbSelLonkkaFleksioVas, self.cbVoimaPolviEkstensioOik)
        self.setTabOrder(self.cbVoimaPolviEkstensioOik, self.cbVoimaPolviEkstensioVas)
        self.setTabOrder(self.cbVoimaPolviEkstensioVas, self.cbSelPolviEkstensioOik)
        self.setTabOrder(self.cbSelPolviEkstensioOik, self.cbSelPolviEkstensioVas)
        self.setTabOrder(self.cbSelPolviEkstensioVas, self.cbVoimaLonkkaUlkokiertoOik)
        self.setTabOrder(self.cbVoimaLonkkaUlkokiertoOik, self.cbVoimaLonkkaUlkokiertoVas)
        self.setTabOrder(self.cbVoimaLonkkaUlkokiertoVas, self.cbSelLonkkaUlkokiertoOik)
        self.setTabOrder(self.cbSelLonkkaUlkokiertoOik, self.cbSelLonkkaUlkokiertoVas)
        self.setTabOrder(self.cbSelLonkkaUlkokiertoVas, self.cbVoimaLonkkaSisakiertoOik)
        self.setTabOrder(self.cbVoimaLonkkaSisakiertoOik, self.cbVoimaLonkkaSisakiertoVas)
        self.setTabOrder(self.cbVoimaLonkkaSisakiertoVas, self.cbSelLonkkaSisakiertoOik)
        self.setTabOrder(self.cbSelLonkkaSisakiertoOik, self.cbSelLonkkaSisakiertoVas)
        self.setTabOrder(self.cbSelLonkkaSisakiertoVas, self.cbVoimaTibialisAnteriorOik)
        self.setTabOrder(self.cbVoimaTibialisAnteriorOik, self.cbVoimaTibialisAnteriorVas)
        self.setTabOrder(self.cbVoimaTibialisAnteriorVas, self.cbSelTibialisAnteriorOik)
        self.setTabOrder(self.cbSelTibialisAnteriorOik, self.cbSelTibialisAnteriorVas)
        self.setTabOrder(self.cbSelTibialisAnteriorVas, self.cbVoimaTibialisPosteriorOik)
        self.setTabOrder(self.cbVoimaTibialisPosteriorOik, self.cbVoimaTibialisPosteriorVas)
        self.setTabOrder(self.cbVoimaTibialisPosteriorVas, self.cbSelTibialisPosteriorOik)
        self.setTabOrder(self.cbSelTibialisPosteriorOik, self.cbSelTibialisPosteriorVas)
        self.setTabOrder(self.cbSelTibialisPosteriorVas, self.cbVoimaPeroneusOik)
        self.setTabOrder(self.cbVoimaPeroneusOik, self.cbVoimaPeroneusVas)
        self.setTabOrder(self.cbVoimaPeroneusVas, self.cbSelPeroneusOik)
        self.setTabOrder(self.cbSelPeroneusOik, self.cbSelPeroneusVas)
        self.setTabOrder(self.cbSelPeroneusVas, self.cbVoimaExtHallucisLongusOik)
        self.setTabOrder(self.cbVoimaExtHallucisLongusOik, self.cbVoimaExtHallucisLongusVas)
        self.setTabOrder(self.cbVoimaExtHallucisLongusVas, self.cbSelExtHallucisLongusOik)
        self.setTabOrder(self.cbSelExtHallucisLongusOik, self.cbSelExtHallucisLongusVas)
        self.setTabOrder(self.cbSelExtHallucisLongusVas, self.cbVoimaFlexHallucisLongusOik)
        self.setTabOrder(self.cbVoimaFlexHallucisLongusOik, self.cbVoimaFlexHallucisLongusVas)
        self.setTabOrder(self.cbVoimaFlexHallucisLongusVas, self.cbSelFlexHallucisLongusOik)
        self.setTabOrder(self.cbSelFlexHallucisLongusOik, self.cbSelFlexHallucisLongusVas)
        self.setTabOrder(self.cbSelFlexHallucisLongusVas, self.cbVoima25OjennusOik)
        self.setTabOrder(self.cbVoima25OjennusOik, self.cbVoima25OjennusVas)
        self.setTabOrder(self.cbVoima25OjennusVas, self.cbSel25OjennusOik)
        self.setTabOrder(self.cbSel25OjennusOik, self.cbSel25OjennusVas)
        self.setTabOrder(self.cbSel25OjennusVas, self.cbVoima25KoukistusOik)
        self.setTabOrder(self.cbVoima25KoukistusOik, self.cbVoima25KoukistusVas)
        self.setTabOrder(self.cbVoima25KoukistusVas, self.cbSel25KoukistusOik)
        self.setTabOrder(self.cbSel25KoukistusOik, self.cbSel25KoukistusVas)
        self.setTabOrder(self.cbSel25KoukistusVas, self.cbVoimaGastroOik)
        self.setTabOrder(self.cbVoimaGastroOik, self.cbVoimaGastroVas)
        self.setTabOrder(self.cbVoimaGastroVas, self.cbSelGastroOik)
        self.setTabOrder(self.cbSelGastroOik, self.cbSelGastroVas)
        self.setTabOrder(self.cbSelGastroVas, self.cbVoimaSoleusOik)
        self.setTabOrder(self.cbVoimaSoleusOik, self.cbVoimaSoleusVas)
        self.setTabOrder(self.cbVoimaSoleusVas, self.cbSelSoleusOik)
        self.setTabOrder(self.cbSelSoleusOik, self.cbSelSoleusVas)
        self.setTabOrder(self.cbSelSoleusVas, self.spVirheasAnteversioOik)
        self.setTabOrder(self.spVirheasAnteversioOik, self.spVirheasAnteversioVas)
        self.setTabOrder(self.spVirheasAnteversioVas, self.spVirheasPatellaAltaOik)
        self.setTabOrder(self.spVirheasPatellaAltaOik, self.spVirheasPatellaAltaVas)
        self.setTabOrder(self.spVirheasPatellaAltaVas, self.lnPolvenValgusOik)
        self.setTabOrder(self.lnPolvenValgusOik, self.lnPolvenValgusVas)
        self.setTabOrder(self.lnPolvenValgusVas, self.spQkulmaOik)
        self.setTabOrder(self.spQkulmaOik, self.spQkulmaVas)
        self.setTabOrder(self.spQkulmaVas, self.spVirheasJalkaReisiOik)
        self.setTabOrder(self.spVirheasJalkaReisiOik, self.spVirheasJalkaReisiVas)
        self.setTabOrder(self.spVirheasJalkaReisiVas, self.spVirheasJalkateraEtuTakaOik)
        self.setTabOrder(self.spVirheasJalkateraEtuTakaOik, self.spVirheasJalkateraEtuTakaVas)
        self.setTabOrder(self.spVirheasJalkateraEtuTakaVas, self.spVirheasBimalleoliOik)
        self.setTabOrder(self.spVirheasBimalleoliOik, self.spVirheasBimalleoliVas)
        self.setTabOrder(self.spVirheasBimalleoliVas, self.spVirheas2ndtoeOik)
        self.setTabOrder(self.spVirheas2ndtoeOik, self.spVirheas2ndtoeVas)
        self.setTabOrder(self.spVirheas2ndtoeVas, self.spTasapOik)
        self.setTabOrder(self.spTasapOik, self.spTasapVas)

        
    def set_constants(self):
        self.not_measured_text = u'Ei mitattu'
        self.checkbox_yestext = u'Kyllä'
        self.checkbox_notext = u'EI'
        # Set dirs according to platform
        if sys.platform == 'win32':
            self.tmp_fldr = '/Temp'
            self.data_root_fldr = 'C:/'
        else:  # Linux
            self.tmp_fldr = '/tmp'
            self.data_root_fldr = '/'
        self.tmpfile = self.tmp_fldr + '/liikelaajuus_tmp.json'
        # exceptions that might be generated when parsing and loading/saving json
        # these should all be caught
        self.json_io_exceptions = (UnicodeDecodeError, EOFError, IOError, TypeError)
        self.json_filter = u'JSON files (*.json)'
        self.text_filter = u'Text files (*.txt)'
        self.global_fontsize = 13
        self.traceback_file = 'traceback.txt'
        
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
        # DEBUG
        #self.btnReport.clicked.connect(self.make_report)
        self.btnReport.clicked.connect(self.save_report_dialog)
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
            # DEBUG: make report on every widget update
            #self.make_report()
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
            except self.json_io_exceptions:
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
            except self.json_io_exceptions:
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
        """ Save form input data into temporary backup file. Exceptions will be caught
        by the fatal exception mechanism. """
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
    eapp = EntryApp()
   
    def my_excepthook(type, value, tback):
        """ Custom exception handler for fatal (unhandled) exceptions: 
        report to user via GUI and terminate. """
        tb_full = u''.join(traceback.format_exception(type, value, tback))
        eapp.message_dialog(ll_msgs.unhandled_exception+tb_full)
        # dump traceback to file
        try:
            with io.open(eapp.traceback_file, 'w', encoding='utf-8') as f:
                f.write(tb_full)
        # here is a danger of infinitely looping the exception hook,
        # so try to catch any exceptions...
        except Exception:
            print('Cannot dump traceback!')
        sys.__excepthook__(type, value, tback) 
        app.quit()
        
    sys.excepthook = my_excepthook
    
    eapp.show()
    app.exec_()

if __name__ == '__main__':
    main()
    
    


    
