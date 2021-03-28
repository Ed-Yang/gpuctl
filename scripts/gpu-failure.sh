#!/bin/bash

# disable alarm
sh -c "echo 0 > /sys/class/rtc/rtc0/wakealarm" 

# wakeup after 5 minutes
sh -c "echo `date '+%s' -d '+ 5 minutes'` > /sys/class/rtc/rtc0/wakealarm"

# halh system and wait boot
shutdown now

