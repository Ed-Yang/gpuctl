#!/bin/bash

PORT=3333

sudo gpuctl --set-speed 50
$PHOENIX_PATH/PhoenixMiner -pool asia1.ethermine.org:4444 -wal 0xf6Daa81109Dc170e4145D8661c3f50A1E32D348b -worker pm-all -mode 1 -log 0 -ftime 55 -retrydelay 1 -tt 79 -tstop 89  -coin eth -rate 0 -cdm 2 -cdmport $PORT
