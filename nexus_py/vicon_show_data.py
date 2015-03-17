from __future__ import division, print_function

"""
Read and plot PiG output variables while Nexus is running, and trial has
been processed.
Works with Nexus 2.1.x

@author: jussi
"""

import sys
import numpy as np
import vicon_makeplots  # custom plotting code
import vicon_getdata


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
KinematicsPiG = vicon_getdata.vicon_pig_outputs(vicon, KinematicsVars)
KineticsPiG = vicon_getdata.vicon_pig_outputs(vicon, KineticsVars)
EMG = vicon_getdata.vicon_emg(vicon)
tn = np.linspace(0, 100, 101)  # x grid
vicon_makeplots.KinematicsPlot(TrialName, tn, KinematicsPiG.Vars)
vicon_makeplots.EMGPlot(EMG)


"""
tn = np.linspace(0, 100, 101)  # x grid
vicon_pig_makeplots.KinematicsPlot(TrialName, tn, KinematicsAll)
vicon_pig_makeplots.KineticsPlot(TrialName, tn, KineticsAll)
vemg = vicon_emg(vicon)
vemg.plotall()

plt.show()
"""








