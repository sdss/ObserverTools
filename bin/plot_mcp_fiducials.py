#!/usr/bin/env python3
"""
Plot and analyze new fiducial data before applying it to the mcp.

Originally converted nearly line-by-line by RHL from iop/etc/fiducials.tcl,
hence the generally unpythonic and cryptic syntax.
By John Parejko. 

History of changes
2020-04-02 -Fixed bug to read data file as numpy array, same as it was done for
 gz file. 
           -Reconfigured  how to read path for data file, default from current,
            and 
            optional from args,  no mjd format for directory name. Default dir
             option is ''. 
            
~/sdss4/fiducials/git/trunk/bin/plotMcpFiducials.py -rot -mjd 58799 -t0 1573542725 -t1 1573545137 -reset   -noplot
/Users/elenam/sdss4/fiducials/mcptpm/58799

Program: 
~/sdss4/fiducials/git/trunk/bin/plotMcpFiducials.py 
comm='~/sdss4/fiducials/git/trunk/bin/plotMcpFiducials.py'
eval $comm  <args>

Args: 
-mjd 58799 -az -t0 1573538393 -t1 1573542412  -table az.dat
-mjd 58799 -alt -t0 1573545352 -t1 1573546087  -table alt.dat
-mjd 58799 -rot -t0 1573542725 -t1 1573545137  -table rot.dat  -setCanon 80

-canon -reset -scale -verbose -noplot  -table stdout
            
-scale  az, alt, rot
warning
/Users/elenam/sdss4/fiducials/git/trunk/bin/plotMcpFiducials.py:448:
 RuntimeWarning: invalid value encountered in less
  tmp = fiducials[np.abs(fiducials_deg - 360 - fiducials_deg[i]) < 1]


plotMcpFiducials.py -mjd 58799 -dir data/58799 
-alt -t0 1573545352 -t1 1573546087 -fiducialFile=data/v1_141/alt.dat  
-table stdout -canon -reset -scale -noplot

  
"""
# from sdss.utilities import yanny
from pydl.pydlutils.yanny import yanny
import os
import pwd
import re
import sys
import gzip
import argparse
try:
    import matplotlib.pyplot as pyplot
    pyplot.ion()
    pyplot.rcParams.update({'font.size': 15,
                            'axes.labelsize': 13,
                            'legend.fontsize': 16,
                            'xtick.labelsize': 10,
                            'ytick.labelsize': 10,
                            'axes.linewidth': 2})
    from matplotlib import gridspec
except ImportError:
    pyplot = None

from pathlib import Path
from astropy.time import Time

import numpy as np
np.seterr(all='raise')
np.seterr(invalid='warn')


def getMJD():
    """Get the MJD for the current day as an int."""
    return int(Time.now().mjd)


axisAbbrevs = dict(azimuth="az", altitude="alt", rotator="rot")


def reset_fiducials(fididx, ud_delta, velocity, pos, verbose, axisName, resetFid):
    """
    Reset the position vector <pos> every time it crosses the first
    fiducial in the vector fididx
    """

    # # Find the indices where the velocity changes sign
    # NOTE: we do want to catch the first and last elements!
    sign = np.greater_equal(velocity, 0)
    sign_changes = (np.roll(sign, 1) - sign) != 0
    # add in the last element if we counted the first
    # (so we're counting both) front and back of the array)
    #if sign_changes[0]: sign_changes[-1] = True
    sign_changes[0] = True  # EM
    sign_changes[-1] = True  # EM
    sign_changes = np.arange(0, len(pos))[sign_changes]

    # Generate a vector with the `sweep number', incremented every time
    # the velocity changes sign
    sweep = []                    # which sweep the fiducial belongs to
    for i in range(len(sign_changes) - 1):
        sweep += (sign_changes[i+1] - sign_changes[i])*[i]
    # make sweep and fididx have same length
    sweep += (len(fididx) - len(sweep))*[i]
    sweep = np.array(sweep)

    # print "len(sweep)=", len(sweep),  "len(fididx)=", len(fididx)
    # print "%s    %s     %s   %s " % ("fididx",  "pos1",  "velocity", "sweep ")
    # for i in range(len(fididx)):
    #    print "%s  %4i  %10i  %8i  %s " % ( i, fididx[i], pos[i], velocity[i], sweep[i])

    # Choose the average fiducial as a standard (it should be in the middle of
    # the range), resetting the offset to zero whenever we see it
    nff, ff = 0, 0.0
    for i in range(len(sign_changes)):
        sign_changes = fididx[np.where(sweep == i)]
        sign_changes[np.where(sign_changes > ud_delta)] -= ud_delta

        ff += sum(sign_changes)
        nff += len(sign_changes)

    ff = int(ff/nff + 0.5)
    ffval = 0.0
    # ff=65    # from  RL code  and JP, but only 2 sweeps have this fid  for 58799, my testing data
    # ff=79   #  7 fid availble,  good for reset.
    # Find the indices where we see the ff fiducial,  tmp  <type 'numpy.ndarray'>
    if verbose:
        print("Default resetting fiducial %s,  requested %s" % (ff, resetFid))

    if resetFid is None:
        pass
    else:
        ff = resetFid

    tmp = np.arange(len(pos))[np.logical_or(
        fididx == ff, fididx == ff + ud_delta)]
    if verbose:
        print("Resetting at fiducial %d" % ff)
    if len(tmp) == 0:
        print("ERROR: reseting fiducial does not have values, exit",
              file=sys.stderr)
        sys.exit(1)

    # optimize reset fiducial for rotator - EM test code, not approved to use
    # if axisName=="rotator":
    #    maxind=len(tmp); ff2=ff
    #    for ind in range(1,10):
    #        ff1=ff+ind
    #        tmp = np.arange(len(pos))[np.logical_or(fididx == ff1,
    #  fididx == ff1 + ud_delta)]
    #        if len(tmp)> maxind: maxind=len(tmp); ff2=ff1
    #        ff1=ff-ind
    #        tmp = np.arange(len(pos))[np.logical_or(fididx == ff1,
    #  fididx == ff1 + ud_delta)]
    #        if len(tmp)> maxind: maxind=len(tmp); ff2=ff1
    #    ff=ff2
    #    tmp = np.arange(len(pos))[np.logical_or(fididx == ff,
    #  fididx == ff + ud_delta)]
    #    if verbose:
    #        print "Optimized resetting at fiducial %d" % ff
    #        print "Optimized indices of reset fiducials, ff=%d,
    #   %s " %  (ff,tmp), " (%s)" % len(tmp)

    # Generate a vector of corrections; the loop count is the index
    # of resetting fiducials in tmp array, one per sweep if exist
    corrections = {}   # <type 'dict'>
    for i in range(len(tmp)):
        corrections[sweep[tmp[i]]] = ffval - pos[tmp[i]]

