# -*- coding: utf-8 -*-
"""
Experimental global autoprocessing. This can be used to process many sessions at
once (for a single subject).


@author: Jussi (jnu@iki.fi)
"""
# %% init

import os
from pathlib import Path
import shutil
import numpy as np
import time
import logging
import datetime
import sqlite3

import gaitutils
from gaitutils import (
    sessionutils,
    nexus,
    cfg,
    autoprocess,
    trial,
    videos,
    GaitDataError,
)
from gaitutils.report import web, pdf
from ulstools.num import check_hetu

# how many trials to tag per context
MAX_TAGS_PER_CONTEXT = 3
# root dir for copy destination
DEST_ROOT = Path(r'Y:\Userdata_Vicon_Server')
# diag-specific subdirs
DIAGS_DIRS = {
    'H': '1_Hemiplegia',
    'D': '1_Diplegia',
    'M': '1_Meningomyelocele',
    'E': '1_Eridiagnoosit',
    'C': '1_Muu CP',
}


logging.basicConfig(level=logging.DEBUG)


def _count_fp_contacts(trial):
    """Return n of valid forceplate contacts"""
    return len(trial.fp_events['L_strikes']) + len(trial.fp_events['R_strikes'])


def _gait_direction(enffile):
    """Quick and dirty gait direction from enffile, after autoprocessing.
    
    XXX: fragile, relies on certain description string.
    """
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

    for direction in 'ET':
        enfs_thisdir = [
            (k, enffile)
            for (k, enffile) in enumerate(enffiles)
            if _gait_direction(enffile) == direction
        ]
        n_contacts = [_count_fp_contacts(trials[k]) for k, _ in enfs_thisdir]
        best_inds = np.argsort(-np.array(n_contacts))
        bestfiles = [enfs_thisdir[k][1] for k in best_inds]
        for k, enffile in enumerate(bestfiles[:MAX_TAGS_PER_CONTEXT], 1):
            gaitutils.eclipse.set_eclipse_keys(
                enffile, {'NOTES': direction + str(k)}, update_existing=True
            )


def _get_patient_dir():
    """Get patient dir (session root). Must currently be in a session."""
    if not (cwd := gaitutils.nexus.get_sessionpath()):
        raise RuntimeError('cannot get cwd')
    else:
        return cwd.parent


def _is_sessiondir(dir):
    """Check whether given dir is a Nexus session directory"""
    if not dir.is_dir():
        return False
    try:
        sessionutils.get_session_date(dir)
    except GaitDataError:
        return False
    return True


def _run_postprocessing(c3dfiles):
    """Helper function that will be run in a separate thread"""
    nexus._close_trial()
    for c3dfile in c3dfiles:
        nexus._open_trial(c3dfile)
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
# must be in a session dir
session_dirs = [p for p in _get_patient_dir().iterdir() if _is_sessiondir(p)]
if session_dirs:
    print(f'found session dirs: {[str(s) for s in session_dirs]}')
else:
    raise RuntimeError('no valid session dirs')

# check if any dirs already exist on dest
rootdir = session_dirs[0].parent
patient_code = rootdir.name

try:
    diag_dir = DIAGS_DIRS[
        patient_code[0]
    ]  # choose according to 1st letter of patient code
except KeyError:
    raise RuntimeError('Cannot interpret patient code')

destdir_patient = DEST_ROOT / diag_dir / patient_code

if not destdir_patient.is_dir():
    os.mkdir(destdir_patient)  # for patients not seen before
    assert destdir_patient.is_dir()
else:
    print(f'patient destination dir {destdir_patient} already exists')
    for sessiondir in session_dirs:
        sessiondir_dest = destdir_patient / sessiondir.name
        if sessiondir_dest.is_dir():
            raise RuntimeError(f'session destination directory {sessiondir_dest} already exists!')



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
    for lout in cfg.plot.review_layouts:
        fig = gaitutils.viz.plots._plot_sessions(
            p, layout=lout, backend='plotly', figtitle=p.name
        )
        gaitutils.viz.plot_misc.show_fig(fig)



