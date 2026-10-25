# Sistem Pakar Penilaian Kualitas Bibit Sapi Potong (SNI 7651)

Sistem pakar *rule-based* berbasis Python untuk membantu peternak menilai kelayakan bibit sapi potong
sesuai **SNI 7651-x:2020**. Mata kuliah INF313 Kecerdasan Artifisial (UTS Praktikum).

## Rumpun yang didukung
| Rumpun | Acuan | Kelas bibit |
|---|---|---|
| Sapi Bali | SNI 7651-4:2020 | Kelas I / II / III |
| Sapi Aceh | SNI 7651-3:2020 | Satu ukuran minimum (tanpa kelas) |
| Sapi Peranakan Ongole (PO) | SNI 7651-5:2020 | Kelas I / II / III |

Rumpun lain dapat ditambahkan lewat `scripts/build_kb.py` / `data/knowledge_base.json` (bagian `rumpun`).

## Fitur
- **Knowledge base** IF-THEN (31 rule, JSON) - faktual (SNI) & heuristik, lengkap dengan sumber.
- **Inference engine** forward chaining + trace langkah demi langkah.
- **Working memory** menyimpan fakta input, fakta turunan, dan hasil antara.
- **Certainty Factor**: CF rule, CF input (keyakinan umur & penilaian visual), CF gabungan `CF1 + CF2 x (1 - CF1)`.
- **Explanation facility**: WHY (tooltip tiap input), HOW (rantai rule), daftar rule yang dipakai.
- **Knowledge acquisition**: tambah/ubah/hapus rule + validasi (ID unik, CF, sumber, deteksi siklus), simpan ke JSON.
- **Reporting**: ekspor TXT/CSV/PDF, riwayat, statistik per rumpun, rule terbanyak dipakai, pencarian & filter.
- **GUI** Streamlit: Panduan Penggunaan, Konsultasi, Basis Pengetahuan, Riwayat & Statistik.

## Instalasi & menjalankan
```bash
pip install -r requirements.txt
python -m streamlit run app.py   # Windows: py -m streamlit run app.py
python -m tests.test_cases       # pengujian 14 skenario
python scripts/build_kb.py       # (opsional) bangun ulang knowledge_base.json
```

## Struktur
```
app.py                  # UI Streamlit
.streamlit/config.toml  # tema
src/working_memory.py   # memori kerja + validasi input
src/inference_engine.py # forward chaining + CF
src/explanation.py      # WHY / HOW / laporan
src/knowledge_base.py   # CRUD & validasi rule
src/consultation_log.py # riwayat, statistik, ekspor
src/konsultasi.py       # pipeline konsultasi
data/knowledge_base.json
scripts/build_kb.py     # generator knowledge base
tests/test_cases.py
```

## Alur penilaian
1. Pilih rumpun, jenis kelamin, dan kelompok umur standar.
2. Syarat umum (sehat, tanpa cacat, reproduksi normal, silsilah, libido/ambing >= 18 bln) -> `syarat_umum_terpenuhi` atau gugur.
3. Ukuran tubuh (TP, PB, LD, LS) dibandingkan tabel SNI rumpun terpilih -> `kuantitatif_kelas1..3`.
4. Ciri kualitatif khas rumpun -> `kualitatif_sesuai`.
5. Kesimpulan `layak_kelasN` (CF gabungan) -> skor = CF x bobot kelas (I = 1.0, II = 0.85, III = 0.70) x 100.

## Catatan validasi
- Ambang Bali dan Aceh diambil langsung dari dokumen SNI 7651-4:2020 dan SNI 7651-3:2020.
- Ambang dan ciri kualitatif **PO** diambil dari ringkasan SNI 7651-5:2020 oleh BSIP Kepulauan Bangka Belitung
  (salinan resmi belum dapat diakses saat penyusunan). **Cocokkan dengan dokumen SNI asli sebelum dikumpulkan.**
- CF rule bertanda *heuristik* dan bobot kelas adalah perkiraan penyusun; validasikan dengan pakar/literatur.

## Screenshot / demo
1. Halaman Panduan dan Aturan Penggunaan
<img width="1869" height="823" alt="image" src="https://github.com/user-attachments/assets/3068a7c6-6731-4eda-9985-02befdd400fe" />


2. Halaman Konsultasi
<img width="1902" height="826" alt="image" src="https://github.com/user-attachments/assets/caad9e6f-a101-4f5f-95f4-f838a3c0fa0b" />


3. Halaman Basis Pengetahuan (Knowledge Base)
<img width="1897" height="819" alt="image" src="https://github.com/user-attachments/assets/05562a16-a6a8-4370-aea0-6c1e8867a486" />


4. Halaman Riwayat dan Statistik
<img width="1918" height="814" alt="image" src="https://github.com/user-attachments/assets/7300fef1-2a9a-4c34-ba64-44e21e8a7fa0" />



## Kontributor
| Anggota | Bagian |
|---|---|
| Muhammad Hafidz | Setup proyek, log konsultasi dan ekspor, README |
| Putroe Fatimah Azzahra | Knowledge base dan akuisisi pengetahuan |
| Nayla Nabila Syahel | Working memory, inference engine, pipeline |
| Khairul Fikri | Explanation facility, pengujian, laporan |
| Dara Ramadhani | Antarmuka Streamlit dan screenshot |
