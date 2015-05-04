# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics-EMG plot from Nexus.

@author: Jussi
"""

from nexus_plot import nexus_plotter
import matplotlib.pyplot as plt
import sys

layout = [8,3]
plotheightratios = [3,2,2,3,2,2,2,3]
pdftitlestr = 'Kinetics_EMG_'

nplotter = nexus_plotter(layout, plotvars)
trialpath='C:\\Users\\HUS20664877\\Desktop\\Vicon\\vicon_data\\test\\D0001AV\\2015_4_23_seur_AV\\'
trial1='2015_4_23_seur_AV14'
trial2='2015_4_23_seur_AV19'
trial3='2015_4_23_seur_AV24'

print('Nexus path: ', nplotter.get_nexus_path())


nplotter.open_trial(trialpath+trial1)
side = nplotter.side
trials = nplotter.trialselector()
print(trials)
#trialdesc = nplotter.get_eclipse_description(trialpath+trial1)
#print('ENF description:' + trialdesc)
#print(nplotter.get_nexus_path())

sys.exit()

# choose EMG variables according to side
plotvars = ['HipAnglesX','KneeAnglesX','AnkleAnglesX',
            side+'Ham', side+'Rec', side+'TibA',
            side+'Glut',side+'Vas',side+'Per',
            'HipMomentX','KneeMomentX','AnkleMomentX',
            side+'Rec',side+'Ham',side+'Gas',
            None,side+'Glut',side+'Sol',
            None,side+'Gas',None,
            'HipPowerZ','KneePowerZ','AnklePowerZ']
nplotter.plot_trial(plotheightratios=plotheightratios, maintitle='', 
           makepdf=False, onesided_kinematics=True)


nplotter.open_trial(trialpath+trial2)
side = nplotter.side
# choose EMG variables according to side
plotvars = ['HipAnglesX','KneeAnglesX','AnkleAnglesX',
            side+'Ham', side+'Rec', side+'TibA',
            side+'Glut',side+'Vas',side+'Per',
            'HipMomentX','KneeMomentX','AnkleMomentX',
            side+'Rec',side+'Ham',side+'Gas',
            None,side+'Glut',side+'Sol',
            None,side+'Gas',None,
            'HipPowerZ','KneePowerZ','AnklePowerZ']
nplotter.plot_trial(plotheightratios=plotheightratios, maintitle=trial1+' / '+trial2,
           makepdf=False, onesided_kinematics=True,
           linestyle='--', emg_tracecolor='blue')

nplotter.open_trial(trialpath+trial3)
side = nplotter.side
# choose EMG variables according to side
plotvars = ['HipAnglesX','KneeAnglesX','AnkleAnglesX',
            side+'Ham', side+'Rec', side+'TibA',
            side+'Glut',side+'Vas',side+'Per',
            'HipMomentX','KneeMomentX','AnkleMomentX',
            side+'Rec',side+'Ham',side+'Gas',
            None,side+'Glut',side+'Sol',
            None,side+'Gas',None,
            'HipPowerZ','KneePowerZ','AnklePowerZ']

nplotter.plot_trial(plotheightratios=plotheightratios, maintitle=trial1+' / '+trial2+' / '+trial3,
           makepdf=True, onesided_kinematics=True,
           linestyle='-.', emg_tracecolor='gray')

plt.show()
