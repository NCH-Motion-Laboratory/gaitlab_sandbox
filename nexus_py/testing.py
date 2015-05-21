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



