"""
Stylus inclination angle diagram for KBo 1.8++ (CTH 92)
Schematic showing the characteristic stylus angle relative to the clay surface
for each ductus tradition (S=0 Hittite, S=1 Ambivalent, S=2 Assyro-Mittanian).
After Cammarosano (2014) / Devecchi (2012b) palaeographic methodology.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

OUTPUT_IMAGE = "/Users/hannahschier/SIGNS Heatmap/results/stylus_inclination.png"

plt.rcParams.update({'font.family': 'serif', 'font.size': 11, 'axes.linewidth': 0.6})

fig, axes = plt.subplots(1, 3, figsize=(13, 5.5))
fig.subplots_adjust(left=0.04, right=0.96, bottom=0.10, top=0.87, wspace=0.35)

fig.suptitle(
    'Stylus Inclination Relative to Clay Surface in KBo 1.8++ (CTH 92)',
    fontsize=13, fontweight='bold', y=0.97
)

# Each panel: (score, angle_from_horizontal_degrees, color, title, description)
PANELS = [
    (0,  30, '#2c7bb6',
     'Hittite Ductus  (S=0)',
     'Low angle (~30°)\nShallow, broad impressions\nFlat triangular wedge-heads\n'
     '"Peculiar to late Hittite ductus"\n(Devecchi 2012b)'),
    (1,  45, '#fdae61',
     'Ambivalent  (S=1)',
     'Intermediate angle (~45°)\nShared by Hittite and\nnon-Hittite traditions\n'
     'Transitional / mixed forms'),
    (2,  65, '#d7191c',
     'Assyro-Mittanian  (S=2)',
     'Steep angle (~65°)\nDeep, narrow impressions\nBroken / angled wedge-heads\n'
     '"Surely non-Hittite"\n(Devecchi 2012b)'),
]

for ax, (score, angle_deg, color, title, desc) in zip(axes, PANELS):
    ax.set_xlim(-1.5, 2.8)
    ax.set_ylim(-0.5, 3.2)
    ax.set_aspect('equal')
    ax.axis('off')

    # Clay surface
    clay_y = 0.0
    ax.fill_between([-1.4, 2.7], [clay_y - 0.28, clay_y - 0.28],
                    [clay_y, clay_y], color='#c8a96e', zorder=1)
    ax.plot([-1.4, 2.7], [clay_y, clay_y], color='#8b6b30', lw=1.5, zorder=2)
    ax.text(0.6, clay_y - 0.42, 'clay surface',
            ha='center', va='top', fontsize=8.5, color='#8b6b30', style='italic')

    # Stylus body — drawn from tip (at origin) upward at given angle
    angle_rad = np.radians(angle_deg)
    length = 2.5
    tip_x, tip_y = 0.55, clay_y
    end_x = tip_x - length * np.cos(angle_rad)
    end_y = tip_y + length * np.sin(angle_rad)

    # Stylus shaft
    ax.plot([tip_x, end_x], [tip_y, end_y],
            color='#5a3a1a', lw=6, solid_capstyle='round', zorder=4)

    # Grip end (rounded cap)
    ax.plot(end_x, end_y, 'o', color='#5a3a1a', ms=10, zorder=5)

    # Tip wedge impression on clay
    wedge_w = 0.30 - score * 0.06   # wider for Hittite, narrower for AM
    wedge_d = 0.06 + score * 0.05   # deeper for AM
    wx = [tip_x - wedge_w / 2, tip_x, tip_x + wedge_w / 2]
    wy = [clay_y - 0.02, clay_y - wedge_d, clay_y - 0.02]
    ax.fill(wx, wy, color=color, zorder=3, alpha=0.9)

    # Angle arc
    arc_r = 0.55
    theta = np.linspace(0, angle_rad, 60)
    ax.plot(tip_x + arc_r * np.cos(theta),
            tip_y + arc_r * np.sin(theta),
            color='#444', lw=1.0, ls='--', zorder=6)
    ax.text(tip_x + arc_r * 0.72 + 0.05,
            tip_y + arc_r * 0.35,
            f'{angle_deg}°', fontsize=9, color='#444', ha='left')

    # Horizontal reference line (dashed)
    ax.plot([tip_x - 0.1, tip_x + arc_r + 0.2], [clay_y, clay_y],
            color='#aaa', lw=0.8, ls=':', zorder=3)

    # Title and description
    ax.set_title(title, fontsize=10.5, fontweight='bold', color=color, pad=6)
    ax.text(0.5, -0.04, desc,
            ha='center', va='top', fontsize=8.5, color='#333',
            transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#f9f9f9',
                      edgecolor=color, alpha=0.85, linewidth=0.8))

# Footnote
fig.text(0.5, 0.01,
         'After Cammarosano (2014) and Devecchi (2012b). '
         'Angles are schematic and indicative, not measured from photographs.',
         ha='center', va='bottom', fontsize=7.5, color='#666', style='italic')

plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
print(f"Saved: {OUTPUT_IMAGE}")

if __name__ == "__main__":
    pass
