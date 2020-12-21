# -*- coding: utf-8 -*-
"""
Muscle thickness detection from ultrasound images. Steps:

-read .dcm ultrasound using pydicom
-threshold to get strongest features (muscle edges)
-apply median filter for cleanup
-apply Hough transform to get longest lines
-calculate distance between lines (?)

@author: jnu@iki.fi
"""


# %% init
import pydicom
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from functools import partial
from itertools import combinations
from shapely.geometry import LineString
from shapely.ops import nearest_points
import glob



# fuse line segments into single LineString
#
# -if line startpoints/endpoints are close, replace them by average
# -if line start/endpoints are close to anothers end/startpoints, fuse them
# -if nearby line of same slope



paths = Path(r'I:\Ultraääni').rglob('*long*.dcm')

n = 4
fname = list(paths)[n]

dataset = pydicom.dcmread(fname)
# crop
img = dataset.pixel_array
img = img[50:600, 250:900]


def _threshold(img, threshold):
    ret, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return img


def _hough(img, threshold, minlen, maxgap):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lines = cv2.HoughLinesP(
        img,
        rho=1,
        theta=np.pi / 180,
        threshold=threshold,
        minLineLength=minlen,
        maxLineGap=maxgap,
    ).squeeze()
    return lines


def _erode(img, ksize, nit=1):
    kernel = np.ones(ksize, np.uint8)
    img = cv2.erode(img, kernel, iterations=nit)
    return img


def _dilate(img, ksize, nit=1):
    kernel = np.ones(ksize, np.uint8)
    img_dil = cv2.dilate(img, kernel, iterations=nit)
    return img_dil


def _plot_hough(img, lines):
    fig, ax = plt.subplots()
    ax.imshow(img, cmap=plt.cm.bone)
    ax.set_title('hough lines')
    for line in lines:
        line = line.squeeze()
        line2d = plt.Line2D([line[0], line[2]], [line[1], line[3]], color='r')
        ax.add_line(line2d)


def _plot_line(fig, ax, line):
    line2d = plt.Line2D([line[0], line[2]], [line[1], line[3]], color='r')
    ax.add_line(line2d)



def _line_at_x(line, x):
    """Return line y value at point x"""
    x0, y0, x1, y1 = line
    return (x - x0) * (y1 - y0) / (x1 - x0) + y0


def _line_theta(line):
    """Compute line slope in degrees"""
    x0, y0, x1, y1 = line
    return np.arctan((y1 - y0) / (x1 - x0)) / np.pi * 180


def _apply_ops(img, ops):
    """Apply ops in sequence, plot intermediate results"""
    plt.imshow(img, cmap=plt.cm.bone)
    plt.title('original')
    plt.show()
    for k, op in enumerate(ops, 1):
        img = op(img)
        plt.imshow(img, cmap=plt.cm.bone)
        plt.title('after op %d' % k)
        plt.show()
    return img



def _fuse_lines(lines, MAXDIFF):
    pair_inds = combinations(range(len(lines)), 2)
    for i1, i2 in pair_inds:
        l1, l2 = np.array(lines[i1]), np.array(lines[i2])
        maxdiff = np.abs(l1 - l2).max()
        if maxdiff < MAXDIFF:
            lines[i1] = (l1 + l2) / 2
            lines.pop(i2)
            return _fuse_lines(lines, MAXDIFF)
    return lines


def _slope(ls):
    """LineString slope in degrees"""
    (x0, y0), (x1, y1) = ls.coords
    if (x1 - x0) == 0:
        if y0 < y1:
            return 90
        else:
            return -90
    return np.arctan((y1 - y0) / (x1 - x0)) / np.pi * 180



ops = [
    _threshold,
    partial(_erode, ksize=(5, 5), nit=1),
    partial(_dilate, ksize=(0, 11), nit=4),
]

ops = [
    _threshold,
    partial(_dilate, ksize=(0, 3), nit=3),
]


ops = [_threshold,
    partial(_erode, ksize=(0, 5), nit=1),
    partial(_dilate, ksize=(5, 0), nit=1),
    partial(_erode, ksize=(0, 5), nit=1),
    partial(_dilate, ksize=(5, 0), nit=1),
    partial(_erode, ksize=(0, 5), nit=1),
    partial(_dilate, ksize=(5, 0), nit=1),
    partial(_erode, ksize=(0, 5), nit=1),
    partial(_dilate, ksize=(5, 0), nit=1),
    partial(_erode, ksize=(0, 5), nit=1),
    partial(_dilate, ksize=(5, 0), nit=1),
    partial(_erode, ksize=(0, 5), nit=1),
    partial(_dilate, ksize=(5, 0), nit=1),
]

ops = [
    _threshold,
]

ops = [
    _threshold,
    partial(cv2.medianBlur, ksize=5),
    partial(_dilate, ksize=(0, 11), nit=4),
]


img_fin = _apply_ops(img, ops)

lines = _hough(img_fin, threshold=150, minlen=250, maxgap=20)

lines = _fuse_lines(list(lines), 50)


_plot_hough(img, list(lines))

from collections import defaultdict

