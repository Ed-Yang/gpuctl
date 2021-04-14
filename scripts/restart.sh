#!/bin/bash

PORT="0"
SLOT=""

if [[ $# -ne 0 ]] ; then
    SLOT=$1
fi

# multiple GPUs: fill in the corrosponding ports for each card
if [[ $# -ne 0 ]] ; then
    case $1 in
        # 0000:01:00.0)
        #     PORT="3335"
        #     ;;
        *)
            PORT="3333"
            ;;
    esac
fi

if [[ "$PORT" != "0" ]] ; then
    # printf 'send restart command to slot=%s, port=%s\n' $SLOT $PORT
    echo '{"method": "miner_restart", "jsonrpc": "2.0", "id": 5 }' | nc -w 2 localhost "$PORT"
else
    echo -e "slot $1: remote port is not configured !!!\n" 
fi
