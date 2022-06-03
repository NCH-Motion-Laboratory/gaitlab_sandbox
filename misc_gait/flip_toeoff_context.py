# -*- coding: utf-8 -*-
"""
Flip context of toeoff markers (to correct treadmill data)

@author: vicon123
"""



# %%
from gaitutils import nexus


vicon = nexus.viconnexus()
events = nexus._get_metadata(vicon)['events']
toeoffs = events.get_events(event_type='toeoff')

flip_context = dict(('LR', 'RL'))

for ev in toeoffs:
    ev.context = flip_context[ev.context]

vicon.ClearAllEvents()
nexus._create_events(vicon, events)



