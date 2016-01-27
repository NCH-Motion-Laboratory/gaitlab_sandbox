# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:41:31 2015

Gaitplotter utility classes for reading gait data.


NEXT:



Exceptions policy:
-for commonly encountered errors (e.g. device not found, channel not found)
create and raise custom exception (GaitDataError). Caller may catch those
-for unexpected errors, raise Exception with description of the error

ROI on Vicon/c3d:
x axis for c3d variables is ROI; i.e. first frame is beginning of ROI (=offset)
However, event times are referred to whole trial. Thus offset needs to be subtracted
from event times to put them on the common x axis.
For Vicon Nexus data, x axis is the whole trial. 


@author: Jussi
"""


from __future__ import division, print_function

import defs
import sys
import copy
# these needed for Nexus 2.1
if not "C:\Program Files (x86)\Vicon\Nexus2.2\SDK\Python" in sys.path:
    sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.2\SDK\Python")
    # needed at least when running outside Nexus
    sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.2\SDK\Win32")
import numpy as np
import ctypes
from scipy import signal
import psutil
import os
import btk  # biomechanical toolkit for c3d reading
import ViconNexus
import glob
import models

# print debug messages if running under IPython
# debug may prevent scripts from working in Nexus (??)
DEBUG = False
def run_from_ipython():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False
if run_from_ipython():
    DEBUG = True        
        

def debug_print(*args):
    if DEBUG:
        print(*args)

class GaitDataError(Exception):
    """ Custom exception class. Stores a message. """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

def viconnexus():
    """ Return a ViconNexus instance. Convenience for calling classes. """
    return ViconNexus.ViconNexus()

def is_vicon_instance(obj):
    """ Check if obj is an instance of ViconNexus """
    return obj.__class__.__name__ == 'ViconNexus'

def is_c3dfile(obj):
    """ Check whether obj is a valid path to c3d file """
    try:
        return os.path.isfile(obj)
    except TypeError:
        return False

def get_video_filenames(trialpath):
    """ Get AVI files corresponding to given trial. """
    trialpath = os.path.splitext(trialpath)[0]
    return glob.glob(trialpath+'*avi')

def get_eclipse_key(trialname, keyname):
    """ Get the Eclipse database entry 'keyname' for the specified trial. Specify
    trialname with full path. Return empty string for no key. """
    # remove c3d extension if present
    trialname = os.path.splitext(trialname)[0]
    debug_print('get eclipse key for '+trialname+'.c3d')
    if not os.path.isfile(trialname+'.c3d'):
        raise GaitDataError('Cannot find .c3d file '+trialname+'.c3d'+'\nMake sure that the trial was processed properly.')
    enfname = trialname + '.Trial.enf'
    value = None
    if os.path.isfile(enfname):
        f = open(enfname, 'r')
        eclipselines = f.read().splitlines()
        f.close()
    else:
        raise GaitDataError('.enf file (Eclipse) not found for trial '+trialname)
    for line in eclipselines:
        eqpos = line.find('=')
        if eqpos > 0:
            key = line[:eqpos]
            val = line[eqpos+1:]
            if key == keyname:
                value = val
    # assume utf-8 encoding for Windows text files, return Unicode object
    # could also use codecs.read with encoding=utf-8 (recommended way)
    return unicode(value, 'utf-8')

def set_eclipse_key(enfname, keyname, oldval, newval):
    """ Update specified Eclipse file, changing 'keyname' with 'oldval' 
    to 'value'. """
    # read existing entries
    if os.path.isfile(enfname):
        with open(enfname, 'r') as f:
            eclipselines = f.read().splitlines()
    else:
        raise GaitDataError('.enf file {0} not found'.format(enfname))
    linesnew = []
    for line in eclipselines:
        eqpos = line.find('=')
        if eqpos > 0:
            # get old key and value
            key = line[:eqpos]
            val = line[eqpos+1:]
            if key == keyname and val == oldval:
                newline = key + '=' + newval
            else:  # key or val mismatch - copy line as is
                newline = line
        else:  # comment or section header - copy as is
            newline = line
        linesnew.append(newline)
    debug_print('new eclipse file:', enfname)
    debug_print(linesnew)
    with open(enfname, 'w') as f:
        for li in linesnew:
            f.write(li+'\n')
   

def rising_zerocross(x):
    """ Return indices of rising zero crossings in sequence,
    i.e. n where x[n] >= 0 and x[n-1] < 0 """
    x = np.array(x)  # this should not hurt
    return np.where(np.logical_and(x[1:] >= 0, x[:-1] < 0))[0]+1

def falling_zerocross(x):
    return rising_zerocross(-x)


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
        """ Normalize frames-based variable var to the cycle.
        New interpolated x axis is 0..100% of the cycle. """
        return np.interp(self.tn, self.t, var[self.start:self.end])

    def cut_analog_to_cycle(self, var):
        """ Crop analog variable (EMG, forceplate, etc. ) to the
        cycle; no interpolation. """
        return var[self.start_smp:self.end_smp]
  
class trial:
    """ A gait trial. Contains:
    -subject and trial info
    -gait cycles (beginning and end frames)
    -analog data (EMG, forceplate, etc.)
    -model variables (Plug-in Gait, muscle length, etc.)
    """
    def __init__(self, source, emg_mapping=None, emg_auto_off=None):
        """ Open trial, read subject info, events etc. """
        self.lfstrikes = []
        self.rfstrikes = []
        self.ltoeoffs = []
        self.rtoeoffs = []
        self.subject = {}
       
        if is_c3dfile(source):
            debug_print('trial: reading from ', source)
            c3dfile = source
            self.trialname = os.path.basename(os.path.splitext(c3dfile)[0])
            self.sessionpath = os.path.dirname(c3dfile)
            reader = btk.btkAcquisitionFileReader()
            reader.SetFilename(c3dfile)  # check existence?
            reader.Update()
            acq = reader.GetOutput()
            # frame offset (start of trial data in frames)
            self.offset = acq.GetFirstFrame()
            self.framerate = acq.GetPointFrequency()
            self.analograte = acq.GetAnalogFrequency()
            #  get events
            for i in btk.Iterate(acq.GetEvents()):
                if i.GetLabel() == "Foot Strike":
                    if i.GetContext() == "Right":
                        self.rfstrikes.append(i.GetFrame())
                    elif i.GetContext() == "Left":
                        self.lfstrikes.append(i.GetFrame())
                    else:
                        raise Exception("Unknown context on foot strike event")
                elif i.GetLabel() == "Foot Off":
                    if i.GetContext() == "Right":
                        self.rtoeoffs.append(i.GetFrame())
                    elif i.GetContext() == "Left":
                        self.ltoeoffs.append(i.GetFrame())
                    else:
                        raise Exception("Unknown context on foot strike event")
                # get subject info
                metadata = acq.GetMetaData()
                # don't ask
                self.subject['Name'] =  metadata.FindChild("SUBJECTS").value().FindChild("NAMES").value().GetInfo().ToString()[0].strip()
                self.subject['Bodymass'] =  metadata.FindChild("PROCESSING").value().FindChild("Bodymass").value().GetInfo().ToDouble()[0]
                debug_print('Subject info read:\n', self.subject)
        elif is_vicon_instance(source):
            debug_print('trial: reading from Vicon Nexus')
            vicon = source
            subjectnames = vicon.GetSubjectNames()  
            debug_print('subject:', subjectnames)
            if len(subjectnames) > 1:
                raise GaitDataError('Nexus returns multiple subjects, not sure which one to use')
            if not subjectnames:
                raise GaitDataError('No subject defined')
            self.subjectname = subjectnames[0]
            self.subject['Name'] = self.subjectname
            Bodymass = vicon.GetSubjectParam(self.subjectname, 'Bodymass')
            # for unknown reasons, above method may return tuple or float, depending on
            # whether script is run from Nexus or from IPython outside Nexus
            if type(Bodymass) == tuple:
                self.subject['Bodymass'] = vicon.GetSubjectParam(self.subjectname, 'Bodymass')[0]
            else:  # hopefully float
                self.subject['Bodymass'] = vicon.GetSubjectParam(self.subjectname, 'Bodymass')
            trialname_ = vicon.GetTrialName()
            self.sessionpath = trialname_[0]
            self.trialname = trialname_[1]
            if not self.trialname:
                raise GaitDataError('No trial loaded')
            # get events
            self.lfstrikes = vicon.GetEvents(self.subjectname, "Left", "Foot Strike")[0]
            self.rfstrikes = vicon.GetEvents(self.subjectname, "Right", "Foot Strike")[0]
            self.ltoeoffs = vicon.GetEvents(self.subjectname, "Left", "Foot Off")[0]
            self.rtoeoffs = vicon.GetEvents(self.subjectname, "Right", "Foot Off")[0]
            # frame offset (start of trial data in frames)
            self.offset = 1
            self.framerate = vicon.GetFrameRate()
            # Get analog rate. This may not be mandatory if analog devices
            # are not used, but currently it needs to succeed.
            devids = vicon.GetDeviceIDs()
            if not devids:
                raise GaitDataError('No analog devices configured in Nexus, cannot determine analog rate')
            else:
                devid = devids[0]
                _,_,self.analograte,_,_,_ = vicon.GetDeviceDetails(devid)
        else:
            raise GaitDataError('Invalid data source specified')
        debug_print('Foot strikes right:', self.rfstrikes, 'left:', self.lfstrikes)
        if len(self.lfstrikes) < 2 or len(self.rfstrikes) <2:
            raise GaitDataError('Too few foot strike events detected, check that data has been processed')
        # sort events (may be in wrong temporal order, at least in c3d files)
        for li in [self.lfstrikes,self.rfstrikes,self.ltoeoffs,self.rtoeoffs]:
            li.sort()
        # get description and notes from Eclipse database
        if not self.sessionpath[-1] == '\\':
            self.sessionpath = self.sessionpath+('\\')
        trialpath = self.sessionpath + self.trialname
        self.eclipse_description = get_eclipse_key(trialpath, 'DESCRIPTION')
        self.eclipse_notes = get_eclipse_key(trialpath, 'NOTES')        
        self.source = source
        self.fp = forceplate(source)
        # TODO: read from config / put as init params?
        # will be read by read_vars
        # TODO: emg params
        self.emg = emg(source, emg_auto_off=emg_auto_off, emg_mapping=emg_mapping)
        self.model = model_outputs(self.source)
        self.kinetics_side = self.kinetics_available()
        # normalized x-axis of 0,1,2..100%
        self.tn = np.linspace(0, 100, 101)
        self.smp_per_frame = self.analograte/self.framerate
        self.scan_cycles()
        self.video_files = get_video_filenames(self.sessionpath+self.trialname)
        
    def kinetics_available(self):
        """ See whether this trial has ground reaction forces for left/right side
        (or neither, or both). Kinetics modelling requires the GRF for the corresponding
        side, i.e. a forceplate strike. Thus look at foot strike event times and 
        determine whether (clean) forceplate contact is happening at each time.
        """
        forcetot = signal.medfilt(self.fp.forcetot) # remove spikes
        subj_weight = self.subject['Bodymass']*9.81
        F_THRESHOLD = .1 * subj_weight  # rise threshold
        FRISE_WINDOW = .05 * self.analograte  # specify in seconds -> analog frames
        FMAX_MAX_DELAY = .85 * self.analograte
        fmax = max(forcetot)
        fmaxind = np.where(forcetot == fmax)[0][0]  # first maximum
        debug_print('kinetics_available: max force:', fmax, 'at:', fmaxind, 'weight:', subj_weight)
        # allow for inaccuracy in weight
        if max(forcetot) < .9 * subj_weight:
            return ''
        # first rise and last fall 
        friseind = rising_zerocross(forcetot-F_THRESHOLD)[0]
        ffallind = falling_zerocross(forcetot-F_THRESHOLD)[-1]
        #  for a strike to be judged as a clean contact:
        # -1st force rise must occur around foot strike
        # -max force must occur in a window after strike
        kinetics = ''
        lfsind = (np.array(self.lfstrikes) - self.offset) * self.fp.samplesperframe
        rfsind = (np.array(self.rfstrikes) - self.offset) * self.fp.samplesperframe
        for i,ind in enumerate(lfsind):
            debug_print('kinetics_available: strike', i, 'on left')
            debug_print('kinetics_available: dist to 1st force rise:', abs(friseind-ind))
            debug_print('kinetics_available: delay to force max:', fmaxind-ind)
            if abs(friseind-ind) <= FRISE_WINDOW:
                if fmaxind-ind  <= FMAX_MAX_DELAY:
                    debug_print('kinetics_available: judged as clean')
                    kinetics = 'L'
        for i,ind in enumerate(rfsind):
            debug_print('kinetics_available: strike', i, 'on right')
            debug_print('kinetics_available: dist to 1st force rise:', abs(friseind-ind))
            debug_print('kinetics_available: delay to force max:', fmaxind-ind)
            if abs(friseind-ind) <= FRISE_WINDOW:
                if fmaxind-ind  <= FMAX_MAX_DELAY:
                    if kinetics == '':
                        debug_print('kinetics_available: judged as clean')
                        kinetics = 'R'
                    else:
                        # should never happen
                        raise Exception('Clean contact on both feet, how come?')
        return kinetics

    def scan_cycles(self):
        """ Scan for foot strike events and create gait cycle objects. """
        self.cycles = []
        for strikes in [self.lfstrikes, self.rfstrikes]:
            len_s = len(strikes)
            if len_s < 2:
                raise GaitDataError("Insufficient number of foot strike events detected. "+
                        "Check that the trial has been processed.")
            if strikes == self.lfstrikes:
                toeoffs = self.ltoeoffs
                context = 'L'
            else:
                toeoffs = self.rtoeoffs
                context = 'R'
            for k in range(0, len_s-1):
                start = strikes[k]
                end = strikes[k+1]
                toeoff = [x for x in toeoffs if x > start and x < end]
                if len(toeoff) != 1:
                    raise GaitDataError('Expected a single toe-off event during gait cycle')
                cycle = gaitcycle(start, end, self.offset, toeoff[0], context, self.smp_per_frame)
                self.cycles.append(cycle)
        self.ncycles = len(self.cycles)
                 
    def get_cycle(self, context, ncycle):
        """ e.g. ncycle=2 and context='L' returns 2nd left gait cycle. """
        cycles = [cycle for cycle in self.cycles if cycle.context == context]
        if len(cycles) < ncycle:
            return None
        else:
            return cycles[ncycle-1]
    
class forceplate:
    """ Read and process forceplate data. source may be a c3d file or a
    ViconNexus instance. Gives x,y,z and total forces during the whole
    trial (or ROI, for c3d files). Support only single (first) forceplate 
    for now. """
    def __init__(self, source):
        self.nplates = 1  # need to also implement reading multiple plates later
        if is_vicon_instance(source):
            vicon = source
            framecount = vicon.GetFrameCount()
            self.framerate = vicon.GetFrameRate()
            fpdevicename = 'Forceplate'
            devicenames = vicon.GetDeviceNames()
            if fpdevicename in devicenames:
                fpid = vicon.GetDeviceIDFromName(fpdevicename)
            else:
               raise GaitDataError('Forceplate device not found')
            # DType should be 'ForcePlate', drate is sampling rate
            dname,dtype,drate,outputids,_,_ = vicon.GetDeviceDetails(fpid)
            self.sfrate = drate
            self.samplesperframe = drate / self.framerate  # fp samples per Vicon frame
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
            # TODO: raise DeviceNotFound if needed
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

    def __init__(self, source, emg_mapping=None, emg_auto_off=True):
        """ emg_mapping is the replacement dict for EMG electrodes:
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
        self.emg_mapping = emg_mapping
        self.passband = None
    
    def set_filter(self, passband):
        """ Set EMG passband (in Hz). None for off. Affects get_channel. """
        self.passband = passband
        
    def define_emg_names(self):
        """ Defines the electrode mapping. """
        self.ch_normals = defs.emg_normals
        self.ch_names = defs.emg_names
        self.ch_labels = defs.emg_labels
      
    def is_logical_channel(self, chname):
        return chname in self.ch_names
                    
    def is_valid_emg(self, y):
        """ Check whether channel contains a valid EMG signal. Usually invalid
        signal can be identified by the presence of large powerline (harmonics)
        compared to broadband signal. Cause is typically disconnected/badly 
        connected electrodes. """
        # max. relative interference at 50 Hz harmonics
        emg_max_interference = 30  # maximum relative interference level (dB)
        # bandwidth of broadband signal. should be less than distance between powerline harmonics
        broadband_bw = 30
        powerline_freq = 50  # TODO: move into config
        power_bw = 4  # width of power line peak detector (bandpass)
        nharm = 3  # number of harmonics to detect
        # detect 50 Hz harmonics
        linefreqs = (np.arange(nharm+1)+1) * powerline_freq
        debug_print('Using linefreqs:', linefreqs)
        intvar = 0
        for f in linefreqs:
           intvar += np.var(self.filt(y, [f-power_bw/2., f+power_bw/2.])) / power_bw
        # broadband signal
        emgvar = np.var(self.filt(y, [powerline_freq+10, powerline_freq+10+broadband_bw])) / broadband_bw
        intrel = 10*np.log10(intvar/emgvar)
        debug_print('rel. interference: ', intrel)
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
        #yfilt = yfilt - signal.medfilt(yfilt, 21)        
        return yfilt
       
    def read(self):
        """ Read the EMG data. """
        if is_vicon_instance(self.source):
            vicon = self.source
            framerate = vicon.GetFrameRate()
            framecount = vicon.GetFrameCount()
            emg_devname = defs.emg_devname
            devnames = vicon.GetDeviceNames()
            if emg_devname in devnames:
                emg_id = vicon.GetDeviceIDFromName(emg_devname)
            else:
               raise GaitDataError('EMG device not found')
            # DType should be 'other', drate is sampling rate
            dname,dtype,drate,outputids,_,_ = vicon.GetDeviceDetails(emg_id)
            samplesperframe = drate / framerate
            self.sfrate = drate        
            # Myon should only have 1 output; if zero, EMG was not found (?)
            if len(outputids) != 1:
                raise GaitDataError('Expected 1 EMG output')
            outputid = outputids[0]
            # get list of channel names and IDs
            _,_,_,_,self.elnames,self.chids = vicon.GetDeviceOutputDetails(emg_id, outputid)
            # read all (physical) EMG channels
            self.data = {}
            for elid in self.chids:
                eldata, elready, elrate = vicon.GetDeviceChannel(emg_id, outputid, elid)
                elname = self.elnames[elid-1]
                self.data[elname] = np.array(eldata)
                debug_print('electrode:', elname)
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
            if self.elnames:
                self.datalen = len(self.data[elname])
            else:
                raise GaitDataError('No EMG channels found in data!')
        else:
            raise GaitDataError('Invalid data source')
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
                if self.emg_mapping and logch in self.emg_mapping:
                    datach = self.emg_mapping[logch]
                    self.logical_data[datach] = 'EMG_REUSED'
                    self.ch_labels[logch] += ' (read from ' + datach +')'
                else:
                    datach = logch
                # find unique matching physical electrode name
                matches = [x for x in self.elnames if x.find(datach) >= 0]
                if len(matches) == 0:
                    raise GaitDataError('Cannot find a match for requested EMG channel '+datach)
                elname = min(matches, key=len)  # choose shortest matching name
                if len(matches) > 1:
                    debug_print('map_data:', matches, '->', elname)
                self.logical_data[logch] = self.data[elname]

    def cut_to_cycle(self, cyc):
        """ Cut EMG data to a given gait cycle cyc. Also returns a time axis
        0..100% of the same length as the EMG data. """
        logical_data_cyc = {}
        tn = np.linspace(0, 100, cyc.len_smp)
        for ch in self.logical_data:
            data = self.logical_data[ch]
            if data == 'EMG_DISCONNECTED' or data == 'EMG_REUSED':
                logical_data_cyc[ch] = data
            else:
                logical_data_cyc[ch] = cyc.cut_analog_to_cycle(data)
        return tn, logical_data_cyc
       

