#!/bin/bash

SCRIPT_DIR=$(realpath $(dirname $0))
PLOT_DIR=$(realpath $(dirname $0)/../plots)

$SCRIPT_DIR/cache.sh

python3 $PLOT_DIR/figure14.py

