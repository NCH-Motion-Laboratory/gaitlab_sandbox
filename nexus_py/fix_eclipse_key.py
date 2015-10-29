# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 11:17:45 2015

Utility to fix unwanted Eclipse entries.
Fixes all enf files in current Nexus directory.

Be careful! Overwrites files without asking anything.

@author: jussi
"""


import gp.getdata 
import glob
import sys

KEY = 'DESCRIPTION'  # Eclipse key
OLDVAL = 'unipedal right'  # change keys with this value
NEWVAL = ''      # change into this value
ENF_GLOB = '*Trial*enf'

sessionpath = 'C://some_trial_dir//'
enffiles = glob.glob(sessionpath+ENF_GLOB)

if not enffiles:
    sys.exit('No enf files in {0}'.format(sessionpath))

for enffile in enffiles:
    gp.getdata.set_eclipse_key(enffile, KEY, OLDVAL, NEWVAL)
    
    
        


