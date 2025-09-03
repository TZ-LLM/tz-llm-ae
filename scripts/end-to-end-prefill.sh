#!/bin/bash

SCRIPT_DIR=$(realpath $(dirname $0))

while true; do
    timeout 20 hdc file send $SCRIPT_DIR/mem-stress.sh /data/local/tmp/rknpu/mem-stress.sh || continue
    break
done

for sys in base tz strawman; do
    for stress in s; do
        for cache in 0; do
            for model in llama; do
                for prompt in $(seq 5 9); do
                    $SCRIPT_DIR/run-mem-retry.sh $sys $stress $cache $prompt $model 1
                done
                for prompt in $(seq 15 17); do
                    $SCRIPT_DIR/run-mem-retry.sh $sys $stress $cache $prompt $model 1
                done
            done
        done
    done
done
