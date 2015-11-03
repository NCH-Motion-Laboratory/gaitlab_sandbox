# -*- coding: utf-8 -*-
"""
Gaitplotter predefined plot layouts.

Created on Thu Aug 27 14:16:50 2015

@author: Jussi
"""

import gp.defs

# online kinematics plot
std_kinematics = [['PelvisAnglesX','PelvisAnglesY','PelvisAnglesZ'],
                  ['HipAnglesX','HipAnglesY','HipAnglesZ'],
                    ['KneeAnglesX','KneeAnglesY','KneeAnglesZ'],
                   ['AnkleAnglesX','FootProgressAnglesZ','AnkleAnglesZ']]

# online kinetics plot           
std_kinetics = [['HipMomentX','HipMomentY','HipMomentZ'],
             ['HipPowerZ','KneeMomentX','KneeMomentY'],
             ['KneeMomentZ','KneePowerZ','AnkleMomentX'],
             [None,None,'AnklePowerZ']]
             

# muscle lengths
std_musclelen = [['PsoaLength', 'GracLength', 'ReFeLength'],
            ['BiFLLength', 'SeTeLength', 'SeMeLength'],
            ['MeGaLength', 'LaGaLength', 'SoleLength']]

# EMG only
std_emg = [['RGlut','LGlut'],
              ['RHam','LHam'],
              ['RRec','LRec'],
              ['RVas','LVas'],
              ['RTibA','LTibA'],
              ['RPer','LPer'],
              ['RGas','LGas'],
              ['RSol','LSol']]

# kinetics + kinematics
std_kinall = std_kinematics + std_kinetics

# experimental video layout
std_kinall_video = [['PelvisAnglesX', 'PelvisAnglesY', 'PelvisAnglesZ', 'video:'+gp.defs.video_id_front, None],
 ['HipAnglesX', 'HipAnglesY', 'HipAnglesZ', None, None],
 ['KneeAnglesX', 'KneeAnglesY', 'KneeAnglesZ', None, None],
 ['AnkleAnglesX', 'FootProgressAnglesZ', 'AnkleAnglesZ', None, None],
 ['HipMomentX', 'HipMomentY', 'HipMomentZ', 'video:'+gp.defs.video_id_side, None],
 ['HipPowerZ', 'KneeMomentX', 'KneeMomentY', None, None],
 ['KneeMomentZ', 'KneePowerZ', 'AnkleMomentX', None, None],
 [None, None, 'AnklePowerZ', None]]


#std_kinall_video = 
# kin *overlay
# add legend to bottom row
overlay_kinall = list(std_kinall)
overlay_kinall.pop()
overlay_kinall.append(['modellegend',None,'AnklePowerZ'])
              
# EMG overlay - add legend
overlay_emg = list(std_emg)
overlay_emg.append(['emglegend',None])

# kinetics overlay - add legend
overlay_kinetics = list(std_kinetics)
overlay_kinetics.append(['modellegend',None,None])

# Kinetics-EMG. Will return EMG channels according to the given side
def kinetics_emg(side):
    return [['HipAnglesX','KneeAnglesX','AnkleAnglesX'],
            [side+'Ham', side+'Rec', side+'TibA'],
            [side+'Glut',side+'Vas',side+'Per'],
            ['HipMomentX','KneeMomentX','AnkleMomentX'],
            [side+'Rec',side+'Ham',side+'Gas'],
            [None,side+'Glut',side+'Sol'],
            [None,side+'Gas',None],
            ['HipPowerZ','KneePowerZ','AnklePowerZ']]

# Kinematics-only EMG. Will return EMG channels according to the given side
def kinematics_emg(side):
    return [['HipAnglesX','KneeAnglesX','AnkleAnglesX'],
            [side+'Ham', side+'Rec', side+'TibA'],
            [side+'Glut',side+'Vas',side+'Per'],
            [side+'Rec',side+'Ham',side+'Gas'],
            [None,side+'Glut',side+'Sol'],
            [None,side+'Gas',None]]
            


