# -*- coding: utf-8 -*-
"""
experimental global autoprocess

wip:
-autoprocess
-a way to supply patient info for reports
-generate pdf and web reports


@author: Jussi (jnu@iki.fi)
"""

# %% init

import os
import os.path as op
import numpy as np
import subprocess
import time
import psutil

import gaitutils
from gaitutils import sessionutils, nexus, cfg, autoprocess, trial
from gaitutils.report import web, pdf

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
    try:
        sessionutils.get_session_date(dir)
    except GaitDataError:
        return False
    return True


def _run_postprocessing(c3dfiles):
    """Helper function that will be run in a separate thread"""
    vicon = nexus.viconnexus()
    nexus._close_trial()
    for c3dfile in c3dfiles:
        trbase = op.splitext(c3dfile)[0]
        vicon.OpenTrial(trbase, cfg.autoproc.nexus_timeout)
        nexus._run_pipelines(cfg.autoproc.postproc_pipelines)


def _start_nexus():
    """Start Vicon Nexus"""
    exe = op.join(nexus._find_nexus_path(), 'Nexus.exe')
    p = subprocess.Popen([exe])
    time.sleep(12)
    return p


def _kill_nexus(p=None, restart=False):
    """Kill Vicon Nexus process p"""
    if p is None:
        pid = nexus._nexus_pid()
        p = psutil.Process(pid)
    p.terminate()
    if restart:
        time.sleep(5)
        _start_nexus()


def _parse_name(name):
    """Parse trial or session name of the standard form YYYY_MM_DD_desc1_desc2_..._descN_code"""
    name_split = name.split('_')
    if len(name_split) < 3:
        raise ValueError('Could not parse name')
    try:  # see if trial begins with valid date
        datetxt = '-'.join(name_split[:3])
        d = datetime.datetime.strptime(datetxt, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Could not parse name')
    code = name_split[-1] if len(name_split) > 3 else None
    desc = ', '.join(name_split[3:-1]) if len(name_split) > 3 else None
    return d, code, desc




# %% experimental global autoproc
from ulstools.num import check_hetu

# must be in a session dir for starters
rootdir = _get_patient_dir()
session_all = [op.join(rootdir, p) for p in os.listdir(rootdir)]  # all files under patient dir
session_dirs = [f for f in session_all if op.isdir(f) and _is_sessiondir(f)]  # Nexus session dirs


# %% get the session info from the user
patient_name = raw_input('Please enter patient name:')

prompt = 'Please enter hetu:'
while True:
    hetu = raw_input(prompt)
    if check_hetu(hetu):
       break
    else:
        prompt = 'Invalid hetu entered, please re-enter:'

session_desc = dict()
for d in session_dirs:
    session_desc[d] = raw_input('Please enter description for %s' % op.split(d)[-1])



# %%
# autoproc all
for p in session_dirs:
    enffiles = sessionutils.get_enfs(p)
    autoprocess._do_autoproc(enffiles, pipelines_in_proc=False)


# %% autotag all
for p in session_dirs:
    _autotag(p)


# %% review the data
for p in session_dirs:
    fig = gaitutils.viz.plots._plot_sessions(p, backend='plotly', figtitle=op.split(p)[-1])
    gaitutils.viz.plot_misc.show_fig(fig)
    fig = gaitutils.viz.plots._plot_sessions(p, layout_name='lb_kinetics', backend='plotly', figtitle=op.split(p)[-1])
    gaitutils.viz.plot_misc.show_fig(fig)
    fig = gaitutils.viz.plots._plot_sessions(p, layout_name='std_emg', backend='plotly', figtitle=op.split(p)[-1])
    gaitutils.viz.plot_misc.show_fig(fig)


# %% run postproc. pipelines

# restart Nexus for postproc pipelines
_kill_nexus(restart=True)

for p in session_dirs:
    c3dfiles = sessionutils._get_tagged_dynamic_c3ds_from_sessions([p], tags=cfg.eclipse.tags)
    _run_postprocessing(c3dfiles)


# %% generate reports
for p in session_dirs:
    # generate reports
    info = {'fullname': patient_name, 'hetu': hetu, 'session_description': session_desc[p]}
    pdf.create_report(p, info, write_extracted=True, write_timedist=True)
    web.dash_report(p, info)

