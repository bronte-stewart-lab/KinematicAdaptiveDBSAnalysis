import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from plot_config import setup_style

setup_style()

data_dir = 'data/titrations'

#load shank velocity data
stim_levels = [0, 50, 75, 90, 100]
shank_data = []
for level in stim_levels:
    df = pd.read_csv(os.path.join(data_dir, f'shankav_{level}.csv'))
    df['Time'] = df['Time'] - df['Time'].iloc[0]
    df = df[df['Time'] <= 15]
    shank_data.append(df)

#global y limits across all traces
y_min = int(np.floor(min(d[['RZAV','LZAV']].min().min() for d in shank_data)))
y_max = int(np.ceil(max(d[['RZAV','LZAV']].max().max() for d in shank_data)))

#load arrhythmicity data
arr = pd.read_csv(os.path.join(data_dir, 'arr_table.csv'))
arr['Time'] = pd.to_datetime(arr['Time'])
t0 = arr['Time'].iloc[0]
arr['Seconds'] = [(t - t0).total_seconds() for t in arr['Time']]
arr['Arrhythmicity'] = arr['Arrhythmicity'] * 100

fig = plt.figure(figsize=(7.3, 3.5))
gs = plt.GridSpec(5, 2, width_ratios=[1, 1], height_ratios=[1]*5, hspace=0.5)

#left panel: shank angular velocity for each stim level
for i, (level, df) in enumerate(zip(stim_levels, shank_data)):
    ax = fig.add_subplot(gs[i, 0])

    ax.plot(df['Time'], df['RZAV'], color='blue', linewidth=1.5)
    ax.plot(df['Time'], df['LZAV'], color='red', linewidth=1.5)
    ax.axhline(0, color='k', linewidth=0.5, alpha=0.5)

    ax.set_ylim(y_min, y_max)
    ax.set_xlim(0, 15)
    ax.set_xticks([0, 5, 10, 15])
    ax.set_yticks([y_min, 0, y_max])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='both', labelsize=8, direction='out')

    if i < len(stim_levels) - 1:
        ax.set_xticklabels([])
    if i == 2:
        ax.set_ylabel('Shank Angular Velocity (deg/s)', fontsize=9)
    if i == len(stim_levels) - 1:
        ax.set_xlabel('Time (s)', fontsize=9)

#right panel: arrhythmicity over time
ax_arr = fig.add_subplot(gs[:, 1])
ax_arr.plot(arr['Seconds'], arr['Arrhythmicity'], 'k-', linewidth=0.8)

max_sec = arr['Seconds'].max()
ax_arr.set_xlim(0, max_sec)
ax_arr.set_xticks(np.linspace(0, max_sec, 5).astype(int))
ax_arr.set_xlabel('Time (s)', fontsize=9)
ax_arr.set_ylabel('Arrhythmicity', fontsize=9)

y_max_arr = 5 * np.ceil(arr['Arrhythmicity'].max() / 5)
ax_arr.set_ylim(0, y_max_arr)
ax_arr.set_yticks(np.arange(0, y_max_arr + 1, max(int(y_max_arr / 4), 1)))
ax_arr.spines['right'].set_visible(False)
ax_arr.spines['top'].set_visible(False)
ax_arr.tick_params(axis='both', labelsize=8, direction='out')

plt.tight_layout()
fig.subplots_adjust(wspace=0.3, hspace=0.5)

os.makedirs('figures', exist_ok=True)
for ext in ['png', 'svg']:
    plt.savefig(f'figures/fig2b_arrhythmicity_threshold.{ext}', dpi=900, bbox_inches='tight')
plt.show()