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

improve detection of disconnected EMG
documentation
add default y ranges for kine(ma)tics variables?

"""

import matplotlib.pyplot as plt
import numpy as np
import nexus_getdata
from nexus_getdata import error_exit
import sys
# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")
import ViconNexus
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import os
import getpass


def strip_ws(str):
    """ Remove spaces from string """
    return str.replace(' ','')

class nexus_plotter():
    """ Create a plot of Nexus variables. Can overlay data from several trials. """

    def __init__(self, layout, plotvars):
        """ Sets plot layout and variables to be read. """
        
        # default parameters, if none specified on cmd line or config file
        self.emg_passband = None   # none for no filtering, or [f1,f2] for bandpass
        self.side = None   # will autodetect unless specified
        self.trialname = None
        self.plotvars = plotvars        
        
        # paths
        pathprefix = 'c:/users/' + getpass.getuser()
        desktop = pathprefix + '/Desktop'
        configfile = desktop + '/kinetics_emg_config.txt'
        
        # parse args
        arglist = []
        if os.path.isfile(configfile):  # from config file
            f = open(configfile, 'r')
            arglist = f.read().splitlines()
            f.close()
        arglist += sys.argv[1:]  # add cmd line arguments    
        arglist = [strip_ws(x) for x in arglist]  # rm whitespace
        arglist = [x for x in arglist if x and x[0] != '#']  # rm comments
        self.emg_mapping = {}
        for arg in arglist:
            eqpos = arg.find('=')
            if eqpos < 2:
                error_exit('Invalid argument!')
            else:
                key = arg[:eqpos]
                val = arg[eqpos+1:]
                if key.lower() == 'side':
                    self.side = val.upper()
                elif key.lower() == 'emg_passband':
                    try:
                        self.emg_passband = [float(x) for x in val.split(',')]   
                    except ValueError:
                        error_exit('Invalid EMG passband. Specify as emg_passband=f1,f2')
                else:
                    # assume it's EMG channel remapping
                    self.emg_mapping[key] = val
                
        # locate PiG normal data
        self.gcdpath = 'normal.gcd'
        # check user's desktop also
        if not os.path.isfile(self.gcdpath):
            self.gcdpath = desktop + '/projects/llinna/nexus_py/normal.gcd'
        if not os.path.isfile(self.gcdpath):
            error_exit('Cannot find Plug-in Gait normal data (normal.gcd)')
        
        # set default plotting parameters
        # figure size
        self.totalfigsize = (14,12)
        # grid dimensions, vertical and horizontal
        self.gridv = layout[0]
        self.gridh = layout[1]
        # trace colors, right and left
        self.tracecolor_r = 'lawngreen'
        self.tracecolor_l = 'red'
        # label font size
        self.fsize_labels=10
        # for plotting kinematics / kinetics normal data
        self.normals_alpha = .3
        self.normals_color = 'gray'
        # emg normals
        self.emg_normals_alpha = .3
        self.emg_normals_color = 'red'
        self.emg_ylabel = 'mV'
        # x label
        self.xlabel = ''
        self.fig = None
                                                      
    def open_trial(self, trialpath=None):
        """ Read specified trial, or the one already opened in Nexus. """

        # connect to Nexus
        vicon = ViconNexus.ViconNexus()

        if trialpath:
            vicon.OpenTrial(trialpath, 30)            
            # TODO: check errors
        
        subjectnames = vicon.GetSubjectNames()  
        if not subjectnames:
            error_exit('No subject')
        
        trialname_ = vicon.GetTrialName()
        if not trialname_:
            error_exit('No trial loaded')
        self.sessionpath = trialname_[0]
        self.trialname = trialname_[1]
        self.subjectname = subjectnames[0]
        
        # try to detect side (L/R)
        vgc = nexus_getdata.gaitcycle(vicon)
        if not self.side:
            self.side = vgc.detect_side(vicon)
    
        # will read EMG/PiG data only if necessary
        self.pig = nexus_getdata.pig_outputs()
        self.emg = nexus_getdata.nexus_emg(mapping_changes=self.emg_mapping)
        read_emg = False
        read_pig = False
        self.emg_plot_chs = []
        self.emg_plot_pos = []
        self.pig_plot_vars = []
        self.pig_plot_pos = []
        for i, var in enumerate(self.plotvars):
            if var == None:
                pass
            else:
                if var[0] == 'X':
                    var = self.side + var[1:]  # autodetect side
                if self.emg.is_logical_channel(var):
                    read_emg = True
                    self.emg_plot_chs.append(var)
                    self.emg_plot_pos.append(i)
                elif self.pig.is_pig_variable(var):
                    read_pig = True
                    self.pig_plot_vars.append(var)
                    self.pig_plot_pos.append(i)
                else:
                    error_exit('Unknown variable: ' + var)
        if read_emg:
            self.emg.read(vicon)
        if read_pig:
            self.pig.read(vicon, 'PiGLB', self.gcdpath)


    def plot_trial(self, plotheightratios=None, maintitlestr='Plot for ',
                 makepdf=False, pdftitlestr='Nexus_plot_', onesided_kinematics=False,
                 overlay=False):
        """ Plot active trial (must call open_trial first). If a plot is already 
        active and overlay=True, the new trial will be overlaid on the previous one."""        

        if not self.trialname:
            raise Exception('No trial loaded')

        if overlay and not self.fig:
            error_exit('Cannot overlay, no existing plot')

        # output filename
        if makepdf:
            pdf_name = self.sessionpath + pdftitlestr + self.trialname + '.pdf'
         
        if self.side == 'L':
            tracecolor = self.tracecolor_l
        else:
            tracecolor = self.tracecolor_r

        # if plot height ratios not set, set them all equal    
        if not plotheightratios:
            self.plotheightratios = [1] * self.gridv

        maintitle = maintitlestr + self.trialname + ' ('+self.side+')'
        
        # x variable for kinematics / kinetics: 0,1...100
        tn = np.linspace(0, 100, 101)
        # for normal data: 0,2,4...100.
        tn_2 = np.array(range(0, 101, 2))
        
        if self.fig and overlay:
            plt.figure(self.fig.number) 
        else:
            self.fig = plt.figure(figsize=self.totalfigsize)
            self.gs = gridspec.GridSpec(self.gridv, self.gridh, height_ratios=plotheightratios)

        plt.suptitle(maintitle, fontsize=12, fontweight="bold")
        
        if self.pig_plot_vars:
            for k, var in enumerate(self.pig_plot_vars):
                plt.subplot(self.gs[self.pig_plot_pos[k]])
                varname_full = 'Norm'+self.side+var
                # whether to plot two-sided kinematics                
                if not self.pig.is_kinetic_var(var) and not onesided_kinematics:
                    varname_r = 'Norm' + 'R' + var
                    varname_l = 'Norm' + 'L' + var
                    plt.plot(tn, self.pig.Vars[varname_r], self.tracecolor_r)
                    plt.plot(tn, self.pig.Vars[varname_l], self.tracecolor_l)
                else:
                    plt.plot(tn, self.pig.Vars[varname_full], tracecolor)
                nor = np.array(self.pig.normaldata(var))[:,0]
                nstd = np.array(self.pig.normaldata(var))[:,1]
                title = self.pig.description(var)
                ylabel = self.pig.ylabel(varname_full)
                plt.fill_between(tn_2, nor-nstd, nor+nstd, color=self.normals_color, alpha=self.normals_alpha)
                plt.title(title, fontsize=self.fsize_labels)
                plt.xlabel(self.xlabel,fontsize=self.fsize_labels)
                plt.ylabel(ylabel, fontsize=self.fsize_labels)
                #plt.ylim(kinematicsymin[k], kinematicsymax[k])
                plt.axhline(0, color='black')  # zero line
                plt.locator_params(axis = 'y', nbins = 6)  # reduce number of y tick marks
        
        if self.emg_plot_chs:
            for k, thisch in enumerate(self.emg_plot_chs):
                side_this = thisch[0]
                # choose EMG data normalized according to side
                if side_this == 'L':
                    tn_emg = self.emg.tn_emg_l
                    emgdata = self.emg.logical_data_gc1l
                    emg_yscale = self.emg.yscale_gc1l
                elif side_this == 'R':
                    tn_emg = self.emg.tn_emg_r
                    emgdata = self.emg.logical_data_gc1r
                    emg_yscale = self.emg.yscale_gc1r
                else:
                    error_exit('Unexpected EMG channel name: ', thisch)
                ax=plt.subplot(self.gs[self.emg_plot_pos[k]])
                if emgdata[thisch] == 'EMG_DISCONNECTED':
                    ax.annotate('disconnected', xy=(50,0), ha="center", va="center")   
                elif emgdata[thisch] == 'EMG_REUSED':
                        ax.annotate('reused', xy=(50,0), ha="center", va="center")
                else:
                    plt.plot(tn_emg, 1e3*self.emg.filter(emgdata[thisch], self.emg_passband), 'black')
                chlabel = self.emg.ch_labels[thisch]
                # plot EMG normal bars
                emgbar_ind = self.emg.ch_normals[thisch]
                for k in range(len(emgbar_ind)):
                    inds = emgbar_ind[k]
                    plt.axvspan(inds[0], inds[1], alpha=self.emg_normals_alpha, color=self.emg_normals_color)    
                plt.ylim(-1e3*emg_yscale[thisch], 1e3*emg_yscale[thisch])  # scale from logical channel
                plt.xlim(0,100)
                plt.title(chlabel, fontsize=10)
                plt.xlabel(self.xlabel, fontsize=self.fsize_labels)
                plt.ylabel(self.emg_ylabel, fontsize=self.fsize_labels)
                plt.locator_params(axis = 'y', nbins = 4)
        
        # fix plot spacing, restrict to below title
        self.gs.tight_layout(self.fig, h_pad=.5, w_pad=.5, rect=[0,0,1,.95])  
    
        #call plt.show() externally after all figures are complete - it blocks
        #plt.show()
    
        # create pdf
        if makepdf:
            with PdfPages(pdf_name) as pdf:
                print("Writing "+pdf_name)
                pdf.savefig(self.fig)
        
        
    
    
    
    
    
