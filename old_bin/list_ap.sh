#!/usr/bin/env python3
#  EM 12/12/2012

#  usage:  list_ap_Call 
#  python wrap for commands:  
#      setup apogeeql trunk 
#       list_ap1.py
#  the script provides output only, no any actions makes   

import sys
import os

ss="  ".join("%s"%(v) for v in sys.argv[1:])

#list_ap_cmd="setup apogeeql trunk; list_ap1.py %s 2>/dev/null " % (ss)

list_ap_cmd="list_ap %s 2>/dev/null " % (ss)
list_ap=os.popen(list_ap_cmd).read() 

print  list_ap


