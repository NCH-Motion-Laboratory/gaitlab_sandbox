from __future__ import division, print_function

"""
Read and plot PiG output variables while Nexus is running, and trial has
been processed.
Works with Nexus 2.1.x

@author: jussi
"""

import sys
import numpy as np
import vicon_pig_makeplots

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

# list PIG model outputs
PIGvars=vicon.GetModelOutputNames('Roosa')

"""
Note that kinetics is only available for the side where forceplate contact
occurs. E.g. analyzing a trial with left foot forceplate contact will only
give (sensible) left side kinetics. Thus, we must know which foot had 
forceplate contact in the trial. (??)
"""

# figure out gait cycle
# frames where foot strikes occur (1-frame discrepancies with Nexus?)
LFStrike = vicon.GetEvents(SubjectName, "Left", "Foot Strike")[0]
RFStrike = vicon.GetEvents(SubjectName, "Right", "Foot Strike")[0]
# 2 strikes is one complete gait cycle, needed for analysis
lenLFS = len(LFStrike)
lenRFS = len(RFStrike)
if lenLFS and lenRFS < 2:
    raise Exception("Could not detect complete L/R gait cycles")
# extract times for 1st gait cycles, L and R
LGC1Start=min(LFStrike[0:2])
LGC1End=max(LFStrike[0:2])
LGC1Len=LGC1End-LGC1Start
RGC1Start=min(RFStrike[0:2])
RGC1End=max(RFStrike[0:2])
RGC1Len=RGC1End-RGC1Start

# for interpolation variables from gait cycle grid to normalized grid (0...100%)
tn = np.linspace(0, 100, 101)
LGC1t = np.linspace(0, 100, LGC1Len)
RGC1t = np.linspace(0, 100, RGC1Len)

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
KinematicsAll = {}
for Var in KinematicsVars:
    # not sure what the BoolVals are, discard for now
    NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
    KinematicsAll[Var] = np.array(NumVals)
    # pick non-normalized X,Y,Z components into separate vars
    KinematicsAll[Var+'X'] = KinematicsAll[Var][0,:]
    KinematicsAll[Var+'Y'] = KinematicsAll[Var][1,:]
    KinematicsAll[Var+'Z'] = KinematicsAll[Var][2,:]
    # normalize vars to gait cycle 1
    if Var[0] == 'R':  # right side variable
        GC1t = RGC1t
        tStart = RGC1Start
        tEnd = RGC1End
    else:  # left side variable
        GC1t = LGC1t
        tStart = LGC1Start
        tEnd = LGC1End
    # pick per-frame data for gait cycle 1
    VarGC1=KinematicsAll[Var][:,tStart:tEnd]
    # interpolate all three components to gait cycle
    KinematicsAll['Norm'+Var+'X'] = np.interp(tn, GC1t, VarGC1[0,:])
    KinematicsAll['Norm'+Var+'Y'] = np.interp(tn, GC1t, VarGC1[1,:])
    KinematicsAll['Norm'+Var+'Z'] = np.interp(tn, GC1t, VarGC1[2,:])

# kinetics vars
# TODO: divide moments variables by 1000
KineticsAll = {}
for Var in KineticsVars:
    # not sure what the BoolVals are, discard for now
    NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
    KineticsAll[Var] = np.array(NumVals)
    # pick non-normalized X,Y,Z components into separate vars
    KineticsAll[Var+'X'] = KineticsAll[Var][0,:]
    KineticsAll[Var+'Y'] = KineticsAll[Var][1,:]
    KineticsAll[Var+'Z'] = KineticsAll[Var][2,:]
    # normalize vars to gait cycle 1
    if Var[0] == 'R':  # right side variable
        GC1t = RGC1t
        tStart = RGC1Start
        tEnd = RGC1End
    else:  # left side variable
        GC1t = LGC1t
        tStart = LGC1Start
        tEnd = LGC1End
    # pick per-frame data for gait cycle 1
    VarGC1=KineticsAll[Var][:,tStart:tEnd]
    # interpolate all three components to gait cycle
    KineticsAll['Norm'+Var+'X'] = np.interp(tn, GC1t, VarGC1[0,:])
    KineticsAll['Norm'+Var+'Y'] = np.interp(tn, GC1t, VarGC1[1,:])
    KineticsAll['Norm'+Var+'Z'] = np.interp(tn, GC1t, VarGC1[2,:])

# plot
vicon_pig_makeplots.KinematicsPlot(TrialName,tn,KinematicsAll)










