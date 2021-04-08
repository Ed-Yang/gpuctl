# Notes

## PCI


    ```shell
    lspci -D  | awk '/AMD|Nvidia/{print $0}'
    ```

    ```shell
    cat  /sys/bus/pci/devices/0000:00:01.0/vendor
    ```

* GPU

    Vendor | GPU | PCI-ID | Comment
    |---|---|---|---|
    |AMD | RX580 |1002:aaf0| |
    | NVIDIA | GeForce GTX 1060 6GB| 10de:1c03 ||

## AMD

* List AMD cards

    ```shell
    ls /sys/class/drm | grep "^card[[:digit:]]$"
    ```

* Get current temperature:

    ```shell
    cat /sys/class/drm/card1/device/hwmon/temp1_input
    ```

    ```shell
    cat /sys/class/drm/card1/device/uevent
    ```

* Change fan speed

    pwm1_enable: 0-max, 1-manual, 2-auto (boot up default)


    pwn1: 32/10%, 135/50%, 255/100%

    ```shell
    echo '1' | sudo tee /sys/class/drm/card1/device/hwmon/hwmon2/pwm1_enable
    echo '32' | sudo tee /sys/class/drm/card1/device/hwmon/hwmon2/pwm1
    ```

## Nvidia

~/.profile:

```shell
export DISPLAY=:0
export XAUTHORITY=/var/run/lightdm/root/:0
```

In /etc/X11/xorg.conf, add AllowEmptyInitialConfiguration:

```shell
Section "Device"
    Driver          "nvidia"
    Option          "AllowEmptyInitialConfiguration" "true"
```

Get fan speed:

```shell
nvidia-settings -t -q  [fan:0]/GPUTargetFanSpeed
```

Set fan speed:

```shell
nvidia-settings -c :0 -a [gpu:0]/GPUFanControlState=1 -a [fan:0]/GPUTargetFanSpeed=0
```


```shell
sudo watch -c -n 2 nvidia-info
```

## Remote manaagement

* List miner

    ```shell
    lsof -i -P -n | grep -E 'miner|Phoenix' | grep LISTEN
    ```

* Get statistics

    ```shell
    echo '{"method": "miner_getstat1", "jsonrpc": "2.0", "id": 0 }' | nc -w 2 localhost 3333
    ```

    Output:

    ```shell
    {"id":0,"jsonrpc":"2.0","result":["nsfminer-1.3.8","0","21129;0;0","21129","0;0;0","off","0;0","us1.ethermine.org:4444","0;0;0;0"]}
    ```

* Get detail statistics

    One GPU:

    ```shell
    echo '{"method": "miner_getstatdetail", "jsonrpc": "2.0", "id": 0 }' | nc -w 2 localhost 3333
    ```

    Two GPUs:

    "42080;1;0"   : ETH hashrate in KH/s, submitted shares, rejected shares  
    "28596;13484" : Detailed ETH hashrate in KH/s per GPU  

    ```shell
    {"id":0,"jsonrpc":"2.0","result":["nsfminer-1.3.8","1","42080;1;0","28596;13484","0;0;0","off;off","55;60;46;0","us1.ethermine.org:4444","0;0;0;0"]}
    ```

* Restart miner

    ```shell
    echo '{"method": "miner_restart", "jsonrpc": "2.0", "id": 5 }' | nc -w 2 localhost 3333
    ```

    Output:

    ```shell
    {"id":5,"jsonrpc":"2.0","result":true}
    ```

* Reboot rig

    The miner will try to invoke "reboot.sh" which in the same folder as the executable.

    ```shell
    echo '{"method": "miner_reboot", "jsonrpc": "2.0", "id": 5 }' | nc -w 2 localhost 3333
    ```

    Output:

    ```shell
    {"id":5,"jsonrpc":"2.0","result":true}
    ```

## pyopencl

* The DEVICE_TOPOLOGY_AMD is not supported, so cannot use opencl to get PCI info of AMD GPU.

## Terminology

* Graphics Core Next (GCN) is the codename for both a series of microarchitectures as well as for an instruction set architecture that was developed by AMD
* Video Coding Engine (VCE) is AMD's video encoding ASIC implementing the video codec H.264/MPEG-4 AVC. 
* TeamRedMiner (TRM)

## Reference

* [Tweaking your NVIDIA GPU via SSH using nvidia-settings](https://thebravestatistician.wordpress.com/2017/08/13/tweaking-your-nvidia-gpu-via-ssh-using-nvidia-settings/)

