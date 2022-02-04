#!/usr/bin/env python3

# this is the m4l code that queries the system for
# for monitor data that goes into the observers log
#
# This is a version that gets its TPM data from the new TPM
# via a broadcast message

# this code also queries TCC and also reads MIG nominal files
# the MIG nominals are set by sending this script a cmd: write
#
# on host2 this file ran as a script when somebody connected to 2001
#

#from cPickle import dump, load
#from pickle import dump, load
import json
from os import path, stat, listdir
from select import POLLIN, POLLOUT
from stat import ST_MTIME
from subprocess import Popen, PIPE, STDOUT
from sys import argv, exit, stdin, stdout
from time import time
from traceback import format_exc
from telnetlib import Telnet
from pathlib import Path
import logging
import tpmdata


tpmdata.tinit()

#from apo import ResourceLock, tcc

#LOGFILE = '/home/arc/migs/m4l.log'
LOGFILE = Path() / ".m4l.log"
NOMINAL_MIG_DIR = '/home/tpm/migs'

VERBOSE = False


def jfmt(num):
    return "{:7.4f}".format(num)


global_cache = {}


def cached_listdir(path):
    res = global_cache.get(path)
    if res is None:
        res = listdir(path)
        global_cache[path] = res
    return res

# The TCC public keys were added to the tcc@tcc25m:[.ssh]authorization_keys.


def strprec(str, n):
    i = str.find(b".")
    if 0 < i and 0 <= n:
        str = str[0:i + n + 1]
    return str


def sjd():
    ''' Calculates the SDSS Julian Date, which is the MJD + 0.3 days
        See http://maia.usno.navy.mil/
    '''

#    NOTE: The next line must be changed everytime TAI-UTC changes

    # TAI_UTC = 34    # TAI-UTC = 34 seconds as of 1/1/09
    TAI_UTC = 0    # sdsshost2 is on TAI time

    return int((time() + TAI_UTC) / 86400.0 + 40587.3)


class m4l:
    '''Routines to get mirror positions for LUI'''

    def __init__(self):
        try:
            nominalMigs = self.getNominalMigValues(NOMINAL_MIG_DIR)
        except:
            nominalMigs = {}


#    Query TPM

        if VERBOSE:
            print('Querying TPM')
        logging.debug('Querying TPM')
        tpm = self.TPM()

#    Get MIG command

        # cmd = stdin.readline(8).strip()
        # if VERBOSE : print ('Executing Command "' + cmd + '"')
        # logging.debug ('Executing Command "' + cmd + '"')
        # if cmd == 'write' :
        #     nominalMigs["m1_axial_a"] = tpm["m1_axial_a"]
        #     nominalMigs["m1_axial_b"] = tpm["m1_axial_b"]
        #     nominalMigs["m1_axial_c"] = tpm["m1_axial_c"]
        #     nominalMigs["m1_transverse"] = tpm["m1_transverse"]
        #     nominalMigs["m1_lateral_e"] = tpm["m1_lateral_e"]
        #     nominalMigs["m1_lateral_f"] = tpm["m1_lateral_f"]
        #     nominalMigs["m2_axial_a"] = tpm["m2_axial_a"]
        #     nominalMigs["m2_axial_b"] = tpm["m2_axial_b"]
        #     nominalMigs["m2_axial_c"] = tpm["m2_axial_c"]
        #     nominalMigs["m2_y"] = tpm["m2_y"]

        #     # self.saveNominalMigValues (NOMINAL_MIG_DIR, nominalMigs)
        #     exit()

#    Query TCC

        if VERBOSE:
            print('Querying TCC')
        logging.debug('Querying TCC')

        tcc = self.TCC()

        if VERBOSE:
            print('TCC replied:'), tcc

