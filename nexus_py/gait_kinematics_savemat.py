from __future__ import division, print_function

#
# Run from within Nexus. Saves active trial data to a .mat file in trial dir.
#

#Code needed for Nexus 2.1
import sys
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")

import ViconNexus

vicon = ViconNexus.ViconNexus()
import numpy as np
import scipy.io

# Extract information from active trial
SubjectName = vicon.GetSubjectNames()[0]
TrialName = vicon.GetTrialName()[1]
SessionLoc = vicon.GetTrialName()[0]

# Extract Plug-in Gait Lower Body Model Outputs using numpy
LPelvisA = np.array([vicon.GetModelOutput(SubjectName, 'LPelvisAngles')])
RPelvisA = np.array([vicon.GetModelOutput(SubjectName, 'RPelvisAngles')])
LHipA = np.array([vicon.GetModelOutput(SubjectName, 'LHipAngles')])
RHipA = np.array([vicon.GetModelOutput(SubjectName, 'RHipAngles')])
LKneeA = np.array([vicon.GetModelOutput(SubjectName, 'LKneeAngles')])
RKneeA = np.array([vicon.GetModelOutput(SubjectName, 'RKneeAngles')])
LAnkA = np.array([vicon.GetModelOutput(SubjectName, 'LAnkleAngles')])
RAnkA = np.array([vicon.GetModelOutput(SubjectName, 'RAnkleAngles')])
LFootPro = np.array ([vicon.GetModelOutput(SubjectName, 'LFootProgressAngles')])
RFootPro = np.array ([vicon.GetModelOutput(SubjectName, 'RFootProgressAngles')])

# Extract Events from Vicon Data
LFStrike = vicon.GetEvents(SubjectName, "Left", "Foot Strike")[0]
RFStrike = vicon.GetEvents(SubjectName, "Right", "Foot Strike")[0]
lenLFS = len(LFStrike)
lenRFS = len(RFStrike)

# save extracted data to a .mat file, so we can run a version of this outside Nexus
data = {}
data['SubjectName']=SubjectName
data['TrialName']=TrialName
data['LPelvisA']=LPelvisA
data['RPelvisA']=RPelvisA
data['LHipA']=LHipA
data['RHipA']=RHipA
data['LKneeA']=LKneeA
data['RKneeA']=RKneeA
data['LAnkA']=LAnkA
data['RAnkA']=RAnkA
data['LFootPro']=LFootPro
data['RFootPro']=RFootPro
print('Saving: '+SessionLoc + TrialName)
scipy.io.savemat(SessionLoc + TrialName + '.mat',data)
