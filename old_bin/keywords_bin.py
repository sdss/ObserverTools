#!/usr/bin/env python
""" This program is for easy navigation on actorkeys library, which describe
keywords. Usage:
keywords.py [-a actor] [-k keyword] [-h help] [-r search_pattern] [-s short_print]


Examples:

keywords.py -a tcc  # see all keywords for tcc actor with full description

keywords.py -a tcc -k spiderInstAng
    # see the full description  of one tcc keywords spiderInstAng

keywords.py -k spiderInstAng  # see full description of one keyword spiderInstAng

keywords.py -r ab   # see full description of keywords which name has ab pattern

keywords.py -r ab -s   # see short description of requested listing
It might be useful to use grep with short description.

06/30/2015 by EM, and some help from Gordon.

"""

from actorkeys import keyDictionaries
from opscore.protocols.keys import KeysDictionary
import optparse

parser = optparse.OptionParser()
total = 0


# ----- this class from telemetry keydict.py
class configKey:
    def __init__(self, actor, keyword, prefix, opt="jb1"):
        self.actor = actor
        self.keyword = keyword
        self.prefix = prefix
        self.kdict = KeysDictionary.load(self.actor)
        self.key = self.kdict[self.keyword]
        self.n_values = len(self.key.typedValues.vtypes)
        self.opt = opt
        self.names = self.getNames()
        self.minVals = self.key.typedValues.minVals
        self.maxVals = self.key.typedValues.maxVals

    def getType(self, i):
        vtype = self.key.typedValues.vtypes[i]
        return type(vtype).__name__

    def getEnumNumber(self, i, ss):
        vtype = self.key.typedValues.vtypes[i]
        for item, k in list(vtype.enumValues.items()):
            if item.lower() == ss.lower():
                return k

    def getName(self, i):
        return self.names[i]

    def getType(self, i):
        try:
            return type(self.key.typedValues.vtypes[i]).__name__
        except:
            return None

    def getRepMin(self, i):
        return self.key.typedValues.vtypes[i].minRepeat

    def getRepMax(self, i):
        return self.key.typedValues.vtypes[i].maxRepeat

    def getRepType(self, i):
        vtype = self.key.typedValues.vtypes[i]
        return type(vtype.vtype).__name__

    def getNames(self):
        if self.opt == "jb":
            from telemetryConfig import Telemetry
            tel = Telemetry()
            pv_list = tel.keywordValuePVNames(self.actor, self.keyword)
            if len(pv_list) == 0:
                # print "name error-pv_list==None", self.actor, self.keyword
                pv_list = []
                name = "%s:%s:%s" % (self.prefix, self.actor, self.key.name)
                pv_list.append(name)
                return pv_list
            return pv_list
        elif self.opt == "jb1":  # I reproduce JB algorithm
            pv_list = []
            if self.n_values <= 1:
                name = "%s:%s:%s" % (self.prefix, self.actor, self.key.name)
                pv_list.append(name)
                return pv_list
            else:
                unnamed_index = 1
                for index, vtype in enumerate(self.key.typedValues.vtypes):
                    tp = type(vtype).__name__
                    if tp == "RepeatedValueType":  # repeated count
                        sub_name = "%s" % (vtype.vtype.name)
                    else:
                        sub_name = "%s" % (vtype.name)
                    if sub_name == "None":
                        sub_name = "unnamed_%1i" % (unnamed_index)
                        unnamed_index += 1
                    name = "%s:%s:%s:%s" % (
                    self.prefix, self.actor, self.key.name, sub_name)
                    pv_list.append(name)
                return pv_list

        elif self.opt == "em":
            pv_list = []
            if self.n_values <= 1:
                name = "%s:%s:%s" % (self.prefix, self.actor, self.key.name)
                pv_list.append(name)
                return pv_list
            else:
                for index, vtype in enumerate(self.key.typedValues.vtypes):
                    tp = type(vtype).__name__
                    if tp == "RepeatedValueType":  # repeated count
                        sub_name = "%s" % (vtype.vtype.name)
                    else:
                        sub_name = "%s" % (vtype.name)
                    if sub_name == "None":
                        sub_name = "unnamed_%1i" % (index)
                    name = "%s:%s:%s:%s" % (
                    self.prefix, self.actor, self.key.name, sub_name)
                    pv_list.append(name)
                return pv_list
        else:
            raise ValueError('no name style selected')
        # -----------


def describeKeyword(actor, keyword, reg=None):
    kdict = KeysDictionary.load(actor)
    key = kdict[keyword]
    if reg == None:
        pass
    else:
        if reg not in key.name:
            return
    print("------------------")
    print("actor: %s" % (actor))
    ck = configKey(actor, keyword, prefix="25m", opt="jb1")
    if opts.short_print:
        for i, name in enumerate(ck.names):
            ss = "    n=%s  pv=%s" % (i + 1, ck.getName(i))
            tp = ck.getType(i)
            ss = "%s,  type=%s" % (ss, tp)
            if tp == "RepeatedValueType":
                ss = "%s,  RepType=%s,  Nmin=%s,  Nmax=%s" \
                     % (ss, ck.getRepType(i), ck.getRepMin(i), ck.getRepMax(i))
            print(ss)
    else:
        print(key.describe())
        for i, name in enumerate(ck.names):
            ss = "    n=%s  pv=%s" % (i + 1, ck.getName(i))
            print(ss)
    global total
    total = total + 1


def describeActor(actor, reg=None):
    kdict = KeysDictionary.load(actor)
    # print kdict.describe()  # command to print description for all keywords for the actor
    for item, keyword in sorted(kdict.keys.items()):
        if (opts.keyword != None):
            if keyword.name == opts.keyword:
                describeKeyword(actor, keyword.name, reg=reg)
        else:
            describeKeyword(actor, keyword.name, reg=reg)


def describeActors(reg=None):
    for actor in sorted(keyDictionaries):
        if (opts.actor != None):
            if actor == opts.actor:
                describeActor(actor, reg)
        else:
            describeActor(actor, reg)


if __name__ == "__main__":
    # parser = optparse.OptionParser()
    parser.add_option('-a', '--actor', help='Actor to find, default is All',
                      dest='actor', default=None)
    parser.add_option('-k', '--keyword', help='Keyword to find, default is All',
                      dest='keyword', default=None)
    parser.add_option('-r', '--regex',
                      help='regex to search keywords, default is All',
                      dest='reg', default=None)
    parser.add_option('-s', '--short', help='short pv summary',
                      dest='short_print', default=False, action='store_true')
    (opts, args) = parser.parse_args()

    actor = opts.actor;
    keyword = opts.keyword;
    reg = opts.reg

    print("==============================")
    describeActors(reg)

    # if (actor==None):
    #    describeActors(reg)
    #    print "Called describeActors"
    # elif ((actor!=None)and(keyword==None)):
    #    describeActor(actor, reg)
    #    print "Called describeActor"
    # elif ((actor!=None)and(keyword!=None)):
    #    describeKeyword(actor,keyword,reg)
    #    print "Called describeKeyword"
    # else:
    #    print "invalid input"	

    print("==============================")
    if total == 0:
        print("Did not find any keywords")
    else:
        print("Total keyword found %s " % total)
