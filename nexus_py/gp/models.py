# -*- coding: utf-8 -*-
"""

models.py - definitions for various models related to gait analysis
(PiG, muscle length, etc.)

@author: Jussi
"""


class model:
    """ A class for storing model variable data, e.g. Plug-in Gait. """    

    def __init__(self):
        self.read_vars = list()  # vars to be read from data
        self.varnames = list()   # variable names
        self.varlabels = dict()  # descriptive label for each variable
        self.normaldata_map = dict()  # mapping from variable names to normaldata variables
        self.ylabels = dict()  # y axis labels for plotting the variables

    def vars_with_side(self, vars):
        """ Prepend variables in vars with 'L' and 'R', creating a new list of
        variables. Many model variables share the same name, except for leading
        'L' or 'R' that indicates side, so this simplifies creation of variable
        names. """
        return ['L'+var for var in vars]+['R'+var for var in vars]


#
# Plug-in Gait lowerbody
#
pig_lowerbody = model()

pig_lowerbody.read_vars = pig.vars_with_side['HipMoment',
      'KneeMoment',
      'AnkleMoment',
      'HipPower',
      'KneePower',
      'AnklePower',
      'HipMoment',
      'KneeMoment',
      'AnkleMoment',
      'HipPower',
      'KneePower',
      'AnklePower',
      'HipAngles',
      'KneeAngles',
      'AbsAnkleAngle',
      'AnkleAngles',
      'PelvisAngles',
      'FootProgressAngles',
      'HipAngles',
      'KneeAngles',
      'AbsAnkleAngle',
      'AnkleAngles',
      'PelvisAngles',
      'FootProgressAngles']
      
pig_lowerbody.varlabels = {'AnkleAnglesX': 'Ankle dorsi/plant',
                         'AnkleAnglesZ': 'Ankle rotation',
                         'AnkleMomentX': 'Ankle dors/plan moment',
                         'AnklePowerZ': 'Ankle power',
                         'FootProgressAnglesZ': 'Foot progress angles',
                         'HipAnglesX': 'Hip flexion',
                         'HipAnglesY': 'Hip adduction',
                         'HipAnglesZ': 'Hip rotation',
                         'HipMomentX': 'Hip flex/ext moment',
                         'HipMomentY': 'Hip ab/add moment',
                         'HipMomentZ': 'Hip rotation moment',
                         'HipPowerZ': 'Hip power',
                         'KneeAnglesX': 'Knee flexion',
                         'KneeAnglesY': 'Knee adduction',
                         'KneeAnglesZ': 'Knee rotation',
                         'KneeMomentX': 'Knee flex/ext moment',
                         'KneeMomentY': 'Knee ab/add moment',
                         'KneeMomentZ': 'Knee rotation moment',
                         'KneePowerZ': 'Knee power',
                         'PelvisAnglesX': 'Pelvic tilt',
                         'PelvisAnglesY': 'Pelvic obliquity',
                         'PelvisAnglesZ': 'Pelvic rotation'}
      
pig_lowerbody_normaldata_map = {'AnkleAnglesX': 'DorsiPlanFlex',
             'AnkleAnglesZ': 'FootRotation',
             'AnkleMomentX': 'DorsiPlanFlexMoment',
             'AnklePowerZ': 'AnklePower',
             'FootProgressAnglesZ': 'FootProgression',
             'HipAnglesX': 'HipFlexExt',
             'HipAnglesY': 'HipAbAdduct',
             'HipAnglesZ': 'HipRotation',
             'HipMomentX': 'HipFlexExtMoment',
             'HipMomentY': 'HipAbAdductMoment',
             'HipMomentZ': 'HipRotationMoment',
             'HipPowerZ': 'HipPower',
             'KneeAnglesX': 'KneeFlexExt',
             'KneeAnglesY': 'KneeValgVar',
             'KneeAnglesZ': 'KneeRotation',
             'KneeMomentX': 'KneeFlexExtMoment',
             'KneeMomentY': 'KneeValgVarMoment',
             'KneeMomentZ': 'KneeRotationMoment',
             'KneePowerZ': 'KneePower',
             'PelvisAnglesX': 'PelvicTilt',
             'PelvisAnglesY': 'PelvicObliquity',
             'PelvisAnglesZ': 'PelvicRotation'}







pig = model()
pig.read_vars = pig.vars_with_side(pig_lowerbody_read_vars)
pig.varlabels = 





    


pig_lowerbody_read_vars = ['HipMoment',
      'KneeMoment',
      'AnkleMoment',
      'HipPower',
      'KneePower',
      'AnklePower',
      'HipMoment',
      'KneeMoment',
      'AnkleMoment',
      'HipPower',
      'KneePower',
      'AnklePower',
      'HipAngles',
      'KneeAngles',
      'AbsAnkleAngle',
      'AnkleAngles',
      'PelvisAngles',
      'FootProgressAngles',
      'HipAngles',
      'KneeAngles',
      'AbsAnkleAngle',
      'AnkleAngles',
      'PelvisAngles',
      'FootProgressAngles']
    
        
    
        
        


pig = model()
pig.n = 1
vs = pig.vars_with_side(['xxx','yyy'])    




