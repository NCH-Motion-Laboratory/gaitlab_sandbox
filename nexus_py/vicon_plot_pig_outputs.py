# -*- coding: utf-8 -*-
"""
Check Plug-in Gait outputs from Nexus.
Creates online plots of kinematics and kinetics.

@author: Jussi
"""

import matplotlib.pyplot as plt
import numpy as np
import vicon_getdata
import sys
import matplotlib.gridspec as gridspec
from read_pig_normaldata import pig_normaldata

# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")

import ViconNexus
# Python objects communicate directly with the Nexus application.
# Before using the vicon object, Nexus needs to be started and a subject loaded.
vicon = ViconNexus.ViconNexus()
subjectname = vicon.GetSubjectNames()[0]
sessionpath = vicon.GetTrialName()[0]
trialname = vicon.GetTrialName()[1]
pigvars = vicon.GetModelOutputNames(subjectname)

# try to detect which foot hit the forceplate
vgc = vicon_getdata.vicon_gaitcycle(vicon)
side = vgc.detect_side(vicon)
# or specify manually:
#side = 'R'

# plotting parameters
# total figure size
totalfigsize = (14,12)
# trace colors, right and left
rcolor='lawngreen'
lcolor='red'
# label font size
fsize_labels=10
# for plotting kinematics / kinetics normal data
normals_alpha = .3
normals_color = 'gray'
xlabel='% of gait cycle'
     
# kinematics vars to plot (without 'Norm' + side)
kinematicsvarsplot_ = ['PelvisAnglesX',
                       'PelvisAnglesY',
                       'PelvisAnglesZ',
                       'HipAnglesX',
                       'HipAnglesY',
                       'HipAnglesZ',
                       'KneeAnglesX',
                       'KneeAnglesY',
                       'KneeAnglesZ',
                       'AnkleAnglesX',
                       'FootProgressAnglesZ',
                       'AnkleAnglesZ']
# append 'Norm' + side to get the full variable name                       
kinematicsvarsplot = ['Norm'+side+str for str in kinematicsvarsplot_]
# variable descriptions
kinematicstitles = ['Pelvic tilt',
                    'Pelvic obliquity',
                    'Pelvic rotation',
                    'Hip flexion',
                    'Hip adduction',
                    'Hip rotation',
                    'Knee flexion',
                    'Knee adduction',
                    'Knee rotation',
                    'Ankle dorsi/plant',
                    'Foot progress angles',
                    'Ankle rotation']
# y labels
kinematicslabels = ['Pst     ($^\circ$)      Ant',
                    'Dwn     ($^\circ$)      Up',
                    'Bak     ($^\circ$)      For',
                    'Ext     ($^\circ$)      Flex',
                    'Abd     ($^\circ$)      Add',
                    'Ext     ($^\circ$)      Int',
                    'Ext     ($^\circ$)      Flex',
                    'Val     ($^\circ$)      Var',
                    'Ext     ($^\circ$)      Int',
                    'Pla     ($^\circ$)      Dor',
                    'Ext     ($^\circ$)      Int',
                    'Ext     ($^\circ$)      Int']
# corresponding normal variables as specified in normal.gcd
# TOOD: check
kinematicsnormals = ['PelvicTilt',
                     'PelvicObliquity',
                     'PelvicRotation',
                     'HipFlexExt',
                     'HipAbAdduct',
                     'HipRotation',
                     'KneeFlexExt',
                     'KneeValgVar',
                     'KneeRotation',
                     'DorsiPlanFlex',
                     'FootProgression',
                     'FootRotation']
# subplot positions
kinematicspos = [1,2,3,4,5,6,7,8,9,10,11,12]
# plot y scaling: min and max values for each var
kinematicsymin = [-20,-20,-30,-20,-30,-20,-15,-30,-30,-30,-30,-30]
kinematicsymax = [40,40,40,50,30,30,75,30,30,30,30,30]


# kinetics vars to plot
kineticsvarsplot_ = ['HipMomentX',
                     'HipMomentY',
                     'HipMomentZ',
                     'HipPowerZ',
                     'KneeMomentX',
                     'KneeMomentY',
                     'KneeMomentZ',
                     'KneePowerZ',
                     'AnkleMomentX',
                     'AnklePowerZ']
