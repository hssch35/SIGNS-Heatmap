"""
Combined figure: Ductus DNA strip (top) + Diplomatic Intensity bars (bottom)
Two panels sharing the same x-axis, saved as a single publication figure.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as ticker
import numpy as np
import re
from io import StringIO
from matplotlib.lines import Line2D
from matplotlib.transforms import blended_transform_factory

CSV_FILE     = "/Users/hannahschier/SIGNS Heatmap/data/kbo_data.csv"
OUTPUT_IMAGE = "/Users/hannahschier/SIGNS Heatmap/results/combined_strip_intensity.png"

COLORS = {0: '#2c7bb6', 1: '#fdae61', 2: '#d7191c'}
LABELS_BAR  = {0: 'Hittite (S=0)', 1: 'Ambivalent (S=1)', 2: 'Assyro-Mittanian (S=2)'}
COLORS_LIST = ['#2c7bb6', '#fdae61', '#d7191c']
LABELS_LIST = ['Hittite (0)', 'Ambivalent (1)', 'Assyro-Mittanian (2)']

SECTIONS = [
    (1,  5,  'Preamble'),
    (5,  30, 'Historical Prologue'),
    (30, 90, 'Stipulations'),
]

ZONES = [
    (21, 30, "Bentešina's Restoration\n(obv. 21–30)"),
    (46, 80, "Binding Stipulations\n(rev. 1–35)"),
]

ERASURES_ALL = {4, 6, 7, 13, 21, 24, 28, 29, 30, 34}
ERASURES_S2  = {28, 29, 30, 34}


def draw_section_brackets(ax, sections, y_frac=-0.20, tick_h=0.07):
    trans = blended_transform_factory(ax.transData, ax.transAxes)
    for x1, x2, label in sections:
        kw = dict(color='#222', lw=1.0, clip_on=False, transform=trans)
        ax.plot([x1, x2], [y_frac,          y_frac],          **kw)
        ax.plot([x1, x1], [y_frac,          y_frac + tick_h], **kw)
        ax.plot([x2, x2], [y_frac,          y_frac + tick_h], **kw)
        ax.text((x1 + x2) / 2, y_frac - 0.03, label,
                ha='center', va='top', fontsize=8.5, style='italic',
                clip_on=False, transform=trans, color='#222')


# --- LOAD DATA ---
with open(CSV_FILE, encoding='utf-8-sig') as f:
    clean_data = [
        line.strip().strip('"').replace('""""', '"').replace('""', '"')
        for line in f
    ]
df = pd.read_csv(StringIO('\n'.join(clean_data)), sep=';')
df.columns = [str(c).strip() for c in df.columns]
df[df.columns[0]] = df[df.columns[0]].ffill()

# --- BUILD DNA MATRIX ---
dna_data = []
with open(CSV_FILE, 'r', encoding='latin1') as f:
    raw_lines = f.readlines()

for i, line in enumerate(raw_lines):
    if i == 0:
        continue
    parts = line.replace('"', '').split(';')
    if len(parts) < 5:
        continue
    try:
        score_str = parts[4].strip().replace(',', '.')
        if not score_str:
            continue
        score_val = int(float(score_str))
    except (ValueError, IndexError):
        continue
    beleg = parts[2].lower().strip()
    if not beleg or beleg == 'nan':
        continue
    line_numbers = re.findall(r'\d+', beleg)
    is_reverse   = any(x in beleg for x in ['rev', 'rs', "'"])
    for num in line_numbers:
        line_val = int(num)
        if 'kbo 1.8' in line.lower() and line_val in (1, 8):
            continue
        if is_reverse:
            line_val += 45
        dna_data.append({'line': line_val, 'score': score_val})

dna_df = pd.DataFrame(dna_data)
matrix = np.full((15, 92), np.nan)
for l_num in range(1, 92):
    scores = dna_df[dna_df['line'] == l_num]['score'].values
    for j, s in enumerate(scores[:15]):
        matrix[j, l_num] = s

# --- BUILD PER-LINE COUNTS FOR INTENSITY BARS ---
line_counts = {s: {} for s in [0, 1, 2]}
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
    lines = [int(n) for n in re.findall(r'\d+', refs)]
    for line in lines:
        adj = line + 45 if (is_reverse and line <= 45) else line
        if 1 <= adj <= 90:
            line_counts[score][adj] = line_counts[score].get(adj, 0) + 1

x = np.arange(1, 91)
c = {s: np.array([line_counts[s].get(l, 0) for l in x]) for s in [0, 1, 2]}
total = c[0] + c[1] + c[2]

# --- FIGURE: 2 rows ---
plt.rcParams.update({'font.family': 'serif', 'font.size': 11, 'axes.linewidth': 0.8})

fig, (ax_dna, ax_bar) = plt.subplots(
    2, 1, figsize=(18, 8.5),
    gridspec_kw={'height_ratios': [1, 2], 'hspace': 0.08}
)
fig.subplots_adjust(bottom=0.22, top=0.93, left=0.06, right=0.92)

# ---- TOP: DNA STRIP ----
cmap = mcolors.ListedColormap(COLORS_LIST)
norm = mcolors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)
ax_dna.imshow(matrix, aspect='auto', cmap=cmap, norm=norm, origin='lower')
ax_dna.axvline(x=45.5, color='black', linewidth=2.0, zorder=5)

