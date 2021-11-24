# -*- coding: utf-8 -*-
"""
Look at Francesco Cenni's EMG data (JYU)

@author: vicon123
"""


# %%
import gaitutils
from gaitutils import cfg

# set the EMG device name
cfg.emg.devname = 'emg'
# set labels for each physical channel name; this also defines the physical channels to read
cfg.emg.channel_labels = {'1': 'Channel 1', '2': 'Channel 2', '3': 'Channel 3', '4': 'Channel 4'}
# define context for each channel (L/R)
cfg.emg.channel_context = {'1': 'R', '2': 'R', '3': 'L', '4': 'L'}
# do not try to autodetect bad channels
cfg.emg.autodetect_bads = False

# load current trial from Nexus
tr = gaitutils.trial.nexus_trial(from_c3d=False)
# we can scale the EMG before reading
tr.emg.correction_factor = .001

# define layout for plotting; each element is a channel name
layout = [['1'], ['2'], ['3'], ['4']]

# plot unnormalized data
gaitutils.viz.plot_trials(tr, layout, cycles='unnormalized')

# plot data normalized to gait cycles
#gaitutils.viz.plot_trials(tr, layout, cycles={'emg': 'all', 'model': None, 'marker': None}, max_cycles={'emg': None, 'model': None, 'marker': None})

gaitutils.viz.plot_trials(tr, layout, cycles={'emg': 'all'}, max_cycles={'emg': None})


# %%
didef = {'a': 1, 'b': 2, 'c': 3}
di = {'a': 4, 'c': 3}

didef.update(di)

didef