class model_outputs:
    """ Handles model output variables, e.g. Plug-in Gait, muscle length etc. 
    Actual model data (variable names etc.) is in models.py. """

    def __init__(self, source):
        self.source = source
        # local copy of models is mutable, so need a fresh copy instead of binding
        self.models = copy.deepcopy(models.models_all)  
        self.varnames = []
        self.varlabels = {}
        self.normaldata_map = {}
        self.ylabels = {}
        self.modeldata = {}  # read by read_model as necessary
        self.normaldata = {}  # ditto
        # update varnames etc. for this class
        for model in self.models:
            self.varnames += model.varnames
            self.varlabels.update(model.varlabels)
            self.normaldata_map.update(model.normaldata_map)
            self.ylabels.update(model.ylabels)

    def get_model(self, varname):
        """ Returns model corresponding to varname. """
        for model in self.models:
            if varname in model.varnames:
                return model

    def read_model(self, model):
        """ Read variables of given model (instance of models.model) and normal data
        into self.modeldata. """
        debug_print('Reading model:', model.desc)
        source = self.source
        if is_vicon_instance(source):
            # read from Nexus
            vicon = source
            SubjectName = vicon.GetSubjectNames()[0]
            for Var in model.read_vars:
                debug_print('Getting:', Var)
                NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
                if not NumVals:
                    raise GaitDataError('Cannot read model variable: '+Var+
                    '. \nMake sure that the appropriate model has been executed in Nexus.')
                # remove singleton dimensions
                self.modeldata[Var] = np.squeeze(np.array(NumVals))
        elif is_c3dfile(source):
            # read from c3d            
            c3dfile = source
            reader = btk.btkAcquisitionFileReader()
            reader.SetFilename(c3dfile)
            reader.Update()
            acq = reader.GetOutput()
            for Var in model.read_vars:
                try:
                    self.modeldata[Var] = np.transpose(np.squeeze(acq.GetPoint(Var).GetValues()))
                except RuntimeError:
                    raise GaitDataError('Cannot find model variable in c3d file: ', Var)
        else:
            raise GaitDataError('Invalid data source')
        # postprocessing
        for Var in model.read_vars:
                if Var.find('Moment') > 0:
                    # moment variables have to be divided by 1000 -
                    # apparently stored in Newton-millimeters
                    debug_print('Normalizing:', Var)                    
                    self.modeldata[Var] /= 1000.
                #debug_print('read_raw:', Var, 'has shape', self.modeldata[Var].shape)
                components = model.read_strategy
                if components == 'split_xyz':
                    if self.modeldata[Var].shape[0] == 3:
                        # split 3-d arrays into x,y,z variables
                        self.modeldata[Var+'X'] = self.modeldata[Var][0,:]
                        self.modeldata[Var+'Y'] = self.modeldata[Var][1,:]
                        self.modeldata[Var+'Z'] = self.modeldata[Var][2,:]
                    else:
                        raise GaitDataError('XYZ split requested but array is not 3-d')
                elif components:
                    self.modeldata[Var] = self.modeldata[Var][components,:]
        # read normal data if it exists. only gcd files supported for now
        gcdfile = model.normaldata_path
        if gcdfile:
            if not os.path.isfile(gcdfile):
                raise Exception('Cannot find specified normal data file')
            f = open(gcdfile, 'r')
            lines = f.readlines()
            f.close()
            # normaldata variables are named as in the file. the model should have a corresponding map.
            normaldata = {}
            for li in lines:
                if li[0] == '!':  # it's a variable name
                    thisvar = li[1:li.find(' ')]  # set dict key
                    normaldata[thisvar] = list()
                elif li[0].isdigit() or li[0] == '-':  # it's a number, so read into list
                    normaldata[thisvar].append([float(x) for x in li.split()])
            self.normaldata.update(normaldata)

    def is_kinetic_var(self, varname):
        """ Tell whether a variable represents kinetics. Works at least for PiG variables... """
        return varname.find('Power') > -1 or varname.find('Moment') > -1
       
    def get_normaldata(self, varname):
        """ Return the normal data for variable varname, if available. """
        model = self.get_model(varname)
        if model and varname in model.normaldata_map:
            normalkey = model.normaldata_map[varname]
            return self.normaldata[normalkey]
        else:
            return None

