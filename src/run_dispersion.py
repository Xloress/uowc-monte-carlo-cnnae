"""
Runner dispersi waktu: RMS delay spread vs tipe air, aperture, dan jarak.

Menghasilkan:
  data/dispersion.csv
  figs/fig4_dispersi.png      (tau_rms vs jarak, dibanding durasi simbol)
  figs/fig3_aperture.png      (IR vs diameter aperture)
"""

import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from monte_carlo_uowc import (WATER_TYPES, simulate_channel,
                              rms_delay_spread_ns, tau_ns)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG, DAT = os.path.join(ROOT, "figs"), os.path.join(ROOT, "data")

plt.rcParams.update({"figure.dpi": 160, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.axisbelow": True,
                     "savefig.bbox": "tight"})

N = 800_000
DIV = 1.75
COLORS = {"Pure sea": "#1f77b4", "Clear ocean": "#2ca02c",
          "Coastal": "#ff7f0e", "Harbor": "#d62728"}


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def run(water, Z, D=0.20, seeds=(1, 2)):
    """Rata-rata RMS delay spread dan rugi dari beberapa seed."""
    taus, losses, ir = [], [], None
    for s in seeds:
        r = simulate_channel(water, Z=Z, D=D, n_photons=N,
                             divergence_deg=DIV, seed=s, return_ir=True,
                             ir_bins=400, ir_span_ns=5.0)
        if r["n_received"] < 50:
            return None
        taus.append(rms_delay_spread_ns(r["t_arrival"], r["w_arrival"], Z))
        losses.append(r["loss_db"])
        if ir is None:
            ir = r
    return dict(water=water, Z=Z, D=D,
                tau_rms=float(np.mean(taus)), tau_std=float(np.std(taus)),
                loss_db=float(np.mean(losses)), ir=ir)


def fig_dispersion():
    log("dispersi: tau_rms vs jarak")
    rows = []
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    for water in ["Pure sea", "Clear ocean", "Coastal"]:
        zs, ts, es = [], [], []
        for Z in [10, 20, 30, 40, 50]:
            r = run(water, Z)
            if r is None:
                continue
            zs.append(Z)
            ts.append(r["tau_rms"])
            es.append(r["tau_std"])
            rows.append(dict(water=water, Z=Z, D_cm=20, tau_rms_ns=r["tau_rms"],
                             tau_std_ns=r["tau_std"], loss_db=r["loss_db"]))
            log(f"   {water:12s} Z={Z:3d}m  tau_rms={r['tau_rms']:.3f} ns")
        if zs:
            ax.errorbar(zs, ts, yerr=es, fmt="s-", ms=4, lw=1.6,
                        color=COLORS[water], label=water, capsize=2.5)
    for rate, ls in [(1e9, "--"), (100e6, ":")]:
        ax.axhline(0.1 / rate * 1e9, color="k", ls=ls, lw=1.1,
                   label=f"0,1$\\cdot$T$_{{sym}}$ @ {rate/1e6:.0f} Mbps")
    ax.set_xlabel("Jarak link Z (m)")
    ax.set_ylabel("RMS delay spread $\\tau_{rms}$ (ns)")
    ax.set_title("Dispersi waktu kanal (aperture 20 cm)")
    ax.legend(fontsize=7.5)
    fig.savefig(os.path.join(FIG, "fig4_dispersi.png"))
    plt.close(fig)

    with open(os.path.join(DAT, "dispersion.csv"), "w") as f:
        f.write("water,Z_m,D_cm,tau_rms_ns,tau_std_ns,loss_db\n")
        for r in rows:
            f.write(f"{r['water']},{r['Z']},{r['D_cm']},{r['tau_rms_ns']:.4f},"
                    f"{r['tau_std_ns']:.4f},{r['loss_db']:.3f}\n")
    return rows


def fig_aperture():
    log("aperture: IR vs diameter")
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    rows = []
    for D in [0.005, 0.05, 0.20, 0.50]:
        r = run("Clear ocean", 20, D=D, seeds=(1,))
        if r is None:
            log(f"   D={D*100:.1f} cm: foton terlalu sedikit, dilewati")
            continue
        ir = r["ir"]
        ax.plot(ir["ir_time_ns"], ir["ir_weight_db"], lw=1.6,
                label=f"D = {D*100:.1f} cm  ({r['loss_db']:.1f} dB, "
                      f"$\\tau_{{rms}}$ = {r['tau_rms']:.2f} ns)")
        rows.append(dict(D_cm=D * 100, loss_db=r["loss_db"],
                         tau_rms_ns=r["tau_rms"]))
        log(f"   D={D*100:5.1f} cm  loss={r['loss_db']:7.2f} dB  "
            f"tau_rms={r['tau_rms']:.3f} ns")
    ax.set_xlim(-0.3, 3.0)
    ax.set_ylim(-40, 2)
    ax.set_xlabel("Waktu tiba relatif terhadap lintasan lurus (ns)")
    ax.set_ylabel("Intensitas ternormalisasi (dB)")
    ax.set_title("Impulse response vs diameter aperture\n(clear ocean, Z = 20 m)")
    ax.legend(fontsize=7.5)
    fig.savefig(os.path.join(FIG, "fig3_aperture.png"))
    plt.close(fig)
    return rows


def fig_ir_water():
    log("impulse response per tipe air")
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    rows = []
    for water in ["Pure sea", "Clear ocean", "Coastal"]:
        # seeds harus sama dengan fig_dispersion() agar nilai tau_rms di legenda
        # identik dengan tabel di paper (rata-rata 2 seed, bukan 1 seed).
        r = run(water, 20)
        if r is None:
            continue
        ir = r["ir"]
        ax.plot(ir["ir_time_ns"], ir["ir_weight_db"], lw=1.7,
                color=COLORS[water],
                label=f"{water}  ($\\tau_{{rms}}$ = {r['tau_rms']:.2f} ns)")
        rows.append(dict(water=water, tau_rms_ns=r["tau_rms"],
                         loss_db=r["loss_db"]))
    ax.set_xlim(-0.3, 3.0)
    ax.set_ylim(-40, 2)
    ax.set_xlabel("Waktu tiba relatif terhadap lintasan lurus (ns)")
    ax.set_ylabel("Intensitas ternormalisasi (dB)")
    ax.set_title("Channel impulse response pada Z = 20 m, aperture 20 cm")
    ax.legend(fontsize=8)
    fig.savefig(os.path.join(FIG, "fig2_impulse_response.png"))
    plt.close(fig)
    return rows


if __name__ == "__main__":
    rows = fig_dispersion()
    ap = fig_aperture()
    ir = fig_ir_water()
    import json
    with open(os.path.join(DAT, "dispersion_summary.json"), "w") as f:
        json.dump(dict(sweep=rows, aperture=ap, ir=ir), f, indent=1)
    log("selesai")
