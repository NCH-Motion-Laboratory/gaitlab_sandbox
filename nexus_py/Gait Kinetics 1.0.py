from __future__ import division, print_function

__filename__ = "Gait Kinetics 1.0"
__version__ = "1.0"
__company__ = "Vicon Motion System"
__date__ = "2014"
__author__ = "jgay"

# This Python Code is an example code created to work in conjunction with Vicon Nexus 2 and processed Lower Body
# Plug-in Gait Data. The code needs to be run from within Vicon Nexus 2.
# Data needs to contain at least one left and right complete gait cycle(for Normalized data) and force plate strike.
# The newly created pdf file will be saved in your Session Folder.

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
NormTrialName = SessionLoc + vicon.GetTrialName()[1] + "_Normalized Kinetics.pdf"
NormGraphTitle = "Kinetics for " + vicon.GetTrialName()[1] + " Normalized to Gait Cycle"

# If the data does not contain events to normalise create the file name and graph title
UnNormTrialName = SessionLoc + vicon.GetTrialName()[1] + "_Kinetics.pdf"
UnNormGraphTitle = "Kinetics for " + vicon.GetTrialName()[1]

LKneeA = np.array([vicon.GetModelOutput(SubjectName, 'LKneeAngles')])
RKneeA = np.array([vicon.GetModelOutput(SubjectName, 'RKneeAngles')])

myInt = 1000

# Extract Plug-in Gait Lower Body Model Outputs using numpy
LHipM = np.array([vicon.GetModelOutput(SubjectName, 'LHipMoment')])
LHipMX = np.array([vicon.GetModelOutput(SubjectName, 'LHipMoment')][0][0][0])
LHipMY = np.array([vicon.GetModelOutput(SubjectName, 'LHipMoment')][0][0][1])
LHipMZ = np.array([vicon.GetModelOutput(SubjectName, 'LHipMoment')][0][0][2])
LHipMXD = [i/myInt for i in LHipMX]
LHipMYD = [i/myInt for i in LHipMY]
LHipMZD = [i/myInt for i in LHipMZ]

RHipM = np.array([vicon.GetModelOutput(SubjectName, 'RHipMoment')])
RHipMX = np.array([vicon.GetModelOutput(SubjectName, 'RHipMoment')][0][0][0])
RHipMY = np.array([vicon.GetModelOutput(SubjectName, 'RHipMoment')][0][0][1])
RHipMZ = np.array([vicon.GetModelOutput(SubjectName, 'RHipMoment')][0][0][2])
RHipMXD = [i/myInt for i in RHipMX]
RHipMYD = [i/myInt for i in RHipMY]
RHipMZD = [i/myInt for i in RHipMZ]

LKneeM = np.array([vicon.GetModelOutput(SubjectName, 'LKneeMoment')])
LKneeMX = np.array([vicon.GetModelOutput(SubjectName, 'LKneeMoment')][0][0][0])
LKneeMY = np.array([vicon.GetModelOutput(SubjectName, 'LKneeMoment')][0][0][1])
LKneeMZ = np.array([vicon.GetModelOutput(SubjectName, 'LKneeMoment')][0][0][2])
LKneeMXD = [i/myInt for i in LKneeMX]
LKneeMYD = [i/myInt for i in LKneeMY]
LKneeMZD = [i/myInt for i in LKneeMZ]

RKneeM = np.array([vicon.GetModelOutput(SubjectName, 'RKneeMoment')])
RKneeMX = np.array([vicon.GetModelOutput(SubjectName, 'RKneeMoment')][0][0][0])
RKneeMY = np.array([vicon.GetModelOutput(SubjectName, 'RKneeMoment')][0][0][1])
RKneeMZ = np.array([vicon.GetModelOutput(SubjectName, 'RKneeMoment')][0][0][2])
RKneeMXD = [i/myInt for i in RKneeMX]
RKneeMYD = [i/myInt for i in RKneeMY]
RKneeMZD = [i/myInt for i in RKneeMZ]

