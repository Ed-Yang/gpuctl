#!/usr/bin/env python3

import os
import sys
import time
import re
import pynvml as nv

from gpuctl import logger
from gpuctl import FileVarMixn as fv
from gpuctl import ShellCmdMixin as sc

__all__ = ['PciDev', 'GpuDev']

class PCI_VID:
    VID_AMD = '1002'
    VID_NV = '10DE'

VENDOR_NAME  = {
    PCI_VID.VID_AMD: 'AMD', 
    PCI_VID.VID_NV: 'NVIDIA'
    }

class PciDev():
    """
    slot_name: DDDD:BB:SS.F (domain:bus:slot/device:function)
    """

    @staticmethod
    def parse_slot_name(slot_name):
        try:
            ids = slot_name.split(':')
            domain = ids[0]
            bus_id = ids[1].upper()
            slot_id = ids[2].split('.')[0].upper()
            function = ids[2].split('.')[1].upper()
            return domain, bus_id, slot_id, function
        except:
            # logger.error(f"Invaid slot name: {slot_name}")
            raise Exception(f"Invaid slot name: {slot_name}")



    def __init__(self, slot_name, pci_id, desc):
        self.desc = desc
        self.slot_name = slot_name

        try:
            self.domain, self.bus_id, self.slot_id, self.function = self.parse_slot_name(
                slot_name)
            self.vendor_id = pci_id.split(':')[0].upper()
            self.device_id = pci_id.split(':')[1].upper()
            self._vendor_name = VENDOR_NAME.get(self.vendor_id, 'Other')
        except:
            self.vendor_id = ''
            self.device_id = ''
            self._vendor_name = ''

    def vendor_name(self):
        return self._vendor_name

    def is_amd(self):
        if self.vendor_id == PCI_VID.VID_AMD:
            return True
        else:
            return False

    def is_nvidia(self):
        if self.vendor_id == PCI_VID.VID_NV:
            return True
        else:
            return False

    @classmethod
    def create(cls, slot_name):
        """
        /sys/bus/pci/devices/
        """
        slot_name = slot_name.strip('\'').rstrip('\'')
        SLOT_DIR = f'/sys/bus/pci/devices/{slot_name}'
        domain, bus_id, slot_id, function = cls.parse_slot_name(
            slot_name)

        try:
            vendor_id = fv.read_file_str(SLOT_DIR, 'vendor').strip('0x')
            device_id = fv.read_file_str(SLOT_DIR, 'device').strip('0x')
            pci_id = vendor_id.upper() + ':' + device_id.upper()
            desc = 'Other'
            if vendor_id == PCI_VID.VID_AMD:
                desc = 'AMD'
            elif vendor_id == PCI_VID.VID_NV:
                desc = 'Nvidia'
            else:
                desc = 'Other'
        except:
            return None

        return cls(slot_name, pci_id, desc)

    @staticmethod
    def discovery(vendor_filter=None):
        """
        cretiria: 
            - AMD or Nvida PCI devices
        """
        # self.gpu_devices = []
        pci_devices = []
        cmd = ''
        if vendor_filter:
            cmd = "lspci -D -nn | awk '/" f"{'|'.join(vendor_filter)}" + "/{print $0}'"
        else:
            cmd = "lspci -D -nn"
        try:
            data = sc.exec_cmd(cmd)
            lines = data.decode("utf-8").split('\n')
        except:
            logger.error(f'exec_cmd: {cmd} failed !!')
            lines = []

        desc = ''
        for line in lines:
            if line == '':
                continue
            slot_name, desc = line.split(' ', 1)
            group = re.findall('\[(.*?)\]', desc)
            pdev = None
            for g in group:
                if ':' in g:
                    pcidev = None
                    try:
                        pcidev = PciDev(slot_name, g.upper(), desc)
                        break
                    except:
                        pass

            if vendor_filter:
                if pcidev.vendor_name() in vendor_filter:
                    pci_devices.append(pcidev)
            else:
                pci_devices.append(pcidev)

        return pci_devices

    @staticmethod
    def discovery_by_slots(vendor, slots):
        pci_devices = []
        for sn in slots:
            sn = sn.strip().lstrip()
            sn = sn.strip('\'').lstrip('\'')
            pdev = PciDev.create(sn)

            if pdev != None:
                pci_devices.append(pdev)

class GpuDev():
    def __init__(self, pcidev=None):
        # devices
        self.name = 'Other'
        self.dev_info = {}
        self.dev_info['bios_ver'] = ""
        self.pci_dev = pcidev

        # curve
        self.curve = None
        self.sp_delta = None

        # current info
        self.speed = 0  # percentage
        self.temperature = 0

    # def get_dev_info(self):
    #     return self.dev_info

    def is_gpu(self):
        raise NotImplementedError

    def is_working(self):
        raise NotImplementedError

    def get_temperature(self):
        raise NotImplementedError

    def get_pwr(self):
        raise NotImplementedError

    def get_speed(self):
        raise NotImplementedError

    def set_speed(self, percentage):
        raise NotImplementedError

    @staticmethod
    def check_curve(curve):
        if len(curve) < 2:
            return False

        for i in range(len(curve)-1):
            if curve[i][0] > curve[i+1][0] or curve[i][1] > curve[i+1][1]:
                return False
        return True

    def set_curve(self, curve):
        self.curve = curve

    def temp_to_speed(self, temp):
        """
        assume temp is greater than 0
        """
        speed = None
        for t in range(len(self.curve)):
            if temp < self.curve[t][0]:
                speed = int(self.curve[t - 1][1] + (self.curve[t][1] - self.curve[t - 1][1]) / (
                    self.curve[t][0] - self.curve[t - 1][0]))
                break

        return speed

if __name__ == '__main__':

    pass
