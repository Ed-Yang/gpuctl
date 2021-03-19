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

* Environment variables

    For configuring Nvidia's GPU, it is needed to set the following environment.

    ```shell
    export DISPLAY=:0
    export XAUTHORITY=/var/run/lightdm/root/:0
    export NO_AT_BRIDGE=1
    ```

* Clone the source

    ```shell
    https://github.com/Ed-Yang/gpuctl
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

    After completed the above procedure, before you run the gpuctl, you need to to run only:

    ```shell
    source ./venv/bin/activate
    ```

### Usage

Some parameters are applying to every GPU on ststem (like interval, curve, etc.),
if it is necessary to provide specific setting for a GPU, it is able to run seperate
gpuctl instance with expected parametets.

    ```shell
    usage: gpuctl [-h] [-l] [-s SLOTS] [-a] [-n] [--interval INTERVAL] [-f FAN]
                [-d DELTA] [--temp TEMP] [--temp-cdown TEMP_CDOWN] [--tas TAS]
                [--rms RMS] [--rate RATE] [--rate-cdown RATE_CDOWN] [--ras RAS]
                [--curve CURVE] [-v]

    optional arguments:
    -h, --help            show this help message and exit
    -l, --list            list all GPU cards
    -s SLOTS, --slots SLOTS
                            use PCI slot name to locate GPU (ie.
                            0000:01:00.0/0000:01:00.1)
    -a, --amd             only use AMD GPU
    -n, --nvidia          only use Nvidia GPU
    --interval INTERVAL   monitoring interval
    -f FAN, --fan FAN     if temperature is exceed than FAN once, activate fan
                            control (default:70)
    -d DELTA, --delta DELTA
                            set fan speed if temperature diff % is over DELTA
                            (defaut:2)
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

    --api-bind 127.0.0.1:3333 or
    --api-port -3333 

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
    ID Slot Name    Vendor   PCI-ID
    -- ------------ -------- -----------
    1 0000:01:00.0 AMD      [1002:67DF]
    ```

* Example 2) For all of the GPUs, if its temperature is over 30c, then activate the fan speed control.

    ```shell
    sudo gpuctl --fan 30
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID
    -- ------------ -------- -----------
    1 0000:01:00.0 AMD      [1002:67DF]

    gpuctl: started

    12:02:20 INFO     [0000:01:00.0/AMD] current temp. 57c set speed 52%
    12:03:39 INFO     [0000:01:00.0/AMD] current temp. 60c set speed 61%
    ```

* Example 3) For every GPU, if its temeprature is over 50c, then activate fan control and if its temeprature is 55c for 5s, call restart script

    ```shell
    sudo gpuctl --fan 50 --temp 55 --tas ./scripts/restart.sh --temp-cdown 5
    ```

    ```shell
    ID Slot Name    Vendor   PCI-ID
    -- ------------ -------- -----------
    1 0000:01:00.0 AMD      [1002:67DF]

    gpuctl: started

    03:50:36 INFO     [0000:01:00.0/AMD] current temp. 58c set speed 52%
    03:50:36 WARNING  [0000:01:00.0/AMD] temp: 58c/55c CD: 5
    03:50:37 WARNING  [0000:01:00.0/AMD] temp: 58c/55c CD: 4
    03:50:38 WARNING  [0000:01:00.0/AMD] temp: 59c/55c CD: 3
    03:50:39 WARNING  [0000:01:00.0/AMD] temp: 58c/55c CD: 2
    03:50:40 WARNING  [0000:01:00.0/AMD] temp: 59c/55c CD: 1
    03:50:41 INFO     [0000:01:00.0/AMD] over heat, exec script ./scripts/restart.sh
    03:50:41 INFO     [0000:01:00.0/AMD] result: send restart command to slot=0000:01:00.0, port=3333
    {"id":5,"jsonrpc":"2.0","result":true}

    03:50:42 WARNING  [0000:01:00.0/AMD] temp: 56c/55c CD: 5
    03:50:43 WARNING  [0000:01:00.0/AMD] temp: 57c/55c CD: 4
    ```

* Example 4) For every GPU, if its temeprature is over 55c, or rate under 30000 Kh/s call restart script

Use ethminer as example:

    ```shell
    ethminer -G --api-port 3333 -P ....
    ```

    ```shell
    sudo gpuctl --temp 55 --tas ./scripts/restart.sh --rms ./scripts/rate.sh --rate 30000 --ras ./scripts/restart.sh
    ```

    ```shell
    03:45:38 WARNING  [0000:01:00.0/AMD] rate: 28564/30000 CD: 2
    03:45:39 WARNING  [0000:01:00.0/AMD] temp: 60c/55c CD: 1
    03:45:39 INFO     [0000:01:00.0/AMD] over heat, exec script ./scripts/restart.sh
    03:45:39 INFO     [0000:01:00.0/AMD] result: send restart command to slot=0000:01:00.0, port=3333
    {"id":5,"jsonrpc":"2.0","result":true}

    03:45:40 WARNING  [0000:01:00.0/AMD] temp: 57c/55c CD: 120
    03:45:42 ERROR    0000:01:00.0/AMD] get hashrate, exec script ./scripts/rate.sh failed !!
    ```

If the miner is rebooting, it might not be able to retrieve the hash rate for a few seconds.

* Run Test Cause

    ```shell
    python3 -m unittest discover tests
    ```

## Diagnostics

* Monitor AMD GPU card

    ```shell
    sudo watch -c -n 2 amd-info
    ```

* Monitor Nvidia GPU card

    ```shell
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
* [GPUFan](https://github.com/milani/gpufan)
* [PyOpenCL Samples](https://github.com/virus-warnning/pyopencl_samples)
* [Associating OpenCL device ids with GPUs](https://anteru.net/blog/2014/associating-opencl-device-ids-with-gpus/)
