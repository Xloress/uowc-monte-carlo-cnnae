"""
Paper UOWC — struktur 6 bagian sesuai instruksi tugas dosen.

Format wajib:
  - Kertas A4, Times New Roman 12, spasi 1,5
  - Margin kiri 4 cm, kanan 2 cm, atas/bawah 2 cm
  - 9-12 halaman termasuk kover
  - Struktur: (1) Pendahuluan & tujuan 1-2 hal, (2) Cara kerja/spesifikasi
    0,5-1 hal, (3) Penggunaan & data pengujian 2 hal, (4) Analisis sistem
    1-2 hal, (5) Kesimpulan 1 hal, (6) Pustaka 3-5 sumber 1 hal.
  - PDF final; file ini membangun DOCX yang dikonversi ke PDF.
"""

import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "PAPER_UOWC_revisi.docx")
FIG = os.path.join(ROOT, "figs")

PAGE_W_CM, PAGE_H_CM = 21.0, 29.7
MARGIN_LEFT, MARGIN_OTHER = 4.0, 2.0
FONT_PT = 12
LINE_SPACING = 1.5
FIG_MAX_IN = 4.20         # 13,6 cm, selebar kolom teks (15 cm) dikurangi sedikit


def set_page(doc):
    for s in doc.sections:
        s.page_width = Cm(PAGE_W_CM)
        s.page_height = Cm(PAGE_H_CM)
        s.left_margin = Cm(MARGIN_LEFT)
        s.right_margin = Cm(MARGIN_OTHER)
        s.top_margin = Cm(MARGIN_OTHER)
        s.bottom_margin = Cm(MARGIN_OTHER)


def set_base_style(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(FONT_PT)
    st.paragraph_format.space_after = Pt(0)
    st.paragraph_format.space_before = Pt(0)
    st.paragraph_format.line_spacing = LINE_SPACING
    for name, size in [("Heading 1", 12), ("Heading 2", 12), ("Title", 14)]:
        s = doc.styles[name]
        s.font.name = "Times New Roman"
        s.font.size = Pt(size)
        s.font.color.rgb = RGBColor(0, 0, 0)
        s.font.bold = True
        s.paragraph_format.space_before = Pt(4)
        s.paragraph_format.space_after = Pt(2)
        s.paragraph_format.line_spacing = 1.0


def add_caption(doc, text):
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    for r in p.runs:
        r.font.size = Pt(9.5)
        r.font.italic = True
    return p


def add_figure(doc, filename, caption, width=FIG_MAX_IN):
    path = os.path.join(FIG, filename)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_picture(path, width=Inches(min(width, FIG_MAX_IN)))
    add_caption(doc, caption)


def add_table(doc, header, rows, caption, font=10):
    add_caption(doc, caption)
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(font)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(v))
            run.font.size = Pt(font)
            cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    return t


def para(doc, text, justify=True, first_indent=True):
    p = doc.add_paragraph(text)
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if first_indent:
        p.paragraph_format.first_line_indent = Inches(0.3)
    return p


def formula(doc, text):
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].italic = True
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    return p


