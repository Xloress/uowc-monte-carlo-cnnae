"""
Sistem UOWC berbasis CNN-Autoencoder (CNN-AE) dengan kanal turbulensi EGG.

Mengikuti arsitektur pada:
  X. Bo, C. Cui, Y. Wang, M. Zhao, "Channel Modeling and Performance Analysis of
  Underwater Wireless Optical Communication System", Proc. 6th CISCE, 2024.

Model turbulensi EGG (Exponential-Generalized Gamma):
  E. Zedini et al., "Unified Statistical Channel Model for Turbulence-Induced
  Fading in Underwater Wireless Optical Communication Systems",
  IEEE Trans. Commun., 2018.

Arsitektur (lapisan konvolusi 1D + lapisan dense, seperti pada Bo dkk.):
  Encoder : Conv1D(1->64, ELU) -> Conv1D(64->64, ELU) -> Flatten
            -> Linear(64*M->256, ELU) -> Linear(256->n_ch)
            -> PowerConstraint: sigmoid(beta*s) + normalisasi daya rata-rata
  Channel : y = I*s + n,  I ~ EGG (I = 1 untuk AWGN murni)
  Decoder : Linear(n_ch->256, ELU) -> Linear(256->64*M) -> Reshape(64, M)
            -> Conv1D(64->64, ELU) -> Conv1D(64->M) -> softmax
"""

import numpy as np
import torch
import torch.nn as nn


# --------------------------------------------------------------- kanal EGG
def sample_egg(n, omega, lam, a, b, c, rng=None):
    """
    Sampel intensitas ternormalisasi I dari distribusi EGG:

        f_I(x) = omega * lam*exp(-lam x)
               + (1-omega) * c*b^a/Gamma(a) * x^(a c - 1) * exp(-b x^c)

    Komponen generalized-Gamma disampel lewat Y = X^c ~ Gamma(a, 1/b).
    """
    rng = rng or np.random.default_rng(0)
    u = rng.random(n)
    out = np.empty(n)
    is_exp = u < omega
    m = int(is_exp.sum())
    if m:
        out[is_exp] = rng.exponential(1.0 / lam, m)
    if n - m:
        y = rng.gamma(a, 1.0 / b, n - m)
        out[~is_exp] = y ** (1.0 / c)
    return out


def egg_scintillation_index(omega, lam, a, b, c, n=400_000, seed=0):
    """Indeks sintilasi sigma_I^2 = Var(I)/E[I]^2 (numerik)."""
    I = sample_egg(n, omega, lam, a, b, c, np.random.default_rng(seed))
    return float(I.var() / I.mean() ** 2)


# Parameter dikalibrasi numerik -> sigma_I^2 = 0,20 / 0,75 / 2,0
EGG_CASES = {
    "Lemah":    dict(omega=0.15, lam=6.0, a=8.0, b=8.0, c=1.30),
    "Sedang":   dict(omega=0.35, lam=0.8, a=2.0, b=2.0, c=1.00),
    "Kuat":     dict(omega=0.65, lam=1.5, a=1.0, b=1.0, c=0.70),
}


def verify_egg():
    print("Verifikasi parameter EGG (indeks sintilasi numerik):")
    out = {}
    for name, p in EGG_CASES.items():
        s2 = egg_scintillation_index(**p)
        out[name] = s2
        print(f"  {name:7s}  sigma_I^2 = {s2:6.3f}")
    return out


# --------------------------------------------------------------- model
class CNN_AE(nn.Module):
    def __init__(self, k=4, n_ch=8, width=64, hid=256):
        super().__init__()
        self.k, self.M, self.n_ch = k, 2 ** k, n_ch
        M = self.M
        self.enc = nn.Sequential(
            nn.Conv1d(1, width, 3, padding=1), nn.ELU(),
            nn.Conv1d(width, width, 3, padding=1), nn.ELU(),
            nn.Flatten(),
            nn.Linear(width * M, hid), nn.ELU(),
            nn.Linear(hid, n_ch),
        )
        self.beta = 3.0          # parameter soft-binarisasi
        # decoder diberi estimasi kanal (h_hat) sebagai masukan tambahan:
        # tanpa ini decoder buta terhadap skala fading dan muncul error floor
        self.dec = nn.Sequential(
            nn.Linear(n_ch + 1, hid), nn.ELU(),
            nn.Linear(hid, width * M),
            nn.Unflatten(1, (width, M)),
            nn.Conv1d(width, width, 3, padding=1), nn.ELU(),
            nn.Conv1d(width, M, 1),
            nn.Flatten(),
        )

    def encode(self, x):
        """x: (B, M, 1) one-hot -> (B, n_ch) simbol non-negatif, peak-limited.

        Skala RMS diterapkan SEBELUM sigmoid. Normalisasi setelah sigmoid akan
        memusatkan keluaran di 0,5-1,0 (semua simbol hampir identik) dan
        melumpuhkan training; menskalakan pra-aktivasi menjaga rentang tetap
        di sekitar titik kerja sigmoid.
        """
        pre = self.enc(x.transpose(1, 2))
        pre = pre / (pre.pow(2).mean().sqrt() + 1e-9)
        s = torch.sigmoid(self.beta * pre)      # 0 <= s <= 1
        # normalisasi daya memakai skalar batch (bukan per-sampel) agar daya
        # simbol = 1 tanpa menghapus informasi antar-simbol
        return s / (s.pow(2).mean().sqrt() + 1e-9)

    def decode(self, y, h_hat=None):
        """y: (B, n_ch) -> (B, M) logits. h_hat: estimasi kanal (B,) atau (B,1)."""
        if h_hat is None:
            h_hat = torch.ones(y.shape[0], 1, device=y.device)
        h_hat = h_hat.reshape(-1, 1)
        return self.dec(torch.cat([y, h_hat], dim=1))

    def forward(self, x, h=None, noise_var=0.0, gen=None):
        s = self.encode(x)
        if h is not None:
            s = s * h.unsqueeze(1)
        if noise_var > 0:
            s = s + torch.randn(s.shape, generator=gen) * np.sqrt(noise_var)
        return self.decode(s, h_hat=h), s


