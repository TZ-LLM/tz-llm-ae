#!/bin/bash

set -e

SCRIPT_DIR=$(realpath $(dirname $0))
KICK_THE_TIRES_DIR=$SCRIPT_DIR/kick-the-tires/
FLASH_PROXY_DIR=$SCRIPT_DIR/../flash-proxy/
AE_ROOT=$(realpath $SCRIPT_DIR/../)
RESULTS_DIR=$AE_ROOT/results/

$KICK_THE_TIRES_DIR/build-llama.sh
$KICK_THE_TIRES_DIR/build-oh.sh
$KICK_THE_TIRES_DIR/flash.sh

$SCRIPT_DIR/run-mem-retry.sh tz s 0 32 qwen 8
echo "=================kick-the-tires results================="
cat $RESULTS_DIR/tz-s-0-32-qwen-8.txt
echo "=================kick-the-tires results================="
rm $RESULTS_DIR/tz-s-0-32-qwen-8.txt
