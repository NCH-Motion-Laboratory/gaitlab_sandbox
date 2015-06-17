# -*- coding: utf-8 -*-
"""

Generic Nexus plotter. Plots Plug-in Gait variables and EMG from a running
Vicon Nexus application, using matplotlib.


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


TODO:

tests
documentation
add default y ranges for kine(ma)tics variables?
"""




from Tkinter import *
import matplotlib.pyplot as plt
import numpy as np
import nexus_getdata
from nexus_getdata import error_exit, messagebox
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
import ConfigParser
from ConfigParser import SafeConfigParser



def strip_ws(str):
    """ Remove spaces from string """
    return str.replace(' ','')


class PlotterConfig():
    """ Class to store and handle config data. Config variables are internally
    stored as text, but returned as float or boolean if applicable. """

    def __init__(self, appdir):
        """ Initialize user-configurable values to default. """
        
        self.config = {}
        self.config['emg_lowpass'] = '400'
        self.config['emg_highpass'] = '10'
        self.config['emg_yscale'] = '0.5'
        self.config['pig_normaldata_path'] = appdir + '/Data/normal.gcd'
        self.config['emg_auto_off'] = 'True'
        self.config['emg_apply_filter'] = 'True'
        self.configfile = appdir + '/Config/NexusPlotter.ini'
        self.appdir = appdir        
        
        # get EMG electrode names and write enable/disable values
        self.emg_names = nexus_getdata.nexus_emg().ch_names
        self.emg_names.sort()
        for chname in self.emg_names:
            self.config[self.emg_enabled_key(chname)] = 'True'

        # some limits for config file validation (and Tk widgets)      
        self.min = {}
        self.max = {}
        self.min['emg_lowpass'] = 10
        self.min['emg_highpass'] = 0
        self.min['emg_yscale'] = 1e-2
        self.max['emg_yscale'] = 100
        self.max['emg_lowpass'] = 500
        self.max['emg_highpass'] = 490
        
        if os.path.isfile(self.configfile):
            self.read()
        
    def isfloat(self, str):
        """ Check if str can be interpreted as floating point number. """
        try:
            float(str)
            return True
        except ValueError:
            return False
            
    def isboolean(self, str):
        """ Check if str is "boolean". """
        return str in ['True', 'False']

    def check(self):
        """ Validate config. """
        hp = self.getval('emg_highpass')
        lp = self.getval('emg_lowpass')
        if not self.isfloat(hp) and self.isfloat(lp):
            return (False, 'Frequencies must be numeric')            
        # want to leave at least 5 Hz band, and lowpass > highpass
        if not hp+5 <= lp <= self.max['emg_lowpass']:
            return (False, 'Invalid lowpass frequency')
        if not self.min['emg_highpass'] <= hp <= lp-5:
            return (False, 'Invalid highpass frequency')
        return (True, '')
        
    def getval(self, key):
        """ Return value as float or boolean if possible, otherwise as string """
        val = self.config[key]
        if self.isboolean(val):
            return val == 'True'
        elif self.isfloat(val):
            return float(val)
        else:
            return val
            
    def setval(self, key, val):
        """ Stores val into config dict as string. """
        self.config[key] = str(val)
        
    def emg_enabled_key(self, emgch):
        """ Returns an 'enable' key name for a given EMG channel. 
        This is just a prefix and the channel name. """
        return 'EMG_ENABLE_'+emgch

    def is_emg_enabled_key(self, key):
        """ Tell whether it's an EMG 'enable' key. """
        return key.find('EMG_ENABLE_') == 0
    
    def emg_enabled(self, emgch):
        """ Return the 'enabled' value for the given EMG channel. """
        key = self.emg_enabled_key(emgch)
        return self.config[key] == 'True'
                      
    def read(self):
        """ Read whole config dict from disk file. Disk file must match the dict
        object in memory. """
        parser = SafeConfigParser()
        parser.optionxform = str  # make it case sensitive
        parser.read(self.configfile)
        for key in self.config.keys():
            if self.is_emg_enabled_key(key):
                section = 'EMG_enable'
            else:
                section = 'NexusPlotter'
            try:
                self.config[key] = parser.get(section, key)
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                error_exit('Invalid configuration file, please fix or delete: ' + self.configfile)
        
    def write(self):
        """ Save current config dict to a disk file. """
        try:
            inifile = open(self.configfile, 'wt')
        except IOError:
            error_exit('Cannot open config file for writing: ', self.configfile)
        parser = SafeConfigParser()
        parser.optionxform = str  # make it case sensitive
        parser.add_section('NexusPlotter')
        parser.add_section('EMG_enable')  
        for key in self.config.keys():
            if self.is_emg_enabled_key(key):
                section = 'EMG_enable'
            else:
                section = 'NexusPlotter'
            parser.set(section, key, self.config[key])
        parser.write(inifile)
        inifile.close()

    def window(self):
        """ Opens a Tk window for setting config variables. """
        
        def saver_callback(window, list):
            """ Signaler callback for root window; modify list to indicate that 
            user pressed save, and destroy the window. """
            list.append(1)
            window.destroy()
        # Tk variables
        master = Tk()
        emg_auto_off = IntVar()
        emg_apply_filter = IntVar()
        emg_lowpass = StringVar()
        emg_highpass = StringVar()
        emg_yscale = DoubleVar()
        gcdpath = StringVar()
        emg_enable_vars = []
        # read default values (config -> Tk variables)        
        if self.getval('emg_auto_off'):
            emg_auto_off.set(1)
        else:
            emg_auto_off.set(0)
        if self.getval('emg_apply_filter'):
            emg_apply_filter.set(1)
        else:
            emg_apply_filter.set(0)
        emg_lowpass.set(self.getval('emg_lowpass'))
        emg_highpass.set(self.getval('emg_highpass'))
        emg_yscale.set(self.getval('emg_yscale'))
        gcdpath.set(self.getval('pig_normaldata_path'))
        # populate root window
        save = []
        thisrow = 1
        Label(master, text="Select options for Nexus plotter:").grid(row=thisrow, columnspan=2, pady=4)
        thisrow += 1
        Checkbutton(master, text="Autodetect disconnected EMG electrodes", variable=emg_auto_off).grid(row=thisrow, pady=4, columnspan=2, sticky=W)              
        thisrow += 1
        Checkbutton(master, text="Apply EMG filter", variable=emg_apply_filter).grid(row=thisrow, pady=4, columnspan=2, sticky=W)
        thisrow += 1
        Label(master, text='EMG highpass (Hz):').grid(row=thisrow, column=0, pady=4, sticky=W)
        sp2=Spinbox(master, from_=self.min['emg_highpass'], to=self.max['emg_highpass'], textvariable=emg_highpass).grid(row=thisrow, column=1, pady=4, sticky=W)
        thisrow += 1
        Label(master, text='EMG lowpass (Hz):').grid(row=thisrow, column=0, pady=4, sticky=W)
        Spinbox(master, from_=self.min['emg_lowpass'], to=self.max['emg_lowpass'], textvariable=emg_lowpass).grid(row=thisrow, column=1, pady=4, sticky=W)
        thisrow += 1        
        Label(master, text='EMG y scale (mV):').grid(row=thisrow, column=0, pady=4, sticky=W)
        e = Spinbox(master, from_=.05, to=5, format="%.2f", increment=.05, textvariable=emg_yscale).grid(row=thisrow, column=1, pady=4, sticky=W)
        thisrow += 1
        Label(master, text='Enable or disable EMG electrodes:').grid(row=thisrow, column=0, pady=4, sticky=W)
        thisrow += 1
        # put EMG channel names into two columns
        for i, ch in enumerate(self.emg_names):
            emg_enable_vars.append(IntVar())
            if self.emg_enabled(ch):
                emg_enable_vars[i].set(1)
            else:
                emg_enable_vars[i].set(0)
            if not i % 2:  # even - left col
                Checkbutton(master, text=ch, variable=emg_enable_vars[i]).grid(row=thisrow, column=0, sticky=W)
            else:  # right col
                Checkbutton(master, text=ch, variable=emg_enable_vars[i]).grid(row=thisrow, column=1, sticky=W)            
                thisrow += 1
        Label(master, text='Location of PiG normal data (.gcd):   ').grid(row=thisrow, column=0, pady=4, sticky=W)
        e = Entry(master, textvariable=gcdpath).grid(row=thisrow, column=1, pady=4, sticky=W)
        thisrow += 1
        Button(master, text='Cancel', command=master.destroy).grid(row=thisrow, column=0, pady=4)
        Button(master, text='Save config', command=lambda: saver_callback(master, save)).grid(row=thisrow, column=1, pady=4)
        mainloop()  # Tk
        if not save:  # user hit Cancel
            return None
        else:
            # create new tentative config instance, test validity first
            newconfig = PlotterConfig(self.appdir)
            # from Tk variables to config
            newconfig.setval('emg_lowpass', emg_lowpass.get())
            newconfig.setval('emg_highpass', emg_highpass.get())
            newconfig.setval('emg_yscale', emg_yscale.get())
            newconfig.setval('pig_normaldata_path', gcdpath.get())
            if emg_auto_off.get():
                newconfig.setval('emg_auto_off', 'True')
            else:
                newconfig.setval('emg_auto_off', 'False')
            if emg_apply_filter.get():
                newconfig.setval('emg_apply_filter', 'True')
            else:
                newconfig.setval('emg_apply_filter', 'False')
            for i,var in enumerate(emg_enable_vars):
                if var.get():
                    newconfig.setval(newconfig.emg_enabled_key(self.emg_names[i]), 'True')
                else:
                    newconfig.setval(newconfig.emg_enabled_key(self.emg_names[i]), 'False')                    
            config_ok, msg = newconfig.check()
            if not config_ok:
                messagebox('Invalid configuration: ' + msg)
                self.window()
            else:  # config ok
                self.config = newconfig.config
                self.write()

