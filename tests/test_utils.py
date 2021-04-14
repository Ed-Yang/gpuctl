#!/usr/bin/env python3

import unittest
import time

from gpuctl import FileVarMixn as fv
from gpuctl import ShellCmdMixin as sc

from threading import Timer


class TestUtils(unittest.TestCase):

    COUNTER = 0

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

    def test_delay_script(self):
        print(f'{time.time()}: test_delay_script')
        script = './tests/ok.sh'
        task = Timer(2, sc.exec_script, [script, '0'])
        task.start()
        time.sleep(5)

    def delay_func(self, script, params=None, no_wait=None):
        print(f'{time.time()}: delay_func called')
        print(f"delay_func: {script} {params} {no_wait}")
        TestUtils.COUNTER += 1
        
    def test_delay_function(self):
        wait = 5
        params = [1, 2, 3]
        task = Timer(wait, self.delay_func, ['ok.sh', params, True])
        print(f'{time.time()}: start delay_func')
        task.start()
        time.sleep(2)
        self.assertEqual(TestUtils.COUNTER, 0)
        time.sleep(wait)
        self.assertEqual(TestUtils.COUNTER, 1)



if __name__ == '__main__':
    unittest.main()
