#!/usr/bin/env python3

import pytest
import subprocess as sub
from bin import list_collisions

def test_noargs():
    sub.call(list_collisions.__file__, shell=True)
    
def test_oor():
    sub.call([list_collisions.__file__, "-o"], shell=True)

if __name__ == "__main__":
    pytest.main()
    