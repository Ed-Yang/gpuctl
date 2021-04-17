# GPU Monitoring and Failure Notification/Recovery

[![CircleCI](https://circleci.com/gh/Ed-Yang/gpuctl.svg?style=svg)](https://circleci.com/gh/Ed-Yang/gpuctl)

While in minging crytocurrency with GPU, although the GPU has built-in thermal control,
but it might not be fitted in some environment and cause hash rate decreases or even GPU
faults.  This project provides a tool to:

- According the detected temperature to change fan speed
- Execute custom action scripts while current temperature of GPU(s) is over a defined threshold
- Execute custom action scripts while current hash rate of GPU(s) is under a defined threshold

Currently, the example of action script are based on the [miner's remote managemen API](https://github.com/ethereum-mining/ethminer/blob/master/docs/API_DOCUMENTATION.md), for different miner, it might be needed to customize locally.


## Environment and Installation

Intel CPU/16G RAM
Ubuntu 18.4/Python3

* Environment setup

    For configuring Nvidia's GPU (ie. fan), it is needed to set the following environment.

    In ~/.profile and/or ~/.bashrc, add:

    ```shell
    export DISPLAY=:0
    export NO_AT_BRIDGE=1
    export XAUTHORITY=/var/run/lightdm/root/:0
    ```

    In some shell script examples, it is needed to invoke the miner executive:

    ```shell
    export PHOENIX_PATH=<path-to-phoenixminer-root>
    export NSF_PATH=<path-to-nsfxminer-root>
    ```

    and also the wallet and pool address:

    ```shell
    export ETH_WALLET=<your-ethereum-wallet-address> # 0x
    export ETH_POOL=<your-favorite-pool> # ex. asia1.ethermine.org:4444
    ```

* Installation from PyPI

    Setup Python vitual environment:

    ```shell
    cd gpuctl
    python3 -m venv venv
    source ./venv/bin/activate
    ```

    ```shell
    pip insall gpuctl
    ```

* Installation from source

    ```shell
    git clone https://github.com/Ed-Yang/gpuctl
    ```

    Setup Python vitual environment:

    ```shell
    cd gpuctl
    python3 -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt
    ```

    Install gpuctl:

    ```shell
    pip install .
    ```

    After completed the above procedure, before you run the gpuctl, you only need to to run:

    ```shell
    source ./venv/bin/activate
    ```

## Interaction with miners

For the the under rate detection feature, it need to retreive the current hashrate of miner through the network management API
of miner.

The following exapmple setup a netowrk management port on TCP port 3333.

* ethminer/nsfminer, additional parameters:

    --HWMON 2 --api-port -3333  
    or  
    --HWMON 2 --api-bind 127.0.0.1:3333  

* Phoenixminer, additional parameters ([check section 3](https://bitcointalk.org/index.php?topic=2647654.0)):

    -cdm 2 -cdmport 3333  

To test if the miner's network management function is correctly enabled:

    ```shell
    ./scripts/get-rate.sh 3333
    ```

* Example of script for running PhonenixMiner and nsfminer

For utilizing the miner's script, it have to define:

    ```
    export PHOENIX_PATH=<path-to-phoenixminer-root>
    export NSF_PATH=<path-to-nsfxminer-root>

    export ETH_WALLET=<your-ethereum-wallet-address> # 0x
    export ETH_POOL=<your-favorite-pool> # ex. asia1.ethermine.org:4444
    ```

    pm-dev.sh <n>: start PhoenixMiner on device <n>, n is starting from zero
    pm-all.sh : start PhoenixMiner all GPU devices
    nsf-dev.sh <n>: start nsfminer on device <n>, n is starting from zero
    nsf-all.sh : start PhoenixMiner all GPU devices

## GpuCtl

Some parameters are applying to every GPU on whole system (like interval, curve, etc.),
if it is necessary to provide specific setting for a GPU, it is able to run seperate
gpuctl instance with expected parametets.

* Usage

    ```shell
    gpuctl --help
    ```

    ```shell
    usage: gpuctl [-h] [-l] [-s SLOTS] [-a] [-n] [--interval INTERVAL]
                [--wait WAIT] [--set-speed [0-100]] [-f FAN] [-d DELTA]
                [--curve CURVE] [--temp TEMP] [--tas TAS] [--scan] [-v] [-V]

    optional arguments:
    -h, --help            show this help message and exit
    -l, --list            list all GPU cards
    -s SLOTS, --slots SLOTS
                            use PCI slot name to locate GPU (ie.
                            0000:01:00.0/0000:01:00.1)
    -a, --amd             only use AMD GPU
    -n, --nvidia          only use Nvidia GPU
    --interval INTERVAL   monitoring interval
    --wait WAIT           seconds before report failure
    --set-speed [0-100]   set the fan speed (0~100)
    -f FAN, --fan FAN     if temperature is exceed than FAN once, activate fan
                            control (default:70)
    -d DELTA, --delta DELTA
                            set fan speed if temperature diff % is over DELTA
                            (defaut:2)
    --curve CURVE         set temp/fan-speed curve (ie. 0:0/10:10/80:100)
    --temp TEMP           over temperature action threshold
    --tas TAS             over temperature action script
    --scan                list miner through network inquiry
    -v, --verbose         show debug message
    -V, --version         show version info
    ```

* Slot Name

The slot name of each GPU card could be found by using "lspci -D" command.
In the following output, the slot name of AMD GPU card is "0000:01:00.0".

    ```shell
    lspci -D
    ```

    ```shell
    0000:01:00.0 VGA compatible controller....
    ```

* Action scripts

A few examples of action script are provided for reference, besides it is feasible to write a script to send syslog, email or telegram message, etc.

- scripts/gpu-failure.sh: shutdown system and schedule reboot
- scripts/restart.sh: restart miner
- scripts/reboot.sh: reboot rig

If a failure is detected, the gpuctl will invoke the given script with slot name as argument.


### Examples

* Example 1) List status of GPU cards 

    ```shell
    gpuctl --list
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR    Working
    -- ------------ -------- ----------- ----- ---- ------ -------
    1 0000:01:00.0 NVIDIA   [10DE:1C03]  54c  10%  73.63w True
    2 0000:0b:00.0 AMD      [1002:67DF]  61c  60%  80.00w True
    3 0000:0d:00.0 NVIDIA   [10DE:1C03]  47c   0%  76.18w True
    ```

    Retreive GPU's status through network management API:
    
    Note, if the miner is running as root priviledge, it must invoke with "sudo".

    ```shell
    sudo gpuctl --scan
    ```

    ```shell
    Miner : nsfminer-1.3.12+, tcp port: 3333, pid: 10208
    Uptime: 960s
    Rate(kh) Temp Fan  
    ======== ==== ==== 
    18800  58c  11%
    26939  60c  60%
    19933  48c   0%
    ```

* Example 2) Set the fan speed of all GPUs to 50%

    ```shell
    sudo gpuctl --set-speed 50
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR     Working
    -- ------------ -------- ----------- ----- ---- ------- -------
    1 0000:01:00.0  NVIDIA   [10DE:1C03]   61c  50%  74.76w True
    2 0000:0b:00.0  AMD      [1002:67DF]   78c  47%  81.00w True
    3 0000:0d:00.0  NVIDIA   [10DE:1C03]   49c  50%  72.60w True
    ```

* Example 3) If the temperature of a GPU is over 65c, activate the fan speed control for the specific GPU.

    ```shell
    sudo gpuctl --fan 65
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR     Working
    -- ------------ -------- ----------- ----- ---- ------- -------
    1 0000:01:00.0 NVIDIA   [10DE:1C03]   60c  50%  76.08w True
    2 0000:0b:00.0 AMD      [1002:67DF]   77c  80%  81.00w True
    3 0000:0d:00.0 NVIDIA   [10DE:1C03]   49c  50%  74.41w True


    gpuctl: started

    12:22:25 INFO     query intervel: 5 wait-time: 120
    12:22:25 INFO     temperature threshold: 85
    12:22:25 INFO     fan control threshold: 65
    12:22:25 INFO     script: None


    12:22:30 INFO     [0000:0b:00.0/AMD] current temp. 75c set speed 84%
    12:22:35 INFO     [0000:0b:00.0/AMD] current temp. 72c set speed 72%
    12:22:50 INFO     [0000:0b:00.0/AMD] current temp. 76c set speed 84%
    12:23:00 INFO     [0000:0b:00.0/AMD] current temp. 73c set speed 72%
    12:23:10 INFO     [0000:0b:00.0/AMD] current temp. 70c set speed 72%
    12:23:36 INFO     [0000:0b:00.0/AMD] current temp. 67c set speed 61%
    ```

* Example 4)  **nsfminer** If the temeprature of a GPU is over 75c for 10s, call action script "restart.sh" to restart miner

    Note, the Phoenix might not be corectly restared through network command, so this mechanism only suitable for nsfminer.

    T

    ```shell
    sudo gpuctl --temp 75 --wait 10 --tas ./scripts/restart.sh 
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR     Working
    -- ------------ -------- ----------- ----- ---- ------- -------
    1 0000:01:00.0 NVIDIA   [10DE:1C03]   52c  11%  73.90w True
    2 0000:0b:00.0 AMD      [1002:67DF]   56c  60%  80.00w True
    3 0000:0d:00.0 NVIDIA   [10DE:1C03]   46c   0%  75.48w True


    gpuctl: started

    12:49:00 INFO     query intervel: 5 wait-time: 10
    12:49:00 INFO     temperature threshold: 75
    12:49:00 INFO     fan control threshold: None
    12:49:00 INFO     script: ./scripts/restart.sh


    12:51:07 WARNING  [0000:0b:00.0/AMD] over temperature 75c, exec ./scripts/restart.sh
    12:51:07 INFO     exec script ./scripts/restart.sh 0000:0b:00.0 no_wait False

    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR     Working
    -- ------------ -------- ----------- ----- ---- ------- -------
    1 0000:0b:00.0 AMD      [1002:67DF]   78c  60%  82.00w True
    ```

    In the nsfminer's terminal:

    ```shell
    12:51:07 miner API : Method miner_restart requested
    12:51:07 miner Restart miners...
    12:51:07 miner Shutting down miners...
    12:51:07 miner Spinning up miners...
    ```

* Example 5) For every GPU, if its temeprature is over 75c for 10s, call failure action script

    Note, invoking gpu-failure.sh will shutdown the system and schedulee to restart at 5 minutes later.

    ```shell
    sudo gpuctl --temp 75 --wait 10 --tas ./scripts/gpu-failure.sh 
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR     Working
    -- ------------ -------- ----------- ----- ---- ------- -------
    1 0000:01:00.0 NVIDIA   [10DE:1C03]   56c  11%  75.99w True
    2 0000:0b:00.0 AMD      [1002:67DF]   61c  60%  81.00w True
    3 0000:0d:00.0 NVIDIA   [10DE:1C03]   48c   0%  75.49w True


    gpuctl: started

    13:11:17 INFO     query intervel: 5 wait-time: 10
    13:11:17 INFO     temperature threshold: 75
    13:11:17 INFO     fan control threshold: None
    13:11:17 INFO     script: ./scripts/gpu-failure.sh


    13:12:23 WARNING  [0000:0b:00.0/AMD] over temperature 75c, exec ./scripts/gpu-failure.sh
    13:12:23 INFO     exec script ./scripts/gpu-failure.sh 0000:0b:00.0 no_wait False
    ```

