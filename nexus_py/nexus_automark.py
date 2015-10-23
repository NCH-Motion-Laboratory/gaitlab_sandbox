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
from gp import getdata

THRESHOLD_FALL = .2  # above minimum
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
    
def get_fp_strike_and_toeoff():
    """ Return forceplate strike and toeoff frames. """
    FP_THRESHOLD = .1  # % of maximum force
    fp0 = getdata.forceplate(vicon)
    ftot = fp0.forcetot
    frel = ftot/ftot.max()
    # in analog frames
    fpstrike = rising_zerocross(frel-FP_THRESHOLD)[0]
    fptoeoff = falling_zerocross(frel-FP_THRESHOLD)[0]
    return np.round(fpstrike/fp0.samplesperframe), np.round(fptoeoff/fp0.samplesperframe)
     
# get data for specified markers
mrkdata = {}    
for marker in ['RHEE','RTOE','RANK','LHEE','LTOE','LANK']:
    roifr,P,V,A = roi_pos_vel_acc(marker)
    mrkdata['roifr'] = roifr
    mrkdata[marker+'_P'] = P
    mrkdata[marker+'_V'] = V
    mrkdata[marker+'_A'] = A
roi0 = roifr[0]

rfootctrV = (mrkdata['RHEE_V']+mrkdata['RTOE_V']+mrkdata['RANK_V'])/3.
rfootctrv = np.sqrt(np.sum(rfootctrV[:,1:3]**2,1))
lfootctrV = (mrkdata['LHEE_V']+mrkdata['LTOE_V']+mrkdata['LANK_V'])/3.
lfootctrv = np.sqrt(np.sum(lfootctrV[:,1:3]**2,1))


print('Initial strike autodetect right:')
thre_fall = rfootctrv.max() * THRESHOLD_FALL + rfootctrv.min()
thre_up = rfootctrv.max() * THRESHOLD_UP + rfootctrv.min()
rfallframes = falling_zerocross(rfootctrv-thre_fall)
rupframes = rising_zerocross(rfootctrv-thre_up)
print(rfallframes+roi0)

print('Initial strike autodetect left:')
thre_fall = lfootctrv.max() * THRESHOLD_FALL + lfootctrv.min()
thre_up = lfootctrv.max() * THRESHOLD_UP + lfootctrv.min()
lfallframes = falling_zerocross(lfootctrv-thre_fall)
lupframes = rising_zerocross(lfootctrv-thre_up)
print(lfallframes+roi0)

fpstrike, fptoeoff = get_fp_strike_and_toeoff()
print('Forceplate strike:', fpstrike, 'toeoff:', fptoeoff)
print('Relative velocities at forceplate:')
if min(abs(lfallframes-(fpstrike-roi0))) < min(abs(rfallframes-(fpstrike-roi0))):
    print('Left:')
    print('Strike:',lfootctrv[fpstrike-roi0]/lfootctrv.max())
    print('Toeoff:',lfootctrv[fptoeoff-roi0]/lfootctrv.max())
    THRESHOLD_FALL = lfootctrv[fpstrike-roi0]/lfootctrv.max()
    THRESHOLD_UP = lfootctrv[fptoeoff-roi0]/lfootctrv.max()
else:
    print('Right:')
    print('Strike:',rfootctrv[fpstrike-roi0]/rfootctrv.max())
    print('Toeoff:',rfootctrv[fptoeoff-roi0]/rfootctrv.max())
    THRESHOLD_FALL = rfootctrv[fpstrike-roi0]/rfootctrv.max()
    THRESHOLD_UP = rfootctrv[fptoeoff-roi0]/rfootctrv.max()

print('Redetect strike and toeoff right:')
thre_fall = rfootctrv.max() * THRESHOLD_FALL + rfootctrv.min()
thre_up = rfootctrv.max() * THRESHOLD_UP + rfootctrv.min()
rfallframes = falling_zerocross(rfootctrv-thre_fall)
rupframes = rising_zerocross(rfootctrv-thre_up)
print(rfallframes+roi0)
print('Redetect strike and toeoff left:')
thre_fall = lfootctrv.max() * THRESHOLD_FALL + lfootctrv.min()
thre_up = lfootctrv.max() * THRESHOLD_UP + lfootctrv.min()
lfallframes = falling_zerocross(lfootctrv-thre_fall)
lupframes = rising_zerocross(lfootctrv-thre_up)
print(lfallframes+roi0)

# mark events
for strike in rfallframes:
    vicon.CreateAnEvent(subjectname, 'Right', 'Foot Strike', strike+roi0, 0.0 )
for fr in rupframes:
    vicon.CreateAnEvent(subjectname, 'Right', 'Foot Off', fr+roi0, 0.0 )
for strike in lfallframes:
    vicon.CreateAnEvent(subjectname, 'Left', 'Foot Strike', strike+roi0, 0.0 )
for fr in lupframes:
    vicon.CreateAnEvent(subjectname, 'Left', 'Foot Off', fr+roi0, 0.0 )



