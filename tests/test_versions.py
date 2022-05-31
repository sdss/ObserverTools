#!/usr/bin/env python3
import pytest
import subprocess as sub
from bin import versions


class TestVersion():
    def test_no_args(self):
        output = sub.Popen(versions.__file__, stderr=sub.PIPE,
                          stdout=sub.PIPE)
        for line in output.stderr.read().decode('utf-8').splitlines():
            print(line)
            assert 'not found' not in line, 'Package manager or package not found'
        # self.assertEqual(output.returncode, 0)


if __name__ == '__main__':
    pytest.main()
