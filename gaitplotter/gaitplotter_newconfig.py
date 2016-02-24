# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:25:38 2015

Create a new config file for Gaitplotter.

@author: Jussi
"""

from gp.config import Config
from gp.site_defs import appdir

cfg = Config(appdir)
cfg.write()


