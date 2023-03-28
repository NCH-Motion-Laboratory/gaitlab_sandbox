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

from gaitutils.stats import Trial, Gaitcycle
from gaitutils.stats import models, numutils
from gaitutils.envutils import GaitDataError
from gaitutils.config import cfg


DATA_FLDR = '/home/andrey/storage/Data/Gait_Lab/D0063_RR/2020_9_8_postOp1v_RR/'
MODEL_VAR_NAMES = {'RAnkleAnglesX', 'LAnkleAnglesX',
                   'RFootProgressAnglesZ', 'LFootProgressAnglesZ',
                   'RKneeAnglesX', 'LKneeAnglesX',
                   'RHipAnglesX', 'LHipAnglesX',
                   'RPelvisAnglesX', 'LPelvisAnglesX',
                   'RNormalisedGRFX', 'RNormalisedGRFX',
                   'RNormalisedGRFY', 'RNormalisedGRFY',
                   'RNormalisedGRFZ', 'RNormalisedGRFZ',
                   'RAnkleMomentX', 'LAnkleMomentX',
                   'RAnklePowerZ', 'LAnklePowerZ',
                   'RKneeMomentX', 'LKneeMomentX',
                   'RKneePowerZ', 'LKneePowerZ',
                   'RHipMomentX', 'LHipMomentX',
                   'RHipMomentY', 'LHipMomentY',
                   'RHipPowerZ', 'LHipPowerZ',
                   'RSoleLength', 'LSoleLength',
                   'RTiAnLength', 'LTiAnLength',
                   'RMeGaLength', 'LMeGaLength',
                   'RLaGaLength', 'LLaGaLength',
                   'RBiFLLength', 'LBiFLLength',
                   'RSeMeLength', 'LSeMeLength',
                   'RSeTeLength', 'LSeTeLength',
                   'RReFeLength', 'LReFeLength',
                   'RGracLength', 'LGracLength',
                   'RPsoaLength', 'LPsoaLength'}

# Compute derivatives (w.r.t. time) for this variables. Add the derivatives to the script's output.
MODEL_VAR_NAMES_TO_DIFF = {'RAnkleAnglesX', 'LAnkleAnglesX',
                           'RFootProgressAnglesZ', 'LFootProgressAnglesZ'}

EMG_VAR_NAMES = {'RHam', 'LHam',
                 'RRec', 'LRec',
                 'RVas', 'LVas',
                 'RTibA', 'LTibA',
                 'RPer', 'LPer',
                 'RGas', 'LGas',
                 'RSol', 'LSol'}
# VALID_ECLIPSE_TAGS = {'E2', 'E3', 'E4', 'T2', 'T3', 'T4'}
VALID_ECLIPSE_TAGS = {'T1', 'E1'}
MODEL_OUT_FNAME = '/tmp/model_exported.mat'
EMG_OUT_FNAME = '/tmp/emg_exported.mat'


logger = logging.getLogger(__name__)