## EthCtl

* Usage

    ```shell
    ethctl --help
    ```

    ```shell
    usage: ethctl [-h] [-l] [-b BASE] [--interval INTERVAL] [-w WAIT] [-t TEMP]
                [-r RATE] [--rmode RMODE] [-d DELAY] [-s SCRIPT] [-v] [-V]

    optional arguments:
    -h, --help            show this help message and exit
    -l, --list            list all miners
    -b BASE, --base BASE  tcp port offset, ie. device N is listened on base + N
    --interval INTERVAL   monitoring interval
    -w WAIT, --wait WAIT  count down interval
    -t TEMP, --temp TEMP  over temperature action threshold
    -r RATE, --rate RATE  under rate threshold (default: 2000 kh)
    --rmode RMODE         failure restart, 0: none, 1: net restart, 2: kill
    -d DELAY, --delay DELAY
                            delay before calling the action script
    -s SCRIPT, --script SCRIPT
                            calling to script on failure
    -v, --verbose         show debug message
    -V, --version         show version info
    ```

### Examples

* Example 1) List all miner with network management function enabled

    ```shell
    ethctl --list
    ```

    ```shell
    Miner : nsfminer-1.3.12+, tcp port: 3333, pid: 19526
    Uptime: 92100s
    Rate(kh) Temp Fan  
    ======== ==== ==== 
       18794  58c  50%
       26624  62c  47%
       19898  47c  50%
    ```