raydi = defaultdict(list)
mindist, maxdist = 75, 250
ANGLE_TOL = 5
ymax = 300
linepairs = combinations(lines, 2)
for l1, l2 in linepairs:
    if l1[[1, 3]].max() < ymax and l2[[1, 3]].max() < ymax:    
        ls1 = LineString([l1[:2], l1[2:]])
        ls2 = LineString([l2[:2], l2[2:]])
        for k in np.linspace(0, 1, 10):
            p1 = ls1.interpolate(k, normalized=True)
            p1key = tuple(p1.coords)
            _, p2 = nearest_points(p1, ls2)
            ray = LineString([p1, p2])
            if mindist < ray.length < maxdist:
                if 90 - ANGLE_TOL < abs(_slope(ray) - _slope(ls1)) < 90 + ANGLE_TOL:
                    if 90 - ANGLE_TOL < abs(_slope(ray) - _slope(ls2)) < 90 + ANGLE_TOL:
                        raydi[p1key].append(ray)

raydi_ = dict()
widths = list()
for p, rays in raydi.items():
    raylens = np.array([ray.length for ray in rays])
    shortest_ray = rays[raylens.argmin()]
    widths.append(raylens.min())
    raydi_[p] = np.array(shortest_ray).flatten()

_plot_hough(img, list(lines) + list(raydi_.values()))
#_plot_hough(img, list(lines))

print(np.mean(widths))
print(np.median(widths))










# %% foobar

k = np.linspace(0, 1, 50)

f = 2/5 * (2 + 3*k) / (1 + k)

plt.plot(k * 100, f * 100)
plt.ylabel('Korvaussumma verrattuna todelliseen (%)')
plt.xlabel('Lapsen kustannus aikuiseen verrattuna (%)')



def _line_to_linestring(line):







from shapely.geometry import LineString
from shapely.ops import nearest_points
line = LineString([(0, 0), (1, 1)])
other = LineString([(0, 1), (1, 0)])
print(nearest_points(line, other)[1])





rays = list()
nok = 0
mindist, maxdist = 25, 150
slopediff = 5
ymax = 250
from itertools import combinations
linepairs = combinations(lines, 2)
for l1, l2 in linepairs:
    if l1[[1, 3]].max() < ymax and l2[[1, 3]].max() < ymax:
        ls1 = LineString([l1[:2], l1[2:]])
        ls2 = LineString([l2[:2], l2[2:]])
        p1, p2 = nearest_points(ls1, ls2)
        if mindist < p1.distance(p2) < maxdist and abs(_slope(ls1) - _slope(ls2)) < slopediff:
            print('dist and slope ok:')
            print(l1)
            print(l2)
            nok += 1
            rays.append(l1)
            rays.append(l2)
_plot_hough(img, rays)



# scan through x values
intersects = dict()

for x in np.arange(img.shape[1]):
    intersects[x] = list()
    for line in lines:
        line_ = line.squeeze()
        if line_[0] < x < line_[2]:  # ray intersects line
            ypt = _line_at_x(line, x)
            intersects[x].append(ypt)

widths = list()
rays = list()
for x in intersects:
    if intersects[x]:
        widths.append(max(intersects[x]) - min(intersects[x]))
    if len(intersects[x]) >= 2 and x % 10 == 0:
        ray = np.array([x, min(intersects[x]), x, max(intersects[x])])
        rays.append(ray)


# %% foo

"""
   (0018, 6024) Physical Units X Direction          US: 3
   (0018, 6026) Physical Units Y Direction          US: 3
   (0018, 602c) Physical Delta X                    FD: 0.0087943
   (0018, 602e) Physical Delta Y                    FD: 0.0087943
"""

#assert dataset[(0x0018, 0x6024)] == dataset[(0x0018, 0x6026)]
#deltax = dataset[(0x0018, 0x602c)]

_plot_hough(img, rays)
widths = np.array(widths)
widths_mm = widths * 0.0087943 * 10
widths_mm = widths_mm[np.where(widths_mm > 4)]
print('mean thickness: %.2f mm' % np.mean(widths_mm))
print('median thickness: %.2f mm' % np.median(widths_mm))
    










# %% foo
img_tr = _threshold(img)
img_er = _erode(img_tr, (3, 7), nit=2)
img_dil = _dilate(img_er, (3, 15), nit=4)
lines = _hough(img_dil)


plt.imshow(img, cmap=plt.cm.bone)
plt.title('original')
plt.show()
plt.imshow(img_tr, cmap=plt.cm.bone)
plt.title('thresholded')
plt.show()
plt.imshow(img_er, cmap=plt.cm.bone)
plt.title('eroded')
plt.show()
plt.imshow(img_dil, cmap=plt.cm.bone)
plt.title('dilated')
plt.show()
_plot_hough(img, lines)


# %% foo
plt.imshow(img_den, cmap=plt.cm.bone)
plt.title('denoised')
plt.show()
plt.imshow(img_dil, cmap=plt.cm.bone)
plt.title('dilated')
plt.show()


def _line_param(line, npts=100):
    """Return npts points on line segment defined by (x0, y0, x1, y1)"""
    v = line[2:] - line[:2]
    return line[:2] + np.linspace(0, 1, npts)[:, None] * v





fused = list()
def _fuse(x):
    pairs = combinations(x, 2)
    for a, b in pairs:
        if abs(a - b) > 1:
            fused.append(a)
            fused.append(b)




