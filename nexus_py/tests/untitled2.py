# -*- coding: utf-8 -*-
"""
Created on Mon May 18 10:38:28 2015

@author: HUS20664877
"""

from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

# Generate a test signal, a 2 Vrms sine wave at 1234 Hz, corrupted by
# 0.001 V**2/Hz of white noise sampled at 10 kHz.

fs = 10e3
N = 1e5
amp = 2*np.sqrt(2)
freq = 1234.0
noise_power = 0.001 * fs / 2
time = np.arange(N) / fs
x = amp*np.sin(2*np.pi*freq*time)
x += np.random.normal(scale=np.sqrt(noise_power), size=time.shape)



def filter(y, passband, sfrate):
    """ Bandpass filter given data y to passband, e.g. [1, 40].
    Passband is given in Hz. None for no filtering. """
    if passband == None:
        return y
    else:
        passbandn = 2 * np.array(passband) / sfrate
        b, a = signal.butter(4, passbandn, 'bandpass')
        yfilt = signal.filtfilt(b, a, y)        
        return yfilt

xfilt = filter(x, [1200,1300], fs)

plotspectrum(xfilt, fs)