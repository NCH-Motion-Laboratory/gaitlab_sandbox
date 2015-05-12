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


def error_exit(message):
    """ Custom error handler """
    # graphical error dialog - Windows specific
    ctypes.windll.user32.MessageBoxA(0, message, "Error in Nexus Python script", 0)
    sys.exit()

def messagebox(message):
    """ Custom error handler """
    # graphical error dialog - Windows specific
    ctypes.windll.user32.MessageBoxA(0, message, "Message from Nexus Python script", 0)
    
class nexus_emg:
    """ Class for reading and processing EMG data from Nexus.
    vicon is a ViconNexus.ViconNexus() object. EMG object can be created
    without reading any actual data (e.g. to check electrode names). """
    
    def define_emg_mapping(self, emg_system='Myon', mapping_changes=None):
        """ Defines electrode mapping. mapping_changes contains the replacement
        dict for EMG electrodes: e.g. key 'LGas'='LSol4' means that LGas data will be 
        read from the LSol4 electrode. emg_system may be used to support systems
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
            # default mapping of logical channels to physical ones
            self.ch_mapping = {'LGas': 'LGas4',
             'LGlut': 'LGlut8',
             'LHam': 'LHam7',
             'LPer': 'LPer2',
             'LRec': 'LRec5',
             'LSol': 'LSol3',
             'LTibA': 'LTibA1',
             'LVas': 'LVas6',
             'RGas': 'RGas12',
             'RGlut': 'RGlut16',
             'RHam': 'RHam15',
             'RPer': 'RPer10',
             'RRec': 'RRec13',
             'RSol': 'RSol11',
             'RTibA': 'RTibA9',
             'RVas': 'RVas14'}
        else:
            error_exit('Unsupported EMG system: '+emg_system)
            
        # user specified changes to electrode mapping
        if mapping_changes:
            for logch in mapping_changes:
                physch = mapping_changes[logch]
                # mark channel as remapped
                for ch in self.ch_mapping.keys():
                    if self.ch_mapping[ch] == physch:
                        self.ch_mapping[ch] = 'EMG_REUSED'
                self.ch_mapping[logch] = mapping_changes[logch]
                self.ch_labels[logch] += ' (read from ' + physch +')'
                
    def emg_channelnames(self):
        """ Return names of known (logical) EMG channels. """
        return self.ch_names
        
    def is_logical_channel(self, chname):
        return chname in self.ch_names

    def __init__(self, emg_system='Myon', mapping_changes=None):
        # default plotting scale in medians (channel-specific)
        yscale_medians = 1
        # whether to auto-find disconnected EMG channels
        self.find_disconnected = True
        # normal data and logical chs
        self.define_emg_mapping(emg_system, mapping_changes)

    def read(self, vicon):
        # find EMG device and get some info
        framerate = vicon.GetFrameRate()
        framecount = vicon.GetFrameCount()
        emgdevname = 'Myon'
        devnames = vicon.GetDeviceNames()
        if emgdevname in devnames:
            emg_id = vicon.GetDeviceIDFromName(emgdevname)
        else:
           error_exit('no EMG device found in trial')
        # DType should be 'other', drate is sampling rate
        dname,dtype,drate,outputids,_,_ = vicon.GetDeviceDetails(emg_id)
        samplesperframe = drate / framerate
        # Myon should only have 1 output; if zero, EMG was not found
        assert(len(outputids)==1)
        outputid = outputids[0]
        # list of channel names and IDs
        _,_,_,_,self.elnames,self.chids = vicon.GetDeviceOutputDetails(emg_id, outputid)
        for i in range(len(self.elnames)):
            elname = self.elnames[i]    
            # if elname starts with 'Voltage', remove it
            if elname.find('Voltage') > -1:
                elname = elname[elname.find('.')+1:]
            self.elnames[i] = elname
        # read EMG channels into dict
        # also cut data to L/R gait cycles
        self.data = {}
        vgc1 = gaitcycle(vicon)
        self.data_gc1l = {}
        self.data_gc1r = {}
        # gait cycle beginning and end, samples
        self.lgc1start_s = int(round((vgc1.lgc1start - 1) * samplesperframe))
        self.lgc1end_s = int(round((vgc1.lgc1end - 1) * samplesperframe))
        self.rgc1start_s = int(round((vgc1.rgc1start - 1) * samplesperframe))
        self.rgc1end_s = int(round((vgc1.rgc1end - 1) * samplesperframe))
        self.lgc1len_s = self.lgc1end_s - self.lgc1start_s
        self.rgc1len_s = self.rgc1end_s - self.rgc1start_s

        # init dicts
        self.reused = {}
        self.disconnected = {}
        for elname in self.elnames:
            self.disconnected[elname] = False
            self.reused[elname] = False
        
        # read all physical channels (electrodes)
        for elid in self.chids:
            eldata, elready, elrate = vicon.GetDeviceChannel(emg_id, outputid, elid)
            assert(elrate == drate), 'Channel has an unexpected sampling rate'
            elname = self.elnames[elid-1]
            self.data[elname] = np.array(eldata)
            # zero out invalid EMG signals
            if self.find_disconnected and not self.is_valid_emg(self.data[elname]):
                self.data[elname] = "EMG_DISCONNECTED"
                self.data_gc1l[elname] = "EMG_DISCONNECTED"
                self.data_gc1r[elname] = "EMG_DISCONNECTED"
            else:
                # cut to L/R gait cycles. no interpolation
                self.data_gc1l[elname] = self.data[elname][self.lgc1start_s:self.lgc1end_s]
                self.data_gc1r[elname] = self.data[elname][self.rgc1start_s:self.rgc1end_s]
            # median scaling - beware of DC!
            #self.yscalegc1l[elname] = yscale_medians * np.median(np.abs(self.datagc1l[elname]))
            #self.yscalegc1r[elname] = yscale_medians * np.median(np.abs(self.datagc1r[elname]))
            # fixed scale

        # assign data to logical channels
        self.logical_data = {}
        self.logical_data_gc1l = {}
        self.logical_data_gc1r = {}
        self.yscale_gc1l = {}
        self.yscale_gc1r = {}
        
        for logch in self.ch_mapping:
            if self.ch_mapping[logch] != 'EMG_REUSED':
                physch = self.ch_mapping[logch]
                if physch not in self.data:
                    error_exit('Cannot read requested physical channel: '+physch)
                self.logical_data[logch] = self.data[physch]
                # EMG data during gait cycles
                if self.data[physch] != 'EMG_DISCONNECTED':
                    self.logical_data_gc1l[logch] = self.logical_data[logch][self.lgc1start_s:self.lgc1end_s]
                    self.logical_data_gc1r[logch] = self.logical_data[logch][self.rgc1start_s:self.rgc1end_s]
                else:
                    self.logical_data_gc1l[logch] = 'EMG_DISCONNECTED'
                    self.logical_data_gc1r[logch] = 'EMG_DISCONNECTED'                    
            else:
                self.logical_data[logch] = 'EMG_REUSED'
                self.logical_data_gc1l[logch] = 'EMG_REUSED'
                self.logical_data_gc1r[logch] = 'EMG_REUSED'
            # set fixed scales
            self.yscale_gc1l[logch] = .5e-3
            self.yscale_gc1r[logch] = .5e-3

        self.datalen = len(eldata)
        assert(self.datalen == framecount * samplesperframe)
        self.sfrate = drate        
        # samples to time (s)
        self.t = np.arange(self.datalen)/self.sfrate
        # normalized grids (from 0..100) of EMG length; useful for plotting
        self.tn_emg_r = np.linspace(0, 100, self.rgc1len_s)
        self.tn_emg_l = np.linspace(0, 100, self.lgc1len_s)
        
    def is_valid_emg(self, y):
        """ Check whether channel contains valid EMG signal. """
        # simple variance check
        emg_max_variance = 5e-7
        return np.var(y) < emg_max_variance
        
    def filter(self, y, passband):
        """ Bandpass filter given data y to passband, e.g. [1, 40].
        Passband is given in Hz. None for no filtering. """
        if passband == None:
            return y
        else:
            passbandn = np.array(passband) / self.sfrate
            b, a = signal.butter(4, passbandn, 'bandpass')
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

class pig_outputs:
    """ Reads given plug-in gait output variables (in varlist). Variable 
    names starting with 'R' and'L' are normalized into left and right 
    gait cycles, respectively. Can also use special keyword 'PiGLB'
    to get the usual set of Plug-in Gait lower body variables."""
        
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
        """ Read the PiG output from Nexus. """
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
        # be created. Variables are named like 'NormLKneeAnglesX' (normalized)
        # or 'RHipAnglesX' (non-normalized)
        self.Vars = {}
        for Var in varlist:
            # not sure what the BoolVals are, discard for now
            NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
            if not NumVals:
                error_exit('Unable to get Plug-in Gait output variable. '+
                            'Check that the trial has been processed.')
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



