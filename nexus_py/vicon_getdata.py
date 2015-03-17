# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:41:31 2015

Utility functions for reading data from Vicon Nexus.

@author: Jussi
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
        # also normalize data to L/R gait cycles
        self.data = {}
        vgc1 = vicon_gaitcycle(vicon)
        self.normDataL = {}
        self.normDataR = {}
        for chID in self.chIDs:
            chData, chReady, chRate = vicon.GetDeviceChannel(EMGDeviceID, OutputID, chID)
            assert(chRate == DRate), 'Channel has an unexpected sampling rate'
            # remove 'Voltage.' from beginning of dict key
            chName = self.chNames[chID-1]
            self.data[chName] = chData
            self.normDataL[chName] = vgc1.normalize(chData,'L')
            self.normDataR[chName] = vgc1.normalize(chData,'R')
        self.dataLen = len(chData)    
        self.sfRate = DRate        
        # samples to time (s)
        self.t = np.arange(self.dataLen)/self.sfRate

class vicon_gaitcycle:
    """ Determines 1st L/R gait cycles from data. Normalizes vars to 0..100%
    of gait cycle. """
    
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
        
    def normalize(self,y,side):
        """ Normalize any variable y to left or right gait cycle. """
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
    """ Reads given PiG output variables. Variables are
    also normalized into the gait cycle. """

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
            
    
    
    
