
# python chunks.py <theta0 theta1 num_chunks r_out r_in xctr yctr>
#  e.g.
# python chunks.py  3.77 5.65 5 100 80 0 0   # small circle; large curvature
# python chunks.py  3.77 5.65 5 300 280 0 200   # small circle; large curvature
#
import sys
import numpy as np

# math.pi * 1.2 = 3.77
# math.pi * 1.8 = 5.65
# python chunks.py  3.77 5.65 5 100 80
print("# args=",len(sys.argv)-1)
# fname = "rwh1b.svg"
theta0 = float(sys.argv[1])
theta1 = float(sys.argv[2])
num_chunks = int(sys.argv[3])
r_out = float(sys.argv[4])
r_in = float(sys.argv[5])
xctr = float(sys.argv[6])
yctr = float(sys.argv[7])

#theta_del = float(sys.argv[3])
print("theta0 = ",theta0)
print("theta1 = ",theta1)
print("num_chunks = ",num_chunks)
print("r_out = ",r_out)
print("r_in = ",r_in)
tdel = (theta1 - theta0) / num_chunks
print("tdel = ",tdel)
print("xctr = ",xctr)
print("yctr = ",yctr)


tval = theta0
for idx in range(num_chunks):
    fname = "chunk"+str(idx+1)+".csv"
    print(fname)
    filep = open(fname, 'w')
    x1 = xctr + r_out * np.cos(tval)
    y1 = yctr + r_out * np.sin(tval)
    x2 = xctr + r_out * np.cos(tval+tdel)
    y2 = yctr + r_out * np.sin(tval+tdel)
    x3 = xctr + r_in * np.cos(tval+tdel)
    y3 = yctr + r_in * np.sin(tval+tdel)
    x4 = xctr + r_in * np.cos(tval)
    y4 = yctr + r_in * np.sin(tval)
    filep.write(f"{x1},{y1}, {x2},{y2}\n")
    filep.write(f"{x2},{y2}, {x3},{y3}\n")
    filep.write(f"{x3},{y3}, {x4},{y4}\n")
    filep.write(f"{x4},{y4}, {x1},{y1}\n")
    filep.close()
    tval += tdel

print("-- Now run raster_chunks.sh")