#  python rasterize_polygon.py test_poly1.csv cells1.csv 2
#
# Author: Randy Heiland
#
__author__ = "Randy Heiland"

import sys
import os
import csv
# import xml.etree.ElementTree as ET
import math
#from svg.path import parse_path, Path, Move
import itertools

try:
  import matplotlib
  from matplotlib.patches import Circle, Ellipse, Rectangle
  from matplotlib.collections import PatchCollection
except:
  print("\n---Error: cannot import matplotlib")
  print("---Try: python -m pip install matplotlib")
#   print(join_our_list)
#  print("---Consider installing Anaconda's Python 3 distribution.\n")
  raise
try:
  import numpy as np  # if mpl was installed, numpy should have been too.
except:
  print("\n---Error: cannot import numpy")
  print("---Try: python -m pip install numpy\n")
#   print(join_our_list)
  raise

import matplotlib.pyplot as plt
from collections import deque
from operator import add


print("# args=",len(sys.argv)-1)
# fname = "rwh1b.svg"
lsegs_file = sys.argv[1]
#cells_out_file = "test_cells.csv"
cells_out_file = sys.argv[2]
cell_id = int(sys.argv[3])

#-----------------------------------------------------
def circles(x, y, s, c='b', vmin=None, vmax=None, **kwargs):
    """
    See https://gist.github.com/syrte/592a062c562cd2a98a83 

    Make a scatter plot of circles. 
    Similar to plt.scatter, but the size of circles are in data scale.
    Parameters
    ----------
    x, y : scalar or array_like, shape (n, )
        Input data
    s : scalar or array_like, shape (n, ) 
        Radius of circles.
    c : color or sequence of color, optional, default : 'b'
        `c` can be a single color format string, or a sequence of color
        specifications of length `N`, or a sequence of `N` numbers to be
        mapped to colors using the `cmap` and `norm` specified via kwargs.
        Note that `c` should not be a single numeric RGB or RGBA sequence 
        because that is indistinguishable from an array of values
        to be colormapped. (If you insist, use `color` instead.)  
        `c` can be a 2-D array in which the rows are RGB or RGBA, however. 
    vmin, vmax : scalar, optional, default: None
        `vmin` and `vmax` are used in conjunction with `norm` to normalize
        luminance data.  If either are `None`, the min and max of the
        color array is used.
    kwargs : `~matplotlib.collections.Collection` properties
        Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls), 
        norm, cmap, transform, etc.
    Returns
    -------
    paths : `~matplotlib.collections.PathCollection`
    Examples
    --------
    a = np.arange(11)
    circles(a, a, s=a*0.2, c=a, alpha=0.5, ec='none')
    plt.colorbar()
    License
    --------
    This code is under [The BSD 3-Clause License]
    (http://opensource.org/licenses/BSD-3-Clause)
    """

    if np.isscalar(c):
        kwargs.setdefault('color', c)
        c = None

    if 'fc' in kwargs:
        kwargs.setdefault('facecolor', kwargs.pop('fc'))
    if 'ec' in kwargs:
        kwargs.setdefault('edgecolor', kwargs.pop('ec'))
    if 'ls' in kwargs:
        kwargs.setdefault('linestyle', kwargs.pop('ls'))
    if 'lw' in kwargs:
        kwargs.setdefault('linewidth', kwargs.pop('lw'))
    # You can set `facecolor` with an array for each patch,
    # while you can only set `facecolors` with a value for all.

    zipped = np.broadcast(x, y, s)
    patches = [Circle((x_, y_), s_)
               for x_, y_, s_ in zipped]
    collection = PatchCollection(patches, **kwargs)
    if c is not None:
        c = np.broadcast_to(c, zipped.shape).ravel()
        collection.set_array(c)
        collection.set_clim(vmin, vmax)

    ax = plt.gca()
    ax.add_collection(collection)
    ax.autoscale_view()
    plt.draw_if_interactive()
    if c is not None:
        plt.sci(collection)
    return collection

#--------------------------------

fig = plt.figure(figsize=(7,7))
ax = fig.gca()
#ax.set_aspect("equal")
#plt.ion()

