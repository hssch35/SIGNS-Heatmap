import pandas as pd
import matplotlib.pyplot as plt
import math
import re
from io import StringIO
from matplotlib.transforms import blended_transform_factory

# --- SETTINGS ---
CSV_FILE     = "/Users/hannahschier/SIGNS Heatmap/data/kbo_data.csv"
OUTPUT_IMAGE = "/Users/hannahschier/SIGNS Heatmap/results/kbo_heatmap_final.png"
PASSIM_VALUE = 10

COLORS = {0: '#2c7bb6', 1: '#fdae61', 2: '#d7191c'}
LABELS = {0: 'Hittite', 1: 'Ambivalent', 2: 'Assyro-Mittanian'}

# Section definitions: (x_start, x_end, label)
# obv. lines 1-45; rev. lines stored with +45 offset (46-90)
SECTIONS = [
    (1,  5,  'Preamble'),
    (5,  30, 'Historical Prologue'),
    (30, 90, 'Stipulations'),
]


def draw_section_brackets(ax, sections, y_frac=-0.14, tick_h=0.05):
    """Bracket annotations below the x-axis (blended data-x / axes-y transform)."""
    trans = blended_transform_factory(ax.transData, ax.transAxes)
    for x1, x2, label in sections:
        kw = dict(color='#222', lw=1.0, clip_on=False, transform=trans)
        ax.plot([x1, x2], [y_frac,          y_frac],          **kw)
        ax.plot([x1, x1], [y_frac,          y_frac + tick_h], **kw)
        ax.plot([x2, x2], [y_frac,          y_frac + tick_h], **kw)
        ax.text((x1 + x2) / 2, y_frac - 0.02, label,
                ha='center', va='top', fontsize=9, style='italic',
                clip_on=False, transform=trans, color='#222')


# --- LOAD & CLEAN DATA ---
with open(CSV_FILE, encoding='utf-8-sig') as f:
    clean_data = [
        line.strip().strip('"').replace('""""', '"').replace('""', '"')
        for line in f
    ]

df = pd.read_csv(StringIO('\n'.join(clean_data)), sep=';')
df.columns = [str(c).strip() for c in df.columns]
df[df.columns[0]] = df[df.columns[0]].ffill()

# --- BUILD PLOT & STAT ROWS ---
plot_rows = []
stat_rows = []

for _, row in df.iterrows():
    if pd.isna(row[df.columns[4]]):
        continue

    sign_name = str(row[df.columns[0]]).split('(')[0].strip()
    refs      = str(row[df.columns[2]]).lower()

    try:
        score = int(float(str(row[df.columns[4]]).strip()))
    except ValueError:
        continue

    is_reverse = any(x in refs for x in ['rev', 'rs', "'"])
    section    = 'Reverse' if is_reverse else 'Obverse'

    lines  = [int(n) for n in re.findall(r'\d+', refs)]
    weight = PASSIM_VALUE if 'passim' in refs else max(len(lines), 1)

    stat_rows.append({'Section': section, 'Score': score, 'Weight': weight})

    for line in lines:
        adj_line = line + 45 if (is_reverse and line <= 45) else line
        plot_rows.append({'Line': adj_line, 'Sign': sign_name, 'Score': score})

# --- ENTROPY STATISTICS ---
sdf = pd.DataFrame(stat_rows)
print('\n--- QUANTITATIVE RESULTS (Information Density) ---')
for section, group in sdf.groupby('Section'):
    total = group['Weight'].sum()
    probs = [group[group['Score'] == s]['Weight'].sum() / total for s in [0, 2]]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    print(f'{section:10} | H = {entropy:.3f} | Foreign share = {probs[1]:.3f}')

# --- VISUALISATION ---
plt.rcParams.update({
    'font.family':    'serif',
    'font.size':      11,
    'axes.linewidth': 0.8,
})

pdf = pd.DataFrame(plot_rows).sort_values('Sign', ascending=False)

fig, ax = plt.subplots(figsize=(14, 10))
fig.subplots_adjust(bottom=0.14, top=0.93, left=0.12, right=0.97)

for score in [0, 1, 2]:
    sub = pdf[pdf['Score'] == score]
    if not sub.empty:
        ax.scatter(sub['Line'], sub['Sign'],
                   c=COLORS[score], label=LABELS[score],
                   s=110, edgecolors='white', linewidths=0.5, alpha=0.85, zorder=3)

# Obverse / reverse dividing line
ax.axvline(x=45.5, color='black', linestyle='-', linewidth=1.5, alpha=0.6, zorder=2)

ax.set_title(
    'Ductus Variant Distribution in KBo 1.8++ (CTH 92)',
    fontsize=15, fontweight='bold', pad=10
)
ax.set_xlabel('Sequential Line  (Obverse 1–45 | Reverse 46+)', fontsize=11)
ax.set_ylabel('Sign', fontsize=11)

ax.legend(
    title='Ductus Type', title_fontsize=10,
    loc='upper right', fontsize=10,
    frameon=True, edgecolor='#aaa'
)
ax.grid(axis='x', linestyle=':', alpha=0.4, zorder=1)

# Section brackets below x-axis
draw_section_brackets(ax, SECTIONS)

plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
print(f'\nSaved: {OUTPUT_IMAGE}')
