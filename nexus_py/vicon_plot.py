# -*- coding: utf-8 -*-
"""

Generic Nexus plotter

params:
plot layout
channels to plot
main title leading string
create pdf or not
pdf name leading string

rules:
precede EMG channel name with X to autodetect side and plot corresponding variable
e.g. 'XHam'
channel type is autodetected by looking into corresponding dict
variables always normalized
always plot PiG normal data
kinetics always plotted for one side only
kinematics always plotted for both sides (can add option later)
vars can be specified without leading 'Norm'+side (e.g. 'HipMomentX')

TODO:
documentation


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

def nexus_plot(layout, plotvars, plotheightratios, maintitlestr, makepdf, pdftitlestr=None,
                onesided_kinematics=False, annotate_disconnected=True, annotate_reused=True):
    """ Call to create a plot of Nexus variables. """

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
        
    arglist = []
    if os.path.isfile(configfile):  # from config file
        f = open(configfile, 'r')
        arglist = f.read().splitlines()
        f.close()
    arglist += sys.argv[1:]  # add cmd line arguments    
    arglist = [strip_ws(x) for x in arglist]  # rm whitespace
    arglist = [x for x in arglist if x and x[0] != '#']  # rm comments
    
    emg_mapping = {}
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
                # assume it's EMG channel remapping
                emg_mapping[key] = val
            
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
    subjectnames = vicon.GetSubjectNames()
    if not subjectnames:
        error_exit('No subject')
    subjectname = subjectnames[0]
    trialname_ = vicon.GetTrialName()
    if not trialname_:
        error_exit('No trial loaded')
    sessionpath = trialname_[0]
    trialname = trialname_[1]
  
    # try to detect which foot hit the forceplate
    vgc = vicon_getdata.gaitcycle(vicon)
    if not side:
        side = vgc.detect_side(vicon)
    
    # plotting parameters
    # figure size
    totalfigsize = (14,12)
    # grid dimensions, vertical and horizontal
    gridv = layout[0]
    gridh = layout[1]
    # main title
    maintitle = maintitlestr + trialname + ' ('+side+')'
    # trace colors, right and left
    tracecolor_r = 'lawngreen'
    tracecolor_l = 'red'
    # label font size
    fsize_labels=10
    # for plotting kinematics / kinetics normal data
    normals_alpha = .3
    normals_color = 'gray'
    # emg normals
    emg_normals_alpha = .3
    emg_normals_color = 'red'
    emg_ylabel = 'mV'

    
    pig = vicon_getdata.pig_outputs()
    emg = vicon_getdata.vicon_emg(mapping_changes=emg_mapping)

    read_emg = False
    read_pig = False
    
    # check the variables to see what should be read
    emg_plot_chs = []
    emg_plot_pos = []
    pig_plot_vars = []
    pig_plot_pos = []
    for i, var in enumerate(plotvars):
        if var == None:
            pass
        else:
            if var[0] == 'X':
                var = side + var[1:]
            if emg.is_logical_channel(var):
                read_emg = True
                emg_plot_chs.append(var)
                emg_plot_pos.append(i)
            elif pig.is_pig_variable(var):
                read_pig = True
                pig_plot_vars.append(var)
                pig_plot_pos.append(i)
            else:
                error_exit('Unknown variable: ' + var)

    if read_emg:
        emg.read(vicon)
    if read_pig:
        pig.read(vicon, 'PiGLB', gcdpath)
    
    # output filename
    if makepdf:
        pdf_name = pdftitlestr + trialname + '.pdf'
     
    xlabel = ''
    
    if side == 'L':
        tracecolor = tracecolor_l
    else:
        tracecolor = tracecolor_r
    # EMG variables
    if emg_plot_chs:
        if side == 'L':
            tn_emg = emg.tn_emg_l
            emgdata = emg.logical_data_gc1l
            emg_yscale = emg.yscale_gc1l
        else:
            tn_emg = emg.tn_emg_r
            emgdata = emg.logical_data_gc1r
            emg_yscale = emg.yscale_gc1r
    
    # for kinematics / kinetics: 0,1...100
    tn = np.linspace(0, 100, 101)
    # for normal data: 0,2,4...100.
    tn_2 = np.array(range(0, 101, 2))
        
    fig = plt.figure(figsize=totalfigsize)
    gs = gridspec.GridSpec(gridv, gridh, height_ratios=plotheightratios)
    plt.suptitle(maintitle, fontsize=12, fontweight="bold")
    #plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)
    
    if pig_plot_vars:
        for k, var in enumerate(pig_plot_vars):
            plt.subplot(gs[pig_plot_pos[k]])
            varname_full = 'Norm'+side+var
            # whether to plot two-sided kinematics                
            if not pig.is_kinetic_var(var) and not onesided_kinematics:
                varname_r = 'Norm' + 'R' + var
                varname_l = 'Norm' + 'L' + var
                plt.plot(tn, pig.Vars[varname_r], tracecolor_r)
                plt.plot(tn, pig.Vars[varname_l], tracecolor_l)
            else:
                plt.plot(tn, pig.Vars[varname_full], tracecolor)
            nor = np.array(pig.normaldata(var))[:,0]
            nstd = np.array(pig.normaldata(var))[:,1]
            title = pig.description(var)
            ylabel = pig.ylabel(varname_full)
            plt.fill_between(tn_2, nor-nstd, nor+nstd, color=normals_color, alpha=normals_alpha)
            plt.title(title, fontsize=fsize_labels)
            plt.xlabel(xlabel,fontsize=fsize_labels)
            plt.ylabel(ylabel, fontsize=fsize_labels)
            #plt.ylim(kinematicsymin[k], kinematicsymax[k])
            plt.axhline(0, color='black')  # zero line
            plt.locator_params(axis = 'y', nbins = 6)  # reduce number of y tick marks
    
    if emg_plot_chs:
        for k, thisch in enumerate(emg_plot_chs):
            ax=plt.subplot(gs[emg_plot_pos[k]])
            if emgdata[thisch] == 'EMG_DISCONNECTED':
                ax.annotate('disconnected', xy=(50,0), ha="center", va="center")   
            elif emgdata[thisch] == 'EMG_REUSED':
                    ax.annotate('reused', xy=(50,0), ha="center", va="center")
            else:
                plt.plot(tn_emg, 1e3*emg.filter(emgdata[thisch], emg_passband), 'black')
            chlabel = emg.ch_labels[thisch]
            # plot EMG normal bars
            emgbar_ind = emg.ch_normals[thisch]
            for k in range(len(emgbar_ind)):
                inds = emgbar_ind[k]
                plt.axvspan(inds[0], inds[1], alpha=emg_normals_alpha, color=emg_normals_color)    
            plt.ylim(-1e3*emg_yscale[thisch], 1e3*emg_yscale[thisch])  # scale from logical channel
            plt.xlim(0,100)
            plt.title(chlabel, fontsize=10)
            plt.xlabel(xlabel, fontsize=fsize_labels)
            plt.ylabel(emg_ylabel, fontsize=fsize_labels)
            plt.locator_params(axis = 'y', nbins = 4)
    
    # fix plot spacing, restrict to below title
    gs.tight_layout(fig, h_pad=.5, w_pad=.5, rect=[0,0,1,.95])  
    plt.show()

    # create pdf
    if makepdf:
        with PdfPages(pdf_name) as pdf:
            print("Writing "+pdf_name)
            pdf.savefig(fig)
        
        
    
    
    
    
    
