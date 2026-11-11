"""
Runner: menghasilkan seluruh data & gambar kanal UOWC dari simulator Monte Carlo.

Output:
  data/attenuation_vs_distance.csv
  data/ir_water_types.csv
  data/ir_aperture.csv
  data/tau_summary.csv
  data/linkbudget_compare.csv
  figs/fig1_redaman_vs_jarak.png
  figs/fig2_impulse_response.png
  figs/fig3_aperture.png
  figs/fig4_tau_vs_jarak.png
  figs/fig5_linkbudget_3model.png
"""

import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from monte_carlo_uowc import (WATER_TYPES, simulate_channel,
                              beer_lambert_loss_db, geometric_loss_db)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figs")
DAT = os.path.join(ROOT, "data")
os.makedirs(FIG, exist_ok=True)
os.makedirs(DAT, exist_ok=True)

# Setelan global (dipakai konsisten di seluruh paper)
LAMBDA_NM = 532
BEAM_W = 3e-3
DIV_DEG = 1.75      # setengah sudut divergensi efektif (divalidasi ke Gabriel 2011)
FOV_DEG = 180.0
N_PHOTONS = 300_000

plt.rcParams.update({
    "figure.dpi": 160, "font.size": 9, "axes.grid": True,
    "grid.alpha": 0.3, "axes.axisbelow": True,
    "savefig.bbox": "tight",
})

COLORS = {"Pure sea": "#1f77b4", "Clear ocean": "#2ca02c",
          "Coastal": "#ff7f0e", "Harbor": "#d62728"}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ------------------------------------------------------------------ Fig 1
def fig1_redaman_vs_jarak():
    log("Fig 1: redaman vs jarak")
    rows = []
    dists = [5, 10, 20, 30, 40, 50, 60, 80, 100]
    for water in WATER_TYPES:
        for Z in dists:
            # harbor: redaman ekstrem, batasi jarak agar tidak menghabiskan waktu
            if water == "Harbor" and Z > 20:
                continue
            n = N_PHOTONS if Z <= 60 else 600_000
            r = simulate_channel(water, Z=Z, D=0.20, n_photons=n,
                                 beam_width=BEAM_W, divergence_deg=DIV_DEG,
                                 fov_deg=FOV_DEG, seed=7)
            rows.append(dict(water=water, Z_m=Z, n_photons=n,
                             loss_db=r["loss_db"], n_received=r["n_received"],
                             bl_db=beer_lambert_loss_db(water, Z)))
            log(f"   {water:12s} Z={Z:3d}m  MC={r['loss_db']:7.2f} dB "
                f"(Beer-Lambert {rows[-1]['bl_db']:7.2f})")

    with open(os.path.join(DAT, "attenuation_vs_distance.csv"), "w") as f:
        f.write("water,Z_m,n_photons,loss_mc_db,loss_beerlambert_db,n_received\n")
        for r in rows:
            f.write(f"{r['water']},{r['Z_m']},{r['n_photons']},"
                    f"{r['loss_db']:.3f},{r['bl_db']:.3f},{r['n_received']}\n")

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    # Sumbu-y dibatasi ke rentang fisik yang bermakna. Nilai sentinel
    # -300 dB (nol foton terdeteksi) sengaja tidak diplot supaya tidak
    # merusak skala grafik; jarak tanpanya dilaporkan di bawah grafik.
    ax.set_ylim(-105, 0)
    for water in WATER_TYPES:
        sub = [r for r in rows if r["water"] == water and r["n_received"] > 0]
        if not sub:
            continue
        z = [r["Z_m"] for r in sub]
        y = [r["loss_db"] for r in sub]
        ax.plot(z, y, "o-", ms=3.5, lw=1.6, color=COLORS[water],
                label=f"{water} (c = {WATER_TYPES[water]['c']:.3f} m$^{{-1}}$)")
    ax.axhline(-100, color="gray", ls=":", lw=1.2)
    ax.text(2, -97, "batas deteksi -100 dB", fontsize=7.5, color="gray")
    ax.set_xlabel("Jarak link Z (m)")
    ax.set_ylabel("Intensitas diterima (dB, relatif terhadap daya pancar)")
    ax.set_title(f"Redaman kanal UOWC vs jarak\n"
                 f"($\\lambda$ = {LAMBDA_NM} nm, aperture 20 cm, "
                 f"divergensi $\\theta_0$ = {DIV_DEG}$^\\circ$, Monte Carlo)")
    ax.set_ylim(-105, 0)
    ax.legend(fontsize=7.5, loc="lower left")
    # Titik dengan <10 foton terdeteksi adalah noise Monte Carlo (ketidakpastian
    # relatif 1/sqrt(N) sangat besar), bukan sinyal. Ditandai terpisah.
    noisy = [r for r in rows if 0 < r["n_received"] < 10]
    if noisy:
        ax.plot([r["Z_m"] for r in noisy], [r["loss_db"] for r in noisy],
                "x", ms=5, color="0.35", mew=1.2,
                label="noise MC (<10 foton)")
        ax.legend(fontsize=7.5, loc="lower left")
        n_zero = sum(1 for r in rows if r["n_received"] == 0)
        ax.text(0.985, 0.03,
                f"nol foton terdeteksi pada {n_zero} titik jarak "
                "(di bawah batas deteksi, tidak diplot)",
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=6.5, color="0.35", style="italic")
    fig.savefig(os.path.join(FIG, "fig1_redaman_vs_jarak.png"))
    plt.close(fig)
    return rows


