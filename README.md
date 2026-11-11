# Optimization of Underwater Optical Wireless Communication (UOWC) via CNN-Autoencoder and Acoustic-Optical Hybrid Architecture

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![OptiSystem](https://img.shields.io/badge/OptiSystem-Optical%20Simulation-brightgreen)]()
[![Monte Carlo](https://img.shields.io/badge/Simulation-Monte%20Carlo%20Photons-blue)]()

Repositori ini memuat implementasi komputasi, pemodelan kanal, arsitektur *deep learning*, serta dataset riset mengenai optimalisasi sistem **Underwater Optical Wireless Communication (UOWC)**. Riset ini mengintegrasikan simulasi propagasi foton berbasis **Monte Carlo**, penekanan *Bit Error Rate* (BER) menggunakan **CNN-Autoencoder (PyTorch)**, dan perancangan mekanisme keandalan jaringan hibrida **Optik-Akustik OSPFv2**.

Proyek riset ini disusun oleh **Azlan Abdurahman (241344006)** dan **Muhammad Alvian Syahputra (241344018)** di bawah bimbingan:
* **Mohammad Farid Susanto, ST., M.Eng**
* **Ahmad Ikhyari, M.T.**  
*Program Studi D4 Teknik Telekomunikasi, Jurusan Teknik Elektro, Politeknik Negeri Bandung (POLBAN)*.

---

## 📌 Abstrak & Latar Belakang

Komunikasi nirkabel bawah laut berbasis akustik konvensional memiliki keterbatasan fisik mendasar berupa latensi perambatan yang tinggi ($\approx 1500\text{ m/s}$) dan lebar pita yang sangat sempit (orde kilohertz). UOWC menggunakan spektrum cahaya biru-hijau ($\lambda = 532\text{ nm}$) menawarkan solusi transmisi data berkecepatan tinggi hingga orde Gigabits per detik (Gbps). 

Penelitian ini memfokuskan pada tiga pilar penyelesaian tantangan kanal optik bawah air:
1. **Karakterisasi Kanal & Hamburan Multi-jalur:** Menggunakan simulasi Monte Carlo untuk memetakan divergensi geometris, *impulse response*, dan *RMS delay spread*.
2. **Mitigasi Turbulensi & Sintilasi Laut:** Menerapkan arsitektur *end-to-end* CNN-Autoencoder yang dilatih langsung terhadap pemodelan kanal turbulensi *Exponential-Generalized Gamma* (EGG).
3. **Keandalan Tautan Berkelanjutan:** Merancang sistem hibrida terpadu dengan failover otomatis menggunakan rute akustik cadangan berbasis protokol routing dinamis OSPFv2.

---

## 🔬 Metodologi dan Hasil Kunci

### 1. Karakterisasi Kanal Monte Carlo
* Melacak transmisi $3 \times 10^5$ paket foton per titik pengujian pada empat tipe perairan (*pure sea, clear ocean, coastal, harbor*).
* Memvalidasi bahwa rumus analitis *Beer-Lambert* mengabaikan efek geometris berkas cahaya (deviasi hingga $13,5\text{ dB}$ pada jarak $20\text{ m}$).
* Hasil redaman simulasi terverifikasi presisi terhadap literatur acuan internasional (*Gabriel et al., 2011*): $-26,5\text{ dB}$ berbanding $-28,0\text{ dB}$ pada perairan *clear ocean $20\text{ m}$*.

### 2. Evaluasi Model Deep Learning CNN-Autoencoder
* Model neural network *end-to-end* dirancang dengan lapisan aktivasi *sigmoid* guna memastikan sinyal intensitas optik bersifat unipolar non-negatif.
* Pada kondisi turbulensi sedang ($\sigma_I^2 = 0,75$ pada $E_b/N_0 = 10\text{ dB}$), model CNN-Autoencoder berhasil menurunkan nilai BER dari **$0,066$ menjadi $0,029$**.
* Analisis batasan model menunjukkan adanya *error floor* pada kondisi turbulensi kuat ($\sigma_I^2 = 2,03$), yang mengonfirmasi batas teoritis kompensasi *fading* ekstrem tanpa diversitas ruang tambahan.

### 3. Jaringan Hibrida Optik-Akustik & Analisis Failover
* Integrasi jalur utama UOWC dengan jalur cadangan akustik menggunakan protokol routing dinamis OSPFv2 (metrik biaya rute 1 berbanding 100).
* Pengujian menunjukkan *convergence time* peralihan rute otomatis sebesar $\approx 40\text{ detik}$ saat tautan optik mengalami *los of sight* atau interupsi fisik, menjamin kelangsungan transmisi data telemetri dasar laut.

---

## 📂 Struktur Repositori

```text
├── docs/
│   └── Paper_UOWC_CNN_AE_Azlan_Alvian.pdf    # Naskah lengkap paper ilmiah (PDF format)
├── optisystem/                                # File simulasi OptiSystem
│   ├── uowc_linkbudget.osd                    # Desain rangkaian OptiSystem (.osd)
│   └── optisystem_layout.png                  # Diagram skema layout optik OptiSystem
├── src/                                       # Seluruh kode sumber simulasi & model
│   ├── monte_carlo_uowc.py                    # Engine simulasi propagasi foton
│   ├── cnn_ae_uowc.py                         # Arsitektur & pelatihan model PyTorch CNN-AE
│   ├── hybrid_network.py                      # Pemodelan failover jaringan hibrida
│   ├── run_channel_sims.py                    # Pipeline simulasi rugi kanal
│   ├── run_dispersion.py                      # Pipeline perhitungan RMS delay spread
│   └── run_cnn_ae.py                          # Pipeline evaluasi kurva BER vs SNR
├── models/                                    # Bobot model terlatih PyTorch (.pt)
│   ├── ae_lemah.pt                            # Model terlatih turbulensi lemah
│   ├── ae_sedang.pt                           # Model terlatih turbulensi sedang
│   └── ae_kuat.pt                             # Model terlatih turbulensi kuat
├── data/                                      # Data numerik mentah (.csv & .json)
├── figs/                                      # 16 visualisasi grafik resolusi tinggi (PNG)
├── TUTORIAL_OPTISYSTEM.md                     # Panduan simulasi OptiSystem
├── TUTORIAL_PACKET_TRACER.md                  # Panduan simulasi jaringan OSPF
├── requirements.txt                           # Daftar dependensi Python
└── jalankan_semuanya.sh                       # Skrip otomasi reproduksi hasil riset
```

---

## 🛠️ Panduan Instalasi dan Menjalankan Kode

### 1. Persiapan Lingkungan (Environment Setup)
Pastikan Python 3.10+ telah terpasang pada sistem operasi:

```bash
# Clone repositori
git clone https://github.com/Xloress/uowc-monte-carlo-cnnae.git
cd uowc-monte-carlo-cnnae

# Buat virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Pasang dependensi
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 2. Menjalankan Simulasi Per Bagian
Eksekusi modul dapat dilakukan secara independen sesuai fokus analisis:

```bash
# 1. Validasi simulator Monte Carlo terhadap literatur Gabriel (2011)
python src/monte_carlo_uowc.py

# 2. Simulasi rugi kanal dan perbandingan link budget (Fig. 1 & Fig. 5)
python src/run_channel_sims.py

# 3. Simulasi respon impuls dan dispersi multipath (Fig. 2, 3, & 4)
python src/run_dispersion.py

# 4. Evaluasi kurva BER model CNN-Autoencoder menggunakan checkpoint terlatih
python src/run_cnn_ae.py figs

# 5. Simulasi dinamika failover jaringan hibrida optik-akustik
python src/hybrid_network.py
```

Seluruh grafik keluaran akan tersimpan otomatis di direktori `figs/`.

---

## 📊 Pemetaan Gambar Hasil Riset

| Gambar | Keterangan Parameter Teknis |
|:---|:---|
| `fig1_redaman_vs_jarak.png` | Karakteristik rugi kanal terhadap jarak pada 4 tipe perairan |
| `fig5_linkbudget_3model.png` | Perbandingan model analitis Beer-Lambert vs Monte Carlo |
| `fig2_impulse_response.png` | Respon impuls kanal optik pada jarak transmisi $20\text{ m}$ |
| `fig3_aperture.png` | Pengaruh diameter aperture penerima terhadap penerimaan foton |
| `fig4_dispersi.png` | Karakteristik pelebaran waktu sinyal (*RMS delay spread*) |
| `fig6_ber_vs_snr.png` | Kurva kinerja BER vs $E_b/N_0$ pada berbagai kondisi turbulensi |
| `fig7_ber_vs_turbulensi.png`| Evaluasi performa model CNN-AE terhadap variasi indeks sintilasi |
| `fig8_failover_timeline.png`| Dinamika waktu transisi (*convergence*) failover rute OSPF |
| `fig9_throughput_latensi.png`| Karakteristik throughput dan latensi sistem hibrida terpadu |

---

## 📈 Validasi & Keterbatasan Ilmiah

* **Keterlacakan Hasil (Reproducibility):** Seluruh proses stokastik Monte Carlo dan inisialisasi jaringan syaraf tiruan dikunci menggunakan *fixed random seed* (`seed=0, 7, 11, 23, 123`) untuk memastikan hasil numerik dapat direproduksi secara bit-identik.
* **Batas Deteksi Foton:** Nilai atenuasi $\le -300\text{ dB}$ pada simulasi merepresentasikan ketiadaan foton yang mencapai aperture penerima, bukan nilai daya kontinu nyata.
* **Evaluasi Transparansi Model:**
  * *Error Floor* pada turbulensi kuat ($\sigma_I^2 = 2,03$) merupakan karakteristik alami keterbatasan modulasi intensitas optik tunggal pada fluktuasi acak ekstrem.
  * Durasi *dead-time* $40\text{ detik}$ pada failover rute OSPF adalah konsekuensi dari timer standar *Dead Interval* OSPFv2, yang mengindikasikan perlunya protokol deteksi jalur cepat (*Bidirectional Forwarding Detection* / BFD) untuk implementasi taktis lanjutan.