bx = [0,1,2,3]
by = [0,2,1,4]
#plt.plot(bx,by)
by2 = list(map(add,by,[1,1,1,1]))
#plt.plot(bx,by2)
#plt.show()

xoff = -300
yoff = 250
scale_factor = 5.0

plot_pieces_flag = False

def perp( a ):
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

def seg_intersect(a1,a2, b1,b2):
    # print("seg_intersect: a1,a2,b1,b2=", a1,a2,b1,b2)
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = np.dot( dap, db)
    num = np.dot( dap, dp )
    return (num / denom)*db + b1

    # if abs(denom) < 1.e-6:
    #     # print("denom=",denom,"  < 1.e-6")
    #     # sys.exit()
    #     return np.array([999,999])
    # else:
    #     return (num / denom)*db + b1

#-------------------
# cell_radius = 8.412710547954228  # PhysiCell default
cell_radius = 5 # 
cell_radius = 4 # 
cell_radius = 2.5 # ~5 micron spacing of subcells
# cell_radius = 1.5  # ~2 micron spacing
cell_diam = cell_radius*2
delta = cell_radius*1.5
delta = 0.0

#yc = -1.0
y_idx = -1
# hex packing constants
x_spacing = cell_radius*2
y_spacing = cell_radius*np.sqrt(3)

subcells_flag = True
create_csv_flag = True
debug_print = False

bbox_xmin = -100
bbox_xmax = 100
bbox_xmin = -300
bbox_xmax = 300

y_min = -200
y_min = 240
y_min = 200
y_min = 150
y_min = -190
y_min = -300
y_max = y_min + y_spacing

# In [3]: yend.min()  # -231.5
# In [4]: yend.max()  # 279.5
y_min = -231.5
y_max = 279.5

my_data_name = ''

# from https://github.com/PhysiCell-Models/Kidney_FTU/blob/main/PhysiCell/config/mymodel.xml 
    #   <cell_definition name="mesangial_matrix" ID="12">

# lsegs_file = "test_poly2.csv"
# lsegs_file = "test_poly1.csv"
# lsegs_file = "glom_cells_lsegs.csv"  # read this  (optionally write glom_cells.csv)
# filep = open(lsegs_file, 'r')


cell_data = np.genfromtxt(
   lsegs_file,
   dtype="float", delimiter=",")
xstart = cell_data[:,0]
ystart = cell_data[:,1]
xend = cell_data[:,2]
yend = cell_data[:,3]
if plot_pieces_flag:
    plt.plot(xstart,ystart,'r.')
num_lsegs = len(xstart)
print("# line segs = ",len(xstart))
xline = np.array( [0.0, 0.0] )
yline = np.array( [0.0, 0.0] )
for idx in range(num_lsegs):
    xline[0] = xstart[idx]
    xline[1] = xend[idx]
    yline[0] = ystart[idx]
    yline[1] = yend[idx]
    if plot_pieces_flag:
        plt.plot(xline,yline)

# idx=7
# print("lseg 7: ",xstart[idx],ystart[idx],xend[idx],yend[idx] )

hline0 = np.array( [bbox_xmin, 0.0] )  # artificially chosen x range for horiz line.
hline1 = np.array( [bbox_xmax, 0.0] )
lseg_p0 = np.array( [0.0, 0.0] )
lseg_p1 = np.array( [0.0, 0.0] )

cells_x = np.array([])
cells_y = np.array([])

y_idx = 0
for yval in np.arange(y_min,y_max, y_spacing):
    xvals = []
    y_idx += 1
    # print("--- yval = ",yval)
    hline0[1] = yval
    hline1[1] = yval
