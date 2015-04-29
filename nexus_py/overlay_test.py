# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 15:48:51 2015

@author: HUS20664877
"""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

d1 = [1,2,4,5]
d2 = [6,3,2,5]

gs = gridspec.GridSpec(2,2)

fig1=plt.figure()

ax = plt.subplot(gs[0])
plt.plot(d1)
plt.subplot(gs[1])
plt.plot(d2)
    
gs2 = gridspec.GridSpec(2,2)
#plt.figure(fig1)
plt.subplot(gs2[0])
plt.plot(d2)