# ---  JP corrections algorithm with EM adapted-----
#  For rot,   6 sweeps,  selected middle fid #60,  but only 2 sweeps
#  have this fiducial.  For each sweep we have been check if reset fid exist,
#  if yes, ok.
# if not, check on sweep below if exist, and next check for sweep up, if exist.
# if both exist, take average with prorated diff.
# if not low, take upper. If not upper, take low.
# the result looks not good.

    # Did any sweeps miss the `reset-canonical' fiducials?
    nsweep = sweep[-1] + 1
    # print "Cycle on sweeps:"

    for s in range(nsweep):
        # print "sweep=", s, " corrections.has_key(s):", corrections.has_key(s)
        if s in corrections:
            continue    # already got it

        # for s0 in range(s, -1, -1):   # JP
        for s0 in range(s-1, -2, -1):   # EM range(start, stop, step)
            # print "    testing low sweep (s0) =", s0, " has correction? ",
            #  corrections.has_key(s0)
            if s0 in corrections:
                break

        # for s1 in range(s, nsweep):  # JP
        for s1 in range(s+1, nsweep+1):  # EM
            # print "    testing upper sweep (s1) =", s1, " has correction? ",
            #  corrections.has_key(s1)
            if s1 in corrections:
                break

        #assert (s0 >= 0) or (s1 < nsweep)
        # JP corrections
        if s0 >= 0:
            if s1 < nsweep:              # we have two points
                #import ipdb
                # ipdb.set_trace()
                # print "    set between s0 and s1"
                corrections[s] = corrections[s0] + \
                    float(s - s0)/(s1 - s0)*(corrections[s1] - corrections[s0])
                # KeyError: 0
            else:
                # print "    set same as s0"
                corrections[s] = corrections[s0]
        else:
            # print "    set same as s1"
            corrections[s] = corrections[s1]

    # Build a corrections vector the same length as e.g. $pos
    corr = np.empty_like(pos) + 1.1e10
    for s, c in list(corrections.items()):
        corr[sweep == s] = c

    # Apply those corrections
    pos += np.int32(corr)

    return pos


def make_fiducials_vector(fididx, extend=True):
    """Make a vector from 0 to number of fiducials that we've seen."""
    if extend:
        return np.arange(0, max(fididx)+1)
    else:
        return np.array(sorted(set(fididx)), dtype=int)

# def read_fiducials(fiducial_file, axisName, readHeader=True):


def read_fiducials(fiducial_file, readHeader=True):
    """
    Read the positions of the fiducials for AXIS into VECS findex, p1 and p2

    FIDUCIAL_FILE may be a filename, or a format expecting a single string
    argument (az, alt, or rot), or an MCP version.
    """
    fiducial_file = Path(fiducial_file)
    if not fiducial_file.exists():
        raise RuntimeError(
            "I can find fiducial file  {}".format(fiducial_file))

    try:
        ffd = fiducial_file.open('r')
    except IOError as e:
        raise RuntimeError("I cannot read %s: %s" % (fiducial_file, e))

    # Read header
    header = {}
    while True:
        line = ffd.readline()

        if not line or re.search(r"^\# Fiducial", line):
            break

        if not readHeader:
            continue

        mat = re.search(r"^#\s*([^:]+):\s*(.*)", line)
        if mat:
            var, val = mat.group(1), mat.group(2)
            if var == "$Name":
                var = "Name"
                val = re.search(r"^([^ ]+)", val).group(1)

            if var == "Canonical fiducial":
                val = int(val)
            elif var == "Scales":
                val = [float(x) for x in val.split()]

            header[var] = val

    # Done with header; read data
    vecNames = [("findex", 0, int), ("pos1", 1, float), ("pos2", 5, float)]
    vecs = {}
    for v, col, t in vecNames:
        vecs[v] = []

    while True:
        fields = ffd.readline().split()

        if not fields:
            break

        for v, col, tt in vecNames:
            vecs[v].append(fields[col])

    ffd.close()

    # Convert to numpy arrays
    for v, col, tt in vecNames:
        vecs[v] = np.array(vecs[v], dtype=tt)

    return fiducial_file, vecs, header


