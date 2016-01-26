# -*- coding: utf-8 -*-
"""

Gaitplotter: plot gait data using matplotlib.

TODO:
variable title handling if multiple vars on single subplot (L/R mess)


Rules:
-channel type is autodetected by looking into the known names
-can specify channel as 'None' to leave corresponding subplot empty
-can specify channel as 'modellegend' or 'emglegend' to get a legend on a particular subplot
(useful for overlay plots)
-variables always normalized to gait cycle
-always plot model normal data if available
-kinetics always plotted for one side only
-vars are specified without leading side prefix (e.g. 'HipMomentX'
 instead of 'NormRHipMomentX'; side is either autodetected or manually forced

"""


from Tkinter import *
import tkFileDialog
import matplotlib.pyplot as plt
import numpy as np
import getdata
from misc import error_exit, messagebox, nexus_pid
from getdata import debug_print
import config
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import os
import getpass
import glob
import subprocess
import pylab


class gaitplotter():
    """ Create a plot of Nexus variables. Can overlay data from several trials. """

    def __init__(self):
        # set paths
        pathprefix = 'c:/users/' + getpass.getuser()
        self.desktop = pathprefix + '/Desktop'
        self.appdir = self.desktop + '/GaitPlotter'
        
        # read .ini file if available
        self.cfg = config.Config(self.appdir)
        config_ok, msg = self.cfg.check()
        if not config_ok:
            error_exit('Error in configuration file, please fix or delete: ', self.configfile)
        self.emg_passband = [0,0]
        self.emg_passband[0] = self.cfg.getval('emg_highpass')
        self.emg_passband[1] = self.cfg.getval('emg_lowpass')
        self.emg_apply_filter = self.cfg.getval('emg_apply_filter')
        self.emg_auto_off = self.cfg.getval('emg_auto_off')
        self.emg_names = getdata.emg(None).ch_names
        self.emg_names.sort()
        self.emg_manual_enable={}
        for ch in self.emg_names:
            self.emg_manual_enable[ch] = self.cfg.emg_enabled(ch)

        # (currently) non-configurable stuff
        # figure size
        #self.totalfigsize = (8.48*1.2,12*1.2) # a4
        self.totalfigsize = (14,12)
        # grid dimensions, vertical and horizontal
        self.gridv = None
        self.gridh = None
        # trace colors, right and left
        self.tracecolor_r = 'lawngreen'
        self.tracecolor_l = 'red'
        # relative length of toe-off arrow (multiples of plot y height)
        self.toeoff_rel_len = .15
        # subplot title font size
        self.fsize_titles=10
        # subplot label font size
        self.fsize_labels=8
        # subplot tick label font size
        self.fsize_ticks=8
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
        # must be opened later
        self.vicon = None
        
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

    def dir_trialselector(self, trialpath):
        """ Let the user choose from processed trials in the trial directory. 
        Will also show the Eclipse description for each processed trial, if 
        available. Tk checkbox dialog. """
        if not os.path.isdir(trialpath):
            error_exit('Invalid path')
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
            desc = getdata.get_eclipse_key(trialpath, 'DESCRIPTION')
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
            self.chosen = self.trials.values()
            
        def cancel(self):
            self.chosen = []
            self.master.destroy()
            
        def delete_trial(self, trial):
            self.tributtons[trial].grid_remove()
            self.trilabels[trial].grid_remove()
            self.tributtons.pop(trial, None)
            self.trilabels.pop(trial, None)            
            self.trials.pop(trial, None)
            self.ntrials -= 1
            if self.ntrials < self.MAX_TRIALS:
                self.loadb.config(state='normal')
    
        def load_trial(self):
            nrow = self.ntrials + 1
            trialpath = tkFileDialog.askopenfilename(**self.options).encode()
            if not trialpath:
                return
            trial =  os.path.basename(os.path.splitext(trialpath)[0])
            if trial in self.trials:
                messagebox('Trial already loaded!')
            elif os.path.isfile(trialpath):
                # get Eclipse info (notes and description) for the trial
                desc = getdata.get_eclipse_key(trialpath, 'DESCRIPTION')
                if not desc:
                    desc = '(no description)'
                notes = getdata.get_eclipse_key(trialpath, 'NOTES')
                if not notes:
                    notes = '(no notes)'
                trialstr = trial+4*' '+desc+4*' '+notes
                la = Label(self.master, text=trialstr)
                la.grid(row=nrow, column=0, columnspan=2, sticky=W)
                self.trilabels[trial] = la
                bu = Button(self.master, text='Delete', command=lambda: self.delete_trial(trial))
                bu.grid(row=nrow, column=2)
                self.tributtons[trial] = bu
                self.trials[trial] = trialpath
                self.ntrials += 1                
                if self.ntrials == self.MAX_TRIALS:
                    self.loadb.config(state='disabled')
            else:
                # this should never happen, since file dialog checks for existence?
                messagebox('Requested trial does not exist!')
    
        def __init__(self, max_trials=4, initialdir='C:\\'):
            self.trials = {}
            self.chosen = []
            self.trilabels = {}
            self.tributtons = {}
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
        if not nexus_pid():
            error_exit('Cannot get Nexus PID, Nexus not running?')
        if not self.vicon:
            self.vicon = getdata.viconnexus()
        trialname_ = self.vicon.GetTrialName()
        if not trialname_:
            return None
        else:
            return(trialname_[0])

    def open_nexus_trial(self):
        """ Open trial from Nexus. """
        if not nexus_pid():
            error_exit('Cannot get Nexus PID, Nexus not running?')
        self.vicon = getdata.viconnexus()
        try:
            self.trial = getdata.trial(self.vicon, emg_auto_off=self.emg_auto_off, emg_mapping=self.emg_mapping)
        except getdata.GaitDataError as e:
            error_exit('Error while opening trial from Nexus:\n'+e.msg)
        
    def open_c3d_trial(self, trialpath):
        """ Open a c3d trial. """
        if not os.path.isfile(trialpath):
            error_exit('Cannot find trial: '+trialpath)
        try:
            self.trial = getdata.trial(trialpath, emg_auto_off=self.emg_auto_off, emg_mapping=self.emg_mapping)
        except getdata.GaitDataError as e:
            error_exit('Error while opening '+trialpath+':\n'+e.msg)

    def external_play_video(self, vidfile):
        """ Launch an external video player (defined in config) to play vidfile.
        vidfile is given as the last argument to the command. """
        # TODO: put into config file
        PLAYER_CMD = self.cfg.getval('videoplayer_path')
        PLAYER_OPTS = self.cfg.getval('videoplayer_opts')
        subprocess.Popen([PLAYER_CMD,PLAYER_OPTS,vidfile])
        
    def read_trial(self, vars):
        """ Read requested trial variables and directives.
        vars is a list of lists: rows to be plotted. """
        self.gridv = len(vars)
        self.gridh = len(vars[0])
        self.vars = []
        [self.vars.extend(x) for x in vars]  # flatten 2-dim list to 1-dim
        read_emg = False
        read_models = []  # which models to read
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
                elif var in self.trial.model.varnames or 'R'+var in self.trial.model.varnames:
                    """ Model vars are specified without side (e.g. 'HipMomentX'), but the actual
                    stored variables have a side (=leading 'R' or 'L'). This is a bit ugly. """
                    read_models.append(self.trial.model.get_model('R'+var))
                    self.model_plot_vars.append(var)
                    self.model_plot_pos.append(i)
                else:
                    error_exit('Unknown variable or plot directive: ' + var)
        try:
            if read_emg:
                    self.trial.emg.read()
            if read_models:
                    for model in read_models:
                        if not model.was_read:
                            self.trial.model.read_model(model)
                            model.was_read = True
        except getdata.GaitDataError as e:
            msg = 'Error while reading from trial ' + self.trial.trialname + ':\n' + e.msg
            error_exit(msg)
                                      
    def set_fig_title(self, title):
        if self.fig:
            plt.figure(self.fig.number) 
            plt.suptitle(title, fontsize=12, fontweight="bold")

    def plot_trial(self, cycle=1, side=None, plotheightratios=None, maintitle=None, maintitleprefix='',
                 onesided=False, model_linestyle='-', emg_tracecolor='black'):
        """ Plot active trial (must call open_xxx_trial first). If a plot is already 
        active, the new trial will be overlaid on the previous one.
        Parameters:
        cycle: which gait cycle to use from the trial (default=first)
        side: which side kinetics/kinematics to plot (default=determine from trial).
        Note that non-kinetics vars are two-sided by default (unless onesided=True)
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
            side = self.trial.kinetics_side
        
        # if plot height ratios not set, set them all equal    
        if not plotheightratios:
            self.plotheightratios = [1] * self.gridv

        # automatic title
        if not maintitle:
            maintitle = maintitleprefix + self.trial.trialname + ' ('+self.trial.kinetics_side+')'
        
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

        # get info on left and right gait cycles
        lcyc = self.trial.get_cycle('L', cycle)
        rcyc = self.trial.get_cycle('R', cycle)
        if not (lcyc and rcyc):
            error_exit('Cannot get requested left/right gait cycles from data')

        # handle model output vars (Plug-in Gait, muscle length, etc.)
        if self.model_plot_vars:
            for k, varname_ in enumerate(self.model_plot_vars):  # varname_ is not side specific, e.g. 'HipMomentX'
                ax = plt.subplot(self.gs[self.model_plot_pos[k]])
                # plot one side only on single subplot?
                plot_onesided = self.trial.model.is_kinetic_var(varname_) or onesided
                if not plot_onesided:
                    sides = ['L','R']
                else:
                    sides = side
                for side_ in sides:  # loop thru sides, normalize and plot data
                    varname = side_ + varname_  # side-specific variable name, e.g. 'LHipMomentX'
                    debug_print('Plotting:', varname)                    
                    if side_ == 'L':
                        tracecolor = self.tracecolor_l
                        cyc = lcyc
                    elif side_ == 'R':
                        tracecolor = self.tracecolor_r
                        cyc = rcyc
                    data_gc = cyc.normalize(self.trial.model.modeldata[varname])
                    plt.plot(tn, data_gc, tracecolor, linestyle=model_linestyle, label=self.trial.trialname)
                # plot normal data, if available
                ndata = self.trial.model.get_normaldata(varname)
                if ndata:
                    nor = np.array(ndata)[:,0]
                    nstd = np.array(ndata)[:,1]
                    plt.fill_between(tn_2, nor-nstd, nor+nstd, color=self.normals_color, alpha=self.normals_alpha)
                # set titles and labels
                # include side info if plotting single side
                if plot_onesided:
                    title = self.trial.model.varlabels[varname] + ' ('+side+')'
                else:
                    title = self.trial.model.varlabels[varname] + ' (LR)'
                ylabel = self.trial.model.ylabels[varname]
                plt.title(title, fontsize=self.fsize_titles)
                plt.xlabel(self.xlabel,fontsize=self.fsize_labels)
                plt.ylabel(ylabel, fontsize=self.fsize_labels)
                # experimental - reduce label padding
                #axcurrent = plt.gca()
                #axcurrent.yaxis.labelpad = 0
                # variable-specific scales
                #plt.ylim(kinematicsymin[k], kinematicsymax[k])
                ylim_default= ax.get_ylim()
                # include zero line and extend y scale a bit for kin* variables
                plt.axhline(0, color='black')  # zero line
                if self.trial.model.get_model(varname).type == 'PiG':
                    if ylim_default[0] == 0:
                        plt.ylim(-10, ylim_default[1])
                    if ylim_default[1] == 0:
                        plt.ylim(ylim_default[0], 10)
                # expand the default scale a bit for muscle length variables, but no zeroline
                if self.trial.model.get_model(varname).type == 'musclelen':
                    plt.ylim(ylim_default[0]-10, ylim_default[1]+10)
                plt.locator_params(axis = 'y', nbins = 6)  # reduce number of y tick marks
                # tick font size                
                plt.tick_params(axis='both', which='major', labelsize=self.fsize_ticks)
                # add arrows indicating toe off times
                if self.add_toeoff_markers:
                    ymin = ax.get_ylim()[0]
                    ymax = ax.get_ylim()[1]
                    xmin = ax.get_xlim()[0]
                    xmax = ax.get_xlim()[1]
                    arrlen = (ymax-ymin) * self.toeoff_rel_len
                    # these are related to plot height/width, to avoid aspect ratio effects
                    hdlength = arrlen * .33
                    hdwidth = (xmax-xmin) / 50.
                    # plot both L/R toeoff arrows
                    if not plot_onesided:
                        plt.arrow(lcyc.toeoffn, ymin, 0, arrlen, color=self.tracecolor_l, 
                                  head_length=hdlength, head_width=hdwidth)
                        plt.arrow(rcyc.toeoffn, ymin, 0, arrlen, color=self.tracecolor_r, 
                                  head_length=hdlength, head_width=hdwidth)
                    else:  # single trace was plotted - only plot one-sided toeoff
                        if side == 'L':
                            toeoff = lcyc.toeoffn
                            arrowcolor = self.tracecolor_l
                        else:
                            toeoff = rcyc.toeoffn
                            arrowcolor = self.tracecolor_r
                        plt.arrow(toeoff, ymin, 0, arrlen, color=arrowcolor, 
                          head_length=hdlength, head_width=hdwidth)
        
        # emg plotting
        if self.emg_plot_chs:
            for k, thisch in enumerate(self.emg_plot_chs):
                side_this = thisch[0]
                # normalize EMG data according to side
                if side_this == 'L':
                    cyc = lcyc
                elif side_this == 'R':
                    cyc = rcyc
                else:
                    error_exit('Unexpected EMG channel name: ', thisch)
                tn_emg, emgdata = self.trial.emg.cut_to_cycle(cyc)
                
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
                        plt.plot(tn_emg, 1e3*self.trial.emg.filt(emgdata[thisch], self.emg_passband), emg_tracecolor, alpha=self.emg_alpha, label=self.trial.trialname)
                    else:
                        plt.plot(tn_emg, 1e3*emgdata[thisch], emg_tracecolor, alpha=self.emg_alpha, label=self.trial.trialname)
                chlabel = self.trial.emg.ch_labels[thisch]
                # plot EMG normal bars
                emgbar_ind = self.trial.emg.ch_normals[thisch]
                for k in range(len(emgbar_ind)):
                    inds = emgbar_ind[k]
                    plt.axvspan(inds[0], inds[1], alpha=self.emg_normals_alpha, color=self.emg_normals_color)    
                plt.ylim(-emg_yscale, emg_yscale)  # scale is in mV
                plt.xlim(0,100)
                plt.title(chlabel, fontsize=self.fsize_titles)
                plt.xlabel(self.xlabel, fontsize=self.fsize_labels)
                plt.ylabel(self.emg_ylabel, fontsize=self.fsize_labels)
                plt.locator_params(axis = 'y', nbins = 4)
                # tick font size                
                plt.tick_params(axis='both', which='major', labelsize=self.fsize_ticks)
                
                if self.add_toeoff_markers:
                    ymin = ax.get_ylim()[0]
                    ymax = ax.get_ylim()[1]
                    xmin = ax.get_xlim()[0]
                    xmax = ax.get_xlim()[1]
                    arrlen = (ymax-ymin) * self.toeoff_rel_len
                    hdlength = arrlen / 4.
                    hdwidth = (xmax-xmin) / 40.
                    if side_this == 'L':
                        toeoff = lcyc.toeoffn
                        arrowcolor = self.tracecolor_l
                    else:
                        toeoff = rcyc.toeoffn
                        arrowcolor = self.tracecolor_r
                    plt.arrow(toeoff, ymin, 0, arrlen, color=arrowcolor, 
                              head_length=hdlength, head_width=hdwidth)
                    plt.arrow(toeoff, ymin, 0, arrlen, color=arrowcolor, 
                              head_length=hdlength, head_width=hdwidth)

        """ Update the legends on each added trial. The "artists" (corresponding to 
        line styles) and the labels are appended into lists and the legend
        is recreated when plotting each trial (the legend has no add method) """
        if self.model_legendpos or self.emg_legendpos:
            self.legendnames.append(self.trial.trialname+4*' '+self.trial.eclipse_description+4*' '+self.trial.eclipse_notes)
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
        # magic numbers that work for most cases; hspace and wspace need to be adjusted if label font sizes change, etc.
        self.gs.update(left=.08, right=.98, top=.92, bottom=.03, hspace=.37, wspace=.22)

    def move_figure(self, x,y):
        """ Move figure upper left corner to x,y. Only works with Qt backend. """
        if 'Qt4' in pylab.get_backend():
            cman = pylab.get_current_fig_manager()
            _,_,dx,dy = cman.window.geometry().getRect()
            cman.window.setGeometry(x,y,dx,dy)
    
    def create_pdf(self, pdf_name=None, pdf_prefix=None):
        """ Make a pdf out of the created figure into the Nexus session directory. 
        If pdf_name is not specified, automatically name according to current trial. """
        if self.fig:
            # resize figure to a4 size
            # self.fig.set_size_inches([8.27,11.69])
            if pdf_name:
                # user specified name into session dir
                pdf_name = self.trial.sessionpath + pdf_name
            else:
                # automatic naming by trialname
                if not pdf_prefix:
                    pdf_prefix = 'Nexus_plot_'
                pdf_name = self.trial.sessionpath + pdf_prefix + self.trial.trialname + '.pdf'
            try:
                debug_print('trying to create: '+pdf_name)
                with PdfPages(pdf_name) as pdf:
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
            
    
   
   
