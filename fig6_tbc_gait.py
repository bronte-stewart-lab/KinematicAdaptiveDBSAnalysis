import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from plot_config import *

warnings.filterwarnings('ignore', category=UserWarning)

raw_data = pd.read_csv('data/MergedTBCMetrics.csv')
raw_filtered = raw_data[raw_data['stringvisit'].isin(EVENT_MAP.keys())].copy()

rows = []
for _, row in raw_filtered.iterrows():
    patient = row['patient_num']
    condition = row['stringvisit']

    rows.append({
        'patient_num': patient,
        'stringvisit': condition,
        'Task': 'Ellipses',
        'mean_freezing': row.get('Emean_freezing', np.nan),
        'arrhythmicity_scaled': row.get('Earrhythmicity_new', np.nan) * 100
            if pd.notna(row.get('Earrhythmicity_new', np.nan)) else np.nan,
        'mean_shankav': row.get('Emean_shankav', np.nan)
    })

    rows.append({
        'patient_num': patient,
        'stringvisit': condition,
        'Task': 'Figure8',
        'mean_freezing': row.get('eigmean_freezing', np.nan),
        'arrhythmicity_scaled': row.get('eigarrhythmicity_new', np.nan) * 100
            if pd.notna(row.get('eigarrhythmicity_new', np.nan)) else np.nan,
        'mean_shankav': row.get('eigmean_shankav', np.nan)
    })

filtered = pd.DataFrame(rows)
filtered['Condition'] = filtered['stringvisit'].map(EVENT_MAP)

freezers = ['RCS02', 'RCS03', 'RCS09', 'RCS11']
nonfreezer = ['RCS01', 'RCS04', 'RCS10']
available = sorted(filtered['patient_num'].unique())

vel_lim = get_axis_limits(filtered, 'mean_shankav')
arrh_f_lim = get_axis_limits(filtered, 'arrhythmicity_scaled', freezers)
arrh_nf_lim = get_axis_limits(filtered, 'arrhythmicity_scaled', nonfreezer)

fig = plt.figure(figsize=(7.3, 7.2), dpi=600)
fig.patch.set_alpha(0.0)
gs = fig.add_gridspec(4, 2, hspace=0.4, wspace=0.3, height_ratios=[1, 1, 1, 0.35],
                      left=0.08, right=0.96, top=0.96, bottom=0.04)

# A: % time freezing boxplot (both tasks)
ax_a = fig.add_subplot(gs[0, 0])
style_axis(ax_a)
sns.boxplot(data=filtered, x='Condition', y='mean_freezing',
            order=CONDITION_ORDER, palette=CONDITION_COLORS,
            width=0.6, ax=ax_a, flierprops={'marker': 'none'},
            boxprops={'alpha': 0.8, 'linewidth': 1.0},
            whiskerprops={'linewidth': 1.0}, capprops={'linewidth': 1.0},
            medianprops={'linewidth': 1.5, 'color': 'white'},
            hue='Condition', legend=False)
sns.stripplot(data=filtered, x='Condition', y='mean_freezing',
              order=CONDITION_ORDER, color='#2C2C2C', size=5, alpha=0.7,
              jitter=0.25, ax=ax_a, marker='o',
              edgecolor='white', linewidth=0.5)
ax_a.set_xticks(range(len(CONDITION_ORDER)))
ax_a.set_xticklabels(CONDITION_ORDER, fontsize=9)
set_zero_padded_ticks(ax_a, 100)
ax_a.set_ylabel('% Time Freezing', fontsize=11)
ax_a.set_xlabel('')

# B: freezer trajectories (averaged across tasks)
ax_b = fig.add_subplot(gs[0, 1])
style_axis(ax_b)
traj_freeze = filtered.groupby(['patient_num', 'Condition'])['mean_freezing'].mean().reset_index()
plot_trajectories(ax_b, traj_freeze, freezers, 'mean_freezing')
set_zero_padded_ticks(ax_b, 100)
ax_b.set_ylabel('% Time Freezing\n(Baseline Freezers)', fontsize=11)

