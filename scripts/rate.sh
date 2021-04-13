#!/bin/bash

PORT="3333"
SLOT=""

if [[ $# -ne 0 ]] ; then
    SLOT=$1
fi

# multiple GPUs: fill in the corrosponding ports for each card
if [[ $# -ne 0 ]] ; then
    case $1 in
        0000:01:00.0)
            PORT="3333"
            ;;
        *)
            PORT="3333"
            ;;
    esac
fi

if [[ "$PORT" != "0" ]] ; then
    DATA=$(echo '{"method": "miner_getstat1", "jsonrpc": "2.0", "id": 0 }' | nc -w 2 localhost 3333)
    echo "$DATA" | sed 's/.*\[\([^]]*\)\].*/\1/g' | awk '{split($0,a,","); print a[4]}' | tr -d '"'
else
    echo -e "slot $1: remote port is not configured !!!\n" 
    exit 1
fi

