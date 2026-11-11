"""
Simulasi jaringan hibrida akustik-optik UOWC: mekanisme failover berbasis OSPF.

Tujuan: menghasilkan kurva throughput & latensi terhadap jarak, serta log
peristiwa peralihan jalur, sebagai pengganti screenshot Packet Tracer
(yang tetap disarankan dijalankan terpisah untuk validasi konfigurasi).

Model:
  - Link optik  : throughput mengikuti kapasitas kanal dari hasil Monte Carlo,
                  mati bila rugi kanal melebihi budget daya (default 100 dB)
  - Link akustik: throughput dari model bandwidth sempit (Thorp + spreading)
  - Router menjalankan OSPF: cost antarmuka optik = 1, akustik = 100
    -> trafik selalu lewat optik selama optik up (cost lebih rendah)
  - Saat optik down, OSPF konvergen dalam waktu konvergensi (default 40 s),
    selama itu trafik terputus (blackhole)
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from monte_carlo_uowc import WATER_TYPES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAT = os.path.join(ROOT, "data")
os.makedirs(DAT, exist_ok=True)

# ------------------------------------------------------------------ parameter
OPT_TX_DBM = 20.0          # 100 mW laser
OPT_RX_SENS_DBM = -30.0    # sensitivitas APD tipikal
OPT_BUDGET_DB = OPT_TX_DBM - OPT_RX_SENS_DBM      # 50 dB

# throughput optik hasil praktikum (kapasitas link, bit/s)
OPT_CAPACITY_BPS = 1.0e9   # 1 Gbps pada kondisi terbaik (Bo dkk. 2024)

# akustik: model bandwidth sempit
ACO_CAPACITY_BPS = 15e3    # 15 kbps, frekuensi menengah
ACO_CAPACITY_LOW_BPS = 2.4e3
SOUND_SPEED = 1500.0       # m/s

OSPF_COST_OPT = 1
OSPF_COST_ACO = 100
OSPF_CONVERGENCE_S = 40.0  # waktu konvergensi OSPF (hello/dead interval)


def acoustic_capacity(distance_m):
    """Kapasitas akustik turun terhadap jarak (Thorp + spreading, disederhanakan)."""
    if distance_m <= 500:
        return ACO_CAPACITY_BPS
    if distance_m <= 2000:
        return ACO_CAPACITY_LOW_BPS
    return ACO_CAPACITY_LOW_BPS * 0.5


def optical_loss_db(water, distance_m):
    """Rugi kanal optik: dipakai kurva Monte Carlo (fallback: Beer-Lambert)."""
    path = os.path.join(DAT, "attenuation_vs_distance.csv")
    if os.path.exists(path):
        best = None
        with open(path) as f:
            next(f)
            for line in f:
                w, z, n, loss, bl, nr = line.strip().split(",")
                if w == water and int(nr) > 0:
                    z = float(z)
                    if best is None or abs(z - distance_m) < abs(best[0] - distance_m):
                        best = (z, float(loss))
        if best and abs(best[0] - distance_m) <= 10:
            return best[1]
    c = WATER_TYPES[water]["c"]
    return -c * distance_m * 10.0 / np.log(10.0)


def route(distance_m, water="Clear ocean", optical_up=True):
    """Kembalikan (jalur_aktif, throughput_bps, latensi_ms, cost)."""
    loss = optical_loss_db(water, distance_m)
    opt_ok = optical_up and (loss > -OPT_BUDGET_DB)

    if opt_ok:
        return ("optik", OPT_CAPACITY_BPS,
                distance_m / (3e8 / 1.33) * 1e3, OSPF_COST_OPT)
    # akustik: latensi propagasi dominan
    return ("akustik", acoustic_capacity(distance_m),
            distance_m / SOUND_SPEED * 1e3, OSPF_COST_ACO)


def simulate_failover(water="Clear ocean", t_total=300.0, dt=0.5,
                      blackout_at=60.0, restore_at=180.0, distance_m=40.0,
                      seed=0):
    """
    Timeline: mulai di jarak tertentu, optik up. Pada t=blackout_at, AUV masuk
    perairan keruh (optik down). Pada t=restore_at, optik pulih.

    Return: list dict per langkah waktu.
    """
    rng = np.random.default_rng(seed)
    events = []
    t = 0.0
    converged = True
    last_switch = -1e9

    while t <= t_total:
        optical_physically_up = not (blackout_at <= t < restore_at)
        # OSPF butuh waktu konvergensi setelah perubahan status link
        if not optical_physically_up and converged:
            converged = False
            last_switch = t
        if optical_physically_up and not converged:
            converged = True
            last_switch = t

        in_transition = (not converged) and (t - last_switch < OSPF_CONVERGENCE_S)

        if in_transition:
            path_name, thr, lat = "transisi", 0.0, np.nan
            cost = OSPF_COST_OPT
        else:
            path_name, thr, lat, cost = route(distance_m, water,
                                              optical_up=optical_physically_up)
        # throughput efektif dengan jitter kecil
        thr_eff = thr * (1.0 + 0.02 * rng.standard_normal()) if thr > 0 else 0.0
        events.append(dict(t_s=round(t, 2), path=path_name,
                           throughput_mbps=round(max(thr_eff, 0.0) / 1e6, 4),
                           latency_ms=None if np.isnan(lat) else round(lat, 4),
                           ospf_cost=cost, link_up=optical_physically_up))
        t += dt
    return events


def sweep_distance():
    """Throughput & latensi vs jarak untuk kedua mode."""
    rows = []
    for water in ["Clear ocean", "Coastal"]:
        for d in [5, 10, 20, 30, 40, 50, 60, 80, 100, 200, 500, 1000, 2000]:
            for optical_up in (True, False):
                path, thr, lat, cost = route(d, water, optical_up=optical_up)
                rows.append(dict(water=water, distance_m=d, optical_up=optical_up,
                                 path=path, throughput_kbps=thr / 1e3,
                                 latency_ms=lat, ospf_cost=cost))
    return rows


if __name__ == "__main__":
    ev = simulate_failover()
    with open(os.path.join(DAT, "failover_timeline.json"), "w") as f:
        json.dump(ev, f, indent=1)
    rows = sweep_distance()
    with open(os.path.join(DAT, "hybrid_sweep.csv"), "w") as f:
        f.write("water,distance_m,optical_up,path,throughput_kbps,latency_ms,ospf_cost\n")
        for r in rows:
            f.write(f"{r['water']},{r['distance_m']},{r['optical_up']},{r['path']},"
                    f"{r['throughput_kbps']:.3f},{r['latency_ms']:.4f},{r['ospf_cost']}\n")

    print(f"budget daya optik: {OPT_BUDGET_DB:.0f} dB "
          f"(Tx {OPT_TX_DBM:.0f} dBm, sensitivitas {OPT_RX_SENS_DBM:.0f} dBm)\n")
    print(f"{'jarak':>7} {'jalur':>9} {'throughput':>14} {'latensi':>12} {'cost':>5}")
    for r in rows:
        if r["water"] != "Clear ocean":
            continue
        print(f"{r['distance_m']:>6.0f}m {r['path']:>9} "
              f"{r['throughput_kbps']:>11.1f} kbps {r['latency_ms']:>9.3f} ms "
              f"{r['ospf_cost']:>5}")

    print("\nTimeline failover (detik):")
    prev = None
    for e in ev:
        if e["path"] != prev:
            print(f"  t={e['t_s']:6.1f}s  ->  {e['path']:9s}  "
                  f"thr={e['throughput_mbps']:.3f} Mbps  "
                  f"lat={e['latency_ms']}")
            prev = e["path"]
