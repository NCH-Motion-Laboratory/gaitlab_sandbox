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
    def __init__(self, source, emg_mapping=None, emg_auto_off=None,
                 pig_normaldata_path=None):
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
        self.model = model_outputs(self.source, pig_normaldata_path)
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
        
    def get_logical_channel(self, chname):
        """ Get EMG channel, filtered if self.passband is set. """
        if self.is_logical_channel(chname):
            data = self.logical_data[chname]
            return self.filt(data, self.passband)
        else:
            raise GaitDataError('Cannot find requested channel: '+chname)

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
        emg_max_interference = 50  # maximum relative interference level
        broadband_bw = 30  # bandwidth of broadband signal
        powerline_freq = 50  # TODO: move into config
        power_bw = 4  # width of power line peak detector (bandpass)
        nharm = 3  # number of harmonics to detect
        # detect 50 Hz harmonics
        linefreqs = (np.arange(nharm+1)+1) * powerline_freq
        debug_print('Using linefreqs:', linefreqs)
        intvar = 0
        for f in linefreqs:
           intvar += np.var(self.filt(y, [f-power_bw/2., f+power_bw/2.]))
        # broadband signal
        emgvar = np.var(self.filt(y, [powerline_freq+10, powerline_freq+10+broadband_bw]))
        intrel = intvar/emgvar
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
    Model variables may have a preceding L/R indicating left/right side.
    For brevity, description dicts etc. are specified for variable names without
    the side info (since descriptions are the same regardless of side).
    This creates some complications, as certain methods expect variable names
    without side and certain methods require it. """
    
    def merge_dicts(self, dict1, dict2):
        """ Merge two dicts, return result. """
        x = dict1.copy()
        x.update(dict2)
        return x
        
    def __init__(self, source, pig_normaldata_path=None):
        """ Sets up variables but does not read data.
        source can be either a ViconNexus instance or a c3d file.
        pig_normaldata_path: a gcd file to read PiG lowerbody normaldata from."""

        self.source = source        
        
        # PiG variables to be read. These are 3d arrays that will be split
        # into x,y,z components.
        self.pig_lowerbody_read_vars = ['LHipMoment',
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

        # Descriptive labels for variables. These are without leading 'L'/'R'.
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
                         
        self.pig_lowerbody_varnames = self.pig_lowerbody_varlabels.keys()

        # muscle length variables to be read
        self.musclelen_read_vars = ['LGMedAntLength',
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

                         
        # muscle length (MuscleLength.mod) variable descriptions (not complete)
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
        
        self.musclelen_varnames = self.musclelen_varlabels.keys()
       
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
        
        # Vars will be read by read_() methods, as needed
        self.Vars = {}
        
        # read PiG normal data from given gcd file
        gcdfile = pig_normaldata_path
        if gcdfile:
            if not os.path.isfile(gcdfile):
                raise Exception('Cannot find specified PiG normal data file')
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

    def read_musclelen(self):
        """ Read muscle length variables produced by MuscleLengths.mod.
        Reads into self.Vars """
        if is_vicon_instance(self.source):
            self.read_raw(self.musclelen_read_vars)
        else:
            # scalars are apparently written into c3d files as 3rd component
            # of a 3-d array
            self.read_raw(self.musclelen_read_vars, components=2)
        
    def read_pig_lowerbody(self):
        """ Read the lower body Plug-in Gait model outputs. """
        self.read_raw(self.pig_lowerbody_read_vars, components='split_xyz')
            
    def read_raw(self, varlist, components=None):
        """ Read specified model output variables into self.Vars.
        components will pick the corresponding components from multidim arrays
        (zero is first component).
        'split_xyz' splits 3-d arrays into separate x,y,z variables. """
        source = self.source
        if is_vicon_instance(source):
            vicon = source
            SubjectName = vicon.GetSubjectNames()[0]
            for Var in varlist:
                NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
                if not NumVals:
                    raise GaitDataError('Cannot read model variable: '+Var+
                    '. \nMake sure that the appropriate model has been executed.')
                # remove singleton dimensions
                self.Vars[Var] = np.squeeze(np.array(NumVals))
        elif is_c3dfile(source):
            c3dfile = source
            reader = btk.btkAcquisitionFileReader()
            reader.SetFilename(c3dfile)
            reader.Update()
            acq = reader.GetOutput()
            for Var in varlist:
                try:
                    self.Vars[Var] = np.transpose(np.squeeze(acq.GetPoint(Var).GetValues()))
                except RuntimeError:
                    raise GaitDataError('Cannot find model variable: ', Var)
        else:
            raise GaitDataError('Invalid data source')
        # postprocessing
        for Var in varlist:
                if Var.find('Moment') > 0:
                    # moment variables have to be divided by 1000 -
                    # apparently stored in Newton-millimeters
                    self.Vars[Var] /= 1000.
                debug_print('read_raw:', Var, 'has shape', self.Vars[Var].shape)
                if components == 'split_xyz':
                    if self.Vars[Var].shape[0] == 3:
                        # split 3-d arrays into x,y,z variables
                        self.Vars[Var+'X'] = self.Vars[Var][0,:]
                        self.Vars[Var+'Y'] = self.Vars[Var][1,:]
                        self.Vars[Var+'Z'] = self.Vars[Var][2,:]
                    else:
                        raise GaitDataError('XYZ split requested but array is not 3-d')
                elif components:
                    self.Vars[Var] = self.Vars[Var][components,:]
                    

    def rm_side(self, varname):
        """ Remove side info (preceding L/R) from variable name. Internally
        some dicts use variable names without the side info. Will have to be
        modified for sideless model variables (not used so far). """
        side = varname[0].upper()
        if side in ['L','R']:
            return varname[1:],side
        else:
            raise Exception('Variable name expected to begin with L or R')

    def is_pig_lowerbody_variable(self, varname):
        """ PiG lower body variable? Without preceding L/R """
        return varname in self.pig_lowerbody_varnames

    def is_kinetic_var(self, varname):
        """ Tell whether a (PiG lowerbody) variable represents kinetics. """
        return self.is_pig_lowerbody_variable(varname) and varname.find('Power') > -1 or varname.find('Moment') > -1
        
    def is_musclelen_variable(self, varname):
        """ Muscle length variable? Without preceding L/R """
        return varname in self.musclelen_varnames

    def description(self, varname):
        """ Returns a more elaborate description for a model variable (L/R),
        if known. If var is normalized to a gait cycle, side will be reflected
        in the name. """
        varname_,side = self.rm_side(varname)
        if varname_ in self.varlabels:
            return self.varlabels[varname_]  #+' ('+side+')'
        else:
            return varname_
        
    def ylabel(self, varname):
        """ Return y label for plotting a given variable (without preceding L/R). """
        if varname in self.ylabels:
            return self.ylabels[varname]
        # use default for muscle len variable
        elif self.is_musclelen_variable(varname):
            return 'Length (mm)'
        else:
            return None
       
    def normaldata(self, varname):
        """ Return the normal data (in the given gcd file) for 
        PiG variable var (without preceding L/R)), if available.
        TODO: normal data for muscle lengths? """
        if varname in self.normdict:
            return self.pig_normaldata[self.normdict[varname]]
        else:
            return None

