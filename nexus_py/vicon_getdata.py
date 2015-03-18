# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:41:31 2015

Utility classes for reading data from Vicon Nexus.

@author: Jussi
"""

from __future__ import division, print_function

import numpy as np
from scipy import signal

class vicon_emg:
    """ Class for reading and processing EMG data from Nexus. """

    def __init__(self, vicon):
        # find EMG device and get some info
        FrameRate = vicon.GetFrameRate()
        FrameCount = vicon.GetFrameCount()
        EMGDeviceName = 'Myon'
        DeviceNames = vicon.GetDeviceNames()
        if EMGDeviceName in DeviceNames:
            EMGDeviceID = vicon.GetDeviceIDFromName(EMGDeviceName)
        else:
           raise Exception('no EMG device found in trial')
        # DType should be 'other', Drate is sampling rate
        DName,DType,DRate,OutputIDs,_,_ = vicon.GetDeviceDetails(EMGDeviceID)
        #
        SamplesPerFrame = DRate / FrameRate
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
        # also cut data to L/R gait cycles
        self.data = {}
        self.yScaleGC1L = {}        
        self.yScaleGC1R = {}            
        vgc1 = vicon_gaitcycle(vicon)
        self.dataGC1L = {}
        self.dataGC1R = {}
        # gait cycle beginning and end, samples
        self.LGC1Start_s = int(round((vgc1.LGC1Start - 1) * SamplesPerFrame))
        self.LGC1End_s = int(round((vgc1.LGC1End - 1) * SamplesPerFrame))
        self.RGC1Start_s = int(round((vgc1.RGC1Start - 1) * SamplesPerFrame))
        self.RGC1End_s = int(round((vgc1.RGC1End - 1) * SamplesPerFrame))
        self.LGC1Len_s = self.LGC1End_s - self.LGC1Start_s
        self.RGC1Len_s = self.RGC1End_s - self.RGC1Start_s

        for chID in self.chIDs:
            chData, chReady, chRate = vicon.GetDeviceChannel(EMGDeviceID, OutputID, chID)
            assert(chRate == DRate), 'Channel has an unexpected sampling rate'
            # remove 'Voltage.' from beginning of dict key
            chName = self.chNames[chID-1]
            self.data[chName] = np.array(chData)
            # convert gait cycle times (in frames) to sample indices
            # cut to L/R gait cycles
            self.dataGC1L[chName] = np.array(chData[self.LGC1Start_s:self.LGC1End_s])
            self.dataGC1R[chName] = np.array(chData[self.RGC1Start_s:self.RGC1End_s])
            # compute scales of EMG signal, to be used as y scaling of plots
            self.yScaleGC1L[chName] = 3*np.median(np.abs(self.dataGC1L[chName]))
            self.yScaleGC1R[chName] = 3*np.median(np.abs(self.dataGC1R[chName]))
          
        self.dataLen = len(chData)
        assert(self.dataLen == FrameCount * SamplesPerFrame)
        self.sfRate = DRate        
        # samples to time (s)
        self.t = np.arange(self.dataLen)/self.sfRate
        
    def filter(self, y, passband):
        """ Bandpass filter given data y to passband, e.g. [1, 40] 
        Passband is given in Hz. """
        passbandn = np.array(passband) / self.sfRate / 2
        b, a = signal.butter(4, passbandn, 'bandpass')
        yfilt = signal.filtfilt(b, a, y)        
        return yfilt
        

class vicon_gaitcycle:
    """ Determines 1st L/R gait cycles from data. Can also normalize
    vars to 0..100% of gait cycle. """
    
    def __init__(self,vicon):
        SubjectName = vicon.GetSubjectNames()[0]
        # figure out gait cycle
        # frames where foot strikes occur (1-frame discrepancies with Nexus?)
        LFStrike = vicon.GetEvents(SubjectName, "Left", "Foot Strike")[0]
        RFStrike = vicon.GetEvents(SubjectName, "Right", "Foot Strike")[0]
        # 2 strikes is one complete gait cycle, needed for analysis
        lenLFS = len(LFStrike)
        lenRFS = len(RFStrike)
        if lenLFS and lenRFS < 2:
            raise Exception("Could not detect complete L/R gait cycles")
        # extract times for 1st gait cycles, L and R
        self.LGC1Start=min(LFStrike[0:2])
        self.LGC1End=max(LFStrike[0:2])
        self.LGC1Len=self.LGC1End-self.LGC1Start
        self.RGC1Start=min(RFStrike[0:2])
        self.RGC1End=max(RFStrike[0:2])
        self.RGC1Len=self.RGC1End-self.RGC1Start
        self.tn = np.linspace(0, 100, 101)
        
    def cut(self, y):
        """ Cut a varible to left or right gait cycle, without interpolation. """
        
    def normalize(self, y, side):
        """ Interpolate any variable y to left or right gait cycle.
        New x axis will be 0..100, and data is taken from the specified 
        gait cycle (side = L or R). """
        LGC1t = np.linspace(0, 100, self.LGC1Len)
        RGC1t = np.linspace(0, 100, self.RGC1Len)
        if side.upper() == 'R':  # norm to right side
            GC1t = RGC1t
            tStart = self.RGC1Start
            tEnd = self.RGC1End
        else:  # to left side
            GC1t = LGC1t
            tStart = self.LGC1Start
            tEnd = self.LGC1End
        # interpolate variable to gait cycle
        yip = np.interp(self.tn, GC1t, y[tStart:tEnd])
        return yip


class vicon_pig_outputs:
    """ Reads given plug-in gait output variables. Variable names starting
    with 'R' and'L' are normalized into left and right gait cycles,
    respectively."""
    def __init__(self, vicon, VarList):
        SubjectName = vicon.GetSubjectNames()[0]
        # get gait cycle info 
        vgc1 = vicon_gaitcycle(vicon)
         # read all kinematics vars into dict and normalize into gait cycle 1
        self.Vars = {}
        for Var in VarList:
            # not sure what the BoolVals are, discard for now
            NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
            self.Vars[Var] = np.array(NumVals)
            # moment variables have to be divided by 1000 - not sure why    
            if Var.find('Moment') > 0:
                self.Vars[Var] /= 1000.
            # pick non-normalized X,Y,Z components into separate vars
            self.Vars[Var+'X'] = self.Vars[Var][0,:]
            self.Vars[Var+'Y'] = self.Vars[Var][1,:]
            self.Vars[Var+'Z'] = self.Vars[Var][2,:]
            # normalize vars to gait cycle 1
            side = Var[0]  # L or R
            self.Vars['Norm'+Var+'X'] = vgc1.normalize(self.Vars[Var+'X'], side)
            self.Vars['Norm'+Var+'Y'] = vgc1.normalize(self.Vars[Var+'Y'], side)
            self.Vars['Norm'+Var+'Z'] = vgc1.normalize(self.Vars[Var+'Z'], side)
            
    
    
    