def get_input_file(filename, mjd, mcp_log_dir, verbose=False):
    """Figure out where the file is, and return the full path.
    EM: 2020-08-09 reconfigured get_fiducial_file(), if no arg -dir, 
    look file in current directory,  if -dir <dirname>, read in <dirname>. """

    mcp_log_dir = Path(mcp_log_dir)

    if not filename:
        filename = Path("mcpFiducials-{:.0f}.dat".format(mjd))

    # searching input file in
    # -dir (1),  (.), default - /data/logs/mcp/ starting from 58722,
    # old data ?
    result = mcp_log_dir / filename
    if not result.exists():
        result = result.with_suffix(result.suffix + ".gz")
    if not result.exists():
        print("did not find data or gz file {},  exit".format(result),
              file=sys.stderr)
        sys.exit(1)

    return result.absolute()


def set_canonical_fiducials(axisName, vecs, setCanonical):
    """Set up the canonical fiducial values."""

    if setCanonical:
        temp = setCanonical.split(':')
        ff = int(temp[0])
        if len(temp) == 1:
            ffval = (vecs["true1"][vecs["fididx"] == ff][0])
        else:
            ffval = int(temp[1])
        ss = "(setCanonical:%s:%s)" % (ff, ffval)  # setCanonical
    else:
        if axisName == 'azimuth':
            ff = 19
        elif axisName == 'altitude':
            ff = 1
        elif axisName == 'rotator':
            ff = 80
        ffval = (vecs["true1"][vecs["fididx"] == ff][0])
        #ffval=(vecs["true1"][vecs["fididx"] == ff][0]).copy()
        ss = "(default)"

    return ff, ffval, ss


def plot_one(fig, ax, x, y, xlabel, ylabel, axisName, velocity, ffile,
             ms, t0, tbase):

    xmin = min(x)  # xmax = max(x)
    # ymin = min(y); ymax = max(y)

    if xlabel == "time":
        if t0 != 0:
            xmin = t0 - tbase
        # if args.t1 != 0:
        #     xmax = t1 - tbase

    # set limits to just beyond the data on all sides
    ax.margins(0.1)
    ax.yaxis.grid(True, which='major')

    l = velocity >= 0
    ax.plot(x[l], y[l], "rx", ms=3, mew=3, label='v>=0')   # ms - sym size;
    l = velocity < 0
    ax.plot(x[l], y[l], "g+", ms=3, mew=3, label='v<0')

    if xlabel == 'time' and ms:
        plot_ms(fig, ms['on'], ms['off'], axisName, tbase)

    if xlabel == "time" and tbase:
        # print "Initial time on plot:",tbase-xmin
        ax.set_xlabel("time - %s" % tbase)
    else:
        ax.set_xlabel(xlabel)

    fig.show()


def plot_data(axisName, vecs, index, plotFile, ffile,
              ms, reset, updown, error, t0, tbase):
    """Generate plots of (time,deg,index,etc.) vs. the fiducial positions."""

    def make_filename(axisName, xlabel, ylabel):
        if plotFile:
            filename = "%s-%s-%s" % (axisName, xlabel, ylabel)
            if reset:
                filename += "-R"
            if updown:
                filename += "-U"
            if updown:
                filename += "-E"
            filename += ".png"
        else:
            filename = ''
        return filename

    # Have to delete this from the local mapping, as it breaks matplotlib's
    # TK backend. It will still be set for the shell when we exit.
    if os.environ.get('TCL_LIBRARY', None) is not None:
        del os.environ['TCL_LIBRARY']

    title = axisName
    if reset:
        title += " -reset"
    if updown:
        title += " -updown"
    if error:
        title += " -error"
    title += "\n  Data: %s \n" % ffile

    labels = ['time', 'deg', 'index', 'fididx']
    for ylabel in ['pos1', 'pos2']:
        fig = pyplot.figure(figsize=(13, 8))
        gs = gridspec.GridSpec(2, 2, wspace=0.02)  # , height_ratios=[3, 1])
        ax = []
        #pyplot.rc('figure', titlesize=10)
        pyplot.suptitle(title)
        for i, xlabel in enumerate(labels):
            # right-side plots share the y axis.
            if i % 2 == 0:
                ax.append(pyplot.subplot(gs[i]))
                ax[i].set_ylabel(ylabel)
            else:
                ax.append(pyplot.subplot(gs[i], sharey=ax[i-1]))
                pyplot.setp(ax[i].get_yticklabels(), visible=False)
                ax[i].yaxis.tick_right()

            plotfile = make_filename(axisName, xlabel, ylabel)
            if xlabel == 'index':
                plot_one(fig, ax[i], index, vecs[ylabel], xlabel, ylabel,
                         axisName, vecs['velocity'], ffile, ms, t0, tbase)
            else:
                plot_one(fig, ax[i], vecs[xlabel], vecs[ylabel], xlabel,
                         ylabel, axisName, vecs['velocity'], ffile, ms, t0,
                         tbase)
            # use this for the label, incase we plotted with 'ms'
            if xlabel == 'time':
                ax[i].legend(loc='best', numpoints=1, fancybox=True,
                             ncol=2, bbox_to_anchor=(0.4, 1.15))
        if plotfile:
            # fig.tight_layout()
            fig.savefig(plotfile, bbox_inches="tight")


