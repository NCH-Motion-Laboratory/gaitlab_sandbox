# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 18:56:52 2016

Qt Designer plugin for checkspinbox

@author: jussi
"""

from liikelaajuus import CheckDegSpinBox
from PyQt4 import QtGui, QtCore, QtDesigner


class CheckDegSpinBoxPlugin(QtDesigner.QPyDesignerCustomWidgetPlugin):
    
    def __init__(self, parent = None):
        
        QtDesigner.QPyDesignerCustomWidgetPlugin.__init__(self)
        
        self.initialized = False
        
        
    def initialize(self, core):
        
        if self.initialized:
            return
            
        self.initialized = True
        
    def isInitialized(self):
        
        return self.initialized
    
    def createWidget(self, parent):
        return CheckDegSpinBox(parent)
        
    def name(self):
        return "CheckDegSpinBox"
        
    def group(self):
        return "PyQt Examples"
        
    def isContainer(self):
        return False
        
    def includeFile(self):
        return "liikelaajuus"
        