LAnkM = np.array([vicon.GetModelOutput(SubjectName, 'LAnkleMoment')])
LAnkMX = np.array([vicon.GetModelOutput(SubjectName, 'LAnkleMoment')][0][0][0])
LAnkMY = np.array([vicon.GetModelOutput(SubjectName, 'LAnkleMoment')][0][0][1])
LAnkMZ = np.array([vicon.GetModelOutput(SubjectName, 'LAnkleMoment')][0][0][2])
LAnkMXD = [i/myInt for i in LAnkMX]
LAnkMYD = [i/myInt for i in LAnkMY]
LAnkMZD = [i/myInt for i in LAnkMZ]

RAnkM = np.array([vicon.GetModelOutput(SubjectName, 'RAnkleMoment')])
RAnkMX = np.array([vicon.GetModelOutput(SubjectName, 'RAnkleMoment')][0][0][0])
RAnkMY = np.array([vicon.GetModelOutput(SubjectName, 'RAnkleMoment')][0][0][1])
RAnkMZ = np.array([vicon.GetModelOutput(SubjectName, 'RAnkleMoment')][0][0][2])
RAnkMXD = [i/myInt for i in RAnkMX]
RAnkMYD = [i/myInt for i in RAnkMY]
RAnkMZD = [i/myInt for i in RAnkMZ]

LHipP = np.array([vicon.GetModelOutput(SubjectName, 'LHipPower')])
LHipPZ = np.array([vicon.GetModelOutput(SubjectName, 'LHipPower')][0][0][2])
#LHipPZD = [i/myInt for i in LHipPZ]

RHipP = np.array([vicon.GetModelOutput(SubjectName, 'RHipPower')])
RHipPZ = np.array([vicon.GetModelOutput(SubjectName, 'RHipPower')][0][0][2])
#RHipPZD = [i/myInt for i in RHipPZ]

LKneeP = np.array([vicon.GetModelOutput(SubjectName, 'LKneePower')])
LKneePZ = np.array([vicon.GetModelOutput(SubjectName, 'LKneePower')][0][0][2])
#LKneePZD = [i/myInt for i in LKneePZ]

RKneeP = np.array([vicon.GetModelOutput(SubjectName, 'RKneePower')])
RKneePZ = np.array([vicon.GetModelOutput(SubjectName, 'RKneePower')][0][0][2])

LAnkP = np.array([vicon.GetModelOutput(SubjectName, 'LAnklePower')])
LAnkPZ = np.array([vicon.GetModelOutput(SubjectName, 'LAnklePower')][0][0][2])

