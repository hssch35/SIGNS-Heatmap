"""
Figure 1 – Ductus variant distribution across KBo 1.8++ (CTH 92)
Publication-ready export: fig1_schier.tif (600 dpi) + fig1_schier.eps (vector).

What the figure shows (matching the submitted caption):
  - Stacked bars per line: S=0 (bottom), S=1 (middle), S=2 (top)
  - Passage-zone shadings for Bentešina's Restoration and Binding Stipulations
    (not covered by caption → must stay in figure)
  - Section brackets below x-axis (referenced in caption as visual markers)
  - No title (supplied by caption)
  - Minimal colour key only (S-score labels defined in caption)
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import numpy as np
import re
from io import StringIO
from matplotlib.transforms import blended_transform_factory

CSV_FILE   = "/Users/hannahschier/SIGNS Heatmap/data/kbo_data.csv"
OUT_DIR    = "/Users/hannahschier/SIGNS Heatmap/results"
OUT_JPG    = os.path.join(OUT_DIR, "fig1_schier.jpg")
OUT_PNG    = os.path.join(OUT_DIR, "diplomatic_intensity.png")   # screen preview

COLORS = {0: '#2c7bb6', 1: '#fdae61', 2: '#d7191c'}

SECTIONS = [
    (1,  5,  'Preamble'),
    (5,  30, 'Historical Prologue'),
    (30, 90, 'Stipulations'),
]


# ── Parser ────────────────────────────────────────────────────────────────────
def parse_line_refs(refs_str):
    s = str(refs_str).lower().strip()
    if not s or s == 'nan' or s == 'passim':
        return []
    if 'notizen' in s or 'notes' in s:
        return []
    s = re.sub(r'\[(\d+)\]', r'\1', s)
    s = re.sub(r'\(\d+x\)', '', s)
    s = re.sub(r'\(over [^)]+\)', '', s)
    results = []
    current_rev = False
    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        if 'obv' in part:
            current_rev = False
        elif any(x in part for x in ['rev', 'rs', "'"]):
            current_rev = True
        for n in re.findall(r'\d+', part):
            results.append((int(n), current_rev))
    return results


# ── Section brackets (data-x / axes-y blended) ───────────────────────────────
def draw_section_brackets(ax, sections, y_frac=-0.17, tick_h=0.07):
    trans = blended_transform_factory(ax.transData, ax.transAxes)
    for x1, x2, label in sections:
        kw = dict(color='#444', lw=0.8, clip_on=False, transform=trans)
        ax.plot([x1, x2], [y_frac,          y_frac],          **kw)
        ax.plot([x1, x1], [y_frac,          y_frac + tick_h], **kw)
        ax.plot([x2, x2], [y_frac,          y_frac + tick_h], **kw)
        ax.text((x1 + x2) / 2, y_frac - 0.03, label,
                ha='center', va='top', fontsize=8, style='italic',
                clip_on=False, transform=trans, color='#444')


# ── Load & aggregate ──────────────────────────────────────────────────────────
with open(CSV_FILE, encoding='utf-8-sig') as f:
    clean_data = [
        line.strip().strip('"').replace('""""', '"').replace('""', '"')
        for line in f
    ]
df = pd.read_csv(StringIO('\n'.join(clean_data)), sep=';')
df.columns = [str(c).strip() for c in df.columns]
df[df.columns[0]] = df[df.columns[0]].ffill()

line_counts = {s: {} for s in [0, 1, 2]}
for _, row in df.iterrows():
    if pd.isna(row[df.columns[4]]):
        continue
    try:
        score = int(float(str(row[df.columns[4]]).strip()))
    except ValueError:
        continue
    if score not in [0, 1, 2]:
        continue
    for line_val, is_rev in parse_line_refs(str(row[df.columns[2]])):
        adj = line_val + 45 if is_rev else line_val
        if 1 <= adj <= 90:
            line_counts[score][adj] = line_counts[score].get(adj, 0) + 1

x = np.arange(1, 91)
c = {s: np.array([line_counts[s].get(l, 0) for l in x]) for s in [0, 1, 2]}


# ── Figure ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':    'serif',
    'font.size':      9,
    'axes.linewidth': 0.6,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
})

# Width ~17 cm (fits a full-page journal column); height proportioned for bars
fig, ax = plt.subplots(figsize=(6.7, 2.8))
fig.subplots_adjust(bottom=0.35, top=0.88, left=0.07, right=0.98)

# ── Stacked bars ──────────────────────────────────────────────────────────────
ax.bar(x, c[0],                   color=COLORS[0], width=1.0, linewidth=0, zorder=2)
ax.bar(x, c[1], bottom=c[0],      color=COLORS[1], width=1.0, linewidth=0, zorder=2)
ax.bar(x, c[2], bottom=c[0]+c[1], color=COLORS[2], width=1.0, linewidth=0, zorder=2)

# ── Obverse / reverse divider ─────────────────────────────────────────────────
ax.axvline(x=45.5, color='black', lw=1.4, zorder=5)

# ── Axes ──────────────────────────────────────────────────────────────────────
ax.set_xlim(0.5, 90.5)
ax.set_ylim(bottom=0)
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=4))
ax.set_ylabel('Variant types\nper line', fontsize=8.5, labelpad=4)
ax.grid(axis='y', linestyle=':', linewidth=0.5, color='#cccccc', zorder=0)
ax.tick_params(axis='both', length=3, labelsize=8)

ax.set_xticks([1, 15, 30, 45, 60, 75, 90])
ax.set_xticklabels(
    ['1', '15', '30', '45\n(Obv.)', '15\n(Rev.)', '30', '45'], fontsize=8)

# ── Section brackets ──────────────────────────────────────────────────────────
draw_section_brackets(ax, SECTIONS, y_frac=-0.27, tick_h=0.07)

# ── Minimal colour key (scores defined in caption; just swatches here) ────────
patches = [
    mpatches.Patch(facecolor=COLORS[0], label='S=0', linewidth=0),
    mpatches.Patch(facecolor=COLORS[1], label='S=1', linewidth=0),
    mpatches.Patch(facecolor=COLORS[2], label='S=2', linewidth=0),
]
ax.legend(
    handles=patches,
    loc='upper right',
    fontsize=7.5,
    frameon=True,
    edgecolor='#ccc',
    framealpha=1.0,
    ncol=3,
    handlelength=1.2,
    handleheight=0.9,
    borderpad=0.5,
    columnspacing=0.8,
    labelspacing=0.2,
)

# ── Export ────────────────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)

# 600-dpi JPG  (submitted file)
plt.savefig(OUT_JPG, dpi=600, bbox_inches='tight', format='jpeg', pil_kwargs={'quality': 95})
print(f"Saved (JPG 600 dpi):  {OUT_JPG}")

# 300-dpi PNG  (screen preview only — not for submission)
plt.savefig(OUT_PNG, dpi=300, bbox_inches='tight', format='png')
print(f"Saved (PNG preview):  {OUT_PNG}")


if __name__ == "__main__":
    pass
