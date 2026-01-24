import pandas as pd
import matplotlib.pyplot as plt
import re
from pathlib import Path
from typing import List, Dict, Tuple

class KBoAnalyzer:
    COLORS = {0: '#2c7bb6', 1: '#fdae61', 2: '#d7191c'}
    MARKERS = {0: 'o', 1: 's', 2: 'D'}
    LABELS = {
        0: 'Hethitisch (Score 0)',
        1: 'Hybrid (Score 1)',
        2: 'Assyro-Mittani (Score 2)'
    }
    OBVERSE_REVERSE_SPLIT = 45.5
        
    def __init__(self, file_path: str, output_path: str):
        self.file_path = Path(file_path)
        self.output_path = Path(output_path)
        self.df = None
        self.plot_data = []

    def load_data(self) -> bool:
        if not self.file_path.exists():
            return False
        try:
            self.df = pd.read_csv(
                self.file_path,
                sep=';',
                encoding='utf-8-sig',
                engine='python'
            )
            return True
        except:
            return False

    def clean_sign_name(self, raw_name: str) -> str:
        return re.sub(r'\s*\(\d+\)', '', str(raw_name)).strip()

    def parse_references(self, refs: str) -> Tuple[List[int], bool]:
        refs_lower = str(refs).lower()
        line_numbers = [int(n) for n in re.findall(r'\d+', refs_lower)]
        reverse_indicators = ['rev', 'rs', "'"]
        is_reverse = any(indicator in refs_lower for indicator in reverse_indicators)
        return line_numbers, is_reverse

    def process_data(self) -> None:
        if self.df is None:
            return
        
        self.df['Zeichen (Sign)'] = self.df['Zeichen (Sign)'].ffill()
        self.plot_data = []
        
        for _, row in self.df.iterrows():
            clean_name = self.clean_sign_name(row['Zeichen (Sign)'])
            refs = str(row['Belegstellen (KBo 1.8++)'])
            line_numbers, is_reverse = self.parse_references(refs)
            
            try:
                score = int(row['Score'])
            except:
                score = 0
                
            for line_num in line_numbers:
                if is_reverse and line_num <= 45:
                    line_num += 45
                
                self.plot_data.append({
                    'Line': line_num,
                    'Sign': clean_name,
                    'Score': score
                })

    def create_plot(self) -> None:
        if not self.plot_data:
            return

        pdf = pd.DataFrame(self.plot_data).sort_values('Sign', ascending=False)
        
        plt.figure(figsize=(20, 14))
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
        
        for score in [0, 1, 2]:
            subset = pdf[pdf['Score'] == score]
            if not subset.empty:
                plt.scatter(
                    subset['Line'],
                    subset['Sign'],
                    c=self.COLORS[score],
                    marker=self.MARKERS[score],
                    label=self.LABELS[score],
                    s=130,
                    edgecolors='white',
                    alpha=0.8,
                    zorder=3
                )

        plt.axvline(
            x=self.OBVERSE_REVERSE_SPLIT,
            color='black',
            linewidth=1.5,
            alpha=0.6,
            linestyle='--'
        )

        plt.text(22, -1.5, 'VORDERSEITE (Obv.)', ha='center', fontweight='bold', fontsize=13)
        plt.text(68, -1.5, 'RÜCKSEITE (Rev.)', ha='center', fontweight='bold', fontsize=13)

        plt.title('Paläographische Verteilung: Mixed Ductus in KBo 1.8++', size=20, pad=30, fontweight='bold')
        plt.xlabel('Zeilennummer (fortlaufend)', size=14, fontweight='bold')
        plt.ylabel('Keilschriftzeichen (Umschrift)', size=14, fontweight='bold')
        
        plt.xlim(0, 92)
        plt.xticks(range(0, 95, 5))
        plt.grid(True, axis='both', linestyle=':', alpha=0.3, zorder=1)
        plt.legend(loc='upper right', frameon=True, shadow=True, title="Paläographischer Typ", fontsize=11)
        
        plt.tight_layout()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(self.output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def run(self) -> bool:
        if not self.load_data():
            return False
        self.process_data()
        self.create_plot()
        return True

def main():
    file_path = "/Users/hannahschier/SIGNS Heatmap/data/kbo_data.csv"
    output_path = "/Users/hannahschier/SIGNS Heatmap/results/kbo_heatmap_final.png"
    
    analyzer = KBoAnalyzer(file_path, output_path)
    analyzer.run()

if __name__ == "__main__":
    main()