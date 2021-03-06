#!/usr/bin/env python3

import time
# from re import U
import unittest


from gpuctl import PciDev, GpuCtl, GpuDev, GpuAMD, GpuNV, GpuOk
from gpuctl import GpuOk, GpuNak
        
class TestGpuCtl(unittest.TestCase):

    def test_invalid_key(self):
        gpu_ctl = None
        try:
            gpu_ctl = GpuCtl(slots='aaaa')
            self.assertEqual(gpu_ctl, None)
        except:
            pass

    def test_discover_all(self):

        pci_devices = PciDev.discovery()
        gpu_devices = []
        for pdev in pci_devices:
            gpu = None
            if pdev.is_amd():
                gpu = GpuAMD(pdev)
            if pdev.is_nvidia():
                gpu = GpuNV(pdev)
            if gpu and gpu.is_gpu():
                gpu_devices.append(gpu)

        gpu_ctl = GpuCtl(gpu_devices=gpu_devices)

    def test_discover_vendor(self):

        vendors = ['AMD', 'NVIDIA']
        pci_devices = PciDev.discovery(vendor_filter=vendors)
        gpu_devices = []
        for pdev in pci_devices:
            gpu = None
            if pdev.is_amd():
                gpu = GpuAMD(pdev)
            if pdev.is_nvidia():
                gpu = GpuNV(pdev)
            if gpu and gpu.is_gpu():
                gpu_devices.append(gpu)

        gpu_ctl = GpuCtl(gpu_devices=gpu_devices)

    def test_add_devices(self):

        vendors = ['AMD', 'NVIDIA']
        pci_devices = PciDev.discovery(vendor_filter=vendors)
        gpu_devices = []
        for pdev in pci_devices:
            gpu = None
            if pdev.is_amd():
                gpu = GpuAMD(pdev)
            if pdev.is_nvidia():
                gpu = GpuNV(pdev)
            if gpu and gpu.is_gpu():
                gpu_devices.append(gpu)

        gpu_ctl = GpuCtl(gpu_devices=gpu_devices)
        cnt = gpu_ctl.add_gpu_devices(gpu_devices)
        self.assertEqual(cnt, 0)

    def test_over_temp(self):
        slot_name = '1111:11:11.1'
        pci_id = '1111:1111'
        pdev = PciDev(slot_name, pci_id, 'mock pci')
        self.assertIsNotNone(pdev)
        self.assertEqual(pdev.vendor_name(), 'Other')

        gpu_dev = GpuNak(pdev)
        self.assertIsNotNone(gpu_dev)

        gpu_ctl = GpuCtl(gpu_devices=[gpu_dev], fan=10, temp=20, tas='./tests/ok.sh')
        self.assertNotEqual(gpu_ctl, None)

        rv = gpu_ctl.set_interval(wait_period=10)
        self.assertTrue(rv)

        gpu_ctl.start()
        time.sleep(5)
        gpu_ctl.stop()

    def test_interval(self):
        slot_name = '1111:11:11.1'
        pci_id = '1111:1111'
        pdev = PciDev(slot_name, pci_id, 'mock pci')
        self.assertIsNotNone(pdev)
        self.assertEqual(pdev.vendor_name(), 'Other')

        gpu_dev = GpuOk(pdev)
        self.assertIsNotNone(gpu_dev)

        gpu_ctl = GpuCtl(gpu_devices=[gpu_dev])

        rv = gpu_ctl.set_interval(intvl=1, wait_period=3)
        self.assertTrue(rv)

        rv = gpu_ctl.set_interval(intvl=2, wait_period=20)
        self.assertTrue(rv)

        rv = gpu_ctl.set_interval(intvl=2, wait_period=1)
        self.assertFalse(rv)

    def test_nak_gpu(self):
        slot_name = '1111:11:11.1'
        pci_id = '1111:1111'
        pdev = PciDev(slot_name, pci_id, 'mock pci')
        self.assertIsNotNone(pdev)
        self.assertEqual(pdev.vendor_name(), 'Other')

        gpu_dev = GpuNak(pdev)
        self.assertIsNotNone(gpu_dev)

        gpu_ctl = GpuCtl(gpu_devices=[gpu_dev], verbose=True)

        rv = gpu_ctl.set_interval(wait_period=10)
        self.assertTrue(rv)

        gpu_ctl.start()
        time.sleep(5)
        gpu_ctl.stop()

if __name__ == '__main__':
    unittest.main()
