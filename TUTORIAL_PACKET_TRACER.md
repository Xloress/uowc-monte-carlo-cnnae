# Tutorial Packet Tracer — Simulasi Failover Hibrida Akustik-Optik

Panduan ini menghasilkan **screenshot topologi + log failover** untuk
Bagian V paper. Hasilnya melengkapi `fig8_failover_timeline.png` (yang
dihasilkan dari model Python) dengan bukti konfigurasi nyata.

## Konsep yang diuji

Dua router: **R1 = Base Station**, **R2 = AUV**. Keduanya terhubung dua jalur:

- **Jalur optik** — merepresentasikan link UOWC: bandwidth tinggi, cost OSPF rendah
- **Jalur akustik** — merepresentasikan link akustik: bandwidth rendah, cost OSPF tinggi

OSPF memilih jalur optik selama jalur itu *up*. Ketika jalur optik di-*shutdown*
(AUV masuk perairan keruh), OSPF mengonvergensi ke jalur akustik.

## 1. Topologi

```
        +------------------+                 +------------------+
        |        R1        |  Gi0/0 (optik)  |        R2        |
        |  Base Station    |=================|       AUV        |
        |                  |  10.10.10.0/30  |                  |
        |                  |                 |                  |
        |                  |  Se0/0/0 (akustik)                 |
        |                  |=================|                  |
        +------------------+  10.10.20.0/30  +------------------+
                 |                                    |
            PC-PT (operator)                    PC-PT (sensor)
          192.168.1.0/24                      192.168.2.0/24
```

Di Packet Tracer:

1. Letakkan dua **Router 2911** (atau 4331).
2. Tambah **2 PC** untuk menguji konektivitas.
3. Sambungkan R1↔R2 dengan **GigabitEthernet** (kabel *cross-over*).
4. Sambungkan R1↔R2 lagi dengan **Serial** — perlu modul `HWIC-2T`
   (matikan router → *Physical* → tarik modul → nyalakan).
5. Sambungkan tiap PC ke routernya dengan GigabitEthernet.

## 2. Konfigurasi dasar

**R1:**
```
enable
configure terminal
hostname R1
!
interface GigabitEthernet0/0
 description LINK-OPTIK-UOWC
 ip address 10.10.10.1 255.255.255.252
 bandwidth 1000000
 no shutdown
!
interface Serial0/0/0
 description LINK-AKUSTIK
 ip address 10.10.20.1 255.255.255.252
 bandwidth 15
 clock rate 64000
 no shutdown
!
interface GigabitEthernet0/1
 description LAN-OPERATOR
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 1.1.1.1
 network 10.10.10.0 0.0.0.3 area 0
 network 10.10.20.0 0.0.0.3 area 0
 network 192.168.1.0 0.0.0.255 area 0
!
end
write memory
```

**R2:**
```
enable
configure terminal
hostname R2
!
interface GigabitEthernet0/0
 description LINK-OPTIK-UOWC
 ip address 10.10.10.2 255.255.255.252
 bandwidth 1000000
 no shutdown
!
interface Serial0/0/0
 description LINK-AKUSTIK
 ip address 10.10.20.2 255.255.255.252
 bandwidth 15
 no shutdown
!
interface GigabitEthernet0/1
 description LAN-SENSOR
 ip address 192.168.2.1 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 2.2.2.2
 network 10.10.10.0 0.0.0.3 area 0
 network 10.10.20.0 0.0.0.3 area 0
 network 192.168.2.0 0.0.0.255 area 0
!
end
write memory
```

## 3. Memaksa pemilihan jalur optik

OSPF secara default menghitung cost dari bandwidth. Untuk kontrol penuh,
set cost secara eksplisit:

**Di R1 dan R2:**
```
interface GigabitEthernet0/0
 ip ospf cost 1
interface Serial0/0/0
 ip ospf cost 100
```

Verifikasi:
```
R1# show ip ospf interface brief
R1# show ip route ospf
```

Rute ke `192.168.2.0/24` harus lewat `GigabitEthernet0/0` (cost 1),
bukan `Serial0/0/0` (cost 100).

## 4. Uji kondisi normal

Dari PC operator (192.168.1.10) ke PC sensor (192.168.2.10):

