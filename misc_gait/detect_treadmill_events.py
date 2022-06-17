# -*- coding: utf-8 -*-
"""
Detect AMTI treadmill events from virtual forceplates

"""


import gaitutils
import matplotlib.pyplot as plt


# %% read force data directly from Nexus

vicon = gaitutils.nexus.viconnexus()
fdata = gaitutils.nexus._get_forceplate_data(vicon)

fdata1 = fdata[0]
fz = fdata1['F'][:, 2]

plt.plot(fz[:5000])



# %% create trial object from Nexus

# this will read the underlying C3D trial
trial = gaitutils.trial.nexus_trial(from_c3d=True)

# this will read the trial via the Nexus API
trial = gaitutils.trial.nexus_trial(from_c3d=True)



# %% create trial object from C3D file - no Nexus needed

from pathlib import Path

c3dfile = Path('D:/ViconData/Exo_cross-sectional/Pilot_jussi/2022_3_18/2022_3_1808.c3d')

trial = gaitutils.trial.Trial(c3dfile)

t, fdata = trial.get_forceplate_data(0)

plt.plot(fdata[:5000, 2])
