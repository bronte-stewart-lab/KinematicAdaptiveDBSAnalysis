import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from plot_config import setup_style

setup_style()

#load titration data
df = pd.read_csv('data/titrations_Output_Bertec.csv')
df = df.sort_values('Stim Level')

stim_levels = df['Stim Level'].tolist()
freezing = df['freezes'].tolist()

fig, ax = plt.subplots(figsize=(3.65, 3.5))
fig.patch.set_alpha(0.0)
ax.patch.set_alpha(0.0)

#therapeutic window shading
green_start = stim_levels.index(75)
green_end = stim_levels.index(100)
ax.axvspan(green_start, green_end, alpha=1, color='#BAC095')

ax.plot(range(len(stim_levels)), freezing, 'k-', linewidth=2.5)
ax.scatter(range(len(stim_levels)), freezing, s=100, color='black', zorder=5)

ax.set_xlim(-0.5, len(stim_levels) - 0.5)
ax.set_ylim(0, 100)
ax.set_xlabel('Stim Level (%)', fontsize=12)
ax.set_ylabel('% Time Freezing', fontsize=12)
ax.set_xticks(range(len(stim_levels)))
ax.set_xticklabels([str(int(s)) for s in stim_levels])
ax.tick_params(axis='both', labelsize=12, width=0.5, length=5, direction='out')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

plt.tight_layout()
os.makedirs('figures', exist_ok=True)
for ext in ['png', 'pdf', 'svg']:
    plt.savefig(f'figures/fig2a_titration_freezing.{ext}', dpi=900, transparent=True)
plt.show()