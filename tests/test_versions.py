#!/usr/bin/env python3
import unittest
import subprocess as sub
from bin import versions


class TestSPVersion(unittest.TestCase):
    def test_no_args(self):
        output = sub.Popen(versions.__file__, stderr=sub.PIPE,
                          stdout=sub.PIPE)
        for line in output.stderr.read().decode('utf-8').splitlines():
            print(line)
            self.assertNotIn('not found', line,
                             msg='Package manager or package not found')
        # self.assertEqual(output.returncode, 0)


if __name__ == '__main__':
    unittest.main()
