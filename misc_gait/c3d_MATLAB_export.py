"""
Read all the c3d files in a given folder, select relevant trials, and export
them to a MATLAB file.

Requires gaitutils Anaconda environment
"""

import os
import numpy as np
import scipy.io

import logging
import numpy as np
import scipy
import itertools
from collections import defaultdict

from gaitutils.stats import collect_trial_data
from gaitutils.envutils import GaitDataError
from gaitutils.config import cfg


DATA_FLDR = 'Z:/Misc/0_Mika/CP-projekti/HP/H0188_AJ/2022_06_20_seur_AJ/'
MODEL_VAR_NAMES = {'RAnkleAnglesX', 'LAnkleAnglesX',
                   'RKneeAnglesX', 'LKneeAnglesX',
                   'RNormalisedGRFZ', 'LNormalisedGRFZ',
                   'RAnkleMomentX', 'LAnkleMomentX',
                   'RAnklePowerZ', 'LAnklePowerZ',
                   'RKneeMomentX', 'LKneeMomentX',
                   'RKneePowerZ', 'LKneePowerZ',
                   'RSoleLength', 'LSoleLength',
                   'RMeGaLength', 'LMeGaLength'}

"""
Other model variables which were exported earlier
                   'RNormalisedGRFX', 'LNormalisedGRFX',
                   'RNormalisedGRFY', 'LNormalisedGRFY',
                   'RFootProgressAnglesZ', 'LFootProgressAnglesZ',
                   'RHipAnglesX', 'LHipAnglesX',
                   'RPelvisAnglesX', 'LPelvisAnglesX',
                   'RHipMomentX', 'LHipMomentX',
                   'RHipMomentY', 'LHipMomentY',
                   'RHipPowerZ', 'LHipPowerZ',
                   'RTiAnLength', 'LTiAnLength'
                   'RLaGaLength', 'LLaGaLength',
                   'RBiFLLength', 'LBiFLLength',
                   'RSeMeLength', 'LSeMeLength',
                   'RSeTeLength', 'LSeTeLength',
                   'RReFeLength', 'LReFeLength',
                   'RGracLength', 'LGracLength',
                   'RPsoaLength', 'LPsoaLength'
"""

# Compute derivatives (w.r.t. time) for this variables. Add the derivatives to the script's output.
MODEL_VAR_NAMES_TO_DIFF = {'RAnkleAnglesX', 'LAnkleAnglesX',
                           'RSoleLength', 'LSoleLength',
                           'RMeGaLength', 'LMeGaLength'}

EMG_VAR_NAMES = {'RTibA', 'LTibA',
                 'RGas', 'LGas',
                 'RSol', 'LSol'}

"""
Other EMG variables which were exported earlier
                 'RPer', 'LPer',
                 'RHam', 'LHam',
                 'RRec', 'LRec',
                 'RVas', 'LVas',
"""

VALID_ECLIPSE_TAGS = {'E2', 'E3', 'E4', 'T2', 'T3', 'T4'}
# VALID_ECLIPSE_TAGS = {'T1', 'E1'}
MODEL_OUT_FNAME = 'C:/Users/vicon123/model_exported.mat'
EMG_OUT_FNAME = 'C:/Users/vicon123/emg_exported.mat'


logger = logging.getLogger(__name__)


def main():
    model_res = defaultdict(lambda: np.zeros((101,0)))
    emg_res = defaultdict(lambda: np.zeros((1000,0)))
    model_delta_t = defaultdict(lambda: [])

    fnames = os.listdir(DATA_FLDR)
    for fname in fnames:
        if fname[-4:] == '.c3d':
            print('Reading file %s ...' % fname)
            full_name = DATA_FLDR + '/' + fname
            try:
                data, cycles = collect_trial_data(full_name, analog_envelope=False, force_collect_all_cycles=False, fp_cycles_only=True)

                for var_name in MODEL_VAR_NAMES:
                    try:
                        if cycles['model'][var_name][0].trial.eclipse_tag in VALID_ECLIPSE_TAGS:
                            # Append normalized trial data
                            model_res[var_name] = np.hstack((model_res[var_name], data['model'][var_name].T))

                            # Compute and append the new sample duration after normalization
                            for cyc in cycles['model'][var_name]:
                                delta_t = ((cyc.end - cyc.start) / cyc.trial.framerate) / data['model'][var_name].shape[1]
                                model_delta_t[var_name].append(delta_t)

                            print('\t ... added %i cycles for variable \'%s\' (eclipse label \'%s\')' % (data['model'][var_name].shape[0], var_name, cycles['model'][var_name][0].trial.eclipse_tag))
                        else:
                            print('\t ... no data imported for variable \'%s\' from file %s (wrong eclipse label)' % (var_name, fname))
                    except:
                        print('\t ... no data imported for variable \'%s\' from file %s' % (var_name, fname))

                for var_name in EMG_VAR_NAMES:
                    try:
                        if cycles['emg'][var_name][0].trial.eclipse_tag in VALID_ECLIPSE_TAGS:
                            emg_res[var_name] = np.hstack((emg_res[var_name], data['emg'][var_name].T))
                            print('\t ... added %i cycles for variable \'%s\' (eclipse label \'%s\')' % (data['emg'][var_name].shape[0], var_name, cycles['emg'][var_name][0].trial.eclipse_tag))
                        else:
                            print('\t ... no data imported for variable \'%s\' from file %s (wrong eclipse label)' % (var_name, fname))
                    except:
                        print('\t ... no data imported for variable \'%s\' from file %s' % (var_name, fname))
            except:
                print('\t ... failed!')


    # Compute the derivatives
    for var_name in MODEL_VAR_NAMES_TO_DIFF:
        model_res[var_name + '_dt'] = np.diff(model_res[var_name], axis=0) / np.array(model_delta_t[var_name])

    scipy.io.savemat(MODEL_OUT_FNAME, model_res)
    scipy.io.savemat(EMG_OUT_FNAME, emg_res)


if __name__ == '__main__':
    main()