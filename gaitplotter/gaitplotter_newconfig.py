# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:25:38 2015

Create a new config file for Gaitplotter.

@author: Jussi
"""

import getpass
from gp.config import Config

pathprefix = 'c:/users/' + getpass.getuser()
desktop = pathprefix + '/Desktop'
appdir = desktop + '/GaitPlotter'


cfg = Config(appdir)
cfg.write()


