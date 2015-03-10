from __future__ import division, print_function

#
# Run from within Nexus. Saves active trial data to a file in the trial dir.
#

#Code needed for Nexus 2.1
import sys
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")

import ViconNexus

vicon = ViconNexus.ViconNexus()
import numpy as np
import pickle

# Extract information from active trial
SubjectName = vicon.GetSubjectNames()[0]
TrialName = vicon.GetTrialName()[1]
SessionLoc = vicon.GetTrialName()[0]

# Extract Plug-in Gait Lower Body Model Outputs using numpy
modeldata = {}
modeldata['LPelvisA'] = np.array([vicon.GetModelOutput(SubjectName, 'LPelvisAngles')])
modeldata['RPelvisA'] = np.array([vicon.GetModelOutput(SubjectName, 'RPelvisAngles')])
modeldata['LHipA'] = np.array([vicon.GetModelOutput(SubjectName, 'LHipAngles')])
modeldata['RHipA'] = np.array([vicon.GetModelOutput(SubjectName, 'RHipAngles')])
modeldata['LKneeA'] = np.array([vicon.GetModelOutput(SubjectName, 'LKneeAngles')])
modeldata['RKneeA'] = np.array([vicon.GetModelOutput(SubjectName, 'RKneeAngles')])
modeldata['LAnkA'] = np.array([vicon.GetModelOutput(SubjectName, 'LAnkleAngles')])
modeldata['RAnkA'] = np.array([vicon.GetModelOutput(SubjectName, 'RAnkleAngles')])
modeldata['LFootPro'] = np.array ([vicon.GetModelOutput(SubjectName, 'LFootProgressAngles')])
modeldata['RFootPro'] = np.array ([vicon.GetModelOutput(SubjectName, 'RFootProgressAngles')])

# Extract Events from Vicon Data
modeldata['LFStrike'] = vicon.GetEvents(SubjectName, "Left", "Foot Strike")[0]
modeldata['RFStrike'] = vicon.GetEvents(SubjectName, "Right", "Foot Strike")[0]
modeldata['lenLFS'] = len(modeldata['LFStrike'])
modeldata['lenRFS'] = len(modeldata['RFStrike'])

modeldata['SubjectName'] = SubjectName
modeldata['TrialName'] = TrialName

# dump
outputfn = SessionLoc + TrialName + '.p'
pickle.dump(modeldata, open(outputfn, 'wb'))

