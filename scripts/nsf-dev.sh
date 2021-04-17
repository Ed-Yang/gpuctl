#!/bin/bash

BASE_PORT=3333

DEV=$(($1))
PORT=$(($1 + BASE_PORT))

# ETH_WALLET=
# ETH_POOL=asia1.ethermine.org:4444

ETH_WORKER="nsf-dev-${DEV}"
ETH_URL="${ETH_WALLET}.${ETH_WORKER}"

$NSF_PATH/nsfminer --devices $DEV -P stratum1+tcp://${ETH_URL}@${ETH_POOL} --HWMON 2 --api-port $PORT

