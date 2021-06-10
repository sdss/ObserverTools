#!/usr/bin/env python3
import unittest
import sp_version
import subprocess as sub


class TestSPVersion(unittest.TestCase):
    def test_no_args(self):
        output = sub.Popen(sp_version.__file__, stderr=sub.PIPE)
        for line in output.stderr.read().decode('utf-8').splitlines():
            print(line)
            self.assertNotIn('not found', line,
                             msg='Package manager or package not found')


if __name__ == '__main__':
    unittest.main()
