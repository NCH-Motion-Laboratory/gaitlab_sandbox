# -*- coding: utf-8 -*-
"""
Created on Fri Jul 03 12:20:36 2015

Handles configuration for Gaitplotter.

@author: Jussi
"""


from Tkinter import *
import nexus_getdata
from nexus_getdata import error_exit, messagebox
import sys
# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")
import os
import ConfigParser
from ConfigParser import SafeConfigParser



class Config():
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
        self.emg_names = nexus_getdata.emg().ch_names
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
            newconfig = Config(self.appdir)
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
