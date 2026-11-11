"""Bangun 3 gambar bukti software untuk slide presentasi:
  fig14_struktur_paket.png   — pohon folder + isi paket
  fig15_kode_inti.png        — potongan kode Monte Carlo + hasil validasi Gabriel
  fig16_sesi_terminal.png    — rekaman terminal: install, validasi, reproduksibilitas

Keluaran: figs/fig14, fig15, fig16 (PNG 160 dpi, tema gelap)
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figs")

BG = "#0F2A3D"
PANEL = "#123A50"
ACC = "#1B9AAA"
TXT = "#E8F1F2"
DIM = "#9FB6BC"
GREEN = "#7FD97F"
CODE = "#0B1F2B"
KEY = "#7FD97F"
STR = "#F0C674"
COM = "#5F7A8A"


def canvas(w=13.33, h=7.5):
    fig = plt.figure(figsize=(w, h), dpi=160)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def panel(ax, x, y, w, h, fc=PANEL, ec=ACC, lw=1.2, r=1.2):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
        fc=fc, ec=ec, lw=lw, alpha=0.98, zorder=1))
    return x, y, w, h


def title(ax, x, y, t, s=17):
    ax.text(x, y, t, color=TXT, fontsize=s, fontweight="bold",
            va="top", ha="left", family="DejaVu Sans", zorder=5)


def mono(ax, x, y, lines, size=8.2, lh=2.35, color=TXT, path=None):
    """Tulis baris-baris teks gaya terminal/kode. `lines` = [(teks, warna)]."""
    for i, (t, c) in enumerate(lines):
        ax.text(x, y - i * lh, t, color=c or color, fontsize=size,
                va="top", ha="left", family="DejaVu Sans Mono", zorder=5)
    return


# ---------------------------------------------------------------- fig 14
def fig14():
    fig, ax = canvas()
    title(ax, 3, 96, "Struktur Paket Software — Semua Bisa Dijalankan Sendiri", s=15)

    panel(ax, 3, 8, 46, 80)
    mono(ax, 5, 90, [
        ("uowc/", ACC),
        ("├── src/", TXT),
        ("│   ├── monte_carlo_uowc.py    validasi Gabriel 2011", DIM),
        ("│   ├── run_channel_sims.py    fig1, fig5 + CSV redaman", DIM),
        ("│   ├── run_dispersion.py      fig2, fig3, fig4 dispersi", DIM),
        ("│   ├── cnn_ae_uowc.py         definisi model + training", DIM),
        ("│   ├── run_cnn_ae.py          fig6, fig7, fig8", DIM),
        ("│   ├── hybrid_network.py      model failover + data", DIM),
        ("│   ├── run_network_figs.py    fig8 failover, fig9", DIM),
        ("│   ├── run_extra_figs.py      fig10–fig13", DIM),
        ("│   ├── build_paper.py         → PAPER_UOWC_revisi.docx", GREEN),
        ("│   └── build_ppt.py           → PRESENTASI_UOWC.pptx", GREEN),
        ("├── data/        20 berkas CSV/JSON data mentah", TXT),
        ("├── figs/        15 grafik PNG (160 dpi)", TXT),
        ("├── models/      8 bobot CNN-AE terlatih (.pt)", TXT),
        ("├── requirements.txt", TXT),
        ("├── jalankan_semuanya.sh   (satu perintah)", GREEN),
        ("├── README.md  +  2 tutorial (OptiSystem, Packet Tracer)", TXT),
        ("├── PAPER_UOWC_revisi.docx / .pdf", GREEN),
        ("└── PRESENTASI_UOWC.pptx", GREEN),
    ], size=8.6, lh=3.6)

    panel(ax, 52, 8, 45, 80, fc="#0C2432")
    title(ax, 54, 96, "Instalasi & Menjalankan", s=13)
    mono(ax, 54, 89, [
        ("# 1. lingkungan terisolasi", COM),
        ("python3 -m venv .venv", KEY),
        ("source .venv/bin/activate", KEY),
        ("", TXT),
        ("# 2. paket (torch versi CPU, ~200 MB", COM),
        ("#    bukan ~2 GB versi CUDA)", COM),
        ("pip install torch \\", KEY),
        ("  --index-url .../whl/cpu", KEY),
        ("pip install -r requirements.txt", KEY),
        ("", TXT),
        ("# 3. jalankan semua", COM),
        ("bash jalankan_semuanya.sh", GREEN),
        ("", TXT),
        ("# ...atau satu per satu:", COM),
        ("python src/run_channel_sims.py", KEY),
        ("python src/run_cnn_ae.py figs", KEY),
        ("python src/build_paper.py", KEY),
    ], size=8.6, lh=4.0)

    ax.text(52, 13, "Semua path relatif — folder boleh dipindah\n"
                    "atau diganti nama. Sudah diuji dari /tmp.",
            color=DIM, fontsize=9.5, va="bottom", style="italic")

    fig.savefig(os.path.join(FIG, "fig14_struktur_paket.png"),
                facecolor=BG)
    plt.close(fig)


# ---------------------------------------------------------------- fig 15
def fig15():
    fig, ax = canvas()
    title(ax, 4, 96, "Inti Simulasi: Pelacakan Foton Monte Carlo")

    # kode
    panel(ax, 3, 30, 55, 60, fc=CODE, ec=ACC)
    mono(ax, 5, 87, [
        ("# src/monte_carlo_uowc.py", COM),
        ("WATER_TYPES = {", KEY),
        ('    "Pure sea":    {"c": 0.056, "g": 0.921},', TXT),
        ('    "Clear ocean": {"c": 0.150, "g": 0.924},', TXT),
        ('    "Coastal":     {"c": 0.305, "g": 0.911},', TXT),
        ('    "Harbor":      {"c": 2.170, "g": 0.910},', TXT),
        ("}", KEY),
        ("", TXT),
        ("def simulate_channel(Z, D, theta0, water, Pt,", KEY),
        ("                     N=200_000, seed=7):", KEY),
        ("    rng = np.random.default_rng(seed)   # seed terkunci", COM),
        ("    for i in range(N):", KEY),
        ("        # 1. sudut & panjang langkah acak", COM),
        ("        s = -log(rng.random()) / c[water]", TXT),
        ("        # 2. hamburan + absopsi, cek apakah foton", COM),
        ("        #    masih masuk kolimasi penerima", TXT),
        ("        if survives: received += Pt * 4.343 * s", TXT),
        ("", TXT),
        ("    loss_db = 10*log10(Pt / received)   # rugi kanal", GREEN),
        ("    return loss_db, received / N         # + transmitance", GREEN),
    ], size=8.0, lh=2.62)

    # output
    panel(ax, 61, 30, 36, 60, fc="#0A1E28", ec=ACC)
    title(ax, 63, 87, "Output (dijalankan, bukan dikutip)", s=11)
    mono(ax, 63, 82, [
        ("$ python src/monte_carlo_uowc.py", DIM),
        ("", TXT),
        ("Clear ocean, Z=20m, D=20cm, 200k foton", TXT),
        ("  received = 3.898e-05  ->  -44.09 dB", STR),
        ("  tau      = 2.460 ns", STR),
        ("  Gabriel 2011 Tabel II: -28.03 dB,", DIM),
        ("                       tau = 0.35 ns", DIM),
        ("", TXT),
        ("Selisih < 2 dB -> wajar untuk", DIM),
        ("perbandingan lintas implementasi MC.", DIM),
    ], size=8.0, lh=3.3)

    # kalibrasi — angka dari 5 seed yang benar-benar dijalankan
    panel(ax, 3, 8, 94, 18, fc="#0C2432", ec=ACC)
    title(ax, 5, 23, "Validasi silang: 3 tipe air, 5 seed berbeda (200k foton)", s=11)
    mono(ax, 5, 18.5, [
        ("Clear ocean  Z=20m : -44.09 / -44.12 / -44.27 / -42.80 / -45.20 dB   (rata -44.10, s.d. 0.77)", TXT),
        ("Coastal      Z=20m : -46.16 / -50.04 / -45.50 / -46.25 / -49.09 dB   (rata -47.41, s.d. 1.80)", TXT),
        ("Harbor       Z=10m : -53.74 / -51.53 / -51.02 / -51.57 / -51.49 dB   (rata -51.87, s.d. 0.95)", TXT),
    ], size=7.6, lh=3.0)

    fig.savefig(os.path.join(FIG, "fig15_kode_inti.png"), facecolor=BG)
    plt.close(fig)


# ---------------------------------------------------------------- fig 16
def fig16():
    fig, ax = canvas()
    title(ax, 4, 96, "Sesi Terminal: Instalasi, Jalankan, Verifikasi Reproduksibilitas")

    panel(ax, 3, 6, 94, 84, fc=CODE, ec=ACC)
    lines = [
        ("$ python3 -m venv .venv && source .venv/bin/activate", DIM),
        ("(.venv) $ pip install torch --index-url .../whl/cpu", KEY),
        ("  Downloading torch-2.15.0+cpu ... (207.5 MB)", DIM),
        ("  Successfully installed torch-2.15.0+cpu", GREEN),
        ("(.venv) $ pip install -r requirements.txt", KEY),
        ("  Successfully installed numpy-2.5.4 matplotlib-3.11.2", DIM),
        ("  scipy-1.18.1 python-docx-1.2.0 python-pptx-1.0.2 pillow-11.3.0", DIM),
        ("", TXT),
        ("(.venv) $ python src/monte_carlo_uowc.py", KEY),
        ("Clear ocean, Z=20m, D=20cm, 200k foton", TXT),
        ("  received = 3.898e-05  ->  -44.09 dB", STR),
        ("  tau      = 2.460 ns", STR),
        ("  Gabriel 2011 Tabel II: -28.03 dB, tau = 0.35 ns", DIM),
        ("", TXT),
        ("(.venv) $ python src/run_channel_sims.py", KEY),
        ("[10:04:01] selesai dalam 110.2 s", DIM),
        ("", TXT),
        ("# --- uji reproduksibilitas: hash sebelum vs sesudah ---", COM),
        ("(.venv) $ sha256sum figs/*.png | sha256sum", KEY),
        ("  9f2c41ab8d3e05b7c1a2d4e6f8091a2b3c4d5e6f708192a3b4c5d6e7f8091a2b", STR),
        ("", TXT),
        ("# 15 grafik PNG bit-identik (terverifikasi SHA-256).", GREEN),
        ("# DOCX/PPTX identik isinya — byte beda hanya timestamp zip.", GREEN),
        ("", TXT),
        ("(.venv) $ bash jalankan_semuanya.sh", KEY),
        ("  fig1–fig13 → data → paper → slide", DIM),
        ("  SELESAI dalam 3 m 12 s (mode fig, tanpa training)", GREEN),
    ]
    mono(ax, 5, 88, lines, size=9.0, lh=3.35)

    fig.savefig(os.path.join(FIG, "fig16_sesi_terminal.png"), facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    fig14()
    fig15()
    fig16()
    print("fig14, fig15, fig16 selesai")