#    Print the formatted results

        self.m4lprint(nominalMigs, tpm, tcc)
        return None

    def m4lprint(self, nominalMigs, tpm, tcc):

        # Print data in proper format for log

        reply = '\nPRIMARY:\n'
        reply += '--------\n'
        if not tcc["Connected"]:
            print("TCC connection failed")
        reply += 'Scale: {}\n'.format(tcc['ScaleFac'].decode('ASCII'))

        reply += '\nMIGS\t\tTONIGHT\tNOMINAL\n'
        reply += 'Axial A:\t' + \
            jfmt(tpm['m1_axial_a']) + '\t' + \
            jfmt(nominalMigs['m1_axial_a']) + '\n'

        reply += 'Axial B:\t' + \
            jfmt(tpm['m1_axial_b']) + '\t' + \
            jfmt(nominalMigs['m1_axial_b']) + '\n'
        reply += 'Axial C:\t' + \
            jfmt(tpm['m1_axial_c']) + '\t' + \
            jfmt(nominalMigs['m1_axial_c']) + '\n'
        reply += 'Trans D:\t' + \
            jfmt(tpm['m1_transverse']) + '\t' + \
            jfmt(nominalMigs['m1_transverse']) + '\n'
        reply += 'Lateral E:\t' + \
            jfmt(tpm['m1_lateral_e']) + '\t' + \
            jfmt(nominalMigs['m1_lateral_e']) + '\n'
        reply += 'Lateral F:\t' + \
            jfmt(tpm['m1_lateral_f']) + '\t' + \
            jfmt(nominalMigs['m1_lateral_f']) + '\n'

        reply += '\nGALILS\n'
        reply += 'Commanded:  ' + str(tpm['galil_m1_c_0']) + ' ' + str(tpm['galil_m1_c_1']) + ' ' + str(
            tpm['galil_m1_c_2']) + ' ' + str(tpm['galil_m1_c_3']) + ' ' + str(tpm['galil_m1_c_4']) + ' ' + str(tpm['galil_m1_c_5']) + '\n'
        reply += 'Actual:     ' + str(tpm['galil_m1_a_0']) + ' ' + str(tpm['galil_m1_a_1']) + ' ' + str(
            tpm['galil_m1_a_2']) + ' ' + str(tpm['galil_m1_a_3']) + ' ' + str(tpm['galil_m1_a_4']) + ' ' + str(tpm['galil_m1_a_5']) + '\n'

        reply += '\nSETMIR VALUES\n'
        reply += 'PrimDesOrient: ' + tcc['PrimDesOrient'] + '\n'
        reply += 'PrimOrient:    ' + tcc['PrimOrient'] + '\n'

        reply += '\nSECONDARY:\n'
        reply += '----------\n'

        reply += '\nFocus:      ' + tcc['SecFocus'].decode('ASCII') + '\n'
        reply += 'Air temp:   ' + "{:6.2f}".format(tpm['DpTempA']) + '\n'
        reply += 'Altitude:   {:.1f}\n'.format(
            tpm['alt_pos']*tpm['alt_spt']/3600.0)

        reply += '\nMIGS\t\tTONIGHT\tNOMINAL\n'
        reply += 'Axial A:\t' + \
            jfmt(tpm['m2_axial_a']) + '\t' + \
            jfmt(nominalMigs['m2_axial_a']) + '\n'
        reply += 'Axial B:\t' + \
            jfmt(tpm['m2_axial_b']) + '\t' + \
            jfmt(nominalMigs['m2_axial_b']) + '\n'
        reply += 'Axial C:\t' + \
            jfmt(tpm['m2_axial_c']) + '\t' + \
            jfmt(nominalMigs['m2_axial_c']) + '\n'
        reply += 'Trans D:\t' + \
            jfmt(tpm['m2_y']) + '\t' + jfmt(nominalMigs['m2_y']) + '\n'

        reply += '\nGALILS\n'
        reply += 'Commanded: ' + str(tpm['galil_m2_c_0']) + ' ' + str(tpm['galil_m2_c_1']) + ' ' + str(
            tpm['galil_m2_c_2']) + ' ' + str(tpm['galil_m2_c_3']) + ' ' + str(tpm['galil_m2_c_4']) + '\n'
        reply += 'Actual:    ' + str(tpm['galil_m2_a_0']) + ' ' + str(tpm['galil_m2_a_1']) + ' ' + str(
            tpm['galil_m2_a_2']) + ' ' + str(tpm['galil_m2_a_3']) + ' ' + str(tpm['galil_m2_a_4']) + '\n'

        reply += '\nSETMIR VALUES\n'
        reply += 'SecDesOrient: ' + tcc['SecDesOrient'] + '\n'
        reply += 'SecOrient:    ' + tcc['SecOrient'] + '\n'

        print(reply)

    def getNominalMigValues(self, dir):

        #    Make sure that the requested directory in dir exists

        try:
            stat(dir)[ST_MTIME]
        except:
            fake_nominals = {
                "m1_axial_a": 0,
                "m1_axial_b": 0,
                "m1_axial_c": 0,
                "m1_transverse": 0,
                "m1_lateral_e": 0,
                "m1_lateral_f": 0,
                "m2_axial_a": 0,
                "m2_axial_b": 0,
                "m2_axial_c": 0,
                "m2_y": 0

            }
            return fake_nominals

#    Obtain the files in the directory and add the full path to them

        max_time = -1
        filename = ''

        for file in cached_listdir(dir):
            file = path.join(dir, file)
#        logging.debug ('%s %s' % (file, file.find ('nominalMigs-')))

