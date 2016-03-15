# -*- coding: utf-8 -*-
"""
Kinetics/kinematics/EMG plot from Nexus.
Try to automatically figure out what to plot.

"""

from gp.plot import gaitplotter
from gp.misc import messagebox
import nexus_kinetics_emgplot
import nexus_kinematicsonly_emgplot

do_kinetics = True
do_emg = True
msg = ''


gplotter = gaitplotter()
gplotter.open_nexus_trial()
gplotter.trial.emg.read()

if not gplotter.trial.kinetics_side:
    do_kinetics = False
    msg = msg + 'Forceplate strike not detected. Plotting kinematics only.\n'

if gplotter.trial.emg.no_emg:
    do_emg = False
    msg = msg + 'All EMG channels disconnected. Using non-EMG layout.'
    
if not (do_kinetics and do_emg):
    messagebox(msg)
    
if do_kinetics and do_emg:  # 1-page kinetics/EMG according to side
    nexus_kinetics_emgplot.do_plot()

elif do_kinetics and not do_emg:  # 1-page kinetics/kinematics
    nexus_kinetics_emgplot.do_plot(emg=False)

elif not do_kinetics and do_emg:  # 2-page EMG-kinematics (one side per page)
    nexus_kinematicsonly_emgplot.do_plot()

elif not do_kinetics and not do_emg:  # 1-page kinematics plot
    nexus_kinematicsonly_emgplot.do_plot(emg=False)
    


    
    

    
    