def make_batch(bits, k):
    """bits: (B, k) tensor biner -> ((B, M, 1) one-hot, (B,) indeks simbol)."""
    idx = (bits * (2 ** torch.arange(k - 1, -1, -1))).sum(dim=1).long()
    M = 2 ** k
    oh = torch.zeros(bits.shape[0], M)
    oh[torch.arange(bits.shape[0]), idx] = 1.0
    return oh.unsqueeze(-1), idx


def train_ae(k=4, n_ch=8, snr_train_db=10.0, steps=4000, batch=256,
             egg=None, seed=0, lr=1e-3, verbose=True):
    """Latih CNN-AE. snr_train_db adalah Eb/N0 dalam dB."""
    torch.manual_seed(seed)
    model = CNN_AE(k=k, n_ch=n_ch)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps)
    lossf = nn.CrossEntropyLoss()
    gen = torch.Generator().manual_seed(seed + 1)
    rng = np.random.default_rng(seed + 2)

    # Daya simbol dinormalisasi ke 1 di encoder, sehingga N0 = k / EbN0
    # Daya simbol dinormalisasi ke 1 (Es = 1). Eb = Es/k sehingga
    # Es/N0 = k * Eb/N0  ->  varians derau sigma^2 = 1/(k * EbN0).
    # (Memakai k/EbN0 membuat derau 12 dB terlalu besar untuk k = 4.)
    noise_var = 1.0 / (k * 10 ** (snr_train_db / 10))

    for it in range(steps):
        bits = torch.randint(0, 2, (batch, k), generator=gen)
        x, idx = make_batch(bits, k)
        h = None
        if egg is not None:
            h = torch.tensor(sample_egg(batch, **egg, rng=rng), dtype=torch.float32)
        logits, _ = model(x, h=h, noise_var=noise_var, gen=gen)
        loss = lossf(logits, idx)
        opt.zero_grad()
        loss.backward()
        opt.step()
        sched.step()
        if verbose and (it + 1) % 1000 == 0:
            acc = (logits.argmax(1) == idx).float().mean().item()
            print(f"    step {it+1:5d}  loss = {loss.item():.4f}  acc = {acc:.3f}",
                  flush=True)
    model.eval()
    return model


@torch.no_grad()
def evaluate_ber(model, k, snr_db_list, egg=None, n_symbols=80_000,
                 seed=123):
    """BER vs Eb/N0 untuk model terlatih."""
    gen = torch.Generator().manual_seed(seed)
    rng = np.random.default_rng(seed + 1)
    out = []
    for snr_db in snr_db_list:
        nv = 1.0 / (k * 10 ** (snr_db / 10))   # Es=1, Eb=Es/k
        errs = tot = 0
        done = 0
        while done < n_symbols:
            b = min(4096, n_symbols - done)
            bits = torch.randint(0, 2, (b, k), generator=gen)
            x, _ = make_batch(bits, k)
            h = None
            if egg is not None:
                h = torch.tensor(sample_egg(b, **egg, rng=rng), dtype=torch.float32)
            logits, _ = model(x, h=h, noise_var=nv, gen=gen)
            pred = logits.argmax(dim=1)
            pb = ((pred.unsqueeze(1) >> torch.arange(k - 1, -1, -1)) & 1)
            errs += (pb != bits).sum().item()
            tot += bits.numel()
            done += b
        out.append(max(errs / tot, 1e-6))
    return out


def baseline_threshold(k, snr_db_list, egg=None, n=400_000, seed=7):
    """
    Baseline tanpa AI: deteksi ambang pada kanal yang sama.
    Tanpa fading: BER = Q(sqrt(SNR)).  Dengan fading: BER = E_I[Q(sqrt(SNR I^2))].
    """
    from scipy.special import erfc
    rng = np.random.default_rng(seed)
    out = []
    for snr_db in snr_db_list:
        snr = 10 ** (snr_db / 10)
        if egg is None:
            ber = 0.5 * erfc(np.sqrt(snr / 2))
        else:
            I = sample_egg(n, **egg, rng=rng)
            ber = float(np.mean(0.5 * erfc(np.sqrt(snr * I ** 2 / 2))))
        out.append(max(ber, 1e-6))
    return out


if __name__ == "__main__":
    verify_egg()
