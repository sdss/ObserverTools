#!/usr/bin/env python3
"""
XMID
A tool to test spectrograph collimation using SOS/DOS, a twin to WAVEMID.
EM 09/04/2010

usage:
XMID 4908.6 7984.0 4999.9 8058.3 pro[plot]

The above line doesn't need to be typed and is designed to be copied straight
from SOS/DOS

"""
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import sys


__version__ = '3.0.0'


if not sys.argv[1:4]:
    print("    Usage:  XMID  2036.0 2045.0 2043.0 2044.0  [ct]")
    print("    ct - optional cart number, 0 - sos nominal")
    sys.exit("Error: program requires at least 4 arguments, exit")
nPar = len(sys.argv)
# print " "

# read sosXmids arguments  
# for i in range(1,len(sys.argv)):
sosXmid = np.zeros(4, dtype=float)
for i in range(4):
    sosXmid[i] = float(sys.argv[i + 1])

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

# check if Kaike's table exist on disk
fPath = Path('.')
# fName="bin/xmid.dat"
# fullName=fPath+"/"+fName
fullName = Path(__file__).parent.parent / "dat/xmid.dat"
# print "fullName=", fullName
if not fullName.exists():
    sys.exit(fullName + " was not found, exit")

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
# print "--- Kaike's table for flat's sets (dat/xmid.dat)"
# print "cart   b1      r1      b2      r2"
n = len(lineArr)
tblCart = np.zeros([n])
tblXmid = np.zeros([n, 4])
for i in range(0, n):
    aa = lineArr[i].split()
    tblCart[i] = int(aa[0])
    for j in range(0, 4):
        tblXmid[i, j] = float(aa[j + 1])
    ss = "%2i   %6.1f  %6.1f  %6.1f  %6.1f" % (
        tblCart[i], tblXmid[i, 0], tblXmid[i, 1], tblXmid[i, 2], tblXmid[i, 3])
#    if i == 0: print ss, "(sos nominal)"
#   else: print ss

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

# select line for rewuested cart and calulate the difference 
tblXmidC = tblXmid[tblInd, 0:4]  # requested cart parameters from table
difXmidC = sosXmid - tblXmidC  # difference between sos and table for requested
# cart

# print "   Requested nominal set for cart=%2i" % (tblCart[tblInd])
print(" " * 13, "  b1     r1     b2     r2")
print("current     : {:6.1f} {:6.1f} {:6.1f} {:6.1f}".format(
      sosXmid[0], sosXmid[1], sosXmid[2], sosXmid[3]))
print("nominal [{:2.0f}]: {:6.1f} {:6.1f} {:6.1f} {:6.1f}".format(
      tblCart[tblInd], tblXmidC[0], tblXmidC[1], tblXmidC[2], tblXmidC[3]))
print("XMID spec   : {:6.1f} {:6.1f} {:6.1f} {:6.1f}".format(
    difXmidC[0], difXmidC[1], difXmidC[2], difXmidC[3]))
# print "difference: %6.1f %6.1f %6.1f %6.1f" % (difXmidC[0], difXmidC[1],
# difXmidC[2],difXmidC[3])
print("-" * 40)

# -a=-b=c
# boss moveColl spec=sp1 a=-63 b=-63 c=63  # +1
step = 63.0
sp1 = round((difXmidC[0] + difXmidC[1]) / 2.0 * step)
sp2 = round((difXmidC[2] + difXmidC[3]) / 2.0 * step)
print("boss moveColl spec=sp1 a=%i b=%i c=%i" % (sp1, sp1, -sp1))
print("boss moveColl spec=sp2 a=%i b=%i c=%i" % (sp2, sp2, -sp2))
print("-" * 40)
print("The tolerance is +/- 8 pixels (yellow), +/- 12 pixel (red)")
# print ""

#  figure

# check if to plot
if not plotQ:
    sys.exit(" ")

print("Plotting, close window with plot to exit")

tblXmidN = np.zeros([n, 4])
tblXmidN[:, 0:4] = tblXmid[:, 0:4] - tblXmid[0,
                                     0:4]  # tbl minus tbl sos nominal

sosXmidN = np.zeros([4])
sosXmidN[:] = sosXmid[:] - tblXmid[0, :]  # sos minus tbl sos nominal

plt.figure(num=None, figsize=(9.5, 4.5), )
# plt.ioff()
xmin = -15
xmax = 15
ymin = -15
ymax = 15
xtol = 8
ytol = 8
xtol1 = 12
ytol1 = 12

plt.subplot(121)
# sp1=plt.plot(tblXmidN[1:,0],tblXmidN[1:,1],"bo")
plt.axis([xmin, xmax, ymin, ymax])
plt.grid(True)
plt.xlabel('b1 - b1(nominal), pix')
plt.ylabel('r1 - r1(nominal), pix')
plt.title('sp1 xmid', size=15)
tolerance = plt.plot([-xtol, xtol, xtol, -xtol, -xtol],
                     [ytol, ytol, -ytol, -ytol, ytol], color='b', linewidth=0.6)
tolerance1 = plt.plot([-xtol1, xtol1, xtol1, -xtol1, -xtol1],
                      [ytol1, ytol1, -ytol1, -ytol1, ytol1], color='r',
                      linewidth=0.6)
curCart = plt.plot(sosXmidN[0], sosXmidN[1], 'rs')
plt.annotate("current", [sosXmidN[0] + 0.5, sosXmidN[1] - 0.1], color="r",
             size=13)
line3 = plt.plot([xmin, xmax], [ymin, ymax], color='black', linewidth=0.6)
# plt.setp(line3, color='black', linewidth=1.0)
# for i in range(1,n):
#     plt.annotate("%2i"% (tblCart[i]), [tblXmidN[i,0]+0.4,tblXmidN[i,1]-0.1],
#     color="b", size=12)

plt.subplot(122)
# sp2=plt.plot(tblXmidN[0:,2],tblXmidN[0:,3],"bo")
plt.axis([xmin, xmax, ymin, ymax])
plt.grid(True)
plt.xlabel('b2 - b2(nominal), pix')
plt.ylabel('r2 - r2(nominal), pix')
plt.title('sp2 xmid', size=15)
tolerance = plt.plot([-xtol, xtol, xtol, -xtol, -xtol],
                     [ytol, ytol, -ytol, -ytol, ytol], color='b', linewidth=0.6)
tolerance1 = plt.plot([-xtol1, xtol1, xtol1, -xtol1, -xtol1],
                      [ytol1, ytol1, -ytol1, -ytol1, ytol1], color='r',
                      linewidth=0.6)
curCart = plt.plot(sosXmidN[2], sosXmidN[3], 'rs')
plt.annotate("current", [sosXmidN[2] + 0.5, sosXmidN[3] - 0.1], color="r",
             size=13)
line3 = plt.plot([xmin, xmax], [ymin, ymax], color='black', linewidth=0.6)
# for i in range(1,n):
#     plt.annotate("%2i"% (tblCart[i]), [tblXmidN[i,2]+0.4,tblXmidN[i,3]-0.1],
#     color="b", size=12)

# plt.ion()

# plt.draw()
plt.show()
print("")
