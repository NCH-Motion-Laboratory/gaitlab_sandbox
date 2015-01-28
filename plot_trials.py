# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 09:13:34 2015

@author: vicon123
"""

"""
Plot trial data from within Vicon Nexus.
"""
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np

#Code needed for Nexus 2.1
import sys
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")


import ViconNexus
vicon = ViconNexus.ViconNexus()

import seaborn as sns


# Extract information from active trial
SubjectName = vicon.GetSubjectNames()[0]
SessionLoc = vicon.GetTrialName()[0]

txt='''
    Subject: {subject}
    Trial: {trial}
    rivi kolme'''.format(subject=SubjectName,trial=SessionLoc)
    
fig=plt.figure()
fig.text(.1,.1,txt)
plt.show()