# C: angular velocity boxplot
ax_c = fig.add_subplot(gs[1, 0])
style_axis(ax_c)
sns.boxplot(data=filtered, x='Condition', y='mean_shankav',
            order=CONDITION_ORDER, palette=CONDITION_COLORS,
            width=0.6, ax=ax_c, flierprops={'marker': 'none'},
            boxprops={'alpha': 0.8, 'linewidth': 1.0},
            whiskerprops={'linewidth': 1.0}, capprops={'linewidth': 1.0},
            medianprops={'linewidth': 1.5, 'color': 'white'},
            hue='Condition', legend=False)
sns.stripplot(data=filtered, x='Condition', y='mean_shankav',
              order=CONDITION_ORDER, color='#2C2C2C', size=5, alpha=0.7,
              jitter=0.25, ax=ax_c, marker='o',
              edgecolor='white', linewidth=0.5)
ax_c.set_xticks(range(len(CONDITION_ORDER)))
ax_c.set_xticklabels(CONDITION_ORDER, fontsize=9)
set_nice_ticks(ax_c, vel_lim[0], vel_lim[1])
ax_c.set_ylabel('Mean Angular Velocity\n(deg/s)', fontsize=11)
ax_c.set_xlabel('')

# D: velocity trajectories (freezers & non-freezers)
ax_d = fig.add_subplot(gs[1, 1])
style_axis(ax_d)
traj_vel = filtered.groupby(['patient_num', 'Condition'])['mean_shankav'].mean().reset_index()
plot_trajectories(ax_d, traj_vel, freezers, 'mean_shankav', marker='o', ls='-')
plot_trajectories(ax_d, traj_vel, nonfreezer, 'mean_shankav', marker='^', ls='--')
set_nice_ticks(ax_d, vel_lim[0], vel_lim[1])
ax_d.set_ylabel('Mean Angular Velocity\n(deg/s)', fontsize=11)

# E: arrhythmicity (freezers)
ax_e = fig.add_subplot(gs[2, 0])
style_axis(ax_e)
traj_arrh = filtered.groupby(['patient_num', 'Condition'])['arrhythmicity_scaled'].mean().reset_index()
plot_trajectories(ax_e, traj_arrh, freezers, 'arrhythmicity_scaled')
set_nice_ticks(ax_e, arrh_f_lim[0], arrh_f_lim[1])
ax_e.set_ylabel('Arrhythmicity\n(Freezers)', fontsize=11)

# F: arrhythmicity (non-freezers)
ax_f = fig.add_subplot(gs[2, 1])
style_axis(ax_f)
plot_trajectories(ax_f, traj_arrh, nonfreezer, 'arrhythmicity_scaled', marker='^', ls='--')
set_nice_ticks(ax_f, arrh_nf_lim[0], arrh_nf_lim[1])
ax_f.set_ylabel('Arrhythmicity\n(Non-Freezers)', fontsize=11)

ax_leg = fig.add_subplot(gs[3, :])
ax_leg.axis('off')

handles = []
sorted_f = sorted([p for p in freezers if p in available], key=lambda x: int(PATIENT_LABELS[x]))
sorted_nf = sorted([p for p in nonfreezer if p in available], key=lambda x: int(PATIENT_LABELS[x]))

for pid in sorted_f:
    handles.append(Line2D([0], [0], color=PATIENT_COLORS[pid],
                          marker='o', linewidth=2.2, markersize=7,
                          markerfacecolor=PATIENT_COLORS[pid],
                          markeredgecolor='white', markeredgewidth=0.8,
                          label=f'P{PATIENT_LABELS[pid]}'))

handles.append(Patch(facecolor='none', edgecolor='none', label=''))

for pid in sorted_nf:
    handles.append(Line2D([0], [0], color=PATIENT_COLORS[pid],
                          marker='^', linewidth=2.2, markersize=7,
                          markerfacecolor=PATIENT_COLORS[pid],
                          markeredgecolor='white', markeredgewidth=0.8,
                          linestyle='--', label=f'P{PATIENT_LABELS[pid]}'))

ax_leg.legend(handles=handles, loc='center',
              ncol=len(sorted_f) + 1, fontsize=10,
              frameon=False, columnspacing=1.5,
              handletextpad=0.6, handlelength=2.2)

all_axes = [ax_a, ax_b, ax_c, ax_d, ax_e, ax_f]
finalize_axes(all_axes)
plt.tight_layout(pad=1.2)

fig.savefig('figures/fig6_tbc_gait.svg', format='svg', dpi=900,
            bbox_inches='tight', transparent=True)
plt.show()