* Example 2) **PhoenixMiner** if the highest of temeprature of miner's GPU(s) is over 75c, 
or the lowest hashrate under 2 Mh/s call for 120s, 
kill the miner's process and call action script to restart miner

Use PhoenixMiner 5.3b as example:

    Start miner:

    ```shell
    ./scripts/pm-all.sh
    ```

    Open a new terminal and run:

    ```shell
    ethctl -t 75 -r 2000 --rmode 2 -d 120 -s ./scripts/pm-all.sh
    ```

    ```shell
    Miner : 'PM 5.3b'   
    Uptime: 0s
    Rate(kh) Temp Fan  
    ======== ==== ==== 
           0  48c  48%


    ethctl: started

    23:29:52 INFO     query intervel: 5 wait-time: 120
    23:29:52 INFO     temperature: 75c hashrate: 2000 kh/s
    23:29:52 INFO     restart mode: 2 script: ./scripts/pm-all.sh


    23:30:43 INFO     add miner 'PM 5.3b - ETH':3333 pid 27381
    23:33:20 WARNING  'PM 5.3b - ETH':3333 dev 0 rate 0 under threshold
    23:33:20 WARNING  'PM 5.3b - ETH':3333 dev 0 temp [72] rate [0]
    23:33:20 INFO     'PM 5.3b - ETH':3333 dev 0 restarting pid 27381 mode 2 
    23:33:20 INFO     'PM 5.3b - ETH':3333 miner removed
    23:33:20 INFO     'PM 5.3b - ETH':3333 delay 120 exec ./scripts/pm-all.sh 0 3333 72 0
    ```

