# -*- coding: utf-8 -*-
"""

Replace marker data with data derived from other markers.

@author: Jussi (jnu@iki.fi)
"""

# %% main code
from gaitutils import nexus

import logging

logging.basicConfig(level=logging.DEBUG)

vicon = nexus.viconnexus()

# subject has to match Nexus subject name
subj = '01_egor'
# derive data from existing markers
mkrdata = nexus._get_marker_data(vicon, ['RKNE', 'RANK'])
ltib_est = (mkrdata['RKNE'] + mkrdata['RANK']) / 2.0
x, y, z = ltib_est.T
exists = [True] * len(x)
# write the desired marker
vicon.SetTrajectory(subj, 'RTIB', x, y, z, exists)

