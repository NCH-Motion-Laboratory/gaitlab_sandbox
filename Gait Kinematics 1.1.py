from __future__ import division, print_function

__filename__ = "Gait Kinematics 1.1"
__version__ = "1.1"
__company__ = "Vicon Motion System"
__date__ = "2014"
__author__ = "jgay"

# This Python Code is an example code created to work in conjunction with Vicon Nexus 2 and processed Lower Body
# Plug-in Gait Data. The code needs to be run from within Vicon Nexus 2.
# Data needs to contain at least one complete gait cycle.
# The newly created pdf file will be saved in in your Session Folder.
# Version 1.1 Updates
    # Updated for Nexus 2.1 compatibility
    # Corrected Foot Progression Output
    # Added Y-axis Component

#Code needed for Nexus 2.1
import sys
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")

import ViconNexus

vicon = ViconNexus.ViconNexus()
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

print("Python Script: " + __filename__)

print("Processing Script: " + __filename__)

# Extract information from active trial
SubjectName = vicon.GetSubjectNames()[0]
SessionLoc = vicon.GetTrialName()[0]

# If the data contain events to normalise create the file name and graph title
NormTrialName = SessionLoc + vicon.GetTrialName()[1] + "_Normalized Kinematics.pdf"
NormGraphTitle = "Kinematics for " + vicon.GetTrialName()[1] + " Normalized to Gait Cycle"

# If the data does not contain events to normalise create the file name and graph title
UnNormTrialName = SessionLoc + vicon.GetTrialName()[1] + "_Kinematics.pdf"
UnNormGraphTitle = "Kinematics for " + vicon.GetTrialName()[1]

# Extract Plug-in Gait Lower Body Model Outputs using numpy
LPelvisA = np.array([vicon.GetModelOutput(SubjectName, 'LPelvisAngles')])
RPelvisA = np.array([vicon.GetModelOutput(SubjectName, 'RPelvisAngles')])
LHipA = np.array([vicon.GetModelOutput(SubjectName, 'LHipAngles')])
RHipA = np.array([vicon.GetModelOutput(SubjectName, 'RHipAngles')])
LKneeA = np.array([vicon.GetModelOutput(SubjectName, 'LKneeAngles')])
RKneeA = np.array([vicon.GetModelOutput(SubjectName, 'RKneeAngles')])
LAnkA = np.array([vicon.GetModelOutput(SubjectName, 'LAnkleAngles')])
RAnkA = np.array([vicon.GetModelOutput(SubjectName, 'RAnkleAngles')])
LFootPro = np.array ([vicon.GetModelOutput(SubjectName, 'LFootProgressAngles')])
RFootPro = np.array ([vicon.GetModelOutput(SubjectName, 'RFootProgressAngles')])

# Extract Events from Vicon Data
LFStrike = vicon.GetEvents(SubjectName, "Left", "Foot Strike")[0]
RFStrike = vicon.GetEvents(SubjectName, "Right", "Foot Strike")[0]
lenLFS = len(LFStrike)
lenRFS = len(RFStrike)


