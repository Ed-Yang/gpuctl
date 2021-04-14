# GPU Monitoring and Failure Notification/Recovery

[![CircleCI](https://circleci.com/gh/Ed-Yang/gpuctl.svg?style=svg)](https://circleci.com/gh/Ed-Yang/gpuctl)

While in minging crytocurrency with GPU, although the GPU has built-in thermal control,
but it might not be fitted in some environment and cause hash rate decreases or even GPU
faults.  This project provides a tool to:

- According the detected temperature to change fan speed
- Execute custom action scripts while current temperature of GPU(s) is over a defined threshold
- Execute custom action scripts while current hash rate of GPU(s) is under a defined threshold

Currently, the example of action script are based on the [miner's remote managemen API](https://github.com/ethereum-mining/ethminer/blob/master/docs/API_DOCUMENTATION.md), for different miner, it might be needed to custimize locally.


## Environment and Installation

Intel CPU/16G RAM
Ubuntu 18.4/Python3

* Environment setup

    For configuring Nvidia's GPU, it is needed to set the following environment.

    ```shell
    export DISPLAY=:0
    export XAUTHORITY=/var/run/lightdm/root/:0
    export NO_AT_BRIDGE=1
    ```

    In some shell script, it is needed to invoke the miner executive:

    ```shell
    export PHOENIX_PATH=<path-to-phoenixminer-root>
    export NSF_PATH=<path-to-nsfxminer-root>
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

To utilize the the under rate detection feature, the miner's must provide a way
to retreive its current hash rate.  Some miner's implement the network management
function, it could be easily enabled to make it accessable by others.

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

## GpuCtl

Some parameters are applying to every GPU on whole system (like interval, curve, etc.),
if it is necessary to provide specific setting for a GPU, it is able to run seperate
gpuctl instance with expected parametets.

* Usage

    ```shell
    usage: gpuctl [-h] [-l] [-s SLOTS] [-a] [-n] [--interval INTERVAL]
              [--wait WAIT] [--set-speed [0-100]] [-f FAN] [-d DELTA]
              [--curve CURVE] [--temp TEMP] [--tas TAS] [--scan] [-v]

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
    ```

* Action scripts

A few examples of action script are provided for reference, besides it is feasible to write a script to send syslog, email or telegram message, etc.

- scripts/gpu-failure.sh: shutdown system and schedule reboot
- scripts/restart.sh: restart miner
- scripts/reboot.sh: reboot rig

If a failure is detected, the gpuctl will invoke the given script with slot name as argument.

Take the 'nsfminer' as example, if we want to implement while error is detected, the gpuctl will inform 'nsfminer' program
to restart itself, we should fill in the correct mapping for slot to TCP port number which the nsfminer listened to.

    ```shell
    if [[ $# -ne 0 ]] ; then
        case $1 in
            0000:01:00.0)
            #     PORT="3335"
            #     ;;
            *)
                PORT="3333"
                ;;
        esac
    fi
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

### Examples

* Example 1) List on board GPU cards 

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

* Example 2) For all of the GPUs, if its temperature is over 50c, then activate the fan speed control.

    ```shell
    sudo gpuctl --fan 50
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR    Working
    -- ------------ -------- ----------- ----- ---- ------ -------
    1 0000:01:00.0 NVIDIA   [10DE:1C03]  57c  30%  73.29w True
    2 0000:0b:00.0 AMD      [1002:67DF]  80c  27%  81.00w True
    3 0000:0d:00.0 NVIDIA   [10DE:1C03]  49c  30%  74.90w True

    gpuctl: started

    02:01:17 INFO     [0000:01:00.0/NV ] current temp. 57c set speed 52%
    02:01:18 INFO     [0000:0b:00.0/AMD] current temp. 80c set speed 100%
    02:01:19 INFO     [0000:0d:00.0/NV ] current temp. 49c set speed 0%
    ```

* Example 3) For every GPU, if its temeprature is over 50c, then activate fan control and if its temeprature is over 85c for 30s, call failure action script

    Note, invoking gpu-failure.sh will shutdown the system and schedulee to restart at 5 minutes later.

    ```shell
    sudo gpuctl --fan 50 --temp 85 --tas ./scripts/gpu-failure.sh --wait 30
    ```

