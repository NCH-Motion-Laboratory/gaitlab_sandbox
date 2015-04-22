# -*- coding: utf-8 -*-
"""
Make EMG report and save as pdf. Can be run from Vicon Nexus.

@author: Jussi


TODO:

check filtering (order?)
fix EMG scaling in getdata (median/DC)?
verify
"""

import matplotlib.pyplot as plt
import numpy as np
import vicon_getdata
from vicon_getdata import error_exit
import sys
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import os
import getpass


# default parameters, if none specified on cmd line or config file
emg_passband = None   # none for no filtering, or [f1,f2] for bandpass
side = None   # will autodetect unless specified

# paths
pathprefix = 'c:/users/'+getpass.getuser()
desktop = pathprefix + '/Desktop'
configfile = desktop + '/kinetics_emg_config.txt'

# parse args
def strip_ws(str):
    return str.replace(' ','')
    
if os.path.isfile(configfile):  # from config file
    f = open(configfile, 'r')
    arglist = f.read().splitlines()
    f.close()
arglist += sys.argv[1:]  # add cmd line arguments    
arglist = [strip_ws(x) for x in arglist]  # rm whitespace
arglist = [x for x in arglist if x and x[0] != '#']  # rm comments

emgrepl = {}
for arg in arglist:
    eqpos = arg.find('=')
    if eqpos < 2:
        error_exit('Invalid argument!')
    else:
        key = arg[:eqpos]
        val = arg[eqpos+1:]
        if key.lower() == 'side':
            side = val.upper()
        elif key.lower() == 'emg_passband':
            try:
                emg_passband = [float(x) for x in val.split(',')]   
            except ValueError:
                error_exit('Invalid EMG passband. Specify as emg_passband=f1,f2')
        else:
            emgrepl[key] = val
        
# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")
# PiG normal data
gcdpath = 'normal.gcd'
# check user's desktop also
if not os.path.isfile(gcdpath):
    gcdpath = desktop + '/projects/llinna/nexus_py/normal.gcd'
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
if not side:
    side = vgc.detect_side(vicon)
# or specify manually:
#side = 'R'

# plotting parameters
# figure size
totalfigsize = (14,12)
# grid size
gridv = 8
gridh = 2
# main title
maintitle = 'EMG plot for '+trialname+' ('+side+')'
# relative heights of different plots
plotheightratios = [2] * 8
# trace colors, right and left
rcolor='lawngreen'
lcolor='red'
# label font size
fsize_labels=10
# for plotting kinematics / kinetics normal data
normals_alpha = .3
normals_color = 'gray'
xlabel = ''

# read emg
emg = vicon_getdata.vicon_emg(vicon)
# emg normals
emg_normals_alpha = .3
emg_normals_color = 'red'
emg_ylabel = 'mV'
# output filename
pdf_name = sessionpath + 'emg_' + trialname + '.pdf'
# EMG channels to plot
emgchsplot = ['RGlut','LGlut',
              'RHam','LHam',
              'RRec','LRec',
              'RVas','LVas',
              'RTibA','LTibA',
              'RPer','LPer',
              'RGas','LGas',
              'RSol','LSol']
              
# generate labels              
emgchlabels = [emg.label(x) for x in emgchsplot]
# corresponding EMG channel positions on subplot grid
emgchpos = range(16)
# EMG normal bars: expected ranges of normal EMG activation
# see emg_normal_bars.py
emg_normaldata = emg.normaldata()
emg_legal = emg.legal()

# sanity check for EMG replacement dict
if emgrepl:
    for key in emgrepl.keys():
        if not key in emg_legal:
            error_exit('Cannot replace electrode '+key)
     
# for kinematics / kinetics: 0,1...100
tn = np.linspace(0, 100, 101)
# for normal data: 0,2,4...100.
tn_2 = np.array(range(0, 101, 2))

with PdfPages(pdf_name) as pdf:

    fig = plt.figure(figsize=totalfigsize)
    gs = gridspec.GridSpec(gridv, gridh, height_ratios = plotheightratios)
    plt.suptitle(maintitle, fontsize=12, fontweight="bold")
    #plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)
    for k in range(len(emgchsplot)):
        chnamepart = emgchsplot[k]
        side_this = chnamepart[0]
        if side_this == 'L':
            gclen_emg = emg.lgc1len_s
            emgdata = emg.datagc1l
            yscale = emg.yscalegc1l
        else:
            gclen_emg = emg.rgc1len_s
            emgdata = emg.datagc1r
            yscale = emg.yscalegc1r
        # x grid from 0..100 with as many elements as EMG has samples
        tn_emg = np.linspace(0, 100, gclen_emg)
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
        if not emg.disconnected[chname]:
            plt.plot(tn_emg, 1e3*emg.filter(emgdata[chname], emg_passband), 'black', alpha=.7)
        # plot EMG normal bars    
        emgbar_ind = emg_normaldata[chnamepart[1:]]
        for k in range(len(emgbar_ind)):
            inds = emgbar_ind[k]
            plt.axvspan(inds[0], inds[1], alpha=emg_normals_alpha, color=emg_normals_color)    
        plt.ylim(-1e3*yscale[chname], 1e3*yscale[chname])
        plt.xlim(0,100)
        plt.title(chlabel+' '+side_this+replstr, fontsize=10)
        plt.xlabel(xlabel, fontsize=fsize_labels)
        plt.ylabel(emg_ylabel, fontsize=fsize_labels)
        plt.locator_params(axis = 'y', nbins = 4)
    # fix plot spacing, restrict to below title
    gs.tight_layout(fig, h_pad=.5, w_pad=.5, rect=[0,0,1,.95])        
    print("Writing "+pdf_name)
    pdf.savefig()
    plt.show()
    





