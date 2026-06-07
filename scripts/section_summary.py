"""
Section-level ductus composition – KBo 1.8++ (CTH 92)
Horizontal stacked bar showing S=0/S=1/S=2 proportions for each text section
(Preamble, Historical Prologue, Stipulations) and for Obverse vs. Reverse.
The clearest single-argument figure for the paper.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import re
import math
from io import StringIO

CSV_FILE     = "/Users/hannahschier/SIGNS Heatmap/data/kbo_data.csv"
OUTPUT_IMAGE = "/Users/hannahschier/SIGNS Heatmap/results/section_summary.png"

PASSIM_VALUE = 10
COLORS = {0: '#2c7bb6', 1: '#fdae61', 2: '#d7191c'}
LABELS = {0: 'Hittite (S=0)', 1: 'Ambivalent (S=1)', 2: 'Assyro-Mittanian (S=2)'}

# Section assignment by adjusted line number
def line_to_section(adj_line):
    if 1 <= adj_line <= 5:
        return 'Preamble\n(obv. 1–5)'
    elif 6 <= adj_line <= 30:
        return 'Historical Prologue\n(obv. 6–30)'
    elif 31 <= adj_line <= 45:
        return 'Stipulations\n(obv. 31–45)'
    elif 46 <= adj_line <= 90:
        return 'Stipulations\n(rev. 1–45)'
    return None


# --- LOAD DATA ---
with open(CSV_FILE, encoding='utf-8-sig') as f:
    clean_data = [
        line.strip().strip('"').replace('""""', '"').replace('""', '"')
        for line in f
    ]
df = pd.read_csv(StringIO('\n'.join(clean_data)), sep=';')
df.columns = [str(c).strip() for c in df.columns]
df[df.columns[0]] = df[df.columns[0]].ffill()

# Accumulate weighted scores per section and per side
section_counts = {}  # {label: {0: n, 1: n, 2: n}}
side_counts     = {'Obverse\n(lines 1–45)': {0:0,1:0,2:0},
                   'Reverse\n(lines 46–90)': {0:0,1:0,2:0}}

for _, row in df.iterrows():
    if pd.isna(row[df.columns[4]]):
        continue
    refs = str(row[df.columns[2]]).lower()
    try:
        score = int(float(str(row[df.columns[4]]).strip()))
    except ValueError:
        continue
    if score not in [0, 1, 2]:
        continue

    is_reverse = any(x in refs for x in ['rev', 'rs', "'"])
    lines  = [int(n) for n in re.findall(r'\d+', refs)]
    weight = PASSIM_VALUE if 'passim' in refs else max(len(lines), 1)

    # Side counts use weight
    side_key = 'Reverse\n(lines 46–90)' if is_reverse else 'Obverse\n(lines 1–45)'
    side_counts[side_key][score] += weight

    # Section counts: if passim assign weight to each section proportionally
    if 'passim' in refs:
        for sec_label in [
            'Preamble\n(obv. 1–5)',
            'Historical Prologue\n(obv. 6–30)',
            'Stipulations\n(obv. 31–45)',
            'Stipulations\n(rev. 1–45)',
        ]:
            section_counts.setdefault(sec_label, {0:0,1:0,2:0})
            section_counts[sec_label][score] += PASSIM_VALUE / 4
    else:
        for line in lines:
            adj = line + 45 if (is_reverse and line <= 45) else line
            sec_label = line_to_section(adj)
            if sec_label:
                section_counts.setdefault(sec_label, {0:0,1:0,2:0})
                section_counts[sec_label][score] += 1

# --- FIGURE ---
plt.rcParams.update({'font.family': 'serif', 'font.size': 11, 'axes.linewidth': 0.7})

ORDER_SECTIONS = [
    'Preamble\n(obv. 1–5)',
    'Historical Prologue\n(obv. 6–30)',
    'Stipulations\n(obv. 31–45)',
    'Stipulations\n(rev. 1–45)',
]
ORDER_SIDES = ['Obverse\n(lines 1–45)', 'Reverse\n(lines 46–90)']

fig, (ax_sec, ax_side) = plt.subplots(
    1, 2, figsize=(14, 4.8),
    gridspec_kw={'width_ratios': [2, 1], 'wspace': 0.55}
)
fig.subplots_adjust(left=0.22, right=0.98, top=0.88, bottom=0.12)

fig.suptitle(
    'Ductus Composition by Text Section — KBo 1.8++ (CTH 92)',
    fontsize=12.5, fontweight='bold', y=0.97
)


def draw_horizontal_bars(ax, order, data_dict):
    y = np.arange(len(order))
    totals = [sum(data_dict.get(k, {s: 0 for s in [0,1,2]}).values()) for k in order]
    lefts  = np.zeros(len(order))

    for score in [0, 1, 2]:
        vals = np.array([
            data_dict.get(k, {0:0,1:0,2:0})[score] / max(t, 1)
            for k, t in zip(order, totals)
        ])
        bars = ax.barh(y, vals, left=lefts, color=COLORS[score],
                       height=0.55, label=LABELS[score], zorder=2)
        # Percentage labels inside bars (only if segment wide enough)
        for i, (val, left) in enumerate(zip(vals, lefts)):
            if val >= 0.06:
                ax.text(left + val / 2, i, f'{val*100:.0f}%',
                        ha='center', va='center', fontsize=8.5,
                        color='white', fontweight='bold')
        lefts += vals

    ax.set_yticks(y)
    ax.set_yticklabels(order, fontsize=10)
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{int(v*100)}%'))
    ax.set_xlabel('Proportion of attestations', fontsize=10)
    ax.grid(axis='x', linestyle=':', alpha=0.3, zorder=0)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Entropy annotation on the right
    for i, (k, t) in enumerate(zip(order, totals)):
        d = data_dict.get(k, {0:0,1:0,2:0})
        probs = [d[s] / max(t, 1) for s in [0, 2]]
        H = -sum(p * math.log2(p) for p in probs if p > 0)
        ax.text(1.02, i, f'H={H:.2f}', va='center', ha='left',
                fontsize=8, color='#555', transform=ax.get_yaxis_transform())


draw_horizontal_bars(ax_sec,  ORDER_SECTIONS, section_counts)
draw_horizontal_bars(ax_side, ORDER_SIDES,    side_counts)

ax_sec.set_title('By Text Section', fontsize=11, pad=6)
ax_side.set_title('By Tablet Side', fontsize=11, pad=6)

# Shared legend below
handles = [plt.Rectangle((0,0),1,1, color=COLORS[s]) for s in [0,1,2]]
fig.legend(handles, [LABELS[s] for s in [0,1,2]],
           loc='lower center', ncol=3, fontsize=9.5,
           frameon=True, edgecolor='#bbb',
           bbox_to_anchor=(0.5, -0.04))

plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
print(f"Saved: {OUTPUT_IMAGE}")

if __name__ == "__main__":
    pass
