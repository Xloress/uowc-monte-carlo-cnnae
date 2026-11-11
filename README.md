# Optimization of Underwater Optical Wireless Communication (UOWC) via CNN-Autoencoder and Acoustic-Optical Hybrid Architecture

Repositori riset ilmiah dan simulasi komputasi komunikasi optik nirkabel bawah air (*Underwater Optical Wireless Communication* / UOWC) menggunakan metode **Monte Carlo**, perbaikan Bit Error Rate (BER) berbasis **Deep Learning CNN-Autoencoder (PyTorch)**, serta perancangan skema failover hibrida **Optik-Akustik OSPFv2**.

Proyek riset ini disusun oleh **Azlan Abdurahman (241344006)** dan **Muhammad Alvian Syahputra (241344018)** di bawah bimbingan dosen:
* Mohammad Farid Susanto, ST., M.Eng
* Ahmad Ikhyari, M.T.  
*Program Studi D4 Teknik Telekomunikasi, Politeknik Negeri Bandung (POLBAN)*.

---

## 🌊 Latar Belakang & Masalah Riset

Komunikasi bawah air konvensional menggunakan gelombang akustik memiliki latensi tinggi (~1500 m/s) dan keterbatasan bandwidth (orde kbps). UOWC menggunakan spektrum cahaya biru-hijau ($\lambda = 532\text{ nm}$) menawarkan throughput data tinggi hingga orde Gbps. Namun, UOWC menghadapi tantangan absorpsi, hamburan multipath partikel laut, dan turbulensi fluktuasi indeks bias (sintilasi laut).

---

## 🔬 Metodologi & Hasil Kunci

1. **Simulasi Kanal Monte Carlo:**
   * Melacak propagasi 300.000 foton per titik pada empat karakteristik air (*pure sea, clear ocean, coastal, harbor*).
   * Membuktikan bahwa rumus analitis sederhana *Beer-Lambert* terlalu optimis 13,5 dB pada jarak 20 m karena mengabaikan rugi geometris divergensi berkas.
   * Redaman simulasi tervalidasi terhadap literatur internasional: $-26,5\text{ dB}$ berbanding acuan $-28,0\text{ dB}$ pada *clear ocean 20 m*.

2. **Denoising Kanal Berbasis CNN-Autoencoder (PyTorch):**
   * Mengimplementasikan arsitektur end-to-end autoencoder dengan aktivasi sigmoid (menjaga sinyal intensitas optik unipolar non-negatif).
   * **Hasil Evaluasi:** Berhasil menekan Bit Error Rate (BER) dari **0,066 menjadi 0,029** pada kondisi turbulensi sedang ($E_b/N_0 = 10\text{ dB}$).

3. **Arsitektur Jaringan Hibrida Optik-Akustik:**
   * Integrasi jalur transmisi primer UOWC berkecepatan tinggi dengan jalur akustik sekunder berjangkauan jauh menggunakan protokol routing dinamis OSPFv2 (metrik cost 1 vs 100).
   * Memastikan mekanisme *automatic failover* sebesar ~40 detik saat tautan optik terhalang/terputus.

---

## 📂 Struktur Repositori

```text
├── docs/
│   └── Paper_UOWC_CNN_AE_Azlan_Alvian.docx    # Naskah lengkap paper ilmiah
├── simulation/
│   └── monte_carlo_uowc.py                    # Script simulator kanal foton Monte Carlo
├── models/
│   └── cnn_autoencoder.py                     # Arsitektur PyTorch CNN-Autoencoder UOWC
└── README.md
```
