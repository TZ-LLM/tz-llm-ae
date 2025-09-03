#!/bin/bash

SCRIPT_DIR=$(realpath $(dirname $0))
RESULTS_DIR=$(realpath $SCRIPT_DIR/../results)

rm_and_print() {
    local file=$1
    echo "rm -rf $file"
    ls -la $file
    rm -rf $file
}

if [ "$1" = "all" ]; then
    rm_and_print $RESULTS_DIR/*
elif [ "$1" = "end" ]; then
    if [ -n "$2" ]; then
        if [ "$2" in "tz" "base" "strawman" ]; then
            rm_and_print $RESULTS_DIR/$2-s-0-*-llama-1.txt
            rm_and_print $RESULTS_DIR/$2-s-0-128-*-64.txt
        else
            echo "invalid setup $2"
            exit 1
        fi
    else
        rm_and_print $RESULTS_DIR/*-s-0-*-llama-1.txt
        rm_and_print $RESULTS_DIR/*-s-0-128-*-64.txt
    fi
elif [ "$1" = "schedule" ]; then
    for prompt in 64 192 320 448; do
        rm_and_print $RESULTS_DIR/tz-*-1-$prompt-llama-1.txt
    done
elif [ "$1" = "cache" ]; then
    for cache in 32 128 256 384 512; do
        rm_and_print $RESULTS_DIR/tz-s-*-$cache-llama-1.txt
    done
else
    echo "invalid argument $1"
    exit 1
fi