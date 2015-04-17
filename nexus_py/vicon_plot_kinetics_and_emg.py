# -*- coding: utf-8 -*-
"""
Make combined kinetics-EMG report (idea from Leuven)
Uses single trial of data from Vicon Nexus.
Save report as pdf.
@author: Jussi

plot layout:
hip flex/ext        knee flex/ext       ankle dorsi/plant
lham                lrec                ltib
lglut               lvas                lper
hip flex/ext mom    knee flex/ext       ankle dors/plan
lrec                lham                lgas
                    lglut               lsol     
                    lgas
hip power           knee power          ankle power

TODO:
update layout (new above)
EMG filtering (edge effects)
EMG labeling
move remaining plot definitions to parameters
verify (Polygon)
"""


import matplotlib.pyplot as plt
import numpy as np
import vicon_getdata
from vicon_getdata import error_exit
import sys
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import os


# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")
# PiG normal data
gcdpath = 'normal.gcd'
# if we're running from Nexus, try another place
if not os.path.isfile(gcdpath):
    gcdpath = 'C:/Users/Vicon123/Desktop/nexus_python/llinna/nexus_py/normal.gcd'
if not os.path.isfile(gcdpath):
    error_exit('Cannot find Plug-in Gait normal data (normal.gcd)')

import ViconNexus
# Python objects communicate directly with the Nexus application.
# Before using the vicon object, Nexus needs to be started and a subject loaded.
vicon = ViconNexus.ViconNexus()
subjectname = vicon.GetSubjectNames()[0]
sessionpath = vicon.GetTrialName()[0]
trialname = vicon.GetTrialName()[1]
if trialname == '':
    error_exit('No trial loaded')

pigvars = vicon.GetModelOutputNames(subjectname)

# try to detect which foot hit the forceplate
vgc = vicon_getdata.gaitcycle(vicon)
side = vgc.detect_side(vicon)
# or specify manually:
#side = 'R'

# plotting parameters
# figure size
totalfigsize = (14,12)
# grid size
gridv = 7
gridh = 3
# relative heights of different plots
plotheightratios = [3,2,2,3,2,2,3]
# trace colors, right and left
rcolor='lawngreen'
lcolor='red'
# label font size
fsize_labels=10
# for plotting kinematics / kinetics normal data
normals_alpha = .3
normals_color = 'gray'
# emg normals
emg_normals_alpha = .3
emg_normals_color = 'red'
# main title
maintitle = 'Kinetics-EMG plot for trial '+trialname+' ('+side+')'
emg_ylabel = 'mV'
# output filename
pdf_name = sessionpath + 'kinematics_emg_' + trialname + '.pdf'


# EMG channels to plot
emgchsplot = ['Ham','Rec','Gas','Glut','Vas','Sol','Rec','Ham','Tib',
              'Gas']
if side == 'R':
    emgchsplot = ['R'+str for str in emgchsplot]
else:
    emgchsplot = ['L'+str for str in emgchsplot]
# corresponding EMG channel positions on subplot grid
emgchpos = [3,4,5,6,7,8,12,13,14,16]
# can define more elaborate labels later, if needed
emgchlabels = emgchsplot
# EMG normal bars: expected ranges of normal EMG activation
# see emg_normal_bars.py
emgbar_inds = {'Gas': [[16,50]],
               'Glut': [[0,42],[96,100]],
               'Ham': [[0,2],[92,100]],
               'Per': [[4,54]],
               'Rec': [[0,14],[56,100]],
               'Sol': [[10,54]],
               'Tib': [[0,12],[56,100]],
               'Vas': [[0,24],[96,100]]}

     
# kinematics vars to plot
kinematicsvarsplot_ = ['HipAnglesX','KneeAnglesX','AnkleAnglesX']
# corresponding normal variables as specified in normal.gcd
kinematicsnormals = ['HipFlexExt','KneeFlexExt','DorsiPlanFlex']
# append 'Norm' + side to get the full variable name
kinematicsvarsplot = ['Norm'+side+str for str in kinematicsvarsplot_]
kinematicstitles = ['Hip flexion','Knee flexion','Ankle dorsi/plantar']
# y labels
kinematicslabels = ['Ext     ($^\circ$)      Flex',
                    'Ext     ($^\circ$)      Flex',
                    'Pla     ($^\circ$)      Dor']
