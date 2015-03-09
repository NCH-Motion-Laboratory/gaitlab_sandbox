# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 14:34:36 2015

@author: Vicon123

Python plotting tests.
matplotlib.pyplot provides a Matlab-like interface.

"""

import matplotlib.pyplot as plt
import numpy as np

# time range
t=np.arange(0,.5,.002)
plt.figure(1)
# create subplots
plt.subplot(211)
# plt.plot returns line2d instances
line1,line2=plt.plot(t,t**2,t,t**3)
plt.title('first subplot')
# modify properties
plt.setp(line1,color='k',linewidth=2.0)
plt.setp(line2,color='g',linewidth=2.0)
# another subplot
plt.subplot(212)
line3,line4=plt.plot(t,t**5,t,t**4)
plt.title('second subplot')
plt.xlabel('t axis')
plt.ylabel('y axis')
plt.show()
