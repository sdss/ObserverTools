#!/usr/bin/env python3
import unittest
import subprocess as sub
from bin import sp_version


class TestSPVersion(unittest.TestCase):
    def test_no_args(self):
        output = sub.check_output(sp_version.__file__, timeout=10)
        for line in output.stderr.read().decode('utf-8').splitlines():
            print(line)
            self.assertNotIn('not found', line,
                             msg='Package manager or package not found')


if __name__ == '__main__':
    unittest.main()
