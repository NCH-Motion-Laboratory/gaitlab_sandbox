# -*- coding: utf-8 -*-
"""

models.py - definitions for various models (PiG, muscle length, etc.)
Defines variable names, descriptions, etc.
For a new model, create a model() instance and fill the 

@author: Jussi


-model defs in models.py (instances of model class)
    -read and output variable defs
    -read method?
-create list of all model defs (in models.py)


"""


import numpy as np
import getdata
import btk


allmodels = []



class model:
    """ A class for storing model variable data, e.g. Plug-in Gait. """    

    def __init__(self):
        self.read_vars = list()  # vars to be read from data
        # How to read multidimensional variables: 'split_xyz' splits each 
        # variable into x,y,z components; or give a number to read the 
        # corresponding dimension only (e.g. 0=first dim)
        self.components = None  # which components to pick from read variables
        self.desc = ''  # description of model
        self.varnames = list()   # resulting variable names
        self.varlabels = dict()  # descriptive label for each variable
        self.normaldata_map = dict()  # mapping from variable names to .gcd normaldata variables (optional)
        self.ylabels = dict()  # y axis labels for plotting the variables (optional)
        
    def read_raw(self, source, components):
        """ Read model variables.
        components will pick the corresponding components from multidim arrays
        (zero is first component).
        'split_xyz' splits 3-d arrays into separate x,y,z variables. """
        if getdata.is_vicon_instance(source):
            vicon = source
            SubjectName = vicon.GetSubjectNames()[0]
            for Var in varlist:
                NumVals,BoolVals = vicon.GetModelOutput(SubjectName, Var)
                if not NumVals:
                    raise getdata.GaitDataError('Cannot read model variable: '+Var+
                    '. \nMake sure that the appropriate model has been executed.')
                # remove singleton dimensions
                self.Vars[Var] = np.squeeze(np.array(NumVals))
        elif getdata.is_c3dfile(source):
            c3dfile = source
            reader = btk.btkAcquisitionFileReader()
            reader.SetFilename(c3dfile)
            reader.Update()
            acq = reader.GetOutput()
            for Var in varlist:
                try:
                    self.Vars[Var] = np.transpose(np.squeeze(acq.GetPoint(Var).GetValues()))
                except RuntimeError:
                    raise getdata.GaitDataError('Cannot find model variable: ', Var)
        else:
            raise getdata.GaitDataError('Invalid data source')
        # postprocessing
        for Var in varlist:
                if Var.find('Moment') > 0:
                    # moment variables have to be divided by 1000 -
                    # apparently stored in Newton-millimeters
                    self.Vars[Var] /= 1000.
                getdata.debug_print('read_raw:', Var, 'has shape', self.Vars[Var].shape)
                if components == 'split_xyz':
                    if self.Vars[Var].shape[0] == 3:
                        # split 3-d arrays into x,y,z variables
                        self.Vars[Var+'X'] = self.Vars[Var][0,:]
                        self.Vars[Var+'Y'] = self.Vars[Var][1,:]
                        self.Vars[Var+'Z'] = self.Vars[Var][2,:]
                    else:
                        raise getdata.GaitDataError('XYZ split requested but array is not 3-d')
                elif components:
                    self.Vars[Var] = self.Vars[Var][components,:]

    def list_with_side(self, vars):
        """ Prepend variables in vars with 'L' and 'R', creating a new list of
        variables. Many model variables share the same name, except for leading
        'L' or 'R' that indicates side, so this simplifies creation of variable
        names. """
        return ['L'+var for var in vars]+['R'+var for var in vars]

    def dict_with_side(self, dict0, append_side=False):
        """ Prepend dict0 keys with 'R' or 'L'. If append_side,
        also append corresponding ' (R)' or ' (L)' to every dict value. """
        di = {}
        if append_side:
            Rstr, Lstr = (' (R)',' (L)')
        else:
            Rstr, Lstr = ('', '')
        for key in dict0:
            di['R'+key] = dict0[key]+Rstr
            di['L'+key] = dict0[key]+Lstr
        return di
#
# Plug-in Gait lowerbody
#
pig_lowerbody = model()

pig_lowerbody.desc = 'Plug-in Gait lower body'

pig_lowerbody.components = 'split_xyz'

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

pig_lowerbody.varnames = pig_lowerbody.varlabels.keys()
      
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

allmodels.append(pig_lowerbody)



#
# Muscle length (MuscleLength.mod)
#

musclelen = model()

musclelen.components = 0

musclelen.desc = 'Muscle length (MuscleLength.mod)'

