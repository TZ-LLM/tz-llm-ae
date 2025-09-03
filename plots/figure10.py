#!/bin/python

import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from matplotlib import rc
import re

from common import *


fontsize = 11
latex_col = 241.02039  ## pt

sbar_space = 0.02
sbar_wz = 0.21 - sbar_space
n_sbar = 6
whole_bar_width = (sbar_space + sbar_wz) * (n_sbar - 1)
width = whole_bar_width  # the width of the bars: can also be len(x) sequence
linewidth = 0.5

mpl.rcParams["hatch.linewidth"] = 0.5  # previous pdf hatch

LLAMA_3_8B = "Llama-3-8B"

BASE_FLASH = "REE-LLM-Flash"
TZ_LLM_STRESS = "TZ-LLM"
STRAWMAN = "Strawman"

ULTRA = "UC"
PERSONA = "PC"
DROIDTASK = "DT"

models = [LLAMA_3_8B]
setups = [BASE_FLASH, TZ_LLM_STRESS, STRAWMAN]
benchmarks = [ULTRA, DROIDTASK]

def read_ttft_data(prefix):
    """Read TTFT data from result files and compute averages for given prefix"""
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    
    # File ranges for each benchmark
    ultra_files = [f"{prefix}-s-0-{i}-llama-1.txt" for i in range(5, 10)]  # 5-9
    persona_files = [f"{prefix}-s-0-{i}-llama-1.txt" for i in range(10, 15)]  # 10-14
    droidtask_files = [f"{prefix}-s-0-{i}-llama-1.txt" for i in range(15, 18)]  # 15-17
    
    def read_files_data(file_list):
        ttft_values = []
        for filename in file_list:
            filepath = os.path.join(results_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    content = f.read().strip()
                    # Extract TTFT value using regex
                    match = re.search(r'ttft: ([0-9.]+)', content)
                    if match:
                        ttft_values.append(float(match.group(1)))
                    else:
                        print(f"Warning: Could not parse TTFT from {filename}")
            except FileNotFoundError:
                print(f"Warning: File {filename} not found")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        
        average = sum(ttft_values) / len(ttft_values) if ttft_values else 0
        return average, ttft_values
    
    # Compute averages and collect all values
    ultra_avg, ultra_values = read_files_data(ultra_files)
    droidtask_avg, droidtask_values = read_files_data(droidtask_files)
    
    # print(f"{prefix.upper()} averages - ULTRA: {ultra_avg:.2f}, DROIDTASK: {droidtask_avg:.2f}")
    
    return {
        ULTRA: ultra_avg,
        DROIDTASK: droidtask_avg
    }, {
        ULTRA: ultra_values,
        DROIDTASK: droidtask_values
    }

def read_tz_ttft_data():
    """Read TZ_LLM_STRESS data from result files"""
    return read_ttft_data("tz")

def read_base_ttft_data():
    """Read BASE_FLASH data from result files"""
    return read_ttft_data("base")

def read_strawman_ttft_data():
    """Read STRAWMAN data from result files"""
    return read_ttft_data("strawman")

# Read data from files for both TZ and BASE setups
tz_llm_stress_data, tz_llm_stress_values = read_tz_ttft_data()
base_flash_data, base_flash_values = read_base_ttft_data()
strawman_data, strawman_values = read_strawman_ttft_data()

# Data with dynamic reading for BASE_FLASH and TZ_LLM_STRESS, hard-coded for STRAWMAN
data = {
    LLAMA_3_8B: {
        BASE_FLASH: base_flash_data,  # dynamically read from base-s-0-*-llama-1.txt files
        TZ_LLM_STRESS: tz_llm_stress_data,  # dynamically read from tz-s-0-*-llama-1.txt files
        STRAWMAN: strawman_data,  # dynamically read from strawman-s-0-*-llama-1.txt files
    },
}

# Individual values for geometric mean calculations
individual_values = {
    LLAMA_3_8B: {
        BASE_FLASH: base_flash_values,
        TZ_LLM_STRESS: tz_llm_stress_values,
        STRAWMAN: strawman_values,
    },
}

def geometric_mean(values):
    """Calculate geometric mean without scipy"""
    if not values or any(v <= 0 for v in values):
        return 0
    n = len(values)
    product = 1
    for v in values:
        product *= v
    return product ** (1.0 / n)

def calculate_reduction_and_overhead():
    """Calculate TTFT reduction and overhead using geometric means"""
    model = LLAMA_3_8B
    
    # print("\n" + "="*60)
    # print("TTFT REDUCTION AND OVERHEAD ANALYSIS")
    # print("="*60)
    
    # Calculate reductions (TZ_LLM_STRESS vs STRAWMAN) and overhead (TZ_LLM_STRESS vs BASE_FLASH)
    reductions = {}  # TZ_LLM_STRESS vs STRAWMAN
    overheads = {}   # TZ_LLM_STRESS vs BASE_FLASH
    
    for benchmark in benchmarks:
        tz_values = individual_values[model][TZ_LLM_STRESS][benchmark]
        strawman_values = individual_values[model][STRAWMAN][benchmark]
        base_values = individual_values[model][BASE_FLASH][benchmark]
        
        if not tz_values or not strawman_values or not base_values:
            print(f"Warning: Missing data for {benchmark}")
            continue
            
        # Calculate point-wise reductions and overheads
        point_reductions = []
        point_overheads = []
        
        # For reduction calculation (TZ vs STRAWMAN)
        min_len_reduction = min(len(tz_values), len(strawman_values))
        for i in range(min_len_reduction):
            if strawman_values[i] > 0:
                reduction = (strawman_values[i] - tz_values[i]) / strawman_values[i]
                point_reductions.append(reduction)
        
        # For overhead calculation (TZ vs BASE)
        min_len_overhead = min(len(tz_values), len(base_values))
        for i in range(min_len_overhead):
            if base_values[i] > 0:
                overhead = (tz_values[i] - base_values[i]) / base_values[i]
                point_overheads.append(overhead)
        
        # Calculate geometric means
        if point_reductions:
            # Convert to positive values for geometric mean (add 1 to handle negative reductions)
            positive_reductions = [r + 1 for r in point_reductions]
            geom_mean_reduction = geometric_mean(positive_reductions) - 1
            reductions[benchmark] = geom_mean_reduction
        
        if point_overheads:
            # Convert to positive values for geometric mean (add 1 to handle negative overheads)
            positive_overheads = [o + 1 for o in point_overheads]
            geom_mean_overhead = geometric_mean(positive_overheads) - 1
            overheads[benchmark] = geom_mean_overhead
        
        # print(f"\n{benchmark}:")
        # print(f"  {TZ_LLM_STRESS} vs {STRAWMAN} reduction (geometric mean): {reductions.get(benchmark, 0)*100:.2f}%")
        # print(f"  {TZ_LLM_STRESS} vs {BASE_FLASH} overhead (geometric mean): {overheads.get(benchmark, 0)*100:.2f}%")
        # print(f"  Individual TZ values: {tz_values}")
        # print(f"  Individual STRAWMAN values: {strawman_values}")
        # print(f"  Individual BASE values: {base_values}")
    
    # Find maximum reduction and overhead
    max_reduction = max(reductions.values()) if reductions else 0
    min_reduction = min(reductions.values()) if reductions else 0
    # max_reduction_benchmark = max(reductions, key=reductions.get) if reductions else "N/A"
    
    max_overhead = max(overheads.values()) if overheads else 0
    min_overhead = min(overheads.values()) if overheads else 0
    # max_overhead_benchmark = max(overheads, key=overheads.get) if overheads else "N/A"
    
    print(f"\n" + "-"*60)
    print("SUMMARY:")
    print(f"TTFT reduction ({TZ_LLM_STRESS} vs {STRAWMAN}): {min_reduction*100:.2f}% ~ {max_reduction*100:.2f}%")
    print(f"TTFT overhead ({TZ_LLM_STRESS} vs {BASE_FLASH}): {min_overhead*100:.2f}% ~ {max_overhead*100:.2f}%")
    print("-"*60)
    
    return reductions, overheads

# Calculate and print reduction and overhead analysis
calculate_reduction_and_overhead()

colors = {
    BASE_FLASH: "#6BAED6",
    TZ_LLM_STRESS: "#2171B5",
    STRAWMAN: "#084594"
}

yticks_bottom = {
    LLAMA_3_8B: [0, 10, 20]
}

yticks_top = {
    LLAMA_3_8B: [150, 200]
}


def plot(fig, ax):
    # Single subplot for Llama-3-8B only
    model = LLAMA_3_8B
    
    # Create two subplots with height ratios for the break
    gs = gridspec.GridSpec(2, 1, figure=fig, height_ratios=[7, 12], hspace=0.1)
    ax_top = fig.add_subplot(gs[0])
    ax_bottom = fig.add_subplot(gs[1])
    
    # Calculate bar positions
    x = np.arange(len(benchmarks))
    legend_handles = []
    legend_labels = []
    
    # Plot bars for each setup in both top and bottom axes
    for setup_idx, setup in enumerate(setups):
        values = [data[model][setup][benchmark] / 1000 for benchmark in benchmarks]
        offset = (setup_idx - len(setups)/2 + 0.5) * (sbar_wz + sbar_space)
        
        # Plot in top axis
        bar_top = ax_top.bar(
            x + offset,
            values,
            sbar_wz,
            label=setup,
            lw=0.05,
            edgecolor="black",
            color=colors[setup],
            zorder=3
        )
        legend_handles.append(bar_top)
        legend_labels.append(setup)
        
        # Plot same data in bottom axis
        bar_bottom = ax_bottom.bar(
            x + offset,
            values,
            sbar_wz,
            lw=0.05,
            edgecolor="black",
            color=colors[setup],
            zorder=3
        )
    
    # Set different scales for top and bottom
    top_ylim_lower = data[model][STRAWMAN][DROIDTASK] / 1000 * 0.8
    top_ylim_upper = data[model][STRAWMAN][DROIDTASK] / 1000 * 1.1
    bottom_ylim_lower = 0
    bottom_ylim_upper = max(data[model][TZ_LLM_STRESS][DROIDTASK], data[model][STRAWMAN][ULTRA]) / 1000 * 1.1
    ax_top.set_ylim(top_ylim_lower, top_ylim_upper)
    ax_bottom.set_ylim(bottom_ylim_lower, bottom_ylim_upper)
    
    # Add break marks
    d = 0.015  # Size of the diagonal lines
    kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False)
    ax_top.plot((-d, +d), (-d, +d), **kwargs)
    ax_top.plot((1-d, 1+d), (-d, +d), **kwargs)
    kwargs.update(transform=ax_bottom.transAxes)
    ax_bottom.plot((-d, +d), (1-d, 1+d), **kwargs)
    ax_bottom.plot((1-d, 1+d), (1-d, 1+d), **kwargs)
    
    # Customize each subplot
    for ax_sub in [ax_top, ax_bottom]:
        adjust_ax_style(ax_sub)
        ax_sub.set_xticks(x)
        ax_sub.tick_params(axis="y", labelsize=fontsize)
    
    # Only show x labels on bottom plot
    ax_top.set_xticklabels([])
    ax_bottom.set_xticklabels(benchmarks)
    ax_bottom.tick_params(axis='x', labelsize=fontsize - 1)

    ax_top.set_yticks(yticks_top[model])
    ax_bottom.set_yticks(yticks_bottom[model])
    
    # Add model name to top-left of top subplot
    ax_top.text(0.03, 0.93, model, fontsize=fontsize-2, 
               transform=ax_top.transAxes, 
               verticalalignment='top')
    
    # Add y-label
    ax_bottom.set_ylabel("TTFT (s)", fontsize=fontsize)
    
    # Add legend at the top of the figure
    fig.legend(
        legend_handles,
        legend_labels,
        fontsize=fontsize-2,
        frameon=False,
        loc="upper center",
        handlelength=1.2,
        labelspacing=0.1,
        ncol=len(setups),
        bbox_to_anchor=(0.5, 1.02),  # Position above the figure
        handletextpad=0.3,
    )


if __name__ == "__main__":
    plt.rcParams["lines.markersize"] = 3
    plt.rcParams["font.family"] = 'sans-serif'

    fig = plt.figure(constrained_layout=False)

    plot(fig, None)

    # Adjust figure size for single subplot
    fig.set_size_inches(get_figsize(latex_col, wf=0.8, hf=0.12 * 4))  # Smaller size for single subplot
    fig.subplots_adjust(top=0.85)  # Leave space for legend

    save_figure(fig, os.path.splitext(__file__)[0])
