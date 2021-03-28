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
    TEMP_CDOWN = 120 # seconds
    RATE_CDOWN = 120 # seconds

    def __init__(self, **kwargs):

        self.vendors = None

        # overwrite default value with arguments
        valid_keys = ["slots", "gpu_devices",
                      "fan", "delta", "temp", "tas", "rms", "rate", "ras", "curve"]
        for key in valid_keys:
            setattr(self, key, kwargs.get(key))

        self.thread = None
        self.abort = False

        # if curve is set, apply curve to all GPUs
        if self.curve:
            for gpu_dev in self.gpu_devices:
                gpu_dev.set_curve(self.curve)
            
        # fan
        self.fan_ctrl_flag = False

        # action script
        self.interval = GpuCtl.INTERVAL
        self.temp_cdown = GpuCtl.TEMP_CDOWN
        self.rate_cdown = GpuCtl.RATE_CDOWN

        for gpu in self.gpu_devices:
            gpu.prev_temp = None
            gpu.temp_cdown = self.temp_cdown
            gpu.rate_cdown = self.rate_cdown

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

    def _temp_action(self, gpu, t):
        if self.temp and t > self.temp:
            logger.warning(f"[{gpu.pci_dev.slot_name}/{gpu.name}] temp: {t}c/{self.temp}c CD: {gpu.temp_cdown}s")
            gpu.temp_cdown -= self.interval
        else:
            gpu.temp_cdown = self.temp_cdown
            return
        
        # take action
        if gpu.temp_cdown <= 0:
            if self.tas:
                try:
                    rv = sc.exec_script(self.tas, params=gpu.pci_dev.slot_name)
                    logger.info(f"[{gpu.pci_dev.slot_name}/{gpu.name}] over heat, exec script {self.tas}")
                    logger.info(f"[{gpu.pci_dev.slot_name}/{gpu.name}] result: {rv.decode('utf-8')}")
                except:
                    logger.error(f"{gpu.pci_dev.slot_name}/{gpu.name}] over heat, exec script {self.tas} failed !!")
            else:
                logger.warning(f"[{gpu.pci_dev.slot_name}/{gpu.name}] over heat, no action script defined")

            gpu.temp_cdown = self.temp_cdown

    def _get_hashrate(self, gpu, script):
        rate = None
        try:
            rv = sc.exec_script(script, params=gpu.pci_dev.slot_name)
            rate = int(rv.decode('utf-8').strip('\n'))
        except:
            logger.error(f"{gpu.pci_dev.slot_name}/{gpu.name}] get hashrate, exec script {script} failed !!")
        return rate

    def _rate_action(self, gpu, rate):
        if rate and self.rate and rate < self.rate:
            logger.warning(f"[{gpu.pci_dev.slot_name}/{gpu.name}] rate: {rate}/{self.rate} CD: {gpu.rate_cdown}s")
            gpu.rate_cdown -= self.interval
        else:
            gpu.rate_cdown = self.rate_cdown
            return
        
        # take action
        if gpu.rate_cdown <= 0:
            if self.ras:
                try:
                    rv = sc.exec_script(self.ras, params=gpu.pci_dev.slot_name)
                    logger.info(f"[{gpu.pci_dev.slot_name}/{gpu.name}] under rate, exec script {self.tas}")
                    logger.info(f"[{gpu.pci_dev.slot_name}/{gpu.name}] result: {rv.decode('utf-8')}")
                except:
                    logger.error(f"{gpu.name} under rate, exec script {self.tas} failed !!")
            else:
                logger.warning(f"[{gpu.pci_dev.slot_name}/{gpu.name}] under rate, no action script defined")

            gpu.rate_cdown = self.rate_cdown

    def _gpu_thread(self):
        while self.abort != True:
            for gpu in self.gpu_devices:
                time.sleep(self.interval)
                t = gpu.get_temperature()

                # fan speed
                self._fan_control(gpu, t)

                # action scripts
                self._temp_action(gpu, t)

                # rate
                rate = self._get_hashrate(gpu, self.rms) if self.rms else None
                self._rate_action(gpu, rate)

                temp_str = f'temp: {t}/{gpu.temp_cdown}s' if t else ''
                rate_str = f'rate: {rate}/{gpu.rate_cdown}s' if rate else ''
                msg = temp_str + ' ' + rate_str
                logger.debug(f"[{gpu.pci_dev.slot_name}/{gpu.name}] {msg}")


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
        nv.nvmlShutdown()

    def set_interval(self, intvl=None, temp=None, rate=None):

        interval = intvl if intvl else self.interval
        temp_cdown = temp if temp else self.temp_cdown
        rate_cdown = rate if rate else self.rate_cdown

        if interval <= 0 or temp_cdown < interval or rate_cdown < interval:
            logger.error(f'invalid intervals {intvl} {temp} {rate}!!!')
            return False

        self.interval = interval
        self.temp_cdown = temp_cdown
        self.rate_cdown = rate_cdown

        for gpu in self.gpu_devices:
            gpu.temp_cdown = self.temp_cdown
            gpu.rate_cdown = self.rate_cdown

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

    for gpu in gpu_devices:
        rate = gpu.get_hashrate('./scripts/rate.sh')
        print(f'[{gpu.pci_dev.slot_name}/{gpu.name}] rate: {rate}')