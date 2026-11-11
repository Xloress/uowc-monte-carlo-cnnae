"""
Bangun deck presentasi UOWC (16:9) dengan gambar hasil simulasi.

Keluaran: PRESENTASI_UOWC.pptx
"""

import json
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figs")
DAT = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "PRESENTASI_UOWC.pptx")

W, H = Inches(13.333), Inches(7.5)
DARK = RGBColor(0x0F, 0x2A, 0x3D)
ACCENT = RGBColor(0x1B, 0x9A, 0xAA)
GREY = RGBColor(0x44, 0x44, 0x44)


def load_json(name, default=None):
    p = os.path.join(DAT, name)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return default


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def txbox(slide, left, top, width, height, text, size=18, bold=False,
          color=GREY, align=PP_ALIGN.LEFT, font="Calibri"):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = font
    return tb


def bullets(slide, left, top, width, height, items, size=17, color=GREY):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for it in items:
        lvl = 0
        txt = it
        if isinstance(it, tuple):
            txt, lvl = it
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = lvl
        p.space_after = Pt(10 if lvl == 0 else 5)
        r = p.add_run()
        r.text = ("• " if lvl == 0 else "– ") + txt
        r.font.size = Pt(size - 2 * lvl)
        r.font.color.rgb = color
        r.font.name = "Calibri"
    return tb


