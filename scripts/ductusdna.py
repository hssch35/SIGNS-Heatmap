import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os
import re

csv_path = "/Users/hannahschier/SIGNS Heatmap/data/kbo_data.csv"
output_path = "/Users/hannahschier/SIGNS Heatmap/results/ductus_dna_strip.png"

def generate_dna_manual_split():
    print("--- STARTING MANUAL SPLIT RECOVERY ---")
    
    data_points = []
    current_sign = ""

    try:
        with open(csv_path, 'r', encoding='latin1') as f:
            lines = f.readlines()
        
        print(f"Datei erfolgreich geöffnet. Verarbeite {len(lines)} Zeilen...")

        for i, line in enumerate(lines):
            
            if i == 0: continue
            
            
            parts = line.replace('"', '').split(';')
            
            
            if len(parts) < 5: continue
            
            
            if parts[0].strip():
                current_sign = parts[0].strip()
            
            
            try:
                score_str = parts[4].strip().replace(',', '.')
                if not score_str: continue
                score_val = int(float(score_str))
            except:
                continue

            
            beleg = parts[2].lower().strip()
            if not beleg or beleg == 'nan': continue
            
            line_numbers = re.findall(r'\d+', beleg)
            is_reverse = any(x in beleg for x in ['rev', 'rs', "'"])
            
            for num in line_numbers:
                line_val = int(num)
                
                if "1.8" in line and (line_val == 1 or line_val == 8):
                    continue
                
                if is_reverse:
                    line_val += 45
                
                data_points.append({'line': line_val, 'score': score_val})

    except Exception as e:
        print(f"Kritischer Fehler: {e}")
        return

    if not data_points:
        print("Immer noch keine Daten. Bitte prüfe, ob die Datei wirklich Semikolons enthält.")
        return

    print(f"ERFOLG! {len(data_points)} Datenpunkte extrahiert.")
    
    
    df_plot = pd.DataFrame(data_points)
    matrix = np.full((15, 92), np.nan)
    for l_num in range(1, 92):
        scores = df_plot[df_plot['line'] == l_num]['score'].values
        for j, s in enumerate(scores):
            if j < 15: matrix[j, l_num] = s

    fig, ax = plt.subplots(figsize=(18, 5))
    
    cmap = mcolors.ListedColormap(['#2c7bb6', '#fdae61', '#d7191c'])
    
    ax.imshow(matrix, aspect='auto', cmap=cmap, origin='lower')
    
    ax.set_title("Scribal Fingerprint: Ductus Distribution on KBo 1.8++", fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks([1, 15, 30, 45, 60, 75, 90])
    ax.set_xticklabels(['1', '15', '30', '45 (Obv)', '15 (Rev)', '30', '45'])
    ax.set_yticks([])
    ax.axvline(x=45.5, color='black', linewidth=3)
    
    
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color='#2c7bb6', lw=8, label='Hittite (0)'),
                    Line2D([0], [0], color='#fdae61', lw=8, label='Mixed (1)'),
                    Line2D([0], [0], color='#d7191c', lw=8, label='Assyro-Mittanian (2)')]
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"BILD ERSTELLT: {output_path}")
    plt.show()

if __name__ == "__main__":
    generate_dna_manual_split()