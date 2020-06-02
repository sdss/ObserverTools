#!/usr/bin/env python

'''
See this CA library  https://github.com/RobbieClarken/channelarchiver
'''

from channelarchiver import Archiver, codes, utils
import optparse
import datetime
from keydict import configKey

parser = optparse.OptionParser() 
utc = utils.UTC()

prefix="test"

ss='http://sdss-telemetry.apo.nmsu.edu/telemetry/cgi/ArchiveDataServer.cgi'
archiver = Archiver(ss)

def getMultiData(channel, startTime, endTime):
    ''' getting multiple values - in progress, testing mode'''
    
    channels = ["25m:guider:probe:exposureID","25m:guider:probe:probeID","25m:guider:probe:flags"]
    archiver.scan_archives()
    data0,data1,data2 = archiver.get(channels,startTime, endTime)
    print("----------------------------------------------")
    print("    Data     Time(UT)     Value")
    print("----------------------------------------------")    
    for i in range(len(data0.values)):
        print(data0.values[i],data1.values[i],data2.values[i])
    print("----------------------------------------------")
    return [data0,data1,data2]


def getBit(val, ind):
    mask = 1 << ind
    if  val & mask !=0:
        return 1
    else:
        return 0

def convert_to_bits(nbit,d):
    ss=""
    nbit=32
    for i in range(nbit):
	    ss=str(getBit(d,i))+ss
    return ss


def getData(channel, startTime, endTime):
    ''' getting one pv '''

    archiver.scan_archives()
    data= archiver.get(channel,startTime, endTime)
    return data


def printData(pvname, startTime, endTime):
    archiver.scan_archives()
    data= archiver.get(pvname,startTime, endTime)

    split_pv=pvname.split(':')
    ck=configKey(split_pv[1], split_pv[2], prefix="25m", opt="jb1")
    ind=ck.names.index(pvname)    
    ifBits=(ck.getType(ind)=="Bits") and (opts.nbit != None)
    if (opts.nbit != None) and (ck.getType(ind) !="Bits"):
        print("Warning: ignoring bits option as pvtype is not Bits")
    wd=60
    print("-"*wd)
    print("%s, N=%s" % (pvname,len(data.values)))
    header="    Data     Time(UT)     Value"
    if ifBits: # opts.nbit != None:
        header=header+ "    Bit= %s (%s)" % (opts.nbit, ck.getBitName(ind,opts.nbit))
    print(header)  
    print("-"*wd)
    
    for d,t in zip(data.values, data.times):
        gentime=t.strftime('%Y-%m-%d  %H:%M:%SZ')
        ss="%s" % gentime
        ss="%s   %s" % (ss, d)  # print date-time and value
        if ifBits:  # (opts.nbit != None) and (ck.getType(ind)=="Bits"):
            d1=int(d,0)  # convert from hex-string to integer              
            nbits=ck.getBitWidth(ind)  # get the number of bits in the pvname(channel)
            d2=convert_to_bits(nbits,d1)  # present hex int as bits
            sd2='-'.join(d2[i:i+4] for i in range(0,len(d2),4)) # split bits by 4 digits
            
            nbit=opts.nbit+1 # nbit start from 0 in descr, but convert from 1
            if (nbit >nbits):
                bit="?"
            else:
                bit=d2[nbits-nbit]
            
            ss="%s   %s" % (ss, bit)  # print selected bit
            ss="%s   %s" % (ss, sd2)  # add bits to string for printing

        print(ss)
    print("-"*wd)
    print("cafetch.py -p %s --t1 '%s' --t2 '%s'" % (pvname, startTime, endTime))

    if opts.desc:
        print("----------------------------------------------")
        print(ck.getDescribe())  
    print("-"*wd)
    print("")
    return data

if __name__ == "__main__":
    def_t2=datetime.datetime.now(tz=utc)
    def_t1=def_t2-datetime.timedelta(0,300)
    format = "%Y-%m-%d %H:%M:%S"        
    def_t1 = def_t1.strftime(format)
    def_t2 = def_t2.strftime(format)
    
    pvname="25m:mcp:cwPositions"
    
    parser.add_option('-p', '--pvname', dest='pvname',default=pvname,\
        help='pvname,  default 25m:mcp:cwPositions')
    parser.add_option('--t1', '--startTime', dest='statTime',default=def_t1,\
        help='start time of query, default is 5 min ago, format "2015-06-23 22:10"')
    parser.add_option('--t2', '--endTime', dest='endTime',default=def_t2,\
        help='end time of query, default is current time now, format "2015-06-23 22:15"')
    #parser.add_option('-b', '--bit', dest='bit',default=False,action='store_true',\
    #    help='if True, add convertion to bits, default False')
    parser.add_option('-b',  dest='nbit',default=None, help='bit number ', type='int')
    parser.add_option('--desc',  dest='desc',default=False, action='store_true', help='print description?')
        
    (opts, args) = parser.parse_args()

    data=printData(opts.pvname, opts.statTime, opts.endTime) 
