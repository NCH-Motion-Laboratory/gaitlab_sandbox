# -*- coding: utf-8 -*-
"""
running analysis

-compute compression of leg during loading phase
-force at max. compression
-project to ankle joint center - hip joint center line



@author: Jussi (jnu@iki.fi)
"""

from time import localtime, strftime
from openpyxl import Workbook
import numpy as np
from numpy.linalg import norm
import glob
import os.path as op
import logging

import gaitutils
from gaitutils import read_data


# name files according to script start time
timestr_ = strftime("%Y_%m_%d-%H%M%S", localtime())


def write_workbook_rows(results, filename, first_col=1, first_row=1):
    """Write results into .xlsx file (filename). results must be a list of
    lists which represent the rows to write. first_col and first_row
    specify the column and row where to start writing (1-based) """
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Running compression analysis"
    for j, row in enumerate(results):
        for k, val in enumerate(row):
            ws1.cell(column=k+1+first_col, row=j+1+first_row, value=val)
    wb.save(filename=filename)


rootdir = u'Z:/siirto/Running/'
outfile = op.join(rootdir, 'foot_force_at_max_compression_%s.xlsx' % timestr_)
glob_ = '*.c3d'
files = glob.glob(op.join(rootdir + glob_))


def _get_comp_values(c3dfile):

    mdata = read_data.get_marker_data(c3dfile, ['RFEP', 'RTIO'])
    tr = gaitutils.Trial(c3dfile)

    # ankle joint - hip joint distance
    jnt_vec = mdata['RFEP_P'] - mdata['RTIO_P']
    dist = np.sqrt(np.sum(jnt_vec**2, 1))

    dist[mdata['RFEP_gaps']] = np.nan
    dist[mdata['RTIO_gaps']] = np.nan

    strikes = np.array(tr.rstrikes)
    plates = tr.fp_events['R_strikes_plate']
    toeoffs = np.array(tr.rtoeoffs)

    for ind, (strike, plate) in enumerate(zip(strikes, plates), 1):
        toeoff_cands = toeoffs[np.where(toeoffs > strike)]
        if len(toeoff_cands) == 0:
            print('No toeoff for foot strike at %d!' % strike)
            continue
        toeoff = toeoff_cands[0]
        # minimum length during contact phase
        min_len = dist[strike:toeoff].min()
        # frame where min. length (max compression) occurs
        min_frame = np.argmin(dist[strike:toeoff]) + strike
        jnt_vec_at_min = jnt_vec[min_frame, :]
        jnt_vec_at_min_1 = jnt_vec_at_min / norm(jnt_vec_at_min)
        min_frame_analog = int(tr.samplesperframe * min_frame)
        fvec_at_min = -tr.forceplate_data[plate-1]['F'][min_frame_analog, :]
        # projection
        fproj = jnt_vec_at_min_1 * np.dot(jnt_vec_at_min_1, fvec_at_min)
        fx, fy, fz = fproj
        strike_len = dist[strike]
        yield c3dfile, ind, min_frame, strike_len - min_len, plate, fx, fy, fz
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    results = list()
    results.append(['filename:', 'cycle:', 'frame of max compression', 'max. compression (mm)', 'forceplate', 'Fx at max. comp. (N)', 'Fy at max. comp. (N)', 'Fz at max. comp. (N)'])
    for c3dfile in files:
        for vals in _get_comp_values(c3dfile):
            results.append([str(v) for v in vals])
    
    write_workbook_rows(results, outfile)
