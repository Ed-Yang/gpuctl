#!/usr/bin/env python3

import os
import sys
import time
import re
import argparse
import subprocess as sb
from threading import Thread
import pynvml as nv

from gpuctl import logger
from gpuctl import PciDev, GpuAMD, GpuNV
from gpuctl import FileVarMixn as fv
from gpuctl import ShellCmdMixin as sc

__all__ = ['GpuCtl']


class GpuCtl():

    INTERVAL = 1
    WAIT_PERIOD = 60

    def __init__(self, **kwargs):

        self.vendors = None

        # overwrite default value with arguments
        valid_keys = ["slots", "gpu_devices", 
                      "fan", "curve", "delta", "temp", "tas", "verbose"]
        for key in valid_keys:
            setattr(self, key, kwargs.get(key))

        self.thread = None
        self.abort = False

        # if curve is set, apply curve to all GPUs
        if self.curve:
            for gpu_dev in self.gpu_devices:
                gpu_dev.set_curve(self.curve)
            
        # temp
        self.gpu_dict = {}

        # fan
        self.fan_ctrl_flag = False

        # action script
        self.interval = GpuCtl.INTERVAL
        self.wait = GpuCtl.WAIT_PERIOD


    def _fan_control(self, gpu, t):
        if t and not self.fan_ctrl_flag and (self.fan and t > self.fan):
            logger.debug('fan control is activated')
            self.fan_ctrl_flag = True

        if not self.fan_ctrl_flag:
            return

        speed = gpu.temp_to_speed(t)
        ptemp = gpu.prev_temp
        # if pwm change more than delta percentage, then do action
        if (ptemp == None or abs(t - ptemp) > gpu.temp_delta):
            logger.info(
                f"[{gpu.pci_dev.slot_name}/{gpu.name}] current temp. {t}c set speed {speed}%")
            gpu.set_speed(speed)
            gpu.prev_temp = t

    def _failure_action(self, gpu, t):
        if self.tas:
            try:
                logger.warning(f"[{gpu.pci_dev.slot_name}/{gpu.name}] over temperature {self.temp}c, exec {self.tas}")
                rv = sc.exec_script(self.tas, params=gpu.pci_dev.slot_name)
                logger.warning(f"[{gpu.pci_dev.slot_name}/{gpu.name}] result: {rv.decode('utf-8')}")
            except:
                logger.error(f"{gpu.pci_dev.slot_name}/{gpu.name}] over temperature, exec {self.tas} failed !!")
        else:
            logger.warning(f"[{gpu.pci_dev.slot_name}/{gpu.name}] over temperature {self.temp}c, no script defined")


    def update(self, gpu, t, set_flag=False):
        cur_temp = gpu.get_temperature()
        fan_speed = gpu.get_speed()

        if set_flag == True:
            self.gpu_dict[gpu] = {'time': t, 'temp': cur_temp, 'fan':fan_speed}
            return self.gpu_dict[gpu]

        if self.gpu_dict.get(gpu):
            if cur_temp != None and self.temp != None and cur_temp < self.temp:
                self.gpu_dict[gpu] = {'time': t, 'temp': cur_temp, 'fan':fan_speed}
        else:
            self.gpu_dict[gpu] = {'time': t, 'temp': cur_temp, 'fan':fan_speed}

        return self.gpu_dict[gpu]

    def _gpu_thread(self):
        while self.abort != True:
            for gpu in self.gpu_devices:

                time.sleep(self.interval)

                t = time.time()

                tt = self.update(gpu, t)

                if self.verbose:
                    logger.debug(f"[{gpu.pci_dev.slot_name}/{gpu.name}] temperature {self.temp}c fan {tt['fan']}%")

                # fan speed
                self._fan_control(gpu, tt['temp'])


                # action scripts
                if (t - tt['time']) > GpuCtl.WAIT_PERIOD:
                    self._failure_action(gpu, tt['temp'])
                    tt = self.update(gpu, t, set_flag=True)
                    

    def add_gpu_devices(self, gpu_devices):
        cnt = 0
        for gpu in gpu_devices:
            dup_flag = False
            for g in self.gpu_devices:
                if gpu.pci_dev.slot_name == g.pci_dev.slot_name:
                    dup_flag = True
                    logger.debug(f'duplicate slot {gpu.pci_dev.slot_name}')
                    break
            if not dup_flag:
                cnt += 1
                self.gpu_devices.append()
        return cnt

    def start(self):
        if len(self.gpu_devices) == 0:
            logger.error('No GPU found !!!')
            return
        self.thread = Thread(target=self._gpu_thread)
        self.thread.start()

    def stop(self):
        logger.info("exit")
        self.abort = True
        self.thread.join()

    def set_interval(self, intvl=None, wait_period=None):

        interval = intvl if intvl else self.interval
        wait_period = wait_period if wait_period else self.wait

        if interval <= 0 or wait_period < interval:
            logger.error(f'invalid intervals {intvl} {wait_period} !!!')
            return False

        self.interval = interval
        self.wait = wait_period

        return True

if __name__ == '__main__':
    pci_devices = PciDev.discovery()
    gpu_devices = []
    for pdev in pci_devices:
        gpu_dev = None
        if pdev and pdev.is_amd():
            gpu_dev = GpuAMD(pdev)
        if pdev and pdev.is_nvidia():
            gpu_dev = GpuNV(pdev)

        # remove duplicate gpu
        if gpu_dev and gpu_dev.is_gpu():
            gpu_devices.append(gpu_dev)
