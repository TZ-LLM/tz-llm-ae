# TZ-LLM Artifact

This repository contains the artifact for the EuroSys '26 paper "TZ-LLM: Protecting On-Device Large Language Models with Arm TrustZone". Authors: Xunjie Wang*, Jiacheng Shi*, Zihan Zhao, Yang Yu, Zhichao Hua, Jinyu Gu (Shanghai Jiao Tong University).

## Overview

The artifact includes the source code of our prototype system (`tz-llm`), the scripts for running experiments in the paper (`scripts`), the scripts for plotting the experimental results (`plots`), and the tools for flashing images to the board (`flash-proxy`).

## Project Structure

```
├── flash-proxy/           # Tools to flash images to the board
├── plots/                 # Python scripts to generate result figures
├── scripts/               # Evaluation scripts
└── tz-llm/                # Source code
    ├── linux-5.10-opi/    # Linux kernel for Orange Pi
    ├── llama.cpp/         # llama.cpp framework
    ├── tee_os_kernel/     # TEE OS
    └── tzdriver/          # TEE driver for Linux-TEE communication
```

## Hardware Dependencies

The artifact requires an Orange Pi 5 Plus board (RK3588 CPU/NPU).
A standalone machine is required to build the artifact and communicate with the board using a USB-to-USB cable.
The machine should have at least 8 GB of memory and 100 GB of free disk space.

## Software Dependencies

The standalone machine should operate on a Linux OS (Ubuntu 22.04.3 tested)
and have the following dependencies installed:
OpenHarmony Device Connector for board communication,
Python3 and its matplotlib library for plotting and analysis,
and Docker for containerized builds.

## Setup

1. Connect to the prepared host machine using SSH. Please provide your SSH public keys on the HotCRP website.
2. Download the artifact to the host machine.
3. Initialize the submodules.

```
git submodule update --init
```

## Major Claims

- Claim C1: TZ-LLM can reduce TTFT by 76.1\%~90.9\% compared to the Strawman baseline and incur 5.2\%~28.3\% overhead compared to the REE-LLM-Memory baseline.
- Claim C2: TZ-LLM can increase decoding speed by 0.9\%~23.2\% compared to the Strawman 
baseline and incur 1.3\%~4.9\% overhead compared to the REE-LLM baseline.
- Claim C3: As more parameters are cached, partial parameter caching can reduce TTFT approximately linearly up to a threshold.

## Evaluation Workflow

### 0. Kick-the-Tires

This step builds the system components and runs a simple test:

```bash
./scripts/0-kick-the-tires.sh
```

It builds the Linux kernel and TEE OS (including llama.cpp Trusted Application),
flashes images of the Linux kernel and the TEE OS to the Orange Pi board,
and runs a simple LLM inference with performance measurements.

**Expected output:**
```
=================kick-the-tires results=================
ttft: 1957.70        # TTFT in miliseconds
decoding_thpt: 7.77  # Decoding speed in tokens/s
=================kick-the-tires results=================
```

**Runtime:** ~30 compile-minutes and ~10 compute-minutes.

### 1. End-to-End Prefill Performance (Experiment E1)

To reproduce **Figure 10** in the paper, run the script:

```bash
./scripts/1-end-to-end-prefill.sh
```

It evaluates the TTFT of TZ-LLM and other baselines across different benchmarks.
The results are displayed in `plots/figure10.pdf`.

**Runtime:** ~60 compute-minutes.

### 2. End-to-End Decoding Performance (Experiment E2)

To reproduce **Figure 11** in the paper, run the script:

```bash
./scripts/2-end-to-end-decoding.sh
```

It evaluates the decoding speed of TZ-LLM and other baselines across different models.
The results are displayed in `plots/figure11.pdf`.

**Runtime:** ~20 compute-minutes.

### 3. Partial Parameter Caching (Experiment E3)

To reproduce **Figure 14** in the paper, run the script:

```bash
./scripts/3-caching.sh
```

It evaluates the effect of partial parameter caching on the TTFT of TZ-LLM across different cache proportions and prompt lengths.
The results are displayed in `plots/figure14.pdf`.

**Runtime:** ~60 compute-minutes.

## Additional Information

### Docker Images

Prebuilt Docker images are used for reproducible builds:
- `vectorxj0553/tz-llm-llama-builder`: Contains toolchain for building llama.cpp
- `vectorxj0553/tz-llm-oh-builder`: Contains OpenHarmony build environment for kernel and TEE OS
- These images are too large to download. To avoid the download effort, we have prepared the images on the host machine.

### Flash Full OpenHarmony Images

The prepared board already has the necessary OpenHarmony base images flashed. For normal evaluation, you only need to flash the TEE OS and Linux kernel components, which are handled automatically by the evaluation scripts.

However, if you want to flash full images, please follow these steps:
1. Use the [Linux Upgrade Tool](https://github.com/LubanCat/tools/tree/master/linux/Linux_Upgrade_Tool/Linux_Upgrade_Tool) to flash complete OpenHarmony images
2. Prebuilt full system images are available [here](https://zenodo.org/records/17047745)