musclelen.read_vars = ['LGMedAntLength',
                     'RGMedAntLength',
                     'LGMedMidLength',
                     'RGMedMidLength',
                     'LGMedPosLength',
                     'RGMedPosLength',
                     'LGMinAntLength',
                     'RGMinAntLength',
                     'LGMinMidLength',
                     'RGMinMidLength',
                     'LGMinPosLength',
                     'RGMinPosLength',
                     'LSeMeLength',
                     'RSeMeLength',
                     'LSeTeLength',
                     'RSeTeLength',
                     'LBiFLLength',
                     'RBiFLLength',
                     'LBiFSLength',
                     'RBiFSLength',
                     'LSartLength',
                     'RSartLength',
                     'LAdLoLength',
                     'RAdLoLength',
                     'LAdBrLength',
                     'RAdBrLength',
                     'LAdMaSupLength',
                     'RAdMaSupLength',
                     'LAdMaMidLength',
                     'RAdMaMidLength',
                     'LAdMaInfLength',
                     'RAdMaInfLength',
                     'LPectLength',
                     'RPectLength',
                     'LGracLength',
                     'RGracLength',
                     'LGlMaSupLength',
                     'RGlMaSupLength',
                     'LGlMaMidLength',
                     'RGlMaMidLength',
                     'LGlMaInfLength',
                     'RGlMaInfLength',
                     'LIliaLength',
                     'RIliaLength',
                     'LPsoaLength',
                     'RPsoaLength',
                     'LQuFeLength',
                     'RQuFeLength',
                     'LGemeLength',
                     'RGemeLength',
                     'LPeriLength',
                     'RPeriLength',
                     'LReFeLength',
                     'RReFeLength',
                     'LVaMeLength',
                     'RVaMeLength',
                     'LVaInLength',
                     'RVaInLength',
                     'LVaLaLength',
                     'RVaLaLength',
                     'LMeGaLength',
                     'RMeGaLength',
                     'LLaGaLength',
                     'RLaGaLength',
                     'LSoleLength',
                     'RSoleLength',
                     'LTiPoLength',
                     'RTiPoLength',
                     'LFlDLLength',
                     'RFlDLLength',
                     'LFlHLLength',
                     'RFlHLLength',
                     'LTiAnLength',
                     'RTiAnLength',
                     'LPeBrLength',
                     'RPeBrLength',
                     'LPELOLength',
                     'RPELOLength',
                     'LPeTeLength',
                     'RPeTeLength',
                     'LExDLLength',
                     'RExDLLength',
                     'LExHLLength',
                     'RExHLLength']

musclelen.varlabels = musclelen.dict_with_side({'AdBrLength': 'AdBrLength',
                       'AdLoLength': 'AdLoLength',
                        'AdMaInfLength': 'AdMaInfLength',
                        'AdMaMidLength': 'AdMaMidLength',
                        'AdMaSupLength': 'AdMaSupLength',
                        'BiFLLength': 'Biceps femoris length',
                        'BiFSLength': 'BiFSLength',
                        'ExDLLength': 'ExDLLength',
                        'ExHLLength': 'ExHLLength',
                        'FlDLLength': 'FlDLLength',
                        'FlHLLength': 'FlHLLength',
                        'GMedAntLength': 'GMedAntLength',
                        'GMedMidLength': 'GMedMidLength',
                        'GMedPosLength': 'GMedPosLength',
                        'GMinAntLength': 'GMinAntLength',
                        'GMinMidLength': 'GMinMidLength',
                        'GMinPosLength': 'GMinPosLength',
                        'GemeLength': 'GemeLength',
                        'GlMaInfLength': 'GlMaInfLength',
                        'GlMaMidLength': 'GlMaMidLength',
                        'GlMaSupLength': 'GlMaSupLength',
                        'GracLength': 'Gracilis length',
                        'IliaLength': 'IliaLength',
                        'LaGaLength': 'Lateral gastrocnemius length',
                        'MeGaLength': 'Medial gastrocnemius length',
                        'PELOLength': 'PELOLength',
                        'PeBrLength': 'PeBrLength',
                        'PeTeLength': 'PeTeLength',
                        'PectLength': 'PectLength',
                        'PeriLength': 'PeriLength',
                        'PsoaLength': 'Psoas length',
                        'QuFeLength': 'QuFeLength',
                        'ReFeLength': 'Rectus femoris length',
                        'SartLength': 'SartLength',
                        'SeMeLength': 'Semimembranosus length',
                        'SeTeLength': 'Semitendinosus length',
                        'SoleLength': 'Soleus length',
                        'TiAnLength': 'Tibialis anterior length',
                        'TiPoLength': 'TiPoLength',
                        'VaInLength': 'VaInLength',
                        'VaLaLength': 'VaLaLength',
                        'VaMeLength': 'VaMeLength'}, append_side=True)
                       
allmodels.append(musclelen)                       



