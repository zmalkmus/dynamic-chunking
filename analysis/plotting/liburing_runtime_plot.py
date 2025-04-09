#!/usr/bin/env python3
import os
import numpy as np       # For numerical operations
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches  # For legend handles
import matplotlib.ticker as ticker     # For setting tick intervals
import seaborn as sns  # For a colorblind-friendly palette
from matplotlib.lines import Line2D  # For creating custom legend handles

# ------------------------------
# Step 0: Define Helper Variables
# ------------------------------
# Mapping from test case indicator (in "Copy Time") to test case name.
legend_mapping = {
    'afo': '100% First Occurs',
    'afd': '100% Fixed Duplicates',
    'sfm': '25% First Occurs,\n50% Shifted Duplicates'
}

# ------------------------------
# Step 1: Load the CSV Data
# ------------------------------
csv_filename = '../data/liburing/liburing_runtimes.csv'
df = pd.read_csv(csv_filename, header=None, 
                 names=["Approach", "Unused1", "Unused2", "Copy Time", "Restore Time"])

df = df[df["Approach"] != "Tree_Baseline"]
df = df[df["Approach"] != "List"]
df = df[df["Approach"] != "Basic"]

# Preserve the original order of approaches as they appear in the CSV.
original_approach_order = df["Approach"].unique()
df["Approach"] = pd.Categorical(df["Approach"], 
                                categories=original_approach_order, 
                                ordered=True)

# ------------------------------
# Step 2: Process the Data
# ------------------------------
grouped = df.groupby(['Approach', 'Copy Time'], sort=False)['Restore Time'].mean().reset_index()
pivot = grouped.pivot(index='Approach', columns='Copy Time', values='Restore Time')

# ------------------------------
# Step 3: Prepare Consistent Ordering, Colors, and Dense Hatch Patterns
# ------------------------------
approach_order = list(original_approach_order)
global_colors = sns.color_palette("colorblind", n_colors=len(approach_order))
hatch_patterns = [
    r'//',   # Dense forward slashes
    r'\\',   # Dense backslashes
    r'++',   # Dense plus signs
    r'XX',   # Dense X's (if more needed, add more patterns)
]
test_case_order = list(legend_mapping.keys())

# ------------------------------
# Step 4: Create a Grouped Bar Chart with a Broken y-Axis
# ------------------------------
data_for_plot = pivot.loc[approach_order, test_case_order].T

# Define parameters for the broken y-axis.
y_break = 20  # y-value at which to break the axis
max_val = data_for_plot.max().max()
upper_ylim = max_val * 1.1 if max_val > y_break else y_break

# Set up the figure with two subplots (upper and lower) sharing the x-axis.
fig, (ax_upper, ax_lower) = plt.subplots(2, 1, sharex=True, figsize=(8, 7),
                                           gridspec_kw={'height_ratios': [1, 2]})

n_test_cases = len(test_case_order)
n_approaches = len(approach_order)
indices = np.arange(n_test_cases)
group_width = 0.7
bar_width = group_width / n_approaches

# Plot bars for each approach on both axes.
for i, approach in enumerate(approach_order):
    values = data_for_plot[approach].values
    x_positions = indices - group_width/2 + i * bar_width + bar_width/2
    ax_upper.bar(x_positions, values, width=bar_width,
                 color=global_colors[i],
                 hatch=hatch_patterns[i % len(hatch_patterns)],
                 label=approach)
    ax_lower.bar(x_positions, values, width=bar_width,
                 color=global_colors[i],
                 hatch=hatch_patterns[i % len(hatch_patterns)])

# Set y-axis limits.
ax_upper.set_ylim(y_break, upper_ylim)
ax_lower.set_ylim(0, y_break)
ax_lower.yaxis.set_major_locator(ticker.MultipleLocator(5))  # Lower axis ticks at intervals of 5

# Hide the spines between the two plots.
ax_upper.spines['bottom'].set_visible(False)
ax_lower.spines['top'].set_visible(False)
ax_upper.tick_params(labeltop=False)  # Hide top tick labels on the upper plot

# Add diagonal lines to indicate the break.
d = .015  # proportion for the diagonal line size in axes coordinates
kwargs = dict(transform=ax_upper.transAxes, color='k', clip_on=False)
ax_upper.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
ax_upper.plot((1 - d, 1 + d), (-d, +d), **kwargs)    # top-right diagonal
kwargs.update(transform=ax_lower.transAxes)
ax_lower.plot((-d, +d), (1 - d, 1 + d), **kwargs)    # bottom-left diagonal
ax_lower.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

# Set the x-axis labels to the test case names (from legend_mapping) on the lower axis.
ax_lower.set_xticks(indices)
ax_lower.set_xticklabels([legend_mapping[tc] for tc in test_case_order])
ax_lower.set_xlabel('Test Case')
ax_lower.set_ylabel('Restore Time')
ax_upper.set_title("Restoring Final Chkpt (3) in 1G×4 Chkpts (512B Chunks)")

# Add a horizontal line at Restore Time = 1.52456 on the lower axis.
ax_lower.axhline(y=3.95082, color='black', linestyle='-', linewidth=1, label='Full')

# Option 2: Manually add the "Full" line handle to the legend.
full_line_handle = Line2D([0], [0], color='black', linestyle='-', linewidth=1, label='Full')
handles, labels = ax_upper.get_legend_handles_labels()
handles.insert(0, full_line_handle)
labels.insert(0, 'Full')
ax_upper.legend(handles=handles, labels=labels, title='Approach', loc='best')

plt.tight_layout()

# ------------------------------
# Step 5: Save the Figure
# ------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
graphs_dir = os.path.join(script_dir, '../graphs')
if not os.path.exists(graphs_dir):
    os.makedirs(graphs_dir)

merged_save_path = os.path.join(graphs_dir, 'liburing_restore_time_polaris.png')
plt.savefig(merged_save_path, dpi=300)
print(f"Merged graph saved to {merged_save_path}")

plt.show()
