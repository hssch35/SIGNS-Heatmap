import pandas as pd
import matplotlib.pyplot as plt
import os
import re


base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base_path, 'data', 'kbo_data.csv')
text_path = os.path.join(base_path, 'data', 'transliteration.txt')
output_path = os.path.join(base_path, 'results', 'visual_strategy_kbo18.png')

def parse_transliteration(filepath):
    text_map = {}
    if not os.path.exists(filepath):
        print(f"Hinweis: Umschrift-Datei nicht gefunden unter {filepath}")
        return text_map
    pattern = re.compile(r'(Vs\.|Rs\.)\s*(\d+)')
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    side, num = match.group(1), int(match.group(2))
                    final_num = num + 45 if 'Rs' in side else num
                    text_map[final_num] = line.strip()
    except Exception as e:
        print(f"Fehler beim Lesen der Umschrift: {e}")
    return text_map

def run_analysis():
    print("Suche Datei...")
    if not os.path.exists(data_path):
        print(f"FEHLER: Datei nicht gefunden! Pfad: {data_path}")
        return

    
    try:
        
        df = pd.read_csv(data_path, sep=',', encoding='utf-8-sig')
        if df.shape[1] < 2: 
            df = pd.read_csv(data_path, sep=';', encoding='utf-8-sig')
    except:
        df = pd.read_csv(data_path, sep=';', encoding='latin-1')

    
    df['Zeichen (Sign)'] = df['Zeichen (Sign)'].ffill()
    
    trans_map = parse_transliteration(text_path)
    
    plot_data = []
    for _, row in df.iterrows():
        refs = str(row['Belegstellen (KBo 1.8++)'])
        if 'passim' in refs.lower() or pd.isna(refs): continue
        
        
        for part in refs.split(','):
            side_off = 45 if 'rev' in part.lower() or 'rs' in part.lower() else 0
            num_m = re.search(r'(\d+)', part)
            if num_m:
                ln = int(num_m.group(1)) + side_off
                plot_data.append({
                    'Line': ln,
                    'Sign': row['Zeichen (Sign)'],
                    'Score': int(row['Score']),
                    'Context': trans_map.get(ln, "")
                })

    if not plot_data:
        print("Keine plotbaren Daten gefunden. Prüfe die Spalte 'Belegstellen'.")
        return

    pdf = pd.DataFrame(plot_data)
    
    
    plt.figure(figsize=(14, 10))
    colors = {0: '#2c7bb6', 1: '#fdae61', 2: '#d7191c'}
    markers = {0: 'o', 1: 's', 2: 'D'}
    
    for score in sorted(pdf['Score'].unique()):
        sub = pdf[pdf['Score'] == score]
        plt.scatter(sub['Line'], sub['Sign'], c=colors[score], 
                    marker=markers[score], label=f'Score {score}', 
                    s=120, edgecolors='black', alpha=0.8)

    plt.axvline(x=45.5, color='black', linestyle='--', alpha=0.4)
    plt.title('KBo 1.8++: Verteilung palaeographischer Varianten', fontsize=14)
    plt.xlabel('Zeile (Vs. 1-45 | Rs. 1-45)')
    plt.ylabel('Keilschriftzeichen')
    plt.legend(title="Score (0=Heth, 2=Assyr-Mitt)")
    plt.grid(True, which='both', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"FERTIG! Das Bild liegt hier: {output_path}")

if __name__ == "__main__":
    run_analysis()