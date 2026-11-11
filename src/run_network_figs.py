"""
Gambar untuk bagian integrasi jaringan hibrida akustik-optik.

Output:
  figs/fig8_failover_timeline.png
  figs/fig9_throughput_latensi.png
"""

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from hybrid_network import (simulate_failover, sweep_distance, OPT_BUDGET_DB,
                            OSPF_CONVERGENCE_S, OPT_CAPACITY_BPS,
                            ACO_CAPACITY_BPS, ACO_CAPACITY_LOW_BPS)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG, DAT = os.path.join(ROOT, "figs"), os.path.join(ROOT, "data")

plt.rcParams.update({"figure.dpi": 160, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.axisbelow": True,
                     "savefig.bbox": "tight"})


def fig8():
    ev = simulate_failover(seed=3)
    t = np.array([e["t_s"] for e in ev])
    thr = np.array([e["throughput_mbps"] for e in ev])
    lat = np.array([e["latency_ms"] if e["latency_ms"] is not None else np.nan
                    for e in ev])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.6, 4.8), sharex=True,
                                   gridspec_kw=dict(height_ratios=[2, 1]))
    ax1.plot(t, np.maximum(thr, 1e-3), lw=1.6, color="#1f77b4")
    ax1.set_yscale("log")
    ax1.set_ylabel("Throughput (Mbps)")
    ax1.set_ylim(1e-3, 5e3)
    ax1.axvspan(60, 60 + OSPF_CONVERGENCE_S, color="red", alpha=0.12)
    ax1.axvspan(180, 180 + OSPF_CONVERGENCE_S, color="red", alpha=0.12)
    ax1.annotate("optik down\n(air keruh)", xy=(60, 500), xytext=(72, 700),
                 fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.9))
    ax1.annotate("OSPF konvergen\nke akustik", xy=(95, 0.02), xytext=(105, 0.6),
                 fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.9))
    ax1.annotate("optik pulih", xy=(180, 500), xytext=(188, 300),
                 fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.9))
    ax1.set_title("Timeline failover hibrida akustik-optik\n"
                  f"(Z = 40 m, cost OSPF: optik {1}, akustik {100}, "
                  f"konvergensi {OSPF_CONVERGENCE_S:.0f} s)")

    ax2.plot(t, lat, lw=1.6, color="#d62728")
    ax2.set_yscale("log")
    ax2.set_xlabel("Waktu simulasi (s)")
    ax2.set_ylabel("Latensi (ms)")
    ax2.set_ylim(1e-3, 200)
    ax2.axvspan(60, 60 + OSPF_CONVERGENCE_S, color="red", alpha=0.12)
    ax2.axvspan(180, 180 + OSPF_CONVERGENCE_S, color="red", alpha=0.12)
    fig.savefig(os.path.join(FIG, "fig8_failover_timeline.png"))
    plt.close(fig)


def fig9():
    rows = sweep_distance()
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.7))

    # hanya jalur yang benar-benar dipilih router (optical_up=True = kondisi
    # normal; router memilih optik bila masih dalam budget)
    for water, col in [("Clear ocean", "#2ca02c"), ("Coastal", "#ff7f0e")]:
        sub = [r for r in rows if r["water"] == water and r["optical_up"]]
        d = [r["distance_m"] for r in sub]
        thr = [r["throughput_kbps"] for r in sub]
        lat = [r["latency_ms"] for r in sub]
        axes[0].semilogy(d, thr, "o-", ms=3.5, lw=1.6, color=col, label=water)
        axes[1].loglog(d, lat, "o-", ms=3.5, lw=1.6, color=col, label=water)

    # garis referensi kapasitas tiap moda
    axes[0].axhline(OPT_CAPACITY_BPS / 1e3, color="gray", ls=":", lw=1.0)
    axes[0].axhline(ACO_CAPACITY_BPS / 1e3, color="gray", ls=":", lw=1.0)
    axes[0].text(3, OPT_CAPACITY_BPS / 1e3 * 1.6, "optik 1 Gbps",
                 fontsize=7.5, color="gray")
    axes[0].text(3, ACO_CAPACITY_BPS / 1e3 * 1.6, "akustik 15 kbps",
                 fontsize=7.5, color="gray")

    axes[0].set_xscale("log")
    axes[0].set_xlabel("Jarak link (m)")
    axes[0].set_ylabel("Throughput jalur terpilih (kbps)")
    axes[0].set_title("(a) Throughput vs jarak", fontsize=8.5)
    axes[0].legend(fontsize=7.5, loc="lower left")

    axes[1].set_xlabel("Jarak link (m)")
    axes[1].set_ylabel("Latensi propagasi (ms)")
    axes[1].set_title("(b) Latensi vs jarak", fontsize=8.5)
    axes[1].legend(fontsize=7.5, loc="upper left")

    fig.suptitle("Jalur yang dipilih router pada jaringan hibrida "
                 f"(budget optik {OPT_BUDGET_DB:.0f} dB)", fontsize=9.5)
    fig.savefig(os.path.join(FIG, "fig9_throughput_latensi.png"))
    plt.close(fig)


if __name__ == "__main__":
    fig8()
    fig9()
    print("fig8, fig9 selesai")
