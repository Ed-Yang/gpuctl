#!/usr/bin/env python3

import unittest

from gpuctl import FileVarMixn as fv
from gpuctl import ShellCmdMixin as sc


class TestPci(unittest.TestCase):

    def test_exec_cmd_ok(self):
        cmd = 'python --version'
        try:
            data = sc.exec_cmd(cmd)
        except:
            data = ''

        self.assertIn(b'Python', data)

    def test_exec_cmd_nak(self):
        cmd = 'python --versionxxxx'
        try:
            data = sc.exec_cmd(cmd)
            self.assertFalse(True)
        except:
            pass

    def test_exec_script_ok(self):
        data = sc.exec_script('./tests/ok.sh', params="1")
        self.assertEqual(data, b'1')        
    def test_exec_script_txt(self):
        try:
            data = sc.exec_script('./tests/nak.sh')
            self.assertFalse(True)
        except:
            pass

    def test_exec_script_not_exited(self):
        try:
            data = sc.exec_script('./tests/fake.sh')
            self.assertFalse(True)
        except:
            pass

if __name__ == '__main__':
    unittest.main()
