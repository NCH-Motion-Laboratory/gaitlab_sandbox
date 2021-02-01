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

from gaitutils import nexus, sessionutils, cfg

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _compute_emg_envelope():
    """Compute EMG linear envelope and rectified signal for currently open Nexus trial.

    Write as model outputs.
    """

    # define parameters
    HPF = 5  # high pass frequency
    LPF = 10  # low pass frequency
    BUTTER_ORDER = 4  # filter order

    # read EMG data
    vicon = nexus.viconnexus()
    emgdata = nexus._get_emg_data(vicon)['data']
    meta = nexus._get_metadata(vicon)
    emgrate = meta['analograte']
    subject = meta['name']
    nframes = meta['length']

    # apply hpf
    b_HPF, a_HPF = scipy.signal.butter(
        BUTTER_ORDER, HPF * 2 / emgrate, 'high', analog=False
    )
    emg_hpf = {
        chname: scipy.signal.filtfilt(b_HPF, a_HPF, chdata)
        for chname, chdata in emgdata.items()
    }

    # rectify
    emg_rectified = {chname: np.abs(chdata) for chname, chdata in emg_hpf.items()}

    # apply lpf
    b_LPF, a_LPF = scipy.signal.butter(
        BUTTER_ORDER, LPF * 2 / emgrate, 'low', analog=False
    )
    emg_rectified_lpf = {
        chname: scipy.signal.filtfilt(b_LPF, a_LPF, chdata)
        for chname, chdata in emg_rectified.items()
    }

    # downsample
    emg_rectified_ds = {
        chname + '_Rectified': scipy.signal.resample(chdata, nframes)
        for chname, chdata in emg_rectified.items()
    }
    emg_linearenvelope_ds = {
        chname + '_LinearEnvelope': scipy.signal.resample(chdata, nframes)
        for chname, chdata in emg_rectified_lpf.items()
    }

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

    # write the processed EMG as model outputs
    exists = [True] * nframes

    for chname, chdata in emg_rectified_ds.items():
        logger.debug('writing data for %s' % chname)
        vicon.SetModelOutput(subject, chname, [chdata], exists)

    for chname, chdata in emg_linearenvelope_ds.items():
        logger.debug('writing data for %s' % chname)
        vicon.SetModelOutput(
            subject,
            chname,
            [chdata],
            exists,
        )


if __name__ == '__main__':
    vicon = nexus.viconnexus()
    # get and process all session trials
    sp = nexus.get_sessionpath()
    c3ds = sessionutils.get_c3ds(sp)
    for c3dfile in c3ds:
        logger.debug('opening %s' % c3dfile)
        nexus._open_trial(c3dfile)
        _compute_emg_envelope()
        vicon.SaveTrial(cfg.autoproc.nexus_timeout)
