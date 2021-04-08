# -*- coding: utf-8 -*-
"""
experimental global autoprocess



@author: Jussi (jnu@iki.fi)
"""

# %% init

import os
import os.path as op
import shutil
import numpy as np
import time
import logging
import datetime

import gaitutils
from gaitutils import sessionutils, nexus, cfg, autoprocess, trial, videos, GaitDataError
from gaitutils.report import web, pdf
from ulstools.num import check_hetu

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
        enfs_thisdir = [
            (k, enffile)
            for (k, enffile) in enumerate(enffiles)
            if _gait_dir(enffile) == dir
        ]
        n_contacts = [_count_fp_contacts(trials[k]) for k, _ in enfs_thisdir]
        best_inds = np.argsort(-np.array(n_contacts))
        bestfiles = [enfs_thisdir[k][1] for k in best_inds]
        for k, enffile in enumerate(bestfiles[:MAX_TAGS_PER_CONTEXT], 1):
            gaitutils.eclipse.set_eclipse_keys(
                enffile, {'NOTES': dir + str(k)}, update_existing=True
            )


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


# %%
# 1: get session dirs
logging.basicConfig(level=logging.DEBUG)
# must be in a session dir for starters
rootdir = _get_patient_dir()
session_all = [op.join(rootdir, p) for p in os.listdir(rootdir)]

session_dirs = [
    f for f in session_all if op.isdir(f) and _is_sessiondir(f)
]  # Nexus session dirs


# %%
# 2: autoproc all
for p in session_dirs:
    enffiles = sessionutils.get_enfs(p)
    autoprocess._do_autoproc(enffiles, pipelines_in_proc=False)


# %%
# 3: autotag all
for p in session_dirs:
    _autotag(p)


# %%
# 4: review the data
for p in session_dirs:
    # kinematics
    fig = gaitutils.viz.plots._plot_sessions(
        p, backend='plotly', figtitle=op.split(p)[-1]
    )
    gaitutils.viz.plot_misc.show_fig(fig)
    # kinetics
    fig = gaitutils.viz.plots._plot_sessions(
        p, layout_name='lb_kinetics', backend='plotly', figtitle=op.split(p)[-1]
    )
    gaitutils.viz.plot_misc.show_fig(fig)
    # EMG
    fig = gaitutils.viz.plots._plot_sessions(
        p, layout_name='std_emg', backend='plotly', figtitle=op.split(p)[-1]
    )
    gaitutils.viz.plot_misc.show_fig(fig)


# %%
# 5: get info from user
patient_name = input('Please enter patient name:')

prompt = 'Please enter hetu:'
while True:
    hetu = input(prompt)
    if check_hetu(hetu):
        break
    else:
        prompt = 'Invalid hetu entered, please re-enter:'

session_desc = dict()
for d in session_dirs:
    session_desc[d] = input(
        'Please enter description for %s' % op.split(d)[-1])


# %%
# 6: run postproc. pipelines

# restart Nexus for postproc pipelines
nexus._kill_nexus(restart=True)
time.sleep(20)  # might take a while

for sessiondir in session_dirs:
    c3dfiles = sessionutils.get_c3ds(
        sessiondir,
        tags=cfg.eclipse.tags,
        trial_type='dynamic',
        check_if_exists=False,
    )
    c3dfiles += sessionutils.get_c3ds(
        sessiondir, trial_type='static', check_if_exists=False
    )
    _run_postprocessing(c3dfiles)


# %%
# 7: generate reports
for sessiondir in session_dirs:

    info = {
        'fullname': patient_name,
        'hetu': hetu,
        'session_description': session_desc[sessiondir],
    }
    sessionutils.save_info(sessiondir, info)
    vidfiles = videos._collect_session_videos(sessiondir, tags=cfg.eclipse.tags)
    if not vidfiles:
        raise RuntimeError('Cannot find any video files for session %s' % sessiondir)

    if not videos.convert_videos(vidfiles, check_only=True):
        procs = videos.convert_videos(vidfiles=vidfiles)
        if not procs:
            raise RuntimeError('video converter processes could not be started')

        # wait in a sleep loop until all converter processes have finished
        completed = False
        _n_complete = -1
        while not completed:
            n_complete = len([p for p in procs if p.poll() is not None])
            prog_txt = 'Converting videos: %d of %d files done' % (
                n_complete,
                len(procs),
            )
            if _n_complete != n_complete:
                print(prog_txt)
                _n_complete = n_complete
            time.sleep(1)
            completed = n_complete == len(procs)

    web.dash_report(sessions=[sessiondir], info=info, recreate_plots=True)
    pdf.create_report(sessiondir, info, write_extracted=True, write_timedist=True)


# %%
# 8: move patient to network drive

DEST_ROOT = r'Y:\Userdata_Vicon_Server'

patient_code = op.split(rootdir)[-1]

diags_dirs = {
    'H': '1_Hemiplegia',
    'D': '1_Diplegia',
    'M': '1_Meningomyelocele',
    'E': '1_Eridiagnoosit',
    'C': '1_Muu CP',
}
try:
    diag_dir = diags_dirs[patient_code[0]]  # choose according to 1st letter of patient code
except KeyError:
    raise RuntimeError('Cannot interpret patient code')

destdir_patient = op.join(DEST_ROOT, diag_dir, patient_code)

assert op.isdir(destdir_patient)

# kill Nexus so it doesn't get confused by the move operation
nexus._kill_nexus()

copy_done = False
for sessiondir in session_dirs:
    _sessiondir = op.split(sessiondir)[-1]
    destdir = op.join(destdir_patient, _sessiondir)
    print('%s -> '%s' % (sessiondir, destdir))
    shutil.copytree(sessiondir, destdir)
copy_done = True


# %% DANGER --- DANGER --- DANGER
# remove from local drive, if copy was successful
# set ALLOW_DELETE manually
if copy_done and ALLOW_DELETE:  
    shutil.rmtree(rootdir)


# %% ALT: only convert the videos - for video-only sessions

REDO_ALL = True  # force conversion even if target files exist

for sessiondir in session_dirs:
    vidfiles = videos._collect_session_videos(sessiondir, tags=cfg.eclipse.tags)
    if not vidfiles:
        raise RuntimeError('Cannot find any video files for session %s' % sessiondir)

    if REDO_ALL or not videos.convert_videos(vidfiles, check_only=True):
        procs = videos.convert_videos(vidfiles=vidfiles)
        if not procs:
            raise RuntimeError('video converter processes could not be started')

        # wait in sleep loop until all converter processes have finished
        completed = False
        _n_complete = -1
        while not completed:
            n_complete = len([p for p in procs if p.poll() is not None])
            prog_txt = 'Converting videos: %d of %d files done' % (
                n_complete,
                len(procs),
            )
            if _n_complete != n_complete:
                print(prog_txt)
                _n_complete = n_complete
            time.sleep(1)
            completed = n_complete == len(procs)
