#!/usr/bin/env python3

import  pynvml as nv

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

        INFO_PATH = "/proc/driver/nvidia/gpus/"
        super(GpuNV, self).__init__(pcidev)

        nv.nvmlInit()
        deviceCount = nv.nvmlDeviceGetCount()
        for i in range(deviceCount):
            handle = nv.nvmlDeviceGetHandleByIndex(i)
            info = nv.nvmlDeviceGetPciInfo(handle)
            domain, bus_id, slot_id, function = PciDev.parse_slot_name(
                info.busId.decode('utf-8'))
            if bus_id == self.pci_dev.bus_id and \
               slot_id == self.pci_dev.slot_id and \
               function == self.pci_dev.function:
                ver = nv.nvmlSystemGetDriverVersion().decode('utf-8')
                name = nv.nvmlDeviceGetName(handle).decode('utf-8')
                logger.debug(f"NV[{i}]: Device {name} Driver {ver}")
                self.nv_id = i
                self.nvh = handle
                self.name = 'NV '
                break

        self.curve = GpuNV.CURVE
        self.temp_delta = GpuNV.TEMP_DELTA

    def is_gpu(self):
        return True if self.nvh else False

    def set_speed(self, speed):

        if DRYRUN:
            return

        cmd = f"nvidia-settings -c {self.display} -a [gpu:{self.nv_id}]/GPUFanControlState=1 -a [fan:{self.nv_id}]/GPUTargetFanSpeed={speed}"
        logger.debug(f'exec: {cmd}')
        try:
            sc.exec_cmd(cmd)
            logger.debug(f'[{self.pci_dev.slot_name}/{self.name}] set speed {speed}%')
            self.speed = speed
        except:
            logger.error(f'exec_cmd: {cmd} failed !!')


    def get_speed(self):
        # TODO: nvmlDeviceGetFanSpeed report wrong speed, so return store value
        # s = nv.nvmlDeviceGetFanSpeed(self.nvh)
        s = self.speed
        return s

    def get_temperature(self):
        t = nv.nvmlDeviceGetTemperature(self.nvh, nv.NVML_TEMPERATURE_GPU)
        return t
