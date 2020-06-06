#!/usr/bin/env python3
import unittest
from bin import sp_version
import subprocess as sub


class TestSPVersion(unittest.TestCase):
    def test_no_args(self):
        output = sub.Popen(sp_version.__file__, stderr=sub.PIPE)
        for line in output.stderr.read().decode('utf-8').splitlines():
            self.assertNotIn('not found', line)


if __name__ == '__main__':
    unittest.main()
