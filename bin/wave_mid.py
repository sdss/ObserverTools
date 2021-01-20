#!/usr/bin/env python3
"""
WAVEMID
A tool to test spectrograph collimation using SOS/DOS.
EM 09/04/2010

usage:
WAVEMID 4908.6 7984.0 4999.9 8058.3 pro[plot]

The above line doesn't need to be typed and is designed to be copied straight
from SOS/DOS

"""
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import sys

__version__ = '3.0.0'

if not sys.argv[1:2]:
    print("    Usage:  WAVEMID  2036.0 2045.0 2043.0 2044.0  [ct]")
    print("    ct - optional cart number, 0 - sos nominal")
    print("    plot - to plot ")
    sys.exit("Error: program requires at least 4 arguments, exit")
nPar = len(sys.argv)
# print " "

# read sosWmids arguments
sosWmid = np.array(sys.argv[1:]).astype(float)

# read sosCart & plot options
sosCart = 0
plotQ = False
if nPar >= 6:
    if sys.argv[5] == "plot":
        plotQ = True
    else:
        sosCart = int(sys.argv[5])
if nPar >= 7:
    if sys.argv[6] == "plot":
        plotQ = True
    else:
        sosCart = int(sys.argv[6])
# print "sosCart=", sosCart
# print "plotQ=",plotQ

# check if Kaike's table exist on disk
fPath = Path('.')
# fName="bin/wavemid.dat"
# fullName=fPath+"/"+fName
fullName = Path(__file__).absolute().parent.parent / 'dat/wavemid.dat'
if not fullName.exists():
    sys.exit("{} was not found, exit".format(fullName.absolute()))

# read Kaike's table file  to string array
file = fullName.open('r')
line = "a"
lineArr = []
while line != "":
    line = file.readline()
    line = line.strip()
    if line != "":
        lineArr.append(line)
file.close()

# convert Kaike's table to np.array
# print "--- Kaike's table for arc's sets (dat/wavemid.dat):"
# print "cart   b1      r1      b2      r2"
n = len(lineArr)
tblCart = np.zeros([n])
tblWmid = np.zeros([n, 4])
for i in range(0, n):
    aa = lineArr[i].split()
    tblCart[i] = int(aa[0])
    for j in range(0, 4):
        tblWmid[i, j] = float(aa[j + 1])
    ss = "%2i   %6.1f  %6.1f  %6.1f  %6.1f" % (
        tblCart[i], tblWmid[i, 0], tblWmid[i, 1], tblWmid[i, 2], tblWmid[i, 3])
#    if i == 0: print ss, "(sos nominal)"
#    else: print ss

# search sos cart number in Kaike's table
iii = np.nonzero(tblCart == sosCart)[0]
# print iii,  len(iii)
if len(iii) == 0:
    sys.exit("Error: no requested cart number in the table, exit")
elif len(iii) > 1:
    sys.exit("Error: more then one cart number found in the table, exit")
else:
    tblInd = iii[0]  # index of table for requested cart number
# print "sosInd=", tblInd
# print "tblCart=", tblCart[tblInd]

# select line for requested cart and calulate the difference 
tblWmidC = tblWmid[tblInd, 0:len(sosWmid)]  # requested cart parameters from
# table
difWmid = sosWmid - tblWmidC  # difference between sos and table for requested
# cart

# print "   Requested nominal set for cart=%2i" % (tblCart[tblInd])
print(" " * 13, "  b1     r1     b2     r2")
print("current     :" + (" {:6.1f}" * len(sosWmid)).format(*sosWmid))

# print "   Requested nominal set for cart=%2i" % (tblCart[tblInd])
# print "tblCart=", tblCart[tblInd]

# print "nominal  : %6.1f %6.1f %6.1f %6.1f" % (tblWmidC[0],tblWmidC[1],
# tblWmidC[2],tblWmidC[3])

print("nominal  {:2.0f} :".format(tblCart[tblInd])
      + (" {:6.1f}" * len(sosWmid)).format(*tblWmidC))
# print "difference : %6.1f %6.1f %6.1f %6.1f" % (difWmid[0], difWmid[1],
# difWmid[2],difWmid[3])
print("WAVEMID spec:" + ("{:6.1f}" * len(difWmid)).format(*difWmid))
print("-------------- ")

