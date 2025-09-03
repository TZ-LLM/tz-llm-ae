#!/bin/python

import matplotlib.pyplot as plt
from common import *
import os

fontsize = 16
latex_col = 241.02039  ## pt
linewidth = 1.4
plt.rcParams['lines.markersize'] = 3

marker_sz = 6
marker_edge_w = linewidth

LLAMA_3_8B = "Llama-3-8B"

BASE = "REE-LLM"
TZ_LLM = "TZ-LLM"

def read_result_file(filepath):
    """Read a result file and return a dictionary of metrics"""
    data = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(': ')
                    try:
                        data[key] = float(value)
                    except ValueError:
                        data[key] = value
    except FileNotFoundError:
        print(f"Warning: File {filepath} not found")
        return None
    return data

models = [LLAMA_3_8B]
setups = [BASE, TZ_LLM]
contexts = [32, 256, 512]
cache_percentages = [0, 20, 40, 60, 80, 100]
cache_values = [0, 1, 2, 3, 4, 5]  # Maps to cache_percentages

# Read data from result files
results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')

# Initialize data structure
data = {LLAMA_3_8B: {}}

for context in contexts:
    data[LLAMA_3_8B][context] = {TZ_LLM: []}
    
    for cache_val in cache_values:
        # Read the result file: tz-s-$cache-$prompt_length-llama-1.txt
        filename = f"tz-s-{cache_val}-{context}-llama-1.txt"
        filepath = os.path.join(results_dir, filename)
        result_data = read_result_file(filepath)
        
        if result_data is not None:
            # Use ttft as the metric (TTFT in milliseconds)
            ttft = result_data.get('ttft', 0)
            data[LLAMA_3_8B][context][TZ_LLM].append(ttft)
        else:
            # Fill with 0 if file not found
            data[LLAMA_3_8B][context][TZ_LLM].append(0)
            print(f"Missing file: {filename}")

print("Data loaded:")
for context in contexts:
    print(f"Context {context}: {data[LLAMA_3_8B][context][TZ_LLM]}")

RPS = "rps"
LATENCY = "latency"
MARKER = "marker"
COLOR = "color"

TTFT = "TTFT (s)"
TPOT = "TPOT (s)"

markers = {
    32: 'o',
    256: 'h',
    512: 'D',
}

colors = {
    32: color_list[0],
    256: color_list[3],
    512: color_list[4],
}

fig, ax = plt.subplots(1, 1, figsize=(6, 4))

model = LLAMA_3_8B

ylim_upper = 0

for ctx in contexts:
    tz_llm_data = [ttft / data[model][ctx][TZ_LLM][0] for ttft in data[model][ctx][TZ_LLM]]
    # base_data = data[model][ctx][BASE] / 1000
    ylim_upper = max(ylim_upper, max(tz_llm_data))
    
    # Plot TZ-LLM line
    ax.plot(
        cache_percentages,
        tz_llm_data,
        label=f"len={ctx}",
        marker=markers[ctx],
        color=colors[ctx],
        linewidth=linewidth,
        markersize=marker_sz,
        markeredgewidth=marker_edge_w,
    )
    
    # Plot baseline horizontal line
    # ax.axhline(
    #     y=base_data,
    #     color=colors[ctx],
    #     linestyle='--',
    #     label=f"{BASE} (len={ctx})"
    # )

ax.set_xlabel('Cache Proportion (%)', fontsize=fontsize)
ax.set_ylabel('Normalized TTFT', fontsize=fontsize)

ax.text(0.5, 1.05, model,
        horizontalalignment='center',
        transform=ax.transAxes,
        fontsize=fontsize)
        
ax.grid(True, linestyle='--')
ax.tick_params(axis='both', labelsize=fontsize-2)

# Set only the lower bound of y-axis
ax.set_ylim([0, ylim_upper * 1.1])

# Adjust legend - show all lines
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, 
          ncol=3, 
          bbox_to_anchor=(0.5, 1.07),
          loc='center', 
          fontsize=fontsize,
        #   columnspacing=0.6,
          frameon=False)

plt.tight_layout()
save_figure(fig, os.path.splitext(__file__)[0])
