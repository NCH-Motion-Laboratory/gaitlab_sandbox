from __future__ import division, print_function

"""
Test the Vicon object for communicating with Vicon Nexus application.
Works with Nexus 2.1.x
@author: jussi
"""

import sys
import numpy as np
import matplotlib.pyplot as plt



# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")

import ViconNexus


# Python objects communicate directly with the Nexus application.
# Before using the vicon object, Nexus needs to be started and a subject loaded.
vicon = ViconNexus.ViconNexus()
SubjectName = vicon.GetSubjectNames()[0]
SessionPath = vicon.GetTrialName()[0]
TrialName = vicon.GetTrialName()[1]

# peripherals (force plate, EMG, etc.)
DeviceList = vicon.GetDeviceNames()

# list PIG model outputs
PIGvars=vicon.GetModelOutputNames('Roosa')

# gives info about the variables associated with certain model output
gr1,comp1,types1=vicon.GetModelOutputDetails('Roosa','LHipMoment')

"""
Test extraction of kinetics variables.
Note that kinetics is only available for the side where forceplate contact
occurs. E.g. analyzing a trial with left foot forceplate contact will only
give left side kinetics. (???)

# gives tuple with 2 list elements
LHipMomT = vicon.GetModelOutput(SubjectName, 'LHipMoment')
# unpack gives nested list Moments: 3 lists of 370 elements
# Something has boolean values, not clear what
LHipMomentsL,Something = LHipMomT
LHipMoments = np.array(LHipMomentsL)
LHipX = LHipMoments[0][0:200]
"""

# ...but Vicon example does directly like this
LHipMomX = np.array([vicon.GetModelOutput(SubjectName, 'LHipMoment')])
RHipMomX = np.array([vicon.GetModelOutput(SubjectName, 'RHipMoment')])

# frames where foot strikes occur (1-frame discrepancies with Nexus?)
LFStrike = vicon.GetEvents(SubjectName, "Left", "Foot Strike")[0]
RFStrike = vicon.GetEvents(SubjectName, "Right", "Foot Strike")[0]
# 2 strikes is one complete gait cycle, needed for analysis
lenLFS = len(LFStrike)
lenRFS = len(RFStrike)
if lenLFS and lenRFS < 2:
    raise Exception("Could not detect a complete gait cycle")
# extract times for 1st gait cycles, L and R
LGC1Start=min(LFStrike[0:2])
LGC1End=max(LFStrike[0:2])
LGC1Len=LGC1End-LGC1Start
RGC1Start=min(RFStrike[0:2])
RGC1End=max(RFStrike[0:2])
RGC1Len=RGC1End-RGC1Start

# data corresponding to 1st gait cycles
LHipMomX1=LHipMomX[0][0][0][LGC1Start:LGC1End]
RHipMomX1=RHipMomX[0][0][0][RGC1Start:RGC1End]
# interp variables from gait cycle grid to normalized grid (0...100%)
tn = np.linspace(0, 100, 101)
LGC1t = np.linspace(0, 100, LGC1Len)
RGC1t = np.linspace(0, 100, RGC1Len)
Norm_LHipMomX1 = np.interp(tn, LGC1t, LHipMomX1)
Norm_RHipMomX1 = np.interp(tn, RGC1t, RHipMomX1)

# plot
plt.figure()
plot1 = plt.plot(tn, Norm_RHipMomX1, '#DC143C')
#plt.title('Pelvic tilt', fontsize=10)
plt.xlabel('Percentage Gait Cycle (%)')
#plt.ylabel('Pst     ($^\circ$)      Ant')
#plt.ylim(0., 60.0)
plt.show()

# plot
plt.figure()
plot1 = plt.plot(tn, Norm_LHipMomX1, '#DC143C')
#plt.title('Pelvic tilt', fontsize=10)
plt.xlabel('Percentage Gait Cycle (%)')
#plt.ylabel('Pst     ($^\circ$)      Ant')
#plt.ylim(0., 60.0)
plt.show()