def build():
    doc = Document()
    set_page(doc)
    set_base_style(doc)

    # ------------------------------------------------------------ kover
    for _ in range(3):
        doc.add_paragraph()
    title = doc.add_paragraph(
        "OPTIMALISASI KOMUNIKASI OPTIK NIRKABEL BAWAH AIR (UOWC) "
        "MELALUI PEMODELAN CNN-AE DAN ARSITEKTUR HIBRIDA AKUSTIK-OPTIK")
    title.style = doc.styles["Title"]
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()
    for line in ["Disusun Oleh:",
                 "1. ........................................ (NIM. ................)",
                 "2. ........................................ (NIM. ................)",
                 "",
                 "Program Studi Teknik Telekomunikasi, Jurusan Teknik Elektro",
                 "Politeknik Negeri Bandung",
                 "2026"]:
        p = doc.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
    doc.add_page_break()

    # ========================================== 1. PENDAHULUAN DAN TUJUAN
    doc.add_heading("1. PENDAHULUAN DAN TUJUAN", level=1)
    para(doc,
         "Banyak pekerjaan bawah laut kini dikerjakan mesin, bukan penyelam. "
         "Kendaraan tanpa awak (AUV) dan sensor dasar laut harus saling "
         "bertukar data dengan cepat. Gelombang akustik jadi pilihan utama "
         "karena mampu menempuh kilometer dengan redaman kecil. Namun suara "
         "punya batas. Rambatnya hanya 1500 m/s sehingga 2 km butuh 1,33 "
         "detik, bandwidth praktisnya hanya orde kilohertz, dan daya "
         "pancarnya besar [1].")

    para(doc,
         "Gelombang radio juga bukan jawabannya. Air laut konduktif karena "
         "garam, dan konduktivitas itulah yang menyerap gelombang "
         "elektromagnetik sehingga sinyal RF hanya bertahan beberapa "
         "sentimeter sampai meter [1]. Tabel 1 merangkum ketiga pilihan "
         "tersebut.")

    add_table(doc,
              ["Parameter", "Akustik", "RF", "Optik (UOWC)"],
              [["Frekuensi pembawa", "10\u2013100 kHz", "1\u2013100 MHz", "532 nm"],
               ["Bandwidth praktis", "kbps", "sangat terbatas", "Mbps \u2013 Gbps"],
               ["Jangkauan", "hingga 10 km", "< 10 m", "10\u2013100 m"],
               ["Latensi @1 km", "\u2248 667 ms", "\u2248 3,3 \u03bcs", "\u2248 4,4 \u03bcs"],
               ["Kendala utama", "bandwidth, latensi", "redaman ekstrem",
                "jarak, alignment"]],
              "Tabel 1. Perbandingan tiga moda komunikasi nirkabel bawah air "
              "[1]. Latensi optik 4,4 \u03bcs/km dihitung dari v = c/n = "
              "2,26\u00d7108 m/s; angka ini sering salah ditulis 4,4 ms.")

    para(doc,
         "UOWC (Underwater Optical Wireless Communication) menjawab "
         "kebuntuan itu. UOWC memakai cahaya biru-hijau 450\u2013550 nm yang "
         "paling sedikit diserap air laut, sehingga sanggup mengirim data "
         "sampai orde Gigabit per detik pada jarak puluhan meter. Ada tiga "
         "persoalan yang harus dibereskan lebih dulu, yaitu karakterisasi "
         "kanal, degradasi akibat turbulensi, dan keterbatasan jarak.")

    para(doc, "Tujuan penulisan paper ini adalah:")
    for i2, t in enumerate([
        "Menelaah perilaku kanal bawah air lewat simulasi Monte Carlo yang "
        "mencakup absorpsi, hamburan, dan pelebaran waktu sinyal.",
        "Membandingkan link budget analitis dengan simulasi untuk melihat "
        "seberapa jauh rumus sederhana bisa dipercaya.",
        "Menguji CNN-Autoencoder untuk menekan kesalahan bit akibat "
        "turbulensi.",
        "Menyusun skema hibrida akustik-optik dengan peralihan otomatis "
        "agar kecepatan dan jangkauan didapat sekaligus."]):
        p2 = doc.add_paragraph(f"{i2+1}. {t}")
        p2.paragraph_format.left_indent = Inches(0.4)
        p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # ================================== 2. CARA KERJA DAN SPESIFIKASI
    doc.add_heading("2. CARA KERJA DAN SPESIFIKASI SISTEM", level=1)
    para(doc,
         "Gambar 1 merangkum alur sistem yang dimodelkan. Alurnya terdiri "
         "dari tautan optik dari pemancar AUV ke penerima, rantai CNN-AE "
         "yang dilatih bersama kanalnya, dan jalur akustik cadangan yang "
         "diaktifkan OSPF.")

    add_figure(doc, "fig10_skema_sistem.png",
               "Gambar 1. Skema sistem, terdiri atas tautan optik, rantai "
               "end-to-end, dan jalur akustik cadangan.")

    para(doc,
         "Ada dua hal yang terjadi pada cahaya saat masuk ke air. Yang "
         "pertama absorpsi, yaitu foton diserap molekul air, garam, atau "
         "pigmen fitoplankton lalu hilang sebagai panas. Yang kedua "
         "hamburan, yaitu arah foton dibelokkan partikel tersuspensi. "
         "Keduanya digabung menjadi koefisien atenuasi total "
         "c(\u03bb) = a(\u03bb) + b(\u03bb), dan tanpa hamburan daya yang "
         "tersisa mengikuti Hukum Beer-Lambert L_P = exp(\u2212c\u00b7z). "
         "Rumus ini membuang bagian terpenting. Di perairan keruh hamburan "
         "justru dominan, dan foton yang sudah terhambur masih bisa masuk "
         "aperture. Konsekuensinya diuji di Bab 3.")

    para(doc,
         "Suhu dan salinitas laut tidak seragam, sehingga indeks bias air "
         "berubah sepanjang lintasan dan intensitas di penerima naik-turun "
         "seperti lampu yang digoyang. Gejala ini disebut sintilasi dan "
         "dinyatakan dengan indeks \u03c3_I2 yang merupakan varians "
         "intensitas ternormalisasi. Fluktuasinya dibangkitkan dari "
         "distribusi Exponential-Generalized Gamma (EGG) [3] dengan "
         "parameter terkalibrasi untuk \u03c3_I2 = 0,20 (lemah), 0,75 "
         "(sedang), dan 2,03 (kuat), lalu diverifikasi ulang dengan 400.000 "
         "sampel tiap eksekusi (Gambar 2).")

    add_figure(doc, "fig11_sintilasi_egg.png",
               "Gambar 2. Kanal sintilasi EGG, yaitu realisasi waktu "
               "ternormalisasi untuk turbulensi lemah, sedang, dan kuat, "
               "serta sebaran peluangnya.")

    para(doc,
         "Link budget sederhananya adalah pembukuan daya, yaitu berapa "
         "yang dikirim, berapa yang hilang di jalan, dan berapa yang "
         "sampai.")
    formula(doc, "P_r = P_t + G_t + G_r + L_s + L_n")
    para(doc,
         "P_t adalah daya pancar dalam dBm, G_t dan G_r adalah penguatan "
         "geometris pemancar dan aperture penerima, L_s adalah rugi kanal, "
         "serta L_n adalah rugi derau latar. Perlu dicatat bahwa P_r "
         "merupakan daya, bukan SNR.")

    para(doc,
         "Pada CNN-Autoencoder end-to-end [4], seluruh sistem komunikasi "
         "dilihat sebagai satu jaringan saraf. Encoder belajar memilih "
         "bentuk simbol yang tahan gangguan, kanal fisik menjadi lapisan "
         "tak terlatih, dan decoder memulihkan bit. Karena sinyal optik tak "
         "mungkin negatif, keluaran encoder dilewatkan sigmoid lalu dayanya "
         "dinormalisasi.")

    add_table(doc,
              ["Komponen", "Parameter", "Nilai"],
              [["Pemancar", "Panjang gelombang \u03bb", "532 nm"],
               ["", "Setengah sudut divergensi \u03b80", "1,75\u00b0"],
               ["Kanal", "Tipe air", "pure sea, clear ocean, coastal, harbor"],
               ["", "Parameter Henyey-Greenstein g", "0,924"],
               ["Penerima", "Diameter aperture D", "0,5\u201350 cm (default 20 cm)"],
               ["Monte Carlo", "Jumlah foton", "3\u00d7105 (6\u00d7105 untuk Z \u2265 80 m)"],
               ["CNN-AE", "Bit per simbol k", "4 (16 simbol)"],
               ["", "Pelatihan", "2500 langkah, Adam, lr 10\u22123, batch 256"]],
              "Tabel 2. Parameter simulasi Monte Carlo dan CNN-AE.")

    para(doc,
         "Simulator menembakkan foton satu per satu. Tiap foton diberi "
         "jarak tempuh bebas, bobotnya menyusut setiap tumbukan, dan arah "
         "pasca-tumbukan diambil dari fungsi fase Henyey-Greenstein. Foton "
         "dianggap diterima bila melintasi bidang penerima di dalam "
         "aperture dan medan pandang, sedangkan waktu tibanya dihitung dari "
         "panjang lintasan dibagi kecepatan cahaya dalam air "
         "(2,26\u00d7108 m/s). Hasilnya diuji terhadap Tabel II pada [2], "
         "yaitu \u221226,5 dB untuk clear ocean 20 m (literatur "
         "\u221228,0 dB) dan \u221220,5 dB untuk pure sea (literatur "
         "\u221220,6 dB). Selisih di bawah 1,5 dB ini wajar karena model "
         "fase berbeda dari acuan.")

    # ========================= 3. PENGGUNAAN SISTEM & DATA PENGUJIAN
    doc.add_heading("3. PENGGUNAAN SISTEM DAN DATA PENGUJIAN", level=1)
    para(doc,
         "Skenario yang dimodelkan adalah link garis lurus (line-of-sight) "
         "antara AUV dan stasiun pangkalan, atau antar dua node sensor, "
         "pada jarak 10\u2013100 m. Penerapannya meliputi pengiriman video "
         "inspeksi lambung kapal, unggahan data sensor oseanografi, dan "
         "kendali real-time AUV di sekitar rig lepas pantai. Bagian ini "
         "menyajikan data pengujian kanal, yaitu redaman, ketepatan model "
         "link budget, dan dispersi waktu.")

    para(doc,
         "Gambar 3 menunjukkan daya yang sampai di penerima untuk empat "
         "tipe air. Kurva Beer-Lambert yang digambar putus-putus jauh "
         "berbeda dari Monte Carlo. Pada clear ocean 20 m Beer-Lambert "
         "memberi \u221213,0 dB sementara Monte Carlo \u221226,5 dB. "
         "Selisih 13,5 dB itu bukan kesalahan hitung, melainkan rugi "
         "geometris karena berkas nyata melebar seiring jarak, dan hal itu "
         "tidak ada di rumus.")

    add_figure(doc, "fig1_redaman_vs_jarak.png",
               "Gambar 3. Intensitas diterima terhadap jarak untuk empat tipe "
               "air (\u03bb = 532 nm, aperture 20 cm, Monte Carlo), dengan "
               "garis putus-putus sebagai prediksi Beer-Lambert.")

    para(doc,
         "Gambar 4 membandingkan tiga model link budget pada kondisi "
         "identik. Untuk berkas sempit (\u03b80 = 1,75\u00b0), model "
         "analitis yang sudah ditambah rugi geometris masih mengikuti Monte "
         "Carlo dengan baik. Namun begitu berkas dilebarkan "
         "(\u03b80 > 5\u00b0), model itu terlalu pesimistis karena tidak "
         "menghitung foton terhambur yang tetap masuk aperture. Karena itu "
         "perancangan link UOWC perlu simulasi Monte Carlo, bukan rumus "
         "analitis sederhana.")

    add_figure(doc, "fig5_linkbudget_3model.png",
               "Gambar 4. (a) Tiga model link budget pada berkas sempit. "
               "(b) Penyimpangan model analitis ketika divergensi diperlebar "
               "(Z = 20 m).")

    para(doc,
         "Gambar 5 membandingkan penyimpangan yang tersisa. Penyimpangan "
         "tersebut adalah selisih prediksi analitis dan Monte Carlo untuk "
         "pure sea dan clear ocean di sepanjang jarak uji.")

    add_figure(doc, "fig13_deviasi_model.png",
               "Gambar 5. Selisih prediksi model analitis terhadap hasil "
               "Monte Carlo di sepanjang jarak, untuk pure sea dan clear "
               "ocean. Nilai positif berarti model melebih-lebihkan daya "
               "yang sampai di penerima.")

    para(doc,
         "Pulsa pendek yang dikirim sampai di penerima dalam bentuk lebih "
         "panjang karena sebagian foton berkelok akibat hamburan dan tiba "
         "terlambat. Pelebaran ini diukur dengan RMS delay spread "
         "\u03c4_rms. Pada Z = 20 m diperoleh 0,013 ns untuk pure sea, "
         "0,154 ns untuk clear ocean, dan 0,461 ns untuk coastal. Gambar 6 "
         "memperlihatkan pulsa melebar tersebut. Gambar 7 menunjukkan "
         "pertumbuhan \u03c4_rms terhadap jarak, yaitu dari 0,038 ns di "
         "10 m menjadi 1,03 ns di 50 m untuk clear ocean, sedangkan coastal "
         "sudah 2,9 ns di 30 m.")

    add_figure(doc, "fig2_impulse_response.png",
               "Gambar 6. Respons impuls kanal bawah air, yaitu pulsa yang "
               "dikirim melebar dan meredup setelah menempuh air "
               "(\u03bb = 532 nm, aperture 20 cm, clear ocean 20 m).")

    add_figure(doc, "fig4_dispersi.png",
               "Gambar 7. RMS delay spread terhadap jarak dan tipe air, "
               "dibandingkan ambang 0,1\u00b7T_sym pada 1 Gbps dan 100 Mbps.")

    para(doc,
         "Untuk menilai apakah ini masalah, angka tersebut dibandingkan "
         "dengan durasi satu simbol. Pada 1 Gbps satu simbol hanya 1 ns, "
         "sehingga batas praktis 0,1 ns sudah terlewati clear ocean sejak "
         "20 m dan coastal sejak 10 m. Pada 100 Mbps batasnya lebih longgar, "
         "yaitu 1 ns, dan clear ocean baru terlewati sekitar 50 m. Aperture "
         "juga berpengaruh. Dari 5 cm ke 50 cm daya terima naik 19,7 dB, "
         "tetapi dispersi ikut naik dari 0,10 ns ke 0,145 ns karena "
         "aperture lebar menangkap foton terhambur yang tiba terlambat.")

    add_figure(doc, "fig3_aperture.png",
               "Gambar 8. Bentuk pulsa terima untuk tiga diameter aperture "
               "(clear ocean, Z = 20 m). D = 0,5 cm tidak ditampilkan karena "
               "foton yang lolos terlalu sedikit untuk membentuk statistik "
               "yang sahih.")

    para(doc,
         "Gambar 9 menutup bagian ini dengan anggaran foton. Angka yang "
         "ditunjukkan adalah berapa foton yang benar-benar sampai ke "
         "aperture pada setiap jarak dan tipe air, dibandingkan ambang 50 "
         "foton agar hasil simulasi masih sahih secara statistik.")

    add_figure(doc, "fig12_foton_diterima.png",
               "Gambar 9. Jumlah foton diterima terhadap jarak untuk empat "
               "tipe air (3\u00d7105 foton ditembakkan per titik). Garis "
               "putus-putus menandai ambang 50 foton.")

    # ============================================ 4. ANALISIS SISTEM
    doc.add_heading("4. ANALISIS SISTEM", level=1)
    para(doc,
         "Gambar 10 membandingkan Bit Error Rate (BER) CNN-AE dengan "
         "deteksi ambang konvensional pada kanal AWGN dan tiga tingkat "
         "turbulensi. Pada Eb/N0 = 10 dB, CNN-AE mencapai BER "
         "1,0\u00d710\u22126 di kanal AWGN sementara deteksi ambang masih "
         "7,8\u00d710\u22124. Pada turbulensi sedang hasilnya "
         "2,9\u00d710\u22122 berbanding 6,6\u00d710\u22122, dan pada "
         "turbulensi kuat 9,2\u00d710\u22122 berbanding "
         "1,4\u00d710\u22121. Kurva CNN-AE berada di bawah pembanding pada "
         "semua kondisi.")

    add_figure(doc, "fig6_ber_vs_snr.png",
               "Gambar 10. BER terhadap Eb/N0 untuk CNN-AE dan deteksi ambang "
               "pada kanal AWGN dan turbulensi EGG lemah, sedang, dan kuat.")

    para(doc,
         "Perlu dinyatakan terbuka bahwa pada turbulensi kuat kurva CNN-AE "
         "mendatar (error floor) di kisaran 10\u22122\u201310\u22121 "
         "walau Eb/N0 dinaikkan. Sebabnya bukan kapasitas jaringan "
         "melainkan fading, yaitu sebagian simbol jatuh terlalu dalam "
         "sehingga informasinya hilang dan tidak bisa dipulihkan decoder "
         "apa pun. Jadi AI tidak menggantikan diversitas spasial atau "
         "tambahan daya pada turbulensi ekstrem.")

    para(doc,
         "Gambar 11 menguji arti pengetahuan kanal. Model yang dilatih pada "
         "kanal tanpa fading lalu diuji pada kanal EGG merosot jauh lebih "
         "cepat. Pada \u03c3_I2 = 2,03 BER-nya 1,5\u00d710\u22121 "
         "berbanding 9,2\u00d710\u22122 untuk model yang dilatih dengan "
         "statistik kanal yang benar. Pada turbulensi kuat, model tanpa "
         "pengetahuan kanal (1,5\u00d710\u22121) justru lebih buruk "
         "daripada deteksi ambang biasa (1,4\u00d710\u22121). Artinya, "
         "memakai AI dengan kanal latih yang salah hasilnya lebih buruk "
         "daripada tidak memakai AI sama sekali. Perbaikan relatif terbesar "
         "terjadi pada turbulensi sedang, yaitu 56 persen.")

    add_figure(doc, "fig7_ber_vs_turbulensi.png",
               "Gambar 11. BER pada Eb/N0 = 10 dB terhadap indeks sintilasi "
               "untuk CNN-AE, deteksi ambang, dan CNN-AE tanpa pengetahuan "
               "kanal.")

    add_figure(doc, "fig8_channel_aware_gain.png",
               "Gambar 12. Perbandingan BER CNN-AE dengan dan tanpa "
               "pengetahuan kanal pada tiga tingkat turbulensi, dengan rasio "
               "perbaikan 1,41\u00d7 / 2,10\u00d7 / 1,65\u00d7 pada "
               "turbulensi lemah / sedang / kuat.")

    para(doc,
         "Karena rugi kanal optik naik cepat terhadap jarak, jangkauan UOWC "
         "berhenti di puluhan meter, padahal misi AUV sering mencakup "
         "kilometer, sehingga akustik kembali dibutuhkan [5]. Mekanisme "
         "peralihan diuji dengan OSPF. Antarmuka optik diberi cost 1 dan "
         "akustik cost 100, sehingga router selalu memilih optik selama "
         "link optik hidup. Ketika AUV masuk perairan keruh dan link optik "
         "padam, OSPF menghitung ulang dan berpindah ke jalur akustik. "
         "Gambar 13 memperlihatkan harganya, yaitu selama konvergensi OSPF "
         "selama sekitar 40 detik trafik terputus total.")

    add_figure(doc, "fig8_failover_timeline.png",
               "Gambar 13. Timeline failover, yaitu throughput dan latensi "
               "selama peralihan optik \u2192 akustik \u2192 optik "
               "(Z = 40 m, konvergensi OSPF 40 s).")

    para(doc,
         "Gambar 14 merangkum alasan seluruh rancangan ini dibuat. Pada "
         "20 m jalur optik memberi throughput 1 Gbps dengan latensi 0,09 ms. "
         "Pada 2 km jalur akustik hanya memberi 2,4 kbps dengan latensi "
         "1,33 s. Selisihnya enam orde untuk throughput dan empat orde untuk "
         "latensi, dan tidak ada satu moda pun yang bisa menutup rentang "
         "sebesar itu sendirian.")

    add_figure(doc, "fig9_throughput_latensi.png",
               "Gambar 14. Throughput dan latensi jalur yang dipilih router "
               "terhadap jarak, untuk clear ocean dan coastal.")

    para(doc,
         "Beberapa keterbatasan perlu dicatat. Simulasi mengabaikan "
         "polarisasi cahaya dan menganggap air seragam, padahal perairan "
         "nyata berlapis secara vertikal. Turbulensi EGG dibangkitkan "
         "secara sintetis, bukan dari data lapangan. Simulasi jaringan juga "
         "masih berada pada tingkat model antrian dan routing, belum sampai "
         "emulator paket. Terakhir, waktu inferensi CNN-AE pada perangkat "
         "keras kelas AUV belum diukur.")

    # ================================================== 5. KESIMPULAN
    doc.add_heading("5. KESIMPULAN", level=1)
    para(doc,
         "Dari simulasi dan analisis yang dilakukan dapat disimpulkan empat "
         "hal. Pertama, kanal UOWC pada jendela biru-hijau mengalami rugi "
         "yang naik cepat terhadap jarak. Nilainya \u221226,5 dB pada 20 m "
         "dan \u221249,0 dB pada 50 m untuk clear ocean, sehingga jangkauan "
         "praktisnya terbatas pada puluhan meter.")

    para(doc,
         "Kedua, link budget Beer-Lambert tidak cukup untuk perancangan "
         "karena mengabaikan rugi geometris dan kontribusi foton terhambur. "
         "Selisihnya mencapai 13,5 dB dari hasil simulasi. Monte Carlo "
         "memberi prediksi yang lebih dekat, dengan selisih validasi di "
         "bawah 1,5 dB terhadap literatur.")

    para(doc,
         "Ketiga, soal dispersi jawabannya bergantung pada laju data. Pada "
         "100 Mbps interferensi antar simbol masih bisa diabaikan sampai "
         "puluhan meter. Namun pada 1 Gbps batasnya ketat, yaitu clear "
         "ocean sejak 20 m dan coastal sejak 10 m, sehingga equalizer sudah "
         "diperlukan.")

    para(doc,
         "Keempat, CNN-AE memberi manfaat nyata pada kanal turbulensi, "
         "tetapi manfaat itu bergantung pada kanal latih. Model yang "
         "dilatih dengan asumsi kanal salah bahkan lebih buruk daripada "
         "deteksi ambang biasa, sehingga klaim kinerja AI tidak sah bila "
         "kanal latihnya tidak disebutkan. Integrasi hibrida akustik-optik "
         "dengan failover OSPF menjembatani trade-off kecepatan dan "
         "jangkauan, dengan catatan blackout sekitar 40 detik saat "
         "konvergensi. Riset lanjutan disarankan mengarah pada peralihan "
         "proaktif berbasis prediksi kanal, validasi pada emulator jaringan "
         "nyata, dan pengukuran waktu inferensi CNN-AE pada prosesor kelas "
         "AUV.")

    # ================================================== 6. DAFTAR PUSTAKA
    doc.add_heading("DAFTAR PUSTAKA", level=1)
    refs = [
        "H. Kaushal and G. Kaddoum, \"Underwater optical wireless "
        "communication,\" IEEE Access, vol. 4, pp. 1518–1547, 2016, "
        "doi: 10.1109/ACCESS.2016.2552538.",
        "C. Gabriel, M.-A. Khalighi, S. Bourennane, P. Leon, and V. Rigaud, "
        "\"Channel modeling for underwater optical communication,\" in Proc. "
        "2nd IEEE Workshop on Optical Wireless Communications, 2011, "
        "pp. 833–837.",
        "E. Zedini, H. M. Oubei, A. Kammoun, M. Hamdi, B. S. Ooi, and "
        "M.-S. Alouini, \"Unified statistical channel model for "
        "turbulence-induced fading in underwater wireless optical "
        "communication systems,\" IEEE Trans. Communications, vol. 66, "
        "no. 5, pp. 2087–2102, 2018, doi: 10.1109/TCOMM.2018.2797988.",
        "T. O'Shea and J. Hoydis, \"An introduction to deep learning for "
        "the physical layer,\" IEEE Trans. Cognitive Communications and "
        "Networking, vol. 3, no. 4, pp. 563–575, 2017, "
        "doi: 10.1109/TCCN.2017.2758370.",
        "K. Y. Islam, I. Ahmad, D. Habibi, M. I. A. Zahed, and T. Iqbal, "
        "\"Green underwater wireless communications using hybrid "
        "optical-acoustic technologies,\" IEEE Access, vol. 9, "
        "pp. 85109–85123, 2021, doi: 10.1109/ACCESS.2021.3088467.",
    ]
    for i, r in enumerate(refs, 1):
        p = doc.add_paragraph(f"[{i}] {r}")
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for run in p.runs:
            run.font.size = Pt(12)

    doc.save(OUT)
    print("tersimpan:", OUT)


if __name__ == "__main__":
    build()