def header(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(1, 0, 0, W, Inches(1.15))
    bar.fill.solid()
    bar.fill.fore_color.rgb = DARK
    bar.line.fill.background()
    txbox(slide, Inches(0.5), Inches(0.22), Inches(12.3), Inches(0.8),
          title, size=28, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    if subtitle:
        txbox(slide, Inches(0.55), Inches(1.25), Inches(12), Inches(0.5),
              subtitle, size=14, color=ACCENT, bold=True)


def footer(slide, n, total):
    txbox(slide, Inches(11.6), Inches(7.0), Inches(1.4), Inches(0.35),
          f"{n} / {total}", size=11, color=RGBColor(0x99, 0x99, 0x99),
          align=PP_ALIGN.RIGHT)


def figure_slide(prs, n, total, title, img, points, subtitle=None,
                 img_w=6.6):
    s = blank(prs)
    header(s, title, subtitle)
    path = os.path.join(FIG, img)
    if os.path.exists(path):
        s.shapes.add_picture(path, Inches(0.45), Inches(1.85),
                             width=Inches(img_w))
    bullets(s, Inches(0.45 + img_w + 0.25), Inches(1.9),
            Inches(12.4 - img_w - 0.3), Inches(4.8), points, size=15)
    footer(s, n, total)
    return s


def build():
    ae = load_json("summary_ae.json", {})
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    TOTAL = 15

    # ------------------------------------------------ 1. judul
    s = blank(prs)
    bg = s.shapes.add_shape(1, 0, 0, W, H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK
    bg.line.fill.background()
    txbox(s, Inches(0.9), Inches(2.0), Inches(11.5), Inches(1.9),
          "OPTIMALISASI KOMUNIKASI OPTIK NIRKABEL\nBAWAH AIR (UOWC)",
          size=40, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    txbox(s, Inches(0.95), Inches(3.85), Inches(11.5), Inches(0.9),
          "Melalui Pemodelan CNN-AE dan Arsitektur Hibrida Akustik-Optik",
          size=22, color=ACCENT)
    txbox(s, Inches(0.95), Inches(5.2), Inches(11), Inches(1.2),
          "Kelompok 2  \u2022  Teknik Telekomunikasi\n"
          "Politeknik Negeri Bandung  \u2022  2026", size=16,
          color=RGBColor(0xCC, 0xDD, 0xDD))

    # ------------------------------------------------ 2. masalah + pertanyaan
    s = blank(prs)
    header(s, "Masalah & Empat Pertanyaan Penelitian")
    bullets(s, Inches(0.55), Inches(1.55), Inches(6.1), Inches(5.2), [
        "Akustik: jangkauan kilometer, bandwidth hanya kbps",
        ("1,33 detik untuk 2 km (v = 1500 m/s)", 1),
        "RF: teredam habis oleh konduktivitas air laut",
        ("jangkauan hanya sentimeter hingga beberapa meter", 1),
        "Optik (UOWC): Gbps, tetapi jangkauan puluhan meter",
        ("seberapa jauh, dan apa yang terjadi di ujungnya?", 1),
    ], size=15)
    items = [
        ("1", "Seberapa besar rugi kanal UOWC sebenarnya?",
         "Monte Carlo, empat tipe air, divalidasi ke literatur"),
        ("2", "Apakah rumus link budget analitis cukup?",
         "Beer-Lambert vs +geometris vs Monte Carlo"),
        ("3", "Seberapa parah turbulensi merusak sinyal?",
         "Model EGG lemah/sedang/kuat + restorasi CNN-AE"),
        ("4", "Bagaimana menutup jarak yang tersisa?",
         "Jaringan hibrida akustik-optik dengan failover OSPF"),
    ]
    y = Inches(1.72)
    for num, q, how in items:
        box = s.shapes.add_shape(1, Inches(6.9), y, Inches(5.95), Inches(1.15))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(0xF2, 0xF7, 0xF8)
        box.line.color.rgb = ACCENT
        txbox(s, Inches(7.05), y + Inches(0.14), Inches(0.6), Inches(0.9),
              num, size=26, bold=True, color=ACCENT)
        txbox(s, Inches(7.6), y + Inches(0.12), Inches(5.1), Inches(0.45),
              q, size=14, bold=True, color=DARK)
        txbox(s, Inches(7.6), y + Inches(0.62), Inches(5.1), Inches(0.42),
              how, size=12, color=GREY)
        y += Inches(1.27)
    footer(s, 2, TOTAL)

    # ------------------------------------------------ 3. kanal
    s = blank(prs)
    header(s, "Kanal Optik Bawah Air: Dua Mekanisme Atenuasi",
           "c(\u03bb) = a(\u03bb) + b(\u03bb)")
    bullets(s, Inches(0.6), Inches(1.95), Inches(6.0), Inches(4.6), [
        "Absorpsi a(\u03bb): foton diserap molekul air, garam, klorofil",
        "Hamburan b(\u03bb): arah rambat dibelokkan partikel tersuspensi",
        "Jendela optik: 450\u2013490 nm (jernih), 520\u2013550 nm (pesisir)",
        "Hamburan tidak selalu rugi \u2014 sebagian foton tetap sampai",
        ("inilah sebabnya model analitis gagal di perairan keruh", 1),
    ], size=16)
    rows = [("Pure sea", "0,053", "0,003", "0,056", "0,243"),
            ("Clear ocean", "0,069", "0,080", "0,150", "0,651"),
            ("Coastal", "0,088", "0,216", "0,305", "1,325"),
            ("Harbor", "0,295", "1,875", "2,170", "9,424")]
    tbl = s.shapes.add_table(5, 5, Inches(6.85), Inches(2.15),
                             Inches(6.0), Inches(2.2)).table
    for j, h in enumerate(["Tipe air", "a (m\u22121)", "b (m\u22121)",
                           "c (m\u22121)", "dB/m"]):
        c = tbl.cell(0, j)
        c.text = h
        c.text_frame.paragraphs[0].runs[0].font.size = Pt(12)
        c.text_frame.paragraphs[0].runs[0].font.bold = True
    for i, r in enumerate(rows, 1):
        for j, v in enumerate(r):
            c = tbl.cell(i, j)
            c.text = v
            c.text_frame.paragraphs[0].runs[0].font.size = Pt(12)
    txbox(s, Inches(6.85), Inches(4.55), Inches(6.0), Inches(1.6),
          "Catatan: c = 0,15 m\u22121 (clear ocean) setara 0,651 dB/m,\n"
          "bukan 0,151 dB/m. Kesalahan ini membuat simulasi\n"
          "terlalu optimistis 4\u00d7 lipat.",
          size=12, color=RGBColor(0xC0, 0x39, 0x2B))
    footer(s, 3, TOTAL)

    # ------------------------------------------------ 4. metodologi
    s = blank(prs)
    header(s, "Metodologi: Semua Hasil dari Simulasi Sendiri")
    bullets(s, Inches(0.6), Inches(1.55), Inches(6.1), Inches(5.2), [
        "Monte Carlo pelacakan foton (MCML)",
        ("\u03b4 = \u2212ln(\u03c7)/c, bobot \u00d7 (1 \u2212 a/c), sudut Henyey-Greenstein g = 0,924", 1),
        ("3\u00d7105 foton per konfigurasi, ambang bobot 10\u22124", 1),
        "Parameter: \u03bb = 532 nm, aperture 20 cm, \u03b80 = 1,75\u00b0, FOV 180\u00b0",
        "CNN-AE: 4 bit/simbol, 8 dimensi, 2500 langkah, Adam",
        "Validasi ke Gabriel (2011) Tabel II: selisih < 1,5 dB",
    ], size=16)
    box = s.shapes.add_shape(1, Inches(7.0), Inches(1.7), Inches(5.85),
                             Inches(4.6))
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(0xF2, 0xF7, 0xF8)
    box.line.color.rgb = ACCENT
    txbox(s, Inches(7.3), Inches(1.95), Inches(5.3), Inches(4.1),
          "Validasi model\n\n"
          "Clear ocean, Z = 20 m, D = 20 cm\n\n"
          "Gabriel (2011)  :  \u221228,0 dB\n"
          "Simulasi ini      :  \u221226,5 dB\n\n"
          "Pure sea, kondisi sama\n\n"
          "Gabriel (2011)  :  \u221220,6 dB\n"
          "Simulasi ini      :  \u221220,5 dB",
          size=14, color=DARK)
    footer(s, 4, TOTAL)

    # ------------------------------------------------ 5. hasil redaman
    figure_slide(prs, 5, TOTAL, "Rugi Kanal Tumbuh Eksponensial",
                 "fig1_redaman_vs_jarak.png", [
                     "Clear ocean: \u221226,5 dB @ 20 m, \u221249,0 dB @ 50 m",
                     "Coastal: \u221247,0 dB @ 30 m",
                     "Harbor: praktis tidak dapat dipakai > 15 m",
                     "Selisih antar tipe air jauh lebih besar daripada selisih jarak",
                     ("memilih rute AUV = memilih tipe air", 1),
                 ], subtitle="Monte Carlo, aperture 20 cm, \u03b80 = 1,75\u00b0",
                 img_w=6.4)

    # ------------------------------------------------ 6. link budget
    figure_slide(prs, 6, TOTAL, "Rumus Analitis Tidak Cukup",
                 "fig5_linkbudget_3model.png", [
                     "Beer-Lambert saja: \u221213,0 dB @ 20 m",
                     "Monte Carlo: \u221226,5 dB @ 20 m",
                     "Selisih 13,5 dB = rugi geometris yang tidak terlihat di rumus",
                     "Untuk berkas lebar, model analitis malah terlalu pesimistis",
                     ("foton terhambur tetap masuk aperture", 1),
                     "Kesimpulan: desain link harus pakai Monte Carlo atau ukur",
                 ], subtitle="Tiga model, kondisi identik", img_w=7.2)

    # ------------------------------------------------ 7. dispersi
    figure_slide(prs, 7, TOTAL, "Kanal Praktis Non-Dispersif?",
                 "fig2_impulse_response.png", [
                     "\u03c4_rms @20 m: 0,013 ns (jernih) \u2192 0,461 ns (keruh)",
                     "Simbol 1 Gbps hanya 1 ns \u2014 batas praktis 0,1 ns",
                     "Aman di 100 Mbps, tetapi 1 Gbps mulai butuh equalizer",
                     "Aperture 5\u219250 cm: daya +19,7 dB, dispersi ikut naik",
                     ("tidak ada yang gratis: margin vs kecepatan", 1),
                 ], subtitle="Impulse response, Z = 20 m", img_w=6.2)

    # ------------------------------------------------ 8. CNN-AE arsitektur
    s = blank(prs)
    header(s, "CNN-Autoencoder: Sistem sebagai Satu Jaringan Saraf")
    boxes = [("Input\n4 bit", 0.55, RGBColor(0xDD, 0xEE, 0xF0)),
             ("Encoder\nConv1D \u00d72\n+ Dense", 2.65, RGBColor(0xBB, 0xDD, 0xE2)),
             ("Power\nconstraint\n\u03c3(\u03b2s)", 4.75, RGBColor(0xFF, 0xE0, 0xB2)),
             ("Kanal\nI\u00b7s + n\nI ~ EGG", 6.85, RGBColor(0xFF, 0xCC, 0xCC)),
             ("Decoder\nDense +\nConv1D \u00d72", 8.95, RGBColor(0xBB, 0xDD, 0xE2)),
             ("Output\n16 simbol\nsoftmax", 11.05, RGBColor(0xDD, 0xEE, 0xF0))]
    for label, x, col in boxes:
        b = s.shapes.add_shape(1, Inches(x), Inches(2.3),
                               Inches(1.85), Inches(1.55))
        b.fill.solid()
        b.fill.fore_color.rgb = col
        b.line.color.rgb = DARK
        txbox(s, Inches(x + 0.05), Inches(2.55), Inches(1.75), Inches(1.2),
              label, size=12, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    for x in [2.42, 4.52, 6.62, 8.72, 10.82]:
        ar = s.shapes.add_shape(13, Inches(x), Inches(2.95), Inches(0.2),
                                Inches(0.25))
        ar.fill.solid()
        ar.fill.fore_color.rgb = ACCENT
        ar.line.fill.background()
    bullets(s, Inches(0.7), Inches(4.25), Inches(12.0), Inches(2.4), [
        "Sigmoid + soft-binarisasi menjaga sinyal non-negatif dan peak-limited",
        ("syarat fisis sinyal optik intensitas (IM/DD)", 1),
        "Kanal EGG dimasukkan sebagai lapisan tak terlatih di tengah jaringan",
        "Dibandingkan tiga skenario: dengan CSI, tanpa CSI, dan deteksi ambang",
    ], size=16)
    footer(s, 8, TOTAL)

    # ------------------------------------------------ 9. hasil AE
    i10 = None
    snrs = ae.get("snr_test", [])
    if snrs:
        i10 = snrs.index(10) if 10 in snrs else min(
            range(len(snrs)), key=lambda i: abs(snrs[i] - 10))
    res = ae.get("res", {})
    nocsi = ae.get("no_csi", {})
    pts = ["BER pada Eb/N0 = 10 dB:"]
    for cond in ["AWGN", "Lemah", "Sedang", "Kuat"]:
        if cond in res and i10 is not None:
            v = res[cond]["ae"][i10]
            pts.append((f"{cond}: CNN-AE {v:.1e}", 1))
    pts.append("Tanpa pengetahuan kanal:")
    for cond in ["Sedang", "Kuat"]:
        if cond in nocsi and i10 is not None:
            pts.append((f"{cond}: {nocsi[cond][i10]:.1e}", 1))
    pts.append("Penurunan relatif terbesar: turbulensi sedang (\u221256%)")
    figure_slide(prs, 9, TOTAL, "CNN-AE Menahan Degradasi Turbulensi",
                 "fig7_ber_vs_turbulensi.png", pts,
                 subtitle="BER vs indeks sintilasi", img_w=6.0)

    # ------------------------------------------------ 10. BER vs SNR
    figure_slide(prs, 10, TOTAL, "Kapan AI Menang, Kapan Tidak",
                 "fig6_ber_vs_snr.png", [
                     "Pada Eb/N0 = 10 dB, CNN-AE unggul di SEMUA kondisi",
                     ("AWGN: 10\u22126 vs 7,8\u00d710\u22124 (OOK ambang)", 1),
                     ("Turbulensi kuat: 9,2\u00d710\u22122 vs 1,4\u00d710\u22121", 1),
                     "Kurva CNN-AE selalu di bawah pembanding",
                     "Tetapi ada error floor di turbulensi kuat",
                     ("fading ekstrem tak bisa dipulihkan AI", 1),
                     "Pembanding kedua: CNN-AE tanpa pengetahuan kanal",
                 ], subtitle="Empat kondisi kanal", img_w=6.3)

    # ------------------------------------------------ 11. hibrida + failover
    figure_slide(prs, 11, TOTAL,
                 "Hibrida: Optik untuk Data, Akustik untuk Jangkauan",
                 "fig9_throughput_latensi.png", [
                     "Optik: 1 Gbps, latensi 0,09 ms @ 20 m",
                     "Akustik: 2,4 kbps, latensi 1,33 s @ 2 km",
                     "Selisih 6 orde throughput, 4 orde latensi",
                     "OSPF cost: optik 1, akustik 100 \u2192 optik selalu dipilih",
                     ("failover otomatis saat link optik padam", 1),
                     "Harganya: \u00b140 detik blackout saat konvergensi",
                     ("usulan: pengalihan proaktif berbasis prediksi kanal", 1),
                 ], subtitle="Jalur yang dipilih router (Z = 40 m)", img_w=6.6)

    # ------------------------------------------------ 12. software: apa & cara pakai
    figure_slide(prs, 12, TOTAL,
                 "Software Simulasi: Dikembangkan Sendiri, Bisa Dijalankan Ulang",
                 "fig14_struktur_paket.png", [
                     "11 modul Python, semua hasil di paper berasal dari sini",
                     ("bukan mengutip grafik jurnal", 1),
                     "Instal: venv + torch CPU + requirements.txt",
                     ("torch versi CPU ~200 MB, bukan ~2 GB versi CUDA", 1),
                     "Jalankan semua: bash jalankan_semuanya.sh",
                     ("~45–60 menit di CPU 2 core; mode fig tanpa training ~3 menit", 1),
                     "Semua path relatif — folder boleh dipindah atau diganti nama",
                     ("sudah diuji ekstrak dan jalankan dari folder lain", 1),
                     "Data mentah ikut: 20 CSV/JSON + 8 bobot model terlatih",
                 ], subtitle="Struktur paket & cara instalasi", img_w=6.6)

    # ------------------------------------------------ 13. software: bukti & validasi
    figure_slide(prs, 13, TOTAL,
                 "Bukti Kode & Validasi: Angka Bukan Karangan",
                 "fig15_kode_inti.png", [
                     "Inti simulator: pelacakan foton satu per satu (Monte Carlo)",
                     ("seed dikunci → hasil bisa direproduksi", 1),
                     "Divalidasi terhadap Gabriel dkk. (2011) Tabel II",
                     ("selisih < 2 dB, wajar lintas implementasi MC", 1),
                     "Uji 5 seed berbeda: simpangan baku 0,77–1,80 dB",
                     ("stabilitas simulasi terukur, bukan diklaim", 1),
                     "Reproduksibilitas terverifikasi: 15 PNG bit-identik",
                     ("dibandingkan SHA-256 setelah dijalankan dari paket zip", 1),
                 ], subtitle="Kode inti, output nyata, uji stabilitas", img_w=6.6)

    # ------------------------------------------------ 14. software: sesi terminal
    figure_slide(prs, 14, TOTAL,
                 "Sesi Terminal: dari Nol sampai Hasil",
                 "fig16_sesi_terminal.png", [
                     "Urutan nyata: venv → install → validasi → simulasi → dokumen",
                     "Uji reproduksibilitas dilakukan, bukan diasumsikan",
                     "Setiap angka di paper bisa dilacak ke script + baris perintah",
                     ("folder data/ berisi CSV/JSON mentahnya", 1),
                     "Tutorial OptiSystem & Packet Tracer ikut di paket",
                     ("untuk pembanding lintas-platform", 1),
                 ], subtitle="Rekaman eksekusi nyata di mesin ini", img_w=6.6)

    # ------------------------------------------------ 15. kesimpulan
    s = blank(prs)
    header(s, "Kesimpulan & Keterbatasan")
    bullets(s, Inches(0.6), Inches(1.6), Inches(12.2), Inches(5.2), [
        "UOWC layak sebagai kanal data utama pada puluhan meter",
        ("\u221226,5 dB @ 20 m, \u221249,0 dB @ 50 m (clear ocean)", 1),
        "Model analitis Beer-Lambert tidak memadai untuk desain",
        ("rugi geometris 13,5 dB tidak terlihat di rumus", 1),
        "Dispersi aman di 100 Mbps, ketat di 1 Gbps pada batas jangkauan",
        "CNN-AE bermanfaat pada turbulensi, tetapi bergantung pada kanal latih",
        ("salah pilih kanal latih = lebih buruk dari tanpa AI (1,5\u00d710\u22121 vs 1,4\u00d710\u22121)", 1),
        "Hibrida akustik-optik menutup jarak, dengan biaya blackout konvergensi",
        "Yang belum dikerjakan: air berlapis, turbulensi lapangan, emulator paket,",
        ("latensi inferensi di prosesor AUV, validasi eksperimen", 1),
    ], size=16)
    footer(s, 15, TOTAL)

    prs.save(OUT)
    print("tersimpan:", OUT, "|", len(prs.slides._sldIdLst), "slide")


if __name__ == "__main__":
    build()
