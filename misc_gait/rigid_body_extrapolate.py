# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 17:33:49 2019

@author: vicon123
"""


# %% foo
import matplotlib.pyplot as plt
import numpy as np



def _rotation_matrix(yaw, pitch, roll):
    """Rotation matrix from yaw, pitch, roll in degrees"""
    yaw, pitch, roll = np.array([yaw, pitch, roll]) / 180 * np.pi
    cos, sin = np.cos, np.sin
    r1 = [cos(yaw)*cos(pitch),
          cos(yaw)*sin(pitch)*sin(roll)-sin(yaw)*cos(roll),
          cos(yaw)*sin(pitch)*cos(roll)+sin(yaw)*sin(roll)]
    r2 = [sin(yaw)*cos(pitch),
          sin(yaw)*sin(pitch)*sin(roll)+cos(yaw)*cos(roll),
          sin(yaw)*sin(pitch)*cos(roll)-cos(yaw)*sin(roll)]
    r3 = [-sin(pitch), cos(pitch)*sin(roll), cos(pitch)*cos(roll)]
    return np.array([r1, r2, r3])


def _rotation_matrix(yaw, pitch, roll):
    """Rotation matrix from yaw, pitch, roll in degrees"""
    yaw, pitch, roll = np.array([yaw, pitch, roll]) / 180 * np.pi
    for op in (np.cos, np.sin):
        for varname in 'yaw', 'pitch', 'roll':
            print('%s_%s=%s' % (op.__name__, varname, op(eval(varname))))



def kabsch_rotation(P, Q):
    """Calculate a rotation matrix P->Q using the Kabsch algorithm"""
    H = np.dot(P.T, Q)
    U, S, V = np.linalg.svd(H)
    E = np.eye(3)
    E[2, 2] = np.sign(np.linalg.det(np.dot(V.T, U.T)))
    return np.dot(np.dot(V.T, E), U.T)


P = np.array([[1, 0, 0], [2, 0, 0], [3, 0, 0]])
Q = np.array([[6, 0, 1], [5, 0, 0], [4, 0, 0]])



# test: first make pts1 from pts0 by rotation + translation,
# then recover rot & trans by the Kabsch algorithm
# define four corner points in a plane (our rigid body)
yaw, pitch, roll = np.random.rand(3) * 360
R = _rotation_matrix(yaw, pitch, roll)
pts0 = np.array([[1, 1, 0], [-1, 1, 0], [-1, -1, 0], [2, 2, 0], [1, -1, 0]]).astype(np.float64)
trans0 = pts0.mean(axis=0)
pts0 -= trans0
translation = np.random.randn(1, 3)
pts1 = np.dot(R, pts0.T).T + translation

trans1 = pts1.mean(axis=0)
pts1_ = pts1 - trans1

R_kabsch = kabsch_rotation(pts0, pts1_)

# check the results
print('Kabsch rotation:')
print(R_kabsch)
print('Original rotation:')
print(R)

print('True pts1:')
print(pts1)
print('Computed ptsi:')
pts_ = np.dot(R_kabsch, pts0.T).T + trans1
print(pts_)



def extrapolate_rigid_set(P0, Pr):
    """Extrapolate some markers in a rigid set.
    P0 (N x 3), the marker positions in the static frame.
    Pr (M x 3), the marker positions in where extrapolation is needed.
    N-M markers will be extrapolated.
    
    Algorithm:
    -find R and t that go from Pr0 -> Pr by Kabsch algorithm
    -apply R and t to p to get the extrapolated position
    """
    nref = Pr.shape[0]
    if P0.shape <= nref:
        raise ValueError('1st dim of P0 needs to be larger than 1st dim of Pr')
    Pr0 = P0[:nref, :]  # reference markers
    # find rotation and translation that take the static reference position to the
    # position where extrapolation is needed; then apply this transformation to the
    # markers to be extrapolated
    trans0 = Pr0.mean(axis=0)
    Pr0_ = Pr0 - trans0
    P0_ = P0 - trans0
    trans1 = Pr.mean(axis=0)
    Pr_ = Pr - trans1
    R = kabsch_rotation(Pr0_, Pr_)
    return np.dot(R, P0_[nref:, :].T).T + trans1 


# %% from Nexus
# for static trial: read reference positions of markers to be extrapolated
mdata = gaitutils.read_data.get_marker_data(vicon, ['LASI', 'PELVIS_LEFT', 'PELVIS_FRONT', 'RPSI', 'RASI', 'LPSI'])
frame = 10
P0 = np.row_stack((mdata['LASI'][frame, :], mdata['PELVIS_LEFT'][frame, :],
                     mdata['PELVIS_FRONT'][frame, :], mdata['RPSI'][frame, :],
                     mdata['RASI'][frame, :], mdata['LPSI'][frame, :]))


# %% this is for dynamic
from collections import defaultdict
mdata = gaitutils.read_data.get_marker_data(vicon, ['LASI', 'PELVIS_LEFT', 'PELVIS_FRONT'])
to_interp = ['RPSI', 'RASI', 'LPSI']
interp_coords = defaultdict(list)

for frame in range(vicon.GetFrameCount()):
    Pr = np.row_stack((mdata['LASI'][frame, :], mdata['PELVIS_LEFT'][frame, :],
                        mdata['PELVIS_FRONT'][frame, :]))
    ic = extrapolate_rigid_set(P0, Pr)
    for marker, pos in zip(to_interp, ic):
        interp_coords[marker].append(pos)

for marker, vals in interp_coords.items():
    vals_array = np.array(vals)
    vicon.SetTrajectory('04_Alisa', marker, vals_array[:, 0], vals_array[:, 1], vals_array[:, 2], [True] * vicon.GetFrameCount())




"""
ui for rigid body fill:

