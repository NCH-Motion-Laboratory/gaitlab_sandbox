# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 14:33:01 2015

Play with detecting events automatically from marker trajectories.

candidate markers for events:
TOE-OFF: Z and Y velocities both cross (relative?) 
threshold (after remaining around zero)

"""



import matplotlib.pyplot as plt
import numpy as np
import vicon_getdata
import sys
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import os

# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")
# PiG normal data
gcdpath = 'normal.gcd'
# if we're running from Nexus, try another place
if not os.path.isfile(gcdpath):
    gcdpath = 'C:/Users/Vicon123/Desktop/nexus_python/llinna/nexus_py/normal.gcd'


import ViconNexus
# Python objects communicate directly with the Nexus application.
# Before using the vicon object, Nexus needs to be started and a subject loaded.
vicon = ViconNexus.ViconNexus()
subjectname = vicon.GetSubjectNames()[0]
sessionpath = vicon.GetTrialName()[0]
trialname = vicon.GetTrialName()[1]
pigvars = vicon.GetModelOutputNames(subjectname)

# try to detect which foot hit the forceplate
vgc = vicon_getdata.gaitcycle(vicon)
side = vgc.detect_side(vicon)
# or specify manually:
#side = 'R'

t1=vicon.GetTrajectory(subjectname,'RTOE')
x,y,z=t1[0],t1[1],t1[2]
t=range(len(x))
xd=np.diff(x)
td=range(len(xd))
plt.plot(td,xd)
