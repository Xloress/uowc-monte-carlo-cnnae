# Tutorial OptiSystem — Praktikum Link Budget UOWC

Panduan ini menghasilkan **Gambar 2(a)** pada paper: topologi rangkaian,
eye diagram, dan Q-factor untuk link optik bawah air.

> **Peringatan angka.** Panduan praktikum sebelumnya menyuruh mengisi
> *Attenuation* = 0,151 dB/m untuk clear ocean. Nilai itu **salah**.
> Tabel I Gabriel (2011) memberi c = 0,15 m⁻¹, yang setara **0,651 dB/m**.
> Nilai 0,151 dB/m setara c ≈ 0,035 m⁻¹ — tidak cocok dengan tipe air mana pun.
> Kalau dipakai, redaman 20 m hanya 3 dB dan eye diagram akan terlihat bagus
> padahal seharusnya sudah tertutup. Selalu pakai tabel konversi di bawah.

## 0. Konversi koefisien ke dB/m

OptiSystem menerima atenuasi dalam dB/m, sedangkan literatur memberi c dalam m⁻¹.

```
atenuasi [dB/m] = c [m⁻¹] × 10 / ln(10) = c × 4,343
```

| Tipe air | c (m⁻¹) | dB/m yang diisi di OptiSystem |
|---|---|---|
| Pure sea | 0,056 | **0,243** |
| Clear ocean | 0,150 | **0,651** |
| Coastal | 0,305 | **1,325** |
| Turbid harbor | 2,170 | **9,424** |

## 1. Menyiapkan proyek

1. Buka OptiSystem → **File → New**.
2. Simpan sebagai `uowc_linkbudget.osd`.
3. Atur **global parameter** (klik kanan di kanvas → *Global parameters*):
   - `Bit rate` = 1e9 (1 Gbps) — atau 100e6 kalau komputasi terlalu berat
   - `Sequence length` = 8192 bit
   - `Samples per bit` = 64
4. Buka **Layout → Layout properties**, set *Simulation bandwidth* = 10 × bit rate.

## 2. Rangkaian pemancar

Urutan komponen dari kiri ke kanan:

| No | Komponen (library) | Parameter yang diubah |
|---|---|---|
| 1 | **Pseudo-Random Bit Sequence Generator** (Default/Transmitters/Bit sequence generators) | Bit rate = `Bit rate`, lihat global |
| 2 | **NRZ Pulse Generator** (Default/Visualization library/Signal processing/Pulse generators) | Duty cycle = 1 |
| 3 | **CW Laser** (Default/Transmitters/Optical sources) | Frequency = 563,6 THz (λ=532 nm); Power = 20 mW; Linewidth = 10 MHz |
| 4 | **Mach-Zehnder Modulator** (Default/Transmitters/Optical modulators) | Extinction ratio = 30 dB |

Sambungkan: PRBS → NRZ → port *electrical input* MZM;
CW Laser → port *optical input* MZM.

**Cara mengisi λ = 532 nm:** OptiSystem memakai frekuensi. Hitung dengan
`f = c/λ = 3e8 / 532e-9 = 5,639e14 Hz = 563,9 THz`.

## 3. Kanal air laut

Komponen: **FSO Channel** (Default/Transmitters/Optical fiber/FSO channel)
atau **Optical Attenuator** kalau FSO tidak tersedia di versi Anda.

Untuk **FSO Channel**:
- *Range* = 20 m
- *Attenuation* = `0,651` dB/m (clear ocean)
- *Geometrical loss* = **aktifkan**, isi:
  - Transmitter aperture diameter = 3 mm
  - Receiver aperture diameter = 200 mm
  - Beam divergence = 1,75 deg (setengah sudut)

Untuk **Optical Attenuator** (lebih sederhana, tapi kehilangan rugi geometris):
- *Attenuation* = `0,651 × 20` = **13,02 dB**
- Tambahkan rugi geometris manual: **−24,9 dB** (dari simulasi Monte Carlo,
  θ₀ = 1,75°, D = 20 cm, Z = 20 m)
- Total = **37,9 dB**

> Angka 37,9 dB ini adalah nilai yang harus Anda dapat. Kalau hasil simulasi
> Anda jauh berbeda, periksa konversi dB/m dan rugi geometrisnya.

## 4. Rangkaian penerima

