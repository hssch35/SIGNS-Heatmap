"""
Ductus DNA Strip – KBo 1.8++ (CTH 92)
Each column = one line (obv. 1–45, rev. 46–90).
Each row slot = one sign attestation, sorted score-descending so S=2 stacks
at the top — making high-intensity lines visually prominent.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import re
import os
from matplotlib.lines import Line2D
from matplotlib.transforms import blended_transform_factory

csv_path    = "/Users/hannahschier/SIGNS Heatmap/data/kbo_data.csv"
output_path = "/Users/hannahschier/SIGNS Heatmap/results/ductus_dna_strip.png"

SECTIONS = [
    (1,  5,  'Preamble'),
    (5,  30, 'Historical Prologue'),
    (30, 90, 'Stipulations'),
]
COLORS = ['#2c7bb6', '#fdae61', '#d7191c']
LABELS = ['Hittite (S=0)', 'Ambivalent (S=1)', 'Assyro-Mittanian (S=2)']


# ── Fixed line-reference parser ───────────────────────────────────────────────
def parse_line_refs(refs_str):
    """
    Returns list of (line_int, is_reverse) tuples.
    Handles: mixed obv./rev. in one cell, (2x) notation, [3]4 bracketing,
    non-line references like (Notizen S. 52), and passim (returns []).
    """
    s = str(refs_str).lower().strip()
    if not s or s in ('nan',) or 'passim' == s:
        return []
    if 'notizen' in s or 'notes' in s:
        return []
    # Reconstruct bracketed damaged digits: [3]4 → 34
    s = re.sub(r'\[(\d+)\]', r'\1', s)
    # Remove multiplier notation: (2x), (3x)
    s = re.sub(r'\(\d+x\)', '', s)
    # Remove parenthetical annotations that aren't line numbers
    s = re.sub(r'\(over [^)]+\)', '', s)

    results = []
    current_rev = False

    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        # Update side context from explicit markers in this part
        if 'obv' in part:
            current_rev = False
        elif any(x in part for x in ['rev', 'rs', "'"]):
            current_rev = True
        # No marker → inherit current_rev (continuation of same side)

        for n in re.findall(r'\d+', part):
            results.append((int(n), current_rev))

    return results


# ── Load data ─────────────────────────────────────────────────────────────────
def load_data():
    data_points = []
    with open(csv_path, 'r', encoding='latin1') as f:
        raw = f.readlines()

    for i, line in enumerate(raw):
        if i == 0:
            continue
        parts = line.replace('"', '').split(';')
        if len(parts) < 5:
            continue
        try:
            score_val = int(float(parts[4].strip().replace(',', '.')))
        except (ValueError, IndexError):
            continue

        beleg = parts[2].strip()
        refs  = parse_line_refs(beleg)
        for line_val, is_rev in refs:
            # Skip KBo 1.8 tablet reference numbers (1 and 8 in source identifier)
            raw_lower = line.lower()
            if 'kbo 1.8' in raw_lower and line_val in (1, 8) and not is_rev:
                continue
            adj = line_val + 45 if is_rev else line_val
            if 1 <= adj <= 90:
                data_points.append({'line': adj, 'score': score_val})

    return pd.DataFrame(data_points)


# ── Build matrix: sort scores descending within each column ───────────────────
def build_matrix(df, n_rows=18):
    matrix = np.full((n_rows, 91), np.nan)
    for col in range(1, 91):
        scores = sorted(df[df['line'] == col]['score'].values, reverse=True)
        for row, s in enumerate(scores[:n_rows]):
            matrix[row, col] = s
    return matrix


def draw_section_brackets(ax, sections, y_frac=-0.22, tick_h=0.08):
    trans = blended_transform_factory(ax.transData, ax.transAxes)
    for x1, x2, label in sections:
        kw = dict(color='#333', lw=0.9, clip_on=False, transform=trans)
        ax.plot([x1, x2], [y_frac,          y_frac],          **kw)
        ax.plot([x1, x1], [y_frac,          y_frac + tick_h], **kw)
        ax.plot([x2, x2], [y_frac,          y_frac + tick_h], **kw)
        ax.text((x1 + x2) / 2, y_frac - 0.04, label,
                ha='center', va='top', fontsize=9, style='italic',
                clip_on=False, transform=trans, color='#333')


def main():
    df     = load_data()
    matrix = build_matrix(df)

    plt.rcParams.update({
        'font.family':    'serif',
        'font.size':      11,
        'axes.linewidth': 0.7,
    })

    fig, ax = plt.subplots(figsize=(18, 4.2))
    fig.subplots_adjust(bottom=0.32, top=0.88, left=0.03, right=0.97)

    cmap = mcolors.ListedColormap(['white'] + COLORS)  # NaN → white via set_bad
    norm = mcolors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5], 3)

    # Build a masked array so NaN cells are truly white
    masked = np.ma.masked_invalid(matrix)
    cmap_plot = mcolors.ListedColormap(COLORS)
    cmap_plot.set_bad(color='#f5f5f5')  # light gray for empty slots
    ax.imshow(masked, aspect='auto', cmap=cmap_plot, norm=norm,
              origin='lower', interpolation='nearest')

    # Thin horizontal rules separating rows (help readability)
    for row in range(1, matrix.shape[0]):
        ax.axhline(row - 0.5, color='white', lw=0.4, zorder=3)

    # Obverse / reverse divider
    ax.axvline(x=45.5, color='black', linewidth=2.0, zorder=5)

    # Axis formatting
    ax.set_xticks([1, 15, 30, 45, 60, 75, 90])
    ax.set_xticklabels(
        ['1', '15', '30', '45\n(Obv.)', '15\n(Rev.)', '30', '45'],
        fontsize=10
    )
    ax.set_yticks([])
    ax.set_xlim(0.5, 90.5)
    ax.tick_params(axis='x', length=4)

    ax.set_title(
        'Ductus Variant Distribution in KBo 1.8++ (CTH 92)',
        fontsize=13, fontweight='bold', pad=8
    )

    draw_section_brackets(ax, SECTIONS)

    legend_elements = [
        Line2D([0], [0], color=c, lw=7, label=l)
        for c, l in zip(COLORS, LABELS)
    ]
    ax.legend(
        handles=legend_elements,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.52),
        ncol=3, fontsize=10,
        frameon=True, edgecolor='#bbb', handlelength=2.5,
    )

    # Small note about sort order
    ax.text(0.98, 0.97,
            'Within each line: S=2 stacked top, S=0 bottom',
            ha='right', va='top', fontsize=7.5, color='#777', style='italic',
            transform=ax.transAxes)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
