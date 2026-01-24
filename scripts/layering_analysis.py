import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from pathlib import Path

class RedactionalLayeringAnalyzer:
    def __init__(self, file_path: str, output_path: str):
        self.file_path = Path(file_path)
        self.output_path = Path(output_path)

    def run_layering_analysis(self):

        df = pd.read_csv(self.file_path, sep=';', encoding='utf-8-sig', engine='python')
        df['Zeichen (Sign)'] = df['Zeichen (Sign)'].ffill()
        
        plot_data = []
        for _, row in df.iterrows():
            refs = str(row['Belegstellen (KBo 1.8++)']).lower()
            nums = re.findall(r'\d+', refs)
            is_rev = any(idx in refs for idx in ['rev', 'rs', "'"])
            
            for n in nums:
                line = int(n)
                if is_rev and line <= 45: line += 45
                plot_data.append({'Line': line, 'Score': int(row['Score'])})

        pdf = pd.DataFrame(plot_data)

        density = []
        for i in range(1, 91):
            window = pdf[(pdf['Line'] >= i-3) & (pdf['Line'] <= i+3)]
            if not window.empty:
                
                var_score = window['Score'].nunique() 
                density.append(var_score)
            else:
                density.append(0)

        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12), 
                                        gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
        
        
        colors = {0: '#2c7bb6', 1: '#fdae61', 2: '#d7191c'}
        labels = {0: 'Hittite', 1: 'Hybrid', 2: 'Assyro-Mittani'}
        
        for s in [0, 1, 2]:
            sub = pdf[pdf['Score'] == s]
            ax1.scatter(sub['Line'], sub['Score'], c=colors[s], s=120, 
                        label=labels[s], alpha=0.6, edgecolors='w')
        
        ax1.set_title("Redactional Layering Index: KBo 1.8++", size=22, pad=20, fontweight='bold')
        ax1.set_ylabel("Ductus Score", fontsize=14)
        ax1.axvline(45.5, color='black', linewidth=2, linestyle='--')
        ax1.legend(loc='upper right')


        density_array = np.array(density).reshape(1, -1)
        im = ax2.imshow(density_array, aspect='auto', cmap='Reds', extent=[0, 90, 0, 1])
        
        ax2.set_yticks([])
        ax2.set_xlabel("Line Number (1-45: Obv | 46-90: Rev)", fontsize=14)
        
        
        cbar = plt.colorbar(im, ax=ax2, orientation='horizontal', pad=0.4)
        cbar.set_label('Ductus Complexity (Unique styles per 7-line window)', size=12)

        plt.tight_layout()
        plt.savefig(self.output_path, dpi=300)
        print(f"Layering Analysis successfully saved: {self.output_path}")

if __name__ == "__main__":
    analyzer = RedactionalLayeringAnalyzer(
        "/Users/hannahschier/SIGNS Heatmap/data/kbo_data.csv",
        "/Users/hannahschier/SIGNS Heatmap/results/layering_analysis.png"
    )
    analyzer.run_layering_analysis()