def plot_ms(fig, ms_on, ms_off, axisName, tbase):
    """Plot the ms on/off values as blue and cyan points, respectively."""
    axes = fig.get_axes()[0]
    ymin, ymax = axes.get_ylim()

    for ms, ctype, label in [(ms_on, 'blue', 'MS on'),
                             (ms_off, 'cyan', 'MS off')]:
        ms_time = np.array(
            [t for t, a in zip(ms["time"], ms_on["axis"])
             if a == axisName.upper()])
        ms_time = ms_time[ms_time > 0] - tbase
        y = np.zeros_like(ms_time) + ymin + 0.1*(ymax - ymin)

        axes.plot(ms_time, y, "+", ms=10, mew=3, color=ctype, label=label)


def do_scale(fiducials, fiducials_deg, axisName, pos, fpos, nfpos, fididx,
             verbose=False):
    """
    If the axis wraps, ensure that pairs of fiducials seen 360 degrees apart are
    always separated by the same amount -- i.e. estimate the axis' scale.
    """
    axis_scale = {}
    match = {}
    for n in ('pos1', 'pos2'):
        ndiff, diff = 0, 0.0
        for i in range(len(fiducials)):
            # skip missing ones
            if fiducials_deg[i] < -999 or not np.isfinite(fiducials_deg[i]):
                continue
            # tmp = fiducials[np.abs(
            # fiducials_deg - 360 - fiducials_deg[i]) < 1]  # warning
                # RuntimeWarning: invalid value encountered in less

            tmp = np.ndarray([0], dtype=int)
            for j in range(len(fiducials)):
                if fiducials_deg[j] < -999 or not np.isfinite(fiducials_deg[j]):
                    continue
                dd = abs(fiducials_deg[j] - 360 - fiducials_deg[i])
                if dd < 1:
                    fid = fiducials[j]
                    tmp = np.append(tmp, [fid])

            if len(tmp) == 0:
                continue            # we were only here once

            match[i] = tmp[0]
            # print "   --", fiducials[i], fiducials_deg[i],  match[i],
            #   fiducials_deg[match[i]] # , tmp

            tmp = pos[n][fididx == fiducials[i]]
            if len(tmp) == 0:
                continue            # we didn't cross this fiducial
            p1 = np.mean(tmp)

            tmp = pos[n][fididx == match[i]]
            # we didn't cross this fiducial
            if len(tmp) == 0:
                continue
            p2 = np.mean(tmp)

            diff += p2 - p1
            ndiff += 1

            # if verbose:
            #    print  fiducials[i], fiducials_deg[i], "--> ", match[i],
            #  fiducials_deg[match[i]]

        if ndiff == 0:
            if n == 1 and 'altitude' != axisName:
                print("You haven't moved a full 360degrees, so I cannot find"
                      " the scale", file=sys.stderr)

            for i in range(len(fiducials)):
                if nfpos[n][i] > 0:
                    v0 = fpos[n][i]
                    deg0 = fiducials_deg[i]
                    break

            for i in range(len(fiducials) - 1, -1, -1):
                if nfpos[n][i] > 0:
                    v1 = fpos[n][i]
                    deg1 = fiducials_deg[i]
                    break

            axis_scale[n] = 1.0/(v0 - v1)  # n.b. -ve; not a real scale
            if verbose:
                print("    %s scale APPROX %.6f  (encoder %s)" %
                      (axisName, 60.0*60.0*(deg0 - deg1)*axis_scale[n], n),
                      file=sys.stderr)
        else:
            diff /= ndiff
            axis_scale[n] = 60.0*60.0*360.0/diff
            if verbose:
                print("    %s scale = %.6f  (encoder %s)" %
                      (axisName, axis_scale[n], n[-1]))
            #
            # Force fiducials to have that scale
            #
            for i in range(len(fiducials)):
                if match.get(i):
                    mean = (fpos[n][i] + fpos[n][match[i]] - diff)/2.0  # error
                    fpos[n][i] = mean
                    fpos[n][match[i]] = mean + diff

    if verbose:
        print("    Encoder2/Encoder1 - 1 = %.6e" %
              (axis_scale['pos2']/axis_scale['pos1'] - 1))

    return axis_scale