* Example 3) **nsfminer** if the highest of temeprature of miner's GPU(s) is over 75c, 
or the lowest hashrate under 2 Mh/s call for 60s, 
restart the miner's process

Use PhoenixMiner 5.3b as example:

    Start miner:

    ```shell
    ./scripts/nsf-dev.sh 1
    ```

    Open a new terminal and run:

    ```shell
    ethctl -t 75 -r 2000 --rmode 2 -w 30 --delay 120 -s ./scripts/nsf-all.sh
    ```

    ```shell
    Miner : 'PM 5.3b'   
    Uptime: 0s
    Rate(kh) Temp Fan  
    ======== ==== ==== 
        0  48c  48%


    ethctl: started

    23:29:52 INFO     query intervel: 5 wait-time: 120
    23:29:52 INFO     temperature: 75c hashrate: 2000 kh/s
    23:29:52 INFO     restart mode: 2 script: ./scripts/pm-all.sh


    23:30:43 INFO     add miner 'PM 5.3b - ETH':3333 pid 27381
    23:33:20 WARNING  'PM 5.3b - ETH':3333 dev 0 rate 0 under threshold
    23:33:20 WARNING  'PM 5.3b - ETH':3333 dev 0 temp [72] rate [0]
    23:33:20 INFO     'PM 5.3b - ETH':3333 dev 0 restarting pid 27381 mode 2 
    23:33:20 INFO     'PM 5.3b - ETH':3333 miner removed
    23:33:20 INFO     'PM 5.3b - ETH':3333 delay 120 exec ./scripts/pm-all.sh 0 3333 72 0
    ```

* Run Test Cause

    ```shell
    python3 -m unittest discover tests
    ```

## Diagnostics

* Monitor AMD GPU card

    ```shell
    # HiveOS
    sudo watch -c -n 2 amd-info
    ```

* Monitor Nvidia GPU card

    ```shell
    # HiveOS
    sudo watch -c -n 2 nvidia-info
    ```

    or

    ```shell
    sudo watch -c -n 2 nvidia-smi
    ```

## Q/A

* nvidia Unable to init server: Could not connect: Connection refused

    In ~/.profile and/or ~/.bashrc, add:

    ```shell
    export DISPLAY=:0
    export XAUTHORITY=/var/run/lightdm/root/:0
    ```

* (nvidia-settings:15781): dbind-WARNING **: 04:46:56.622....

    In ~/.profile and/or ~/.bashrc, add:

    ```shell
    export NO_AT_BRIDGE=1
    ```

## Reference

* [Fan controller for amdgpus](https://github.com/chestm007/amdgpu-fan.git)
* [Ethminer's API](https://github.com/ethereum-mining/ethminer/blob/master/docs/API_DOCUMENTATION.md#list-of-requests)
* [GPUFan](https://github.com/milani/gpufan)
* [PyOpenCL Samples](https://github.com/virus-warnning/pyopencl_samples)
* [Associating OpenCL device ids with GPUs](https://anteru.net/blog/2014/associating-opencl-device-ids-with-gpus/)
