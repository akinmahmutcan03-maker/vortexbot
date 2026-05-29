import io
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_figure():
    style = random.choice(["bar", "radar", "scatter"])
    fig, ax = plt.subplots(figsize=(7, 5), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")

    for spine in ax.spines.values():
        spine.set_edgecolor("#7c3aed")

    ax.tick_params(colors="#e0e0e0")
    ax.xaxis.label.set_color("#e0e0e0")
    ax.yaxis.label.set_color("#e0e0e0")
    ax.title.set_color("#ffffff")

    if style == "bar":
        kategoriler = ["Hız", "Şut", "Pas", "Dribling", "Savunma", "Kondisyon"]
        degerler = [random.randint(55, 99) for _ in kategoriler]
        renkler = ["#7c3aed", "#a855f7", "#6d28d9", "#8b5cf6", "#5b21b6", "#9333ea"]
        bars = ax.bar(kategoriler, degerler, color=renkler, edgecolor="#2d2d5e", linewidth=0.8)
        for bar, val in zip(bars, degerler):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    str(val), ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')
        ax.set_ylim(0, 110)
        ax.set_title("⚡ VORTEX LEAGUE | Oyuncu Analizi", fontsize=13, fontweight='bold', pad=12)
        ax.set_ylabel("Puan")

    elif style == "scatter":
        x = [random.uniform(50, 99) for _ in range(20)]
        y = [random.uniform(50, 99) for _ in range(20)]
        boyutlar = [random.randint(80, 300) for _ in range(20)]
        sc = ax.scatter(x, y, s=boyutlar, c=boyutlar, cmap='plasma', alpha=0.8, edgecolors='white', linewidths=0.5)
        plt.colorbar(sc, ax=ax, label='Performans')
        ax.set_title("⚡ VORTEX LEAGUE | Performans Dağılımı", fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("Atak Puanı")
        ax.set_ylabel("Savunma Puanı")

    else:  # radar
        kategoriler = ["Hız", "Şut", "Pas", "Dribling", "Savunma", "Kondisyon"]
        N = len(kategoriler)
        degerler = [random.randint(55, 99) for _ in kategoriler]
        degerler += degerler[:1]
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        ax = plt.subplot(111, polar=True, facecolor="#16213e")
        ax.set_facecolor("#16213e")
        ax.plot(angles, degerler, 'o-', linewidth=2, color="#a855f7")
        ax.fill(angles, degerler, alpha=0.25, color="#7c3aed")
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(kategoriler, color='white', fontsize=9)
        ax.set_ylim(0, 100)
        ax.tick_params(colors='#a855f7')
        ax.spines['polar'].set_color('#7c3aed')
        ax.set_title("⚡ VORTEX LEAGUE | Radar Analizi", fontsize=13, fontweight='bold', pad=20, color='white')
        fig.patch.set_facecolor("#1a1a2e")

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close()
    return buf
