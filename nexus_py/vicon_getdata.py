# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:41:31 2015

Utility classes for reading data from Vicon Nexus.
TODO: fix naming conventions (vars lower_case, class names CamelCase)

@author: Jussi
"""

from __future__ import division, print_function

import numpy as np
from scipy import signal

class vicon_emg:
    """ Class for reading and processing EMG data from Nexus. """

    def __init__(self, vicon):
        # default plotting scale in medians (channel-specific)
        yscale_medians = 9
        # find EMG device and get some info
        framerate = vicon.GetFrameRate()
        framecount = vicon.GetFrameCount()
        emgdevname = 'Myon'
        devnames = vicon.GetDeviceNames()
        if emgdevname in devnames:
            emg_id = vicon.GetDeviceIDFromName(emgdevname)
        else:
           raise Exception('no EMG device found in trial')
        # DType should be 'other', drate is sampling rate
        dname,dtype,drate,outputids,_,_ = vicon.GetDeviceDetails(emg_id)
        samplesperframe = drate / framerate
        # Myon should only have 1 output; if zero, EMG was not found
        assert(len(outputids)==1)
        outputid = outputids[0]
        # list of channel names and IDs
        _,_,_,_,self.chnames,self.chids = vicon.GetDeviceOutputDetails(emg_id, outputid)
        for i in range(len(self.chnames)):
            chname = self.chnames[i]    
            assert(chname.find('Voltage') == 0), 'Not a voltage channel?'
            chname = chname[chname.find('.')+1:]  # remove 'Voltage.'
            self.chnames[i] = chname
        # read EMG channels into dict
        # also cut data to L/R gait cycles
        self.data = {}
        self.yscalegc1l = {}        
        self.yscalegc1r = {}            
        vgc1 = vicon_gaitcycle(vicon)
        self.datagc1l = {}
        self.datagc1r = {}
        # gait cycle beginning and end, samples
        self.lgc1start_s = int(round((vgc1.lgc1start - 1) * samplesperframe))
        self.lgc1end_s = int(round((vgc1.lgc1end - 1) * samplesperframe))
        self.rgc1start_s = int(round((vgc1.rgc1start - 1) * samplesperframe))
        self.rgc1end_s = int(round((vgc1.rgc1end - 1) * samplesperframe))
        self.lgc1len_s = self.lgc1end_s - self.lgc1start_s
        self.rgc1len_s = self.rgc1end_s - self.rgc1start_s

        for chid in self.chids:
            chdata, chready, chrate = vicon.GetDeviceChannel(emg_id, outputid, chid)
            assert(chrate == drate), 'Channel has an unexpected sampling rate'
            # remove 'Voltage.' from beginning of dict key
            chname = self.chnames[chid-1]
            self.data[chname] = np.array(chdata)
            # convert gait cycle times (in frames) to sample indices
            # cut to L/R gait cycles. no interpolation
            self.datagc1l[chname] = np.array(chdata[self.lgc1start_s:self.lgc1end_s])
            self.datagc1r[chname] = np.array(chdata[self.rgc1start_s:self.rgc1end_s])
            # compute scales of EMG signal, to be used as y scaling of plots
            self.yscalegc1l[chname] = yscale_medians * np.median(np.abs(self.datagc1l[chname]))
            self.yscalegc1r[chname] = yscale_medians * np.median(np.abs(self.datagc1r[chname]))
          
        self.datalen = len(chdata)
        assert(self.datalen == framecount * samplesperframe)
        self.sfrate = drate        
        # samples to time (s)
        self.t = np.arange(self.datalen)/self.sfrate
        
    def filter(self, y, passband):
        """ Bandpass filter given data y to passband, e.g. [1, 40] 
        Passband is given in Hz. """
        passbandn = np.array(passband) / self.sfrate / 2
        b, a = signal.butter(4, passbandn, 'bandpass')
        yfilt = signal.filtfilt(b, a, y)        
        return y #DEBUG

    def findchs(self, str):
        """ Return list of channels whose names contain the given 
        string str. """
        return [chn for chn in self.chnames if chn.find(str) > -1]
        

class vicon_gaitcycle:
    """ Determines 1st L/R gait cycles from data. Can also normalize
    vars to 0..100% of gait cycle. """
    
    def __init__(self,vicon):
        subjectname = vicon.GetSubjectNames()[0]
        # figure out gait cycle
        # frames where foot strikes occur (1-frame discrepancies with Nexus?)
        self.lfstrikes = vicon.GetEvents(subjectname, "Left", "Foot Strike")[0]
        self.rfstrikes = vicon.GetEvents(subjectname, "Right", "Foot Strike")[0]
        # 2 strikes is one complete gait cycle, needed for analysis
        lenLFS = len(self.lfstrikes)
        lenRFS = len(self.rfstrikes)
        if lenLFS and lenRFS < 2:
            raise Exception("Could not detect complete L/R gait cycles")
        # extract times for 1st gait cycles, L and R
        self.lgc1start = min(self.lfstrikes[0:2])
        self.lgc1end = max(self.lfstrikes[0:2])
        self.lgc1len = self.lgc1end-self.lgc1start
        self.rgc1start = min(self.rfstrikes[0:2])
        self.rgc1end = max(self.rfstrikes[0:2])
        self.rgc1len = self.rgc1end-self.rgc1start
        self.tn = np.linspace(0, 100, 101)
        
    def cut(self, y):
        """ Cut a varible to left or right gait cycle, without interpolation. """
        
    def normalize(self, y, side):
        """ Interpolate any variable y to left or right gait cycle.
        New x axis will be 0..100, and data is taken from the specified 
        gait cycle (side = L or R). """
        lgc1t = np.linspace(0, 100, self.lgc1len)
        rgc1t = np.linspace(0, 100, self.rgc1len)
        if side.upper() == 'R':  # norm to right side
            gc1t = rgc1t
            tstart = self.rgc1start
            tend = self.rgc1end
        else:  # to left side
            gc1t = lgc1t
            tstart = self.lgc1start
            tend = self.lgc1end
        # interpolate variable to gait cycle
        yip = np.interp(self.tn, gc1t, y[tstart:tend])
        return yip
        
    def detect_side(self, vicon):
        """ Try to detect whether the trial has L or R forceplate strike
        (or both). Simple heuristic is to look at the forceplate data about
        150 ms after foot strike. """
        delay_ms = 150
        framerate = vicon.GetFrameRate()
        framecount = vicon.GetFrameCount()
        fpdevicename = 'Forceplate'
        devicenames = vicon.GetDeviceNames()
        if fpdevicename in devicenames:
            fpid = vicon.GetDeviceIDFromName(fpdevicename)
        else:
           raise Exception('No forceplate device found in trial!')
        # DType should be 'ForcePlate', drate is sampling rate
        dname,dtype,drate,outputids,_,_ = vicon.GetDeviceDetails(fpid)
        samplesperframe = drate / framerate  # fp samples per Vicon frame
        assert(len(outputids)==3)
        # outputs should be force, moment, cop. select force
        outputid = outputids[0]
        # get list of channel names and IDs
        _,_,_,_,chnames,chids = vicon.GetDeviceOutputDetails(fpid, outputid)
        # read x,y,z forces
        Fxid = vicon.GetDeviceChannelIDFromName(fpid, outputid, 'Fx')
        forcex, chready, chrate = vicon.GetDeviceChannel(fpid, outputid, Fxid)
        Fxid = vicon.GetDeviceChannelIDFromName(fpid, outputid, 'Fy')
        forcey, chready, chrate = vicon.GetDeviceChannel(fpid, outputid, Fxid)
        Fxid = vicon.GetDeviceChannelIDFromName(fpid, outputid, 'Fz')
        forcez, chready, chrate = vicon.GetDeviceChannel(fpid, outputid, Fxid)
        forceall = np.array([forcex,forcey,forcez])
        forcetot = np.sqrt(sum(forceall**2,1))
        # get forces during foot strike events        
        lfsind = np.array(self.lfstrikes) * samplesperframe
        rfsind = np.array(self.rfstrikes) * samplesperframe
        delay = int(delay_ms/1000. * drate)
        lfsforces = forcetot[lfsind.astype(int) + delay]
        rfsforces = forcetot[rfsind.astype(int) + delay]
        print('Total force', delay_ms, 'ms after foot strikes:')
        print('Left: ', lfsforces)
        print('Right: ', rfsforces)
        if max(lfsforces) > max(rfsforces):
            return 'L'
        else:
            return 'R'


class vicon_pig_outputs:
    """ Reads given plug-in gait output variables (in varlist). Variable 
    names starting with 'R' and'L' are normalized into left and right 
    gait cycles, respectively. Can also use special keywords 'PiGLBKinetics'
    and 'PiGLBKinematics' for varlist, to get predefined variables. """
    def __init__(self, vicon, varlist):
        if varlist == 'PiGLBKinetics':
            varlist = ['LHipMoment',
              'LKneeMoment',
              'LAnkleMoment',
              'LHipPower',
              'LKneePower',
              'LAnklePower',
              'RHipMoment',
              'RKneeMoment',
              'RAnkleMoment',
              'RHipPower',
              'RKneePower',
              'RAnklePower']
        if varlist == 'PiGLBKinematics':
            varlist = ['LHipAngles',
                     'LKneeAngles',
                     'LAbsAnkleAngle',
                     'LAnkleAngles',
                     'LPelvisAngles',
                     'LFootProgressAngles',
                     'RHipAngles',
                     'RKneeAngles',
                     'RAbsAnkleAngle',
                     'RAnkleAngles',
                     'RPelvisAngles',
                     'RFootProgressAngles']
        SubjectName = vicon.GetSubjectNames()[0]
        # get gait cycle info 
        vgc1 = vicon_gaitcycle(vicon)
         # read all kinematics vars into dict and normalize into gait cycle 1
        self.Vars = {}
        for Var in varlist:
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
            
    
    
    
