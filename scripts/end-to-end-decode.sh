#!/bin/bash

SCRIPT_DIR=$(realpath $(dirname $0))

while true; do
    timeout 20 hdc file send $SCRIPT_DIR/mem-stress.sh /data/local/tmp/rknpu/mem-stress.sh || continue
    break
done

for sys in tz base strawman; do
    for stress in s; do
        for cache in 5; do
            for model in qwen llama; do
                $SCRIPT_DIR/run-mem-retry.sh $sys $stress $cache 128 $model 64
            done
        done
    done
done
