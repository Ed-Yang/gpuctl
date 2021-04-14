#!/bin/bash

BASE_PORT=3333

DEV=$(($1 + 1))
PORT=$(($1 + BASE_PORT))

$PHOENIX_PATH/PhoenixMiner -gpus $DEV -rmode 0 -pool asia1.ethermine.org:4444 -wal 0xf6Daa81109Dc170e4145D8661c3f50A1E32D348b -worker pm-dev -mode 1 -log 0 -ftime 55 -retrydelay 1 -tt 79 -tstop 89  -coin eth -rate 0 -cdm 2 -cdmport $PORT
