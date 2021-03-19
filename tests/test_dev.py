#!/usr/bin/env python3

import unittest

from gpuctl import PciDev, GpuDev

class TestPci(unittest.TestCase):

    def test_valid_slot(self):
        slot_name = '0000:01:00.0'
        pci_id = '1002:67df'
        
        try:
            pdev = PciDev(slot_name, pci_id, '')
        except:
            pdev = None
            
        self.assertIsNotNone(pdev)
        self.assertEqual(pdev.domain, '0000')
        self.assertEqual(pdev.bus_id, '01')
        self.assertEqual(pdev.slot_id, '00')
        self.assertEqual(pdev.function, '0')

    def test_invalid_slot(self):
        slot_name = '01:00'
        pci_id = '1002:67df'
        try:
            pdev = PciDev(slot_name, pci_id, '')
            self.assertFalse(True)
        except:
            pdev = None

    def test_create(self):

        slot_name = '0000:01:00.0'
        found = False

        # ensure the card is existed then proceed the test
        pci_devices = PciDev.discovery()
        for p in pci_devices:
            if p.slot_name == slot_name:
                found = True
                break

        if not found:
            return

        try:
            pdev = PciDev.create(slot_name=slot_name)
        except:
            pdev = None
        self.assertIsNotNone(pdev)
        self.assertEqual(pdev.domain, '0000')
        self.assertEqual(pdev.bus_id, '01')
        self.assertEqual(pdev.slot_id, '00')
        self.assertEqual(pdev.function, '0')

    def test_mock(self):
        slot_name = '1111:11:11.1'
        pci_id = '1111:1111'

        try:
            pdev = PciDev(slot_name, pci_id, 'mock pci')
        except:
            pdev = None
        
        self.assertIsNotNone(pdev)
        self.assertEqual(pdev.vendor_name(), 'Other')

if __name__ == '__main__':
    unittest.main()
