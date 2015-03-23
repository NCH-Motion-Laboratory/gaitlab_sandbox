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


TODO: need to pick side, how?
"""

import matplotlib.pyplot as plt
import numpy as np
import vicon_getdata
import sys

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

# some parameters
# trace colors
rcolor='lawngreen'
lcolor='red'
# define side (L/R). This should be done automatically, or user-specified
# (maybe cmd line argument?)
# autodetection: look for forceplate output at time of gait events?
side = 'R'
# plot layout
subplotsh = 3
subplotsv = 7

# EMG channels to plot, and corresponding subplot positions
emgchsplot = ['LHam','LRec','LGas','LGlut','LVas','LSol','LRec','LHam','LTib',
              'LGas']
if side == 'R':
    emgchsplot = ['R'+str[1:] for str in emgchsplot]
emgchpos = [4,5,6,7,8,9,13,14,15,17]
# can define more elaborate labels later, if needed
emgchlabels = emgchsplot

# kinematics vars to plot
kinematicsvarsplot_ = ['HipAnglesX','KneeAnglesX','AnkleAnglesX']
# append 'Norm' + side to get the full variable name
kinematicsvarsplot = ['Norm'+side+str for str in kinematicsvarsplot_]
kinematicstitles = ['Hip flexion','Knee flexion','Angle dorsi/plantar']
# y labels
kinematicslabels = ['Ext     ($^\circ$)      Flex',
                    'Ext     ($^\circ$)      Flex',
                    'Pla     ($^\circ$)      Dor']
# subplot positions
kinematicspos = [1,2,3]
# y scaling
kinematicsymin = [-20,-15,-30]
kinematicsymax = [50,75,30]

# kinetics channels to plot
kineticsvarsplot_ = ['HipMomentX','KneeMomentX','AnkleMomentX','HipPowerZ',
                     'KneePowerZ','AnklePowerZ']
# append 'Norm' + side to get the full variable name
kineticsvarsplot = ['Norm'+side+str for str in kineticsvarsplot_]
kineticstitles = ['Hip flex/ext moment','Knee flex/ext moment',
                  'Ankle dors/plan moment','Hip power','Knee power',
                  'Ankle power']
# y labels
kineticslabels = ['Int flex    Nm/kg    Int ext','Int flex    Nm/kg    Int ext',
                  'Int dors    Nm/kg    Int plan','Abs    W/kg    Gen',
                  'Abs    W/kg    Gen','Abs    W/kg    Gen']
# subplot positions
kineticspos = [10,11,12,19,20,21]                  
xlabel = ''
                    
 # read data
kinematicspig = vicon_getdata.vicon_pig_outputs(vicon, 'PiGLBKinematics')
kineticspig = vicon_getdata.vicon_pig_outputs(vicon, 'PiGLBKinetics')
emg = vicon_getdata.vicon_emg(vicon)

# start plotting
if side == 'L':
    tracecolor = lcolor
else:
    tracecolor = rcolor
# EMG variables
if side == 'L':
    gclen_emg = emg.LGC1Len_s
    emgdata = emg.dataGC1L
    yscale = emg.yScaleGC1L
else:
    gclen_emg = emg.RGC1Len_s
    emgdata = emg.dataGC1R
    yscale = emg.yScaleGC1R

# make grid from 0..100 with as many elements as EMG has samples
tn_emg = np.linspace(0, 100, gclen_emg)
# for kinematics / kinetics
tn = np.linspace(0, 100, 101)

plt.figure(figsize=(14,12))
plt.suptitle("Kinematics-EMG plot\n" + trialname + " (1st gait cycle)", fontsize=12, fontweight="bold")
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)

for k in range(len(kinematicsvarsplot)):
    plt.subplot(subplotsv, subplotsh, kinematicspos[k])
    plt.plot(tn, kinematicspig.Vars[kinematicsvarsplot[k]], tracecolor)
    plt.title(kinematicstitles[k])
    plt.xlabel(xlabel)
    plt.ylabel(kinematicslabels[k])
    plt.ylim(kinematicsymin[k], kinematicsymax[k])
    plt.axhline(0, color='black')  # zero line

for k in range(len(kineticsvarsplot)):
    plt.subplot(subplotsv, subplotsh, kineticspos[k])
    plt.plot(tn, kineticspig.Vars[kineticsvarsplot[k]], tracecolor)
    plt.title(kineticstitles[k])
    plt.xlabel(xlabel)
    plt.ylabel(kineticslabels[k])
    #plt.ylim(kineticsymin[k], kineticsymax[k])
    plt.axhline(0, color='black')  # zero line

for k in range(len(emgchsplot)):
    chnamepart = emgchsplot[k]
    chlabel = emgchlabels[k]
    chs = emg.findchs(chnamepart)
    assert(len(chs) == 1)
    chname = chs[0]  # full name, e.g. 'LHam7'
    # plot in mV
    subplotpos = emgchpos[k]
    plt.subplot(subplotsv, subplotsh, subplotpos)
    plt.plot(tn_emg, 1e3*emg.filter(emgdata[chname], [10,300]), '#DC143C')
    plt.ylim(-1e3*yscale[chname], 1e3*yscale[chname])
    plt.title(chname, fontsize=10)
    plt.xlabel(xlabel)
    plt.ylabel('Voltage (mV)')
   
plt.show()







