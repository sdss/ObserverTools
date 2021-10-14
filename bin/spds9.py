#!/usr/bin/env python3
import sys
import subprocess as sub
from pathlib import Path

args = [arg for arg in sys.argv if
        ((Path(__file__).name not in arg) and ("python" not in arg))]
sub.call([Path(__file__).parent / "ds9_live.py", "-b"] + args)
