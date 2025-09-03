#!/bin/bash

SCRIPT_DIR=$(realpath $(dirname $0))
AE_ROOT=$(realpath $SCRIPT_DIR/../)

RESULTS_DIR=$AE_ROOT/results/
if [ "$1" = "strawman" ]; then
    MAX_RETRY_COUNT=40
else
    MAX_RETRY_COUNT=10
fi

hdc_timeout() {
    timeout 5 hdc "$@" 2>/dev/null
}

wait_connect() {
    while true; do
        connect=$(hdc_timeout shell "echo hello" 2>/dev/null || echo "timeout")
        # echo "connect: $connect"
        if [ "$connect" = "hello" ]; then
            return 0
        fi
        # echo "Retrying..."
        sleep 5
    done
}

# Check if output file already exists
args_str=$(printf "%s-" "$@")
args_str=${args_str%-}
output_file="$RESULTS_DIR/${args_str}.txt"

if [ -f "$output_file" ]; then
    echo "Output file $output_file already exists. Exiting."
    exit 0
fi


echo "AE root: $AE_ROOT"

# Outer cycle so we can restart from the beginning on timeout
while true; do
    # 1) Wait until device responds
    wait_connect

    # 2) Reboot device then wait again
    hdc_timeout shell reboot || continue
    echo "system reboot"
    echo "/data/local/tmp/rknpu/mem-stress.sh $@"
    wait_connect

    # 3) Prepare shm, start stress in background
    echo "clear measurement"
    hdc_timeout shell "mkdir -p /dev/shm/ && rm /dev/shm/current_measure" || continue
    hdc_timeout shell "chmod -R +x /data/local/tmp/rknpu/" || continue
    timeout 400 hdc shell \"/data/local/tmp/rknpu/mem-stress.sh $@\" &

    mkdir -p "$RESULTS_DIR"

    # 4) Wait for /dev/shm/current_measure with retry cap
    retry_count=0
    while true; do
        retry_count=$((retry_count + 1))
        # echo "Retrying... $retry_count"
        sleep 10
        if [ $retry_count -gt $MAX_RETRY_COUNT ]; then
            # echo "Exceeded retry count"
            break
        fi

        connect=$(hdc_timeout shell ls /dev/shm/current_measure 2>/dev/null || continue)
        if [ "$connect" = "/dev/shm/current_measure" ]; then
            break
        fi
    done
    if [ $retry_count -gt $MAX_RETRY_COUNT ]; then
        continue
    fi

    # 6) Pull the result and clean up
    while true; do
        timeout 20 hdc file recv /dev/shm/current_measure "$output_file" || continue
        break
    done

    break
done
