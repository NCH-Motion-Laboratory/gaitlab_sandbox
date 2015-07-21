# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 14:16:35 2015

@author: HUS20664877

btk tests

"""

import nexus_getdata
import btk                      
import numpy as np
import nexus_getdata            
import matplotlib.pyplot as plt            
            
c3dfile = "C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/D0012_VS/2015_6_9_seur_VS/2015_6_9_seur_VS33.c3d"


reader = btk.btkAcquisitionFileReader()
reader.SetFilename(c3dfile)  # check existence?
reader.Update()
acq = reader.GetOutput()
samplesperframe = acq.GetNumberAnalogSamplePerFrame()
sfrate = acq.GetAnalogFrequency()
                
data = {}        
for i in btk.Iterate(acq.GetAnalogs()):
    print(i.GetLabel(),i.GetUnit())
    if i.GetDescription().find('Force.') >= 0 and i.GetUnit() == 'N':
        pass
#        data[elname] = np.squeeze(i.GetValues())  # rm singleton dimension        

sys.exit()

plt.figure()
plt.plot(data['Voltage.LTibA1'])

vgc1 = nexus_getdata.gaitcycle()
vgc1.read_c3d(c3dfile)








