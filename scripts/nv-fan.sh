#!/bin/bash

# get fan speed of NV card. starting from 0

# export NO_AT_BRIDGE=1 (need to be defined in .bashrc or .profile)
nvidia-settings -t -q  [fan:$1]/GPUTargetFanSpeed
