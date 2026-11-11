"""Gambar tambahan untuk paper UOWC.

Semua angka berasal dari data simulasi yang tersimpan di data/ dan dari
generator kanal EGG milik cnn_ae_uowc.py.

Output:
  figs/fig10_skema_sistem.png
  figs/fig11_sintilasi_egg.png
  figs/fig12_foton_diterima.png
  figs/fig13_deviasi_model.png
"""

import csv
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, os.path.dirname(__file__))
from cnn_ae_uowc import sample_egg, egg_scintillation_index

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG, DAT = os.path.join(ROOT, "figs"), os.path.join(ROOT, "data")

plt.rcParams.update({"figure.dpi": 160, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.axisbelow": True,
                     "savefig.bbox": "tight"})


def rows(name):
    with open(os.path.join(DAT, name), newline="") as f:
        return list(csv.DictReader(f))


def box(ax, x, y, w, h, text, fc="#eef3fa", ec="#2b4a7a", fs=8.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, p1, p2, text="", style="-|>", ls="-", color="#1f3b6e", fs=7.5,
          dy=0.32):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=13,
                                 lw=1.3, color=color, linestyle=ls,
                                 shrinkA=2, shrinkB=2))
    if text:
        ax.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + dy, text,
                ha="center", va="bottom", fontsize=fs, color=color)