def write_table_file(tableFile, fiducials, fpos, fposErr, nfpos,
                     axisName, dfile, axis_scale, ff, args):
    """Write the results to a fiducials table file for the MCP to use."""
    dfile = Path(dfile)
    ss = ""
    ss = ss+"-dir %s" % dfile.parent
    if args.mjd:
        ss = ss+" -mjd %i" % args.mjd
    ss = ss+" -%s" % axisName
    if args.t0:
        ss = ss+" -t0 %d" % args.t0
    if args.t1:
        ss = ss+" -t1 %d" % args.t1
    if args.setCanonical != None:
        ss = ss+" -setCanon %s" % args.setCanonical
    if args.canonical:
        ss = ss+" -canon"
    if args.resetFid != None:
        ss = ss+" -resetFid %s" % args.resetFid
    if args.reset:
        ss = ss+" -reset"
    if args.scale:
        ss = ss+" -scale"
    ss = ss+" -table %s" % args.tableFile

    if tableFile in ("stdout", "-",):
        fd = sys.stdout
    else:
        fd = open(tableFile, "w")

    # Get a CVS Name tag w/o writing it out literally.
    cvsname = "".join(["$", "Name", "$"])

    tt2 = Time.now().iso[:19] + 'Z'

    scale = {}
    for pos in ['pos1', 'pos2']:
        if axis_scale.get(pos) is None:
            scale[pos] = "None"
        else:
            scale[pos] = "%12.10f" % (axis_scale[pos])

    print("""#
# %s fiducials
#
# %s
#
# Creator:                 %s
# Time:                    %s
# Input file:              %s
# Scales:                  %s  %s
# Canonical fiducial:      %s
# Arguments:               %s
#
# Fiducial Encoder1 +-   error  npoint  Encoder2 +-   error  npoint
""" % (axisName, cvsname, pwd.getpwuid(os.geteuid())[0],
       tt2, dFileTail, scale['pos1'], scale['pos2'], ff, ss), end=' ', file=fd)

    for i in range(1, len(fpos['pos1'])):
        print("%-4d " % fiducials[i], end=' ', file=fd)

        for n in ('pos1', 'pos2'):
            print("   %10.0f +- %7.1f %3d" %
                  (fpos[n][i], fposErr[n][i], nfpos[n][i]), end=' ', file=fd)
        print("", file=fd)

    if fd != sys.stdout:
        fd.close()


def main(argv=None):
    """Read and analyze an mcpFiducials file,  e.g.
    plotMcpFiducials -mjd 51799 --alt -reset -canon -updown -table stdout
    """
    parser = argparse.ArgumentParser("plotMcpFiducials")
    parser.add_argument("fileName", type=str, nargs="?",
                        help="The mcpFiducials file to read")
    parser.add_argument("--azimuth", action="store_true",
                        default=False, help="Read azimuth data")
    parser.add_argument("--altitude", action="store_true",
                        default=False, help="Read altitude data")
    parser.add_argument("--rotator", action="store_true",
                        default=False, help="Read rotator data")

    parser.add_argument("--mjd", default=getMJD(), type=int,
                        help="Read mcpFiducials file for this MJD")
    parser.add_argument("-d", "--dir", default="/data/logs/mcp/",
                        dest="mcp_log_dir",
                        help="Directory to search for input file")

    parser.add_argument("--index0", default=0, type=int,
                        help="Ignore all data in the mcpFiducials file with"
                        " index < index0")
    parser.add_argument("--index1", default=0, type=int,
                        help="Ignore all data in the mcpFiducials file with"
                        " index > index0")

    parser.add_argument("--t0", type=int, default=0,
                        help="Ignore all data in the mcpFiducials file older"
                        " than this timestamp; If less than starting time,"
                        " interpret as starting time + |t0|. See also --index0")
    parser.add_argument("--t1", type=int, default=0,
                        help="""Ignore all data in the mcpFiducials file younger
                        than this timestamp; If less than starting time,
                        interpret as starting time + |t1|. See also
                        --index1""")

    parser.add_argument("--canonical", action="store_true", default=False,
                        help="Set the `canonical' fiducial to its canonical"
                        " value")
    parser.add_argument("--setCanonical", type=str, default=None,
                        help="Specify the canonical fiducial and optionally"
                        " position, e.g. --setCanonical 78 --setCanonical"
                        " 78:168185")
    parser.add_argument("--error", action="store_true", default=False,
                        help="Plot error between true and observed fiducial"
                        " positions")
    parser.add_argument("--errormax", type=float, default=0.0,
                        help="Ignore errors between true and observed fiducial"
                        " positions larger than <max>")
    parser.add_argument("--reset", action="store_true", default=False,
                        help="Reset fiducials every time we recross the first"
                        " one in the file?")
    parser.add_argument("-resetFid",  type=int,
                        help="reset fiducial index if default oe is not good")
    parser.add_argument("--scale", action="store_true", default=False,
                        help="Calculate the scale and ensure that it's the same"
                        " for all fiducial pairs?")
    parser.add_argument("--absolute", action="store_true", default=False,
                        help="Plot the values of the encoder, not the scatter"
                        " about the mean")
    parser.add_argument("--updown", action="store_true", default=False,
                        help="Analyze the `up' and `down' crossings separately")

    parser.add_argument("--ms", action="store_true", default=False,
                        help="Show MS actions on the time axis")
    parser.add_argument("--noplot", action="store_true",
                        help="Don't generate any plots.")
    parser.add_argument("--plotFile", action="store_true",
                        help="Write plot to a file (name automatically"
                        " determined).")
    parser.add_argument("--tableFile", type=str, default='',
                        help='Write fiducials table to this file (may be'
                        ' "stdout", or "-")')
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Be chatty?")

    parser.add_argument("--read_old_mcpFiducials", action="store_true",
                        default=False,
                        help="Read old mcpFiducial files (without encoder2"
                        " info)?")

    args = parser.parse_args(argv)

    if args.verbose:
        print("---------------------")
        print(f"Program: {Path(__file__).absolute()}")


