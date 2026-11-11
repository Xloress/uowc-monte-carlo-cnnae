"""
Monte Carlo simulator untuk kanal Underwater Optical Wireless Communication (UOWC).

Referensi utama:
  C. Gabriel, M.-A. Khalighi, S. Bourennane, P. Leon, V. Rigaud,
  "Channel Modeling for Underwater Optical Communication",
  Proc. 2nd IEEE Workshop on Optical Wireless Communications, 2011, pp. 833-837.

Metode: pelacakan trajektori foton (MCML-style).
  - step size       : delta = -ln(chi_delta) / c
  - weight drop     : W_post = W_pre * (1 - a/c)
  - scattering angle: Henyey-Greenstein dengan parameter g
  - azimuth         : uniform [0, 2pi)

Output: received intensity (dB), channel impulse response, time dispersion tau.
"""

import numpy as np

C0 = 2.99792458e8          # m/s
N_WATER = 1.33             # indeks bias air laut
V_WATER = C0 / N_WATER     # m/s

# Tipe air: (a, b, c) dalam 1/m -- Gabriel 2011, Tabel I, lambda = 532 nm
WATER_TYPES = {
    "Pure sea":    dict(a=0.053, b=0.003, c=0.056),
    "Clear ocean": dict(a=0.069, b=0.080, c=0.150),
    "Coastal":     dict(a=0.088, b=0.216, c=0.305),
    "Harbor":      dict(a=0.295, b=1.875, c=2.170),
}

G_HG = 0.924               # Gabriel 2011, Sec. VI


def _hg_cos_theta(chi, g):
    """Sampel cos(theta) dari fungsi fase Henyey-Greenstein (inversi CDF)."""
    if abs(g) < 1e-9:
        return 1.0 - 2.0 * chi
    t = (1.0 - g * g) / (1.0 - g + 2.0 * g * chi)
    return (1.0 + g * g - t * t) / (2.0 * g)


def _rotate(direction, cos_t, phi):
    """Putar vektor arah satuan sebesar theta (cos_t) dan azimuth phi."""
    d = direction
    aux = np.where(np.abs(d[:, 2:3]) < 0.9,
                   np.array([[0.0, 0.0, 1.0]]),
                   np.array([[1.0, 0.0, 0.0]]))
    u = np.cross(d, aux)
    u = u / np.maximum(np.linalg.norm(u, axis=1, keepdims=True), 1e-12)
    v = np.cross(d, u)
    sin_t = np.sqrt(np.maximum(0.0, 1.0 - cos_t ** 2))
    new = (cos_t[:, None] * d
           + (sin_t * np.cos(phi))[:, None] * u
           + (sin_t * np.sin(phi))[:, None] * v)
    return new / np.linalg.norm(new, axis=1, keepdims=True)


def simulate_channel(water="Clear ocean", Z=20.0, D=0.20, n_photons=300_000,
                     beam_width=3e-3, divergence_deg=20.0, fov_deg=180.0,
                     g=G_HG, max_steps=4000, w_min=1e-4, seed=0,
                     return_ir=False, ir_bins=300, ir_span_ns=8.0):
    """
    Simulasi Monte Carlo satu konfigurasi link.

    Return dict: received_ratio, loss_db, n_received, t_arrival, w_arrival,
    dan (jika return_ir=True) ir_time_ns, ir_weight_db, tau_ns.
    """
    rng = np.random.default_rng(seed)
    p = WATER_TYPES[water]
    a, c = p["a"], p["c"]
    albedo = 1.0 - a / c

    # ---- peluncuran foton ------------------------------------------------
    r_launch = beam_width / 2.0 * np.sqrt(rng.random(n_photons))
    phi0 = 2.0 * np.pi * rng.random(n_photons)
    pos = np.zeros((n_photons, 3))
    pos[:, 0] = r_launch * np.cos(phi0)
    pos[:, 1] = r_launch * np.sin(phi0)

    th0 = np.radians(divergence_deg)
    cos_t0 = 1.0 - rng.random(n_photons) * (1.0 - np.cos(th0))
    dirs = _rotate(np.tile([0.0, 0.0, 1.0], (n_photons, 1)), cos_t0,
                   2.0 * np.pi * rng.random(n_photons))

    weight = np.ones(n_photons)
    path = np.zeros(n_photons)
    alive = np.ones(n_photons, dtype=bool)

    rec_w, rec_t = [], []
    r_ap = D / 2.0
    cos_fov = np.cos(np.radians(fov_deg / 2.0))

    for _ in range(max_steps):
        idx = np.flatnonzero(alive)
        if idx.size == 0:
            break

        step = -np.log(rng.random(idx.size)) / c
        newpos = pos[idx] + step[:, None] * dirs[idx]
        z0, z1 = pos[idx, 2], newpos[:, 2]

        # (a) foton yang melintasi bidang z = Z
        cross = (z0 < Z) & (z1 >= Z)
        if np.any(cross):
            ci = idx[cross]
            fr = (Z - z0[cross]) / np.maximum(z1[cross] - z0[cross], 1e-15)
            hit = pos[ci] + fr[:, None] * step[cross][:, None] * dirs[ci]
            rho = np.hypot(hit[:, 0], hit[:, 1])
            # FOV: sudut antara arah foton datang (+z) dan sumbu optik penerima
            ok = (rho <= r_ap) & (dirs[ci][:, 2] >= cos_fov)
            if np.any(ok):
                gi = ci[ok]
                rec_w.append(weight[gi])
                rec_t.append((path[gi] + fr[ok] * step[cross][ok]) / V_WATER)
                alive[gi] = False

        # (b) foton yang lolos melewati bidang penerima tanpa terdeteksi = hilang
        alive[idx[z1 > Z]] = False

        # (c) foton yang terserap (bobot turun di bawah ambang)
        alive[idx[weight[idx] < w_min]] = False

        still = np.flatnonzero(alive)
        if still.size == 0:
            break

        # (d) pindahkan posisi & akumulasi panjang lintasan
        sub = np.searchsorted(idx, still)
        pos[still] = newpos[sub]
        path[still] += step[sub]

        # (e) atenuasi bobot + hamburan Henyey-Greenstein
        weight[still] *= albedo
        cos_t = _hg_cos_theta(rng.random(still.size), g)
        dirs[still] = _rotate(dirs[still], cos_t, 2.0 * np.pi * rng.random(still.size))

    w = np.concatenate(rec_w) if rec_w else np.zeros(0)
    t = np.concatenate(rec_t) if rec_t else np.zeros(0)

    out = dict(received_ratio=w.sum() / n_photons,
               n_received=int(w.size),
               t_arrival=t, w_arrival=w)
    out["loss_db"] = 10.0 * np.log10(max(out["received_ratio"], 1e-30))

    if return_ir and w.size:
        t_los = Z / V_WATER
        dt = (t - t_los) * 1e9                     # ns, relatif terhadap LOS
        mask = (dt >= -1.0) & (dt <= ir_span_ns)
        hist, edges = np.histogram(dt[mask], bins=ir_bins,
                                   range=(-1.0, ir_span_ns), weights=w[mask])
        centres = 0.5 * (edges[1:] + edges[:-1])
        peak = hist.max() if hist.max() > 0 else 1.0
        ir_db = 10.0 * np.log10(np.maximum(hist / peak, 1e-12))
        above = centres[ir_db >= -20.0]
        tau = float(above.max() - above.min()) if above.size else np.nan
        out.update(ir_time_ns=centres, ir_weight_db=ir_db, tau_ns=tau)
    return out


