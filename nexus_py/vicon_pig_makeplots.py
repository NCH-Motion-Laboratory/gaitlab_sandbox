from __future__ import division, print_function
"""
Created on Mon Mar 16 15:07:18 2015

@author: Jussi
"""
import matplotlib.pyplot as plt




def KinematicsPlot(TrialName,tn,KinematicsAll):
    """ Plot all kinematics vars of interest.
    TrialName trial name
    tn x-axis for plot (0...100 for normalized plots)
    KinematicsAll dict containing all kinematics variables
    """
    
    plt.figure(figsize=(14, 12))
    Rcolor='lawngreen'
    Lcolor='red'
    plt.suptitle("Kinematics output\n" + TrialName + " (1st gait cycle)", fontsize=12, fontweight="bold")
    plt.subplot(4, 3, 1)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)
    plot1 = plt.plot(tn, KinematicsAll['NormLPelvisAnglesX'], Lcolor, KinematicsAll['NormRPelvisAnglesX'], Rcolor)
    plt.title('Pelvic tilt')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Pst     ($^\circ$)      Ant')
    plt.ylim(-20., 40.0)
    plt.axhline(0, color='black')
    # plt.legend(('Left', 'Right'), title="Context", fontsize=10, loc='lower right', bbox_to_anchor=(2.3, -5.1),
    #          ncol=3, fancybox=True, shadow=True)
    
    plt.subplot(4, 3, 2)
    plot2 = plt.plot(tn, KinematicsAll['NormLPelvisAnglesY'], Lcolor, KinematicsAll['NormRPelvisAnglesY'], Rcolor)
    plt.title('Pelvic obliquity')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Dwn     ($^\circ$)      Up')
    plt.ylim(-20., 40.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 3)
    plot3 = plt.plot(tn, KinematicsAll['NormLPelvisAnglesZ'], Lcolor, KinematicsAll['NormRPelvisAnglesZ'], Rcolor)
    plt.title('Pelvic rotation')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Bak     ($^\circ$)      For')
    plt.ylim(-30., 40.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 4)
    plot4 = plt.plot(tn, KinematicsAll['NormLHipAnglesX'], Lcolor, KinematicsAll['NormRHipAnglesX'], Rcolor)
    plt.title('Hip flexion')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Ext     ($^\circ$)      Flex')
    plt.ylim(-20., 50.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 5)
    plot5 = plt.plot(tn, KinematicsAll['NormLHipAnglesY'], Lcolor, KinematicsAll['NormRHipAnglesY'], Rcolor)
    plt.title('Hip adduction')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Abd     ($^\circ$)      Add')
    plt.ylim(-30., 30.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 6)
    plot6 = plt.plot(tn, KinematicsAll['NormLHipAnglesZ'], Lcolor, KinematicsAll['NormRHipAnglesZ'], Rcolor)
    plt.title('Hip rotation')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Ext     ($^\circ$)      Int')
    plt.ylim(-20., 30.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 7)
    plot7 = plt.plot(tn, KinematicsAll['NormLKneeAnglesX'], Lcolor, KinematicsAll['NormRKneeAnglesX'], Rcolor)
    plt.title('Knee flexion')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Ext     ($^\circ$)      Flex')
    plt.ylim(-15., 75.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 8)
    plot8 = plt.plot(tn, KinematicsAll['NormLKneeAnglesY'], Lcolor, KinematicsAll['NormRKneeAnglesY'], Rcolor)
    plt.title('Knee adduction')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Val     ($^\circ$)      Var')
    plt.ylim(-30., 30.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 9)
    plot9 = plt.plot(tn, KinematicsAll['NormLKneeAnglesZ'], Lcolor, KinematicsAll['NormRKneeAnglesZ'], Rcolor)
    plt.title('Knee rotation')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Ext     ($^\circ$)      Int')
    plt.ylim(-30., 30.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 10)
    plot10 = plt.plot(tn, KinematicsAll['NormLAnkleAnglesX'], Lcolor, KinematicsAll['NormRAnkleAnglesX'], Rcolor)
    plt.title('Ankle dorsi/plant')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Pla     ($^\circ$)      Dor')
    plt.ylim(-30., 30.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 11)
    plot11 = plt.plot(tn, KinematicsAll['NormLFootProgressAnglesZ'], Lcolor, KinematicsAll['NormRFootProgressAnglesZ'], Rcolor)
    plt.title('Foot progress angles')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Ext     ($^\circ$)      Int')
    plt.ylim(-30., 30.0)
    plt.axhline(0, color='black')
    
    plt.subplot(4, 3, 12)
    plot11 = plt.plot(tn, KinematicsAll['NormLAnkleAnglesZ'], Lcolor, KinematicsAll['NormRAnkleAnglesZ'], Rcolor)
    plt.title('Ankle rotation')
    plt.xlabel('% of gait cycle')
    plt.ylabel('Ext     ($^\circ$)      Int')
    plt.ylim(-30., 30.0)
    plt.axhline(0, color='black')
     
    plt.show()
    
    
    