# xstart = cell_data[:,0]
# ystart = cell_data[:,1]
# xend = cell_data[:,2]
# yend = cell_data[:,3]
    for idx in range(len(xstart)):  # check all line segments
        # print(idx,") ",xpts_new[idx],ypts_new[idx], " -> ", xpts_new[idx+1],ypts_new[idx+1])
        lseg_p0[0] = xstart[idx]
        lseg_p0[1] = ystart[idx]
        lseg_p1[0] = xend[idx]
        lseg_p1[1] = yend[idx]

        ptint = seg_intersect( hline0,hline1, lseg_p0,lseg_p1)
        # if ptint[0] >= 999:
            # continue
        xmin = min(lseg_p0[0], lseg_p1[0])
        xmax = max(lseg_p0[0], lseg_p1[0])
        ymin = min(lseg_p0[1], lseg_p1[1])
        ymax = max(lseg_p0[1], lseg_p1[1])
        # print("------------ xmin,xmax = ",xmin,xmax)
        # if ptint[0] >= xmin and ptint[0] <= xmax:
        if ptint[0] >= xmin and ptint[0] <= xmax and ptint[1] >= ymin and ptint[1] <= ymax:
            # print("------------ ptint = ",ptint)
            # print("------------ xmin,xmax = ",xmin,xmax)
            xvals.append(ptint[0])
        # elif ptint[1] >= ymin and ptint[1] <= ymax:
        #     print("------------ ptint (2)= ",ptint)
        #     # print("------------ xmin,xmax = ",xmin,xmax)
        #     xvals.append(ptint[0])
            # print("--> ",ptint[0],ptint[1])
        # else:
            # print("-- no intersection.")

    # print("(presorted) xvals = ",end='')
    # for kdx in range(len(xvals)):
    #     print(xvals[kdx],',',end='')
    # print()

    xvals.sort()
    # print("(sorted) xvals = ",end='')
    # for kdx in range(len(xvals)):
        # print(xvals[kdx],',',end='')
    # print()

    if len(xvals) == 1:
        pass
    else:
        for xval in np.arange(bbox_xmin,bbox_xmax, x_spacing):   # create cells along horizontal line
            xval_offset = xval + (y_idx%2) * cell_radius
            # print("xvals = ",xvals)
            # for kdx in range(0,len(xvals),2):
            for kdx in range(0,len(xvals)-1,2):
                if (xval >= xvals[kdx]+delta) and (xval <= xvals[kdx+1]-delta):
                    cells_x = np.append(cells_x, xval_offset)
                    cells_y = np.append(cells_y, yval)

        # last_x = 
        # plt.text(nbx[0],nby[0], str(nbx[0])[0:max_digits] +","+str(nby[0])[0:max_digits])

    # plt.plot(cells_x,cells_y,'go')
    # circles(cells_x,cells_y, s=cell_radius, color=rgbs, alpha=0.6, ed='black', linewidth=0.5)
    # break

if subcells_flag:
    # circles(cells_x,cells_y, s=cell_radius, ec='black', linewidth=0.1)
    # if id_count < len(id_color):
        # mycolor = id_color[id_count]
    # else:
        # mycolor = 'b'
    # mycolor = id_color[id_count % len(id_color)]
    # print(" ----------->>>>>>>>>>>  mycolor = ",mycolor)
    circles(cells_x,cells_y, s=cell_radius, c='b', ec='black', linewidth=0.1)

# cell_id = 1
if create_csv_flag:
    # cells_out_file = "test_cells.csv"
    filep = open(cells_out_file, 'w')
    # matrix_cell_type = 12   # <cell_definition name="mesangial_matrix" ID="12">
    # matrix_cell_type = 8      # <cell_definition name="glomerular_mesangial" ID="8">
    cell_type = 0
    for ipt in range(len(cells_x)):
        filep.write(f"{cells_x[ipt]},{cells_y[ipt]}, 0.0, {cell_type}, {cell_id}\n")
    filep.close()
    print("\n-------> ",cells_out_file)

#--------------------------

# def getColumn(filename, column):
#     results = csv.reader(open(filename), delimiter=",")
#     return [result[column] for result in results]

# fname = "matrix_lsegs.csv"
# fname = "matrix_lsegs-line-for-arc.csv"
# fname = "matrix_plus2juxtaglom_lsegs.csv"
# print("fname= ",fname)

# cell_data = np.genfromtxt(
#    fname,
#    dtype="float", delimiter=",")

# xv = cell_data[:,0]
# yv = cell_data[:,1]
# print("----- num lsegs = ",len(xv))

# for idx in range(len(xv)):
#     if idx >= 0:
#         xpts = [cell_data[idx,0],cell_data[idx,2] ]
#         ypts = [cell_data[idx,1],cell_data[idx,3] ]
#         # print(idx, cell_data[idx,0],cell_data[idx,1])
#         plt.plot(xpts, ypts)

plt.show()
