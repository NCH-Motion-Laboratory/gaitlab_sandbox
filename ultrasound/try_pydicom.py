# -*- coding: utf-8 -*-
"""
Muscle thickness detection from ultrasound images. Steps:

-read .dcm ultrasound using pydicom
-threshold to get strongest features (muscle edges)
-apply median filter for cleanup
-apply Hough transform to get longest lines
-calculate distance between lines (?)

@author: jnu@iki.fi
"""




# %% init
import pydicom
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

fname = Path(r'I:\Ultraääni\H0105_MK\o_long.dcm')
dataset = pydicom.dcmread(fname)
# crop
img = dataset.pixel_array
img = img[50:600, 250:900]


# %% threshold
ret, img_tr = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
img_tr_blur = cv2.medianBlur(img_tr, 7)
img_edges = cv2.Canny(img_tr, 100, 200, 3)
lines = cv2.HoughLinesP(img_edges, rho=1, theta=np.pi/180, threshold=200, minLineLength=minLineLength, maxLineGap=maxLineGap)


plt.imshow(img, cmap=plt.cm.bone)
plt.show()
plt.imshow(img_tr, cmap=plt.cm.bone)
plt.show()
plt.imshow(img_tr_blur, cmap=plt.cm.bone)
plt.show()
plt.imshow(img_edges, cmap=plt.cm.binary)
plt.show()


# %% hough
minLineLength = 200
maxLineGap = 10
img_tr_ = cv2.cvtColor(img_tr_blur, cv2.COLOR_BGR2GRAY)
lines = cv2.HoughLinesP(img_tr_, rho=1, theta=np.pi/180, threshold=200, minLineLength=minLineLength, maxLineGap=maxLineGap)
print(lines)



# %%ksize = 19
img_ = cv2.GaussianBlur(img_tr, (ksize, ksize), 0)
img_edges = cv2.Canny(img_, 100, 200, 3)
plt.imshow(img, cmap=plt.cm.bone)
plt.show()
plt.imshow(img_tr, cmap=plt.cm.bone)
plt.show()
plt.imshow(img_edges, cmap=plt.cm.binary)
plt.show()



# %% hough
minLineLength = 250
maxLineGap = 40
lines = cv2.HoughLinesP(img_edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=minLineLength, maxLineGap=maxLineGap)
print(lines)