* Example 4)  **nsfminer** If the temeprature of a GPU is over 60c, call action script "restart.sh" to restart miner

    Note, the Phoenix might not be corectly restared through network command, so this mechanism only suitable for nsfminer.

    ```shell
    gpuctl --temp 60 --tas ./scripts/restart.sh
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR     Working
    -- ------------ -------- ----------- ----- ---- ------- -------
    1 0000:01:00.0 AMD      [1002:67DF]   76c  47% 129.00w True

    gpuctl: started

    20:21:02 WARNING  [0000:01:00.0/AMD] over temperature 60c, exec ./scripts/restart.sh
    20:21:04 WARNING  [0000:01:00.0/AMD] result: {"id":5,"jsonrpc":"2.0","result":true}
    ```

## EthCtl

* Usage

    ```shell
    usage: ethctl [-h] [-l] [-b BASE] [--interval INTERVAL] [-w WAIT] [-t TEMP]
                [-r RATE] [--rmode RMODE] [-s SCRIPT] [-v]

    optional arguments:
    -h, --help            show this help message and exit
    -l, --list            list all miners
    -b BASE, --base BASE  tcp port offset, ie. device N is listened on base + N
    --interval INTERVAL   monitoring interval
    -w WAIT, --wait WAIT  count down interval
    -t TEMP, --temp TEMP  over temperature action threshold
    -r RATE, --rate RATE  under rate threshold (default: 1000 kh)
    --rmode RMODE         failure restart, 0: none, 1: net restart, 2: kill
    -s SCRIPT, --script SCRIPT
                            calling to script on failure
    -v, --verbose         show debug message
    ```

### Examples

* Example 1) List all miner with network management function enabled

    ```shell
    ethctl --list
    ```

    ```shell
    Miner : 'PM 5.3b - ETH'
    Uptime: 214980s
    Rate(kh) Temp Fan  
    ======== ==== ==== 
    24869    74c  48%
    ```

* Example 2) **PhoenixMiner** if the highest of temeprature of miner's GPU(s) is over 75c, 
or the lowest hashrate under 2 Mh/s call for 60s, 
kill the miner's process and call action script to restart miner

Use PhoenixMiner 5.3b as example:

    Start miner:

    ```shell
    ./scripts/pm-all.sh
    ```

    Open a new terminal and run:

    ```shell
    ethctl -t 75 -r 2000 --rmode 2 -s ./scripts/pm-all.sh
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

## User mode

    For running gpuctl in user mode (optional):

    ```shell
    sudo adduser <user> video
    ```

    ```shell
    # display cards
    ls /sys/class/drm | grep "^card[[:digit:]]$"
    ```

    ```shell
    # fill in correct <card-n> and <hwmon-m>
    sudo chgrp video /sys/class/drm/<card-n>/device/hwmon/<hwmon-m>/pwm1_enable
    sudo chgrp video /sys/class/drm/<card-n>/device/hwmon/<hwmon-m>/pwm1
    sudo chmod g+w /sys/class/drm/<card-n>/device/hwmon/<hwmon-m>/pwm1_enable
    sudo chmod g+w /sys/class/drm/<card-n>/device/hwmon/<hwmon-m>/pwm1
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

    In ~/.profile, add:

    ```shell
    export DISPLAY=:0
    export XAUTHORITY=/var/run/lightdm/root/:0
    ```

* (nvidia-settings:15781): dbind-WARNING **: 04:46:56.622....

    In ~/.profile, add:

    ```shell
    export NO_AT_BRIDGE=1
    ```

## Reference

* [Fan controller for amdgpus](https://github.com/chestm007/amdgpu-fan.git)
* [Ethminer's API](https://github.com/ethereum-mining/ethminer/blob/master/docs/API_DOCUMENTATION.md#list-of-requests)
* [GPUFan](https://github.com/milani/gpufan)
* [PyOpenCL Samples](https://github.com/virus-warnning/pyopencl_samples)
* [Associating OpenCL device ids with GPUs](https://anteru.net/blog/2014/associating-opencl-device-ids-with-gpus/)
