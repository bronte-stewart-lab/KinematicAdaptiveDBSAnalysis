import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

plt.style.use('default')
rcParams['font.sans-serif'] = ['Arial']
rcParams['font.family'] = 'sans-serif'
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42
rcParams['font.size'] = 12
rcParams['axes.linewidth'] = 0.5

data_sip = pd.read_excel('data/KaDBS_I_SIP.xlsx')
data_tbc = pd.read_excel('data/KaDBS_I_TBC.xlsx')

sip_pids = [1, 2, 3, 4, 6, 9, 10, 11]
tbc_pids = [1, 2, 3, 4, 9, 10, 11]

kadbs_sip_event = 'set_a_kadbsi__140h_arm_6'
kadbs_tbc_event = 'set_a_kadbsi__140h_arm_7'
cdbs_sip_event = 'set_a_oldbs140_hz_arm_6'

symptom_mapping = {
    'did_have_any_feelings_of_Nausea': 'Nausea',
    'did_have_any_feelings_of_Pulling': 'Pulling',
    'did_have_any_feelings_of_Tingling': 'Tingling',
    'did_have_any_feelings_of_Dizziness': 'Dizziness',
    'did_have_any_feelings_of_Imbalance': 'Imbalance',
    'did_have_any_feelings_of_Other': 'Other',
    'did_have_any_feelings_of_Noneoftheabove': 'None'
}

colors = {
    "None": "#BDD9BF",
    "Imbalance": "#F39B53",
    "Dizziness": "#9B72CF",
    "Nausea": "#C4B454",
    "Pulling": "#E85D75",
    "Tingling": "#5BC0EB",
    "Other": "#A0A0A0",
}


def filter_data(data, pids, event_name):
    filtered_list = []
    for pid in pids:
        subset = data[(data['patientid'] == pid) & (data['redcap_event_name'] == event_name)]
        if len(subset) > 0:
            filtered_list.append(subset)
    if filtered_list:
        return pd.concat(filtered_list)
    return pd.DataFrame()


def calculate_percentages_by_occurrence(filtered_data):
    if len(filtered_data) == 0:
        return {label: 0.0 for label in symptom_mapping.values()}, {}

    counts = {}
    for col, label in symptom_mapping.items():
        if col in filtered_data.columns:
            counts[label] = int(filtered_data[col].sum())
        else:
            counts[label] = 0

    total = sum(counts.values())
    percentages = {}
    for label, count in counts.items():
        percentages[label] = (count / total) * 100 if total > 0 else 0.0

    return percentages, counts


def calculate_participant_counts(filtered_data):
    n_total = len(filtered_data)
    none_col = 'did_have_any_feelings_of_Noneoftheabove'
    n_none = int(filtered_data[none_col].sum()) if none_col in filtered_data.columns else 0
    n_any = n_total - n_none
    return n_total, n_none, n_any


filtered_arr = filter_data(data_sip, sip_pids, kadbs_sip_event)
filtered_fog = filter_data(data_tbc, tbc_pids, kadbs_tbc_event)
filtered_cdbs = filter_data(data_sip, sip_pids, cdbs_sip_event)

arr_pct, arr_counts = calculate_percentages_by_occurrence(filtered_arr)
fog_pct, fog_counts = calculate_percentages_by_occurrence(filtered_fog)
cdbs_pct, cdbs_counts = calculate_percentages_by_occurrence(filtered_cdbs)

arr_n, arr_none, _ = calculate_participant_counts(filtered_arr)
fog_n, fog_none, _ = calculate_participant_counts(filtered_fog)
cdbs_n, cdbs_none, _ = calculate_participant_counts(filtered_cdbs)

print(f"Arrhythmicity Model: {arr_none}/{arr_n} ({100*arr_none/arr_n:.1f}%) symptom-free")
print(f"P(FOG) Model: {fog_none}/{fog_n} ({100*fog_none/fog_n:.1f}%) symptom-free")
print(f"cDBS: {cdbs_none}/{cdbs_n} ({100*cdbs_none/cdbs_n:.1f}%) symptom-free")


def create_donut(ax, data, title):
    filtered = {k: v for k, v in data.items() if v > 0}
    if len(filtered) == 0:
        ax.text(0, 0, "No data", ha='center', va='center', fontsize=12)
        ax.set_aspect('equal')
        ax.axis('off')
        return

    sorted_keys = sorted(filtered.keys(),
                         key=lambda k: (0 if k == 'None' else 1, -filtered.get(k, 0)))
    sorted_values = [filtered[k] for k in sorted_keys]
    sorted_colors = [colors.get(k, '#CCCCCC') for k in sorted_keys]

    wedges, _ = ax.pie(
        sorted_values, labels=None, colors=sorted_colors,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
        startangle=90
    )

    centre = plt.Circle((0, 0), 0.45, fc='white')
    ax.add_patch(centre)

    none_pct = data.get('None', 0)
    ax.text(0, 0.05, f"{none_pct:.1f}%", ha='center', va='center',
            fontsize=14, fontweight='bold')
    ax.text(0, -0.17, "None", ha='center', va='center', fontsize=12)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=1)
    ax.set_aspect('equal')
    ax.axis('off')


fig, axes = plt.subplots(1, 3, figsize=(7.3, 3.2), gridspec_kw={'wspace': 0.05})
plt.tight_layout(rect=[0, 0.1, 1, 0.95])

create_donut(axes[0], arr_pct, "Arrhythmicity Model")
create_donut(axes[1], fog_pct, "P(FOG) Model")
create_donut(axes[2], cdbs_pct, "Clinical cDBS")

all_symptoms = set()
for d in [arr_pct, fog_pct, cdbs_pct]:
    all_symptoms.update([k for k, v in d.items() if v > 0])

legend_order = ['None']
for sym in ['Imbalance', 'Dizziness', 'Pulling', 'Nausea', 'Tingling', 'Other']:
    if sym in all_symptoms:
        legend_order.append(sym)

legend_elements = [plt.Rectangle((0, 0), 1, 1, fc=colors.get(s, '#CCCCCC'), edgecolor='none')
                   for s in legend_order]

fig.legend(legend_elements, legend_order, loc='lower center',
           ncol=len(legend_order), frameon=False,
           bbox_to_anchor=(0.5, 0.1), handlelength=1.0,
           handletextpad=0.4, columnspacing=1.0, fontsize=12)

plt.tight_layout(rect=[0, 0.12, 1, 1])

fig.savefig('figures/fig4_safety.png', dpi=900, bbox_inches='tight')
fig.savefig('figures/fig4_safety.pdf', dpi=900, bbox_inches='tight')
fig.savefig('figures/fig4_safety.svg', dpi=900, bbox_inches='tight')
plt.show()