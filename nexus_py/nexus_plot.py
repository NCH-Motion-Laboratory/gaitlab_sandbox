# -*- coding: utf-8 -*-
"""

Generic Nexus plotter. Plots Plug-in Gait variables and EMG from a running
Vicon Nexus application, using matplotlib.



Rules:

-channel type is autodetected by looking into the known names
-can specify 'None' to leave corresponding subplot empty
-can specify 'piglegend' or 'emglegend' to get a legend on a particular subplot
-variables always normalized to gait cycle
-always plot PiG normal data if available
-kinetics always plotted for one side only
-vars can be specified without leading 'Norm'+side prefix (e.g. 'HipMomentX'
 instead of 'NormRHipMomentX'


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

class nexus_plotter():
    """ Create a plot of Nexus variables. Can overlay data from several trials. """

    def configwindow(self):
        """ Opens a Tk window for configuring NexusPlotter. """
        
        def saver_callback(window, list):
            """ Signaler callback for root window; modify list to indicate that 
            user pressed save, and destroy the window. """
            list.append(1)
            window.destroy()
        
        master = Tk()
        emg_auto_off = IntVar()
        emg_lowpass = StringVar()
        emg_highpass = StringVar()
        gcdpath = StringVar()
        save = []   
        Label(master, text="Select options for Nexus plotter:").grid(row=0, columnspan=2, pady=4)
        emg_auto_off.set(1)
        Checkbutton(master, text="Autodetect disconnected EMG electrodes", variable=emg_auto_off).grid(row=1, columnspan=2, sticky=W)
        Label(master, text='EMG lowpass (Hz):').grid(row=2, column=0)
        emg_lowpass.set(self.config['emg_lowpass'])
        Spinbox(master, from_=self.EMG_LOWPASS_MIN, to=self.EMG_LOWPASS_MAX, textvariable=emg_lowpass).grid(row=2, column=1, pady=4)
        Label(master, text='EMG highpass (Hz):').grid(row=3, column=0)
        emg_highpass.set(self.config['emg_highpass'])
        sp2=Spinbox(master, from_=self.EMG_HIGHPASS_MIN, to=self.EMG_HIGHPASS_MAX, textvariable=emg_highpass).grid(row=3, column=1, pady=4)
        Label(master, text='Location of PiG normal data (.gcd)').grid(row=4, column=0)
        gcdpath.set(self.config['pig_normaldata_path'])
        e = Entry(master, textvariable=gcdpath).grid(row=4, column=1)
        Button(master, text='Cancel', command=master.destroy).grid(row=5, column=0, pady=4)
        Button(master, text='Save config', command=lambda: saver_callback(master, save)).grid(row=5, column=1, pady=4)
        mainloop()  # Tk
        if not save:  # user hit Cancel
            return None
        else:
            # read vars, put into config dict and call write_config
            self.config['emg_lowpass'] = emg_lowpass.get()
            self.config['emg_highpass'] = emg_highpass.get()
            self.config['pig_normaldata_path'] = gcdpath.get()
            if emg_auto_off.get():
                self.config['emg_auto_off'] = 'True'
            else:
                self.config['emg_auto_off'] = 'False'
            #if not self.check_config():
            #    messagebox('Invalid configuration options specified!')
            #    self.configwindow()
            self.write_config()
            # If the new config is to be used immediately (configwindow() call is
            # followed by use of the class instance), we must call process_config().
            self.process_config()
    
    def default_config(self):
        """ Initialize user-configurable values to default. """
        self.config = {}
        self.config['emg_lowpass'] = '10'
        self.config['emg_highpass'] = '400'
        self.config['pig_normaldata_path'] = self.datadir + '/normal.gcd'
        self.config['emg_auto_off'] = 'True'
        
    def check_config(self):
        """ Validate config dict, useful before calling write_config() or process_config() """
        if not self.EMG_LOWPASS_MIN < int(self.config['emg_lowpass']) < self.EMG_LOWPASS_MAX:
            return False
        if not self.EMG_HIGHPASS_MIN < int(self.config['emg_highpass']) < self.EMG_HIGHPASS_MAX:
            return False
        if not self.config['emg_auto_off'] in ['True', 'False']:
            return False
        return True
        
    def process_config(self):
        """ Set class variables according to config. """
        self.emg_passband = [0,0]
        self.emg_passband[0] = int(self.config['emg_lowpass'])
        self.emg_passband[1] = int(self.config['emg_highpass'])
        pig_normaldata_path = self.config['pig_normaldata_path']
        if self.config['emg_auto_off'] == 'True':
            self.emg_auto_off = True
        else:
            self.emg_auto_off = False
                       
    def read_config(self):
        """ Read configuration from disk file. """
        parser = SafeConfigParser()
        parser.read(self.configfile)
        # read keys that are defined by default_config()
        for key in self.config.keys():
            try:
                self.config[key] = parser.get('NexusPlotter', key)
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                error_exit('Invalid configuration file')
        
    def write_config(self):
        """ Save current configuration to a disk file. """
        try:
            inifile = open(self.configfile, 'wt')
        except IOError:
            error_exit('Cannot open config file for writing: ', self.configfile)
        parser = SafeConfigParser()
        parser.add_section('NexusPlotter')
        for key in self.config.keys():
            parser.set('NexusPlotter', key, self.config[key])
        parser.write(inifile)
        inifile.close()

    def __init__(self, layout):
        # set paths
        pathprefix = 'c:/users/' + getpass.getuser()
        self.desktop = pathprefix + '/Desktop'
        self.configdir = self.desktop + '/NexusPlotter/Config'
        self.datadir = self.desktop + '/NexusPlotter/Data'
        self.configfile = self.configdir + '/NexusPlotter.ini'

        # some defaults for config file validation      
        self.EMG_LOWPASS_MIN = 0
        self.EMG_LOWPASS_MAX = 190
        self.EMG_HIGHPASS_MIN = 200
        self.EMG_HIGHPASS_MAX = 490
        
        # read .ini file if available
        self.default_config()
        if os.path.isfile(self.configfile):
            self.read_config()
        if self.check_config():
            self.process_config()
        else:
            error_exit('Invalid options specified in config file! Please fix or delete the file.')

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
        self.piglegendpos = None
        self.emglegendpos = None
        # used to collect trial names and styles for legend
        self.pigartists = []
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
        
    def get_emg_filter_description(self):
        """ Returns a string describing the filter applied to the EMG data """
        if not self.emg_passband:
            return "No EMG filtering"
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
        if not trialname_:
            error_exit('No trial loaded')
        self.sessionpath = trialname_[0]
        self.trialname = trialname_[1]
        self.subjectname = subjectnames[0]
        
        # update gait cycle information
        self.vgc = nexus_getdata.gaitcycle(self.vicon)
        
        # try to detect side (L/R) if not forced in arguments
        if not side:
            self.side = self.vgc.detect_side(self.vicon)
        else:
            self.side = side    
        
        if nexusvars:
            # will read EMG/PiG data only if necessary
            self.pig = nexus_getdata.pig_outputs()
            self.emg = nexus_getdata.nexus_emg(emg_remapping=self.emg_mapping)
            read_emg = False
            read_pig = False
            self.emg_plot_chs = []
            self.emg_plot_pos = []
            self.pig_plot_vars = []
            self.pig_plot_pos = []
            for i, var in enumerate(self.nexusvars):
                if var == None:  # indicates empty subplot
                    pass
                elif var == 'piglegend':   # place legend on this subplot
                    self.piglegendpos = i
                elif var == 'emglegend':
                    self.emglegendpos = i
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
                self.pig.read(self.vicon, 'PiGLB', self.pig_normaldata_path)


    def set_fig_title(self, title):
        if self.fig:
            plt.figure(self.fig.number) 
            plt.suptitle(title, fontsize=12, fontweight="bold")


    def plot_trial(self, plotheightratios=None, maintitle=None, maintitleprefix='',
                 onesided_kinematics=False, pig_linestyle='-', emg_tracecolor='black'):
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
        
        if self.pig_plot_vars:
            for k, var in enumerate(self.pig_plot_vars):
                ax = plt.subplot(self.gs[self.pig_plot_pos[k]])
                varname_full = 'Norm'+self.side+var
                # plot two-sided kinematics if applicable
                if not self.pig.is_kinetic_var(var) and not onesided_kinematics:
                    varname_r = 'Norm' + 'R' + var
                    varname_l = 'Norm' + 'L' + var
                    plt.plot(tn, self.pig.Vars[varname_r], self.tracecolor_r, linestyle=pig_linestyle, label=self.trialname)
                    plt.plot(tn, self.pig.Vars[varname_l], self.tracecolor_l, linestyle=pig_linestyle, label=self.trialname)
                else:
                    plt.plot(tn, self.pig.Vars[varname_full], tracecolor, linestyle=pig_linestyle, label=self.trialname)
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
                    if not self.pig.is_kinetic_var(var) and not onesided_kinematics:
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
                    emg_yscale = self.emg.yscale_gc1l
                elif side_this == 'R':
                    tn_emg = self.emg.tn_emg_r
                    emgdata = self.emg.logical_data_gc1r
                    emg_yscale = self.emg.yscale_gc1r
                else:
                    error_exit('Unexpected EMG channel name: ', thisch)
                ax = plt.subplot(self.gs[self.emg_plot_pos[k]])
                if emgdata[thisch] == 'EMG_DISCONNECTED':
                    if self.annotate_disconnected:
                        ax.annotate('disconnected', xy=(50,0), ha="center", va="center")   
                elif emgdata[thisch] == 'EMG_REUSED':
                        ax.annotate('reused', xy=(50,0), ha="center", va="center")
                else:
                    plt.plot(tn_emg, 1e3*self.emg.filter(emgdata[thisch], self.emg_passband), emg_tracecolor, alpha=self.emg_alpha, label=self.trialname)
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
        if self.piglegendpos or self.emglegendpos:
            self.legendnames.append(self.trialname)            
        if self.piglegendpos:
            self.pigartists.append(plt.Line2D((0,1),(0,0), color=self.tracecolor_r, linestyle=pig_linestyle))
            ax = plt.subplot(self.gs[self.piglegendpos])
            plt.axis('off')
            nothing = [plt.Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)]
            legtitle = ['Kinematics/kinetics traces:']
            ax.legend(nothing+self.pigartists, legtitle+self.legendnames, prop={'size':self.fsize_labels}, loc='upper center')
        if self.emglegendpos:
            self.emgartists.append(plt.Line2D((0,1),(0,0), color=emg_tracecolor))
            ax = plt.subplot(self.gs[self.emglegendpos])
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
            
    
   
   