if lenLFS and lenRFS >= 2:
    print("Trial contains one Left and one Right Gait Cycle")
    # Calculate Left Gait Cycles
    # Extracting Left Strikes
    LFStrike1 = LFStrike[:1]
    LFStrike2 = LFStrike[1:2]

    # Left Gait Cycle 1
    LGCycle1 = []
    LGCycle1 += LFStrike1
    LGCycle1 += LFStrike2
    LGC1Start = min(LGCycle1)
    LGC1End = max(LGCycle1)

    # Calculate Right Gait Cycles
    # Extract Right Gait Cycles
    RFStrike1 = RFStrike[:1]
    RFStrike2 = RFStrike[1:2]

    #Right Gait Cycle 1
    RGCycle1 = []
    RGCycle1 += RFStrike1
    RGCycle1 += RFStrike2
    RGC1Start = min(RGCycle1)
    RGC1End = max(RGCycle1)

    #Normalize Left to Gait Cycles
    #Left Gait Cycle 1 X
    LGC1LPelvisX = LPelvisA[0][0][0][LGC1Start:LGC1End]
    LGC1LHipX = LHipA[0][0][0][LGC1Start:LGC1End]
    LGC1LKneeX = LKneeA[0][0][0][LGC1Start:LGC1End]
    LGC1LAnkX = LAnkA[0][0][0][LGC1Start:LGC1End]
    #Left Gait Cycle 1 Y
    LGC1LPelvisY = LPelvisA[0][0][1][LGC1Start:LGC1End]
    LGC1LHipY = LHipA[0][0][1][LGC1Start:LGC1End]
    LGC1LKneeY = LKneeA[0][0][1][LGC1Start:LGC1End]
    #Left Gait Cycle 1 Z
    LGC1LPelvisZ = LPelvisA[0][0][2][LGC1Start:LGC1End]
    LGC1LHipZ = LHipA[0][0][2][LGC1Start:LGC1End]
    LGC1LKneeZ = LKneeA[0][0][2][LGC1Start:LGC1End]
    LGC1LFootProZ = LFootPro[0][0][2][LGC1Start:LGC1End]

    #Right Gait Cycle 1 X
    RGC1RPelvisX = RPelvisA[0][0][0][RGC1Start:RGC1End]
    RGC1RHipX = RHipA[0][0][0][RGC1Start:RGC1End]
    RGC1RKneeX = RKneeA[0][0][0][RGC1Start:RGC1End]
    RGC1RAnkX = RAnkA[0][0][0][RGC1Start:RGC1End]
    #Right Right Gait Cycle 1 Y
    RGC1RPelvisY = RPelvisA[0][0][1][RGC1Start:RGC1End]
    RGC1RHipY = RHipA[0][0][1][RGC1Start:RGC1End]
    RGC1RKneeY = RKneeA[0][0][1][RGC1Start:RGC1End]
    #Right Gait Cycle 1 Z
    RGC1RPelvisZ = RPelvisA[0][0][2][RGC1Start:RGC1End]
    RGC1RHipZ = RHipA[0][0][2][RGC1Start:RGC1End]
    RGC1RKneeZ = RKneeA[0][0][2][RGC1Start:RGC1End]
    RGC1RFootProZ = RFootPro[0][0][2][RGC1Start:RGC1End]

    tn = np.linspace(0, 100, 101)
    LGC1t = np.linspace(0, 100, len(LGC1LKneeX))
    RGC1t = np.linspace(0, 100, len(RGC1RKneeX))

    Norm_LGC1LPelvisX = np.interp(tn, LGC1t, LGC1LPelvisX)
    Norm_LGC1LHipX = np.interp(tn, LGC1t, LGC1LHipX)
    Norm_LGC1LKneeX = np.interp(tn, LGC1t, LGC1LKneeX)
    Norm_LGC1LAnkX = np.interp(tn, LGC1t, LGC1LAnkX)

    Norm_LGC1LPelvisY = np.interp(tn, LGC1t, LGC1LPelvisY)
    Norm_LGC1LHipY = np.interp(tn, LGC1t, LGC1LHipY)
    Norm_LGC1LKneeY = np.interp(tn, LGC1t, LGC1LKneeY)

    Norm_LGC1LPelvisZ = np.interp(tn, LGC1t, LGC1LPelvisZ)
    Norm_LGC1LHipZ = np.interp(tn, LGC1t, LGC1LHipZ)
    Norm_LGC1LKneeZ = np.interp(tn, LGC1t, LGC1LKneeZ)
    Norm_LGC1LFootProZ = np.interp(tn, LGC1t, LGC1LFootProZ)

    Norm_LPelvisX = Norm_LGC1LPelvisX
    Norm_LPelvisY = Norm_LGC1LPelvisY
    Norm_LPelvisZ = Norm_LGC1LPelvisZ
    Norm_LHipX = Norm_LGC1LHipX
    Norm_LHipY = Norm_LGC1LHipY
    Norm_LHipZ = Norm_LGC1LHipZ
    Norm_LKneeX = Norm_LGC1LKneeX
    Norm_LKneeY = Norm_LGC1LKneeY
    Norm_LKneeZ = Norm_LGC1LKneeZ
    Norm_LAnkleX = Norm_LGC1LAnkX
    Norm_LFootProZ = Norm_LGC1LFootProZ

    Norm_RGC1RPelvisX = np.interp(tn, RGC1t, RGC1RPelvisX)
    Norm_RGC1RHipX = np.interp(tn, RGC1t, RGC1RHipX)
    Norm_RGC1RKneeX = np.interp(tn, RGC1t, RGC1RKneeX)
    Norm_RGC1RAnkX = np.interp(tn, RGC1t, RGC1RAnkX)

    Norm_RGC1RPelvisY = np.interp(tn, RGC1t, RGC1RPelvisY)
    Norm_RGC1RHipY = np.interp(tn, RGC1t, RGC1RHipY)
    Norm_RGC1RKneeY = np.interp(tn, RGC1t, RGC1RKneeY)

    Norm_RGC1RPelvisZ = np.interp(tn, RGC1t, RGC1RPelvisZ)
    Norm_RGC1RHipZ = np.interp(tn, RGC1t, RGC1RHipZ)
    Norm_RGC1RKneeZ = np.interp(tn, RGC1t, RGC1RKneeZ)
    Norm_RGC1RFootProZ = np.interp(tn, RGC1t, RGC1RFootProZ)

    Norm_RPelvisX = Norm_RGC1RPelvisX
    Norm_RPelvisY = Norm_RGC1RPelvisY
    Norm_RPelvisZ = Norm_RGC1RPelvisZ
    Norm_RHipX = Norm_RGC1RHipX
    Norm_RHipY = Norm_RGC1RHipY
    Norm_RHipZ = Norm_RGC1RHipZ
    Norm_RKneeX = Norm_RGC1RKneeX
    Norm_RKneeY = Norm_RGC1RKneeY
    Norm_RKneeZ = Norm_RGC1RKneeZ
    Norm_RAnkleX = Norm_RGC1RAnkX
    Norm_RFootProZ = Norm_RGC1RFootProZ

    # Set figure style using seaborn
    sns.set_style("white")
    sns.set_context("paper")

    # Create Graphs from extracted data and save to pdf
    with PdfPages(NormTrialName) as pdf:
        plt.figure(figsize=(14, 12))
        plt.suptitle(NormGraphTitle + " (Cycle 1)", fontsize=12, fontweight="bold")

        plt.subplot(4, 3, 1)  # Layout 4 rows, 3 columns, position 1 - top left
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)
        # Plot the X axis of the Model Output
        plot1 = plt.plot(tn, Norm_LPelvisX, '#DC143C', Norm_RPelvisX, '#6495ED')
        # Remove border from graph
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Pelvic tilt', fontsize=10)
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Pst     ($^\circ$)      Ant')
        plt.ylim(0., 60.0)
        plt.legend(('Left', 'Right'), title="Context", fontsize=10, loc='lower right', bbox_to_anchor=(2.3, -5.1),
                   ncol=3, fancybox=True, shadow=True)

        plt.subplot(4, 3, 2)
        # Plot the Y axis of the Model Output
        plot2 = plt.plot(tn, Norm_LPelvisY, '#DC143C', Norm_RPelvisY, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Pelvic obliquity')
        #plt.legend(plot2, ('Left', 'Right'), loc='upper right', shadow=True)
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Dwn     ($^\circ$)      Up')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 3)
        # Plot the Z axis of the Model Output
        plot3 = plt.plot(tn, Norm_LPelvisZ, '#DC143C', Norm_RPelvisZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Pelvic rotation')
        #plt.legend(plot3, ('Left', 'Right'), loc='upper right', shadow=True)
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Bak     ($^\circ$)      For')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 4)
        plot4 = plt.plot(tn, Norm_LHipX, '#DC143C', Norm_RHipX, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip flexion')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Ext     ($^\circ$)      Flex')
        plt.ylim(-20., 70.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 5)
        plot5 = plt.plot(tn, Norm_LHipY, '#DC143C', Norm_RHipY, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip adduction')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Abd     ($^\circ$)      Add')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 6)
        plot6 = plt.plot(tn, Norm_LHipZ, '#DC143C', Norm_RHipZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip rotation')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Ext     ($^\circ$)      Int')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 7)
        plot7 = plt.plot(tn, Norm_LKneeX, '#DC143C', Norm_RKneeX, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee flexion')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Ext     ($^\circ$)      Flex')
        plt.ylim(-15., 75.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 8)
        plot8 = plt.plot(tn, Norm_LKneeY, '#DC143C', Norm_RKneeY, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee adduction')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Val     ($^\circ$)      Var')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 9)
        plot9 = plt.plot(tn, Norm_LKneeZ, '#DC143C', Norm_RKneeZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee rotation')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Ext     ($^\circ$)      Int')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 10)
        plot10 = plt.plot(tn, Norm_LAnkleX, '#DC143C', Norm_RAnkleX, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Dorsiflexion')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Pla     ($^\circ$)      Dor')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 12)
        plot11 = plt.plot(tn, Norm_LFootProZ, '#DC143C', Norm_RFootProZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Foot progression')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Ext     ($^\circ$)      Int')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        pdf.savefig()
        plt.close()

        print('PDF File Created in: ' + NormTrialName)
        print("Completed: Normalized Kinematics Graph")

