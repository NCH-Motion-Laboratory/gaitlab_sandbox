from __future__ import division, print_function

"""
Read and plot PiG output variables while Nexus is running, and trial has
been processed.
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

# list PIG model outputs
PIGvars=vicon.GetModelOutputNames('Roosa')


"""
Test extraction of kinetics variables.
Note that kinetics is only available for the side where forceplate contact
occurs. E.g. analyzing a trial with left foot forceplate contact will only
give (sensible) left side kinetics. Thus, we must know which foot had 
forceplate contact in the trial.

# gives tuple with 2 list elements
LHipMomT = vicon.GetModelOutput(SubjectName, 'LHipMoment')
# unpack gives nested list Moments: 3 lists of 370 elements
# Something has boolean values, not clear what
LHipMomentsL,Something = LHipMomT
LHipMoments = np.array(LHipMomentsL)
LHipX = LHipMoments[0][0:200]
"""

# figure out gait cycle
# frames where foot strikes occur (1-frame discrepancies with Nexus?)
LFStrike = vicon.GetEvents(SubjectName, "Left", "Foot Strike")[0]
RFStrike = vicon.GetEvents(SubjectName, "Right", "Foot Strike")[0]
# 2 strikes is one complete gait cycle, needed for analysis
lenLFS = len(LFStrike)
lenRFS = len(RFStrike)
if lenLFS and lenRFS < 2:
    raise Exception("Could not detect complete L/R gait cycle in trial")
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



# plot all kinematics vars
plt.figure(figsize=(14, 12))
Rcolor='lawngreen'
Lcolor='red'
plt.suptitle("Kinematics output\n" + TrialName + " (1st gait cycle)", fontsize=12, fontweight="bold")
plt.subplot(4, 3, 1)
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)
plot1 = plt.plot(tn, KinematicsAll['NormLPelvisAnglesX'], Lcolor, KinematicsAll['NormRPelvisAnglesX'], Rcolor)
plt.title('Pelvic tilt')
plt.xlabel('% of gait cycle')
plt.ylabel('Pst     ($^\circ$)      Ant')
plt.ylim(-20., 40.0)
plt.axhline(0, color='black')
# plt.legend(('Left', 'Right'), title="Context", fontsize=10, loc='lower right', bbox_to_anchor=(2.3, -5.1),
#          ncol=3, fancybox=True, shadow=True)

plt.subplot(4, 3, 2)
plot2 = plt.plot(tn, KinematicsAll['NormLPelvisAnglesY'], Lcolor, KinematicsAll['NormRPelvisAnglesY'], Rcolor)
plt.title('Pelvic obliquity')
plt.xlabel('% of gait cycle')
plt.ylabel('Dwn     ($^\circ$)      Up')
plt.ylim(-20., 40.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 3)
plot3 = plt.plot(tn, KinematicsAll['NormLPelvisAnglesZ'], Lcolor, KinematicsAll['NormRPelvisAnglesZ'], Rcolor)
plt.title('Pelvic rotation')
plt.xlabel('% of gait cycle')
plt.ylabel('Bak     ($^\circ$)      For')
plt.ylim(-30., 40.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 4)
plot4 = plt.plot(tn, KinematicsAll['NormLHipAnglesX'], Lcolor, KinematicsAll['NormRHipAnglesX'], Rcolor)
plt.title('Hip flexion')
plt.xlabel('% of gait cycle')
plt.ylabel('Ext     ($^\circ$)      Flex')
plt.ylim(-20., 50.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 5)
plot5 = plt.plot(tn, KinematicsAll['NormLHipAnglesY'], Lcolor, KinematicsAll['NormRHipAnglesY'], Rcolor)
plt.title('Hip adduction')
plt.xlabel('% of gait cycle')
plt.ylabel('Abd     ($^\circ$)      Add')
plt.ylim(-30., 30.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 6)
plot6 = plt.plot(tn, KinematicsAll['NormLHipAnglesZ'], Lcolor, KinematicsAll['NormRHipAnglesZ'], Rcolor)
plt.title('Hip rotation')
plt.xlabel('% of gait cycle')
plt.ylabel('Ext     ($^\circ$)      Int')
plt.ylim(-20., 30.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 7)
plot7 = plt.plot(tn, KinematicsAll['NormLKneeAnglesX'], Lcolor, KinematicsAll['NormRKneeAnglesX'], Rcolor)
plt.title('Knee flexion')
plt.xlabel('% of gait cycle')
plt.ylabel('Ext     ($^\circ$)      Flex')
plt.ylim(-15., 75.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 8)
plot8 = plt.plot(tn, KinematicsAll['NormLKneeAnglesY'], Lcolor, KinematicsAll['NormRKneeAnglesY'], Rcolor)
plt.title('Knee adduction')
plt.xlabel('% of gait cycle')
plt.ylabel('Val     ($^\circ$)      Var')
plt.ylim(-30., 30.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 9)
plot9 = plt.plot(tn, KinematicsAll['NormLKneeAnglesZ'], Lcolor, KinematicsAll['NormRKneeAnglesZ'], Rcolor)
plt.title('Knee rotation')
plt.xlabel('% of gait cycle')
plt.ylabel('Ext     ($^\circ$)      Int')
plt.ylim(-30., 30.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 10)
plot10 = plt.plot(tn, KinematicsAll['NormLAnkleAnglesX'], Lcolor, KinematicsAll['NormRAnkleAnglesX'], Rcolor)
plt.title('Ankle dorsi/plant')
plt.xlabel('% of gait cycle')
plt.ylabel('Pla     ($^\circ$)      Dor')
plt.ylim(-30., 30.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 11)
plot11 = plt.plot(tn, KinematicsAll['NormLFootProgressAnglesZ'], Lcolor, KinematicsAll['NormRFootProgressAnglesZ'], Rcolor)
plt.title('Foot progress angles')
plt.xlabel('% of gait cycle')
plt.ylabel('Ext     ($^\circ$)      Int')
plt.ylim(-30., 30.0)
plt.axhline(0, color='black')

plt.subplot(4, 3, 12)
plot11 = plt.plot(tn, KinematicsAll['NormLAnkleAnglesZ'], Lcolor, KinematicsAll['NormRAnkleAnglesZ'], Rcolor)
plt.title('Ankle rotation')
plt.xlabel('% of gait cycle')
plt.ylabel('Ext     ($^\circ$)      Int')
plt.ylim(-30., 30.0)
plt.axhline(0, color='black')
 
plt.show()