# a=-b; c=0
# boss moveColl spec=sp1 a=31 b=-31 c=0 # Move b1 WAVEMID by +1 A, r1
# WAVEMID by 1.36 A.
step = 31.0
sp1 = round((difWmid[0] + difWmid[1] / 1.36) / 2.0 * step)
print("boss moveColl spec=sp1 a=%i b=%i c=0" % (-sp1, sp1))
try:
    sp2 = round((difWmid[2] + difWmid[3] / 1.36) / 2.0 * step)
    print("boss moveColl spec=sp2 a=%i b=%i c=0" % (-sp2, sp2))
except IndexError:
    pass
print("-------------")
print("Tolerance: b,r +/-10(yellow);  b +/-15(red);  r +/-20(red)")
# print " "

# check if to plot
if not plotQ:
    sys.exit()

print("Plotting, close window with plot to exit")

tblWmidN = np.zeros([n, 4])
# tbl minus tbl sos nominal
tblWmidN[:, 0:4] = tblWmid[:, 0:4] - tblWmid[0, 0:4]

sosWmidN = np.zeros([4])
sosWmidN[:] = sosWmid[:] - tblWmid[0, :]  # sos minus tbl sos nominal

plt.figure(num=None, figsize=(9, 4), )
# plt.ioff()
xmin = -22
xmax = 22
ymin = -22
ymax = 22
xtol = 10
ytol = 10
xtol1 = 15
ytol1 = 20

plt.subplot(121)
# sp1=plt.plot(tblWmidN[1:,0],tblWmidN[1:,1],"bo")
plt.axis([xmin, xmax, ymin, ymax])
plt.grid(True)
plt.xlabel('b1 - b1(ct=0), pix')
plt.ylabel('r1 - r1(ct=0), pix')
plt.title('sp1 wavemid', size=15)
plt.plot([-xtol, xtol, xtol, -xtol, -xtol],
         [ytol, ytol, -ytol, -ytol, ytol], color='b', linewidth=0.6)
plt.plot([-xtol1, xtol1, xtol1, -xtol1, -xtol1],
         [ytol1, ytol1, -ytol1, -ytol1, ytol1], color='r',
         linewidth=0.6)
curCart = plt.plot(sosWmidN[0], sosWmidN[1], 'rs')
plt.annotate("current", [sosWmidN[0] + 0.5, sosWmidN[1] - 0.1], color="r",
             size=13)
# line3 = plt.plot([xmin,xmax],[ymin,ymax],color='black', linewidth=0.6)
line3 = plt.plot([xmin, xmax], [xmin * 1.36, xmax * 1.36], color='black',
                 linewidth=0.4)
# plt.setp(line3, color='black', linewidth=1.0)
# for i in range(1,n):
#     plt.annotate("%2i"% (tblCart[i]), [tblWmidN[i,0]+0.4,tblWmidN[i,1]-0.1],
#     color="b", size=12)

plt.subplot(122)
# sp2=plt.plot(tblWmidN[1:,2],tblWmidN[1:,3],"bo")
plt.axis([xmin, xmax, ymin, ymax])
plt.grid(True)
plt.xlabel('b2 - b2(ct=0), pix')
plt.ylabel('r2 - r2(ct=0), pix')
plt.title('sp2 wavemid', size=15)
plt.plot([-xtol, xtol, xtol, -xtol, -xtol],
         [ytol, ytol, -ytol, -ytol, ytol], color='b', linewidth=0.6)
plt.plot([-xtol1, xtol1, xtol1, -xtol1, -xtol1],
         [ytol1, ytol1, -ytol1, -ytol1, ytol1], color='r',
         linewidth=0.6)
plt.plot(sosWmidN[2], sosWmidN[3], 'rs')
plt.annotate("current", [sosWmidN[2] + 0.5, sosWmidN[3] - 0.1], color="r",
             size=13)
# line3 = plt.plot([xmin,xmax],[ymin,ymax],color='black', linewidth=0.6)
plt.plot([xmin, xmax], [xmin * 1.36, xmax * 1.36], color='black',
         linewidth=0.4)
# for i in range(1,n):
#     plt.annotate("%2i"% (tblCart[i]), [tblWmidN[i,2]+0.4,tblWmidN[i,3]-0.1],
#     color="b", size=12)

# plt.ion()

# plt.draw()
plt.show()
print("")
