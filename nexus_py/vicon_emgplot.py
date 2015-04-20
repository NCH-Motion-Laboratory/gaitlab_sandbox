# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 09:42:37 2015

EMG report: plot all L/R EMG channels (two columns)

"""


import matplotlib.pyplot as plt
import numpy as np
import vicon_getdata
from vicon_getdata import error_exit
import sys
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import os

# parse command line args (EMG electrode replacements)
emgrepl = {}
for arg in sys.argv[1:]:
    eqpos = arg.find('=')
    if eqpos < 2:
        error_exit('Invalid argument: arguments must be of form EMG1=EMG2,'+
        'which means that data of electrode EMG1 will be taken from electrode EMG2.')
    else:
        key = arg[:eqpos]
        val = arg[eqpos+1:]
        emgrepl[key] = val

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
    gcdpath = 'C:/Users/HUS20664877/Desktop/projects/llinna/nexus_py/normal.gcd'
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

# plotting parameters
# figure size
totalfigsize = (14,12)
# grid size
gridv = 7
gridh = 2
# relative heights of different plots
plotheightratios = [3,2,2,3,2,2,2,3]
# trace colors, right and left
rcolor='lawngreen'
lcolor='red'
# label font size
fsize_labels=10
# emg normals
emg_normals_alpha = .3
emg_normals_color = 'red'
# main title
maintitle = 'Kinetics-EMG plot for '+trialname+' ('+side+')'
emg_ylabel = 'mV'
# output filename
pdf_name = sessionpath + 'kinematics_emg_' + trialname + '.pdf'
# EMG channel naming dictionary
emg_labels_dict = {'Ham': 'Medial hamstrings',
                   'Rec': 'Rectus femoris',
                   'Gas': 'Gastrognemius',
                   'Glut': 'Gluteus',
                   'Vas': 'Vastus',
                   'Sol': 'Soleus',
                   'Tib': 'Tibialis',
                   'Per': 'Peroneus'}
# EMG channels to plot
emgchsplot = ['Ham','Rec','Tib','Glut','Vas','Per',
              'Rec','Ham','Gas','Glut','Sol','Gas']
# generate labels              
emgchlabels = [emg_labels_dict[x] for x in emgchsplot]
if side == 'R':
    emgchsplot = ['R'+str for str in emgchsplot]
else:
    emgchsplot = ['L'+str for str in emgchsplot]
# corresponding EMG channel positions on subplot grid
emgchpos = [3,4,5,6,7,8,12,13,14,16,17,19]
               
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

# sanity check for EMG replacement dict
if emgrepl:
    emg_legal = ['Per', 'Ham', 'Vas', 'Rec', 'Glut', 'Gas', 'Sol', 'Tib']
    emg_legal = ['R'+str for str in emg_legal]+['L'+str for str in emg_legal]
    for key in emgrepl.keys():
        if not key in emg_legal:
            error_exit('Cannot replace electrode '+key)


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
    for k in range(len(emgchsplot)):
        chnamepart = emgchsplot[k]
        chlabel = emgchlabels[k]
        # check replacement dict to see if data should actually be read
        # from some other channel 
        if chnamepart in emgrepl:
            replstr = ' (read from '+emgrepl[chnamepart]+')'
            chnamepart = emgrepl[chnamepart]            
        else:
            replstr = ''
        # translate to full channel name, e.g. 'LHam' -> 'LHam7'
        chs = emg.findchs(chnamepart)
        if len(chs) == 0:
            plt.close()
            error_exit('EMG channel matching name '+chnamepart+' not found in data')
        if len(chs) > 1:
            plt.close()
            error_exit('Found multiple EMG channels matching requested name: '+chnamepart)
        chname = chs[0]
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
        plt.title(chlabel+' '+side+replstr, fontsize=10)
        plt.xlabel(xlabel, fontsize=fsize_labels)
        plt.ylabel(emg_ylabel, fontsize=fsize_labels)
        plt.locator_params(axis = 'y', nbins = 4)

    # fix plot spacing, restrict to below title
    gs.tight_layout(fig, h_pad=.5, w_pad=.5, rect=[0,0,1,.95])        
    print("Writing "+pdf_name)
    pdf.savefig()
    plt.show()
    









