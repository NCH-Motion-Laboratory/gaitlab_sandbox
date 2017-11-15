# -*- coding: utf-8 -*-
"""
running analysis

compute foot speed at n frames before foot strike

@author: Jussi (jnu@iki.fi)
"""

from time import localtime, strftime
from openpyxl import Workbook
import numpy as np
import glob
import os.path as op

import gaitutils
from gaitutils import read_data


def write_workbook_rows(results, filename, first_col=1, first_row=1):
    """Write results into .xlsx file (filename). results must be a list of
    lists which represent the rows to write. first_col and first_row
    specify the column and row where to start writing (1-based) """
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Foot speed analysis"
    for j, row in enumerate(results):
        for k, val in enumerate(row):
            ws1.cell(column=k+1+first_col, row=j+1+first_row, value=val)
    wb.save(filename=filename)


# name files according to script start time
timestr_ = strftime("%Y_%m_%d-%H%M%S", localtime())

rootdir = u'Z:/siirto/Running/'
outfile = op.join(rootdir, 'foot_speed_%s.xlsx' % timestr_)
glob_ = '*.c3d'
files = glob.glob(op.join(rootdir + glob_))

# how many frames before strike to include
nframes = 4


def _get_comp_values(c3dfile):

    mdata = read_data.get_marker_data(c3dfile, ['RTIO'])
    tr = gaitutils.Trial(c3dfile)

    vel_conv = tr.framerate / 1.0e3  # mm/frame -> m/s
    # vel = np.sqrt(np.sum((mdata['RTIO_V'])**2, axis=1))  # vector sum
    vel = np.abs(mdata['RTIO_V'][:, 2])

    vel[mdata['RTIO_gaps']] = np.nan

    strikes = np.array(tr.rstrikes) - tr.offset
    print c3dfile

    for k, strike in enumerate(strikes):
        frames = np.arange(strike-nframes, strike)
        yield [c3dfile, 'strike %d' % (k+1)] + list(vel_conv * vel[frames])


results = list()
for c3dfile in files:
    results.extend(list(_get_comp_values(c3dfile)))

write_workbook_rows(results, outfile)
