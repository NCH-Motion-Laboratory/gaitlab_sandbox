# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:41:31 2015

Gaitplotter utility classes for reading gait data.

NEXT:
-rewrite EMG class to use new gait cycle defs

TODO:
-handling of error situations (exceptions/error method)
trial class for grouping trial-specific data?
-factor out read methods for Nexus/c3d

Notes:
x axis for c3d variables is ROI; i.e. first frame is beginning of ROI (=offset)
However, event times are referred to whole trial. Thus offset needs to be subtracted
from event times to put them on the common x axis.
For Vicon Nexus data, x axis is the whole trial. 


@author: Jussi
"""


from __future__ import division, print_function

import numpy as np
import ctypes
from scipy import signal
import sys
import psutil
import os
import gait_defs  # lab-specific stuff
import btk  # biomechanical toolkit for c3d reading
# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")
import ViconNexus


def viconnexus():
    """ Return a ViconNexus instance. Convenience for calling classes. """
    return ViconNexus.ViconNexus()

class ModelVarNotFound(Exception):
    pass

class InvalidDataSource(Exception):
    pass

def is_vicon_instance(obj):
    """ Check if obj is an instance of ViconNexus """
    return obj.__class__.__name__ == 'ViconNexus'

def is_c3dfile(obj):
    """ Check c3d file; currently just checks existence of file """
    try:
        return os.path.isfile(obj)
    except TypeError:
        return False

def get_eclipse_description(trialname):
    """ Get the Eclipse database description for the specified trial. Specify
    trialname with full path. """
    # remove c3d extension if present
    trialname = os.path.splitext(trialname)[0]
    if not os.path.isfile(trialname+'.c3d'):
        raise Exception('Cannot find c3d file for trial')
    enfname = trialname + '.Trial.enf'
    description = None
    if os.path.isfile(enfname):
        f = open(enfname, 'r')
        eclipselines = f.read().splitlines()
        f.close()
    else:
        return None
    for line in eclipselines:
        eqpos = line.find('=')
        if eqpos > 0:
            key = line[:eqpos]
            val = line[eqpos+1:]
            if key == 'DESCRIPTION':
                description = val
    # assume utf-8 encoding for Windows text files, return Unicode object
    # could also use codecs.read with encoding=utf-8 (recommended way)
    return unicode(description, 'utf-8')

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


class gaitcycle:
    """" Holds information about one gait cycle. Offset is the frame where
    the data begins; 1 for Vicon Nexus (which always returns whole trial) and
    start of the ROI for c3d files, which contain data only for the ROI. """
    
    def __init__(self, start, end, offset, toeoff, context, smp_per_frame):
        self.offset = offset
        self.len = end - start
        self.start = start - offset
        self.end = end - offset
        self.toeoff = toeoff - offset
        # which foot begins and ends the cycle
        self.context = context
        # start and end on the analog samples axis; round to whole samples
        self.start_smp = int(round(self.start * smp_per_frame))
        self.end_smp = int(round(self.end * smp_per_frame))
        self.len_smp = self.end_smp - self.start_smp
        # normalized x-axis (% of gait cycle) of same length as cycle
        self.t = np.linspace(0, 100, self.len)
        # normalized x-axis of 0,1,2..100%
        self.tn = np.linspace(0, 100, 101)
        # normalize toe-off event to the cycle
        self.toeoffn = round(100*((self.toeoff - self.start) / self.len))
        
    def normalize(self, var):
        """ Normalize frames-based variable var to this cycle.
        New interpolated x axis is 0..100% of the cycle. """
        return np.interp(self.tn, self.t, var[self.start:self.end])

    def cut_analog_to_cycle(self, var):
        """ Crop analog variable (EMG, forceplate, etc. ) to this
        cycle; no interpolation """
        return var[self.start_smp:self.end_smp]
  
class trial:
    """
    A gait trial. Contains:
    -subject and trial info
    -gait cycles (beginning and end frames)
    -analog data (EMG, forceplate, etc.)
    -model variables (Plug-in Gait, muscle length, etc.)
    """
    def __init__(self, source, side=None):
        """ Open trial, read subject info, events etc. """
        self.lfstrikes = []
        self.rfstrikes = []
        self.ltoeoffs = []
        self.rtoeoffs = []
        # TODO: needs to be determined from file
        self.smp_per_frame = 100
        if is_c3dfile(source):
            c3dfile = source
            self.trialname = os.path.basename(os.path.splitext(c3dfile)[0])
            self.sessionpath = os.path.dirname(c3dfile)
            reader = btk.btkAcquisitionFileReader()
            reader.SetFilename(c3dfile)  # check existence?
            reader.Update()
            acq = reader.GetOutput()
            # frame offset (start of trial data in frames)
            self.offset = acq.GetFirstFrame()
            #  get events
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
        elif is_vicon_instance(source):
            vicon = source
            subjectnames = vicon.GetSubjectNames()  
            if not subjectnames:
                error_exit('No subject defined in Nexus')
            trialname_ = vicon.GetTrialName()
            self.sessionpath = trialname_[0]
            self.trialname = trialname_[1]
            if not self.trialname:
                error_exit('No trial loaded')
            self.subjectname = subjectnames[0]
            # get events
            self.lfstrikes = vicon.GetEvents(self.subjectname, "Left", "Foot Strike")[0]
            self.rfstrikes = vicon.GetEvents(self.subjectname, "Right", "Foot Strike")[0]
            self.ltoeoffs = vicon.GetEvents(self.subjectname, "Left", "Foot Off")[0]
            self.rtoeoffs = vicon.GetEvents(self.subjectname, "Right", "Foot Off")[0]
            # frame offset (start of trial data in frames)
            self.offset = 1  # DEBUG
        else:
            raise InvalidDataSource()
        self.source = source
        self.fp = forceplate(source)
        # TODO: read from config / put as init params?
        self.emg_mapping = {}
        self.emg_auto_off = True
        # will be read by read_vars
        self.emg = None
        self.model = None
        self.kinetics = self.kinetics_available()
        self.scan_cycles()
        
    def kinetics_available(self):
        """ See whether this trial has full kinetics for left/right side
        (or neither, or both). Kinetics require the GRF for the corresponding
        side, i.e. a forceplate strike. Thus look at strike event times and 
        determine whether (clean) forceplate contact is happening at each time.
        Currently this method is not very smart and does not work for multiple-plate
        systems. Trials with double contact may also be misclassified. """
        # delay between foot strike event and forceplate data evaluation.
        # idea is to wait until the other foot has lifted off
        delay_ms = 150
        # minimum force (N) to consider it a clean contact
        min_force = 100
        # get force data
        forcetot = self.fp.forcetot
        # foot strike frames -> analog samples
        lfsind = (np.array(self.lfstrikes) - self.offset) * self.fp.samplesperframe
        rfsind = (np.array(self.rfstrikes) - self.offset) * self.fp.samplesperframe
        delay = int(delay_ms/1000. * self.fp.sfrate)
        lfsforces = forcetot[lfsind.astype(int) + delay]
        rfsforces = forcetot[rfsind.astype(int) + delay]
        kinetics = ''
        if max(lfsforces) > min_force:
            kinetics += 'L'
        if max(rfsforces) > min_force:
            kinetics += 'R'
        #print('Strike frames:')
        #print(lfsind)
        #print(rfsind)
        #print('Total force', delay_ms, 'ms after foot strikes:')
        #print('Left: ', lfsforces)
        #print('Right: ', rfsforces)
        return kinetics

    def scan_cycles(self):
        """ Scan for foot strike events and create gait cycle objects. """
        self.cycles = []
        for strikes in [self.lfstrikes, self.rfstrikes]:
            len_s = len(strikes)
            if len_s < 2:
                error_exit("Insufficient number of foot strike events detected. "+
                        "Check that the trial has been processed.")
            if len_s % 2:
                strikes.pop()  # assure even number of foot strikes
            if strikes == self.lfstrikes:
                toeoffs = self.ltoeoffs
                context = 'L'
            else:
                toeoffs = self.rtoeoffs
                context = 'R'
            for k in range(0, 2, len_s):
                start = strikes[k]
                end = strikes[k+1]
                toeoff = [x for x in toeoffs if x > start and x < end]
                if len(toeoff) != 1:
                    error_exit('Expected a single toe-off event during gait cycle')
                cycle = gaitcycle(start, end, self.offset, toeoff[0], context, self.smp_per_frame)
                self.cycles.append(cycle)
            self.ncycles = len(self.cycles)
        
    def read_emg(self):
        """ Read EMG channels from trial data. """
        if not self.emg:
            self.emg = emg(self.source, emg_remapping=self.emg_mapping, emg_auto_off=self.emg_auto_off)
            self.emg.read()
            
    def cut_analog_to_cycle(self, cycle, data):
        """ Returns given analog data (should be an instance variable)
        during a specified gait cycle (1,2,3...) """
        if cycle > ncycles:
            raise Exception("No such gait cycle in data")
        return self.cycles[cycle-1].cut_analog_to_cycle(data)

    def read_model(self, var):
        pass
    
    
class forceplate:
    """ Read and process forceplate data. source may be a c3d file or a
    ViconNexus instance. Gives x,y,z and total forces during the whole
    trial (or ROI, for c3d files). Support only single (first) forceplate 
    for now. """
    def __init__(self, source):
        if is_vicon_instance(source):
            vicon = source
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
        elif is_c3dfile(source):
            """ Read from c3d file. Note: gives force on ROI. """
            c3dfile = source
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
        else:
            raise Exception('Invalid source')
        self.forceall = np.array([self.forcex,self.forcey,self.forcez])
        self.forcetot = np.sqrt(sum(self.forceall**2,1))
                    

class emg:
    """ Read and process EMG data. """

    def __init__(self, source, emg_remapping=None, emg_auto_off=True):
        """ emg_remapping is the replacement dict for EMG electrodes:
        e.g. key 'LGas'='LSol' means that data for LGas will be 
        read from the LSol electrode."""
        self.source = source
        # default plotting scale in medians (channel-specific)
        self.yscale_medians = 1
        # order of Butterworth filter
        self.buttord = 5
        # whether to auto-find disconnected EMG channels
        self.emg_auto_off = emg_auto_off
        # normal data and logical chs
        self.define_emg_names()
        self.emg_remapping = emg_remapping

    def define_emg_names(self):
        """ Defines the electrode mapping. """
        self.ch_normals = gait_defs.emg_normals
        self.ch_names = gait_defs.emg_names
        self.ch_labels = gait_defs.emg_labels
      
    def is_logical_channel(self, chname):
        return chname in self.ch_names
                    
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
        
    def read(self):
        """ Read the EMG data. """
        if is_vicon_instance(self.source):
            vicon = self.source
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
            # read all (physical) EMG channels
            self.data = {}
            for elid in self.chids:
                eldata, elready, elrate = vicon.GetDeviceChannel(emg_id, outputid, elid)
                elname = self.elnames[elid-1]
                self.data[elname] = np.array(eldata)
                if self.emg_auto_off and not self.is_valid_emg(self.data[elname]):
                    self.data[elname] = 'EMG_DISCONNECTED'
            self.datalen = len(eldata)
            assert(self.datalen == framecount * samplesperframe)

        elif is_c3dfile(self.source):
            c3dfile = self.source
            reader = btk.btkAcquisitionFileReader()
            reader.SetFilename(c3dfile)  # check existence?
            reader.Update()
            acq = reader.GetOutput()
            frame1 = acq.GetFirstFrame()  # start of ROI (1-based)
            samplesperframe = acq.GetNumberAnalogSamplePerFrame()
            self.sfrate = acq.GetAnalogFrequency()
            # read physical EMG channels and cut data to L/R gait cycles
            self.data = {}
            self.elnames = []
            for i in btk.Iterate(acq.GetAnalogs()):
                if i.GetDescription().find('EMG') >= 0 and i.GetUnit() == 'V':
                    elname = i.GetLabel()
                    self.elnames.append(elname)
                    self.data[elname] = np.squeeze(i.GetValues())  # rm singleton dimension
                    if self.emg_auto_off and not self.is_valid_emg(self.data[elname]):
                        self.data[elname] = 'EMG_DISCONNECTED'
            self.datalen = len(self.data[elname])
        else:
            raise Exception('Invalid source')
        self.t = np.arange(self.datalen)/self.sfrate
        self.map_data()
        # set scales for plotting channels. Automatic scaling logic may
        # be put here if needed
        self.yscale = {}
        for logch in self.ch_names:
            self.yscale[logch] = .5e-3
            # median scaling - beware of DC!
            #self.yscale_gc1r[elname] = yscale_medians * np.median(np.abs(self.datagc1r[elname]))

    def map_data(self):
        """ Map logical channels into physical ones. For example, the logical name can be 
        'LPer' and the physical channel 'LPer12' will be a match. Thus, the logical names can be 
        shorter than the physical ones. The shortest matches will be found. """
        self.logical_data = {}
        for logch in self.ch_names:
            # check if channel was already assigned (or marked as reused)
            if logch not in self.logical_data:
                # check if channel should be read from some other electrode
                # in this case, the replacement is marked as reused
                if self.emg_remapping and logch in self.emg_remapping:
                    datach = self.emg_remapping[logch]
                    self.logical_data[datach] = 'EMG_REUSED'
                    self.ch_labels[logch] += ' (read from ' + datach +')'
                else:
                    datach = logch
                # find unique matching physical electrode name
                matches = [x for x in self.elnames if x.find(datach) >= 0]
                if len(matches) == 0:
                    error_exit('Cannot find electrode matching requested name '+datach)
                elname = min(matches, key=len)  # choose shortest matching name
                if len(matches) > 1:
                    print('map_data: multiple matching channels for: '+datach+' Choosing: '+elname)
                self.logical_data[logch] = self.data[elname]

        


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
        vgc1 = gaitcycle(vicon)

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
            
            
    def read_raw(self, source, varlist):
        """ Read specified model output variables. Returns a dict. """
        Vars = {}
        if is_vicon_instance(source):
            vicon = source
            SubjectName = vicon.GetSubjectNames()[0]
            for Var in varlist:
                NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
                if not NumVals:
                    raise ModelVarNotFound
                Vars[Var] = np.array(NumVals)
        elif is_c3dfile(source):
            c3dfile = source
            reader = btk.btkAcquisitionFileReader()
            reader.SetFilename(c3dfile)
            reader.Update()
            acq = reader.GetOutput()
            for Var in varlist:
                # TODO: needs error checking + raise ModelVarNotFound
                Vars[Var] = np.squeeze(acq.GetPoint(Var).GetValues())
        else:
            raise Exception('Invalid source')
        return Vars
        
        

    def read_pig_lowerbody(self, source, gcdfile=None):
        """ Read the lower body Plug-in Gait model outputs.
        Variable names starting with 'R' and'L' are normalized into left and right 
        gait cycles, respectively. gcdfile contains PiG normal data variables. 
        Reads into self.Vars """
        
        # the PiG kin* vars contain X,Y,Z components per each variable,
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

            

        vgc1 = gaitcycle()
        vgc1.read(source)

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