# subplot positions
kinematicspos = [0,1,2]
# y scaling
kinematicsymin = [-20,-15,-30]
kinematicsymax = [50,75,30]

# kinetics channels to plot
kineticsvarsplot_ = ['HipMomentX','KneeMomentX','AnkleMomentX','HipPowerZ',
                     'KneePowerZ','AnklePowerZ']
# corresponding normal variables as specified in normal.gcd
kineticsnormals = ['HipFlexExtMoment','KneeFlexExtMoment','DorsiPlanFlexMoment',
                    'HipPower','KneePower','AnklePower']
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
kineticspos = [9,10,11,18,19,20]
xlabel = ''
                    
 # read data
pig = vicon_getdata.pig_outputs(vicon, 'PiGLB')
pig_normaldata = vicon_getdata.pig_normaldata(gcdpath)
emg = vicon_getdata.vicon_emg(vicon)

if side == 'L':
    tracecolor = lcolor
else:
    tracecolor = rcolor
# EMG variables
if side == 'L':
    gclen_emg = emg.lgc1len_s
    emgdata = emg.datagc1l
    yscale = emg.yscalegc1l
else:
    gclen_emg = emg.rgc1len_s
    emgdata = emg.datagc1r
    yscale = emg.yscalegc1r

# x grid from 0..100 with as many elements as EMG has samples
tn_emg = np.linspace(0, 100, gclen_emg)
# for kinematics / kinetics: 0,1...100
tn = np.linspace(0, 100, 101)
# for normal data: 0,2,4...100.
tn_2 = np.array(range(0, 101, 2))

with PdfPages(pdf_name) as pdf:
    
    fig = plt.figure(figsize=totalfigsize)
    gs = gridspec.GridSpec(gridv, gridh, height_ratios = plotheightratios)
    plt.suptitle(maintitle, fontsize=12, fontweight="bold")
    #plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)
    
    for k in range(len(kinematicsvarsplot)):
        plt.subplot(gs[kinematicspos[k]])
        plt.plot(tn, pig.Vars[kinematicsvarsplot[k]], tracecolor)
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
    
    for k in range(len(kineticsvarsplot)):
        plt.subplot(gs[kineticspos[k]])
        plt.plot(tn, pig.Vars[kineticsvarsplot[k]], tracecolor)
        nor = np.array(pig_normaldata[kineticsnormals[k]])[:,0]
        nstd = np.array(pig_normaldata[kineticsnormals[k]])[:,1]
        plt.fill_between(tn_2, nor-nstd, nor+nstd, color=normals_color, alpha=normals_alpha)
        plt.title(kineticstitles[k], fontsize=10)
        plt.xlabel(xlabel, fontsize=fsize_labels)
        plt.ylabel(kineticslabels[k], fontsize=fsize_labels)
        #plt.ylim(kineticsymin[k], kineticsymax[k])
        plt.axhline(0, color='black')  # zero line
        plt.locator_params(axis = 'y', nbins = 6)
    
    for k in range(len(emgchsplot)):
        chnamepart = emgchsplot[k]
        chlabel = emgchlabels[k]
        chs = emg.findchs(chnamepart)
        assert(len(chs) == 1), 'Cannot find channel '+chnamepart+' in data'
        chname = chs[0]  # full name, e.g. 'LHam7'
        # plot in mV
        plt.subplot(gs[emgchpos[k]])
        plt.plot(tn_emg, 1e3*emg.filter(emgdata[chname], [10,300]), 'black')
        # plot EMG normal bars    
        emgbar_ind = emgbar_inds[chnamepart[1:]]
        for k in range(len(emgbar_ind)):
            inds = emgbar_ind[k]
            plt.axvspan(inds[0], inds[1], alpha=emg_normals_alpha, color=emg_normals_color)    
        plt.ylim(-1e3*yscale[chname], 1e3*yscale[chname])
        plt.xlim(0,100)
        plt.title('EMG:'+chname, fontsize=10)
        plt.xlabel(xlabel, fontsize=fsize_labels)
        plt.ylabel(emg_ylabel, fontsize=fsize_labels)
        plt.locator_params(axis = 'y', nbins = 4)

    # fix plot spacing, restrict to below title
    gs.tight_layout(fig, h_pad=.5, w_pad=.5, rect=[0,0,1,.95])        
    print("Writing "+pdf_name)
    pdf.savefig()
    plt.show()
    





