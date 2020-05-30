#!/bin/bash

# http://hroe.me/2016/07/25/lessfits-grepfits/
# This script is released under an "MIT License"; see https://opensource.org/licenses/MIT 
# The MIT License (MIT)
# Copyright (c) 2016 Henry Roe (hroe@hroe.me)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

if [ $# -ne 1 ]
then
  echo "lessfits requires a single filename, e.g.:"
  echo "lessfits n1001.fits"
  echo " or "
  echo "lessfits n1001.fits.gz"
  exit 1
fi

python -c "import gzip
cur_filename = '"$1"'
openfile = (lambda x: gzip.open(x, 'r') if cur_filename.endswith('.gz') else lambda x: open(x, 'r')) 
with openfile(cur_filename) as f:
    curline = f.read(80)
    while not curline.startswith('END                            '):
        print(curline)
        curline = f.read(80)
    print(curline)" | less
    
exit 0
