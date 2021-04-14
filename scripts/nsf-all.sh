#!/bin/bash

PORT=3333

sudo gpuctl --set-speed 50
$NSF_PATH/nsfminer -P stratum1+tcp://0xf6Daa81109Dc170e4145D8661c3f50A1E32D348b.nsf-all@us1.ethermine.org:4444 --HWMON 2 --api-port $PORT

