#!/bin/bash
set -e

CURRENT_DIR=$(realpath $(dirname $0))
ROOT_DIR=$(realpath $CURRENT_DIR/../..)
TZ_LLM_DIR=$ROOT_DIR/tz-llm
SHARE_DIR=$CURRENT_DIR/share

mkdir -p $SHARE_DIR
cp $CURRENT_DIR/build-oh-docker.sh $SHARE_DIR/

$CURRENT_DIR/oh-builder.sh $SHARE_DIR bash -c ./build-oh-docker.sh

for file in $SHARE_DIR/rknpu/*; do
    if [ -f "$file" ]; then
        hdc file send "$file" /data/local/tmp/rknpu/
    fi
done

for file in $SHARE_DIR/build-rknpure/*; do
    if [ -f "$file" ]; then
        hdc file send "$file" /data/local/tmp/rknpu/
    fi
done
