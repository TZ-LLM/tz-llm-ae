#!/bin/bash
set -e

CURRENT_DIR=$(realpath $(dirname $0))
ROOT_DIR=$(realpath $CURRENT_DIR/../..)
TZ_LLM_DIR=$ROOT_DIR/tz-llm
SHARE_DIR=$CURRENT_DIR/share

mkdir -p $SHARE_DIR

cp $CURRENT_DIR/build-chcore-docker.sh $SHARE_DIR/
$CURRENT_DIR/oh-builder.sh $SHARE_DIR bash -c ./build-chcore-docker.sh

cp $CURRENT_DIR/build-llama-docker.sh $SHARE_DIR/
$CURRENT_DIR/llama-builder.sh $SHARE_DIR bash -c ./build-llama-docker.sh

hdc shell "mkdir -p /data/local/tmp/rknpu"