# append 'Norm' + side to get the full variable name
kineticsvarsplot = ['Norm'+side+str for str in kineticsvarsplot_]
# var descriptions
kineticstitles = ['Hip flex/ext moment',
                  'Hip ab/add moment',
                  'Hip rotation moment',
                  'Hip power',
                  'Knee flex/ext moment',
                  'Knee ab/add moment',
                  'Knee rotation moment',
                  'Knee power',
                  'Ankle dors/plan moment',
                  'Ankle power']
# corresponding normal variables as specified in normal.gcd
kineticsnormals = ['HipFlexExtMoment',
                   'HipAbAdductMoment',
                   'HipRotationMoment',
                   'HipPower',
                   'KneeFlexExtMoment',
                   'KneeValgVarMoment',
                   'KneeRotationMoment',
                   'KneePower',
                   'DorsiPlanFlexMoment',
                   'AnklePower']
# y labels
kineticslabels = ['Int flex    Nm/kg    Int ext',
                  'Int add    Nm/kg    Int abd',
                  'Int flex    Nm/kg    Int ext',
                  'Abs    W/kg    Gen',
                  'Int flex    Nm/kg    Int ext',
                  'Int var    Nm/kg    Int valg',
                  'Int flex    Nm/kg    Int ext',
                  'Abs    W/kg    Gen',
                  'Int dors    Nm/kg    Int plan',
                  'Abs    W/kg    Gen']
# subplot positions
kineticspos = [1,2,3,4,5,6,7,8,9,12]

 # read data
kinematicspig = vicon_getdata.vicon_pig_outputs(vicon, 'PiGLBKinematics')
kineticspig = vicon_getdata.vicon_pig_outputs(vicon, 'PiGLBKinetics')

# default trace color
if side == 'L':
    tracecolor = lcolor
else:
    tracecolor = rcolor

# x axis for kinematics / kinetics: 0,1...100
tn = np.linspace(0, 100, 101)
# for normal data: 0,2,4...100.
tn_2 = np.array(range(0, 101, 2))
    

#plt.suptitle(maintitle, fontsize=12, fontweight="bold")
#plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)

# kinematics plot, both L and R
plt.figure(figsize=totalfigsize)
for k in range(len(kinematicsvarsplot)):
    plt.subplot(4, 3, kinematicspos[k])
    varL='Norm'+L+kinematicsvarsplot[k]
    varR='Norm'+R+kinematicsvarsplot[k]
    plt.plot(tn, kinematicspig.Vars[varL], lcolor, kinematicspig.Vars[varR], rcolor)
    # get normal data and std
    nor = np.array(pig_normaldata[kinematicsnormals[k]])[:,0]
    nstd = np.array(pig_normaldata[kinematicsnormals[k]])[:,1]
    plt.fill_between(tn_2, nor-nstd, nor+nstd, color=normals_color, alpha=normals_alpha)
    plt.title(kinematicstitles[k], fontsize=fsize_labels)
    plt.xlabel(xlabel,fontsize=fsize_labels)
    plt.ylabel(kinematicslabels[k], fontsize=fsize_labels)
    plt.ylim(kinematicsymin[k], kinematicsymax[k])
    plt.axhline(0, color='black')  # zero line
    plt.locator_params(axis = 'y', nbins = 6)  # reduce number of y tick marks

# kinetics plot
plt.figure(figsize=totalfigsize)
for k in range(len(kineticsvarsplot)):
    plt.subplot(4, 3, kineticspos[k]])
    plt.plot(tn, kineticspig.Vars[kineticsvarsplot[k]], tracecolor)
    nor = np.array(pig_normaldata[kineticsnormals[k]])[:,0]
    nstd = np.array(pig_normaldata[kineticsnormals[k]])[:,1]
    plt.fill_between(tn_2, nor-nstd, nor+nstd, color=normals_color, alpha=normals_alpha)
    plt.title(kineticstitles[k], fontsize=10)
    plt.xlabel(xlabel, fontsize=fsize_labels)
    plt.ylabel(kineticslabels[k], fontsize=fsize_labels)
    #plt.ylim(kineticsymin[k], kineticsymax[k])
    plt.axhline(0, color='black')  # zero line
    plt.locator_params(axis = 'y', nbins = 6)

plt.show()
    





