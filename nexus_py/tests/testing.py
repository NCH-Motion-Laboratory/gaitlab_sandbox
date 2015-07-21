# -*- coding: utf-8 -*-
"""
Created on Mon May 18 10:03:39 2015

testbench for various Nexus Python stuff

@author: HUS20664877
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
from scipy import signal
import psutil
from ConfigParser import SafeConfigParser
from nexus_plot import nexus_plotter

fs = 1000
ord = 4
lowp = 400
hip = 1
b, a = signal.butter(ord, 2./fs*np.array([hip, lowp]), 'bandpass')
w, h = signal.freqz(b, a, worN=8192)
f = w / np.pi * (fs / 2.)
plt.plot(f, 20 * np.log10(abs(h)))
#plt.xscale('log')
plt.title('Freq response at order ' + str(ord))
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [dB]')
plt.margins(0, 0.1)
plt.grid(which='both', axis='both')
plt.show()

sys.exit()


def koe():
    return (True, 'message')

nplotter = nexus_plotter([9,2])
#nplotter.configwindow()

sys.exit()


config = {}
config['sfrate'] = '1000'
config['name'] = "Jussi Nurminen"

inifile = open('nexusplotter_test.ini','wt')

parser = SafeConfigParser()
parser.add_section('NexusPlotter')
for key in config.keys():
    parser.set('NexusPlotter', key, config[key])
parser.write(inifile)
inifile.close()

inifile = open('nexusplotter_test.ini','rt')

parser2 = SafeConfigParser()
parser.read(inifile)
for key in config.keys():
    print(parser.get('NexusPlotter', key))

parser.get('p','pop')


sys.exit()






def nexus_pid():
    """ Tries to return the PID of the running Nexus process. """
    PROCNAME = "Nexus.exe"
    for proc in psutil.process_iter():
        try:
            if proc.name() == PROCNAME:
                return proc.pid
        except psutil.AccessDenied:
            pass
    return None


def plotspectrum(y, fs):
    f, Pxx_den = signal.welch(y, fs)
    plt.semilogy(f, Pxx_den)
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.show()
    




vicon = ViconNexus.ViconNexus()
emg = nexus_getdata.nexus_emg(emg_auto_off=False)

emg.read(vicon)

plotspectrum(emg.data['Voltage.RSol'],emg.sfrate)



