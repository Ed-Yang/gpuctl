#!/bin/bash

PORT=3333

# ETH_WALLET=
# ETH_POOL=asia1.ethermine.org:4444

ETH_WORKER="pm-all"

$PHOENIX_PATH/PhoenixMiner -pool ${ETH_POOL} -wal ${ETH_WALLET} -worker ${ETH_WORKER} -mode 1 -log 0 -ftime 55 -retrydelay 1 -tt 79 -tstop 89  -coin eth -rate 0 -cdm 2 -cdmport $PORT
