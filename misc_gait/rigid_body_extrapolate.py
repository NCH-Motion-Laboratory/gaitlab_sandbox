# -*- coding: utf-8 -*-
"""

Rigid body extrapolation across trials. The idea:

-you have a (relatively) rigid body of N markers
-all N markers are present in the "reference trial"
-at least 3 of the markers ("reference markers") are available in all trials
-you want to extrapolate the rest (N-3) markers ("extrapolation markers") 
 which may be missing in some of the trials ("extrapolation trials")

This script will:

1) load the reference trial in Nexus and compute the positions of extrapolation markers
relative to reference markers
2) load each extrapolation trial in turn, determine the position of the reference markers
for each frame, determine the corresponding positions of the extrapolation markers, and write
them into Nexus
3) save each extrapolated trial as C3D file.

Please make sure that Nexus is running before you run this script.

NB: this script will overwrite marker trajectories in the extrapolation trials
without asking. Make sure your filenames are correct etc.

@author: jnu@iki.fi
"""

import gaitutils
import logging

# enable logging
logging.basicConfig(level=logging.DEBUG)

# get the Vicon SDK object
vicon = gaitutils.nexus.viconnexus()

# the reference trial; this should contain all markers (both reference and extrapolation markers)
# typically a static trial, but can also be dynamic (there is no fundamental difference)
# NOTE:
# -if using backslash as directory separator, you need to put 'r' in front of the pathname strings
# -trial names are basically C3D filenames, but can be given without the .C3D extension
ref_trial = r"C:\Temp\04_Alisa\2020_9_10_robot\03"

# if necessary, set the frame number in the reference trial from which the relative positions
# of extrapolation markers will be computed
ref_frame = 0

# list of trials for which extrapolation should be performed
extrap_trials = [r"C:\Temp\04_Alisa\2020_9_10_robot\06",
                 r"C:\Temp\04_Alisa\2020_9_10_robot\07"]

# list of the rigid body reference markers; these need to exist in all the trials
ref_markers = ['LASI', 'PELVIS_LEFT', 'PELVIS_FRONT']

# list of markers to extrapolate; these need to exist in the reference trials only
extrap_markers = ['RPSI', 'RASI', 'LPSI']

# run the extrapolation
gaitutils.nexus.rigid_body_extrapolate(vicon, ref_trial, extrap_trials, ref_markers, extrap_markers, ref_frame=ref_frame)

