#!/usr/bin/env python3

from re import U
import unittest

from gpuctl import PciDev, GpuDev, GpuAMD, GpuNV


class TestGpu(unittest.TestCase):
    def test_get_temp(self):
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

        for gpu in gpu_devices:
            gpu.get_temperature()

    def test_get_speed(self):
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

        for gpu in gpu_devices:
            gpu.get_speed()

class TestCurve(unittest.TestCase):
    def test_valid_curve(self):
        curve = [[0,0], [10,10], [50,50], [100,100]]
        rv = GpuDev.check_curve(curve)
        self.assertTrue(rv)

    def test_zero_curve(self):
        curve = []
        rv = GpuDev.check_curve(curve)
        self.assertFalse(rv)

    def test_order(self):
        curve = [[10,0], [10,10], [50,50], [100,100]]
        rv = GpuDev.check_curve(curve)
        self.assertTrue(rv)

        curve = [[20,0], [10,10], [50,50], [100,100]]
        rv = GpuDev.check_curve(curve)
        self.assertFalse(rv)

        curve = [[10,20], [10,10], [50,50], [100,100]]
        rv = GpuDev.check_curve(curve)
        self.assertFalse(rv)

        curve = [[10,0], [10,10], [50,50], [0,0]]
        rv = GpuDev.check_curve(curve)
        self.assertFalse(rv)

    def test_mock(self):

        slot_name = '1111:11:11.1'
        pci_id = '1111:1111'
        pdev = PciDev(slot_name, pci_id, 'mock pci')
        self.assertIsNotNone(pdev)
        self.assertEqual(pdev.vendor_name(), 'Other')

        self.assertIsNotNone(pdev)
        gpu_dev = GpuDev(pdev)
        self.assertIsNotNone(gpu_dev)


if __name__ == '__main__':
    unittest.main()
