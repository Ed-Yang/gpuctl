#!/bin/bash

BASE_PORT=3333

DEV=$(($1))
PORT=$(($1 + BASE_PORT))


./nsfminer/build/nsfminer/nsfminer --devices $DEV -P stratum1+tcp://0xf6Daa81109Dc170e4145D8661c3f50A1E32D348b.nsf-dev@us1.ethermine.org:4444 --HWMON 2 --api-port $PORT

