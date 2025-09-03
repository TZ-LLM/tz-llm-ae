#!/bin/bash
set -e

CURRENT_DIR=$(realpath $(dirname $0))
ROOT_DIR=$(realpath $CURRENT_DIR/../..)
TZ_LLM_DIR=$ROOT_DIR/tz-llm

pushd $1
SHARE_DIR=$(pwd)
popd
shift

echo "SHARE_DIR: $SHARE_DIR"
echo "CMD: $@"

docker run -it --rm \
    -v $TZ_LLM_DIR/tee_os_kernel:/home/vectorxj/openharmony/base/tee/tee_os_kernel \
    -v $TZ_LLM_DIR/llama.cpp:/home/vectorxj/chcore/opentrustee_llm/llama.cpp \
    -v $SHARE_DIR:/home/vectorxj/share \
    -w /home/vectorxj/share \
    vectorxj0553/tz-llm-llama-builder:latest \
    $@
