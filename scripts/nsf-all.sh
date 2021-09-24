#!/bin/bash

PORT=3333

# ETH_WALLET=
# ETH_POOL=asia1.ethermine.org:4444

ETH_WORKER="nsf-all"
ETH_URL="${ETH_WALLET}.${ETH_WORKER}"
$NSF_PATH/nsfminer -P stratum1+tcp://${ETH_URL}@${ETH_POOL} --HWMON 2 --api-port $PORT --retry-max 0 --retry-delay 5

