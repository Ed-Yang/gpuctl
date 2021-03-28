#!/usr/bin/env python3

import pynvml as nv

from gpuctl import logger, DRYRUN
from gpuctl import FileVarMixn as fv
from gpuctl import ShellCmdMixin as sc

from . gpu_dev import PciDev, GpuDev

__all__ = ['GpuNV']


class GpuNV(GpuDev):

    CURVE = [[0, 0], [40, 0], [50, 0], [55, 50], [60, 60], [
        70, 70], [75, 80], [80, 100], [100, 100]]
    TEMP_DELTA = 2

    def __init__(self, pcidev):
        """
        check if the pci device is a GPU device and privided by vendor,
        if yes, fill in self.nvh
        """
        self.nvh = None
        self.display = ':0'
        self.gpu_flag = False

        INFO_PATH = "/proc/driver/nvidia/gpus/"
        super(GpuNV, self).__init__(pcidev)

        nv.nvmlInit()

        self.nvh = None
        self.name = 'NV '
        try:
            self.nvh = nv.nvmlDeviceGetHandleByPciBusId(
                pcidev.slot_name.encode())
            self.nv_id = nv.nvmlDeviceGetIndex(self.nvh)
            self.gpu_flag = True
            self.pcidev = pcidev
        except Exception as e:
            if e.value == nv.NVML_ERROR_GPU_IS_LOST:
                self.gpu_flag = True
            self.working = False
            logger.debug(f'[{self.pci_dev.slot_name}/{self.name}] {str(e)}')

        self.curve = GpuNV.CURVE
        self.temp_delta = GpuNV.TEMP_DELTA

    def is_working(self):
        try:
            h = nv.nvmlDeviceGetHandleByPciBusId(
                self.pcidev.slot_name.encode())
        except Exception as e:
            self.working = False
        return self.working

    def is_gpu(self):
        return True if self.gpu_flag == True else False

    def set_speed(self, speed):

        if DRYRUN:
            return

        if not self.working or self.nvh == None:
            return

        cmd = f"nvidia-settings -c {self.display} -a [gpu:{self.nv_id}]/GPUFanControlState=1 -a [fan:{self.nv_id}]/GPUTargetFanSpeed={speed}"
        logger.debug(f'exec: {cmd}')
        try:
            sc.exec_cmd(cmd)
            logger.debug(
                f'[{self.pci_dev.slot_name}/{self.name}] set speed {speed}%')
            self.speed = speed
        except:
            logger.error(f'exec_cmd: {cmd} failed !!')

    def get_speed(self):
        # TODO: nvmlDeviceGetFanSpeed report wrong speed, so return store value
        # s = nv.nvmlDeviceGetFanSpeed(self.nvh)
        if not self.working or self.nvh == None:
            return 0
        s = self.speed
        return s

    def get_temperature(self):
        if not self.working or self.nvh == None:
            return 0
        t = nv.nvmlDeviceGetTemperature(self.nvh, nv.NVML_TEMPERATURE_GPU)
        return t