else:
    sns.set_style("white")
    sns.set_context("paper")

    print("Trial does not contain Gait Cycle Events")

    # Create Graphs from extracted data and save to pdf
    with PdfPages(UnNormTrialName) as pdf:
        plt.figure(figsize=(14, 12))  # Figure size
        plt.suptitle(UnNormGraphTitle, fontsize=12, fontweight="bold")

        plt.subplot(4, 3, 1)  # Layout 4 rows, 3 columns, position 1 - top left
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.5, hspace=0.5)
        # Plot the X axis of the Model Output
        plot1 = plt.plot(range(len(LPelvisA[0][0][0])), LPelvisA[0][0][0], '#DC143C', RPelvisA[0][0][0], '#6495ED')
        # Remove border from graph
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Pelvic tilt', fontsize=10)
        plt.xlabel('Frame number')
        plt.ylabel('Pst     ($^\circ$)      Ant')
        plt.ylim(0., 60.0)
        plt.legend(('Left', 'Right'), title="Context", fontsize=10, loc='lower right', bbox_to_anchor=(2.3, -5.1),
                   ncol=3, fancybox=True, shadow=True)

        plt.subplot(4, 3, 2)
        # Plot the Y axis of the Model Output
        plot2 = plt.plot(range(len(LPelvisA[0][0][1])), LPelvisA[0][0][1], '#DC143C', RPelvisA[0][0][1], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Pelvic obliquity')
        plt.xlabel('Frame number')
        plt.ylabel('Dwn     ($^\circ$)      Up')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 3)
        # Plot the Z axis of the Model Output
        plot3 = plt.plot(range(len(LPelvisA[0][0][2])), LPelvisA[0][0][2], '#DC143C', RPelvisA[0][0][2], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Pelvic rotation')
        plt.xlabel('Frame number')
        plt.ylabel('Bak     ($^\circ$)      For')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 4)
        plot4 = plt.plot(range(len(LHipA[0][0][0])), LHipA[0][0][0], '#DC143C', RHipA[0][0][0], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip flexion')
        plt.xlabel('Frame number')
        plt.ylabel('Ext     ($^\circ$)      Flex')
        plt.ylim(-20., 70.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 5)
        plot5 = plt.plot(range(len(LHipA[0][0][1])), LHipA[0][0][1], '#DC143C', RHipA[0][0][1], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip adduction')
        plt.xlabel('Frame number')
        plt.ylabel('Abd     ($^\circ$)      Add')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 6)
        plot6 = plt.plot(range(len(LHipA[0][0][2])), LHipA[0][0][2], '#DC143C', RHipA[0][0][2], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip rotation')
        plt.xlabel('Frame number')
        plt.ylabel('Ext     ($^\circ$)      Int')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 7)
        plot7 = plt.plot(range(len(LKneeA[0][0][0])), LKneeA[0][0][0], '#DC143C', RKneeA[0][0][0], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee flexion')
        plt.xlabel('Frame number')
        plt.ylabel('Ext     ($^\circ$)      Flex')
        plt.ylim(-15., 75.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 8)
        plot8 = plt.plot(range(len(LKneeA[0][0][1])), LKneeA[0][0][1], '#DC143C', RKneeA[0][0][1], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee adduction')
        plt.xlabel('Frame number')
        plt.ylabel('Val     ($^\circ$)      Var')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 9)
        plot9 = plt.plot(range(len(LKneeA[0][0][2])), LKneeA[0][0][2], '#DC143C', RKneeA[0][0][2], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee rotation')
        plt.xlabel('Frame number')
        plt.ylabel('Ext     ($^\circ$)      Int')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 10)
        plot10 = plt.plot(range(len(LAnkA[0][0][0])), LAnkA[0][0][0], '#DC143C', RAnkA[0][0][0], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Dorsiflexion')
        plt.xlabel('Frame number')
        plt.ylabel('Pla     ($^\circ$)      Dor')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 12)
        plot11 = plt.plot(range(len(LFootPro[0][0][2])), LFootPro[0][0][2], '#DC143C', RFootPro[0][0][2], '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Foot progression')
        plt.xlabel('Frame number')
        plt.ylabel('Ext     ($^\circ$)      Int')
        plt.ylim(-30., 30.0)
        plt.axhline(0, color='black')


        pdf.savefig()
        plt.close()
        print("PDF File Created in: " + UnNormTrialName)
        print('Completed: Kinematics Graph')
