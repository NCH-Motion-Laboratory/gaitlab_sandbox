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
    
