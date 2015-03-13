# -*- coding: utf-8 -*-
"""
Read EMG data from Vicon Nexus.
Works with Nexus 2.1.x
@author: jussi
"""

from __future__ import division, print_function

"""
Test the Vicon object for communicating with Vicon Nexus application.
Works with Nexus 2.1.x
@author: jussi
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")

import ViconNexus

# Python objects communicate directly with the Nexus application.
# Before using the vicon object, Nexus needs to be started and a subject loaded.
vicon = ViconNexus.ViconNexus()
SubjectName = vicon.GetSubjectNames()[0]
SessionPath = vicon.GetTrialName()[0]
TrialName = vicon.GetTrialName()[1]

# find EMG device and get some info
# error handling is tricky, since ViconNexus.py does not raise exceptions
EMGDeviceName = 'Myon'
EMGDeviceID = vicon.GetDeviceIDFromName(EMGDeviceName)
# DType should be 'other', Drate is sampling rate
DName,DType,DRate,OutputIDs,_,_ = vicon.GetDeviceDetails(EMGDeviceID)
# Myon should only have 1 output; if zero, EMG was not found
assert(len(OutputIDs)==1)
OutputID = OutputIDs[0]
# list of channel names and IDs
_,_,_,_,chNames,chIDs = vicon.GetDeviceOutputDetails(EMGDeviceID, OutputID)

for i in range(len(chNames)):
    chName = chNames[i]    
    assert(chName.find('Voltage') == 0)
    chName = chName[chName.find('.')+1:]  # remove 'Voltage.'
    chNames[i] = chName
    
# read EMG channels into dict
EMGAll = {}
for chID in chIDs:
    chData, chReady, chRate = vicon.GetDeviceChannel(EMGDeviceID, OutputID, chID)
    assert(chRate == DRate)
    # remove 'Voltage.' from beginning of dict key
    chName = chNames[chID-1]
    EMGAll[chName] = chData

dataLen = len(chData)    

# process EMG data, e.g. enveloping

# plot
t = np.arange(dataLen)/DRate

# plot
plt.figure()

assert(16 >= max(chIDs))

for k in chIDs:
    plt.subplot(4, 4, k)
    chName = EMGAll.keys()[k-1]
    plt.plot(t, EMGAll[chName], '#DC143C')
    plt.title(chName, fontsize=10)
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.show()



  
    

