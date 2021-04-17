#!/usr/bin/env python3

import sys
import os
from gpuctl import logger, DRYRUN

import subprocess as sb

__all__ = ['FileVarMixn', 'ShellCmdMixin']

class FileVarMixn(object):
    @staticmethod
    def read_file_value(folder, filename):
        path = folder.rstrip('/') + '/' + filename
        value = None
        try:
            with open(path, 'r') as f:
                t = f.readline()
                value = int(t.strip('\n'))
        except:
            logger.error(f"cannot read value from {path} !!!")

        return value

    @staticmethod
    def read_file_str(folder, filename):
        path = folder.rstrip('/') + '/' + filename
        value = None
        try:
            with open(path, 'r') as f:
                t = f.readline()
                value = str(t.strip('\n'))
        except:
            logger.error(f"cannot read value from {path} !!!")

        return value

    @staticmethod
    def write_file_value(folder, filename, value):
        path = folder.rstrip('/') + '/' + filename
        value_str = str(value)

        if DRYRUN:
            return True
            
        rv = False
        try:
            with open(path, 'w') as f:
                f.write(value_str)
            rv = True
        except PermissionError:
            logger.error(f'needs root priviledge ({path}) !!!')
            # sys.exit(0)

        except:
            logger.error(f"cannot write value {value} to {path} !!!")

        return rv

    @staticmethod
    def read_inifile_value(folder, filename, cfname):
        path = folder.rstrip('/') + '/' + filename
        value = None
        try:
            with open(path, 'r') as f:
                for line in f:
                    name, value = line.lstrip(' ').strip('\n').split('=', 1)
                    if name == cfname:
                        break
        except:
            pass
        return value

class ShellCmdMixin(object):
    @staticmethod
    def exec_cmd(cmd):
        session = sb.Popen(cmd, shell=True, stdout=sb.PIPE, stderr=sb.PIPE)
        data, err = session.communicate()
        if err:
            raise Exception("Error: " + str(err))
        return data

    @staticmethod
    def exec_script(script, params=None, no_wait=False):
        """
        script must have executable permission (chmod +x script)
        """

        logger.info(f"exec script {script} {params} no_wait {no_wait}")

        if no_wait == True:
            cmd =  'nohup' + ' ' + script + ' ' + params
            session = sb.Popen(cmd.split(), 
                preexec_fn=os.setpgrp,
                stdout=open('/dev/null', 'w'), 
                stderr=open('/dev/null', 'w')
                )
            return None
        else:
            cmd = script + ' ' + params
            session = sb.Popen(cmd, shell=True, 
                stdout=sb.PIPE, stderr=sb.PIPE
                )
            data, err = session.communicate()
            if err:
                raise Exception("Error: " + str(err))
            return data