"""
This script adds an extra marker to the foot. The marker is placed 20% of the
foot length to the side of the toe. The script assumes that the foot is not
vertical in any frame. The script is intended to be used with the c3d files.
"""

import numpy as np
from ezc3d import c3d

INP_FILE = '/home/andrey/scratch/01_valtteri02.c3d'
OUT_FILE = '/home/andrey/scratch/01_valtteri02_new.c3d'
T_REF_SUFFIX = 'TOE'
H_REF_SUFFIX = 'HEE'

NEW_MARKER_SUFFIX = 'TOE3'

c = c3d(INP_FILE)

for aspect in ['R', 'L']:
    assert not(aspect + NEW_MARKER_SUFFIX in c['parameters']['POINT']['LABELS']['value']), f'Marker {aspect + NEW_MARKER_SUFFIX} already exists'

    n_points = len(c['parameters']['POINT']['LABELS']['value'])

    toe_idx = c['parameters']['POINT']['LABELS']['value'].index(aspect + T_REF_SUFFIX)
    heel_idx = c['parameters']['POINT']['LABELS']['value'].index(aspect + H_REF_SUFFIX)

    toe_data = c['data']['points'][:3, toe_idx, :]
    heel_data = c['data']['points'][:3, heel_idx, :]

    if np.any(np.isnan(toe_data)) or np.any(np.isnan(heel_data)):
        print(f'The data for the {aspect} foot contains NaNs. I\'ll try to process the data anyway, but have no idea whether the results will be valid.')
        
    delta = toe_data - heel_data
    pdelta = delta.copy()
    pdelta[2, :] = 0

    assert np.nanmin(np.linalg.norm(pdelta, axis = 0) / np.linalg.norm(delta, axis=0)) > 0.001, 'The foot is too vertical at least in one frame'

    pdelta /= np.linalg.norm(pdelta, axis=0)

    # Put the new marker 20% of the foot length to the side of the toe
    offset = (np.cross(pdelta.T, np.array([0, 0, 1])).T * np.linalg.norm(delta, axis=0) * 0.2 * (1 if aspect == 'R' else -1))
    new_marker_data = toe_data + offset

    # Add the new marker to the c3d object
    idx = np.arange(n_points + 1)
    idx[-1] = 0

    c['data']['points'] = c['data']['points'][:,idx,:]
    c['data']['points'][:3, -1, :] = new_marker_data

    c['parameters']['POINT']['LABELS']['value'].append(aspect + NEW_MARKER_SUFFIX)


# Delete meta_points and let ezc3d recreate it
del c['data']['meta_points']
c.write(OUT_FILE)