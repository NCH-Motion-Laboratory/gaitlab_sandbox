# -*- coding: utf-8 -*-
"""
Created on Mon Nov 02 10:57:31 2015

Read video using cv2, display frames using matplotlib
"""

import numpy as np
import sys
import matplotlib.pyplot as plt
import cv2

vidfile = "C://Users//HUS20664877//Desktop//Vicon//vicon_data//test//Verrokki6v_IN//2015_10_22_girl6v_IN//2015_10_22_girl6v_IN57.59875835.20151022144140.avi"
cap = cv2.VideoCapture(vidfile)

plt.figure()

frames = []

while True:
    ret, frame = cap.read()
    if ret and cap.isOpened():
        plt.imshow(frame)
        frames.append(frame)
    else:
        break

sys.exit()








while(cap.isOpened()):
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

