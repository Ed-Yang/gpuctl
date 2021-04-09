#!/usr/bin/env python3

import sys
import time
import signal
import socket
import argparse
import json

from gpuctl import ShellCmdMixin as sc

__all__ = ['MinerCtl', 'scan_miner']

HOST, PORT = "localhost", 3333

MAX_DATA = 512
RX_TIMEOUT = 2

UP_TIME_THRESHOLD = (3 * 60) # seconds

QUERY_INTERVAL = 5 # seconds
OVER_THRESHOLD_PERIOD = 180 # seconds

RATE_COUNTDOWN = int(OVER_THRESHOLD_PERIOD/QUERY_INTERVAL)
TEMP_COUNTDOWN = int(OVER_THRESHOLD_PERIOD/QUERY_INTERVAL)

class CmdType:
    MSG_GET_STAT1 = b'{"method": "miner_getstat1", "jsonrpc": "2.0", "id": 0 }\n'
    MSG_RESTART  = b'{"method":"miner_restart", "id":1,"jsonrpc":"2.0"}\n'
    MSG_REBOOT  = b'{"method":"miner_boot", "id":2,"jsonrpc":"2.0"}\n'

def parse_stats(stats, disp_flag=False):

    if stats == None:
        return None

    result = {}

    result['miner'] = stats[0]
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
        print(f"{result['miner']}: {result['uptime']}m {result['rate']}Mh/s {result['temp']}C {result['fan']}%")

    return result

def scan_miner():
    tcp_ports = []
    cmd = "lsof -i -P -n | grep -E 'miner|Phoenix' | grep LISTEN"
    ret = sc.exec_cmd(cmd)
    items = ret.split(b' ')
    for i in items:
        address = i.split(b':')
        if len(address) == 2: # address:port
            addr = 'localhost' if address[0] == '*' else address[0]
            tcp_ports.append((addr, int(address[1])))
    return tcp_ports

def do_cmd(host, port, cmd):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', port)
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
        print('timeout')
    finally:
        # print('closing socket')
        sock.close()

    return json_data

class MinerCtl:
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def get_stats(self):
        result = do_cmd(self.address, self.port, CmdType.MSG_GET_STAT1)
        stats = parse_stats(result)
        return stats

    def restart(self):
        result = False
        ret = do_cmd(self.address, self.port, CmdType.MSG_RESTART)
        if ret != None:
            result = ret
        return result

    def reboot(self):
        result = False
        ret = do_cmd(self.address, self.port, CmdType.MSG_REBOOT)
        if ret != None:
            result = ret
        return result

def monitor(mctl, rate, temp, verbose):

    rate_cnt = RATE_COUNTDOWN
    temp_cnt = TEMP_COUNTDOWN

    print('start monitoring ....')
    while True:
        time.sleep(QUERY_INTERVAL)
        result = mctl.get_stats()
        if result == None:
            print('cannot get stats')
            continue
        
        if int(result['uptime']) < UP_TIME_THRESHOLD:
            print(f"wait util {UP_TIME_THRESHOLD}, uptime: {result['uptime']} ...")
            rate_cnt = RATE_COUNTDOWN
            temp_cnt = TEMP_COUNTDOWN
            continue

        if rate != None and result['total'] <= rate:
            rate_cnt -= 1
            print(f"rate under threshold current {result['total']} kh/s threshold {rate} kh/s countdown {rate_cnt}/{RATE_COUNTDOWN}")
        else:
            rate_cnt = RATE_COUNTDOWN

        if temp != None and result['temp_high'] >= temp:
            temp_cnt -= 1
            print(f"temp over threshold current {result['temp_high']}c threshold {temp}c countdown {temp_cnt}/{TEMP_COUNTDOWN}")
        else:
            temp_cnt = TEMP_COUNTDOWN

        if verbose:
            print(f"rate: {result['total']} kh/s temp: {result['temp_high']}c countdown {rate_cnt}/{temp_cnt}")

        if rate_cnt <= 0 or temp_cnt <= 0:
            print(f"restart miner: rate {result['total']} kh/s temp {result['temp_high']}c")
            mctl.restart()
            rate_cnt = RATE_COUNTDOWN
            temp_cnt = TEMP_COUNTDOWN
            print(f"wait 30s for miner restart") 
            time.sleep(30)

if __name__ == "__main__":

    def sigstop(a ,b):
        print(f'exit') 
        sys.exit(0)

    signal.signal(signal.SIGINT, sigstop)

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default=HOST, help="host address (default: localhost)")
    parser.add_argument('--port', type=int, default=PORT, help="tcp port number (default: 3333)")
    parser.add_argument('--cmd', type=int, default=0, help="0: get_stats, 1: restart (default: 0)")
    parser.add_argument('--rate', type=int, help="under rate restart")
    parser.add_argument('--temp', type=int, help="over temp restart")
    parser.add_argument('--wait', type=int, help="wait for rx timeout in seconds (default: 2)")
    parser.add_argument('--scan', action='store_true',
                        help="scan miner's info through network management api")
    parser.add_argument('--verbose', action='store_true', help="show debug message")
    args = parser.parse_args()

    # HOST = (args.host or HOST)
    # PORT = (args.port or PORT)

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
        

    minerctl = MinerCtl(args.host, args.port)

    result = None
    if args.rate != None or args.temp != None:
        monitor(minerctl, args.rate, args.temp, args.verbose)
    else:
        if args.cmd == None or args.cmd == 0:
            result = minerctl.get_stats()
        elif args.cmd == 1:
            result = minerctl.restart()
        elif args.cmd == 2:
            result = minerctl.reboot()
        else:
            sys.exit(0)
    
    print('result: ', result)