# -*- coding: utf-8 -*-
"""
running analysis

compute compression of leg during loading phase:
distance hip joint center - ankle joint center


@author: Jussi (jnu@iki.fi)
"""

from time import localtime, strftime
from openpyxl import Workbook
import numpy as np
import glob
import os.path as op

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
outfile = op.join(rootdir, 'foot_compression_%s.xlsx' % timestr_)
glob_ = '*.c3d'
files = glob.glob(op.join(rootdir + glob_))


def _get_comp_values(c3dfile):

    mdata = read_data.get_marker_data(c3dfile, ['RFEP', 'RTIO'])
    tr = gaitutils.Trial(c3dfile)

    dist = np.sqrt(np.sum((mdata['RTIO_P'] - mdata['RFEP_P'])**2, 1))

    dist[mdata['RFEP_gaps']] = np.nan
    dist[mdata['RTIO_gaps']] = np.nan

    strikes = np.array(tr.rstrikes) - tr.offset
    toeoffs = np.array(tr.rtoeoffs) - tr.offset

    print c3dfile

    lens = list()
    for strike in strikes:
        toeoff_cands = toeoffs[np.where(toeoffs > strike)]
        if len(toeoff_cands) == 0:
            print('No toeoff for foot strike at %d!' % strike)
            continue
        toeoff = toeoff_cands[0]
        min_len = dist[strike:toeoff].min()
        strike_len = dist[strike]
        print strike, toeoff, strike_len, min_len
        lens.append(strike_len - min_len)
    return lens


results = list()
for c3dfile in files:
    results.append([c3dfile] + _get_comp_values(c3dfile))

write_workbook_rows(results, outfile)