#    See if the file name matches the pattern

            if (file.find('nominalMigs-') > 0):

                #    Store the name and mtime of only the latest file

                mtime = stat(file)[ST_MTIME]
#                logging.debug ('%d %s %d' % (max_time, file, mtime))
                if max_time < mtime:
                    filename = file
                    max_time = mtime

        if filename:
            if VERBOSE:
                print("filename " + filename)
            logging.debug('nominalMigs file: %s' % filename)
            f = open(filename, 'r')
            nominalMigs = json.load(f)
            f.close()
            for key in nominalMigs.keys():
                if VERBOSE:
                    print('Nominal MIG values ' + str(key) +
                          ' ' + str(nominalMigs[key]))
        else:
            logging.error('Error, nominalMigs file: %s, not found' % filename)
            nominalMigs = {}
            raise Exception

        logging.info('Returned nominalMigs file: %s' % filename)
        return nominalMigs

    def saveNominalMigValues(self, dir, nominalMigs):
        try:
            f = open('%s/nominalMigs-%s.json' % (dir, sjd()), 'w')
            json.dump(nominalMigs, f)
            f.close()
            logging.info('Created %s/nominalMigs-%s.json' % (dir, sjd()))
        except:
            logging.error('Failed to create %s/nominalMigs-%s.json' %
                          (dir, sjd()))

    def TPM(self):
        if VERBOSE:
            print('tpmdata start')
        try:
            tpmd = tpmdata.packet(1, 1)
            if VERBOSE:
                print('got tpm ' + tpmd['tpm_vers'])
        except:
            logging.error('tpmdata failed:\n%s' % (format_exc()))
            if VERBOSE:
                print('tpmdata failed ')

        return tpmd

    def TCC(self):
        '''    The command format specification is in:
            http://www.apo.nmsu.edu/Telescopes/TCC/Commands.html
        '''
        tccd = {}

        if VERBOSE:
            print('TCC: connecting')
        try:
            #            t = tcc.TCC ('10.25.1.16', 2500, LOGFILE)
            # t = Telnet ('10.25.1.16', 2500 )
            t = Telnet('10.25.1.141', 2500)  # sdss5-tcc server
            tccd["Connected"] = True
        except:
            try:
                t = Telnet('10.25.1.16', 2500)  # sdss4-tcc server
                tccd["Connected"] = True
            except:
                if VERBOSE:
                    print('failed to connect to tcc')
                logging.error('Failed to connect to connect to tcc')
                # Old versions would return "48", but this value is never converted
                # to an int/float, so it will be more clear to output it as an
                # obviously non-real value
                tccd['ScaleFac'] = b'None'
                tccd['PrimDesOrient'] = str('0')
                tccd['PrimOrient'] = str('0')
                tccd['SecFocus'] = b'None'
                tccd['SecDesOrient'] = str('0')
                tccd['SecOrient'] = str('0')
                tccd["Connected"] = False
                return tccd

        try:
            if VERBOSE:
                print('TCC: writing "MIRROR STATUS"')
            t.write(b"MIRROR STATUS\n")
            reply = t.read_until(b" :", timeout=2)
        except:
            if VERBOSE:
                print('Failed to write "MIRROR STATUS to tcc"')
            logging.error('Failed to write "MIRROR STATUS" to tcc')
            return

        if VERBOSE:
            print('TCC replied:' + str(reply.rstrip()))
        logging.debug(reply.rstrip())

        '''
        0 0 I PrimEncMount=9900.0,-50.0,6300.0,-1600.0,12000.0,12000.0
        0 0 I PrimOrient=0.0,0.0,0.0,0.0,0.0,0.0
        0 0 I PrimActMount=9900.0,-50.0,6300.0,-1600.0,12000.0,12000.0
        0 0 I PrimCmdMount=9900.0,-50.0,6300.0,-1600.0,12000.0,12000.0
        0 0 I PrimStatus=4,4,4,4,4,4
        0 0 W Text="number keys does not match number of values"
        0 0 I PrimMaxIter=1
        0 0 I PrimDesOrient=0.0,0.0,0.0,0.0,0.0,0.0
        0 0 I PrimDesOrientAge=2498.94
        0 0 I PrimDesEncMount=9900.0,-50.0,6300.0,-1600.0,12000.0,12000.0
        0 0 I PrimState=Done,0,1,0.0,0.0
        0 0 I SecEncMount=1613942.0,1568292.0,1570572.0,-1700.0,-8150.0
        0 0 I SecOrient=1257.43,4.36,-15.08,25.25,111.21,-19.59
        0 0 I SecActMount=1613760.63,1572590.25,1566460.0,-1700.03,-8150.02
        0 0 I SecCmdMount=1613350.08,1567765.54,1570050.84,-1707.84,-8135.67
        0 0 I SecStatus=4,4,4,4,4
        0 0 I SecMaxIter=3
        0 0 I SecDesOrient=1257.0,4.35,-15.05,25.0,111.05,-19.46
        0 0 I SecDesOrientAge=2498.95
        0 0 I SecDesEncMount=1613343.13,1567793.76,1570056.68,-1704.92,-8131.45
        0 0 I SecState=Done,0,3,0.0,0.0
        0 3 :
        '''

        found_flags = 0
        for line in reply.split(b"\n"):
            if 0 < line.find(b"PrimOrient="):
                tmp = line.replace(b"=", b" ").replace(b",", b" ").split()
                if VERBOSE:
                    print('TCC: PrimOrient =' + str(tmp))
                tccd['PrimOrient'] = '%s %s %s %s %s' % (tmp[4].decode('ASCII'), tmp[5].decode(
                    'ASCII'), tmp[6].decode('ASCII'), tmp[7].decode('ASCII'), tmp[8].decode('ASCII'))
                found_flags |= 1

            if 0 < line.find(b"PrimDesOrient="):
                tmp = line.replace(b"=", b" ").replace(
                    b",", b" ").replace(b";", b"").split()
                if VERBOSE:
                    print('TCC: PrimDesOrient = ' + str(tmp))
                tccd['PrimDesOrient'] = '%s %s %s %s %s' % (tmp[4].decode('ASCII'), tmp[5].decode(
                    'ASCII'), tmp[6].decode('ASCII'), tmp[7].decode('ASCII'), tmp[8].decode('ASCII'))
                found_flags |= 2

            if 0 < line.find(b"SecOrient="):
                tmp = line.replace(b"=", b" ").replace(b",", b" ").split()
                if VERBOSE:
                    print('TCC: ' + str(line))
                if VERBOSE:
                    print('TCC: SecOrient = ' + str(tmp))
                tccd['SecOrient'] = '%s %s %s %s %s' % (tmp[4].decode('ASCII'), tmp[5].decode(
                    'ASCII'), tmp[6].decode('ASCII'), tmp[7].decode('ASCII'), tmp[8].decode('ASCII'))
                found_flags |= 4

            if 0 < line.find(b"SecDesOrient="):
                tmp = line.replace(b"=", b" ").replace(
                    b",", b" ").replace(b";", b"").split()
                if VERBOSE:
                    print('TCC: SecDesOrient = ' + str(tmp))
                tccd['SecDesOrient'] = '%s %s %s %s %s' % (tmp[4].decode('ASCII'), tmp[5].decode(
                    'ASCII'), tmp[6].decode('ASCII'), tmp[7].decode('ASCII'), tmp[8].decode('ASCII'))
                found_flags |= 8

        if 15 != found_flags:
            logging.error(
                'Failed to find all "MIRROR STATUS" data in reply from tcc: %X' % found_flags)

        try:
            t.write(b"SHOW FOCUS\n")
            reply = t.read_until(b" :", timeout=2)
            if VERBOSE:
                print('TCC: writing "SHOW FOCUS"')
        except:
            logging.error('Failed to write "SHOW FOCUS" to tcc')

        if VERBOSE:
            print('TCC replied:'), reply.rstrip()
        logging.debug(reply.rstrip())

        found_flags = 0
        for line in reply.split(b"\n"):
            if 0 < line.find(b"SecFocus"):
                tmp = line.replace(b"=", b" ").split()
                tccd['SecFocus'] = tmp[4]
                found_flags = 1

        if 1 != found_flags:
            logging.error('Failed to find "SHOW FOCUS" data in reply from tcc')

        try:
            t.write(b"SHOW SCALE\n")
            reply = t.read_until(b" :", timeout=2)
            if VERBOSE:
                print('TCC: writing "SHOW SCALE"')
        except:
            logging.error('Failed to write "SHOW SCALE" to tcc')

        if VERBOSE:
            print('TCC replied:', reply.rstrip())
        logging.debug(reply.rstrip())

        found_flags = 0
        for line in reply.split(b"\n"):
            if 0 < line.find(b"ScaleFac"):
                tmp = line.replace(b"=", b" ").split()
                tccd['ScaleFac'] = tmp[4][:-1]
                found_flags = 1

        if 1 != found_flags:
            logging.error('Failed to find "SHOW SCALE" data in reply from tcc')

        t.close()

        logging.debug(str(tccd))
        return tccd


if __name__ == '__main__':

    # setup the logging module

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        filename=LOGFILE, filemode='a')

    if 1 < len(argv) and '-v' == argv[1]:
        VERBOSE = True

    m4l()
    if VERBOSE:
        print('done:')