def collect_trial_data(
    trials,
    collect_types=None,
    fp_cycles_only=None,
    collect_all_cycles=None,
    analog_len=None,
    analog_envelope=None,
):
    """Read model and analog cycle-normalized data from trials into numpy arrays.

    Parameters
    ----------
    trials : list | str | Trial
        List of c3d filenames or Trial instances to collect data from.
        Alternatively, a single filename or Trial instance.
    collect_types : list | None
        The types of data to collect. Currently supported types: 'model', 'emg'.
        If None, collect all supported types.
    fp_cycles_only : bool
        If True, collect data from forceplate cycles only. Kinetics model vars
        will always be collected from forceplate cycles only.
    collect_all_cycles: bool
        If true, return all the kinetic cycle, including non-forceplate. Overrides
        fp_cycles_only.
    analog_len : int
        Analog data length varies by gait cycle, so it will be resampled into
        grid length specified by analog_len (default 1000 samples)
    analog_envelope : bool
        Whether to compute envelope of analog data or return raw data. By
        default the data will be enveloped.

    Returns
    -------
    tuple
        Tuple of (data_all, cycles_all):

            data_all : dict
                Nested dict of the collected data. First key is the variable type,
                second key is the variable name. The values are NxT ndarrays of the data,
                where N is the number of collected curves and T is the dimensionality.
            cycles_all : dict
                Nested dict of the collected cycles. First key is the variable type,
                second key is the variable name. The values are Gaitcycle instances.

        Example: you can obtain all collected curves for LKneeAnglesX as
        data_all['model']['LKneeAnglesX']. This will be a Nx101 ndarray. You can obtain
        the corresponding gait cycles as cycles_all['model']['LKneeAnglesX']. This will
        be a length N list of Gaitcycles. You can use that to obtain various metadata, e.g.
        create a list of toeoff frames for each curve:
        [cyc.toeoffn for cyc in cycles_all['model']['LKneeAnglesX']]
    """

    data_all = dict()
    cycles_all = dict()

    if fp_cycles_only is None:
        fp_cycles_only = False

    if collect_types is None:
        collect_types = ['model', 'emg']

    if analog_len is None:
        analog_len = 1000  # reasonable default for analog data (?)

    if analog_envelope is None:
        analog_envelope = True

    if not trials:
        return None, None

    if not isinstance(trials, list):
        trials = [trials]

    if 'model' in collect_types:
        data_all['model'] = defaultdict(lambda: None)
        cycles_all['model'] = defaultdict(list)
        models_to_collect = models.models_all
    else:
        models_to_collect = list()

    if 'emg' in collect_types:
        data_all['emg'] = defaultdict(lambda: None)
        cycles_all['emg'] = defaultdict(list)
        emg_chs_to_collect = cfg.emg.channel_labels.keys()
    else:
        emg_chs_to_collect = list()

    trial_types = list()
    for trial_ in trials:
        # create Trial instance in case we got filenames as args
        trial = trial_ if isinstance(trial_, Trial) else Trial(trial_)
        logger.info(f'collecting data for {trial.trialname}')
        trial_types.append(trial.is_static)
        if any(trial_types) and not all(trial_types):
            raise GaitDataError('Cannot mix dynamic and static trials')

        cycles = [None] if trial.is_static else trial.cycles

        for cycle in cycles:

            # collect model data
            for model in models_to_collect:
                for var in model.varnames:
                    if not trial.is_static:
                        # pick data only if var context matches cycle context
                        # FIXME: should implement context() for models
                        # (and a filter for context?)
                        if var[0] != cycle.context:
                            continue

                        if not collect_all_cycles:
                            # don't collect kinetics if cycle is not on forceplate
                            if (
                                model.is_kinetic_var(var) or fp_cycles_only
                            ) and not cycle.on_forceplate:
                                continue

                    _, data = trial.get_model_data(var, cycle=cycle)
                    if np.all(np.isnan(data)):
                        logger.debug(f'no data for {trial.trialname}/{var}')
                    else:
                        cycles_all['model'][var].append(cycle)
                        if var not in data_all['model']:
                            data_all['model'][var] = data[None, :]
                        else:
                            data_all['model'][var] = np.concatenate(
                                [data_all['model'][var], data[None, :]]
                            )

            # collect EMG data
            for ch in emg_chs_to_collect:
                # check whether cycle matches channel context
                if not trial.is_static and not trial.emg.context_ok(ch, cycle.context):
                    continue

                if not collect_all_cycles:
                    if fp_cycles_only and not cycle.on_forceplate:
                        continue

                # get data on analog sampling grid
                try:
                    logger.debug(f'collecting EMG channel {ch} from {cycle}')
                    _, data = trial.get_emg_data(
                        ch, cycle=cycle, envelope=analog_envelope
                    )
                except (KeyError, GaitDataError):
                    logger.warning(f'no channel {ch} for {trial}')
                    continue
                # resample to requested grid
                data_cyc = scipy.signal.resample(data, analog_len)
                cycles_all['emg'][ch].append(cycle)
                if ch not in data_all['emg']:
                    data_all['emg'][ch] = data_cyc[None, :]
                else:
                    data_all['emg'][ch] = np.concatenate(
                        [data_all['emg'][ch], data_cyc[None, :]]
                    )
    logger.info('collected %d trials' % len(trials))
    return data_all, cycles_all


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
                data, cycles = collect_trial_data(full_name, analog_envelope=True, collect_all_cycles=True, fp_cycles_only=False)

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