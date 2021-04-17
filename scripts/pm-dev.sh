#!/bin/bash

BASE_PORT=3333

DEV=$(($1 + 1))
PORT=$(($1 + BASE_PORT))

# ETH_WALLET=
# ETH_POOL=asia1.ethermine.org:4444

ETH_WORKER="pm-dev-$1"

$PHOENIX_PATH/PhoenixMiner -gpus $DEV -rmode 0 -pool ${ETH_POOL} -wal ${ETH_WALLET} -worker ${ETH_WORKER} -mode 1 -log 0 -ftime 55 -retrydelay 1 -tt 79 -tstop 89  -coin eth -rate 0 -cdm 2 -cdmport $PORT
