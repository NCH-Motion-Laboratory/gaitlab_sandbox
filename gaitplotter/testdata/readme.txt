Five sample C3D files that contain prescaled force plate data.

The 01 and 02 trials feature POINT and ANALOG data from a
subject dancing on the plate, while the 03 and 04 trials are
simple walks over the force plates producing recognisable
force plate gait data.  Each of these files is stored in the
C3D floating point (REAL) format using the PC/DOS byte order.

In each case, Vicon Motion Systems claims that the force plate
calibration matrix has been applied to the force plate data
before the data is written to the C3D file which explains why
the ANALOG:SCALE parameters for the force plate channels are
all set to 1.00

All trials appear to contain filtered POINT data (residuals
are all set to 0.0).  Trials 1 and 2 appear to contain
corrupted analog data - forces that exceed the FP system
limits or the ADC system input range.

The 04i trial is a copy of the 04 trial converted from the
original (REAL) floating point format into DEC integer.  This
demonstrates the problems caused when inappropriate ANALOG
SCALE factors are chosen - note the corruption in the Mx1
channel as the REAl values exceed the range of the 16-bit
integer format - see int_conv.jpg (int data at the top, with
the original floating point data below).

The choice of the analog scaling factors (GEN_SCALE = 1.0 and
SCALE = 1.0) has effectively forced all analog data into the
range of –32768 +32767 causing data corruption when the file
is converted to INTEGER.

