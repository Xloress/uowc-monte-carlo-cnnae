"""Utilitas: memuat hasil CNN-AE per kondisi dan meringkasnya jadi teks."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAT = os.path.join(ROOT, "data")
CONDS = ["AWGN", "Lemah", "Sedang", "Kuat"]
SNR = [-2, 0, 2, 4, 6, 8, 10, 12, 15, 18, 21, 24]


def _load(name):
    p = os.path.join(DAT, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def load_ae():
    out = {}
    for c in CONDS:
        d = _load(f"ae_{c.lower()}.json")
        if d:
            out[c] = d
    return out


def load_nocsi():
    out = {}
    for c in ["Lemah", "Sedang", "Kuat"]:
        d = _load(f"nocsi_{c.lower()}.json")
        if d:
            out[c] = d
    return out


def load_sig2():
    out = {}
    for c in ["Lemah", "Sedang", "Kuat"]:
        d = _load(f"ae_{c.lower()}.json")
        if d and "sig2" in d:
            out[c] = d["sig2"]
    return out


def crossing(ber_list, thresh=3.8e-3, snr_list=None):
    """Eb/N0 pertama yang BER-nya di bawah ambang FEC (interpolasi kasar)."""
    snr_list = snr_list or SNR
    for s, b in zip(snr_list, ber_list):
        if b <= thresh:
            return s
    return None


def summarize():
    ae, nc = load_ae(), load_nocsi()
    lines = []
    for c in CONDS:
        if c not in ae:
            continue
        i10 = SNR.index(10)
        lines.append(dict(
            kondisi=c,
            ber_ae_10=ae[c]["ae"][i10],
            ber_ook_10=ae[c]["base"][i10],
            snr_fec_ae=crossing(ae[c]["ae"]),
            snr_fec_ook=crossing(ae[c]["base"]),
            ber_nocsi_10=nc.get(c, {}).get("ae", [None] * 12)[i10],
        ))
    return lines


if __name__ == "__main__":
    for r in summarize():
        print(r)
