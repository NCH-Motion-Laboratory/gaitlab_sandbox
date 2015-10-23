# -*- coding: utf-8 -*-
"""

Automatically mark gait cycle events.

@author: Jussi
"""

from __future__ import division, print_function

import sys
if not "C:\Program Files (x86)\Vicon\Nexus2.2\SDK\Python" in sys.path:
    sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.2\SDK\Python")
    # needed at least when running outside Nexus
    sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.2\SDK\Win32")
import numpy as np
from scipy import signal
import ViconNexus
import matplotlib.pyplot as plt

THRESHOLD_FALL = .1  # above minimum
THRESHOLD_UP = .5

vicon = ViconNexus.ViconNexus()
subjectnames = vicon.GetSubjectNames()  
trialname_ = vicon.GetTrialName()
sessionpath = trialname_[0]
trialname = trialname_[1]
subjectname = subjectnames[0]

def rising_zerocross(x):
    """ Return indices of rising zero crossings in sequence,
    i.e. n where x[n] >= 0 and x[n-1] < 0 """
    x = np.array(x)  # this should not hurt
    return np.where(np.logical_and(x[1:] >= 0, x[:-1] < 0))[0]+1

def falling_zerocross(x):
    return rising_zerocross(-x)

def roi_pos_vel_acc(marker):
    """ Get position, velocity and acceleration 
    for specified marker over Nexus ROI. """
    roi = vicon.GetTrialRegionOfInterest()
    roifr = range(roi[0],roi[1])
    x,y,z,_ = vicon.GetTrajectory(subjectname, marker)
    xroi = x[roi[0]:roi[1]]
    yroi = y[roi[0]:roi[1]]
    zroi = z[roi[0]:roi[1]]
    Proi = np.array([xroi,yroi,zroi]).transpose()
    Vroi = np.gradient(Proi)[0]
    Aroi = np.gradient(Vroi)[0]
    return roifr, Proi, Vroi, Aroi
     
# get data for specified markers
mrkdata = {}    
for marker in ['RHEE','RTOE','RANK','LHEE','LTOE','LANK']:
    roifr,P,V,A = roi_pos_vel_acc(marker)
    mrkdata['roifr'] = roifr
    mrkdata[marker+'_P'] = P
    mrkdata[marker+'_V'] = V
    mrkdata[marker+'_A'] = A
roi0 = roifr[0]

print('Autodetect right:')
# compute foot centre velocity
footctrV = (mrkdata['RHEE_V']+mrkdata['RTOE_V']+mrkdata['RANK_V'])/3.
rfootctrv = np.sqrt(np.sum(footctrV[:,1:3]**2,1))
# find local minima below zero
rng = rfootctrv.max()-rfootctrv.min()
thre_fall = rng * THRESHOLD_FALL + rfootctrv.min()
thre_up = rng * THRESHOLD_UP + rfootctrv.min()
fallframes = falling_zerocross(rfootctrv-thre_fall)
upframes = rising_zerocross(rfootctrv-thre_up)
print(fallframes+roi0)
for strike in fallframes:
    vicon.CreateAnEvent(subjectname, 'Right', 'Foot Strike', strike+roi0, 0.0 )
for fr in upframes:
    vicon.CreateAnEvent(subjectname, 'Right', 'Foot Off', fr+roi0, 0.0 )


print('Autodetect left:')
# compute foot centre velocity
footctrV = (mrkdata['LHEE_V']+mrkdata['LTOE_V']+mrkdata['LANK_V'])/3.
lfootctrv = np.sqrt(np.sum(footctrV[:,1:3]**2,1))
# find local minima below zero
rng = lfootctrv.max()-lfootctrv.min()
thre_fall = rng * THRESHOLD_FALL + lfootctrv.min()
thre_up = rng * THRESHOLD_UP + lfootctrv.min()
fallframes = falling_zerocross(lfootctrv-thre_fall)
upframes = rising_zerocross(lfootctrv-thre_up)
print(fallframes+roi0)
for strike in fallframes:
    vicon.CreateAnEvent(subjectname, 'Left', 'Foot Strike', strike+roi0, 0.0 )
for fr in upframes:
    vicon.CreateAnEvent(subjectname, 'Left', 'Foot Off', fr+roi0, 0.0 )




