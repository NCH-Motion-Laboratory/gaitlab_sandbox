# -*- coding: utf-8 -*-
"""
Read EMG channels from Nexus. Calculate linear envelope and rectified signal.
Downsample and write as model outputs.

Based on extractEMG.py by Ned Pires.

@author: Jussi (jnu@iki.fi)

requires: gaitutils, numpy, scipy
"""

# %% init

import numpy as np
import scipy
import logging

from gaitutils import nexus

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# define parameters
HPF = 5  # high pass frequency
LPF = 40  # low pass frequency
BUTTER_ORDER = 4  # filter order
emg_devname = 'Myon EMG'  # name of the EMG device in Nexus

# read EMG data
vicon = nexus.viconnexus()
emgdata = nexus._get_emg_data(vicon)['data']
meta = nexus._get_metadata(vicon)
emgrate = meta['analograte']
framerate = meta['framerate']
subject = meta['name']
nframes = meta['length']

# get roi length
startFrame = vicon.GetTrialRegionOfInterest()[0]
endFrame = vicon.GetTrialRegionOfInterest()[1]
roi_length = endFrame - startFrame + 1

# apply hpf
b_HPF, a_HPF = scipy.signal.butter(
    BUTTER_ORDER, HPF * 2 / emgrate, 'high', analog=False
)
emg_hpf = {
    chname: scipy.signal.filtfilt(b_HPF, a_HPF, chdata)
    for chname, chdata in emgdata.items()
}

# remove dc
emg_dc_offset = {
    emgname: emg_hpf[emgname] - np.mean(emg_hpf[emgname]) for emgname in emgdata.keys()
}

# rectify
emg_rectified = {emgname: np.abs(emg_dc_offset[emgname]) for emgname in emgdata.keys()}

# apply lpf
b_LPF, a_LPF = scipy.signal.butter(BUTTER_ORDER, LPF * 2 / emgrate, 'low', analog=False)
emg_rectified_lpf = {
    emgname: scipy.signal.filtfilt(b_LPF, a_LPF, emg_rectified[emgname])
    for emgname in emgdata.keys()
}

# downsample
emg_rectified_ds = {
    emgname + '_Rectified': scipy.signal.resample(emg_rectified[emgname], nframes)
    for emgname in emgdata
}
emg_linearenvelope_ds = {
    emgname
    + '_LinearEnvelope': scipy.signal.resample(emg_rectified_lpf[emgname], nframes)
    for emgname in emgdata
}

# %% write the processed EMG as model outputs

# create the new model outputs in Nexus
existing_outputs = vicon.GetModelOutputNames(subject)
new_outputs = emg_rectified_ds.keys() + emg_linearenvelope_ds.keys()

for output in set(new_outputs) - set(existing_outputs):
    logger.debug('creating model output %s' % output)
    vicon.CreateModelOutput(
        subject,
        output,
        'EMG',
        {'EMG', 'EMG', 'EMG'},
        {'Electric Potential', 'Electric Potential', 'Electric Potential'},
    )

exists = [True] * nframes

for chname, data in emg_rectified_ds.items():
    logger.debug('writing data for %s' % chname)
    vicon.SetModelOutput(subject, chname, [emg_rectified_ds[chname]], exists)

for chname, data in emg_linearenvelope_ds.items():
    logger.debug('writing data for %s' % chname)
    vicon.SetModelOutput(
        subject,
        chname,
        [emg_linearenvelope_ds[chname]],
        exists,
    )
