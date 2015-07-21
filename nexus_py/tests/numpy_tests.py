# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 10:07:08 2015

numpy tests
"""

# make it behave like 3.x
from __future__ import division, print_function

import numpy as np

# make 1-dim array from list
a=np.array([1,2,3,4,5])
print(a.dtype)  # int32
ad=a/2  # float division by default (3.x behavior)
print(ad.dtype)  # float64

# array slicing (works identically to strings)
print(a[0])  # 1
print(a[4])  # 5
#print(a[5])  # error
# beginning always included, end always excluded
print(a[0:4]) # [1,2,3] (slicing excludes last element)
print(a[1:])  # 2 to 5
print(a[:5])  # 1 to 5
print(a[0:5:2])  # step of 2: [1 3 5]

np.arange(1,100)  # 1 to 99
np.arange(1,100,2)  # 1,3,5...
np.arange(1,2,.1)  # better to use linspace (inconsistent results?)
np.linspace(0,1)  # 50 values, 0 to 1 inclusive
np.linspace(0,1,1000)  # 1k values

# 2-dim array from list
A=np.array([[1,2,3,4,5],[6,7,8,9,10]])
A.shape  # (2,5)
A[1]    # [6,7,8,9,10]
A[1,:]  # ditto
A[1,1]  # 7
A[1][1]  # 7

