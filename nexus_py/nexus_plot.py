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
channel type is autodetected by looking into corresponding dict
variables always normalized
always plot PiG normal data
kinetics always plotted for one side only
kinematics always plotted for both sides (can add option later)
vars can be specified without leading 'Norm'+side (e.g. 'HipMomentX')

TODO:

trial selector return values for cancel?
EMG can be disconnected in some trials and not in others; annotation?
currently one figure per instance (can be overlay)
improve detection of disconnected EMG
documentation
add default y ranges for kine(ma)tics variables?

"""

from Tkinter import *
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
import glob


def strip_ws(str):
    """ Remove spaces from string """
    return str.replace(' ','')

class nexus_plotter():
    """ Create a plot of Nexus variables. Can overlay data from several trials. """

    def __init__(self, layout):
        """ Sets plot layout and other stuff. """
        
        # default parameters, if none specified on cmd line or config file
        self.emg_passband = None   # none for no filtering, or [f1,f2] for bandpass
        self.side = None   # will autodetect unless specified
        self.trialname = None
        
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
                # can add key/val pairs here (elif)
                if key.lower() == 'emg_passband':
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
        self.emg_normals_alpha = .8
        self.emg_alpha = .6
        self.emg_normals_color = 'pink'
        self.emg_ylabel = 'mV'
        # x label
        self.xlabel = ''
        self.fig = None

        self.vicon = None

    def get_eclipse_description(self, trialname):
        """ Get the Eclipse database description for the specified trial. Specify
        trialname with full path. """
        # remove c3d extension if present
        trialname = os.path.splitext(trialname)[0]
        if not os.path.isfile(trialname+'.c3d'):
            raise Exception('Cannot find c3d file for trial')
        enfname = trialname + '.Trial.enf'
        description = None
        if os.path.isfile(enfname):
            f = open(enfname, 'r')
            eclipselines = f.read().splitlines()
            f.close()
        else:
            return None
        for line in eclipselines:
            eqpos = line.find('=')
            if eqpos > 0:
                key = line[:eqpos]
                val = line[eqpos+1:]
                if key == 'DESCRIPTION':
                    description = val
        return description
       
    def trialselector(self):
        """ Let the user choose from processed trials in the trial directory. 
        Will also show the Eclipse description for each processed trial, if 
        available. """
        trialpath = self.get_nexus_path()
        if trialpath == '':
            error_exit('Cannot get Nexus path. Please open one trial to set the path.')
        # list of all processed trials
        proctrials = glob.glob(trialpath+'*.c3d')
        lp = len(proctrials)
        # ugly callback: sets list to a "signal" value and destroys the window
        def creator_callback(window, list):
            list.append(1)
            window.destroy()
        # trial selector
        master = Tk()
        Label(master, text="Choose trials for overlay plot:").grid(row=0, columnspan=2, pady=4)
        vars = []
        chosen = []
        for i,trialpath in enumerate(proctrials):
            vars.append(IntVar())
            # remove path and extension from full trial name
            trial =  os.path.basename(os.path.splitext(trialpath)[0])
            desc = self.get_eclipse_description(trialpath)
            Checkbutton(master, text=trial+4*" "+desc, variable=vars[i]).grid(row=i+1, columnspan=2, sticky=W)
        Button(master, text='Cancel', command=master.destroy).grid(row=lp+2, column=0, pady=4)
        Button(master, text='Create plot', command=lambda: creator_callback(master, chosen)).grid(row=lp+2, column=1, pady=4)
        print("chosen: ", chosen)        
        mainloop()
        if not chosen:
            return None
        else:
            chosen = []
            for i,trial in enumerate(proctrials):
                if vars[i].get():
                    chosen.append(trial)
            return chosen

    def get_nexus_path(self):
        if not self.vicon:
            self.vicon = ViconNexus.ViconNexus()
        trialname_ = self.vicon.GetTrialName()
        if not trialname_:
            return None
        else:
            return(trialname_[0])
            
    def detect_side(self):
        """ Detect the side of the loaded gait cycle. """
        vgc = nexus_getdata.gaitcycle(self.vicon)
        return vgc.detect_side(self.vicon)
        
                                                      
    def open_trial(self, nexusvars, trialpath=None, side=None):
        """ Read specified trial, or the one already opened in Nexus. """
        
        self.nexusvars = nexusvars
        if not self.vicon:
            self.vicon = ViconNexus.ViconNexus()
        # remove filename extension if present
        trialpath = os.path.splitext(trialpath)[0]
        if trialpath:
            self.vicon.OpenTrial(trialpath, 10)            
            # TODO: check errors
        subjectnames = self.vicon.GetSubjectNames()  
        if not subjectnames:
            error_exit('No subject')
        trialname_ = self.vicon.GetTrialName()
        if not trialname_:
            error_exit('No trial loaded')
        self.sessionpath = trialname_[0]
        self.trialname = trialname_[1]
        self.subjectname = subjectnames[0]
        
        # try to detect side (L/R) if not forced
        if not side:
            self.side = self.detect_side()
        else:
            self.side = side    
        
        # will read EMG/PiG data only if necessary
        self.pig = nexus_getdata.pig_outputs()
        self.emg = nexus_getdata.nexus_emg(mapping_changes=self.emg_mapping)
        read_emg = False
        read_pig = False
        self.emg_plot_chs = []
        self.emg_plot_pos = []
        self.pig_plot_vars = []
        self.pig_plot_pos = []
        for i, var in enumerate(self.nexusvars):
            if var == None:
                pass
            else:
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
            self.emg.read(self.vicon)
        if read_pig:
            self.pig.read(self.vicon, 'PiGLB', self.gcdpath)

    def set_fig_title(self, title):
        if self.fig:
            plt.figure(self.fig.number) 
            plt.suptitle(title, fontsize=12, fontweight="bold")

    def plot_trial(self, plotheightratios=None, maintitle=None, maintitleprefix='',
                 makepdf=False, pdftitlestr='Nexus_plot_', onesided_kinematics=False,
                 linestyle='-', emg_tracecolor='black'):
        """ Plot active trial (must call open_trial first). If a plot is already 
        active, the new trial will be overlaid on the previous one.
        Parameters:
        maintitle plot title; leave unspecified for automatic title (can also then
        supply maintitleprefix)
        """        

        if not self.trialname:
            raise Exception('No trial loaded')

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

        # automatic title
        if not maintitle:
            maintitle = maintitleprefix + self.trialname + ' ('+self.side+')'
        
        # x variable for kinematics / kinetics: 0,1...100
        tn = np.linspace(0, 100, 101)
        # for normal data: 0,2,4...100.
        tn_2 = np.array(range(0, 101, 2))
        
        if self.fig:
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
                    plt.plot(tn, self.pig.Vars[varname_r], self.tracecolor_r, linestyle=linestyle)
                    plt.plot(tn, self.pig.Vars[varname_l], self.tracecolor_l, linestyle=linestyle)
                else:
                    plt.plot(tn, self.pig.Vars[varname_full], tracecolor, linestyle=linestyle)
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
                    plt.plot(tn_emg, 1e3*self.emg.filter(emgdata[thisch], self.emg_passband), emg_tracecolor, alpha=self.emg_alpha)
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
        
        
    
    
    
    
    
