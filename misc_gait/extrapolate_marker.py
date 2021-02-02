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
subj = nexus.get_subjectnames()
# derive data from existing markers
for ctxt in 'LR':
    mkrdata = nexus._get_marker_data(vicon, ['%sKNE' % ctxt, '%sANK' % ctxt])
    ltib_est = (mkrdata['%sKNE' % ctxt] + mkrdata['%sANK' % ctxt]) / 2.0
    x, y, z = ltib_est.T
    exists = [True] * len(x)
    # write the desired marker
    vicon.SetTrajectory(subj, '%sTIB' % ctxt, x, y, z, exists)
    vicon.SaveTrial(60)

