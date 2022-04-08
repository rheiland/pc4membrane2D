import sys
import numpy as np
from matplotlib.patches import Circle, Ellipse, Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from scipy.stats import norm

print("len(sys.argv) = ",len(sys.argv))

print(" R_out R_in cell_radius theta0(degs) theta1 num_chunks num_layers")
print("e.g., 250 200 2.5 225 315 3 7\n")
idx=1
R_out = float(sys.argv[idx])
idx+=1
R_in = float(sys.argv[idx])
idx+=1
cell_radius = float(sys.argv[idx])
idx+=1
theta0 = float(sys.argv[idx])
theta0 = theta0 * 2*np.pi / 360.
print("theta0 (radians) = ",theta0)
idx+=1
theta1 = float(sys.argv[idx])
theta1 = theta1 * 2*np.pi / 360.
print("theta1 (radians) = ",theta1)
idx+=1
num_chunks = int(sys.argv[idx])
idx+=1
num_layers = int(sys.argv[idx])

plt.figure(figsize=(7, 7))

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
    #-------------------------------------------

mean = 0
std_dev = 20

# x_values = np.arange(-50, 50, 0.2)
xmin = -50
xmax = -xmin
x_values = np.arange(xmin, xmax, 1)
# y_values = norm(mean, std_dev)
# plt.plot(x_values, y_values.pdf(x_values))
# yv = y_values.pdf(x_values) * yscale
# print(yv.min(),yv.max())
# plt.plot(x_values, yv)

print(x_values)
# print(yv)

# y_values = norm(mean, 2)
# plt.plot(x_values, y_values.pdf(x_values))
# y_values = norm(mean, 4)
# plt.plot(x_values, y_values.pdf(x_values))
# yv = y_values.pdf(x_values)
# print(yv.min(),yv.max())

# plt.plot(x_values, yv*50,'--')

#ax.set_title('Normal Gaussian Curve')

# cell_radius = 1.  # ~2 micron spacing
# cell_radius = 2.5 # ~5 micron spacing of subcells; Area=19.63
cell_diam = cell_radius*2

x_min = -50.0
x_max = -x_min
y_min = 0.0
y_max = 150

#yc = -1.0
y_idx = -1
# hex packing constants
x_spacing = cell_radius*2
y_spacing = cell_radius*np.sqrt(3)

membrane_x = np.array([])
membrane_y = np.array([])

cells_x = np.array([])
cells_y = np.array([])

xctr = 0.0
yctr = R_out

circum = 2*np.pi * R_out 
ncells_circle = circum / cell_diam
print("ncells_circle = ",ncells_circle)


#------------------------
#--- plot the membrane (at R_out)
#theta_del = (theta1 - theta0) / 50
theta_del1 = 2*np.pi / (ncells_circle - ncells_circle/10.0)
print("theta_del1 (membrane)= ",theta_del1)
for tval in np.arange(theta0,theta1, theta_del1):
    xv = xctr + R_out * np.cos(tval)
    yv = yctr + R_out * np.sin(tval)
    membrane_x = np.append(membrane_x, xv)
    membrane_y = np.append(membrane_y, yv)
circles(membrane_x,membrane_y, s=cell_radius, c='k', ec='black', linewidth=0.1)

cell_type = 0

#------------------------
ncells = 0
outfile = "mysubcells.csv"
filep = open(outfile, 'w')
for nlayer in range(0,num_layers):
    print("------- layer ",nlayer)
    circum = 2*np.pi * R_out 
    ncells_circle = circum / cell_diam
    theta_del = 2*np.pi / ncells_circle
    print("theta_del (cells)= ",theta_del)
    rval = R_out - cell_diam
    print("theta0, theta1 = ",theta0,theta1)
    theta_chunk_del = (theta1 - theta0) / num_chunks
    for tval in np.arange(theta0,theta1, theta_del):
        xv = xctr + rval * np.cos(tval)
        yv = yctr + rval * np.sin(tval)
        cells_x = np.append(cells_x, xv)
        cells_y = np.append(cells_y, yv)
        ncells += 1
        chunk_id = int((tval - theta0) / theta_chunk_del)
        cell_id = 100 + chunk_id
        # print(xval_offset,',',yval,',0.0, 2, 101')  # x,y,z, cell type, [sub]cell ID
        # filep.write(f"{cells_x[ipt]},{cells_y[ipt]}, 0.0, {cell_type}, {cell_id}\n")
        filep.write(f"{xv},{yv}, 0.0, {cell_type}, {cell_id}\n")
    R_out -= (cell_diam - cell_diam/5.0)
    if nlayer % 2 == 0:
        theta0 += theta_del/2
    else:
        theta0 -= theta_del/2

print("ncells = ",ncells)
#------------------------
# print("\n------ 2nd layer")
# R_out -= (cell_diam - cell_diam/5.0)
# print("R_out = ",R_out)
# circum = 2*np.pi * R_out 
# ncells_circle = circum / cell_diam
# print("ncells_circle = ",ncells_circle)
# theta_del = 2*np.pi / ncells_circle
# print("theta_del (cells)= ",theta_del)
# rval = R_out - cell_diam
# for tval in np.arange(theta0+theta_del/2,theta1, theta_del):
#     xv = xctr + rval * np.cos(tval)
#     yv = yctr + rval * np.sin(tval)
#     cells_x = np.append(cells_x, xv)
#     cells_y = np.append(cells_y, yv)
#     # print(xval_offset,',',yval,',0.0, 2, 101')  # x,y,z, cell type, [sub]cell ID

# #------------------------
# print("\n------ 3rd layer")
# R_out -= (cell_diam - cell_diam/5.0)
# print("R_out = ",R_out)
# circum = 2*np.pi * R_out 
# ncells_circle = circum / cell_diam
# print("ncells_circle = ",ncells_circle)
# theta_del = 2*np.pi / ncells_circle
# print("theta_del (cells)= ",theta_del)
# rval = R_out - cell_diam
# for tval in np.arange(theta0+theta_del/2,theta1, theta_del):
#     xv = xctr + rval * np.cos(tval)
#     yv = yctr + rval * np.sin(tval)
#     cells_x = np.append(cells_x, xv)
#     cells_y = np.append(cells_y, yv)

filep.close()
print("---> ",outfile)
print(" REMINDER: the cell volume in .xml will need to reflect the cell_radius here.")
print(" volume = ", 4./3. * np.pi * cell_radius**3)
circles(cells_x,cells_y, s=cell_radius, c='r', ec='black', linewidth=0.1)
plt.xlim(-260,260)
plt.ylim(-260,260)
plt.show()
