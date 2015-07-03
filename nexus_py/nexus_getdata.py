# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:41:31 2015

Utility classes for reading gait data.

TODO:
trial class for grouping trial-specific data?
-factor out read methods for Nexus/c3d

@author: Jussi
"""


from __future__ import division, print_function

import numpy as np
import ctypes
from scipy import signal
import sys
import psutil
import os
import gaitlab  # lab-specific stuff
import btk  # biomechanical toolkit for c3d reading


def nexus_pid():
    """ Tries to return the PID of the running Nexus process. """
    PROCNAME = "Nexus.exe"
    for proc in psutil.process_iter():
        try:
            if proc.name() == PROCNAME:
                return proc.pid
        except psutil.AccessDenied:
            pass
    return None

def error_exit(message):
    """ Custom error handler """
    # graphical error dialog - Windows specific
    ctypes.windll.user32.MessageBoxA(0, message, "Error in Nexus Python script", 0)
    sys.exit()

def messagebox(message):
    """ Custom notification handler """
    # graphical message dialog - Windows specific
    ctypes.windll.user32.MessageBoxA(0, message, "Message from Nexus Python script", 0)
    
class trial:
    """ FIXME:
     Handles a gait trial.
    -read trial data (model data, emg, forceplate, gait cycle info)
    -process data (filter etc.)
    -load normal data
    -detect side
    -cut / normalize data to gait cycles
    """

    def read_vars(self, trialpath, vars):
        pass
    
        
    
  
    
    
    
class forceplate:
    """ Read and process forceplate data. """
    
    def read_nexus(self, vicon):
        """ Read from Vicon Nexus. """
        framerate = vicon.GetFrameRate()
        framecount = vicon.GetFrameCount()
        fpdevicename = 'Forceplate'
        devicenames = vicon.GetDeviceNames()
        if fpdevicename in devicenames:
            fpid = vicon.GetDeviceIDFromName(fpdevicename)
        else:
           error_exit('No forceplate device found in trial!')
        # DType should be 'ForcePlate', drate is sampling rate
        dname,dtype,drate,outputids,_,_ = vicon.GetDeviceDetails(fpid)
        self.sfrate = drate
        self.samplesperframe = drate / framerate  # fp samples per Vicon frame
        assert(len(outputids)==3)
        # outputs should be force, moment, cop. select force
        outputid = outputids[0]
        # get list of channel names and IDs
        _,_,_,_,chnames,chids = vicon.GetDeviceOutputDetails(fpid, outputid)
        # read x,y,z forces
        Fxid = vicon.GetDeviceChannelIDFromName(fpid, outputid, 'Fx')
        self.forcex, chready, chrate = vicon.GetDeviceChannel(fpid, outputid, Fxid)
        Fxid = vicon.GetDeviceChannelIDFromName(fpid, outputid, 'Fy')
        self.forcey, chready, chrate = vicon.GetDeviceChannel(fpid, outputid, Fxid)
        Fxid = vicon.GetDeviceChannelIDFromName(fpid, outputid, 'Fz')
        self.forcez, chready, chrate = vicon.GetDeviceChannel(fpid, outputid, Fxid)
        self.forceall = np.array([self.forcex,self.forcey,self.forcez])
        self.forcetot = np.sqrt(sum(self.forceall**2,1))
    
    def read_c3d(self, c3dfile):
        """ Read from c3d file. Note: gives force on ROI. """
        reader = btk.btkAcquisitionFileReader()
        reader.SetFilename(c3dfile)  # check existence?
        reader.Update()
        acq = reader.GetOutput()
        self.frame1 = acq.GetFirstFrame()  # start of ROI (1-based)
        self.samplesperframe = acq.GetNumberAnalogSamplePerFrame()
        self.sfrate = acq.GetAnalogFrequency()
        for i in btk.Iterate(acq.GetAnalogs()):
            desc = i.GetLabel()
            if desc.find('Force.') >= 0 and i.GetUnit() == 'N':
                if desc.find('Fx') > 0:
                    self.forcex = np.squeeze(i.GetValues())  # rm singleton dimension
                elif desc.find('Fy') > 0:
                    self.forcey = np.squeeze(i.GetValues())
                elif desc.find('Fz') > 0:
                    self.forcez = np.squeeze(i.GetValues())
                    
        self.forceall = np.array([self.forcex,self.forcey,self.forcez])
        self.forcetot = np.sqrt(sum(self.forceall**2,1))

class emg:
    """ Read and process emg data. """

    def define_emg_names(self):
        """ Defines the electrode mapping. """
        self.ch_normals = gaitlab.emg_normals
        self.ch_names = gaitlab.emg_names
        self.ch_labels = gaitlab.emg_labels
                
    def emg_channelnames(self):
        """ Return names of known (logical) EMG channels. """
        return self.ch_names
       
    def is_logical_channel(self, chname):
        return chname in self.ch_names

    def __init__(self, emg_remapping=None, emg_auto_off=True):
        """ emg_remapping contains the replacement dict for EMG electrodes:
        e.g. key 'LGas'='LSol' means that LGas data will be 
        read from the LSol electrode."""
        # default plotting scale in medians (channel-specific)
        self.yscale_medians = 1
        # order of Butterworth filter
        self.buttord = 5
        # whether to auto-find disconnected EMG channels
        self.emg_auto_off = emg_auto_off
        # normal data and logical chs
        self.define_emg_names()
        self.emg_remapping = emg_remapping
        
    def read(self):
        """ Override in subclass """
        pass
            
    def is_valid_emg(self, y):
        """ Check whether channel contains valid EMG signal. """
        # max. relative interference at 50 Hz harmonics
        emg_max_interference = 50
        # detect 50 Hz harmonics
        int200 = self.filt(y, [195,205])
        int50 = self.filt(y, [45,55])
        int100 = self.filt(y, [95,105])
        # baseline emg signal
        emglevel = self.filt(y, [60,90])
        intrel = np.var(int50+int100+int200)/np.var(emglevel)
        # DEBUG
        #print('rel. interference: ', intrel)
        return intrel < emg_max_interference

    def filt(self, y, passband):
        """ Filter given data y to passband, e.g. [1, 40].
        Passband is given in Hz. None for no filtering. 
        Implemented as pure lowpass, if highpass freq = 0 """
        if passband == None:
            return y
        passbandn = 2 * np.array(passband) / self.sfrate
        if passbandn[0] > 0:  # bandpass
            b, a = signal.butter(self.buttord, passbandn, 'bandpass')
        else:  # lowpass
            b, a = signal.butter(self.buttord, passbandn[1])
        yfilt = signal.filtfilt(b, a, y)        
        return yfilt

    def findchs(self, str):
        """ Return list of channels whose name contains the given 
        string str. """
        return [chn for chn in self.elnames if chn.find(str) > -1]

    def findch(self, str):
        """ Return name of (unique) channel containing the given 
        string str. """
        chlist = [chn for chn in self.elnames if chn.find(str) > -1]
        if len(chlist) != 1:
            error_exit('Cannot find unique channel matching '+str)
        return chlist[0]
        
    def read_nexus(self, vicon):
        """ Read EMG data from a running Vicon Nexus application. """
        self.source = 'Nexus'
        framerate = vicon.GetFrameRate()
        framecount = vicon.GetFrameCount()
        emgdevname = 'Myon'
        devnames = vicon.GetDeviceNames()
        if emgdevname in devnames:
            emg_id = vicon.GetDeviceIDFromName(emgdevname)
        else:
           error_exit('No EMG device found in trial')
        # DType should be 'other', drate is sampling rate
        dname,dtype,drate,outputids,_,_ = vicon.GetDeviceDetails(emg_id)
        samplesperframe = drate / framerate
        self.sfrate = drate        
        # Myon should only have 1 output; if zero, EMG was not found
        assert(len(outputids)==1)
        outputid = outputids[0]
        # get list of channel names and IDs
        _,_,_,_,self.elnames,self.chids = vicon.GetDeviceOutputDetails(emg_id, outputid)
        # get gait cycle
        vgc1 = gaitcycle()
        vgc1.read_nexus(vicon)
        self.lgc1start_s = int(round((vgc1.lgc1start - 1) * samplesperframe))
        self.lgc1end_s = int(round((vgc1.lgc1end - 1) * samplesperframe))
        self.rgc1start_s = int(round((vgc1.rgc1start - 1) * samplesperframe))
        self.rgc1end_s = int(round((vgc1.rgc1end - 1) * samplesperframe))
        self.lgc1len_s = self.lgc1end_s - self.lgc1start_s
        self.rgc1len_s = self.rgc1end_s - self.rgc1start_s
        # read physical EMG channels and cut data to L/R gait cycles
        self.data = {}
        self.data_gc1l = {}
        self.data_gc1r = {}
        for elid in self.chids:
            eldata, elready, elrate = vicon.GetDeviceChannel(emg_id, outputid, elid)
            elname = self.elnames[elid-1]
            self.data[elname] = np.array(eldata)
            if self.emg_auto_off and not self.is_valid_emg(self.data[elname]):
                self.data[elname] = 'EMG_DISCONNECTED'
                self.data_gc1l[elname] = 'EMG_DISCONNECTED'
                self.data_gc1r[elname] = 'EMG_DISCONNECTED'
            else:
                # cut to L/R gait cycles. no interpolation
                self.data_gc1l[elname] = self.data[elname][self.lgc1start_s:self.lgc1end_s]
                self.data_gc1r[elname] = self.data[elname][self.rgc1start_s:self.rgc1end_s]
        self.datalen = len(eldata)
        assert(self.datalen == framecount * samplesperframe)
        # time grid (s)
        self.t = np.arange(self.datalen)/self.sfrate
        # normalized grids (from 0..100) of EMG length; useful for plotting
        self.tn_emg_r = np.linspace(0, 100, self.rgc1len_s)
        self.tn_emg_l = np.linspace(0, 100, self.lgc1len_s)
        # map physical channels to logical ones
        self.map_data()
        
    def read_c3d(self, c3dfile):
        """ Read EMG data from a c3d file. """
        self.source = 'c3d'
        reader = btk.btkAcquisitionFileReader()
        reader.SetFilename(c3dfile)  # check existence?
        reader.Update()
        acq = reader.GetOutput()
        frame1 = acq.GetFirstFrame()  # start of ROI (1-based)
        samplesperframe = acq.GetNumberAnalogSamplePerFrame()
        self.sfrate = acq.GetAnalogFrequency()
        # get gait cycle
        vgc1 = gaitcycle()
        vgc1.read_c3d(c3dfile)
        # convert gait cycle times to EMG samples
        # in c3d, the data is already cut to the region of interest, so
        # frames must be translated by start of ROI (frame1)
        self.lgc1start_s = int(round((vgc1.lgc1start - frame1) * samplesperframe))
        self.lgc1end_s = int(round((vgc1.lgc1end - frame1) * samplesperframe))
        self.rgc1start_s = int(round((vgc1.rgc1start - frame1) * samplesperframe))
        self.rgc1end_s = int(round((vgc1.rgc1end - frame1) * samplesperframe))
        self.lgc1len_s = self.lgc1end_s - self.lgc1start_s
        self.rgc1len_s = self.rgc1end_s - self.rgc1start_s
        # read physical EMG channels and cut data to L/R gait cycles
        self.data = {}
        self.data_gc1l = {}
        self.data_gc1r = {}
        self.elnames = []
        for i in btk.Iterate(acq.GetAnalogs()):
            if i.GetDescription().find('EMG') >= 0 and i.GetUnit() == 'V':
                print(i.GetDescription())
                elname = i.GetLabel()
                self.elnames.append(elname)
                self.data[elname] = np.squeeze(i.GetValues())  # rm singleton dimension
                if self.emg_auto_off and not self.is_valid_emg(self.data[elname]):
                    self.data[elname] = 'EMG_DISCONNECTED'
                    self.data_gc1l[elname] = 'EMG_DISCONNECTED'
                    self.data_gc1r[elname] = 'EMG_DISCONNECTED'
                else:
                    self.data_gc1l[elname] = self.data[elname][self.lgc1start_s:self.lgc1end_s]
                    self.data_gc1r[elname] = self.data[elname][self.rgc1start_s:self.rgc1end_s]
        self.datalen = len(self.data[elname])
        # time grid (s)
        self.t = np.arange(self.datalen)/self.sfrate
        # normalized grids (from 0..100) of EMG length; useful for plotting
        self.tn_emg_r = np.linspace(0, 100, self.rgc1len_s)
        self.tn_emg_l = np.linspace(0, 100, self.lgc1len_s)
        # map physical channels to logical ones
        self.map_data()

    def map_data(self):
        """ Map logical channels into physical ones. Here, the rule is that the
        name of the physical channel must start with the name of the logical channel.
        For example, the logical name can be 'LPer' and the physical channel 'LPer12'
        will be a match. Thus, the logical names can be shorter than the physical ones.
        The shortest match will be found. """
        self.logical_data = {}
        self.logical_data_gc1l = {}
        self.logical_data_gc1r = {}
        self.yscale_gc1l = {}
        self.yscale_gc1r = {}

        for logch in self.ch_names:
            # check if channel was already assigned (or marked as reused)
            if logch not in self.logical_data:
                # check if channel should be read from some other electrode
                # in this case, the replacement is marked as reused
                if self.emg_remapping and logch in self.emg_remapping:
                    datach = self.emg_remapping[logch]
                    self.logical_data[datach] = 'EMG_REUSED'
                    self.logical_data_gc1l[datach] = 'EMG_REUSED'
                    self.logical_data_gc1r[datach] = 'EMG_REUSED'
                    self.ch_labels[logch] += ' (read from ' + datach +')'
                else:
                    datach = logch
                # find unique matching physical electrode name
                matches = [x for x in self.elnames if x.find(datach) >= 0]
                if len(matches) == 0:
                    error_exit('Cannot find electrode matching requested name '+datach)
                elname = min(matches, key=len)  # choose shortest matching name
                # FIXME: matching logic for Nexus, when multiple matches found?
                if len(matches) > 1:
                    print('map_data: multiple matching channels for: ', datach)
                    if self.source == 'Nexus':
                        messagebox('Warning: multiple matching channels for: '+datach+'\nChoosing: '+elname)
                self.logical_data[logch] = self.data[elname]
                # EMG data during gait cycles
                if self.data[elname] != 'EMG_DISCONNECTED':
                    self.logical_data_gc1l[logch] = self.logical_data[logch][self.lgc1start_s:self.lgc1end_s]
                    self.logical_data_gc1r[logch] = self.logical_data[logch][self.rgc1start_s:self.rgc1end_s]
                else:
                    self.logical_data_gc1l[logch] = 'EMG_DISCONNECTED'
                    self.logical_data_gc1r[logch] = 'EMG_DISCONNECTED'                    

        # set channel scaling
        for logch in self.ch_names:
            self.yscale_gc1l[logch] = .5e-3
            self.yscale_gc1r[logch] = .5e-3
            # median scaling - beware of DC!
            #self.yscale_gc1l[elname] = yscale_medians * np.median(np.abs(self.datagc1l[elname]))
            #self.yscale_gc1r[elname] = yscale_medians * np.median(np.abs(self.datagc1r[elname]))

class gaitcycle:
    """ Determines start and end points of 1st gait cycles (L/R) from data. 
    Can also normalize variables to 0..100% of either gait cycle.
    Currently only handles the 1st (L/R) gait cycles, rest are ignored. """
    
    def __init__(self):
        self.side = None
        self.source = None
    
    def read_nexus(self, vicon):
        """ Read gait cycle info from a Vicon Nexus instance. """
        self.source = 'Nexus'
        subjectname = vicon.GetSubjectNames()[0]
        # figure out gait cycle
        # frames where foot strikes occur (1-frame discrepancies with Nexus?)
        self.lfstrikes = vicon.GetEvents(subjectname, "Left", "Foot Strike")[0]
        self.rfstrikes = vicon.GetEvents(subjectname, "Right", "Foot Strike")[0]
        # frames where toe-off occurs
        self.ltoeoffs = vicon.GetEvents(subjectname, "Left", "Foot Off")[0]
        self.rtoeoffs = vicon.GetEvents(subjectname, "Right", "Foot Off")[0]
        self.compute_cycle()
        self.detect_side_nexus(vicon)

    def read_c3d(self, c3dfile):
        """ Read gait cycle info from a c3d file. """
        self.source = 'c3d'
        reader = btk.btkAcquisitionFileReader()
        reader.SetFilename(c3dfile)  # check existence?
        reader.Update()
        acq = reader.GetOutput()
        self.lfstrikes = []
        self.rfstrikes = []
        self.ltoeoffs = []
        self.rtoeoffs = []
        #  get the events
        for i in btk.Iterate(acq.GetEvents()):
            if i.GetLabel() == "Foot Strike":
                if i.GetContext() == "Right":
                    self.rfstrikes.append(i.GetFrame())
                elif i.GetContext() == "Left":
                    self.lfstrikes.append(i.GetFrame())
                else:
                    raise Exception("Unknown context")
            elif i.GetLabel() == "Foot Off":
                if i.GetContext() == "Right":
                    self.rtoeoffs.append(i.GetFrame())
                elif i.GetContext() == "Left":
                    self.ltoeoffs.append(i.GetFrame())
                else:
                    raise Exception("Unknown context")
        self.compute_cycle()
        self.detect_side_c3d(c3dfile)
        
    def compute_cycle(self):
        """ Compute gait cycles. Currently only determines the first gait cycle. """
        # 2 strikes is one complete gait cycle, needed for analysis
        lenLFS = len(self.lfstrikes)
        lenRFS = len(self.rfstrikes)
        if lenLFS < 2 or lenRFS < 2:
            error_exit("Insufficient number of foot strike events detected. "+
                        "Check that the trial has been processed.")
        # extract times for 1st gait cycles, L and R
        self.lgc1start = min(self.lfstrikes[0:2])
        self.lgc1end = max(self.lfstrikes[0:2])
        self.lgc1len = self.lgc1end-self.lgc1start
        self.rgc1start = min(self.rfstrikes[0:2])
        self.rgc1end = max(self.rfstrikes[0:2])
        self.rgc1len = self.rgc1end-self.rgc1start
        self.tn = np.linspace(0, 100, 101)
        # normalize toe off events to 1st gait cycles
        # first toe-off may occur before the gait cycle starts
        ltoeoff_gc1 = [x for x in self.ltoeoffs if x > self.lgc1start and x < self.lgc1end]
        rtoeoff_gc1 = [x for x in self.rtoeoffs if x > self.rgc1start and x < self.rgc1end]
        if len(ltoeoff_gc1) != 1 or len(rtoeoff_gc1) != 1:
            error_exit('Expected a single toe-off event during gait cycle')
        self.ltoe1_norm = round(100*((ltoeoff_gc1[0] - self.lgc1start) / self.lgc1len))
        self.rtoe1_norm = round(100*((rtoeoff_gc1[0] - self.rgc1start) / self.rgc1len))
      
    def normalize(self, y, side):
        """ Interpolate variable y to left or right (1st) gait cycle of this trial.
        Variable is assumed to share the same time axis (frames) as the gait events
        (analog data does not, due to different sampling rate)
        New x axis will be 0..100. """
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
        return np.interp(self.tn, gc1t, y[tstart:tend])
        
    def detect_side_nexus(self, vicon):
        """ Try to determine trial side, i.e. whether the 1st gait cycle has 
        L or R forceplate strike. Forceplate data is read from Nexus.
        Simple heuristic is to look at the forceplate data
        150 ms after each foot strike, when the other foot should have
        lifted off. Might not work with very slow walkers. """
        delay_ms = 150
        # get force data
        fp1 = forceplate()
        fp1.read_nexus(vicon)
        forcetot = fp1.forcetot
        # foot strike frames -> EMG samples
        lfsind = np.array(self.lfstrikes) * fp1.samplesperframe
        rfsind = np.array(self.rfstrikes) * fp1.samplesperframe
        delay = int(delay_ms/1000. * fp1.sfrate)
        lfsforces = forcetot[lfsind.astype(int) + delay]
        rfsforces = forcetot[rfsind.astype(int) + delay]
        print('Total force', delay_ms, 'ms after foot strikes:')
        #rint('Left: ', lfsforces)
        print('Right: ', rfsforces)
        if max(lfsforces) > max(rfsforces):
            self.side = 'L'
        else:
            self.side = 'R'
           
    def detect_side_c3d(self, c3dfile):
        """ Trial side from c3d file. """
        delay_ms = 150
        # get force data
        fp1 = forceplate()
        fp1.read_c3d(c3dfile)
        forcetot = fp1.forcetot
        # foot strike frames -> EMG samples
        # note: c3d frames start from beginning of roi
        lfsind = (np.array(self.lfstrikes) - fp1.frame1) * fp1.samplesperframe
        rfsind = (np.array(self.rfstrikes) - fp1.frame1) * fp1.samplesperframe
        delay = int(delay_ms/1000. * fp1.sfrate)
        lfsforces = forcetot[lfsind.astype(int) + delay]
        rfsforces = forcetot[rfsind.astype(int) + delay]
        print('Total force', delay_ms, 'ms after foot strikes:')
        #rint('Left: ', lfsforces)
        print('Right: ', rfsforces)
        if max(lfsforces) > max(rfsforces):
            self.side = 'L'
        else:
            self.side = 'R'
      

class model_outputs:
    """ Handles model output variables, e.g. Plug-in Gait, muscle length etc. """
    
    def merge_dicts(self, dict1, dict2):
        """ Merge two dicts, return result. """
        x = dict1.copy()
        x.update(dict2)
        return x
        
    def __init__(self):
        """ Sets up some variables, but does not read data.
        Model data is usually stored in normalized form with variables named
        e.g. NormRHipAnglesX, but shorter variable names are used in
        label dicts etc., e.g. HipAnglesX. *_varname functions convert between
        these names. """

        # descriptive labels for variables
        # Plug-in Gait lowerbody
        self.pig_lowerbody_varlabels = {'AnkleAnglesX': 'Ankle dorsi/plant',
                         'AnkleAnglesZ': 'Ankle rotation',
                         'AnkleMomentX': 'Ankle dors/plan moment',
                         'AnklePowerZ': 'Ankle power',
                         'FootProgressAnglesZ': 'Foot progress angles',
                         'HipAnglesX': 'Hip flexion',
                         'HipAnglesY': 'Hip adduction',
                         'HipAnglesZ': 'Hip rotation',
                         'HipMomentX': 'Hip flex/ext moment',
                         'HipMomentY': 'Hip ab/add moment',
                         'HipMomentZ': 'Hip rotation moment',
                         'HipPowerZ': 'Hip power',
                         'KneeAnglesX': 'Knee flexion',
                         'KneeAnglesY': 'Knee adduction',
                         'KneeAnglesZ': 'Knee rotation',
                         'KneeMomentX': 'Knee flex/ext moment',
                         'KneeMomentY': 'Knee ab/add moment',
                         'KneeMomentZ': 'Knee rotation moment',
                         'KneePowerZ': 'Knee power',
                         'PelvisAnglesX': 'Pelvic tilt',
                         'PelvisAnglesY': 'Pelvic obliquity',
                         'PelvisAnglesZ': 'Pelvic rotation'}
                         
        # muscle length (MuscleLength.mod)
        self.musclelen_varlabels = {'AdBrLength': 'AdBrLength',
                               'AdLoLength': 'AdLoLength',
                                'AdMaInfLength': 'AdMaInfLength',
                                'AdMaMidLength': 'AdMaMidLength',
                                'AdMaSupLength': 'AdMaSupLength',
                                'BiFLLength': 'Biceps femoris length',
                                'BiFSLength': 'BiFSLength',
                                'ExDLLength': 'ExDLLength',
                                'ExHLLength': 'ExHLLength',
                                'FlDLLength': 'FlDLLength',
                                'FlHLLength': 'FlHLLength',
                                'GMedAntLength': 'GMedAntLength',
                                'GMedMidLength': 'GMedMidLength',
                                'GMedPosLength': 'GMedPosLength',
                                'GMinAntLength': 'GMinAntLength',
                                'GMinMidLength': 'GMinMidLength',
                                'GMinPosLength': 'GMinPosLength',
                                'GemeLength': 'GemeLength',
                                'GlMaInfLength': 'GlMaInfLength',
                                'GlMaMidLength': 'GlMaMidLength',
                                'GlMaSupLength': 'GlMaSupLength',
                                'GracLength': 'Gracilis length',
                                'IliaLength': 'IliaLength',
                                'LaGaLength': 'Lateral gastrocnemius length',
                                'MeGaLength': 'Medial gastrocnemius length',
                                'PELOLength': 'PELOLength',
                                'PeBrLength': 'PeBrLength',
                                'PeTeLength': 'PeTeLength',
                                'PectLength': 'PectLength',
                                'PeriLength': 'PeriLength',
                                'PsoaLength': 'Psoas length',
                                'QuFeLength': 'QuFeLength',
                                'ReFeLength': 'Rectus femoris length',
                                'SartLength': 'SartLength',
                                'SeMeLength': 'Semimembranosus length',
                                'SeTeLength': 'Semitendinosus length',
                                'SoleLength': 'Soleus length',
                                'TiAnLength': 'Tibialis anterior length',
                                'TiPoLength': 'TiPoLength',
                                'VaInLength': 'VaInLength',
                                'VaLaLength': 'VaLaLength',
                                'VaMeLength': 'VaMeLength'}
        
        # merge all variable dicts into one
        self.varlabels = self.merge_dicts(self.pig_lowerbody_varlabels, self.musclelen_varlabels)

        # mapping from PiG variable names to normal data variables (in normal.gcd)
        # works with Vicon supplied .gcd (at least)
        self.pig_lowerbody_normdict = {'AnkleAnglesX': 'DorsiPlanFlex',
                     'AnkleAnglesZ': 'FootRotation',
                     'AnkleMomentX': 'DorsiPlanFlexMoment',
                     'AnklePowerZ': 'AnklePower',
                     'FootProgressAnglesZ': 'FootProgression',
                     'HipAnglesX': 'HipFlexExt',
                     'HipAnglesY': 'HipAbAdduct',
                     'HipAnglesZ': 'HipRotation',
                     'HipMomentX': 'HipFlexExtMoment',
                     'HipMomentY': 'HipAbAdductMoment',
                     'HipMomentZ': 'HipRotationMoment',
                     'HipPowerZ': 'HipPower',
                     'KneeAnglesX': 'KneeFlexExt',
                     'KneeAnglesY': 'KneeValgVar',
                     'KneeAnglesZ': 'KneeRotation',
                     'KneeMomentX': 'KneeFlexExtMoment',
                     'KneeMomentY': 'KneeValgVarMoment',
                     'KneeMomentZ': 'KneeRotationMoment',
                     'KneePowerZ': 'KneePower',
                     'PelvisAnglesX': 'PelvicTilt',
                     'PelvisAnglesY': 'PelvicObliquity',
                     'PelvisAnglesZ': 'PelvicRotation'}

        # TODO: muscle len normal data
        self.musclelen_normdict = {}
                     
        self.normdict = self.merge_dicts(self.pig_lowerbody_normdict, self.musclelen_normdict)
      
        # y labels for plotting
        self.pig_lowerbody_ylabels = {'AnkleAnglesX': 'Pla     ($^\\circ$)      Dor',
                             'AnkleAnglesZ': 'Ext     ($^\\circ$)      Int',
                             'AnkleMomentX': 'Int dors    Nm/kg    Int plan',
                             'AnklePowerZ': 'Abs    W/kg    Gen',
                             'FootProgressAnglesZ': 'Ext     ($^\\circ$)      Int',
                             'HipAnglesX': 'Ext     ($^\\circ$)      Flex',
                             'HipAnglesY': 'Abd     ($^\\circ$)      Add',
                             'HipAnglesZ': 'Ext     ($^\\circ$)      Int',
                             'HipMomentX': 'Int flex    Nm/kg    Int ext',
                             'HipMomentY': 'Int add    Nm/kg    Int abd',
                             'HipMomentZ': 'Int flex    Nm/kg    Int ext',
                             'HipPowerZ': 'Abs    W/kg    Gen',
                             'KneeAnglesX': 'Ext     ($^\\circ$)      Flex',
                             'KneeAnglesY': 'Val     ($^\\circ$)      Var',
                             'KneeAnglesZ': 'Ext     ($^\\circ$)      Int',
                             'KneeMomentX': 'Int flex    Nm/kg    Int ext',
                             'KneeMomentY': 'Int var    Nm/kg    Int valg',
                             'KneeMomentZ': 'Int flex    Nm/kg    Int ext',
                             'KneePowerZ': 'Abs    W/kg    Gen',
                             'PelvisAnglesX': 'Pst     ($^\\circ$)      Ant',
                             'PelvisAnglesY': 'Dwn     ($^\\circ$)      Up',
                             'PelvisAnglesZ': 'Bak     ($^\\circ$)      For'}

        # concat all vars
        self.ylabels = self.pig_lowerbody_ylabels
        
        # Vars will actually be read by read_() methods, as needed
        self.Vars = {}
                          

    def read_musclelen(self, vicon, gcdfile=None):
        """ Read muscle length variables produced by MuscleLengths.mod.
        Reads into self.Vars """
        
        varlist = ['LGMedAntLength',
                     'RGMedAntLength',
                     'LGMedMidLength',
                     'RGMedMidLength',
                     'LGMedPosLength',
                     'RGMedPosLength',
                     'LGMinAntLength',
                     'RGMinAntLength',
                     'LGMinMidLength',
                     'RGMinMidLength',
                     'LGMinPosLength',
                     'RGMinPosLength',
                     'LSeMeLength',
                     'RSeMeLength',
                     'LSeTeLength',
                     'RSeTeLength',
                     'LBiFLLength',
                     'RBiFLLength',
                     'LBiFSLength',
                     'RBiFSLength',
                     'LSartLength',
                     'RSartLength',
                     'LAdLoLength',
                     'RAdLoLength',
                     'LAdBrLength',
                     'RAdBrLength',
                     'LAdMaSupLength',
                     'RAdMaSupLength',
                     'LAdMaMidLength',
                     'RAdMaMidLength',
                     'LAdMaInfLength',
                     'RAdMaInfLength',
                     'LPectLength',
                     'RPectLength',
                     'LGracLength',
                     'RGracLength',
                     'LGlMaSupLength',
                     'RGlMaSupLength',
                     'LGlMaMidLength',
                     'RGlMaMidLength',
                     'LGlMaInfLength',
                     'RGlMaInfLength',
                     'LIliaLength',
                     'RIliaLength',
                     'LPsoaLength',
                     'RPsoaLength',
                     'LQuFeLength',
                     'RQuFeLength',
                     'LGemeLength',
                     'RGemeLength',
                     'LPeriLength',
                     'RPeriLength',
                     'LReFeLength',
                     'RReFeLength',
                     'LVaMeLength',
                     'RVaMeLength',
                     'LVaInLength',
                     'RVaInLength',
                     'LVaLaLength',
                     'RVaLaLength',
                     'LMeGaLength',
                     'RMeGaLength',
                     'LLaGaLength',
                     'RLaGaLength',
                     'LSoleLength',
                     'RSoleLength',
                     'LTiPoLength',
                     'RTiPoLength',
                     'LFlDLLength',
                     'RFlDLLength',
                     'LFlHLLength',
                     'RFlHLLength',
                     'LTiAnLength',
                     'RTiAnLength',
                     'LPeBrLength',
                     'RPeBrLength',
                     'LPELOLength',
                     'RPELOLength',
                     'LPeTeLength',
                     'RPeTeLength',
                     'LExDLLength',
                     'RExDLLength',
                     'LExHLLength',
                     'RExHLLength']
                     
        SubjectName = vicon.GetSubjectNames()[0]
        # get gait cycle info 
        vgc1 = gaitcycle()
        vgc1.read_nexus(vicon)

        for Var in varlist:
            # not sure what the BoolVals are, discard for now
            NumVals, BoolVals = vicon.GetModelOutput(SubjectName, Var)
            if not NumVals:
                error_exit('Unable to get muscle length output variable. '+
                            'Make sure that the appropriate model has been executed.')
            self.Vars[Var] = np.array(NumVals)[0]
            # normalize var to gait cycle 1
            side = Var[0]  # L or R
            self.Vars['Norm'+Var] = vgc1.normalize(self.Vars[Var], side)

    def read_pig_lowerbody(self, vicon, gcdfile=None):
        """ Read the lower body Plug-in Gait model outputs from Nexus.
        Variable names starting with 'R' and'L' are normalized into left and right 
        gait cycles, respectively. gcdfile contains PiG normal data variables. 
        Reads into self.Vars """
        
        # the PiG kin *vars contain X,Y,Z components per each variable,
        # these will be separated into different variables
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
              'RAnklePower',
              'LHipAngles',
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
        vgc1 = gaitcycle()
        vgc1.read_nexus(vicon)
        # read all kinematics vars into dict. Also normalized variables will
        # be created. Variables will be named like 'NormLKneeAnglesX' (normalized)
        # or 'RHipAnglesX' (non-normalized)

        for Var in varlist:
            # not sure what the BoolVals are, discard for now
            NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
            if not NumVals:
                error_exit('Unable to get Plug-in Gait output variable. '+
                            'Make sure that the appropriate model has been executed.')
            self.Vars[Var] = np.array(NumVals)
            # moment variables have to be divided by 1000 - not sure why
            # apparently stored in Newton-millimeters!
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

        # read PiG normal data from given gcd file
        if gcdfile:
            if not os.path.isfile(gcdfile):
                error_exit('Cannot find specified PiG normal data file')
            f = open(gcdfile, 'r')
            lines = f.readlines()
            f.close()
            pig_normaldata = {}
            for li in lines:
                if li[0] == '!':  # it's a variable name
                    thisvar = li[1:li.find(' ')]  # set dict key
                    pig_normaldata[thisvar] = list()
                elif li[0].isdigit() or li[0] == '-':  # it's a number, so read into list
                    pig_normaldata[thisvar].append([float(x) for x in li.split()])
            self.pig_normaldata = pig_normaldata

    def pig_lowerbody_varnames(self):
        """ Return list of known PiG variables. """
        return self.pig_lowerbody_varlabels.keys()

    def is_pig_lowerbody_variable(self, var):
        """ Is var a PiG lower body variable? var might be preceded with Norm and L/R """
        return var in self.pig_lowerbody_varnames() or self.unnorm_varname(var) in self.pig_lowerbody_varnames()

    def is_kinetic_var(self, var):
        """ Tell whether a (PiG) variable represents kinetics. """
        return var.find('Power') > -1 or var.find('Moment') > -1
        
    def musclelen_varnames(self):
        """ Return list of known muscle length variables. """
        return self.musclelen_varlabels.keys()

    def is_musclelen_variable(self, var):
        """ Is var a muscle length variable? var might be preceded with Norm and L/R """
        return var in self.musclelen_varnames() or self.unnorm_varname(var) in self.musclelen_varnames()

    def unnorm_varname(self, var):
        """ Remove Norm and 'L/R' from beginning of variable name. """
        if var[:4] == 'Norm':
            return var[5:]
        else:
            return var
           
    def norm_varname(self, var, side):
        """ Create normalized variable name corresponding to var. """
        return 'Norm'+side.upper()+var

    def description(self, var):
        """ Returns a more elaborate description for a model variable,
        if known. If var is normalized to a gait cycle, side will be reflected
        in the name. """
        if var[:3] == 'Norm':
            vars = var[4:]
            if vars[0] == 'L':
                sidestr = ( 'L')
                vars = vars[1:]
            elif var[0] == 'R':
                sidestr = ( 'R')
                vars = vars[1:]
        else:
            vars = var
            sidestr = ''
        print(vars)
        if vars in self.varlabels:
            return self.varlabels[vars]+sidestr
        else:
            return var
        
    def ylabel(self, var):
        """ Return y label for plotting a given variable. """
        vars = self.unnorm_varname(var)
        # explicitly specified label?       
        if vars in self.ylabels:
            return self.ylabels[vars]
        # use default for muscle len variable
        elif self.is_musclelen_variable(var):
            return 'Length (mm)'
        # unknown var
        else:
            return None
        
    def normaldata(self, var):
        """ Return the normal data (in the given gcd file) for 
        PiG variable var, if available.
        TODO: normal data for muscle lengths? """
        # strip leading 'Norm' and L/R from variable name
        vars = self.unnorm_varname(var)
        if not vars in self.normdict:
            return None
        else:
            return self.pig_normaldata[self.normdict[vars]]