class nexus_plotter():
    """ Create a plot of Nexus variables. Can overlay data from several trials. """

    def __init__(self, layout):
        # set paths
        pathprefix = 'c:/users/' + getpass.getuser()
        self.desktop = pathprefix + '/Desktop'
        self.appdir = self.desktop + '/NexusPlotter'
        
        # read .ini file if available
        self.cfg = PlotterConfig(self.appdir)
        config_ok, msg = self.cfg.check()
        if not config_ok:
            error_exit('Error in configuration file, please fix or delete: ', self.configfile)

        self.emg_passband = [0,0]
        self.emg_passband[0] = self.cfg.getval('emg_highpass')
        self.emg_passband[1] = self.cfg.getval('emg_lowpass')
        self.emg_apply_filter = self.cfg.getval('emg_apply_filter')
        self.emg_auto_off = self.cfg.getval('emg_auto_off')
        self.pig_normaldata_path = self.cfg.getval('pig_normaldata_path')
        self.emg_names = nexus_getdata.nexus_emg().ch_names
        self.emg_names.sort()
        self.emg_manual_enable={}
        for ch in self.emg_names:
            self.emg_manual_enable[ch] = self.cfg.emg_enabled(ch)

        # muscle length normal data - not yet used
        self.mlen_normaldata_path = None

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
        self.trialname = None
        self.vgc = None
        self.vicon = None
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
            desc = self.get_eclipse_description(trialpath)
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

    def get_nexus_path(self):
        if not self.vicon:
            self.vicon = ViconNexus.ViconNexus()
        trialname_ = self.vicon.GetTrialName()
        if not trialname_:
            return None
        else:
            return(trialname_[0])
                                                    
    def open_trial(self, nexusvars, trialpath=None, side=None):
        """ Read specified trial, or the one already opened in Nexus. The
        variables specified in nexusvars will be read. To open the trial without
        reading variables, set nexusvars=None (useful for e.g. detecting side) """
        self.nexusvars = nexusvars
        if not nexus_getdata.nexus_pid():
            error_exit('Cannot get Nexus PID, Nexus not running?')
        # open connection to Nexus, if not previously opened
        if not self.vicon:
            self.vicon = ViconNexus.ViconNexus()
        if trialpath:
            # remove filename extension if present
            trialpath = os.path.splitext(trialpath)[0]
            self.vicon.OpenTrial(trialpath, 10)            
            # TODO: check errors
        subjectnames = self.vicon.GetSubjectNames()  
        if not subjectnames:
            error_exit('No subject defined in Nexus')
        trialname_ = self.vicon.GetTrialName()
        self.sessionpath = trialname_[0]
        self.trialname = trialname_[1]
        if not self.trialname:
            error_exit('No trial loaded')
        self.subjectname = subjectnames[0]
        
        # update gait cycle information
        self.vgc = nexus_getdata.gaitcycle(self.vicon)
        
        # try to detect side (L/R) if not forced in arguments
        if not side:
            self.side = self.vgc.detect_side(self.vicon)
        else:
            self.side = side    
         
        if nexusvars:
            # will read EMG/model data only if necessary
            self.model = nexus_getdata.model_outputs()
            self.emg = nexus_getdata.nexus_emg(emg_remapping=self.emg_mapping, emg_auto_off=self.emg_auto_off)
            read_emg = False
            read_pig = False
            read_mlen = False
            self.emg_plot_chs = []
            self.emg_plot_pos = []
            self.model_plot_vars = []
            self.model_plot_pos = []
            for i, var in enumerate(self.nexusvars):
                if var == None:  # indicates empty subplot
                    pass
                elif var == 'modellegend':   # place legend on this subplot
                    self.model_legendpos = i
                elif var == 'emglegend':
                    self.emg_legendpos = i
                else:
                    if self.emg.is_logical_channel(var):
                        read_emg = True
                        self.emg_plot_chs.append(var)
                        self.emg_plot_pos.append(i)
                    elif self.model.is_pig_lowerbody_variable(var):
                        read_pig = True
                        self.model_plot_vars.append(var)
                        self.model_plot_pos.append(i)
                    elif self.model.is_mlen_variable(var):
                        read_mlen = True
                        self.model_plot_vars.append(var)
                        self.model_plot_pos.append(i)
                    else:
                        error_exit('Unknown variable: ' + var)
            if read_emg:
                self.emg.read(self.vicon)
            if read_pig:
                self.model.read_pig_lowerbody(self.vicon, self.pig_normaldata_path)
            if read_mlen:
                self.model.read_musclelen(self.vicon, self.mlen_normaldata_path)

    def set_fig_title(self, title):
        if self.fig:
            plt.figure(self.fig.number) 
            plt.suptitle(title, fontsize=12, fontweight="bold")


    def plot_trial(self, plotheightratios=None, maintitle=None, maintitleprefix='',
                 onesided_kinematics=False, model_linestyle='-', emg_tracecolor='black'):
        """ Plot active trial (must call open_trial first). If a plot is already 
        active, the new trial will be overlaid on the previous one.
        Parameters:
        maintitle plot title; leave unspecified for automatic title (can also then
        supply maintitleprefix)
        """        

        if not self.trialname:
            raise Exception('No trial loaded')
       
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
        
        # handles model output vars (Plug-in Gait, muscle length, etc.)

        if self.model_plot_vars:
            for k, var in enumerate(self.model_plot_vars):
                ax = plt.subplot(self.gs[self.model_plot_pos[k]])
                # get normalized variable name
                varname_full = self.model.norm_varname(var, self.side)
                # plot two-sided kinematics if applicable
                if not self.model.is_kinetic_var(var) and not onesided_kinematics:
                    varname_r = self.model.norm_varname(var, 'R')
                    varname_l = self.model.norm_varname(var, 'L')
                    plt.plot(tn, self.model.Vars[varname_r], self.tracecolor_r, linestyle=model_linestyle, label=self.trialname)
                    plt.plot(tn, self.model.Vars[varname_l], self.tracecolor_l, linestyle=model_linestyle, label=self.trialname)
                else:
                    plt.plot(tn, self.model.Vars[varname_full], tracecolor, linestyle=model_linestyle, label=self.trialname)
                # plot normal data, if available
                if self.model.normaldata(var):
                    nor = np.array(self.model.normaldata(var))[:,0]
                    nstd = np.array(self.model.normaldata(var))[:,1]
                    plt.fill_between(tn_2, nor-nstd, nor+nstd, color=self.normals_color, alpha=self.normals_alpha)
                title = self.model.description(var)
                ylabel = self.model.ylabel(varname_full)
                plt.title(title, fontsize=self.fsize_labels)
                plt.xlabel(self.xlabel,fontsize=self.fsize_labels)
                plt.ylabel(ylabel, fontsize=self.fsize_labels)
                # variable-specific scales
                #plt.ylim(kinematicsymin[k], kinematicsymax[k])
                ylim_default= ax.get_ylim()
                # include zero line and extend y scale a bit for kin* variables
                plt.axhline(0, color='black')  # zero line
                if self.model.is_pig_lowerbody_variable(var):
                    if ylim_default[0] == 0:
                        plt.ylim(-10, ylim_default[1])
                    if ylim_default[1] == 0:
                        plt.ylim(ylim_default[0], 10)
                # expand the default scale a bit for muscle length variables
                if self.model.is_mlen_variable(var):
                    plt.ylim(ylim_default[0]-10, ylim_default[1]+10)
                plt.locator_params(axis = 'y', nbins = 6)  # reduce number of y tick marks
                # add arrows indicating toe off times
                if self.add_toeoff_markers:
                    ymin = ax.get_ylim()[0]
                    ymax = ax.get_ylim()[1]
                    xmin = ax.get_xlim()[0]
                    xmax = ax.get_xlim()[1]
                    ltoeoff = self.vgc.ltoe1_norm
                    rtoeoff = self.vgc.rtoe1_norm
                    arrlen = (ymax-ymin) * self.toeoff_rel_len
                    # these are related to plot height/width, to avoid aspect ratio effects
                    hdlength = arrlen * .33
                    hdwidth = (xmax-xmin) / 50.
                    if not self.model.is_kinetic_var(var) and not onesided_kinematics:
                        plt.arrow(ltoeoff, ymin, 0, arrlen, color=self.tracecolor_l, 
                                  head_length=hdlength, head_width=hdwidth)
                        plt.arrow(rtoeoff, ymin, 0, arrlen, color=self.tracecolor_r, 
                                  head_length=hdlength, head_width=hdwidth)
                    else:  # single trace was plotted - only plot one-sided toeoff
                        if self.side == 'L':
                            toeoff = ltoeoff
                            arrowcolor = self.tracecolor_l
                        else:
                            toeoff = rtoeoff
                            arrowcolor = self.tracecolor_r
                        plt.arrow(toeoff, ymin, 0, arrlen, color=arrowcolor, 
                          head_length=hdlength, head_width=hdwidth)
        
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
                        plt.plot(tn_emg, 1e3*self.emg.filt(emgdata[thisch], self.emg_passband), emg_tracecolor, alpha=self.emg_alpha, label=self.trialname)
                    else:
                        plt.plot(tn_emg, 1e3*emgdata[thisch], emg_tracecolor, alpha=self.emg_alpha, label=self.trialname)
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
                    ltoeoff = self.vgc.ltoe1_norm
                    rtoeoff = self.vgc.rtoe1_norm
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
            self.legendnames.append(self.trialname)            
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
                pdf_name = self.sessionpath + pdf_prefix + self.trialname + '.pdf'
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
            
    
   
   
