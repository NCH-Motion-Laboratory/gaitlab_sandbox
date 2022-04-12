# -*- coding: utf-8 -*-
"""

Rigid body extrapolation between trials. The idea:

-you have a rigid body of at least 3 markers ("reference markers") available in all trials
-the position of some markers ("extrapolation markers") relative to the rigid body is available in a "reference trial"
-you want to calculate the positions of these markers in some "extrapolation trials" and insert the trajectories into Nexus

Please make sure that Nexus is running before you run this script.

NB: this script will overwrite marker trajectories in the extrapolation trials
without asking. Make sure your filenames are correct etc.

@author: jnu@iki.fi
"""

import gaitutils

# get the Vicon SDK object
vicon = gaitutils.nexus.viconnexus()

# the reference trial; this should contain all markers (both reference and extrapolation markers)
# typically a static trial, but can be also dynamic
# NB: if using backslash as directory separator, you need to put 'r' in front of the pathname strings
ref_trial = r"C:\Temp\04_Alisa\2020_9_10_robot\03"

# the reference frame to use to calculate the positions of the extrapolation markers
# if the reference trial has a good reconstruction for certain frames only, it
# may be necessary to specify the frame
ref_frame = 0

# list of trials for which extrapolation should be performed
extrap_trials = [r"C:\Temp\04_Alisa\2020_9_10_robot\06",
                 r"C:\Temp\04_Alisa\2020_9_10_robot\07"]

# list of rigid body reference markers; these need to exist in all the trials
ref_markers = ['LASI', 'PELVIS_LEFT', 'PELVIS_FRONT']

# list of markers to extrapolate; these need to exist in the reference trials only
extrap_markers = ['RPSI', 'RASI', 'LPSI']

# run the extrapolation
gaitutils.nexus.rigid_body_extrapolate(vicon, ref_trial, extrap_trials, ref_markers, extrap_markers, ref_frame=ref_frame)

