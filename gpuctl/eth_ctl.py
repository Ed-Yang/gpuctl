#!/usr/bin/env python3

import sys
import os
import time
import signal
import socket
import argparse
import json
import syslog
from threading import Thread, Timer

from gpuctl import logger
from gpuctl import ShellCmdMixin as sc

__all__ = ['EthCtl', 'scan_miner']

HOST, PORT = "localhost", 3333

MAX_DATA = 512
RX_TIMEOUT = 2

# UP_TIME_THRESHOLD = (2 * 60) # seconds
UP_TIME_THRESHOLD = 30

class CmdType:
    MSG_GET_STAT1 = b'{"method": "miner_getstat1", "jsonrpc": "2.0", "id": 0 }\n'
    MSG_RESTART  = b'{"method":"miner_restart", "id":1,"jsonrpc":"2.0"}\n'
    MSG_REBOOT  = b'{"method":"miner_boot", "id":2,"jsonrpc":"2.0"}\n'

def parse_stats(stats, disp_flag=False):

    if stats == None:
        return None

    result = {}

    result['name'] = f"{stats[0]}"[:16]
    result['uptime'] = int(stats[1]) * 60

    summary = stats[2].split(';')
    result['total'] = int(summary[0])
    result['accept'] = int(summary[1])
    result['reject'] = int(summary[2])
    result['rate'] = [int(i) for i in stats[3].split(';')] 

    tf = stats[6].split(';')
    result['temp'] = tf[0::2]
    result['temp'] = [int(i) for i in result['temp']]
    result['temp_high'] = max(result['temp']) 
    result['fan'] = tf[1::2]
    result['fan'] = [int(i) for i in result['fan']] 
    
    if disp_flag:
        print(f"{result['name']}: {result['uptime']}m {result['rate']}Mh/s {result['temp']}C {result['fan']}%")

    return result


def do_cmd(host, port, cmd):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (host, port)
    json_data = None

    try:
        sock.connect(server_address)

        # Send data
        message = cmd
        sock.sendall(message)

        # Look for the response
        sock.settimeout(RX_TIMEOUT)
        data = sock.recv(MAX_DATA)
        if data:
            json_data = json.loads(data)['result']

    # except socket.timeout as e:
    except:
        logger.debug(f'net command {cmd} timeout')
    finally:
        sock.close()

    return json_data

class EthMiner():
    def __init__(self, address, port, pid):
        self.address = address
        self.port = port
        self.pid = pid

    def get_address(self):
        return (self.address, self.port)

    def get_stats(self):
        result = do_cmd(self.address, self.port, CmdType.MSG_GET_STAT1)
        stats = parse_stats(result)
        return stats

    def restart(self, rmode):
        result = None

        if rmode == 1:
            result = do_cmd(self.address, self.port, CmdType.MSG_RESTART)
        elif rmode == 2:
            os.kill(self.pid, signal.SIGKILL) # signal.SIGTERM or signal.SIGKILL 
        else:
            pass

        return result

    def reboot(self):
        result = False
        ret = do_cmd(self.address, self.port, CmdType.MSG_REBOOT)
        if ret != None:
            result = ret
        return result

class EthMon(EthMiner):
    def __init__(self, address, port, pid, max_temp, min_rate):
        self.name = None
        self.uptime = None
        self.cur_temp = None
        self.cur_rate = None
        self.max_temp = max_temp
        self.min_rate = min_rate
        self.last_update = time.time() # last success call update method
        self.last_temp = time.time() # last normal temperature
        self.last_rate = time.time() # last normal rate
        super(EthMon, self).__init__(address, port, pid)

    def update(self):
        r = self.get_stats()
        if r == None:
            return False

        cur_time = time.time()
        self.last_update = cur_time

        self.name = r['name']
        self.uptime = r['uptime']

        self.cur_temp = r['temp']
        self.cur_rate = r['rate']

        max_t = max(r['temp'])
        min_r = min(r['rate'])

        if self.max_temp != None:
            if max_t <= self.max_temp:
                self.last_temp = cur_time
        else:
            self.last_temp = cur_time

        if self.min_rate != None:
            if min_r > self.min_rate:
                self.last_rate = cur_time
        else:
            self.last_rate = cur_time

        # prevent the unstable miner being add to watch list
        if self.uptime < UP_TIME_THRESHOLD:
            return False

        return True

def scan_miner():
    miners = []
    cmd = "lsof -i -P -n | grep -E 'miner|Phoenix' | grep LISTEN"
    ret = sc.exec_cmd(cmd)
    lines = ret.decode('utf-8').split('\n')
    for l in lines:
        items = l.split()
        for i in items:
            address = i.split(':')
            if len(address) == 2: # address:port
                pid = int(items[1])
                port = int(address[1])
                addr = 'localhost' if address[0] == '*' else address[0]
                # some miners will spawn thread, skip duplicate port
                dup_port = any(m.port == port for m in miners)
                if not dup_port:    
                    # print(f'dup port {port}')
                    miners.append(EthMiner(addr, port, pid))
                

    return miners

