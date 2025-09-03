#!/bin/bash

SCRIPT_DIR=$(realpath $(dirname $0))
PLOT_DIR=$(realpath $(dirname $0)/../plots)

$SCRIPT_DIR/end-to-end-decode.sh

python3 $PLOT_DIR/figure11.py

