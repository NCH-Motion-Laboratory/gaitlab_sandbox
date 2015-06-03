# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:41:31 2015

Utility classes for reading data from Vicon Nexus.

@author: Jussi
"""

from __future__ import division, print_function

import numpy as np
import ctypes
from scipy import signal
import sys
import psutil
import os



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
    
class nexus_emg:
    """ Class for reading and processing EMG data from Nexus.
    vicon is a ViconNexus.ViconNexus() object. EMG object can be created
    without reading any actual data (e.g. to check electrode names). """
    
    def define_emg_mapping(self, emg_system='Myon'):
        """ Defines electrode mapping.  emg_system may be used to support systems
        other than Myon in the future. """
        if emg_system == 'Myon':
            self.ch_normals = {'RGas': [[16,50]],
                   'RGlut': [[0,42],[96,100]],
                   'RHam': [[0,2],[92,100]],
                   'RPer': [[4,54]],
                   'RRec': [[0,14],[56,100]],
                   'RSol': [[10,54]],
                   'RTibA': [[0,12],[56,100]],
                   'RVas': [[0,24],[96,100]],
                   'LGas': [[16,50]],
                   'LGlut': [[0,42],[96,100]],
                   'LHam': [[0,2],[92,100]],
                   'LPer': [[4,54]],
                   'LRec': [[0,14],[56,100]],
                   'LSol': [[10,54]],
                   'LTibA': [[0,12],[56,100]],
                   'LVas': [[0,24],[96,100]]}
            self.ch_names = self.ch_normals.keys()
            self.ch_labels = {'RHam': 'Medial hamstrings (R)',
                       'RRec': 'Rectus femoris (R)',
                       'RGas': 'Gastrognemius (R)',
                       'RGlut': 'Gluteus (R)',
                       'RVas': 'Vastus (R)',
                       'RSol': 'Soleus (R)',
                       'RTibA': 'Tibialis anterior (R)',
                       'RPer': 'Peroneus (R)',
                       'LHam': 'Medial hamstrings (L)',
                       'LRec': 'Rectus femoris (L)',
                       'LGas': 'Gastrognemius (L)',
                       'LGlut': 'Gluteus (L)',
                       'LVas': 'Vastus (L)',
                       'LSol': 'Soleus (L)',
                       'LTibA': 'Tibialis anterior (L)',
                       'LPer': 'Peroneus (L)'}
        else:
            error_exit('Unsupported EMG system: '+emg_system)
                
    def emg_channelnames(self):
        """ Return names of known (logical) EMG channels. """
        return self.ch_names
       
    def is_logical_channel(self, chname):
        return chname in self.ch_names

    def __init__(self, emg_system='Myon', emg_remapping=None, emg_auto_off=True):
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
        self.define_emg_mapping(emg_system)
        self.emg_remapping = emg_remapping

    def read(self, vicon):
        """ Read the actual EMG data from Nexus. """
        # find EMG device and get some info
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

        # fix "Voltage." bug - not necessary anymore (matching labels
        # works at any position)
        #for i in range(len(self.elnames)):
            #elname = self.elnames[i]    
            # if elname starts with 'Voltage.', remove it:
            # Nexus 2 prepends 'Voltage.' to electrode names during processing
            #if elname.find('Voltage') > -1:
                #elname = elname[elname.find('.')+1:]
            #self.elnames[i] = elname

        # gait cycle beginning and end, samples
        vgc1 = gaitcycle(vicon)
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
            # DEBUG
            # print(elname)
            if self.emg_auto_off and not self.is_valid_emg(self.data[elname]):
                self.data[elname] = 'EMG_DISCONNECTED'
                self.data_gc1l[elname] = 'EMG_DISCONNECTED'
                self.data_gc1r[elname] = 'EMG_DISCONNECTED'
            else:
                # cut to L/R gait cycles. no interpolation
                self.data_gc1l[elname] = self.data[elname][self.lgc1start_s:self.lgc1end_s]
                self.data_gc1r[elname] = self.data[elname][self.rgc1start_s:self.rgc1end_s]

        """ Map logical channels into physical ones. Here, the rule is that the
        name of the physical channel must start with the name of the logical channel.
        For example, the logical name can be 'LPer' and the physical channel 'LPer12'
        will be a match. Thus, the logical names can be shorter than the physical ones,
        as long as an unique match is found. The user-defined replacements are also taken 
        into account here. """
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
                if len(matches) != 1:
                    error_exit('Cannot find unique electrode matching requested name '+datach)
                elname = matches[0]
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

        # various variables
        self.datalen = len(eldata)
        assert(self.datalen == framecount * samplesperframe)
        # samples to time (s)
        self.t = np.arange(self.datalen)/self.sfrate
        # normalized grids (from 0..100) of EMG length; useful for plotting
        self.tn_emg_r = np.linspace(0, 100, self.rgc1len_s)
        self.tn_emg_l = np.linspace(0, 100, self.lgc1len_s)
        
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
        Passband is given in Hz. None for no filtering. """
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