# input verification
    #
    # Check that flags make sense
    #
    if args.error:
        if args.canonical:
            print("Please don't specify -canonical with -error", file=sys.stderr)
            sys.exit(1)
        if args.reset:
            print("Please don't specify -reset with -error", file=sys.stderr)
            sys.exit(1)
        if args.updown:
            print("Please don't specify -updown with -error", file=sys.stderr)
            sys.exit(1)
        if args.tableFile:
            print("Please don't specify e.g. -table with -error",
                  file=sys.stderr)
            sys.exit(1)


# -- em -- Scale + absolute
    if args.scale:
        if not args.absolute:
            if args.verbose:
                print("-scale only makes sense with -absolute; I'll set it for"
                      " you")
            args.absolute = True

#  --em -- Pyplot? ------
    if pyplot is None:
        print("I am unable to plot as I failed to import matplotlib",
              file=sys.stderr)

# --em -  AXIS -------
    # Which axis are we interested in?
    naxis = args.azimuth + args.altitude + args.rotator

    if not naxis:
        print("Please specify an axis", file=sys.stderr)
        sys.exit(1)
    elif naxis > 1:
        print("Please specify only one axis", file=sys.stderr)
        sys.exit(1)

    if args.altitude:
        axisName = "altitude"
        struct = "ALT_FIDUCIAL"
        names = ["time", "fididx", "pos1",
                 "pos2", "deg", "alt_pos", "velocity"]
    if args.azimuth:
        axisName = "azimuth"
        struct = "AZ_FIDUCIAL"
        names = ["time", "fididx", "pos1", "pos2", "deg", "velocity"]
    if args.rotator:
        axisName = "rotator"
        struct = "ROT_FIDUCIAL"
        names = ["time", "fididx", "pos1", "pos2", "deg", "latch", "velocity"]

# --- old_mcpFiducials ?
    if args.read_old_mcpFiducials:
        names.append("true")
    else:
        names.append("true1")
        names.append("true2")

    if args.verbose:
        print("Axis name=%s, struct=%s, names=%s" % (axisName, struct, names))

# --  get the name of data file
    dfile = get_input_file(args.fileName, args.mjd,
                           args.mcp_log_dir, verbose=args.verbose)
    if args.verbose:
        print("Input file =", dfile)

# --- em Read input file to VECS structure, using yanny function
    if".gz" in dfile.suffix:
        tmp_file = Path.home() / dfile.with_suffix("").name
        print(tmp_file)
        with gzip.open(dfile, "rb") as in_fil:
            with tmp_file.open("w") as out_fil:
                out_fil.write(in_fil.read().decode("utf-8"))
        pars = yanny(tmp_file.open('r'))
        tmp_file.unlink()
    else:
        pars = yanny(dfile)
    vecs = pars[struct]

    if args.verbose:
        print("Input vecs, len(vecs)=%s" % len(vecs))


# -----   ms on/off  ?
    ms = {}
    if args.ms:
        ms['on'] = pars["MS_ON"]
        ms['off'] = pars["MS_OFF"]

# em ------------------------------------------
    # Discard early data if so directed
    t0, t1 = args.t0, args.t1
    index0, index1 = args.index0, args.index1
    tmod = 10000
    tbase = tmod*int(vecs['time'][0]/tmod)

    def rescale_time(t0):
        if t0 != 0 and t0 < vecs['time'][0]:
            t0 = tbase + abs(t0)

    rescale_time(t0)
    rescale_time(t1)

    if t0 != 0 or t1 != 0 or index0 != 0 or index1 != 0:
        if t0 != 0 or t1 != 0:
            if index0 != 0 or index1 != 0:
                print(
                    "Ignoring index[01] in favour of time[01]", file=sys.stderr)

            if t0 == 0:
                t0 = vecs['time'][0]
            if t1 == 0:
                t1 = vecs['time'][-1]

            tmp = (vecs['time'] >= t0) & (vecs['time'] <= t1)
        else:
            index = list(range(0, len(vecs['time'])))
            if index0 < 0:
                index0 = 0
            if index1 == 0 or index1 >= len(vecs['time']):
                index1 = len(vecs['time']) - 1

            tmp = index >= index0 and index <= index1

        vecs = vecs[tmp]

    # re-create the index array into the newly-truncated data.
    index = np.arange(len(vecs['time']))

    # Are there any datavalues left?
    if len(vecs['time']) == 0:
        print("No points to plot after applying the time arguments, exit",
              file=sys.stderr)
        sys.exit(1)

    # Reduce time to some readable value
    vecs['time'] -= tbase

    # re-create the index array into the newly-truncated data.
    index = np.arange(len(vecs['time']))
    if args.verbose:
        print("Applied time frame:  len(vecs)={}".format(len(vecs)))

    # Discard the non-mark rotator fiducials
    if args.rotator:
        tmp = vecs['fididx'] > 0
        vecs = vecs[tmp]
        index = np.arange(len(vecs))
        # re-create the index array into the newly-truncated data.
        index = np.arange(len(vecs['time']))
        if args.verbose:
            print("Discard the non-mark rotator fiducials:  len(vecs)={}"
                  "".format(len(vecs)))

