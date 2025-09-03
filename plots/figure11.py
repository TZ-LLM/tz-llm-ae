#!/bin/python

import matplotlib.pyplot as plt
import numpy as np
import os
import re
import matplotlib as mpl
from common import *

fontsize = 15
latex_col = 241.02039  ## pt

sbar_space = 0.03
sbar_wz = 0.18 - sbar_space
n_sbar = 3  # reduced to 3 setups
width = 0.24  # the width of the bars

TINYLLAMA_1_1B = "TinyLlama-1.1B"
GEMMA_2_2B = "Gemma-2-2B"
QWEN25_3B = "Qwen2.5-3B"
PHI_3_3_8B = "Phi-3-3.8B"
LLAMA_3_8B = "Llama-3-8B"

# TINYLLAMA_1_1B = "1.1B"
# GEMMA_2_2B = "2.2B"
# QWEN25_3B = "3B"
# PHI_3_3_8B = "3.8B"
# LLAMA_3_8B = "8B"

STRAWMAN = "Strawman"
BASE = "REE-LLM"
TZ_LLM = "TZ-LLM"

models = [QWEN25_3B, LLAMA_3_8B]
setups = [BASE, TZ_LLM, STRAWMAN]

def read_data_from_files(prefix):
    """Read data from results directory files with given prefix"""
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    
    # Model name mapping for file names
    model_file_map = {
        QWEN25_3B: 'qwen',
        LLAMA_3_8B: 'llama'
    }
    
    data = []
    for model in models:
        file_model = model_file_map[model]
        filename = f'{prefix}-s-5-128-{file_model}-64.txt'
        filepath = os.path.join(results_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
                # Extract decoding_thpt value using regex
                match = re.search(r'decoding_thpt: ([0-9.]+)', content)
                if match:
                    data.append(float(match.group(1)))
                else:
                    print(f"Warning: Could not parse decoding_thpt from {filename}")
                    data.append(0.0)
        except FileNotFoundError:
            print(f"Warning: File {filename} not found")
            data.append(0.0)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            data.append(0.0)
    
    return data

def read_tz_data():
    """Read TZ_LLM data from results directory"""
    return read_data_from_files('tz')

def read_base_data():
    """Read BASE data from results directory"""
    return read_data_from_files('base')

def read_strawman_data():
    """Read STRAWMAN data from results directory"""
    return read_data_from_files('strawman')

# Hard-coded data for STRAWMAN, dynamic data for BASE and TZ_LLM
data = {
    STRAWMAN: read_strawman_data(),  # dynamically read from strawman-s-0-128-$model-64.txt files
    BASE: read_base_data(),  # dynamically read from base-s-0-128-$model-64.txt files
    TZ_LLM: read_tz_data()   # dynamically read from tz-s-0-128-$model-64.txt files
}

colors = {
    BASE: "#C6DBEF",
    TZ_LLM: "#2171B5",
    STRAWMAN: "#084594"
}

def plot():
    plt.rcParams["lines.markersize"] = 3
    plt.rcParams["font.family"] = 'sans-serif'

    fig, ax = plt.subplots()
    
    x = np.arange(len(models))
    
    # Plot bars for each setup
    for i, setup in enumerate(setups):
        offset = (i - len(setups)/2 + 0.5) * (width + sbar_space)
        bars = ax.bar(
            x + offset,
            data[setup],
            width,
            label=setup,
            lw=0.5,
            edgecolor="black",
            color=colors[setup],
            zorder=3
        )
        
        # Add text annotations for STRAWMAN and BASE
        if setup in [STRAWMAN, BASE]:
            for idx, rect in enumerate(bars):
                height = rect.get_height()
                tz_value = data[TZ_LLM][idx]
                
                # Calculate percentage difference
                pct_diff = ((tz_value - height) / height) * 100
                
                # Format text: show + for speedup, - for slowdown
                text = f"{'+' if pct_diff > 0 else ''}{pct_diff:.1f}"
                
                ax.text(
                    rect.get_x() + rect.get_width()/2,
                    height + 0.5,
                    text,
                    ha='center',
                    va='bottom',
                    fontsize=fontsize,
                    rotation=0
                )
    
    # Customize plot
    ax.set_ylabel("Decoding Speed\n(tokens/s)", fontsize=fontsize)
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.tick_params(axis='x', length=0)  # Remove x-axis tick marks while keeping labels
    ax.set_ylim(0, 25)
    # adjust_ax_style(ax)
    
    # Add legend
    ax.legend(
        fontsize=fontsize,
        frameon=False,
        loc="upper center",
        handlelength=1.2,
        labelspacing=0.1,
        ncol=3,
        handletextpad=0.3,
        bbox_to_anchor=(0.5, 1.3),
    )
    
    # Adjust layout
    fig.set_size_inches(get_figsize(latex_col, wf=0.8 * 2, hf=0.37 * 2))
    plt.tight_layout()
    
    save_figure(fig, os.path.splitext(__file__)[0])

def calculate_and_print_ranges():
    """Calculate and print speedup ranges comparing TZ_LLM to STRAWMAN and overhead comparing TZ_LLM to BASE"""
    
    # print("\n=== Decoding Speed Analysis ===")
    # print(f"Models: {models}")
    # print(f"Data: {data}")
    
    # Calculate speedups (TZ_LLM vs STRAWMAN)
    speedups = []
    overheads = []
    
    for i, model in enumerate(models):
        tz_speed = data[TZ_LLM][i]
        strawman_speed = data[STRAWMAN][i]
        base_speed = data[BASE][i]
        
        # Speedup: TZ_LLM / STRAWMAN (higher is better)
        speedup = tz_speed / strawman_speed if strawman_speed > 0 else 0
        speedups.append(speedup)
        
        # Overhead: TZ_LLM / BASE (closer to 1 is better, <1 means TZ_LLM is slower)
        overhead = tz_speed / base_speed if base_speed > 0 else 0
        overheads.append(overhead)
        
        # print(f"\n{model}:")
        # print(f"  TZ_LLM:   {tz_speed:.2f} tokens/s")
        # print(f"  BASE:     {base_speed:.2f} tokens/s")
        # print(f"  STRAWMAN: {strawman_speed:.2f} tokens/s")
        # print(f"  Speedup vs STRAWMAN: {speedup:.2f}x ({((speedup-1)*100):+.1f}%)")
        # print(f"  Overhead vs BASE: {overhead:.2f}x ({((overhead-1)*100):+.1f}%)")
    
    # print(f"\n=== Summary Ranges ===")
    if speedups:
        min_speedup = min(speedups)
        max_speedup = max(speedups)
        print(f"Speedup vs {STRAWMAN}: percentage range: {((min_speedup-1)*100):.1f}% to {((max_speedup-1)*100):.1f}%")
    
    if overheads:
        min_overhead = min(overheads)
        max_overhead = max(overheads)
        print(f"Overhead vs {BASE}: percentage range: {((1-max_overhead)*100):.1f}% to {((1-min_overhead)*100):.1f}%")


if __name__ == "__main__":
    calculate_and_print_ranges()
    plot()
