from __future__ import division, print_function

"""
Read and plot PiG output variables while Nexus is running, and trial has
been processed.
Works with Nexus 2.1.x

@author: jussi
"""

import sys
import numpy as np
import vicon_pig_makeplots  # custom plotting code
import vicon_pig_read_outputs
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
PIGvars=vicon.GetModelOutputNames(SubjectName)

# define kinematics vars of interest to read
KinematicsVars=['LHipAngles',
 'LKneeAngles',
 'LAbsAnkleAngle',
 'LAnkleAngles',
 'LPelvisAngles',
 'LFootProgressAngles',
 'RHipAngles',
 'RKneeAngles',
 'RAbsAnkleAngle',
 'RAnkleAngles',
 'RPelvisAngles',
 'RFootProgressAngles']

KineticsVars=['LHipMoment',
              'LKneeMoment',
              'LAnkleMoment',
              'LHipPower',
              'LKneePower',
              'LAnklePower',
              'RHipMoment',
              'RKneeMoment',
              'RAnkleMoment',
              'RHipPower',
              'RKneePower',
              'RAnklePower']
              
 # read all kinematics vars into dict and normalize into gait cycle 1
KinematicsAll = vicon_pig_read_outputs.ReadNormalizedPiGVars(vicon,KinematicsVars)              
KineticsAll = vicon_pig_read_outputs.ReadNormalizedPiGVars(vicon,KineticsVars)              

# moment variables have to be divided by 1000 - not sure why    
for Var in KineticsVars:
    if Var.find('Moment') > 0:
        KineticsAll[Var] /= 1000.
  
# create the plots
tn = np.linspace(0, 100, 101)  # x grid
vicon_pig_makeplots.KinematicsPlot(TrialName, tn, KinematicsAll)
vicon_pig_makeplots.KineticsPlot(TrialName, tn, KineticsAll)

plt.show()