def fig_skema():
    fig, ax = plt.subplots(figsize=(6.8, 6.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.grid(False)

    ax.text(5, 9.55, "Skema sistem komunikasi optik nirkabel bawah air",
            ha="center", fontsize=9.5, weight="bold")

    # baris 1 - tautan fisik optik
    box(ax, 0.15, 7.35, 2.5, 1.35,
        "Pemancar (AUV)\nlaser 532 nm\n$\\theta_0$ = 1,75$^\\circ$")
    box(ax, 3.75, 7.35, 2.5, 1.35,
        "Kanal air\nabsorpsi $a(\\lambda)$\nhamburan $b(\\lambda)$\nturbulensi $\\sigma_I^2$")
    box(ax, 7.35, 7.35, 2.5, 1.35,
        "Penerima\naperture $D$ = 20 cm\nfotodioda")
    arrow(ax, (2.65, 8.05), (3.75, 8.05), "berkas melebar")
    arrow(ax, (6.25, 8.05), (7.35, 8.05), "foton terhambur\nmasuk aperture")

    # baris 2 - rantai CNN-AE
    box(ax, 0.15, 4.55, 2.3, 1.15, "bit masuk\n$k$ = 4 bit/simbol",
        fc="#f4f0fa", ec="#5a3b8a")
    box(ax, 2.85, 4.55, 2.2, 1.15, "Encoder CNN\n16 simbol (sigmoid)",
        fc="#f4f0fa", ec="#5a3b8a")
    box(ax, 5.45, 4.55, 2.2, 1.15, "Kanal fisik\nlapisan tak terlatih",
        fc="#f4f0fa", ec="#5a3b8a")
    box(ax, 8.05, 4.55, 1.85, 1.15, "Decoder CNN\n$\\hat{h}$ ikut masuk",
        fc="#f4f0fa", ec="#5a3b8a")
    arrow(ax, (2.45, 5.12), (2.85, 5.12), "", color="#5a3b8a")
    arrow(ax, (5.05, 5.12), (5.45, 5.12), "", color="#5a3b8a")
    arrow(ax, (7.65, 5.12), (8.05, 5.12), "", color="#5a3b8a")
    arrow(ax, (6.55, 4.55), (9.0, 4.55), "", color="#5a3b8a")
    ax.text(7.8, 4.72, "estimasi kanal $\\hat{h}$", ha="center", fontsize=7.5,
            color="#5a3b8a", style="italic")
    ax.text(5, 3.95, "Autoencoder end-to-end: encoder, kanal, dan decoder "
            "dilatih bersama", ha="center", fontsize=7.8,
            color="#5a3b8a")

    # baris 3 - jalur akustik cadangan
    box(ax, 0.15, 1.55, 9.4, 1.5,
        "Jalur cadangan akustik (OSPF cost 100): 2,4 kbps pada 2 km, "
        "latensi 1,33 s\nAktif otomatis ketika tautan optik padam "
        "(blackout konvergensi OSPF $\\approx$ 40 s)",
        fc="#fdf3e7", ec="#9a6b1f", fs=8.0)
    arrow(ax, (6.55, 8.7), (6.55, 6.05), "", color="#9a6b1f", ls="--")
    arrow(ax, (6.55, 6.05), (6.55, 3.05), "", color="#9a6b1f", ls="--")
    ax.text(6.75, 6.6, "pemicu peralihan", fontsize=7.5, color="#9a6b1f")

    fig.savefig(os.path.join(FIG, "fig10_skema_sistem.png"))
    plt.close(fig)


def fig_sintilasi():
    with open(os.path.join(DAT, "egg_params.csv"), newline="") as f:
        pars = list(csv.DictReader(f))
    rng = np.random.default_rng(5)
    n = 1200
    fig, axes = plt.subplots(4, 1, figsize=(8.5, 7.0),
                             gridspec_kw=dict(height_ratios=[1, 1, 1, 1.15]))
    for ax, p in zip(axes[:3], pars):
        par = dict(omega=float(p["omega"]), lam=float(p["lambda"]),
                   a=float(p["a"]), b=float(p["b"]), c=float(p["c"]))
        I = sample_egg(n, rng=rng, **par)
        ax.plot(np.arange(n), I, lw=0.7, color="#1f77b4")
        ax.set_ylabel("$I/I_0$")
        ax.set_title(f"Turbulensi {p['kondisi'].lower()} "
                     f"($\\sigma_I^2$ = {float(p['sigma_I2']):.2f})",
                     fontsize=8.5)
        ax.set_xlim(0, n)
    axes[2].set_xlabel("Indeks sampel (waktu)")

    ax = axes[3]
    for p in pars:
        par = dict(omega=float(p["omega"]), lam=float(p["lambda"]),
                   a=float(p["a"]), b=float(p["b"]), c=float(p["c"]))
        I = sample_egg(400_000, rng=np.random.default_rng(9), **par)
        h, edges = np.histogram(I, bins=140, range=(0, 4), density=True)
        ax.semilogy(0.5 * (edges[1:] + edges[:-1]), h, lw=1.3,
                    label=f"{p['kondisi']} ($\\sigma_I^2$ = "
                          f"{float(p['sigma_I2']):.2f})")
    ax.set_xlabel("Intensitas ternormalisasi $I/I_0$")
    ax.set_ylabel("Kerapatan peluang")
    ax.set_title("Sebaran intensitas EGG (400.000 sampel)", fontsize=8.5)
    ax.legend(fontsize=7.5)
    fig.savefig(os.path.join(FIG, "fig11_sintilasi_egg.png"))
    plt.close(fig)


def fig_foton():
    d = rows("attenuation_vs_distance.csv")
    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    for w, col in [("Pure sea", "#1f77b4"), ("Clear ocean", "#2ca02c"),
                   ("Coastal", "#d62728"), ("Harbor", "#7f4f24")]:
        pts = sorted([(float(r["Z_m"]), int(r["n_received"]))
                      for r in d if r["water"] == w])
        if not pts:
            continue
        z = [a for a, _ in pts]
        n = [max(b, 0.5) for _, b in pts]
        ax.semilogy(z, n, "o-", lw=1.4, ms=3.5, color=col, label=w)
    ax.axhline(50, color="k", ls="--", lw=1.0)
    ax.text(35, 62, "ambang statistik 50 foton", fontsize=7.5)
    ax.set_xlabel("Jarak $Z$ (m)")
    ax.set_ylabel("Jumlah foton diterima (dari 3x10$^5$ ditembakkan)")
    ax.set_title("Anggaran foton: penerimaan terhadap jarak dan tipe air")
    ax.legend(fontsize=8)
    fig.savefig(os.path.join(FIG, "fig12_foton_diterima.png"))
    plt.close(fig)


def fig_deviasi():
    d = rows("linkbudget_compare.csv")
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 4.4), sharey=True)
    for ax, w in zip(axes, ["Pure sea", "Clear ocean"]):
        mc = {float(r["Z_m"]): float(r["loss_db"])
              for r in d if r["water"] == w and r["model"] == "Monte Carlo"}
        for mdl, col, mk in [("Beer-Lambert", "#d62728", "o"),
                             ("BL+geometris", "#1f77b4", "s")]:
            mod = {float(r["Z_m"]): float(r["loss_db"])
                   for r in d if r["water"] == w and r["model"] == mdl}
            zs = sorted(k for k in mc if mc[k] > -200 and k in mod)
            ax.plot(zs, [mod[k] - mc[k] for k in zs], mk + "-", lw=1.4,
                    ms=4, color=col, label=mdl)
        ax.axhline(0, color="k", lw=0.9)
        ax.set_title(w, fontsize=9)
        ax.set_xlabel("Jarak $Z$ (m)")
    axes[0].set_ylabel("Selisih prediksi - Monte Carlo (dB)")
    axes[0].legend(fontsize=8, loc="lower right")
    fig.suptitle("Seberapa jauh rumus analitis menyimpang dari simulasi",
                 fontsize=9.5, y=1.0)
    fig.savefig(os.path.join(FIG, "fig13_deviasi_model.png"))
    plt.close(fig)


if __name__ == "__main__":
    fig_skema()
    fig_sintilasi()
    fig_foton()
    fig_deviasi()
    print("selesai: fig10, fig11, fig12, fig13")
