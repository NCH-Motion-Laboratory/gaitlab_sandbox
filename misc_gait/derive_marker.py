# -*- coding: utf-8 -*-
"""

Example: replace marker data with data derived from other markers.
E.g. put a tibia marker halfway between ankle and knee.

@author: Jussi (jnu@iki.fi)
"""

# %% main code
from gaitutils import nexus

import logging

logging.basicConfig(level=logging.DEBUG)

vicon = nexus.viconnexus()

# subject has to match Nexus subject name
subj = nexus.get_subjectnames()
# derive data from existing markers
for context in 'LR':
    mkrdata = nexus._get_marker_data(vicon, ['%sKNE' % context, '%sANK' % context])
    ltib_est = (mkrdata['%sKNE' % context] + mkrdata['%sANK' % context]) / 2.0
    x, y, z = ltib_est.T
    exists = [True] * len(x)
    # write the desired marker
    vicon.SetTrajectory(subj, '%sTIB' % context, x, y, z, exists)
    vicon.SaveTrial(60)

