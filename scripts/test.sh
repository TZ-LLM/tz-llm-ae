#!/bin/bash

hdc_timeout() {
    timeout 1 hdc "$@" 2>/dev/null
}

hdc_timeout shell "sleep 10" || echo "timeout"