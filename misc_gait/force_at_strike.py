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


# Excel header row (variable titles)
header = ['filename', 'gait cycle', 'frame of max compression',
          'max. compression (mm)', 'forceplate id',
          'maximum contact force (N)',
          'force at max. compression (N)',
          'ankle-hip projected force at max. compression (N)',
          'ankle-hip projected Fx at max. compression (N)',
          'ankle-hip projected Fy at max. compression (N)',
          'ankle-hip projected Fz at max. compression (N)']
rootdir = u'Z:/siirto/Running/'
outfile = op.join(rootdir, 'foot_force_at_max_compression_%s.xlsx' % timestr_)
glob_ = '*.c3d'
context = 'R'
files = glob.glob(op.join(rootdir + glob_))


def _stringify(v):
    if isinstance(v, float):
        return '%.2f' % v
    else:
        return str(v)


def _get_comp_values(c3dfile):

    hip_ctr = context+'FEP'
    ank_ctr = context+'TIO'
    mdata = read_data.get_marker_data(c3dfile, [hip_ctr, ank_ctr])
    tr = gaitutils.Trial(c3dfile)

    # ankle joint - hip joint distance
    jnt_vec = mdata[hip_ctr+'_P'] - mdata[ank_ctr+'_P']
    dist = np.sqrt(np.sum(jnt_vec**2, 1))
    dist[mdata[hip_ctr+'_gaps']] = np.nan  # avoid zero location at gaps
    dist[mdata[hip_ctr+'_gaps']] = np.nan

    fp_cycles = [c for c in tr.cycles if c.on_forceplate and c.context ==
                 context]

    for cyc in fp_cycles:
        strike = cyc.start
        toeoff = cyc.toeoff
        plate = cyc.plate_idx
        cyc_str = context + str(cyc.index)
        # minimum length during contact phase
        min_len = dist[strike:toeoff].min()
        # frame where min. length (max compression) occurs
        min_frame = np.argmin(dist[strike:toeoff]) + strike
        jnt_vec_at_min = jnt_vec[min_frame, :]
        jnt_vec_at_min_1 = jnt_vec_at_min / norm(jnt_vec_at_min)
        min_frame_analog = int(tr.samplesperframe * min_frame)
        fvec_at_min_comp = -tr.forceplate_data[plate]['F'][min_frame_analog, :]
        fmax = tr.forceplate_data[plate]['Ftot'].max()
        # projection
        fproj = jnt_vec_at_min_1 * np.dot(jnt_vec_at_min_1, fvec_at_min_comp)
        fx, fy, fz = fproj
        strike_len = dist[strike]
        comp = strike_len - min_len
        yield (c3dfile, cyc_str, min_frame, comp, plate, fmax,
               norm(fvec_at_min_comp), norm(fproj), fx, fy, fz)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    results = list()
    results.append(header)
    for c3dfile in files:
        for vals in _get_comp_values(c3dfile):
            results.append([_stringify(v) for v in vals])

    write_workbook_rows(results, outfile)