-instruct user to load static data
-select ref. marker set and markers to be extrapolated
-read 'static' frames
    -use avg. or 1st frame for P0
-instruct user to load trial where to do extrapolation
-read ref. markers
-run extrapolate_rigid_set()
-write results back to Nexus













# %% test it
pts0 = np.array([[1, 1, 0], [-1, 1, 0], [-1, -1, 0], [2, 2, 0], [1, -1, 0]]).astype(np.float64)
trans0 = pts0.mean(axis=0)
pts0 -= trans0

for k in range(100):
    yaw, pitch, roll = np.random.rand(3) * 360
    R = _rotation_matrix(yaw, pitch, roll)
    translation = np.random.randn(1, 3)
    pts1 = (R@pts0.T).T + translation
    print('pts1:')
    print(pts1)
    print('extrap:')
    print(extrapolate_rigid_set(pts0, pts1[:-1, :]))






# %% foo

def extrapolate_rigid_set(P0, P):
    """Extrapolate marker in a rigid set.

    P0 (N x 3), where N>=4, the marker positions in the static frame.
    The target marker is the last row.
    P (N-1 x 3 x T) gives the reference marker positions to extrapolate from.
    """
    Nref = P0.shape[0]
    if Nref < 3:
        raise ValueError('Need at least 3 reference markers')
    P0r = P0[:-1, :]  # the reference cluster
    r0 = np.mean(P0r, axis=0)
    P0r -= r0
    # 3 points are always going to be coplanar, so we need to shift the origin away
    # from the plane; we shift towards the plane normal
    if Nref == 3:
        ref_plane_normal = np.cross(P0r[0, :], P0r[1, :])
        P0r -= ref_plane_normal
        r0 += ref_plane_normal
    # solve for p (target marker) in the local coordinate system
    p = P0[-1, :] - r0
    x = np.linalg.pinv(P0r.T) @ p
    # get the coords
    P_ = P - r0
    return P_.T @ x



# define four corner points in a plane (our rigid body)
pts = np.array([[1, 1, 0], [-1, 1, 0], [-1, -1, 0], [2, 2, 0], [1, -1, 0]]).astype(np.float64)

# make the random initial points by 3d rotation and translation
yaw, pitch, roll = np.random.rand(3) * 360
R = _rotation_matrix(yaw, pitch, roll)
pts0 = (R@pts.T).T + np.random.randn(5, 3)

extrapolate_rigid_set(pts, pts0[:4, :])






# %%
import numpy as np


def _rotation_matrix(yaw, pitch, roll):
    """Rotation matrix from yaw, pitch, roll in degrees"""
    yaw, pitch, roll = np.array([yaw, pitch, roll]) / 180 * np.pi
    cos, sin = np.cos, np.sin
    r1 = [cos(yaw)*cos(pitch),
          cos(yaw)*sin(pitch)*sin(roll)-sin(yaw)*cos(roll),
          cos(yaw)*sin(pitch)*cos(roll)+sin(yaw)*sin(roll)]
    r2 = [sin(yaw)*cos(pitch),
          sin(yaw)*sin(pitch)*sin(roll)+cos(yaw)*cos(roll),
          sin(yaw)*sin(pitch)*cos(roll)-cos(yaw)*sin(roll)]
    r3 = [-sin(pitch), cos(pitch)*sin(roll), cos(pitch)*cos(roll)]
    return np.array([r1, r2, r3])

# define four corner points in a plane (our rigid body)
pts = np.array([[1, 1, 0], [-1, 1, 0], [-1, -1, 0], [1, -1, 0]])

# make the random initial points by 3d rotation and translation
yaw, pitch, roll = np.random.rand(3) * 360
R = _rotation_matrix(yaw, pitch, roll)
pts0 = (R@pts.T).T + np.random.randn(4, 3)

# get the local coords
pts_ref = pts0[:3, :].copy()
r0 = np.mean(pts_ref, axis=0)
p_ = pts0[3, :] - r0
pts_ref_ = pts_ref - r0
#pts_plane_normal = np.cross(pts_ref_[0, :], pts_ref_[1, :])
#pts_ref_ = pts_ref_ + pts_plane_normal