| No | Komponen | Parameter |
|---|---|---|
| 5 | **APD** (Default/Receivers/Photodetectors/APD) | Gain = 10; Responsivity = 4 A/W (pada 532 nm); Thermal noise = 1e-22 W/Hz |
| 6 | **Low Pass Bessel Filter** (Default/Filters/Electrical) | Cutoff = 0,75 × bit rate = 750 MHz; Order = 4 |
| 7 | **3R Regenerator** (Default/Receivers/Regenerators) | Decision threshold = 0 (auto) |
| 8 | **BER Test Set** (Default/Visualization library/Electrical/BER test set) | — |
| 9 | **Eye Diagram Analyzer** (Default/Visualization library/Visualizers) | — |

Sambungkan: FSO → APD → LPF → 3R Regenerator → BER Test Set dan
Eye Diagram Analyzer (boleh di-paralel).

## 5. Menjalankan simulasi

1. Klik **Calculate** (ikon kalkulator) atau tekan F10.
2. Tunggu hingga *Calculation finished*.
3. Buka **Eye Diagram Analyzer** → klik *Show graph*.
4. Buka **BER Test Set** → catat nilai **Q-factor** dan **Min BER**.

## 6. Membaca hasil

Interpretasi yang benar untuk laporan:

- **Eye terbuka lebar** → Q > 6 (BER < 1e-9), link layak.
- **Eye mulai menutup** → 3 < Q < 6, link marginal.
- **Eye tertutup / tidak ada mata** → Q < 3, link gagal.

Untuk clear ocean, Z = 20 m, D = 20 cm, θ₀ = 1,75°, dengan Pt = 20 mW
dan sensitivitas APD tipikal −30 dBm:

```
budget daya   = 20 dBm − (−30 dBm) = 50 dB
rugi kanal    = 37,9 dB
margin        = 12,1 dB  ->  link LAYAK
```

Pada Z = 50 m:
```
rugi kanal    = 0,651 × 50 + 38,9 (geometris) = 71,5 dB
margin        = 50 − 71,5 = −21,5 dB  ->  link GAGAL
```

Inilah yang harus terlihat di eye diagram: pada 20 m mata terbuka,
pada 50 m mata tertutup. Kalau keduanya terbuka, ada parameter yang salah.

## 7. Variasi yang perlu dijalankan (untuk Gambar)

Buat **parameter sweep** agar tidak perlu mengubah satu per satu:

1. **Layout → Parameter sweep** (atau *Tools → Parameter sweeps*).
2. Pilih komponen FSO Channel → parameter `Range`.
3. Isi nilai: 10, 20, 30, 40, 50 m.
4. Pilih hasil yang direkam: `Q-factor` dari BER Test Set.
5. Jalankan → ekspor hasil ke CSV.

Ulangi untuk empat tipe air (0,243 / 0,651 / 1,325 / 9,424 dB/m).
Hasilnya: kurva Q-factor vs jarak untuk empat tipe air — ini **Gambar 2(a)**
versi OptiSystem, dan bisa dibandingkan langsung dengan hasil Monte Carlo
Python (Gambar 1).

## 8. Kalau OptiSystem tidak tersedia / versi berbeda

Semua angka di atas bisa direproduksi di Python tanpa OptiSystem:

```python
import numpy as np
c_db_per_m = 0.150 * 10 / np.log(10)        # 0,651 dB/m
Z, D, theta = 20, 0.20, np.radians(1.75)
geo = 10*np.log10(min(1, (D/2)**2 / (Z*np.tan(theta))**2))
loss = c_db_per_m * Z - geo                  # 13,02 + 24,9 = 37,9 dB
```

File `src/monte_carlo_uowc.py` pada folder ini sudah menghitungnya dengan
metode yang lebih akurat (pelacakan foton), dan hasilnya tervalidasi
terhadap Gabriel (2011).

## 9. Checklist sebelum screenshot masuk paper

- [ ] Nilai atenuasi sudah dikonversi ke dB/m (bukan menyalin c)
- [ ] Rugi geometris ikut dihitung, tidak hanya Beer-Lambert
- [ ] Bit rate dan samples per bit dicatat di caption
- [ ] Nama file screenshot menyebut tipe air dan jarak
- [ ] Eye diagram pada 20 m dan 50 m keduanya diambil (kontras terbuka-tertutup)
- [ ] Q-factor dicatat di tabel, bukan hanya dikira-kira dari gambar
