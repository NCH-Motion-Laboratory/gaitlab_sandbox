# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:23:37 2015

@author: HUS20664877
"""

from __future__ import print_function

import sys
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
color_cycle = ax._get_lines.color_cycle


while True:
    print(next(color_cycle))
    
trialpath = "C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/D0012_VS/2015_6_9_seur_tuet_VS/2015_6_9_seur_tuet_VS13.c3d"