x = np.linalg.pinv(pts_ref_.T) @ p_
print(pts_ref_.T @ x)
print(p_)

print(pts_ref_.T @ x + r0)  # should equal p
print(p_ + r0)



# %% foo
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(pts_ref_[:, 0], pts_ref_[:, 1], pts_ref_[:, 2])



# %% foo






# %%verify (random rotations & movements)
for k in range(10):
    yaw, pitch, roll = np.random.rand(3) * 360
    R = _rotation_matrix(yaw, pitch, roll)
    ptsR = (R@pts.T).T + np.random.randn(4, 3)
    cctr = np.mean(ptsR, axis=0)
    ptsR0 = ptsR - cctr  # center
    pest = ptsR0[:3, :].T @ x + cctr
    print(pest)
    print(ptsR)







# %% foo
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(ptsR[:, 0], ptsR[:, 1], ptsR[:, 2])




# %% foo

""" algo:
-pts in 4x3 matrix
-define local coord system using markers 1-3:
-use SVD: P = U S V*, columns of V give a basis
-solve coords for marker 4 in this basis: x = V.T @ pts[3, :]









find p4 coords in local coordinate system




# %% test the gaitutils implementation

import gaitutils


vicon = gaitutils.nexus.viconnexus()



# %% for pelvis
ref_trial = r"C:\Temp\04_Alisa\2020_9_10_robot\03"

extrap_trials = [r"C:\Temp\04_Alisa\2020_9_10_robot\06", r"C:\Temp\04_Alisa\2020_9_10_robot\07"]
extrap_trials = [r"C:\Temp\04_Alisa\2020_9_10_robot\%02d" % n for n in range(4, 18)]

ref_markers = ['LASI', 'PELVIS_LEFT', 'PELVIS_FRONT']
extrap_markers = ['RPSI', 'RASI', 'LPSI']

gaitutils.nexus.rigid_body_extrapolate(vicon, ref_trial, extrap_trials, ref_markers, extrap_markers)


# %% for ankle
ref_trial = r"C:\Temp\04_Alisa\2020_9_10_robot\10"




extrap_trials = [r"C:\Temp\04_Alisa\2020_9_10_robot\10"]
#extrap_trials = [r"C:\Temp\04_Alisa\2020_9_10_robot\%02d" % n for n in range(4, 18)]

ref_markers = ['RTOE', 'RTIB', 'RANK']
extrap_markers = ['RHEE']

gaitutils.nexus.rigid_body_extrapolate(vicon, ref_trial, extrap_trials, ref_markers, extrap_markers, ref_frame=0)




# %% for pelvis

import gaitutils
vicon = gaitutils.nexus.viconnexus()


ref_trial = r"C:\Temp\04_Alisa\2020_9_10_robot_(Max_data)\03"
extrap_trials =[r"C:\Temp\04_Alisa\2020_9_10_robot_(Max_data)\%02d" % n for n in range(4, 11)]

extrap_trials =[r"C:\Temp\04_Alisa\2020_9_10_robot_(Max_data)\10"]

ref_markers = ['LASI', 'PELVIS_LEFT', 'PELVIS_FRONT']
extrap_markers = ['RPSI', 'RASI', 'LPSI']

gaitutils.nexus.rigid_body_extrapolate(vicon, ref_trial, extrap_trials, ref_markers, extrap_markers)


# %%

# %% for pelvis

import gaitutils
vicon = gaitutils.nexus.viconnexus()

import logging

logging.basicConfig(level=logging.DEBUG)

ref_trial = r"C:\Temp\2020_9_4_robot\2020_9_4_robot02.c3d"
extrap_trials =[r"C:\Temp\2020_9_4_robot\2020_9_4_robot%02d.c3d" % n for n in range(4, 11)]
extrap_trials =[r"C:\Temp\2020_9_4_robot\2020_9_4_robot06.c3d"]

ref_markers = ['LASI', 'RASI', 'LSIDE']
extrap_markers = ['LPSI', 'RPSI']

gaitutils.nexus.rigid_body_extrapolate(vicon, ref_trial, extrap_trials, ref_markers, extrap_markers, ref_frame=10)


# %% auto find trials
import gaitutils

vicon = gaitutils.nexus.viconnexus()

sp = gaitutils.nexus.get_sessionpath()

import logging

logging.basicConfig(level=logging.DEBUG)

ref_markers = ['T10', 'STRN', 'CLAV']
extrap_markers = ['C7']

stat_trial = sorted(gaitutils.sessionutils.get_c3ds(sp, trial_type='static'))[-1]
dyn_trials = gaitutils.sessionutils.get_c3ds(sp, trial_type='dynamic')

gaitutils.nexus.rigid_body_extrapolate(vicon, stat_trial, dyn_trials, ref_markers, extrap_markers, ref_frame=68)




