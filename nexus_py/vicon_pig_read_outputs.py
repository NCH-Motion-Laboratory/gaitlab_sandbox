from __future__ import division, print_function
"""
Created on Mon Mar 16 16:09:13 2015

Read and normalize PiG model output variables into a dict.
@author: Jussi
"""

import sys
import numpy as np

# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")

def ReadNormalizedPiGVars(vicon, VarList):
  
    """ Reads given PiG output variables into the given dict. Variables are
    also normalized into the gait cycle. """

    SubjectName = vicon.GetSubjectNames()[0]
    
    # figure out gait cycle
    # frames where foot strikes occur (1-frame discrepancies with Nexus?)
    LFStrike = vicon.GetEvents(SubjectName, "Left", "Foot Strike")[0]
    RFStrike = vicon.GetEvents(SubjectName, "Right", "Foot Strike")[0]
    # 2 strikes is one complete gait cycle, needed for analysis
    lenLFS = len(LFStrike)
    lenRFS = len(RFStrike)
    if lenLFS and lenRFS < 2:
        raise Exception("Could not detect complete L/R gait cycles")
    # extract times for 1st gait cycles, L and R
    LGC1Start=min(LFStrike[0:2])
    LGC1End=max(LFStrike[0:2])
    LGC1Len=LGC1End-LGC1Start
    RGC1Start=min(RFStrike[0:2])
    RGC1End=max(RFStrike[0:2])
    RGC1Len=RGC1End-RGC1Start
    
    # for interpolation of variables from gait cycle grid to 
    # normalized grid (0...100%)
    tn = np.linspace(0, 100, 101)
    LGC1t = np.linspace(0, 100, LGC1Len)
    RGC1t = np.linspace(0, 100, RGC1Len)
    
     # read all kinematics vars into dict and normalize into gait cycle 1
    VarDict = {}
    for Var in VarList:
        # not sure what the BoolVals are, discard for now
        NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
        VarDict[Var] = np.array(NumVals)
        # moment variables have to be divided by 1000 - not sure why    
        if Var.find('Moment') > 0:
            VarDict[Var] /= 1000.
        # pick non-normalized X,Y,Z components into separate vars
        VarDict[Var+'X'] = VarDict[Var][0,:]
        VarDict[Var+'Y'] = VarDict[Var][1,:]
        VarDict[Var+'Z'] = VarDict[Var][2,:]
        # normalize vars to gait cycle 1
        if Var[0] == 'R':  # right side variable
            GC1t = RGC1t
            tStart = RGC1Start
            tEnd = RGC1End
        else:  # left side variable
            GC1t = LGC1t
            tStart = LGC1Start
            tEnd = LGC1End
        # pick per-frame data for gait cycle 1
        VarGC1=VarDict[Var][:,tStart:tEnd]
        # interpolate all three components to gait cycle
        VarDict['Norm'+Var+'X'] = np.interp(tn, GC1t, VarGC1[0,:])
        VarDict['Norm'+Var+'Y'] = np.interp(tn, GC1t, VarGC1[1,:])
        VarDict['Norm'+Var+'Z'] = np.interp(tn, GC1t, VarGC1[2,:])
        
    return VarDict