# ------------------------------------------------------------------ Fig 2
def fig2_impulse_response():
    log("Fig 2: impulse response per tipe air")
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    summary = []
    for water in ["Pure sea", "Clear ocean", "Coastal"]:
        r = simulate_channel(water, Z=20, D=0.20, n_photons=N_PHOTONS,
                             beam_width=BEAM_W, divergence_deg=DIV_DEG,
                             fov_deg=FOV_DEG, seed=11, return_ir=True,
                             ir_bins=250, ir_span_ns=3.0)
        ax.plot(r["ir_time_ns"], r["ir_weight_db"], lw=1.7,
                color=COLORS[water],
                label=f"{water}  ($\\tau$ = {r['tau_ns']:.2f} ns)")
        summary.append(dict(water=water, tau_ns=r["tau_ns"],
                            loss_db=r["loss_db"]))
        np.savetxt(os.path.join(DAT, f"ir_{water.replace(' ', '_').lower()}.csv"),
                   np.c_[r["ir_time_ns"], r["ir_weight_db"]],
                   delimiter=",", header="t_rel_ns,weight_db", comments="")
    ax.set_xlim(-0.3, 3.0)
    ax.set_ylim(-45, 2)
    ax.set_xlabel("Waktu tiba relatif terhadap lintasan lurus (ns)")
    ax.set_ylabel("Intensitas ternormalisasi (dB)")
    ax.set_title("Channel impulse response pada Z = 20 m, aperture 20 cm")
    ax.legend(fontsize=8)
    fig.savefig(os.path.join(FIG, "fig2_impulse_response.png"))
    plt.close(fig)
    return summary


# ------------------------------------------------------------------ Fig 3
def fig3_aperture():
    log("Fig 3: pengaruh diameter aperture")
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    rows = []
    for D in [0.005, 0.05, 0.20, 0.50]:
        r = simulate_channel("Clear ocean", Z=20, D=D, n_photons=N_PHOTONS,
                             beam_width=BEAM_W, divergence_deg=DIV_DEG,
                             fov_deg=FOV_DEG, seed=13, return_ir=True,
                             ir_bins=250, ir_span_ns=3.0)
        ax.plot(r["ir_time_ns"], r["ir_weight_db"], lw=1.7,
                label=f"D = {D*100:.1f} cm  "
                      f"({r['loss_db']:.1f} dB, $\\tau$ = {r['tau_ns']:.2f} ns)")
        rows.append(dict(D_cm=D * 100, loss_db=r["loss_db"], tau_ns=r["tau_ns"]))
        log(f"   D={D*100:5.1f} cm  loss={r['loss_db']:7.2f} dB  tau={r['tau_ns']:.2f} ns")
    ax.set_xlim(-0.3, 3.0)
    ax.set_ylim(-45, 2)
    ax.set_xlabel("Waktu tiba relatif terhadap lintasan lurus (ns)")
    ax.set_ylabel("Intensitas ternormalisasi (dB)")
    ax.set_title("Impulse response vs diameter aperture\n"
                 "(clear ocean, Z = 20 m)")
    ax.legend(fontsize=7.5)
    fig.savefig(os.path.join(FIG, "fig3_aperture.png"))
    plt.close(fig)
    return rows


# ------------------------------------------------------------------ Fig 4
def fig4_tau():
    log("Fig 4: time dispersion vs jarak")
    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    for water in ["Pure sea", "Clear ocean", "Coastal"]:
        zs, taus = [], []
        for Z in [10, 20, 30, 50, 70, 100]:
            if water == "Coastal" and Z > 50:
                continue
            r = simulate_channel(water, Z=Z, D=0.20, n_photons=N_PHOTONS,
                                 beam_width=BEAM_W, divergence_deg=DIV_DEG,
                                 fov_deg=FOV_DEG, seed=17, return_ir=True,
                                 ir_bins=400, ir_span_ns=10.0)
            zs.append(Z)
            taus.append(r["tau_ns"])
        ax.plot(zs, taus, "s-", ms=4, lw=1.6, color=COLORS[water], label=water)
    # batas symbol duration untuk beberapa laju data
    for rate, ls in [(1e9, "--"), (100e6, ":")]:
        ax.axhline(1 / rate * 1e9, color="k", ls=ls, lw=1.1,
                   label=f"T$_{{sym}}$ @ {rate/1e6:.0f} Mbps = {1/rate*1e9:.1f} ns")
    ax.set_xlabel("Jarak link Z (m)")
    ax.set_ylabel("Time dispersion $\\tau$ (ns, lebar pada -20 dB)")
    ax.set_title("Dispersi waktu kanal vs jarak dan tipe air")
    ax.legend(fontsize=7.5)
    fig.savefig(os.path.join(FIG, "fig4_tau_vs_jarak.png"))
    plt.close(fig)