class EthCtl:

    BASE_PORT = 3333
    QUERY_INTERVAL = 5 # seconds
    WAIT_PERIOD = 120 # delay time before take action

    def __init__(self, **kwargs):

        valid_keys = ["base", "temp", "rate", "wait", "rmode", "delay", "script", "verbose"]
        for key in valid_keys:
            setattr(self, key, kwargs.get(key))

        self.thread = None
        self.abort = False


    def _eth_thread(self):

        syslog.syslog(syslog.LOG_INFO, 'started.')

        t_msg = f"{self.temp}c" if self.temp != None else '-' 
        r_msg = f"{self.rate} kh/s" if self.rate != None else '-' 

        logger.info(f"query intervel: {self.interval} wait-time: {self.wait}")
        logger.info(f"temperature threshold: {t_msg}")
        logger.info(f"hashrate threshold: {r_msg}")
        logger.info(f"restart mode: {self.rmode} delay: {self.delay} script: {self.script}")
        print('\n')

        miner_dict = {}

        while self.abort != True:
            time.sleep(EthCtl.QUERY_INTERVAL)

            # re-scan miner
            miners = scan_miner()
            if self.verbose:
                    logger.debug(f"check miner status (total {len(miners)})")

            # add new miners
            for m in miners:
                addr = m.get_address()
                mon = miner_dict.get(addr)
                if mon == None:
                    mon = EthMon(addr[0], addr[1], m.pid, self.temp, self.rate)
                    if mon.update() == False:
                        continue
                    miner_dict[addr] = mon
                    msg = f"add miner {mon.name}:{mon.port} pid {mon.pid}"
                    logger.info(msg)
                    syslog.syslog(syslog.LOG_INFO, msg)


            cur_time = time.time()

            # check threshold
            for key in list(miner_dict):
            # for addr, mon in miner_dict.items():
                mon = miner_dict[key]
                if mon.update() == False:
                    continue

                name = mon.name
                dev_id = mon.port - self.base
                pid = mon.pid
                port = mon.port
                cur_temp = mon.cur_temp
                cur_rate = mon.cur_rate
                max_temp = max(cur_temp)
                min_rate = min(cur_rate)

                if self.verbose:
                    logger.debug(f"{name}:{port} dev {dev_id} temp {cur_temp} rate {cur_rate}")

                restart_flag = False
                if (cur_time - mon.last_temp) > self.wait:
                    logger.warning(f"{name}:{port} dev {dev_id} temp {max_temp} over threshold")
                    restart_flag = True
                if (cur_time - mon.last_rate) > self.wait:
                    logger.warning(f"{name}:{port} dev {dev_id} rate {min_rate} under threshold")
                    restart_flag = True

                if restart_flag:
                    # msg = f"{name}:{port} dev {dev_id} temp {cur_temp} rate {cur_rate}"
                    # logger.warning(msg)
                    # syslog.syslog(syslog.LOG_WARNING, msg)

                    # check rmode first
                    if self.rmode :
                        msg = f"{name}:{port} dev {dev_id} restarting pid {pid} mode {self.rmode} "
                        logger.warning(msg)
                        syslog.syslog(syslog.LOG_WARNING, msg)
                        mon.restart(self.rmode)
                        logger.debug(f"{name}:{port} miner removed")
                        miner_dict.pop(mon.get_address())

                    if self.script :
                        params = f"{dev_id} {port} {max_temp} {min_rate}"
                        if self.delay != None:
                            msg = f"{name}:{port} delay {self.delay} exec {self.script} {params}"
                            task = Timer(self.delay, sc.exec_script, [self.script, params, True])
                            task.start()
                        else:
                            msg = f"{name}:{port} exec {self.script} {params}"
                            sc.exec_script(self.script, params=params, no_wait=True)
                        logger.warning(msg)
                        syslog.syslog(syslog.LOG_WARNING, msg)

            # remove out-dated miner
            for key in list(miner_dict):
                mon = miner_dict[key]
                if (cur_time - mon.last_update) > self.wait:
                    msg = f"{mon.name}:{mon.port} miner removed"
                    logger.info(msg)
                    syslog.syslog(syslog.LOG_INFO, msg)
                    miner_dict.pop(key)

        syslog.syslog(syslog.LOG_INFO, 'stopped.')


    def start(self):
        self.thread = Thread(target=self._eth_thread)
        self.thread.start()

    def stop(self):
        logger.info("exit")
        self.abort = True
        self.thread.join()

    def set_interval(self, intvl=None, wait_period=None):

        interval = intvl if intvl else self.interval
        wait_period = wait_period if wait_period else self.wait_period

        if interval <= 0 or wait_period < interval:
            logger.error(f'invalid intervals {intvl} {wait_period} !!!')
            return False

        self.interval = interval
        self.wait = wait_period

        return True


if __name__ == "__main__":

    def sigstop(a ,b):
        print(f'exit') 
        sys.exit(0)

    signal.signal(signal.SIGINT, sigstop)

    miners = scan_miner()

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
                
