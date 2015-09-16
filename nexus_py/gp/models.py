# -*- coding: utf-8 -*-
"""

models.py - definitions for various models (PiG, muscle length, etc.)
Defines variable names, descriptions, etc.

@author: Jussi
"""


class model:
    """ A class for storing model variable data, e.g. Plug-in Gait. """    

    def __init__(self):
        self.read_vars = list()  # vars to be read from data
        self.read_strategy = None
        self.varnames = list()   # variable names
        self.varlabels = dict()  # descriptive label for each variable
        self.normaldata_map = dict()  # mapping from variable names to normaldata variables
        self.ylabels = dict()  # y axis labels for plotting the variables


    def list_with_side(self, vars):
        """ Prepend variables in vars with 'L' and 'R', creating a new list of
        variables. Many model variables share the same name, except for leading
        'L' or 'R' that indicates side, so this simplifies creation of variable
        names. """
        return ['L'+var for var in vars]+['R'+var for var in vars]

    def dict_with_side(self, dict, append_side=False):
        """ Prepend dict keys with 'R' or 'L'. If append_side,
        also append ' (R)' or ' (L)' to every entry. """
        di = {}
        if append_side:
            Rstr, Lstr = (' (R)',' (L)')
        else:
            Rstr, Lstr = ('', '')
        for key in dict:
            di['R'+key] = dict[key]+Rstr
            di['L'+key] = dict[key]+Lstr
        return di
#
# Plug-in Gait lowerbody
#
pig_lowerbody = model()

pig_lowerbody.read_vars = pig_lowerbody.list_with_side(['HipMoment',
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
      'FootProgressAngles'])
      
pig_lowerbody.varlabels = pig_lowerbody.dict_with_side({'AnkleAnglesX': 'Ankle dorsi/plant',
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
                         'PelvisAnglesZ': 'Pelvic rotation'}, append_side=True)
      
pig_lowerbody.normaldata_map = pig_lowerbody.dict_with_side({'AnkleAnglesX': 'DorsiPlanFlex',
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
             'PelvisAnglesZ': 'PelvicRotation'})

pig_lowerbody.ylabels = pig_lowerbody.dict_with_side({'AnkleAnglesX': 'Pla     ($^\\circ$)      Dor',
                         'AnkleAnglesZ': 'Ext     ($^\\circ$)      Int',
                         'AnkleMomentX': 'Int dors    Nm/kg    Int plan',
                         'AnklePowerZ': 'Abs    W/kg    Gen',
                         'FootProgressAnglesZ': 'Ext     ($^\\circ$)      Int',
                         'HipAnglesX': 'Ext     ($^\\circ$)      Flex',
                         'HipAnglesY': 'Abd     ($^\\circ$)      Add',
                         'HipAnglesZ': 'Ext     ($^\\circ$)      Int',
                         'HipMomentX': 'Int flex    Nm/kg    Int ext',
                         'HipMomentY': 'Int add    Nm/kg    Int abd',
                         'HipMomentZ': 'Int flex    Nm/kg    Int ext',
                         'HipPowerZ': 'Abs    W/kg    Gen',
                         'KneeAnglesX': 'Ext     ($^\\circ$)      Flex',
                         'KneeAnglesY': 'Val     ($^\\circ$)      Var',
                         'KneeAnglesZ': 'Ext     ($^\\circ$)      Int',
                         'KneeMomentX': 'Int flex    Nm/kg    Int ext',
                         'KneeMomentY': 'Int var    Nm/kg    Int valg',
                         'KneeMomentZ': 'Int flex    Nm/kg    Int ext',
                         'KneePowerZ': 'Abs    W/kg    Gen',
                         'PelvisAnglesX': 'Pst     ($^\\circ$)      Ant',
                         'PelvisAnglesY': 'Dwn     ($^\\circ$)      Up',
                         'PelvisAnglesZ': 'Bak     ($^\\circ$)      For'})

#
# Muscle length (MuscleLength.mod)
#