# %%
# 5: run postproc. pipelines
for sessiondir in session_dirs:

    # restart Nexus for postproc pipelines
    nexus._kill_nexus(restart=True)
    time.sleep(30)  # might take a while

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

    print(f'Finished {sessiondir}')

print('*** Finished postprocessing pipelines')


# %%
# 6: get info from ROM database or user


db_file = Path(r'Z:\gaitbase\patients.db')

conn = sqlite3.connect(db_file)
conn.execute('PRAGMA foreign_keys = ON;')
p = list(conn.execute(f"SELECT * from patients WHERE patient_code='{patient_code}'"))
conn.close()

if p:
    print(f'found patient in database: {p[0]}')
    _, firstname, lastname, hetu, _, _ = p[0]
    patient_name = f'{firstname} {lastname}'
else:
    patient_name = input('Please enter patient name:')
    prompt = 'Please enter hetu:'
    while not check_hetu(hetu := input(prompt)):
        prompt = 'Invalid hetu entered, please re-enter:'

session_desc = dict()
for d in session_dirs:
    session_desc[d] = input(f'Please enter description for {d.name}')


# %%

# 7: generate reports
for sessiondir in session_dirs:

    info = {
        'fullname': patient_name,
        'hetu': hetu,
        'session_description': session_desc[sessiondir],
    }
    sessionutils.save_info(sessiondir, info)
    if not (vidfiles := videos._collect_session_videos(sessiondir, tags=cfg.eclipse.tags)):
        raise RuntimeError(f'Cannot find any video files for session {sessiondir}')

    if not videos.convert_videos(vidfiles, check_only=True):
        # need to convert
        if not (procs := videos.convert_videos(vidfiles=vidfiles)):
            raise RuntimeError('video converter processes could not be started')

        # wait in a sleep loop until all converter processes have finished
        completed = False
        _n_complete = -1
        while not completed:
            n_complete = len([p for p in procs if p.poll() is not None])
            prog_txt = f'Converting videos: {n_complete} of {len(procs)} files done'
            if _n_complete != n_complete:
                print(prog_txt)
                _n_complete = n_complete
            time.sleep(1)
            completed = n_complete == len(procs)

    web.dash_report(sessions=[sessiondir], info=info, recreate_plots=True)
    pdf.create_report(sessiondir, info, write_extracted=True, write_timedist=True)

print('*** Finished reports')


# %%
# 8: copy patient to network drive

# kill Nexus so it doesn't get confused by the move operation
nexus._kill_nexus()

copy_done = False
for sessiondir in session_dirs:
    destdir = destdir_patient / sessiondir.name
    print(f'copying {sessiondir} -> {destdir}...')
    shutil.copytree(sessiondir, destdir)
    assert destdir.is_dir()
copy_done = True

# FIXME: should assert that copy really worked?
print('*** Finished copying')


# %% DANGER --- DANGER --- DANGER
# remove from local drive, if copy was successful
# set ALLOW_DELETE manually
if copy_done and ALLOW_DELETE:
    assert rootdir.parent == Path('D:/ViconData/Clinical')
    shutil.rmtree(rootdir)



# %% ALT: only convert the videos - for video-only sessions

REDO_ALL = True  # force conversion even if target files exist

for sessiondir in session_dirs:
    vidfiles = videos._collect_session_videos(sessiondir, tags=cfg.eclipse.tags)
    if not vidfiles:
        raise RuntimeError(f'Cannot find any video files for session {sessiondir}')

    if REDO_ALL or not videos.convert_videos(vidfiles, check_only=True):
        procs = videos.convert_videos(vidfiles=vidfiles)
        if not procs:
            raise RuntimeError('Video converter processes could not be started')
        # wait in sleep loop until all converter processes have finished
        completed = False
        _n_complete = -1
        while not completed:
            n_complete = len([p for p in procs if p.poll() is not None])
            prog_txt = f'Converting videos: {n_complete} of {len(procs)} files done'
            if _n_complete != n_complete:
                print(prog_txt)
                _n_complete = n_complete
            time.sleep(1)
            completed = n_complete == len(procs)

print('*** Finished video conversion')
