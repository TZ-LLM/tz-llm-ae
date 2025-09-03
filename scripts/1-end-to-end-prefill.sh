#!/bin/bash

SCRIPT_DIR=$(realpath $(dirname $0))
PLOT_DIR=$(realpath $(dirname $0)/../plots)

$SCRIPT_DIR/end-to-end-prefill.sh

python3 $PLOT_DIR/figure10.py

