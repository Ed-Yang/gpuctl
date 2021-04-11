# GPU Monitoring and Failure Notification

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

* Clone the source

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

### Usage

Some parameters are applying to every GPU on whole system (like interval, curve, etc.),
if it is necessary to provide specific setting for a GPU, it is able to run seperate
gpuctl instance with expected parametets.

    ```shell
    usage: gpuctl [-h] [-l] [-s SLOTS] [-a] [-n] [--interval INTERVAL]
                [--set-speed [0-100]] [-f FAN] [-d DELTA] [--las LAS]
                [--temp TEMP] [--temp-cdown TEMP_CDOWN] [--tas TAS] [--rms RMS]
                [--rate RATE] [--rate-cdown RATE_CDOWN] [--ras RAS]
                [--curve CURVE] [--scan] [-v]

    optional arguments:
    -h, --help            show this help message and exit
    -l, --list            list all GPU cards
    -s SLOTS, --slots SLOTS
                            use PCI slot name to locate GPU (ie.
                            0000:01:00.0/0000:01:00.1)
    -a, --amd             only use AMD GPU
    -n, --nvidia          only use Nvidia GPU
    --interval INTERVAL   monitoring interval
    --set-speed [0-100]   set the fan speed (0~100)
    -f FAN, --fan FAN     if temperature is exceed than FAN once, activate fan
                            control (default:70)
    -d DELTA, --delta DELTA
                            set fan speed if temperature diff % is over DELTA
                            (defaut:2)
    --las LAS             gpu lost action script
    --temp TEMP           over temperature action threshold
    --temp-cdown TEMP_CDOWN
                            over temperature count down
    --tas TAS             over temperature action script
    --rms RMS             rate monitoring script
    --rate RATE           under rate threshold (default: 1000 kh)
    --rate-cdown RATE_CDOWN
                            under rate count down
    --ras RAS             under rate action script
    --curve CURVE         set temp/fan-speed curve (ie. 0:0/10:10/80:100)
    --scan                scan miner's info through network management api
    -v, --verbose         show debug message
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

- scripts/rate.sh: get miner's current hashrate
- scripts/restart.sh: restart miner
- scripts/reboot.sh: reboot rig


If a failure is detected (over heat or under rate), the gpuctl will invoke the given script with slot name as argument.

Take the 'ethminer' as example, if we want to implement while error is detected, the gpuctl will inform 'ethminer' program
to restart itself, we should fill in the correct mapping for slot to TCP port number which the ethminer listened to.

    ```shell
    if [[ $# -ne 0 ]] ; then
        case $1 in
            # 0000:01:00.0)
            #     PORT="3335"
            #     ;;
            *)
                PORT="3333"
                ;;
        esac
    fi
    ```

### Interaction with miners

To utilize the the under rate detection feature, the miner's must provide a way
to retreive its current hash rate.  Some miner's implement the network management
function, it could be easily enabled to make it accessable by others.

The following exapmple setup a netowrk management port on TCP port 3333.

* Ethminer/nsfminer, additional parameters:

    --HWMON 2 --api-bind 127.0.0.1:3333 or
    --HWMON 2 --api-port -3333 

* Phoenixminer, additional parameters ([check section 3](https://bitcointalk.org/index.php?topic=2647654.0)):

    -cdm 2 -cdmport 3333

    If miner's network management function is enabled, it could be tested by:

* Sample Scripts

Get hash rate:

    ```shell
    ./scripts/rate.sh
    ```

Restart miner:
    
    ```shell
    ./scripts/restart.sh
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

* Example 2) For all of the GPUs, if its temperature is over 30c, then activate the fan speed control.

    ```shell
    sudo gpuctl --fan 30
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR    Working
    -- ------------ -------- ----------- ----- ---- ------ -------
    1 0000:01:00.0 NVIDIA   [10DE:1C03]  54c  60%  73.72w True
    2 0000:0b:00.0 AMD      [1002:67DF]  61c  60%  80.00w True
    3 0000:0d:00.0 NVIDIA   [10DE:1C03]  47c  60%  75.49w True

    gpuctl: started

    02:11:53 INFO     [0000:01:00.0/NV ] current temp. 54c set speed 10%
    02:11:55 INFO     [0000:0b:00.0/AMD] current temp. 61c set speed 61%
    02:11:56 INFO     [0000:0d:00.0/NV ] current temp. 47c set speed 0%
    ```

* Example 3) For every GPU, if its temeprature is over 50c, then activate fan control and if its temeprature is 55c for 5s, call restart script

    ```shell
    sudo gpuctl --fan 50 --temp 55 --tas ./scripts/restart.sh --temp-cdown 5
    ```

* Example 4) For every GPU, if its temeprature is over 55c, or rate under 30000 Kh/s call restart script

Use ethminer as example:

    ```shell
    ethminer -G --HWMON 2 --api-port 3333 -P ....
    ```

    ```shell
    sudo gpuctl --temp 55 --tas ./scripts/restart.sh --rms ./scripts/rate.sh --rate 30000 --ras ./scripts/restart.sh
    ```


If the miner is rebooting, it might not be able to retrieve the hash rate for a few seconds.

* Example 5) Set all of the GPU's fan speed to 50%

    ```shell
    sudo gpuctl --set-speed 50
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID      Temp. Fan  PWR    Working
    -- ------------ -------- ----------- ----- ---- ------ -------
    1 0000:01:00.0 NVIDIA   [10DE:1C03]  54c  50%  73.74w True
    2 0000:0b:00.0 AMD      [1002:67DF]  61c  47%  80.00w True
    3 0000:0d:00.0 NVIDIA   [10DE:1C03]  47c  50%  73.87w True
    ```

* Example 6) If one of GPU(s) failed, halt system and schedule wakeup

    ```shell
    sudo gpuctl --las ./scripts/gpu-failure.sh -v
    ```

* Example 7) Get miner's info through network management API

    If the miner is running in user mode, it can execute the script command without "sudo".

    Note, miner might not report correct current fan speed.

    ```shell
    sudo gpuctl --scan
    ```

    ```shell
    Miner : nsfminer-1.3.9-8+commit.4b250d6b.dirty
    Uptime: 1080s
    Rate(kh) Temp Fan  
    ======== ==== ==== 
    19143  68c   0%
    Miner : nsfminer-1.3.9-8+commit.4b250d6b.dirty
    Uptime: 1080s
    Rate(kh) Temp Fan  
    ======== ==== ==== 
    28340  66c  47%
    Miner : nsfminer-1.3.9-8+commit.4b250d6b.dirty
    Uptime: 1020s
    Rate(kh) Temp Fan  
    ======== ==== ==== 
    19963  48c   0%
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
