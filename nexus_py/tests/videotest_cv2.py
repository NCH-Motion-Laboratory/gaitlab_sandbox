# -*- coding: utf-8 -*-
"""
Created on Mon Nov 02 10:57:31 2015

Read video using cv2, display frames using matplotlib
"""

import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import matplotlib.animation as animation
import cv2

vidfile = "C://Users//HUS20664877//Desktop//Vicon//vicon_data//test//Verrokki6v_IN//2015_10_22_girl6v_IN//2015_10_22_girl6v_IN57.59875835.20151022144140.avi"
cap = cv2.VideoCapture(vidfile)


frames = []

while True:
    ret, frame = cap.read()
    if ret and cap.isOpened():
        frames.append(frame)
    else:
        break

fig = plt.figure()

im = plt.imshow(frames[0])

def animate(i):
    #for fr in frames:
    im.set_data(frames[i])
    return [im]

def init():
    im = plt.imshow(frames[0])
    return [im]

ani = animation.FuncAnimation(fig, animate, range(0,len(frames)), init_func=init, interval=25, blit=True)

plt.draw()

sys.exit()   
         
axprev = plt.axes([
0.7, 0.05, 0.1, 0.075])
axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
bnext = Button(axnext, 'Next')
bnext.on_clicked(playonce)
bprev = Button(axprev, 'Previous')
#bprev.on_clicked(callback.prev)

