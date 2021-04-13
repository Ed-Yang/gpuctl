#!/usr/bin/env python3

import unittest

from gpuctl import PciDev, GpuDev

__all__ = ['GpuOk', 'GpuNak']

RATE_1M  = 1000
RATE_30M = 30000


class GpuOk(GpuDev):
    def is_gpu(self):
        return True

    def is_working(self):
        return True

    def get_temperature(self):
        return 30

    def get_speed(self):
        return 10

    def set_speed(self, percentage):
        self.speed = percentage

class GpuNak(GpuDev):
    def is_gpu(self):
        return True

    def is_working(self):
        return True

    def get_temperature(self):
        return 70

    def get_speed(self):
        return 10
        
    def set_speed(self, percentage):
        self.speed = percentage

