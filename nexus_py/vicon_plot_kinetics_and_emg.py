# -*- coding: utf-8 -*-
"""
Make combined kinetics-EMG plot (idea from Leuven)
Uses single trial of data from Vicon Nexus.
Save as pdf.
@author: Jussi

plot layout:
hip flex/ext        knee flex/ext       ankle dorsi/plant
lham                lrec                lgas
lglut               lvas                lsol
hip flex/ext mom    knee flex/ext       ankle dors/plan
lrec                lham                ltib
                    lgas
hip power           knee power          ankle power

"""

import matplotlib.pyplot as plt
import numpy as np

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



