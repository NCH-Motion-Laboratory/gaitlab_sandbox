# -*- coding: utf-8 -*-
"""
Read EMG data from Vicon Nexus and plot.
Works with Nexus 2.1.x
@author: jussi

TODO:
compute+plot EMG envelope¨(RMS, butterworth, ?)
better error handling
autodetect disconnected emgs?

"""

from __future__ import division, print_function

import numpy as np
import matplotlib.pyplot as plt

class vicon_emg:
    """ Class for reading and processing EMG data from Nexus. """

    def __init__(self, vicon):
        # find EMG device and get some info
        EMGDeviceName = 'Myon'
        DeviceNames = vicon.GetDeviceNames()
        if EMGDeviceName in DeviceNames:
            EMGDeviceID = vicon.GetDeviceIDFromName(EMGDeviceName)
        else:
           raise Exception('no EMG device found in trial')
        # DType should be 'other', Drate is sampling rate
        DName,DType,DRate,OutputIDs,_,_ = vicon.GetDeviceDetails(EMGDeviceID)
        # Myon should only have 1 output; if zero, EMG was not found
        assert(len(OutputIDs)==1)
        OutputID = OutputIDs[0]
        # list of channel names and IDs
        _,_,_,_,self.chNames,self.chIDs = vicon.GetDeviceOutputDetails(EMGDeviceID, OutputID)
        for i in range(len(self.chNames)):
            chName = self.chNames[i]    
            assert(chName.find('Voltage') == 0), 'Not a voltage channel?'
            chName = chName[chName.find('.')+1:]  # remove 'Voltage.'
            self.chNames[i] = chName
        # read EMG channels into dict
        self.EMGAll = {}
        for chID in self.chIDs:
            chData, chReady, chRate = vicon.GetDeviceChannel(EMGDeviceID, OutputID, chID)
            assert(chRate == DRate), 'Channel has an unexpected sampling rate'
            # remove 'Voltage.' from beginning of dict key
            chName = self.chNames[chID-1]
            self.EMGAll[chName] = chData
        self.dataLen = len(chData)    
        self.sfRate = DRate        
        # samples to time
        self.t = np.arange(self.dataLen)/self.sfRate
      
    
    def plotall(self):
        # plot everything
        plt.figure(figsize=(16, 12))
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)
        assert(16 >= max(self.chIDs))
        
        for k in self.chIDs:
            plt.subplot(4, 4, k)
            chName = self.EMGAll.keys()[k-1]
            plt.plot(self.t, self.EMGAll[chName], '#DC143C')
            plt.title(chName, fontsize=10)
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (V)')
            plt.show()


  
    