```
ping 192.168.2.10 repeat 20
tracert 192.168.2.10
```

Hasil yang diharapkan: 20/20 berhasil, traceroute menunjukkan hop tunggal
lewat `10.10.10.2` (jalur optik).

## 5. Simulasi turbulensi (failover)

Di R1, matikan antarmuka optik:
```
configure terminal
interface GigabitEthernet0/0
 shutdown
end
```

Amati di R2:
```
debug ip ospf adj
show ip ospf neighbor
show ip route ospf
```

Yang terjadi:
1. Neighbor adjacency lewat Gi0/0 turun (dead interval 40 detik).
2. Setelah 40 detik, OSPF mendeklarasikan neighbor down.
3. Rute dihitung ulang; jalur akustik (cost 100) menjadi aktif.

Uji lagi:
```
ping 192.168.2.10 repeat 20
tracert 192.168.2.10
```

Hasil yang diharapkan: traceroute sekarang lewat `10.10.20.2` (jalur akustik).
Beberapa ping pertama akan timeout — **ini yang disebut blackout konvergensi**,
dan angkanya harus sekitar 40 detik. Catat berapa ping yang hilang.

## 6. Memulihkan jalur optik

```
configure terminal
interface GigabitEthernet0/0
 no shutdown
end
```

Setelah adjacency terbentuk kembali (beberapa detik hingga 40 detik),
trafik otomatis kembali ke jalur optik karena cost-nya lebih rendah.

## 7. Data yang harus dicatat untuk paper

Buat tabel seperti ini dan isi dari hasil nyata:

| Skenario | Jalur aktif | Next hop | Ping hilang | Waktu konvergensi |
|---|---|---|---|---|
| Normal | optik | 10.10.10.2 | 0 | — |
| Optik shutdown | akustik | 10.10.20.2 | ... | ... detik |
| Optik restore | optik | 10.10.10.2 | ... | ... detik |

Cara mengukur waktu konvergensi secara presisi: aktifkan timestamp di log
(`service timestamps log datetime msec`) lalu bandingkan waktu baris
`%OSPF-5-ADJCHG` saat down dan saat rute baru terpasang.

## 8. Screenshot yang dibutuhkan

1. **Topologi** — tampilan *Logical* dengan label antarmuka terlihat.
   Tambahkan text box berlabel "Jalur Optik (UOWC)" dan "Jalur Akustik".
2. **`show ip route ospf`** di R1 kondisi normal — tunjukkan jalur optik.
3. **`show ip route ospf`** di R1 setelah shutdown — tunjukkan jalur akustik.
4. **Traceroute** kedua kondisi, berdampingan.
5. **`show ip ospf neighbor`** saat adjacency turun.

Semua screenshot ini masuk **Bagian V** paper, di bawah subbab
*Failover Mechanism*, menggantikan tag gambar referensi.

## 9. Batasan yang harus diakui di paper

Simulasi ini memodelkan **logika routing**, bukan fisika kanal:

- Kabel GigabitEthernet tidak memiliki redaman air laut
- "Jalur akustik" adalah pembatasan bandwidth administratif, bukan model
  propagasi akustik sebenarnya
- Waktu konvergensi OSPF (40 s) jauh lebih besar daripada skala waktu
  perubahan kanal optik yang sebenarnya (milidetik hingga detik)

Karena itu, di paper sebaiknya ditulis: *"simulasi ini memvalidasi logika
failover pada lapisan routing, sedangkan karakterisasi kanal fisik diperoleh
dari simulasi Monte Carlo (Bagian IV)."* Jangan klaim bahwa Packet Tracer
membuktikan kinerja UOWC.

## 10. Alternatif tanpa Packet Tracer

Kalau Packet Tracer tidak tersedia, gunakan PNETLab (VM, butuh image IOS)
atau GNS3. Untuk sekedar logika routing, FRRouting di Linux juga cukup:

```bash
# di container/vm
vtysh -c "conf t" -c "router ospf" -c "network 10.10.10.0/30 area 0"
```

Namun untuk keperluan paper mata kuliah, screenshot Packet Tracer lebih
mudah dipahami penguji karena tampilan topologinya visual.
