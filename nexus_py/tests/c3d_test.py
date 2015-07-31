# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 14:16:35 2015

@author: HUS20664877

test nexusplotter c3d/btk functions

"""


import gait_getdata
import sys
# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")
import ViconNexus
                      
            



c3dfile = "C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/D0012_VS/2015_6_9_seur_VS/2015_6_9_seur_VS33.c3d"
vicon = ViconNexus.ViconNexus()


tfile = gait_getdata.trial(c3dfile)
tnexus = gait_getdata.trial(vicon)


sys.exit()

# gait cycle test - ok
vgc1 = gait_getdata.gaitcycle(c3dfile)

vgc2 = gait_getdata.gaitcycle(vicon)

print vgc1.rfstrikes
print vgc2.rfstrikes
print vgc1.lfstrikes
print vgc2.lfstrikes




sys.exit()



# emg test

emg2 = nexus_getdata.emg()
emg2.read_nexus(vicon)

emg1 = nexus_getdata.emg()
emg1.read_c3d(c3dfile)


plt.figure()
plt.plot(emg1.data_gc1l['Voltage.LTibA1'])
plt.plot(emg2.data_gc1l['Voltage.LTibA1'],'r')