def rms_delay_spread_ns(t_arrival, w_arrival, Z):
    """RMS delay spread (ns) relatif terhadap waktu lintasan lurus.

    Metrik ini jauh lebih stabil secara statistik daripada lebar kurva pada
    -20 dB, karena memakai seluruh distribusi waktu tiba (momen kedua),
    bukan dua titik tepi yang sensitif terhadap noise Monte Carlo.
    """
    w = np.asarray(w_arrival, dtype=float)
    if w.size < 50:
        return float("nan")
    t = np.asarray(t_arrival, dtype=float)
    rel = (t - Z / V_WATER) * 1e9
    m1 = (rel * w).sum() / w.sum()
    m2 = (rel ** 2 * w).sum() / w.sum()
    return float(np.sqrt(max(m2 - m1 * m1, 0.0)))


def tau_ns(t_arrival, w_arrival, Z, bins=500, span_ns=5.0):
    """Lebar IR pada -20 dB (dari puncak). Tidak stabil untuk jumlah foton kecil."""
    w = np.asarray(w_arrival, dtype=float)
    if w.size < 50:
        return float("nan")
    rel = (np.asarray(t_arrival) - Z / V_WATER) * 1e9
    mask = (rel >= -1.0) & (rel <= span_ns)
    hist, edges = np.histogram(rel[mask], bins=bins, range=(-1.0, span_ns),
                               weights=w[mask])
    centres = 0.5 * (edges[1:] + edges[:-1])
    peak = hist.max() if hist.max() > 0 else 1.0
    ir_db = 10.0 * np.log10(np.maximum(hist / peak, 1e-12))
    above = centres[ir_db >= -20.0]
    return float(above.max() - above.min()) if above.size else float("nan")


def beer_lambert_loss_db(water, Z):
    """Redaman Beer-Lambert murni: 10*log10(exp(-c*Z))."""
    return -WATER_TYPES[water]["c"] * Z * 10.0 / np.log(10.0)


def geometric_loss_db(Z, D, divergence_deg):
    """Rugi geometris (spreading) berkas kerucut terhadap aperture."""
    r = Z * np.tan(np.radians(divergence_deg))
    ratio = min(1.0, (D / 2.0) ** 2 / max(r, 1e-12) ** 2)
    return 10.0 * np.log10(max(ratio, 1e-30))


if __name__ == "__main__":
    r = simulate_channel("Clear ocean", Z=20.0, D=0.20, n_photons=300_000,
                         return_ir=True, seed=1)
    print("Clear ocean, Z=20m, D=20cm, 300k foton")
    print(f"  received = {r['received_ratio']:.3e}  ->  {r['loss_db']:.2f} dB")
    print(f"  tau      = {r['tau_ns']:.3f} ns")
    print("  Gabriel 2011 Tabel II: -28.03 dB, tau = 0.35 ns")
