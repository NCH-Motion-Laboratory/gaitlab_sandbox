# -*- coding: utf-8 -*-
"""

Gaitplotter: plot gait data using matplotlib.


Rules:
-channel type is autodetected by looking into the known names
-can specify channel as 'None' to leave corresponding subplot empty
-can specify channel as 'modellegend' or 'emglegend' to get a legend on a particular subplot
(useful for overlay plots)
-variables always normalized to gait cycle
-always plot model normal data if available
-kinetics always plotted for one side only
-vars are specified without leading 'Norm'+side prefix (e.g. 'HipMomentX'
 instead of 'NormRHipMomentX'; side is either autodetected or manually forced


NEXT:
-adapt to new classes WIP


TODO:

tests
documentation
add default y ranges for kine(ma)tics variables?
"""


from Tkinter import *
import tkFileDialog
import matplotlib.pyplot as plt
import numpy as np
import gait_getdata
from gait_getdata import error_exit, messagebox
import gait_config
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
import btk



class gaitplotter():
    """ Create a plot of Nexus variables. Can overlay data from several trials. """

    def __init__(self, layout):
        # set paths
        pathprefix = 'c:/users/' + getpass.getuser()
        self.desktop = pathprefix + '/Desktop'
        self.appdir = self.desktop + '/NexusPlotter'
        
        # read .ini file if available
        self.cfg = gait_config.Config(self.appdir)
        config_ok, msg = self.cfg.check()
        if not config_ok:
            error_exit('Error in configuration file, please fix or delete: ', self.configfile)

        self.emg_passband = [0,0]
        self.emg_passband[0] = self.cfg.getval('emg_highpass')
        self.emg_passband[1] = self.cfg.getval('emg_lowpass')
        self.emg_apply_filter = self.cfg.getval('emg_apply_filter')
        self.emg_auto_off = self.cfg.getval('emg_auto_off')
        self.pig_normaldata_path = self.cfg.getval('pig_normaldata_path')
        self.emg_names = gait_getdata.emg(None).ch_names
        self.emg_names.sort()
        self.emg_manual_enable={}
        for ch in self.emg_names:
            self.emg_manual_enable[ch] = self.cfg.emg_enabled(ch)

        # muscle length normal data - not yet used
        self.musclelen_normaldata_path = None

        # can set layout=None, if no plots are intended
        if not layout:
            return

        # (currently) non-configurable stuff
        # figure size
        #self.totalfigsize = (8.48*1.2,12*1.2) # a4
        self.totalfigsize = (14,12)
        # grid dimensions, vertical and horizontal
        self.gridv = layout[0]
        self.gridh = layout[1]
        # trace colors, right and left
        self.tracecolor_r = 'lawngreen'
        self.tracecolor_l = 'red'
        # relative length of toe-off arrow (multiples of plot y height)
        self.toeoff_rel_len = .15
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
        self.annotate_disconnected = True
        self.add_toeoff_markers = True
        self.model_legendpos = None
        self.emg_legendpos = None
        # used to collect trial names and styles for legend
        self.modelartists = []
        self.emgartists = []
        self.legendnames = []
        # x label
        self.xlabel = ''
        self.fig = None
        # these will be set by open_trial()
        self.side = None
        self.gc = None
        self.trial = None
        # TODO: put in config?
        self.emg_mapping = {}
        
    def configwindow(self):
        """ Open a window for configuring NexusPlotter """
        self.cfg.window()
        
    def get_emg_filter_description(self):
        """ Returns a string describing the filter applied to the EMG data """
        if not self.emg_apply_filter:
            return "No EMG filtering"
        elif self.emg_passband[0] == 0:
            return "EMG lowpass " + str(self.emg_passband[1]) + ' Hz'
        else:
            return "EMG bandpass " + str(self.emg_passband[0]) + ' ... ' + str(self.emg_passband[1]) + ' Hz'

    def nexus_trialselector(self):
        """ Let the user choose from processed trials in the trial directory. 
        Will also show the Eclipse description for each processed trial, if 
        available. Tk checkbox dialog. """
        trialpath = self.get_nexus_path()
        if trialpath == '':
            error_exit('Cannot get Nexus path. Please make sure Nexus is running, and open a trial to set the path.')
        # list of all processed trials
        proctrials = glob.glob(trialpath+'*.c3d')
        lp = len(proctrials)
        # ugly callback: sets list to a "semaphor" value and destroys the window
        def creator_callback(window, list):
            list.append(1)
            window.destroy()
        # create trial selector
        master = Tk()
        Label(master, text="Choose trials for overlay plot:").grid(row=0, columnspan=2, pady=4)
        vars = []
        chosen = []
        for i,trialpath in enumerate(proctrials):
            vars.append(IntVar())
            # remove path and extension from full trial name
            trial =  os.path.basename(os.path.splitext(trialpath)[0])
            desc = gait_getdata.get_eclipse_description(trialpath)
            Checkbutton(master, text=trial+4*" "+desc, variable=vars[i]).grid(row=i+1, columnspan=2, sticky=W)
        Button(master, text='Cancel', command=master.destroy).grid(row=lp+2, column=0, pady=4)
        Button(master, text='Create plot', command=lambda: creator_callback(master, chosen)).grid(row=lp+2, column=1, pady=4)
        mainloop()  # Tk
        if not chosen:  # Cancel was pressed
            return None
        else:
            # go through checkbox variables, add selected trial names to list
            chosen = []
            for i,trial in enumerate(proctrials):
                if vars[i].get():
                    chosen.append(trial)
            return chosen
    
    class c3d_trialselector():
        """ Presents file selector window for choosing c3d trials. After user
        presses 'Create', selected trials are stored in the 'chosen' variable."""
    
        def create(self):
            self.master.destroy()
            self.chosen = [x for x in self.chosen if x]  # rm 'None' entries
            
        def cancel(self):
            self.chosen = []
            self.master.destroy()
            
        def delete_trial(self, ntrial):
            self.tributtons[ntrial].grid_remove()
            self.trilabels[ntrial].grid_remove()
            self.chosen[ntrial] = None
            self.ntrials -= 1
            if self.ntrials < self.MAX_TRIALS:
                self.loadb.config(state='normal')
    
        def load_trial(self):
            nthis = len(self.chosen)  # list index (includes deleted trials)
            nrow = self.ntrials + 1
            trialpath = tkFileDialog.askopenfilename(**self.options)
            if os.path.isfile(trialpath):
                desc = gait_getdata.get_eclipse_description(trialpath)
                trial =  os.path.basename(os.path.splitext(trialpath)[0])
                trialstr = trial+4*' '+desc
                la = Label(self.master, text=trialstr)
                la.grid(row=nrow, column=0, columnspan=2, sticky=W)
                self.trilabels.append(la)
                bu = Button(self.master, text='Delete', command=lambda: self.delete_trial(nthis))
                bu.grid(row=nrow, column=2)
                self.tributtons.append(bu)
                self.chosen.append(trialpath.encode())  # Tk returns UTF-8 names -> ASCII
                self.ntrials += 1                
                if self.ntrials == self.MAX_TRIALS:
                    self.loadb.config(state='disabled')
    
        def __init__(self, max_trials=4, initialdir='C:\\'):
            self.chosen = []
            self.trilabels = []
            self.tributtons = []
            self.master = Tk()
            self.ntrials = 0
            self.MAX_TRIALS = max_trials
            self.options = {}
            self.options['defaultextension'] = '.c3d'
            self.options['filetypes'] = [('C3D files', '.c3d'), ('All files', '.*')]
            self.options['parent'] = self.master
            self.options['title'] = 'Load a trial (c3d file):'
            self.options['initialdir'] = initialdir
            bottom = self.MAX_TRIALS + 1
            Label(self.master, text="Choose trials for overlay plot:").grid(row=0, columnspan=2, pady=4)
            Button(self.master, text='Cancel', command=self.cancel).grid(row=bottom, column=0, pady=4)
            self.loadb = Button(self.master, text='Load trial', command=self.load_trial)
            self.loadb.grid(row=bottom, column=1, pady=4)
            Button(self.master, text='Create plot', command=self.create).grid(row=bottom, column=2, pady=4)
            mainloop()  # Tk

    def get_nexus_path(self):
        if not self.vicon:
            self.vicon = ViconNexus.ViconNexus()
        trialname_ = self.vicon.GetTrialName()
        if not trialname_:
            return None
        else:
            return(trialname_[0])

    def open_nexus_trial(self):
        """ Open trial from Nexus. """
        if not gait_getdata.nexus_pid():
            error_exit('Cannot get Nexus PID, Nexus not running?')
        vicon = gait_getdata.viconnexus()
        self.trial = gait_getdata.trial(vicon, pig_normaldata_path=self.pig_normaldata_path)
        
    def open_c3d_trial(self, trialpath):
        """ Open a c3d trial. """
        if not os.path.isfile(trialpath):
            error_exit('Cannot find trial: '+trialpath)
        self.trial = gait_getdata.trial(trialpath, pig_normaldata_path=self.pig_normaldata_path)
        
    def read_trial(self, vars):
        """ Read requested trial variables / legend parameters etc. """
        self.vars = vars
        read_emg = False
        read_pig = False
        read_musclelen = False
        self.emg_plot_chs = []
        self.emg_plot_pos = []
        self.model_plot_vars = []
        self.model_plot_pos = []
        for i, var in enumerate(self.vars):
            if var == None:  # indicates empty subplot
                pass
            elif var == 'modellegend':   # place legend on this subplot
                self.model_legendpos = i
            elif var == 'emglegend':
                self.emg_legendpos = i
            else:
                if self.trial.emg.is_logical_channel(var):
                    read_emg = True
                    self.emg_plot_chs.append(var)
                    self.emg_plot_pos.append(i)
                elif self.trial.model.is_pig_lowerbody_variable(var):
                    read_pig = True
                    self.model_plot_vars.append(var)
                    self.model_plot_pos.append(i)
                elif self.trial.model.is_musclelen_variable(var):
                    read_musclelen = True
                    self.model_plot_vars.append(var)
                    self.model_plot_pos.append(i)
                else:
                    error_exit('Unknown variable: ' + var)
        if read_emg:
            self.trial.emg.read()
        if read_pig:
            self.trial.model.read_pig_lowerbody()
        if read_musclelen:
            self.trial.model.read_musclelen()
                                      
    def set_fig_title(self, title):
        if self.fig:
            plt.figure(self.fig.number) 
            plt.suptitle(title, fontsize=12, fontweight="bold")

    def plot_trial(self, cycle=1, side=None, plotheightratios=None, maintitle=None, maintitleprefix='',
                 onesided_kinematics=False, model_linestyle='-', emg_tracecolor='black'):
        """ Plot active trial (must call open_xxx_trial first). If a plot is already 
        active, the new trial will be overlaid on the previous one.
        Parameters:
        cycle: which gait cycle to use from the trial (default=first)
        side: which side kinetics/kinematics to plot (default=determine from trial).
        Note that kinematics are two-sided by default (unless onesided_kinematics=True)
        maintitle: plot title; leave unspecified for automatic title (can also then
        supply maintitleprefix)
        model_linestyle: plotting style for model variables (PiG etc.)
        emg_tracecolor: color for EMG traces
        """        
        if not self.trial:
            error_exit('No trial loaded')

        # which side kinetics/kinematics to plot (if one-sided)
        if side:
            side = side.upper()
        else:
            side = self.trial.kinetics           
        
        # if plot height ratios not set, set them all equal    
        if not plotheightratios:
            self.plotheightratios = [1] * self.gridv

        # automatic title
        if not maintitle:
            maintitle = maintitleprefix + self.trial.trialname + ' ('+self.trial.kinetics+')'
        
        # x variable for kinematics / kinetics: 0,1...100
        tn = np.linspace(0, 100, 101)
        # for normal data: 0,2,4...100.
        tn_2 = np.array(range(0, 101, 2))

        # create/switch to figure and set title        
        if self.fig:
            plt.figure(self.fig.number) 
        else:
            self.fig = plt.figure(figsize=self.totalfigsize)
            self.gs = gridspec.GridSpec(self.gridv, self.gridh, height_ratios=plotheightratios)
        plt.suptitle(maintitle, fontsize=12, fontweight="bold")
        
        # handle model output vars (Plug-in Gait, muscle length, etc.)
        if self.model_plot_vars:
            for k, varname_ in enumerate(self.model_plot_vars):  # varname_ is not side specific, e.g. 'HipMomentX'
                ax = plt.subplot(self.gs[self.model_plot_pos[k]])
                if not self.trial.model.is_kinetic_var(varname_) and not onesided_kinematics:  # plot both sides (L/R)
                    sides = ['L','R']
                else:
                    sides = side
                for side_ in sides:  # loop thru sides, normalize and plot data
                    varname = side_ + varname_  # side-specific variable name, e.g. 'LHipMomentX'
                    data_gc = self.trial.normalize_to_cycle(self.trial.model.Vars[varname], side_, cycle)
                    if side_ == 'L':
                        tracecolor = self.tracecolor_l
                    elif side_ == 'R':
                        tracecolor = self.tracecolor_r
                    plt.plot(tn, data_gc, tracecolor, linestyle=model_linestyle, label=self.trial.trialname)
                # plot normal data, if available
                if self.trial.model.normaldata(varname_):
                    nor = np.array(self.trial.model.normaldata(varname_))[:,0]
                    nstd = np.array(self.trial.model.normaldata(varname_))[:,1]
                    plt.fill_between(tn_2, nor-nstd, nor+nstd, color=self.normals_color, alpha=self.normals_alpha)
                # set titles and labels
                title = self.trial.model.description(varname)
                ylabel = self.trial.model.ylabel(varname_)
                plt.title(title, fontsize=self.fsize_labels)
                plt.xlabel(self.xlabel,fontsize=self.fsize_labels)
                plt.ylabel(ylabel, fontsize=self.fsize_labels)
                # variable-specific scales
                #plt.ylim(kinematicsymin[k], kinematicsymax[k])
                ylim_default= ax.get_ylim()
                # include zero line and extend y scale a bit for kin* variables
                plt.axhline(0, color='black')  # zero line
                if self.trial.model.is_pig_lowerbody_variable(varname_):
                    if ylim_default[0] == 0:
                        plt.ylim(-10, ylim_default[1])
                    if ylim_default[1] == 0:
                        plt.ylim(ylim_default[0], 10)
                # expand the default scale a bit for muscle length variables, but no zeroline
                if self.trial.model.is_musclelen_variable(varname_):
                    plt.ylim(ylim_default[0]-10, ylim_default[1]+10)
                plt.locator_params(axis = 'y', nbins = 6)  # reduce number of y tick marks
                # add arrows indicating toe off times
                if self.add_toeoff_markers:
                    ymin = ax.get_ylim()[0]
                    ymax = ax.get_ylim()[1]
                    xmin = ax.get_xlim()[0]
                    xmax = ax.get_xlim()[1]
                    ltoeoff = self.gc.ltoe1_norm
                    rtoeoff = self.gc.rtoe1_norm
                    arrlen = (ymax-ymin) * self.toeoff_rel_len
                    # these are related to plot height/width, to avoid aspect ratio effects
                    hdlength = arrlen * .33
                    hdwidth = (xmax-xmin) / 50.
                    if not self.trial.model.is_kinetic_var(varname_) and not onesided_kinematics:
                        plt.arrow(ltoeoff, ymin, 0, arrlen, color=self.tracecolor_l, 
                                  head_length=hdlength, head_width=hdwidth)
                        plt.arrow(rtoeoff, ymin, 0, arrlen, color=self.tracecolor_r, 
                                  head_length=hdlength, head_width=hdwidth)
                    else:  # single trace was plotted - only plot one-sided toeoff
                        if self.trial.kinetics == 'L':
                            toeoff = ltoeoff
                            arrowcolor = self.tracecolor_l
                        else:
                            toeoff = rtoeoff
                            arrowcolor = self.tracecolor_r
                        plt.arrow(toeoff, ymin, 0, arrlen, color=arrowcolor, 
                          head_length=hdlength, head_width=hdwidth)
        
        # emg plotting
        if self.emg_plot_chs:
            for k, thisch in enumerate(self.emg_plot_chs):
                side_this = thisch[0]
                # choose EMG data normalized according to side
                if side_this == 'L':
                    tn_emg = self.emg.tn_emg_l
                    emgdata = self.emg.logical_data_gc1l
                    #emg_yscale = self.emg.yscale_gc1l
                elif side_this == 'R':
                    tn_emg = self.emg.tn_emg_r
                    emgdata = self.emg.logical_data_gc1r
                    #emg_yscale = self.emg.yscale_gc1r
                else:
                    error_exit('Unexpected EMG channel name: ', thisch)
                # at least for now, use fixed scale defined in config
                emg_yscale = self.cfg.getval('emg_yscale')
                ax = plt.subplot(self.gs[self.emg_plot_pos[k]])
                if not self.cfg.emg_enabled(thisch):
                        ax.annotate('disabled (manual)', xy=(50,0), ha="center", va="center")                    
                elif emgdata[thisch] == 'EMG_DISCONNECTED':
                    if self.annotate_disconnected:
                        ax.annotate('disabled (auto)', xy=(50,0), ha="center", va="center")
                elif emgdata[thisch] == 'EMG_REUSED':
                        ax.annotate('reused', xy=(50,0), ha="center", va="center")
                else:  # data OK
                    if self.emg_apply_filter:
                        # convert emg to millivolts
                        plt.plot(tn_emg, 1e3*self.emg.filt(emgdata[thisch], self.emg_passband), emg_tracecolor, alpha=self.emg_alpha, label=self.trial.trialname)
                    else:
                        plt.plot(tn_emg, 1e3*emgdata[thisch], emg_tracecolor, alpha=self.emg_alpha, label=self.trial.trialname)
                chlabel = self.emg.ch_labels[thisch]
                # plot EMG normal bars
                emgbar_ind = self.emg.ch_normals[thisch]
                for k in range(len(emgbar_ind)):
                    inds = emgbar_ind[k]
                    plt.axvspan(inds[0], inds[1], alpha=self.emg_normals_alpha, color=self.emg_normals_color)    
                plt.ylim(-emg_yscale, emg_yscale)  # scale is in mV
                plt.xlim(0,100)
                plt.title(chlabel, fontsize=10)
                plt.xlabel(self.xlabel, fontsize=self.fsize_labels)
                plt.ylabel(self.emg_ylabel, fontsize=self.fsize_labels)
                plt.locator_params(axis = 'y', nbins = 4)
                
                if self.add_toeoff_markers:
                    ymin = ax.get_ylim()[0]
                    ymax = ax.get_ylim()[1]
                    xmin = ax.get_xlim()[0]
                    xmax = ax.get_xlim()[1]
                    ltoeoff = self.gc.ltoe1_norm
                    rtoeoff = self.gc.rtoe1_norm
                    arrlen = (ymax-ymin) * self.toeoff_rel_len
                    hdlength = arrlen / 4.
                    hdwidth = (xmax-xmin) / 40.
                    if side_this == 'L':
                        toeoff = ltoeoff
                        arrowcolor = self.tracecolor_l
                    else:
                        toeoff = rtoeoff
                        arrowcolor = self.tracecolor_r
                    plt.arrow(toeoff, ymin, 0, arrlen, color=arrowcolor, 
                              head_length=hdlength, head_width=hdwidth)
                    plt.arrow(toeoff, ymin, 0, arrlen, color=arrowcolor, 
                              head_length=hdlength, head_width=hdwidth)

        """ Update the legends on each added trial. The "artists" (corresponding to 
        line styles) and the labels are appended into lists and the legend
        is recreated when plotting each trial (the legend has no add method) """
        if self.model_legendpos or self.emg_legendpos:
            self.legendnames.append(self.trial.trialname)
            # TODO: + gait_getdata.get_eclipse_description(self.trial.trialname))            
        if self.model_legendpos:
            self.modelartists.append(plt.Line2D((0,1),(0,0), color=self.tracecolor_r, linestyle=model_linestyle))
            ax = plt.subplot(self.gs[self.model_legendpos])
            plt.axis('off')
            nothing = [plt.Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)]
            legtitle = ['Kinematics/kinetics traces:']
            ax.legend(nothing+self.modelartists, legtitle+self.legendnames, prop={'size':self.fsize_labels}, loc='upper center')
        if self.emg_legendpos:
            self.emgartists.append(plt.Line2D((0,1),(0,0), color=emg_tracecolor))
            ax = plt.subplot(self.gs[self.emg_legendpos])
            plt.axis('off')
            nothing = [plt.Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)]
            legtitle = ['EMG traces:']
            ax.legend(nothing+self.emgartists, legtitle+self.legendnames, prop={'size':self.fsize_labels}, loc='upper center')
        
        # fix plot spacing, restrict to below title
        self.gs.tight_layout(self.fig, h_pad=.1, w_pad=.1, rect=[0,0,1,.95])
        
    
    def create_pdf(self, pdf_name=None, pdf_prefix=None):
        """ Make a pdf out of the created figure into the Nexus session directory. 
        If pdf_name is not specified, automatically name according to current trial. """
        if self.fig:
            # resize figure to a4 size
            # self.fig.set_size_inches([8.27,11.69])
            if pdf_name:
                # user specified name into session dir
                pdf_name = self.sessionpath + pdf_name
            else:
                # automatic naming by trialname
                if not pdf_prefix:
                    pdf_prefix = 'Nexus_plot_'
                pdf_name = self.sessionpath + pdf_prefix + self.trial.trialname + '.pdf'
            try:
                with PdfPages(pdf_name) as pdf:
                    print("Writing "+pdf_name)
                    pdf.savefig(self.fig)
            except IOError:
                messagebox('Error writing PDF file, check that file is not already open.')
                #messagebox('Successfully wrote PDF file: '+pdf_name)
        else:
            raise Exception('No figure to save!')
    
    def show(self):
        """ Shows the figure. """
        if self.fig:
            plt.show(self.fig)
            
    
   
   
