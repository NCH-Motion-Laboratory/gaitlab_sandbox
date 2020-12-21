# -*- coding: utf-8 -*-
"""

some code for comparing contents of drives 

@author: Jussi (jnu@iki.fi)
"""


import os
import os.path as op


# %% scan two drives, Z: and Y:
# Y is supposed to equal Z (except for excluded dirs)


def _all_files(path):
    """Recursively yield all files (not dirs) under a subdir"""
    for dir, _, files in os.walk(path):
        for filename in files:
            yield op.join(dir, filename)


def _filter_exclude(paths, strings):
    """Exclude strings from paths; case insensitive"""
    if not isinstance(strings, list):
        strings = [strings]
    for path in paths:
        if not any(str.lower() in path.lower() for str in strings):
            yield path


def _filter_rm_drive_letter(paths):
    """Remove first character (drive letter)"""
    for path in paths:
        yield path[2:]


def _filter_n(vals, n):
    """Return n first values from an iterator"""
    for k, val in enumerate(vals):
        if k < n:
            yield val
        else:
            break


# find all files
# remove drive letter from names so we can compare

gz = _all_files('Z:\\')
gz = _filter_exclude(gz, 'userdata_vicon_server')
# gz = _filter_n(gz, 20)
gz = _filter_rm_drive_letter(gz)
lz0 = list(gz)


gy = _all_files('Y:\\')
# gy = _filter_n(gy, 20)
gy = _filter_rm_drive_letter(gy)
ly0 = list(gy)


# %% find the differences between the file sets

# missing from y drive - should be copied from z
not_on_y = set(lz0) - set(ly0)

# were deleted from z after copy - should be deleted from y
not_on_z = set(ly0) - set(lz0)

# modified after copy - should be re-copied from z
# this takes a while
on_both = set.intersection(set(lz0), set(ly0))

print(f'{len(on_both)} items on both drives')

modtime_differs = list()
for i, f in enumerate(on_both):
    if i % 500 == 0:
        print(f'{i} files checked')
    if os.path.getmtime('Z:' + f) != os.path.getmtime('Y:' + f):
        modtime_differs.append(f)
