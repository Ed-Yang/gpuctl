#!/bin/bash

# disable alarm
sh -c "echo 0 > /sys/class/rtc/rtc0/wakealarm" 

# wakeup after 5 minutes
sh -c "echo `date '+%s' -d '+ 5 minutes'` > /sys/class/rtc/rtc0/wakealarm"

logger "gpuctl: GPU $1 failure, halt and schedule wakeup in 5 minutes"

# halh system and wait boot
shutdown now

