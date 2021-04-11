#!/usr/bin/env python3

import os

from gpuctl import logger, DRYRUN
from gpuctl import FileVarMixn as fv
from gpuctl import ShellCmdMixin as sc

from . gpu_dev import PciDev, GpuDev

__all__ = ['GpuAMD']


class GpuAMD(GpuDev):
    DRM_DIR = '/sys/class/drm/'
    PWM_MAX = 'pwm1_max'
    PWM_MIN = 'pwm1_min'
    PWM_MODE = 'pwm1_enable'
    PWM_VAL = 'pwm1'
    TEMP_VAL = 'temp1_input'
    PWR_VAL = 'power1_average'

    CURVE = [[0, 0], [40, 0], [50, 30], [55, 50], [60, 60], [
        70, 70], [75, 80], [80, 100], [100, 100]]
    TEMP_DELTA = 2

    def __init__(self, pcidev):
        """
        ls /sys/class/drm | grep "^card[[:digit:]]$"
        check if the pci device is a GPU device and privided by vendor,
        if yes, fill in self.card
        """

        self.card = None
        super(GpuAMD, self).__init__(pcidev)
        card_dirs = [c for c in os.listdir(
            GpuAMD.DRM_DIR) if len(c) <= 6]  # card##

        # locate card dir
        self.hwmon_dir = None
        for card in card_dirs:
            ue_file = f'{GpuAMD.DRM_DIR}{card}/device/uevent'
            slot_name = fv.read_inifile_value('', ue_file, 'PCI_SLOT_NAME')
            if slot_name == self.pci_dev.slot_name:
                self.name = 'AMD'
                self.card = card
                # locate hwmon# dir
                hwmon_root = f'{GpuAMD.DRM_DIR}{self.card}/device/hwmon'
                t = os.listdir(hwmon_root)
                self.hwmon_dir = hwmon_root + '/' + t[0]
                break
        
        # fan
        if self.card:
            self.max = fv.read_file_value(self.hwmon_dir, GpuAMD.PWM_MAX)
            self.min = fv.read_file_value(self.hwmon_dir, GpuAMD.PWM_MIN)

        # curve
        self.curve = GpuAMD.CURVE
        self.temp_delta = GpuAMD.TEMP_DELTA

    def is_gpu(self):
        return True if self.card else False

    def is_working(self):
        return True
        
    def set_speed(self, speed):
        """
        speed: 0~100 (percentage)
        """
        # hwmon_dir = f'{GpuAMD.DRM_DIR}{self.card}/device/hwmon/hwmon?/'
        speed = 100 if speed > 100 else speed
        speed = 0 if speed < 0 else speed
        pwm = int((self.max - self.min) * speed / 100)
        fv.write_file_value(self.hwmon_dir, GpuAMD.PWM_MODE, 0)  # 0: disabled
        fv.write_file_value(self.hwmon_dir, GpuAMD.PWM_MODE, 1)  # 1: manual
        fv.write_file_value(self.hwmon_dir, GpuAMD.PWM_VAL, pwm)
        self.speed = speed
        logger.debug(f'[{self.pci_dev.slot_name}/{self.name}] set speed {speed}% pwm {pwm}')

    def get_speed(self):
        pwn = fv.read_file_value(self.hwmon_dir, GpuAMD.PWM_VAL)
        speed = int(pwn/(self.max-self.min) * 100)
        return speed

    def get_temperature(self):
        # hwmon_dir = f'{GpuAMD.DRM_DIR}{self.card}/device/hwmon/hwmon?/'
        temp = int(fv.read_file_value(self.hwmon_dir, GpuAMD.TEMP_VAL) / 1000)
        self.temperature = temp
        return temp

    def get_pwr(self):
        pwr = int(fv.read_file_value(self.hwmon_dir, GpuAMD.PWR_VAL) / 1000000)
        self.pwr = pwr
        return pwr

