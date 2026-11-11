# README — Paket Paper & Presentasi UOWC Kelompok 2

Semua hasil di sini **dihasilkan dari simulasi sendiri**, bukan mengutip grafik
dari jurnal. Setiap angka di paper bisa dilacak ke script yang menghasilkannya.

## Isi paket

| File | Isi |
|---|---|
| `PAPER_UOWC_revisi.docx` | Paper revisi: 5 bab, 2 tabel, 14 gambar |
| `PRESENTASI_UOWC.pptx` | Deck 12 slide (16:9), siap presentasi |
| `TUTORIAL_OPTISYSTEM.md` | Langkah demi langkah praktikum link budget di OptiSystem |
| `TUTORIAL_PACKET_TRACER.md` | Langkah demi langkah failover OSPF di Packet Tracer |
| `paper_original.docx` | Draft awal (arsip, jangan dihapus) |
| `figs/` | 15 gambar hasil simulasi (PNG 160 dpi) |
| `data/` | Semua data mentah (CSV/JSON) |
| `src/` | Script Python yang menghasilkan semuanya |
| `models/` | Bobot model CNN-AE terlatih |
| `requirements.txt` | Daftar paket Python yang dibutuhkan |
| `jalankan_semuanya.sh` | Satu perintah membangun ulang semuanya |

## Cara menjalankan dari nol

```bash
cd <folder hasil ekstrak>
python3 -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
bash jalankan_semuanya.sh
```

## Cara menjalankan per bagian (tanpa install ulang)

```bash
source .venv/bin/activate          # atau pakai .venv/bin/python langsung

python src/monte_carlo_uowc.py     # validasi ke Gabriel 2011   (<1 detik)
python src/run_channel_sims.py     # fig1, fig5 + data redaman  (~110 detik)
python src/run_dispersion.py       # fig2, fig3, fig4            (~5 detik)
python src/hybrid_network.py       # model failover + data       (<1 detik)
python src/run_network_figs.py     # fig8, fig9                  (<1 detik)
python src/run_extra_figs.py       # fig10-13                    (~5 detik)
python src/run_cnn_ae.py figs      # fig6, fig7, fig8 (cepat, dari data + models/)
python src/build_paper.py          # bangun PAPER_UOWC_revisi.docx
python src/build_ppt.py            # bangun PRESENTASI_UOWC.pptx
```

**Urutan penting:** `run_channel_sims.py` harus jalan lebih dulu karena
`hybrid_network.py` membaca `data/attenuation_vs_distance.csv`.

**Waktu total:** 45-60 menit di CPU 2 core. Paling lama CNN-AE training
(`run_cnn_ae.py all`, ~20 menit). Bobot model yang sudah terlatih ada di
`models/`, jadi pakai mode `figs` kalau tidak mau menunggu training.

## Pemetaan gambar ke bagian paper

| Gambar | Isi | Bab |
|---|---|---|
| fig1_redaman_vs_jarak | Rugi kanal vs jarak, 4 tipe air | 4.1 |
| fig5_linkbudget_3model | Beer-Lambert vs geometris vs Monte Carlo | 4.1 |
| fig2_impulse_response | IR pada Z = 20 m | 4.2 |
| fig3_aperture | IR vs diameter aperture | 4.2 |
| fig4_dispersi | RMS delay spread vs jarak | 4.2 |
| fig4_tau_vs_jarak | Tau vs jarak | 4.2 |
| fig6_ber_vs_snr | BER vs Eb/N0, 4 kondisi | 4.3 |
| fig7_ber_vs_turbulensi | BER vs indeks sintilasi | 4.3 |
| fig8_channel_aware_gain | Manfaat pengetahuan kanal | 4.3 |
| fig8_failover_timeline | Timeline failover | 4.4 |
| fig9_throughput_latensi | Throughput & latensi vs jarak | 4.4 |
| fig10_skema_sistem | Skema sistem UOWC | 2 |
| fig11_sintilasi_egg | Distribusi sintilasi EGG | 4.3 |
| fig12_foton_diterima | Jumlah foton diterima vs jarak | 4.1 |
| fig13_deviasi_model | Deviasi MC vs model analitis | 4.1 |

## Validasi model (penting untuk sidang)

Simulator Monte Carlo divalidasi terhadap Tabel II Gabriel dkk. (2011),
kondisi lambda = 532 nm, Z = 20 m, D = 20 cm. Jalankan:

```bash
python src/monte_carlo_uowc.py
```

Keluar dalam <1 detik. Kalau penguji meminta bukti simulatornya bukan
karangan, ini yang ditunjukkan.

## Reproduksibilitas

Semua seed dikunci di dalam script (`seed=0`, `7`, `11`, `23`, `123`).
Menjalankan ulang dengan versi library yang sama menghasilkan file PNG
**bit-identik** (terverifikasi SHA-256). DOCX/PPTX juga identik isinya;
byte-nya berbeda hanya karena timestamp zip.

## Catatan data (jangan sampai salah kutip)

- `-300 dB` adalah penanda "nol foton terdeteksi", BUKAN nilai rugi nyata.
  Titik seperti itu tidak diplot di fig1/fig5.
- Titik dengan <10 foton terdeteksi adalah noise Monte Carlo (ketidakpastian
  1/sqrt(N) = 33-100%), tidak boleh dipakai sebagai angka.
- Harbor dengan c = 2,17 m⁻¹ butuh ~10⁹ foton untuk estimasi stabil di 10 m;
  dengan 3×10⁵ foton hasilnya hanya kualitatif.
- Angka yang aman dikutip: Coastal -47,0 dB @ 30 m dan Clear ocean
  -26,5 dB @ 20 m (keduanya >200 foton terdeteksi).

## Catatan kejujuran ilmiah

Dua hal yang sengaja ditampilkan apa adanya dan **jangan dihapus**:

- **Error floor CNN-AE** pada turbulensi kuat. Model tidak bisa
  menyelamatkan simbol yang fading-nya ekstrem. Klaim "AI menyelesaikan
  semuanya" akan langsung dipatahkan grafik sendiri.
- **Blackout 40 detik** pada failover OSPF. Ini kelemahan nyata arsitektur
  reaktif, dan justru menjadi dasar usulan riset lanjutan.

Menampilkan keduanya membuat paper lebih kuat, bukan lebih lemah.