RAnkP = np.array([vicon.GetModelOutput(SubjectName, 'RAnklePower')])
RAnkPZ = np.array([vicon.GetModelOutput(SubjectName, 'RAnklePower')][0][0][2])


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
    LGC1LHipX = LHipMXD[LGC1Start:LGC1End]
    LGC1LKneeX = LKneeMXD[LGC1Start:LGC1End]
    LGC1LAnkX = LAnkMXD[LGC1Start:LGC1End]
    #Left Gait Cycle 1 Y
    LGC1LHipY = LHipMYD[LGC1Start:LGC1End]
    LGC1LKneeY = LKneeMYD[LGC1Start:LGC1End]
    LGC1LAnkY = LAnkMYD[LGC1Start:LGC1End]
    #Left Gait Cycle 1 Z
    LGC1LHipZ = LHipMZD[LGC1Start:LGC1End]
    LGC1TLHipZ = LHipPZ[LGC1Start:LGC1End]
    LGC1LKneeZ = LKneeMZD[LGC1Start:LGC1End]
    LGC1TLKneeZ = LKneePZ[LGC1Start:LGC1End]
    LGC1LAnkZ = LAnkMZD[LGC1Start:LGC1End]
    LGC1TLAnkZ = LAnkPZ[LGC1Start:LGC1End]

    #Right Gait Cycle 1 X
    RGC1RHipX = RHipMXD[RGC1Start:RGC1End]
    RGC1RKneeX = RKneeMXD[RGC1Start:RGC1End]
    RGC1RAnkX = RAnkMXD[RGC1Start:RGC1End]
    #Right Right Gait Cycle 1 Y
    RGC1RHipY = RHipMYD[RGC1Start:RGC1End]
    RGC1RKneeY = RKneeMYD[RGC1Start:RGC1End]
    RGC1RAnkY = RAnkMYD[RGC1Start:RGC1End]
    #Right Gait Cycle 1 Z
    RGC1RHipZ = RHipMZD[RGC1Start:RGC1End]
    RGC1TRHipZ = RHipPZ[RGC1Start:RGC1End]
    RGC1RKneeZ = RKneeMZD[RGC1Start:RGC1End]
    RGC1TRKneeZ = RKneePZ[RGC1Start:RGC1End]
    RGC1RAnkZ = RAnkMZD[RGC1Start:RGC1End]
    RGC1TRAnkZ = RAnkPZ[RGC1Start:RGC1End]

    tn = np.linspace(0, 100, 101)
    LGC1t = np.linspace(0, 100, len(LGC1LKneeX))
    RGC1t = np.linspace(0, 100, len(RGC1RKneeX))

    Norm_LGC1LHipX = np.interp(tn, LGC1t, LGC1LHipX)
    Norm_LGC1LKneeX = np.interp(tn, LGC1t, LGC1LKneeX)
    Norm_LGC1LAnkX = np.interp(tn, LGC1t, LGC1LAnkX)

    Norm_LGC1LHipY = np.interp(tn, LGC1t, LGC1LHipY)
    Norm_LGC1LKneeY = np.interp(tn, LGC1t, LGC1LKneeY)
    Norm_LGC1LAnkY = np.interp(tn, LGC1t, LGC1LAnkY)

    Norm_LGC1LHipZ = np.interp(tn, LGC1t, LGC1LHipZ)
    Norm_LGC1TLHipZ = np.interp(tn, LGC1t, LGC1TLHipZ)
    Norm_LGC1LKneeZ = np.interp(tn, LGC1t, LGC1LKneeZ)
    Norm_LGC1TLKneeZ = np.interp(tn, LGC1t, LGC1TLKneeZ)
    Norm_LGC1LAnkZ = np.interp(tn, LGC1t, LGC1LAnkZ)
    Norm_LGC1TLAnkZ = np.interp(tn, LGC1t, LGC1TLAnkZ)

    Norm_LHipX = Norm_LGC1LHipX
    Norm_LHipY = Norm_LGC1LHipY
    Norm_LHipZ = Norm_LGC1LHipZ
    Norm_TLHipZ = Norm_LGC1TLHipZ
    Norm_LKneeX = Norm_LGC1LKneeX
    Norm_LKneeY = Norm_LGC1LKneeY
    Norm_LKneeZ = Norm_LGC1LKneeZ
    Norm_TLKneeZ = Norm_LGC1TLKneeZ
    Norm_LAnkleX = Norm_LGC1LAnkX
    Norm_LAnkleY = Norm_LGC1LAnkY
    Norm_LAnkleZ = Norm_LGC1LAnkZ
    Norm_TLAnkleZ = Norm_LGC1TLAnkZ

    Norm_RGC1RHipX = np.interp(tn, RGC1t, RGC1RHipX)
    Norm_RGC1RKneeX = np.interp(tn, RGC1t, RGC1RKneeX)
    Norm_RGC1RAnkX = np.interp(tn, RGC1t, RGC1RAnkX)

    Norm_RGC1RHipY = np.interp(tn, RGC1t, RGC1RHipY)
    Norm_RGC1RKneeY = np.interp(tn, RGC1t, RGC1RKneeY)
    Norm_RGC1RAnkY = np.interp(tn, RGC1t, RGC1RAnkY)

    Norm_RGC1RHipZ = np.interp(tn, RGC1t, RGC1RHipZ)
    Norm_RGC1TRHipZ = np.interp(tn, RGC1t, RGC1TRHipZ)
    Norm_RGC1RKneeZ = np.interp(tn, RGC1t, RGC1RKneeZ)
    Norm_RGC1TRKneeZ = np.interp(tn, RGC1t, RGC1TRKneeZ)
    Norm_RGC1RAnkZ = np.interp(tn, RGC1t, RGC1RAnkZ)
    Norm_RGC1TRAnkZ = np.interp(tn, RGC1t, RGC1TRAnkZ)

    Norm_RHipX = Norm_RGC1RHipX
    Norm_RHipY = Norm_RGC1RHipY
    Norm_RHipZ = Norm_RGC1RHipZ
    Norm_TRHipZ = Norm_RGC1TRHipZ
    Norm_RKneeX = Norm_RGC1RKneeX
    Norm_RKneeY = Norm_RGC1RKneeY
    Norm_RKneeZ = Norm_RGC1RKneeZ
    Norm_TRKneeZ = Norm_RGC1TRKneeZ
    Norm_RAnkleX = Norm_RGC1RAnkX
    Norm_RAnkleY = Norm_RGC1RAnkY
    Norm_RAnkleZ = Norm_RGC1RAnkZ
    Norm_TRAnkleZ = Norm_RGC1TRAnkZ

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
        plot1 = plt.plot(tn, Norm_LHipX, '#DC143C', Norm_RHipX, '#6495ED')
        # Remove border from graph
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip extensor moment', fontsize=10)
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Flex     (Nm/kg      Ext')
        plt.ylim(-2.0, 3.0)
        plt.legend(('Left', 'Right'), title="Context", fontsize=10, loc='lower right', bbox_to_anchor=(2.3, -5.1),
                   ncol=3, fancybox=True, shadow=True)

        plt.subplot(4, 3, 2)
        # Plot the Y axis of the Model Output
        plot2 = plt.plot(tn, Norm_LHipY, '#DC143C', Norm_RHipY, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip abductor moment')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Abd     (Nm/kg)      Add')
        plt.ylim(-1.0, 2.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 3)
        # Plot the Z axis of the Model Output
        plot3 = plt.plot(tn, Norm_LHipZ, '#DC143C', Norm_RHipZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip rotation moment')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Ext     (Nm/kg)      Int')
        plt.ylim(-0.5, 0.5)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 4)
        plot4 = plt.plot(tn, Norm_LKneeX, '#DC143C', Norm_RKneeX, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee extensor moment')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Ext     (Nm/kg)      Flex')
        plt.ylim(-1.0, 1.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 5)
        plot5 = plt.plot(tn, Norm_LKneeY, '#DC143C', Norm_RKneeY, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee abductor moment')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Valg     (Nm/kg)      Var')
        plt.ylim(-1.0, 1.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 6)
        plot6 = plt.plot(tn, Norm_LKneeZ, '#DC143C', Norm_RKneeZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee rotation moment')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Ext     (Nm/kg)      Int')
        plt.ylim(-0.5, 0.5)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 7)
        plot7 = plt.plot(tn, Norm_LAnkleX, '#DC143C', Norm_RAnkleX, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Plantarflexor moment')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Plan     (Nm/kg)      Dors')
        plt.ylim(-1.0, 3.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 8)
        plot8 = plt.plot(tn, Norm_LAnkleY, '#DC143C', Norm_RAnkleY, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Ankle everter moment')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Abd     (Nm/kg)      Add')
        plt.ylim(-0.5, 0.5)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 9)
        plot9 = plt.plot(tn, Norm_LAnkleZ, '#DC143C', Norm_RAnkleZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Ankle rotation moment')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Ext     (Nm/kg)      Int')
        plt.ylim(-0.5, 0.5)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 10)
        plot10 = plt.plot(tn, Norm_TLHipZ, '#DC143C', Norm_TRHipZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Total hip power')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Abs     (W)      Gen')
        plt.ylim(-3.0, 3.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 11)
        plot10 = plt.plot(tn, Norm_TLKneeZ, '#DC143C', Norm_TRKneeZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Total knee power')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Abs     (W)      Gen')
        plt.ylim(-3.0, 3.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 12)
        plot11 = plt.plot(tn, Norm_TLAnkleZ, '#DC143C', Norm_TRAnkleZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Foot ankle power')
        plt.xlabel('Percentage Gait Cycle (%)')
        plt.ylabel('Abs     (W)      Gen')
        plt.ylim(-2.0, 5.0)
        plt.axhline(0, color='black')

        pdf.savefig()
        plt.show()

        print('PDF File Created in: ' + NormTrialName)
        print("Completed: Normalized Kinetics Graph")

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
        plot1 = plt.plot(range(len(LHipMXD)), LHipMXD, '#DC143C', RHipMXD, '#6495ED')
        # Remove border from graph
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip extensor moment', fontsize=10)
        plt.xlabel('Frame number')
        plt.ylabel('Flex     (Nm/kg)      Ext')
        plt.ylim(-2.0, 3.0)
        plt.axhline(0, color='black')
        plt.legend(('Left', 'Right'), title="Context", fontsize=10, loc='lower right', bbox_to_anchor=(2.3, -5.1),
                   ncol=3, fancybox=True, shadow=True)

        plt.subplot(4, 3, 2)
        # Plot the Y axis of the Model Output
        plot2 = plt.plot(range(len(LHipMYD)), LHipMYD, '#DC143C', RHipMYD, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip abductor moment')
        plt.xlabel('Frame number')
        plt.ylabel('Abd     (Nm/kg)      Add')
        plt.ylim(-1.0, 2.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 3)
        # Plot the Z axis of the Model Output
        plot3 = plt.plot(range(len(LHipMZD)), LHipMZD, '#DC143C', RHipMZD, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Hip rotation moment')
        plt.xlabel('Frame number')
        plt.ylabel('Ext     (Nm/kg)      Int')
        plt.ylim(-0.5, 0.5)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 4)
        plot4 = plt.plot(range(len(LKneeMXD)), LKneeMXD, '#DC143C', RKneeMXD, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee extensor moment')
        plt.xlabel('Frame number')
        plt.ylabel('Ext     (Nm/kg)      Flex')
        plt.ylim(-1.0, 1.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 5)
        plot5 = plt.plot(range(len(LKneeMYD)), LKneeMYD, '#DC143C', RKneeMYD, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee abductor moment')
        plt.xlabel('Frame number')
        plt.ylabel('Valg     (Nm/kg)      Var')
        plt.ylim(-1.0, 1.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 6)
        plot6 = plt.plot(range(len(LKneeMZD)), LKneeMZD, '#DC143C', RKneeMZD, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Knee rotation moment')
        plt.xlabel('Frame number')
        plt.ylabel('Ext     (Nm/kg)      Int')
        plt.ylim(-0.5, 0.5)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 7)
        plot7 = plt.plot(range(len(LAnkMXD)), LAnkMXD, '#DC143C', RAnkMXD, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Plantarflexor moment')
        plt.xlabel('Frame number')
        plt.ylabel('Plan     (Nm/kg)      Dors')
        plt.ylim(-1.0, 3.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 8)
        plot8 = plt.plot(range(len(LAnkMYD)), LAnkMYD, '#DC143C', RAnkMYD, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Ankle everter moment')
        plt.xlabel('Frame number')
        plt.ylabel('Abd     (Nm/kg)      Add')
        plt.ylim(-0.5, 0.5)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 9)
        plot9 = plt.plot(range(len(LAnkMZD)), LAnkMZD, '#DC143C', RAnkMZD, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Ankle rotation moment')
        plt.xlabel('Frame number')
        plt.ylabel('Ext     (Nm)      Int')
        plt.ylim(-0.5, 0.5)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 10)
        plot10 = plt.plot(range(len(LHipPZ)), LHipPZ, '#DC143C', RHipPZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Total hip power')
        plt.xlabel('Frame number')
        plt.ylabel('Abs     (W/kg)      Gen')
        plt.ylim(-3.0, 3.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 11)
        plot10 = plt.plot(range(len(LKneePZ)), LKneePZ, '#DC143C', RKneePZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Total knee power')
        plt.xlabel('Frame number')
        plt.ylabel('Abs     (W/kg)      Gen')
        plt.ylim(-3.0, 3.0)
        plt.axhline(0, color='black')

        plt.subplot(4, 3, 12)
        plot11 = plt.plot(range(len(LAnkPZ)), LAnkPZ, '#DC143C', RAnkPZ, '#6495ED')
        sns.despine(fig=None, ax=None, top=True, right=True, left=False, bottom=False, trim=False)
        plt.title('Total ankle power')
        plt.xlabel('Frame number')
        plt.ylabel('Abs     (W/kg)      Gen')
        plt.ylim(-2.0, 5.0)
        plt.axhline(0, color='black')


        pdf.savefig()
        plt.close()
        print("PDF File Created in: " + UnNormTrialName)
        print('Completed: Kinetics Graph')