# Diplomatic zone shading on DNA strip
trans_dna = blended_transform_factory(ax_dna.transData, ax_dna.transAxes)
for z1, z2, _ in ZONES:
    ax_dna.axvspan(z1 - 0.4, z2 + 0.4, alpha=0.12, color='#d7191c', zorder=0)

ax_dna.set_xticks([1, 15, 30, 45, 60, 75, 90])
ax_dna.set_xticklabels([])
ax_dna.set_yticks([])
ax_dna.set_xlim(0.5, 91.5)
ax_dna.tick_params(axis='x', length=0)
ax_dna.set_title(
    'Ductus Variant Distribution in KBo 1.8++ (CTH 92): Sign-by-Sign and Diplomatic Intensity',
    fontsize=12.5, fontweight='bold', pad=8
)

# DNA legend (top right)
legend_elements = [
    Line2D([0], [0], color=c, lw=7, label=l)
    for c, l in zip(COLORS_LIST, LABELS_LIST)
]
ax_dna.legend(
    handles=legend_elements,
    loc='upper right', ncol=3, fontsize=9,
    frameon=True, edgecolor='#aaa', handlelength=2.2,
)

# ---- BOTTOM: INTENSITY BARS ----
ax_bar.bar(x, c[0],                    color=COLORS[0], width=0.8, label=LABELS_BAR[0], zorder=2)
ax_bar.bar(x, c[1], bottom=c[0],       color=COLORS[1], width=0.8, label=LABELS_BAR[1], zorder=2)
ax_bar.bar(x, c[2], bottom=c[0]+c[1],  color=COLORS[2], width=0.8, label=LABELS_BAR[2], zorder=2)
ax_bar.set_ylim(bottom=0)

# Diplomatic zone shading on bar chart
trans_bar = blended_transform_factory(ax_bar.transData, ax_bar.transAxes)
for z1, z2, z_label in ZONES:
    ax_bar.axvspan(z1 - 0.4, z2 + 0.4, alpha=0.10, color='#d7191c', zorder=0)
    ax_bar.text((z1 + z2) / 2, 0.97, z_label,
                ha='center', va='top', fontsize=8, color='#8b0000', style='italic',
                transform=trans_bar, clip_on=False,
                bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                          edgecolor='#d7191c', alpha=0.85, linewidth=0.8))

# Rolling S=2 proportion on secondary y-axis
ax2 = ax_bar.twinx()
with np.errstate(divide='ignore', invalid='ignore'):
    prop = np.where(total > 0, c[2] / total.astype(float), np.nan)
prop_s = pd.Series(prop, index=x).rolling(5, center=True, min_periods=2).mean()
ax2.plot(x, prop_s, color='#8b0000', lw=1.8, ls='--', alpha=0.72,
         label='S=2 proportion (5-line rolling avg.)', zorder=3)
ax2.set_ylim(0, 1.05)
ax2.set_ylabel('S=2 proportion (5-line rolling avg.)', fontsize=9.5, color='#8b0000')
ax2.tick_params(axis='y', colors='#8b0000', labelsize=9)
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{int(v*100)}%'))
ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])

# Erasure markers
for e in sorted(ERASURES_ALL):
    marker = '▼' if e in ERASURES_S2 else '▽'
    color  = '#8b0000' if e in ERASURES_S2 else '#888'
    ax_bar.annotate(marker, xy=(e, 0), xytext=(e, -0.06),
                    xycoords='data', textcoords=trans_bar,
                    ha='center', va='top', fontsize=8.5,
                    color=color, clip_on=False, annotation_clip=False)

# Obv/rev divider on both panels
ax_bar.axvline(x=45.5, color='black', linewidth=2.0, zorder=4)

# Bar axis formatting
ax_bar.set_xlim(0.5, 90.5)
ax_bar.set_xticks([1, 15, 30, 45, 60, 75, 90])
ax_bar.set_xticklabels(['1', '15', '30', '45\n(Obv.)', '15\n(Rev.)', '30', '45'], fontsize=10)
ax_bar.set_ylabel('Sign attestations per line', fontsize=11)
ax_bar.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax_bar.tick_params(axis='both', length=4)
ax_bar.grid(axis='y', linestyle=':', alpha=0.35, zorder=0)

# Section brackets below bar chart
draw_section_brackets(ax_bar, SECTIONS, y_frac=-0.22, tick_h=0.08)

# Bar legend
h1, l1 = ax_bar.get_legend_handles_labels()
h2 = [plt.Line2D([0], [0], color='#8b0000', lw=1.8, ls='--')]
l2 = ['S=2 proportion (5-line avg.)']
ax_bar.legend(h1 + h2, l1 + l2, loc='upper left', fontsize=9,
              frameon=True, edgecolor='#aaa', ncol=2)

# Erasure footnote
fig.text(0.5, 0.002,
         '▼ Erasures within S=2 peak zone (obv. 28–34)    '
         '▽ Other erasures    — Erasure data: Devecchi (2012b, 53)',
         ha='center', va='bottom', fontsize=7.5, color='#555', style='italic')

plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
print(f"Saved: {OUTPUT_IMAGE}")

if __name__ == "__main__":
    pass
