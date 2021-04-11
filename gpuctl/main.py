#!/usr/bin/env python3

import sys
import signal
import argparse
import logging

from gpuctl import DRYRUN, GpuCtl, logger
from gpuctl import PciDev, GpuDev, GpuAMD, GpuNV

from gpuctl import MinerCtl, scan_miner

def show_net_stats():
    cmd = "lsof -i -P -n | grep -E 'miner|Miner' | grep LISTEN"

def run():

    gpu_ctl = None

    def sigstop(a, b):
        gpu_ctl.stop()
        # print(f'exit')
        # sys.exit(0)

    signal.signal(signal.SIGINT, sigstop)

    parser = argparse.ArgumentParser()

    # device
    parser.add_argument('-l', '--list', action='store_true',
                        help="list all GPU cards")
    parser.add_argument(
        '-s', '--slots', type=str, help="use PCI slot name to locate GPU (ie. 0000:01:00.0/0000:01:00.1)")
    parser.add_argument('-a', '--amd', action='store_true',
                        help="only use AMD GPU")
    parser.add_argument('-n', '--nvidia', action='store_true',
                        help="only use Nvidia GPU")

    # timer
    parser.add_argument('--interval', type=int, default=GpuCtl.INTERVAL,
                        help="monitoring interval")

    # fan control
    parser.add_argument('--set-speed', type=int, choices=range(0,101), metavar="[0-100]", 
                        help="set the fan speed (0~100)")
    parser.add_argument('-f', '--fan', type=int,
                        help="if temperature is exceed than FAN once, activate fan control (default:70)")
    parser.add_argument('-d', '--delta', type=int, default=2,
                        help="set fan speed if temperature diff %% is over DELTA (defaut:2)")

    # gpu lost failure detection
    parser.add_argument('--las', type=str, help="gpu lost action script")

    # temperature monitoring/actions
    parser.add_argument('--temp', type=int,
                        help="over temperature action threshold")
    parser.add_argument('--temp-cdown', type=int, default=GpuCtl.TEMP_CDOWN,
                        help="over temperature count down")
    parser.add_argument('--tas', type=str,
                        help="over temperature action script")

    # rate monitoring/actions
    parser.add_argument('--rms', type=str, help="rate monitoring script")
    parser.add_argument('--rate', type=int, default=1000,
                        help="under rate threshold (default: 1000 kh)")
    parser.add_argument('--rate-cdown', type=int, default=GpuCtl.RATE_CDOWN,
                        help="under rate count down")
    parser.add_argument('--ras', type=str, help="under rate action script")

    parser.add_argument('--curve', type=str,
                        help="set temp/fan-speed curve (ie. 0:0/10:10/80:100)")

    # remote management
    parser.add_argument('--scan', action='store_true',
                        help="scan miner's info through network management api")

    # misc
    parser.add_argument('-v', '--verbose',
                        action='store_true', help="show debug message")

    # parse arguments
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if args.scan:
        # 12, 8, 4, 4, 
        ports = scan_miner()
        for addr, port in ports:
            minerctl = MinerCtl(addr, port)
            r = minerctl.get_stats()
            if r == None:
                continue
            print(f"Miner : {r['miner']:12}")
            print(f"Uptime: {r['uptime']}s")
            print(f"Rate(kh) Temp Fan  ")
            print(f"======== ==== ==== ")
            for i in range(len(r['temp'])):
                print(f"{r['rate'][i]:8} {r['temp'][i]:3}c {r['fan'][i]:3}%")
            print('')
                
        sys.exit(0)

    # parse curve
    curve = None
    if args.curve:
        clst = args.curve.split('/')
        for c in clst:
            if ':' not in c:
                print(f'Invaid curve: [{args.curve}]')
                sys.exit(0)

        if clst:
            curve = [[int(c.split(':')[0]), int(c.split(':')[1])]
                     for c in clst]
        if curve and GpuDev.check_curve(curve):
            print(f'Applying curve: [{args.curve}]')
        else:
            print(f'Invaid curve: [{args.curve}]')

    # by slots
    gpu_devices = []
    slot_names = []

    # parse slot
    slots = None
    if args.slots:
        # by slot
        slots = args.slots.split('/')
        for sn in slots:
            sn = sn.strip().lstrip()
            sn = sn.strip('\'').lstrip('\'')
            pdev = PciDev.create(sn)
            gpu_dev = None
            if pdev and pdev.is_amd():
                gpu_dev = GpuAMD(pdev)
            if pdev and pdev.is_nvidia():
                gpu_dev = GpuNV(pdev)
            if gpu_dev and gpu_dev.is_gpu():
                gpu_devices.append(gpu_dev)
                slot_names.append(gpu_dev.pci_dev.slot_name)
    else:
        # by vendors
        vendors = []
        if args.amd:
            vendors.append('AMD')

        if args.nvidia:
            vendors.append('NVIDIA')

        pci_devices = PciDev.discovery(vendors)
        for pdev in pci_devices:
            gpu_dev = None
            if pdev and pdev.is_amd():
                gpu_dev = GpuAMD(pdev)
            if pdev and pdev.is_nvidia():
                gpu_dev = GpuNV(pdev)

            # remove duplicate gpu
            if gpu_dev and gpu_dev.is_gpu() and pdev.slot_name not in slot_names:
                gpu_devices.append(gpu_dev)

    # list monitored devices
    print("\n")
    print("ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR    Working")
    print("-- ------------ -------- ----------- ----- ---- ------ -------")

    cnt = 1
    for gpu in gpu_devices:
        pdev = gpu.pci_dev
        # set fan speed
        if args.set_speed != None:
            gpu.set_speed(args.set_speed)
        working = gpu.is_working()
        msg  = f"{cnt:2} {pdev.slot_name} {pdev.vendor_name():8} [{pdev.vendor_id}:{pdev.device_id}]"
        msg += f"{gpu.get_temperature():4}c {gpu.get_speed():3}% {gpu.get_pwr():6.2f}w {working}"
        print(msg)
        cnt += 1

    if args.list:
        sys.exit(0)

    if args.set_speed != None:
        sys.exit(0)

    if len(gpu_devices) == 0:
        print('No GPU found, abort !\n')
        sys.exit(0)

    # remove not working devices
    for gpu in list(gpu_devices):
        if gpu.is_working() == False:
            gpu_devices.remove(gpu)

    gpu_ctl = GpuCtl(gpu_devices=gpu_devices, fan=args.fan,
                     delta=args.delta, 
                     las=args.las,
                     temp=args.temp, tas=args.tas,
                     rms=args.rms, rate=args.rate, ras=args.ras, curve=curve)

    if not gpu_ctl.set_interval(intvl=args.interval, temp=args.temp_cdown, rate=args.rate_cdown):
        print(
            f'Interval error {args.interval}/{args.temp_cdown}/{args.rate_cdown} !\n')
        sys.exit(0)

    print(f"\ngpuctl: started\n")
    gpu_ctl.start()


if __name__ == '__main__':
    run()
