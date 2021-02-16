# -*- coding: utf-8 -*-
"""
experimental autotag

wip:
-a way to supply patient info for reports

@author: Jussi (jnu@iki.fi)
"""


from gaitutils import sessionutils, nexus, cfg
import gaitutils
from gaitutils import trial
import os
import os.path as op
import numpy as np

MAX_TAGS_PER_CONTEXT = 3

def _count_fp_contacts(trial):
    """Return n of valid forceplate contacts"""
    return len(trial.fp_events['L_strikes']) + len(trial.fp_events['R_strikes'])


def _gait_dir(enffile):
    """Quick and dirty gait direction from enffile, after autoprocessing"""
    keys = gaitutils.eclipse.get_eclipse_keys(enffile, 'Description')
    thedesc = keys['DESCRIPTION']
    for dir in 'ET':
        if dir in thedesc:
            return dir
    return None


def _autotag(sessiondir):
    """Automatically tag trials in a session dir"""
    c3dfiles = gaitutils.sessionutils.get_c3ds(sessiondir, trial_type='dynamic')
    trials = [trial.Trial(c3dfile) for c3dfile in c3dfiles]
    enffiles = [tr.enfpath for tr in trials]

    for dir in 'ET':
        enfs_thisdir = [(k, enffile) for (k, enffile) in enumerate(enffiles) if _gait_dir(enffile) == dir]
        n_contacts = [_count_fp_contacts(trials[k]) for k, _ in enfs_thisdir]
        best_inds = np.argsort(-np.array(n_contacts))
        bestfiles = [enfs_thisdir[k][1] for k in best_inds]
        for k, enffile in enumerate(bestfiles[:MAX_TAGS_PER_CONTEXT], 1):
            gaitutils.eclipse.set_eclipse_keys(enffile, {'NOTES': dir + str(k)}, update_existing=True)


def _get_patient_dir():
    """Get patient dir (session root). Must currently be in a session."""
    cwd = gaitutils.nexus.get_sessionpath()
    if not cwd:
        raise RuntimeError('cannot get cwd')
    else:
        return op.dirname(cwd)


def _is_sessiondir(dir):
    """Check whether given dir is a Nexus session directory"""
    enfs = sessionutils.get_enfs(dir)
    x1ds = [sessionutils.enf_to_trialfile(fn, 'x1d') for fn in enfs]
    return bool(x1ds)


def _run_postprocessing(c3dfiles):
    """Helper function that will be run in a separate thread"""
    vicon = nexus.viconnexus()
    nexus._close_trial()
    for c3dfile in c3dfiles:
        trbase = op.splitext(c3dfile)[0]
        vicon.OpenTrial(trbase, cfg.autoproc.nexus_timeout)
        nexus._run_pipelines(cfg.autoproc.postproc_pipelines)


# must be in a session dir for starters
rootdir = _get_patient_dir()
session_all = [op.join(rootdir, p) for p in os.listdir(rootdir)]  # all files under patient dir
session_dirs = [f for f in session_all if op.isdir(f) and _is_sessiondir(f)]  # Nexus session dirs


for p in session_dirs:
    _autotag(p)

for p in session_dirs:
    c3dfiles = sessionutils._get_tagged_dynamic_c3ds_from_sessions([p], tags=cfg.eclipse.tags)
    _run_postprocessing(c3dfiles)

