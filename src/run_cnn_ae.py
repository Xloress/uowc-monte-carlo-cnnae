"""
Runner CNN-AE yang dapat dilanjutkan (resumable) dan hemat memori.

Setiap kondisi disimpan langsung ke data/ae_<kondisi>.json setelah selesai,
sehingga kegagalan di tengah jalan tidak menghapus hasil sebelumnya.
Jalankan ulang skrip ini untuk melanjutkan kondisi yang belum ada.
"""

import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

sys.path.insert(0, os.path.dirname(__file__))
from cnn_ae_uowc import (EGG_CASES, verify_egg, train_ae, evaluate_ber,
                         baseline_threshold, egg_scintillation_index)

torch.set_num_threads(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG, DAT = os.path.join(ROOT, "figs"), os.path.join(ROOT, "data")
MOD = os.path.join(ROOT, "models")
for d in (FIG, DAT, MOD):
    os.makedirs(d, exist_ok=True)

plt.rcParams.update({"figure.dpi": 160, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.axisbelow": True,
                     "savefig.bbox": "tight"})

K, N_CH = 4, 8
SNR_TEST = [-2, 0, 2, 4, 6, 8, 10, 12, 15, 18, 21, 24]
STEPS = 2500
FEC = 3.8e-3
N_EVAL = 40_000


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def path_of(cond, tag="ae"):
    return os.path.join(DAT, f"{tag}_{cond.lower()}.json")


def do_condition(cond, egg, tag="ae", seed=11, force=False, test_egg=None):
    """Latih + evaluasi satu kondisi, simpan hasil ke JSON.

    egg      : kanal saat PELATIHAN (None = kanal identitas / tanpa CSI)
    test_egg : kanal saat PENGUJIAN (default sama dengan egg)
    """
    if test_egg is None:
        test_egg = egg
    p = path_of(cond, tag)
    if os.path.exists(p) and not force:
        with open(p) as f:
            log(f"  {tag}/{cond}: sudah ada, dilewati")
            return json.load(f)
    log(f"  latih {tag}/{cond} ...")
    t0 = time.time()
    m = train_ae(k=K, n_ch=N_CH, snr_train_db=10.0, steps=STEPS,
                 egg=egg, seed=seed, verbose=False)
    ae = evaluate_ber(m, K, SNR_TEST, egg=test_egg, n_symbols=N_EVAL, seed=301)
    bl = baseline_threshold(K, SNR_TEST, egg=test_egg)
    out = dict(kondisi=cond, ae=ae, base=[float(x) for x in bl],
               sig2=(0.0 if test_egg is None
                     else egg_scintillation_index(**test_egg)),
               train_s=round(time.time() - t0, 1))
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    torch.save(m.state_dict(), os.path.join(MOD, f"{tag}_{cond.lower()}.pt"))
    del m
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    log(f"  {tag}/{cond}: {out['train_s']}s  "
        f"BER@10dB AE={ae[SNR_TEST.index(10)]:.2e} "
        f"OOK={bl[SNR_TEST.index(10)]:.2e}")
    return out


def load(cond, tag="ae"):
    p = path_of(cond, tag)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def make_figures(sig2):
    res = {c: load(c) for c in ["AWGN", "Lemah", "Sedang", "Kuat"]}
    res = {k: v for k, v in res.items() if v}
    nocsi = {c: load(c, "nocsi") for c in ["Lemah", "Sedang", "Kuat"]}
    nocsi = {k: v for k, v in nocsi.items() if v}
    if len(res) < 2:
        log("data belum cukup untuk membuat gambar")
        return

    # ---- Fig 6: BER vs Eb/N0
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    st = {"AWGN": ("#444444", "o", "-"), "Lemah": ("#1f77b4", "s", "-"),
          "Sedang": ("#ff7f0e", "^", "--"), "Kuat": ("#d62728", "D", "-.")}
    for cond, d in res.items():
        c, mk, ls = st[cond]
        lab = cond if cond == "AWGN" else f"{cond} ($\\sigma_I^2$={sig2[cond]:.2f})"
        ax.semilogy(SNR_TEST, d["ae"], ls, marker=mk, ms=4, lw=1.7, color=c,
                    label=f"CNN-AE — {lab}")
        ax.semilogy(SNR_TEST, d["base"], ":", marker=mk, ms=3, lw=1.1,
                    color=c, alpha=0.7, label=f"OOK ambang — {lab}")
    ax.axhline(FEC, color="k", ls="--", lw=1.2)
    ax.text(-1.5, FEC * 1.6, "ambang FEC 3,8$\\times$10$^{-3}$", fontsize=7.5)
    ax.set_xlabel("$E_b/N_0$ (dB)")
    ax.set_ylabel("BER")
    ax.set_ylim(1e-6, 0.6)
    ax.set_xlim(-2, 24)
    ax.set_title("Kinerja CNN-AE pada kanal AWGN dan turbulensi EGG\n"
                 f"(k = {K} bit/simbol, {N_CH} dimensi, laju kode 0,5)")
    ax.legend(fontsize=6.4, ncol=4, loc="upper center",
              bbox_to_anchor=(0.5, -0.16), frameon=False)
    fig.savefig(os.path.join(FIG, "fig6_ber_vs_snr.png"))
    plt.close(fig)
    log("fig6 selesai")

    # ---- Fig 7: BER @ 10 dB vs indeks sintilasi
    i10 = SNR_TEST.index(10)
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    order = [c for c in ["AWGN", "Lemah", "Sedang", "Kuat"] if c in res]
    x = [0.0 if c == "AWGN" else sig2[c] for c in order]
    y_ae = [res[c]["ae"][i10] for c in order]
    y_ook = [res[c]["base"][i10] for c in order]
    ax.plot(x, y_ae, "o-", lw=1.9, ms=7, color="#1f77b4", label="CNN-AE")
    ax.plot(x, y_ook, "^:", lw=1.4, ms=5, color="#d62728", label="OOK ambang")
    if nocsi:
        xn, yn = [], []
        if "AWGN" in res:
            xn.append(0.0)
            yn.append(res["AWGN"]["ae"][i10])
        for c in ["Lemah", "Sedang", "Kuat"]:
            if c in nocsi:
                xn.append(sig2[c])
                yn.append(nocsi[c]["ae"][i10])
        ax.plot(xn, yn, "s--", lw=1.5, ms=6, color="#9467bd",
                label="CNN-AE tanpa pengetahuan kanal")
    for xi, yi, c in zip(x, y_ae, order):
        ax.annotate(c, (xi, yi), textcoords="offset points", xytext=(0, 9),
                    fontsize=7.5, ha="center")
    ax.set_yscale("log")
    ax.axhline(FEC, color="k", ls="--", lw=1.1)
    ax.set_xlabel("Indeks sintilasi $\\sigma_I^2$")
    ax.set_ylabel("BER pada $E_b/N_0$ = 10 dB")
    ax.set_title("Ketahanan CNN-AE terhadap tingkat turbulensi")
    ax.legend(fontsize=7.2)
    fig.savefig(os.path.join(FIG, "fig7_ber_vs_turbulensi.png"))
    plt.close(fig)
    log("fig7 selesai")

    # ---- Fig 8: manfaat channel-aware
    if nocsi:
        fig, ax = plt.subplots(figsize=(6.0, 4.1))
        for cond in ["Lemah", "Sedang", "Kuat"]:
            if cond not in res or cond not in nocsi:
                continue
            c = {"Lemah": "#1f77b4", "Sedang": "#ff7f0e", "Kuat": "#d62728"}[cond]
            ax.semilogy(SNR_TEST, res[cond]["ae"], "-", marker="o", ms=3.5,
                        lw=1.7, color=c, label=f"{cond} — dengan CSI kanal")
            ax.semilogy(SNR_TEST, nocsi[cond]["ae"], "--", marker="x", ms=4,
                        lw=1.3, color=c, alpha=0.85, label=f"{cond} — tanpa CSI")
        ax.axhline(FEC, color="k", ls="--", lw=1.1)
        ax.text(-1.5, FEC * 1.6, "ambang FEC", fontsize=7.5)
        ax.set_xlabel("$E_b/N_0$ (dB)")
        ax.set_ylabel("BER")
        ax.set_ylim(1e-6, 0.6)
        ax.set_xlim(-2, 24)
        ax.set_title("Manfaat pelatihan berbasis kanal pada turbulensi EGG")
        ax.legend(fontsize=7.0, ncol=2)
        fig.savefig(os.path.join(FIG, "fig8_channel_aware_gain.png"))
        plt.close(fig)
        log("fig8 selesai")

    # ---- CSV
    with open(os.path.join(DAT, "ber_vs_snr.csv"), "w") as f:
        f.write("kondisi,kurva,ebn0_db,ber,sigma_I2\n")
        for cond, d in res.items():
            s2 = 0.0 if cond == "AWGN" else sig2[cond]
            for s, a, b in zip(SNR_TEST, d["ae"], d["base"]):
                f.write(f"{cond},CNN-AE,{s},{a:.4e},{s2:.4f}\n")
                f.write(f"{cond},OOK-ambang,{s},{b:.4e},{s2:.4f}\n")
        for cond, d in nocsi.items():
            for s, a in zip(SNR_TEST, d["ae"]):
                f.write(f"{cond},CNN-AE-tanpa-CSI,{s},{a:.4e},"
                        f"{sig2[cond]:.4f}\n")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    log("verifikasi parameter EGG")
    sig2 = verify_egg()
    with open(os.path.join(DAT, "egg_params.csv"), "w") as f:
        f.write("kondisi,omega,lambda,a,b,c,sigma_I2\n")
        for n, p in EGG_CASES.items():
            f.write(f"{n},{p['omega']},{p['lam']},{p['a']},{p['b']},{p['c']},"
                    f"{sig2[n]:.4f}\n")

    if mode in ("all", "ae"):
        for cond, egg in [("AWGN", None)] + list(EGG_CASES.items()):
            do_condition(cond, egg, "ae")
    if mode in ("all", "nocsi"):
        # "tanpa pengetahuan kanal": dilatih pada kanal identitas (tanpa fading),
        # lalu diuji pada kanal EGG -> mengukur manfaat channel-aware training
        for cond, egg in EGG_CASES.items():
            do_condition(cond, None, "nocsi", test_egg=egg, force=True)
    if mode in ("all", "figs"):
        make_figures(sig2)


if __name__ == "__main__":
    main()
