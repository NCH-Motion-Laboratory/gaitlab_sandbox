# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 13:47:17 2015

@author: vicon123
"""

import ctypes  # An included library with Python install.
ctypes.windll.user32.MessageBoxA(0, "Your text", "Your title", 1)
