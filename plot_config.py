import matplotlib.pyplot as plt
import numpy as np

plt.style.use('default')
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
plt.rcParams['font.size'] = 8
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0
plt.rcParams['lines.linewidth'] = 1.8
plt.rcParams['patch.linewidth'] = 0.8
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['savefig.transparent'] = True

CONDITION_COLORS = {
    "OFF": "#E69F00",
    "cDBS": "#56B4E9",
    "KaDBS": "#009E73",
    "iDBS": "#F0E442"
}

PATIENT_COLORS = {
    'RCS02': '#C62828', 'RCS03': '#1565C0', 'RCS04': '#2E7D32',
    'RCS06': '#EF6C00', 'RCS11': '#6A1B9A',
    'RCS01': '#F06292', 'RCS09': '#42A5F5', 'RCS10': '#66BB6A'
}

PATIENT_LABELS = {
    'RCS02': '02', 'RCS03': '03', 'RCS04': '04',
    'RCS06': '06', 'RCS11': '11',
    'RCS01': '01', 'RCS09': '09', 'RCS10': '10'
}

CONDITION_ORDER = ['OFF', 'cDBS', 'KaDBS', 'iDBS']

EVENT_MAP = {
    'baseline': 'OFF',
    'olDBS': 'cDBS',
    'KaDBSI': 'KaDBS',
    'iolDBSI': 'iDBS'
}


def get_axis_limits(data, metric, group_patients=None):
    if group_patients:
        data = data[data['patient_num'].isin(group_patients)]
    values = data[metric].dropna()
    if len(values) == 0:
        return -5, 15
    ymin = max(-5, values.min() - max(1, values.min() * 0.05))
    ymax = values.max() + max(2, values.max() * 0.1)
    return ymin, ymax


def set_nice_ticks(ax, ymin, ymax):
    r = ymax - ymin
    if r <= 20:
        step = 5
    elif r <= 50:
        step = 10
    elif r <= 100:
        step = 20
    elif r <= 200:
        step = 25
    else:
        step = 50
    start = int(np.floor(ymin / step)) * step
    end = int(np.ceil(ymax / step)) * step
    ticks = np.arange(start, end + step, step)
    ticks = ticks[(ticks >= ymin - step) & (ticks <= ymax + step)]
    ax.set_yticks(ticks)
    ax.set_ylim(ymin - max(step * 0.2, r * 0.08), ymax + step * 0.4)


def set_zero_padded_ticks(ax, ymax, pad=5):
    if ymax <= 20:
        step = 5
    elif ymax <= 50:
        step = 10
    elif ymax <= 100:
        step = 20
    elif ymax <= 200:
        step = 25
    else:
        step = 50
    end = int(np.ceil(ymax / step)) * step
    ticks = np.arange(0, end + step, step)
    ax.set_yticks(ticks)
    ax.set_ylim(-pad, ymax + step * 0.4)


def style_axis(ax):
    ax.spines[['right', 'top']].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=9, pad=3)
    ax.grid(True, linestyle='-', alpha=0.2, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.patch.set_alpha(0.0)


def finalize_axes(axes):
    for ax in axes:
        ax.tick_params(direction='out', pad=4, labelsize=9, width=1.0)
        for spine in ax.spines.values():
            spine.set_color('#333333')
            spine.set_linewidth(1.0)
        ax.margins(x=0.03)


def plot_trajectories(ax, data, patients, metric, marker='o', ls='-'):
    for pid in patients:
        if pid not in data['patient_num'].unique():
            continue
        pdata = data[data['patient_num'] == pid]
        xs, ys = [], []
        for i, cond in enumerate(CONDITION_ORDER):
            row = pdata[pdata['Condition'] == cond]
            if len(row) > 0 and not np.isnan(row[metric].iloc[0]):
                xs.append(i)
                ys.append(row[metric].iloc[0])
        if len(xs) > 1:
            ax.plot(xs, ys, color=PATIENT_COLORS[pid],
                    marker=marker, linewidth=2.2, markersize=7, alpha=0.9,
                    markerfacecolor=PATIENT_COLORS[pid],
                    markeredgecolor='white', markeredgewidth=1.0,
                    linestyle=ls)
    ax.set_xticks(range(len(CONDITION_ORDER)))
    ax.set_xticklabels(CONDITION_ORDER, fontsize=9)