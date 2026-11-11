#!/usr/bin/env bash
# jalankan_semuanya.sh — bangun ulang seluruh data, grafik, paper, dan slide
# dari nol (atau lanjutkan dari hasil yang sudah ada).
#
# Cara pakai:
#   bash jalankan_semuanya.sh
#
# Urutan penting: run_channel_sims.py harus jalan lebih dulu karena
# hybrid_network.py membaca data/attenuation_vs_distance.csv.
#
# Total waktu: sekitar 45-60 menit di CPU 2 core (paling lama CNN-AE ~20 menit).
# Untuk melewati training CNN-AE (pakai bobot model yang sudah ada di models/):
#   bash jalankan_semuanya.sh fig

set -e
cd "$(dirname "$0")"

# Pakai virtualenv kalau ada, kalau tidak pakai python3 biasa
if [ -x ".venv/bin/python" ]; then
    PY=.venv/bin/python
else
    PY=python3
fi

# Argumen "fig" = lewati training CNN-AE, hanya bangun grafik dari data tersimpan
if [ "$1" = "fig" ]; then
    AE_MODE="figs"
    AE_LABEL="dari data tersimpan (tanpa training)"
else
    AE_MODE="all"
    AE_LABEL="latih model + bangun grafik"
fi

echo "==> Python: $($PY -V)"
echo "==> Mode CNN-AE: $AE_LABEL"

echo "==> [1/8] Uji cepat Monte Carlo (validasi ke Gabriel 2011)"
$PY src/monte_carlo_uowc.py

echo "==> [2/8] Kanal optik: fig1, fig5 + data redaman"
$PY src/run_channel_sims.py

echo "==> [3/8] Dispersi + aperture: fig2, fig3, fig4"
$PY src/run_dispersion.py

echo "==> [4/8] Jaringan hibrida: data failover + sweep jarak"
$PY src/hybrid_network.py

echo "==> [5/8] Gambar jaringan: fig8 failover, fig9 throughput"
$PY src/run_network_figs.py

echo "==> [6/8] Gambar tambahan: fig10, fig11, fig12, fig13"
$PY src/run_extra_figs.py

echo "==> [7/8] Gambar software: fig14, fig15, fig16 (untuk slide)"
$PY src/run_software_figs.py

echo "==> [8/8] CNN-AE: $AE_LABEL, fig6, fig7, fig8 + data"
if [ "$AE_MODE" = "all" ]; then
    echo "    (butuh waktu paling lama, ~20 menit di CPU; Ctrl+C aman,"
    echo "     setiap kondisi disimpan terpisah dan bisa dilanjutkan)"
fi
$PY src/run_cnn_ae.py $AE_MODE

echo "==> Bangun dokumen"
$PY src/build_paper.py
$PY src/build_ppt.py

echo
echo "Selesai. Hasil:"
echo "  PAPER_UOWC_revisi.docx   (dokumen paper)"
echo "  PRESENTASI_UOWC.pptx     (deck presentasi)"
echo "  figs/                    (semua grafik PNG)"
echo "  data/                    (semua data mentah CSV/JSON)"
echo "  models/                  (bobot CNN-AE terlatih)"
