#!/bin/bash
set -e

CURRENT_DIR=$(realpath $(dirname $0))
ROOT_DIR=$(realpath $CURRENT_DIR/../..)
FLASH_DIR=$ROOT_DIR/flash-proxy/
SHARE_DIR=$CURRENT_DIR/share

hdc shell reboot loader

sleep 5

env -u http_proxy -u https_proxy python $FLASH_DIR/client.py $SHARE_DIR/images
