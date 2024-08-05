"""
This script adds an extra marker to the foot. The marker is placed a fixed
distance "down" from the toe. "Down" is defined as the direction of the
vector perpendicular heel-toe vector and residing in the same verical plane
as the heel-toe vector (and pointing roughly in the negative z direction).
The script assumes that the foot is not vertical in any frame. The script
is intended to be used with the c3d files.
"""

import numpy as np
from ezc3d import c3d

INP_FILE = '/home/andrey/scratch/01_valtteri01.c3d'
OUT_FILE = '/home/andrey/scratch/01_valtteri01_new.c3d'
T_REF_SUFFIX = 'TOE'
H_REF_SUFFIX = 'HEE'

NEW_MARKER_SUFFIX = 'DOWN'
OFFSET = 50 # mm, MUST BE SAME UNITS AS THE C3D FILE!

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

    down = np.zeros_like(delta)
    down[2,:] = -1

    ndelta = delta / np.linalg.norm(delta, axis=0)

    # Remove the component collinear to ndelta from down
    # Use a very inefficient implementation of column-wise
    # dot product, but who cares
    down -= np.diag(down.T @ ndelta) * ndelta

    # Normalize down
    down /= np.linalg.norm(down, axis=0)

    # Put the new marker OFFSET distance along the "down" direction from the toe
    new_marker_data = toe_data + down * OFFSET

    # Add the new marker to the c3d object
    idx = np.arange(n_points + 1)
    idx[-1] = 0

    c['data']['points'] = c['data']['points'][:,idx,:]
    c['data']['points'][:3, -1, :] = new_marker_data

    c['parameters']['POINT']['LABELS']['value'].append(aspect + NEW_MARKER_SUFFIX)

# Delete meta_points and let ezc3d recreate it
del c['data']['meta_points']
c.write(OUT_FILE)