class gaitcycle:
    """ Determines 1st L/R gait cycles from data. Can also normalize
    vars to 0..100% of gait cycle. """
    
    def __init__(self, vicon):
        subjectname = vicon.GetSubjectNames()[0]
        # figure out gait cycle
        # frames where foot strikes occur (1-frame discrepancies with Nexus?)
        self.lfstrikes = vicon.GetEvents(subjectname, "Left", "Foot Strike")[0]
        self.rfstrikes = vicon.GetEvents(subjectname, "Right", "Foot Strike")[0]
        # frames where toe-off occurs
        self.ltoeoffs = vicon.GetEvents(subjectname, "Left", "Foot Off")[0]
        self.rtoeoffs = vicon.GetEvents(subjectname, "Right", "Foot Off")[0]
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
            error_exit('Expected single toe-off event during gait cycle')
        self.ltoe1_norm = round(100*((ltoeoff_gc1[0] - self.lgc1start) / self.lgc1len))
        self.rtoe1_norm = round(100*((rtoeoff_gc1[0] - self.rgc1start) / self.rgc1len))
        
       
    def normalize(self, y, side):
        """ Interpolate any variable y to left or right gait cycle of this trial.
        New x axis will be 0..100 """
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
        
        
    def detect_side(self, vicon):
        """ Try to detect whether the trial has L or R forceplate strike.
        Simple heuristic is to look at the force data
        150 ms after each foot strike, when the other foot should have
        lifted off. Might not work with very slow walkers. """
        delay_ms = 150
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
        #print('Total force', delay_ms, 'ms after foot strikes:')
        #print('Left: ', lfsforces)
        #print('Right: ', rfsforces)
        if max(lfsforces) > max(rfsforces):
            return 'L'
        else:
            return 'R'

class model_outputs:
    """ Handles model output variables. """
        
    def __init__(self):
        """ Sets up some relevant variables, but does not read data """

        # descriptions of known PiG variables (without side info)
        self.pigdict = {'AnkleAnglesX': 'Ankle dorsi/plant',
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

        # default mapping from PiG variable names to normal data variables (in normal.gcd)
        self.normdict = {'AnkleAnglesX': 'DorsiPlanFlex',
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

         # y labels for plotting
        self.ylabeldict = {'AnkleAnglesX': 'Pla     ($^\\circ$)      Dor',
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

    def read(self, vicon, varlist, gcdfile):
        """ Read the model outputs from Nexus.
        Variable names starting with 'R' and'L' are normalized into left and right 
        gait cycles, respectively. Can also use special keyword 'PiGLB'
        to get the usual set of Plug-in Gait lower body variables. """
        
        # the vars to be read contain X,Y,Z components per each variable,
        # these will be separated into different variables
        if varlist == 'PiGLB':
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
        vgc1 = gaitcycle(vicon)
        # read all kinematics vars into dict. Also normalized variables will
        # be created. Variables will be named like 'NormLKneeAnglesX' (normalized)
        # or 'RHipAnglesX' (non-normalized)
        self.Vars = {}
        for Var in varlist:
            # not sure what the BoolVals are, discard for now
            NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
            if not NumVals:
                error_exit('Unable to get model output variable. '+
                            'Make sure that the appropriate model has been executed.')
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

    def pig_varnames(self):
        """ Return list of known PiG variables. """
        return self.pigdict.keys()
        
    def is_pig_variable(self, var):
        vars = self.strip_varname(var)        
        varlist = self.pig_varnames()
        return vars in varlist
        
    def is_kinetic_var(self, var):
        """ Tell whether a variable represents kinetics. """
        return var.find('Power') > -1 or var.find('Moment') > -1

    def strip_varname(self, var):
        """ Remove Norm and/or L/R from beginning of variable name. """
        vars = var
        if vars[:4] == 'Norm':
            vars = var[4:]
        if vars[0] in ['L','R']:
            vars = vars[1:]
        return vars

    def description(self, var):
        """ Returns a more elaborate description for a PiG variable,
        if known. """
        vars = var
        if var[:3] == 'Norm':
            vars = var[4:]
        if vars[0] == 'L':
            sidestr = ( 'L')
            vars = vars[1:]
        elif var[0] == 'R':
            sidestr = ( 'R')
            vars = vars[1:]
        else:
            sidestr = ''
        if vars in self.pigdict:
            return self.pigdict[vars]+sidestr
        else:
            return var
        
    def ylabel(self, var):
        """ Return y label for plotting a given variable. """
        vars = self.strip_varname(var)
        if vars in self.ylabeldict:
            return self.ylabeldict[vars]
        else:
            return None
        
    def normaldata(self, var):
        """ Return the normal data (in the given gcd file) for 
        PiG variable var. """
        # strip leading 'Norm' and L/R from variable name
        vars = self.strip_varname(var)
        if not vars in self.normdict:
            error_exit('No normal data for variable ',+vars)
        else:
            return self.pig_normaldata[self.normdict[vars]]