# ---------------------------
    # If we want to analyse the `up' and `down' fiducials separately,
    # add ud_delta to fididx for all crossings with -ve velocity
    if args.updown:
        ud_delta = max(vecs['fididx']) + 5
        vecs['fididx'][vecs['velocity'] < 0] += ud_delta
    else:
        ud_delta = 0

# ------ Processing
    # Process fiducial data
    # Start by finding the names of all fiducials crossed

#  E<: JP has "True", and we had fiducials starting from 0. Changed to False.
#  Code from proc:
    # fiducials = make_fiducials_vector(vecs['fididx'], False)
    #  #  EM: np.array(sorted(set(fididx)),dtype=int)
    # JP : np.arange(0, max(fididx)+1)
    fiducials = make_fiducials_vector(vecs['fididx'], True)

    # Find the approximate position of each fiducial (in degrees)
    fiducials_deg = np.empty_like(fiducials) + np.nan
    for i in range(len(fiducials)):
        tmp = vecs['deg'][vecs['fididx'] == fiducials[i]]
        if tmp != []:
            # fiducials_deg[i] = tmp[0]   # RL verbose output match with this definition
            fiducials_deg[i] = np.mean(tmp)

    if args.verbose:
        print("Find the approximate position of each fiducial (in degrees)")
        print("Fididx  Degrees    N   Pos1")
        for i in range(1, len(fiducials)):
            # if np.isfinite(fiducials_deg[i]):  # why John used this?
            tmp2 = vecs['pos1'][vecs['fididx'] == fiducials[i]]
            if len(tmp2) == 0:
                ss = np.nan
            else:
                ss = np.mean(tmp2)
            print(" %3d\t%8.3f  %2d  %10.0f " %
                  (fiducials[i], fiducials_deg[i], len(tmp2), ss))

# L409
    # Unless we just want to see the fiducial errors (-error), estimate
    # the mean of each fiducial value
    fpos = {}
    fpos['pos1'] = np.zeros_like(fiducials)
    fpos['pos2'] = np.zeros_like(fiducials)

    if args.error:
        # Read the fiducial file if provided
        if args.fiducialFile:
            tempvec = read_fiducials(args.fiducialFile, axisName, False)[1]
            for pos in ('pos1', 'pos2'):
                for i, fid in enumerate(fiducials):
                    tmp = tempvec[pos][tempvec['findex'] == fid]
                    fpos[pos][i] = tmp[0] if len(tmp) > 0 else 0
        else:
            # Find the true value for each fiducial we've crossed
            if args.read_old_mcpFiducials:
                true1 = True
            for i in range(len(fiducials)):
                fpos['pos1'][i] = np.mean(
                    true1[vecs['fididx'] == fiducials[i]])
            fpos['pos2'] = fpos['pos1']

    else:
        # --em ------ RESET------
        # Reset the encoders every time that they pass some `fiducial' fiducial?
        if args.reset:
            reset_fiducials(vecs['fididx'], ud_delta, vecs['velocity'],
                            vecs['pos1'], args.verbose, axisName, args.resetFid)
            reset_fiducials(vecs['fididx'], ud_delta, vecs['velocity'],
                            vecs['pos2'], False, axisName, args.resetFid)
            # don't double-print

