# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 14:16:35 2015

@author: HUS20664877

btk experiments

need to get:
-forceplate data
-emg data
-foot strike/toeoff events
-model outputs (PiG, muscle length)

Open a trial from a c3d file. Get:
subject name
trial name
gait cycle info (?)
self.emg instance
self.model instance

"""

import nexus_getdata
import sys
# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")
import ViconNexus
                      
            
            


c3dfile = "C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/D0012_VS/2015_6_9_seur_VS/2015_6_9_seur_VS33.c3d"
vicon = ViconNexus.ViconNexus()



vgc1 = nexus_getdata.gaitcycle()
vgc1.read_c3d(c3dfile)

vgc2 = nexus_getdata.gaitcycle()
vgc2.read_nexus(vicon)



print vgc1.rfstrikes
print vgc2.rfstrikes

print vgc1.lfstrikes
print vgc2.lfstrikes
