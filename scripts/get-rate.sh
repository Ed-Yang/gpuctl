#!/bin/bash

PORT=$1

DATA=$(echo '{"method": "miner_getstat1", "jsonrpc": "2.0", "id": 0 }' | nc -w 2 localhost 3333)
echo "$DATA" | sed 's/.*\[\([^]]*\)\].*/\1/g' | awk '{split($0,a,","); print a[4]}' | tr -d '"'

