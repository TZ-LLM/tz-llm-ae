#!/bin/bash

SHARE_DIR=/home/vectorxj/share

export PATH=/home/tools/clang_linux-x86_64-36cd05-20221030/bin:$PATH
export PATH=/home/tools/ninja:$PATH
export PATH=/home/tools/gn:$PATH
export PATH=/home/tools/node-v14.19.1-linux-x64/bin:$PATH
export PATH=/root/.local/bin:$PATH

pushd /home/vectorxj/openharmony/
./chcore.sh
./linux.sh
set -e
./chcore.sh
popd

ls -lhat /home/vectorxj/openharmony/out/uboot/src_tmp/

mkdir -p $SHARE_DIR/images
cp /home/vectorxj/openharmony/out/uboot/src_tmp/boot.img $SHARE_DIR/images/
cp /home/vectorxj/openharmony/out/uboot/src_tmp/uboot.img $SHARE_DIR/images/

mkdir -p $SHARE_DIR/rknpu/
cp /home/vectorxj/rknpu/* $SHARE_DIR/rknpu/
