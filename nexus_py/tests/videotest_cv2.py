# -*- coding: utf-8 -*-
"""
Created on Mon Nov 02 10:57:31 2015

Read video using cv2, display frames using matplotlib
"""

from __future__ import print_function
import numpy as np
import sys
import matplotlib.pyplot as plt
import cv2

# laptop
if os.getcwd().find('HUS2066'):
    vidpath = "C://Users//HUS20664877//Desktop//Vicon//vicon_data//test//Verrokki6v_IN//2015_10_22_girl6v_IN//"
else:
    vidpath = "C://Users//Vicon123//Desktop//"
vidfile = vidpath + "2015_10_22_girl6v_IN57.59875835.20151022144140.avi"
cap = cv2.VideoCapture(vidfile)
frames = []
ret = True
if cap.isOpened():
    while True:
        ret, frame = cap.read()
        if ret:        
            frames.append(frame)
        else:
            break
nframes = len(frames)
print('read',nframes,'frames')

fig, ax = plt.subplots()
fig.canvas.draw()
im = plt.imshow(frames[0])

for fr in frames:
    im.set_data(fr)
    #ax.draw_artist(ax.patch)
    ax.draw_artist(im)
    fig.canvas.update()
    fig.canvas.flush_events()
    
    
    
    

    