# ------------------------------------------------------------------ Fig 5
def fig5_linkbudget():
    log("Fig 5: perbandingan tiga model link budget")
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8))
    rows = []

    # (a) model sempit (tervalidasi): BL vs BL+geometris vs MC
    zero_mc = []
    for water in ["Pure sea", "Clear ocean"]:
        zs, mc, bl, blg = [], [], [], []
        for Z in [10, 20, 30, 50, 70, 100]:
            r = simulate_channel(water, Z=Z, D=0.20, n_photons=N_PHOTONS,
                                 beam_width=BEAM_W, divergence_deg=DIV_DEG,
                                 fov_deg=FOV_DEG, seed=23)
            zs.append(Z)
            # Nol foton terdeteksi = loss di bawah batas resolusi simulasi,
            # bukan angka -300 dB. Dicatat sebagai batas bawah, bukan titik.
            if r["n_received"] == 0:
                zero_mc.append(Z)
                mc.append(float("nan"))
            else:
                mc.append(r["loss_db"])
                rows.append(dict(water=water, Z_m=Z, model="Monte Carlo",
                                 loss_db=r["loss_db"]))
            bl.append(beer_lambert_loss_db(water, Z))
            blg.append(beer_lambert_loss_db(water, Z)
                       + geometric_loss_db(Z, 0.20, DIV_DEG))
            rows.append(dict(water=water, Z_m=Z, model="Beer-Lambert",
                             loss_db=bl[-1]))
            rows.append(dict(water=water, Z_m=Z, model="BL+geometris",
                             loss_db=blg[-1]))
        c = COLORS[water]
        axes[0].plot(zs, mc, "o-", color=c, lw=1.7, ms=4, label=f"MC, {water}")
        axes[0].plot(zs, blg, "--", color=c, lw=1.2, alpha=0.85,
                     label=f"BL+geometris, {water}")
        axes[0].plot(zs, bl, ":", color=c, lw=1.2, alpha=0.85,
                     label=f"Beer-Lambert saja, {water}")
    axes[0].set_xlabel("Jarak Z (m)")
    axes[0].set_ylabel("Rugi kanal (dB)")
    if zero_mc:
        axes[0].text(0.98, 0.03,
                     "nol foton pada Z = " + ", ".join(f"{z} m" for z in zero_mc)
                     + " (di bawah batas resolusi MC)",
                     transform=axes[0].transAxes, ha="right", va="bottom",
                     fontsize=6.0, color="0.35", style="italic")
    axes[0].set_title(f"(a) Berkas sempit $\\theta_0$ = {DIV_DEG}$^\\circ$\n"
                      "model analitis akurat", fontsize=8.5)
    axes[0].legend(fontsize=6.5, ncol=1)

    # (b) pengaruh divergensi berkas (harga desain)
    divs = [0.5, 1.0, 1.75, 3.0, 5.0, 10.0, 20.0]
    for water in ["Pure sea", "Clear ocean"]:
        ys = []
        for dv in divs:
            r = simulate_channel(water, Z=20, D=0.20, n_photons=N_PHOTONS,
                                 beam_width=BEAM_W, divergence_deg=dv,
                                 fov_deg=FOV_DEG, seed=29)
            ys.append(r["loss_db"])
        axes[1].plot(divs, ys, "o-", color=COLORS[water], lw=1.7, ms=4,
                     label=f"MC, {water}")
        axes[1].plot(divs, [beer_lambert_loss_db(water, 20)
                            + geometric_loss_db(20, 0.20, d) for d in divs],
                     "--", color=COLORS[water], lw=1.1, alpha=0.8,
                     label=f"BL+geometris, {water}")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Setengah sudut divergensi $\\theta_0$ (derajat)")
    axes[1].set_ylabel("Rugi kanal pada Z = 20 m (dB)")
    axes[1].set_title("(b) Pengaruh divergensi berkas\n"
                      "model analitis mulai menyimpang", fontsize=8.5)
    axes[1].legend(fontsize=6.5)
    fig.savefig(os.path.join(FIG, "fig5_linkbudget_3model.png"))
    plt.close(fig)

    with open(os.path.join(DAT, "linkbudget_compare.csv"), "w") as f:
        f.write("water,Z_m,model,loss_db\n")
        for r in rows:
            f.write(f"{r['water']},{r['Z_m']},{r['model']},{r['loss_db']:.3f}\n")
    return rows


if __name__ == "__main__":
    # CATATAN: fig2, fig3, fig4 dihasilkan oleh run_dispersion.py (RMS delay
    # spread). Script ini sengaja TIDAK menulisnya lagi supaya tidak menimpa
    # gambar dengan metrik lama (lebar pada -20 dB) yang tidak stabil.
    t0 = time.time()
    res = {}
    res["fig1"] = fig1_redaman_vs_jarak()
    res["fig5"] = fig5_linkbudget()
    with open(os.path.join(DAT, "summary.json"), "w") as f:
        json.dump(res, f, indent=2, default=float)
    log(f"selesai dalam {time.time()-t0:.1f} s")
