#!/usr/bin/env python

'''
Source
http://hroe.me/2016/07/25/lessfits-grepfits/

FLAVOR  = 'science '           / exposure type, SDSS spectro style  

'''

import gzip
import sys

def grepfitsPro(argv):

    keywords = argv[1].replace(',', ' ').split()

    new_output = ['filename']
    for cur_keyword in keywords:
        new_output.append(cur_keyword)
    output = [new_output]

    for cur_filename in argv[2:]:
        new_output = [cur_filename + ':']
        if cur_filename.endswith('.gz'):
            openfile = lambda x: gzip.open(x, 'r')
        else:
            openfile = lambda x: open(x, 'r')
        with openfile(cur_filename) as f:
            hdr = []
            curline = f.read(80)
            while not curline.startswith('END                            '):
                hdr.append(curline)
                curline = f.read(80)
        for cur_keyword in keywords:
            search_keyword = '{0:8s}='.format(cur_keyword)
            possible_lines = [a for a in hdr if a.startswith(search_keyword)]
            if len(possible_lines) == 0:
                continue
            possible_lines = possible_lines[0]   # TODO: fix that if more than one match, only using first
            new_item = possible_lines.split('=', 1)[1].split('/', 1)[0].strip()
            if new_item.startswith('"') or new_item.startswith("'"):
                new_item = new_item[1:]
            if new_item.endswith('"') or new_item.endswith("'"):
                new_item = new_item[:-1]
            new_output.append(new_item)
        output.append(new_output)
    return output


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("""
Usage: grepfits keywords filename ...
  keywords:  can be comma-separated list, e.g.  DATE,EXPTIME,RA,DEC
             or, 
             a single or double quote enclosed string with comma or space 
             separators,  e.g.:   \"DATE EXPTIME RA,DEC\"
 filename:  either a filename, space separated list of filenames,  
             or an expandable pattern
             e.g.:   x0101.fits.gz
             e.g.:   x*.fits.gz
""")
        exit()
    
    print("")    
    print("sys=", sys.argv)
    print("")
        
        
    output=grepfitsPro(sys.argv)

     # output_lengths = [max([len(entry) for entry in outputline]) for outputline in output]
    output_lengths = [max([len(outputline[position]) for outputline in output]) for position in range(len(output[0]))]
    nspaces = 1
    for outputline in output:
        outstr = ('{0:' + str(output_lengths[0]) + 's}').format(outputline[0])
        for i,outlen in enumerate(output_lengths[1:]):
            outstr += ' '*nspaces + ('{0:' + str(outlen) + 's}').format(outputline[i+1])
        print(outstr)