# -- em ------
        # Calculate mean values of pos[12]
        if args.updown:
            pos0 = {}
            for pos in ('pos1', 'pos2'):
                pos0[pos] = vecs[pos]       # save pos[pos]

                for i, fid in enumerate(fiducials):
                    fpos[pos][i] = np.mean(
                        vecs[pos][vecs['fididx'] == fid])

                down = np.where(vecs['fididx'] < ud_delta)
                tmp2 = vecs['fididx']
                tmp2[down] += ud_delta
                tmp[np.logical_not(down)] -= ud_delta

                tmp = fpos[pos][vecs['fididx']] + fpos[pos][tmp2]
                tmp = tmp/((fpos[pos][vecs['fididx']] != 0) +
                           (fpos[pos][tmp2] != 0))

                vecs[pos] -= fpos[pos][vecs['fididx']] - tmp
            # Undo that +$ud_delta
            vecs['fididx'][vecs['fididx'] > ud_delta] -= ud_delta

            fiducials = make_fiducials_vector(vecs['fididx'])

            for pos in ('pos1', 'pos2'):
                fpos[pos] = np.zeros_like(fiducials)
        # --------

        # (Re)calculate fpos[12] --- `Re' if args.updown was true

        def recalc_pos_err_nfpos(vecs, fiducials):
            fposErr = {}
            nfpos = {}
            fpos = {}
            for pos in ('pos1', 'pos2'):
                nfpos[pos] = np.empty_like(fiducials)
                fposErr[pos] = np.empty_like(fiducials, dtype=float)
                fpos[pos] = np.zeros_like(fiducials, dtype=float)

            for i in range(len(fiducials)):
                for pos in ('pos1', 'pos2'):
                    tmp = vecs[pos][vecs['fididx'] == fiducials[i]]
                    if len(tmp) == 0:
                        fpos[pos][i] = 0
                        nfpos[pos][i] = 0
                        fposErr[pos][i] = -9999  # disable fiducial
                    else:
                        fpos[pos][i] = np.mean(tmp)
                        nfpos[pos][i] = len(tmp)
                        # changed statistics np.std(tmp) -->
                        #   np.std(tmp)/np.sqrt(nfpos[pos][i]-1)
                        fposErr[pos][i] = 1e10 if len(tmp) == 1 else np.std(
                            tmp)/np.sqrt(nfpos[pos][i]-1)
            return fpos, nfpos, fposErr

        fpos, nfpos, fposErr = recalc_pos_err_nfpos(vecs, fiducials)

        #fposErr = {}; nfpos = {}
        # for pos in ('pos1','pos2'):
        #    nfpos[pos] = np.empty_like(fiducials)
        #    fposErr[pos] = np.empty_like(fiducials)

        # for i in range(len(fiducials)):
        #    for pos in ('pos1','pos2'):
        #        tmp =  vecs[pos][vecs['fididx'] == fiducials[i]]
        #        print i, pos, "tmp=", tmp
        #        if len(tmp) == 0:
        #            fposErr[pos][i] = -9999 # disable fiducial
        #            nfpos[pos][i] = 0
        #        else:
        #            fpos[pos][i] = np.mean(tmp)
        #            nfpos[pos][i] = len(tmp)
        #            fposErr[pos][i] = 1e10 if len(tmp) == 1 else np.std(tmp)

        # restore values
        if args.updown:
            for pos in ('pos1', 'pos2'):
                vecs['pos'][pos] = pos0[pos]

# ------ absolute ----------
    # absolute vecs is using for scale, and relative is using for errors
    # default args.absolute is False,
    # if args.scale,  set args.absolute=True
    if not args.absolute:
        if args.verbose:
            print(
                "args.absolute={}, change vecs[pos] to relative values".format(
                    args.absolute))
        for pos in ('pos1', 'pos2'):
            vecs[pos] = vecs[pos] - fpos[pos][vecs['fididx']]
            # next is working for not extended fiducials vector-em
            # for i,ind in enumerate(vecs['fididx']):
            #    i0=np.where(fiducials == ind)
            #    vecs[pos][i] = vecs[pos][i] - fpos[pos][i0[0][0]]
    # else:
    #    if args.verbose:
    #        print  "args.absolute=%s, keep vecs[pos] absolue values" % args.absolute

# -------- SCALE--------
    axis_scale = {}
    if args.scale:
        if args.verbose:
            print("Calculating scale: ")
        axis_scale = do_scale(fiducials, fiducials_deg, axisName,
                              vecs, fpos, nfpos, vecs['fididx'],
                              verbose=args.verbose)

# ------- canonical ---------------------
    # Fix fiducial positions to match canonical value for some fiducial?
    ff = None
    if args.canonical:
        ff, ffval, ss = set_canonical_fiducials(
            axisName, vecs, args.setCanonical)
        if args.verbose:
            print("Applying canonical fiducial value:  %s:%s  %s  " %
                  (ff, ffval, ss))
        for pos in ('pos1', 'pos2'):
            tmp = fpos[pos][fiducials == ff]
            # tmp = tmp[tmp != 0]     # valid crossings aren't == 0?   - reset
            #  fid has zero encod value
            if len(tmp) == 0:
                print("   ------??? Error: You have not crossed/read canonical"
                      " fiducial %d" %
                      (ff), file=sys.stderr)
                sys.exit(1)
            # fpos[pos][nfpos[pos] > 0] += np.int64(ffval - np.mean(tmp))  # JP
            fpos[pos][nfpos[pos] > 0] += (ffval - tmp[0])  # em

# -------   round up --- em --
    for pos in ('pos1', 'pos2'):
        fpos[pos] = np.rint(fpos[pos])
        fposErr[pos] = np.around(fposErr[pos], decimals=1)

# -------- write table file --------
    # Print table?
    if args.tableFile:
        if args.verbose:
            print("Output to %s" % args.tableFile)
        write_table_file(args.tableFile, fiducials, fpos, fposErr, nfpos,
                         axisName, dfile, axis_scale, ff, args)  # it was argv

# -------- args.error -------
    if args.error:
        # we have a measurement of this fiducial
        haveValue = np.where(fpos['pos1'][vecs['fididx']] != 0)
        if args.errormax > 0:
            haveValue = haveValue & abs(vecs['pos1']) < args.errormax
        vecs = vecs[haveValue]

# -------- plot/noplot ------
    if not args.noplot:
        # plot_data(axisName, vecs, index, args.plotFile, ffile, ms, args.reset,
        #  args.updown, args.error, t0, tbase)
        plot_data(axisName, vecs, index, args.plotFile, dfile, ms,
                  args.reset, args.updown, args.error, t0, tbase)
        input("Press enter to exit... ")

    return fiducials, fpos, fposErr, nfpos


if __name__ == "__main__":
    main()
