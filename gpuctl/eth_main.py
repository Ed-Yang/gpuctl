#!/usr/bin/env python3

import sys
import signal
import argparse
import logging
import syslog

from gpuctl import DRYRUN, GpuCtl, logger
from gpuctl import PciDev, GpuDev, GpuAMD, GpuNV

from gpuctl import EthCtl, scan_miner

def run():

    eth_ctl = None

    def sigstop(a, b):
        eth_ctl.stop()

    signal.signal(signal.SIGINT, sigstop)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    parser = argparse.ArgumentParser()

    # miner
    parser.add_argument('-l', '--list', action='store_true',
                        help="list all miners")

    parser.add_argument('-b', '--base', type=int, default=EthCtl.BASE_PORT,
                        help="tcp port offset, ie. device N is listened on base + N")

    # timer
    parser.add_argument('--interval', type=int, default=EthCtl.QUERY_INTERVAL,
                        help="monitoring interval")

    parser.add_argument('-w', '--wait', type=int, default=EthCtl.WAIT_PERIOD,
                        help="count down interval")

    # temperature monitoring
    parser.add_argument('-t', '--temp', type=int,
                        help="over temperature action threshold")

    # rate monitoring
    parser.add_argument('-r', '--rate', type=int, default=1000,
                        help="under rate threshold (default: 1000 kh)")

    # action
    parser.add_argument('--rmode', type=int, default=0,
                        help="failure restart, 0: none, 1: net restart, 2: kill")

    parser.add_argument('-s', '--script', type=str,
                        help="calling to script on failure")

    # misc
    parser.add_argument('-v', '--verbose',
                        action='store_true', help="show debug message")

    # parse arguments
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    miners = scan_miner()

    print('')

    for miner in miners:
        r = miner.get_stats()
        if r == None:
            continue
        print(f"Miner : {r['name']:12}")
        print(f"Uptime: {r['uptime']}s")
        print(f"Rate(kh) Temp Fan  ")
        print(f"======== ==== ==== ")
        for i in range(len(r['temp'])):
            print(f"{r['rate'][i]:8} {r['temp'][i]:3}c {r['fan'][i]:3}%")
        print('')

    if args.list:
        sys.exit(0)

    # if len(miners) == 0:
    #     print('ethctl: No Miner found, abort !\n')
    #     sys.exit(0)

    if args.temp == None and args.rate == None:
        print('ethctl: Must set --temp and/or --rate !\n')
        sys.exit(0)

    eth_ctl = EthCtl(base=args.base, temp=args.temp, rate=args.rate, 
            rmode=args.rmode, script=args.script, verbose=args.verbose)

    if not eth_ctl.set_interval(intvl=args.interval, wait_period=args.wait):
        print(
            f'Interval error {args.interval}/{args.cdown} !\n')
        sys.exit(0)

    print(f"\nethctl: started\n")
    eth_ctl.start()


if __name__ == '__main__':

    run()
