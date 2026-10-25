"""Membangun data/knowledge_base.json (3 rumpun: Bali, Aceh, Peranakan Ongole; acuan SNI 7651-x:2020)."""
import json, pathlib

SNI_ALL = "SNI 7651-3/4/5:2020"
HEUR = "Heuristik penyusun (CF perkiraan, perlu validasi pakar peternakan)"
ROMAN = {1: "I", 2: "II", 3: "III"}
rules = {}


def add(cond, then, cf, jenis, sumber, desk):
    rid = f"R{len(rules) + 1:02d}"
    rules[rid] = {"IF": cond, "THEN": then, "CF": cf, "jenis": jenis, "sumber": sumber, "deskripsi": desk}


# --- Aturan gugur (persyaratan umum, sama pada ketiga SNI)
U = SNI_ALL + " persyaratan umum"
add(["!sehat"], "tidak_layak", 1.0, "faktual", U, "Sapi tidak sehat gugur sebagai bibit")
add(["cacat_fisik"], "tidak_layak", 1.0, "faktual", U, "Sapi cacat fisik gugur sebagai bibit")
add(["!reproduksi_normal"], "tidak_layak", 1.0, "faktual", U, "Organ reproduksi tidak normal gugur")
add(["!silsilah_ada"], "tidak_layak", 0.9, "faktual", U, "Tanpa silsilah tidak memenuhi persyaratan umum")
add(["jantan", "!libido_semen_ok"], "tidak_layak", 0.9, "faktual", U, "Pejantan >=18 bln wajib libido dan semen baik")
add(["betina", "!ambing_ok"], "tidak_layak", 1.0, "faktual", U, "Betina wajib ambing simetris, 4 puting normal")
add(["jantan", "sehat", "!cacat_fisik", "silsilah_ada", "reproduksi_normal", "libido_semen_ok"],
    "syarat_umum_terpenuhi", 1.0, "faktual", U, "Seluruh persyaratan umum pejantan terpenuhi")
add(["betina", "sehat", "!cacat_fisik", "silsilah_ada", "reproduksi_normal", "ambing_ok"],
    "syarat_umum_terpenuhi", 1.0, "faktual", U, "Seluruh persyaratan umum induk terpenuhi")

# --- Persyaratan kualitatif per rumpun & jenis kelamin
QUAL = {
    "bali": {"jantan": ["warna_sesuai", "lutut_putih", "pantat_putih", "ekor_hitam", "tanduk_sesuai", "kepala_sesuai"],
             "betina": ["warna_sesuai", "lutut_putih", "pantat_putih", "ekor_hitam", "garis_belut", "tanduk_sesuai", "kepala_sesuai"]},
    "aceh": {"jantan": ["ac_warna", "ac_putih", "ac_ekor", "ac_badan", "ac_kaki", "ac_tanduk", "ac_telinga", "ac_leher", "ac_punuk"],
             "betina": ["ac_warna", "ac_putih", "ac_ekor", "ac_badan", "ac_kaki", "ac_tanduk", "ac_telinga"]},
    "po": {s: ["po_warna", "po_badan", "po_kepala", "po_mata", "po_telinga", "po_ekor", "po_moncong"] for s in ("jantan", "betina")},
}
SUMBER_Q = {"bali": "SNI 7651-4:2020 butir 4.2.1", "aceh": "SNI 7651-3:2020 butir 3.2.1",
            "po": "SNI 7651-5:2020 butir persyaratan kualitatif (via ringkasan BSIP Babel)"}
for br in QUAL:
    for sex in ("jantan", "betina"):
        add([br, sex] + QUAL[br][sex], "kualitatif_sesuai", 0.9, "faktual", SUMBER_Q[br],
            f"Ciri fisik {sex} sesuai standar rumpun {br.upper() if br == 'po' else br.capitalize()}")
add(["syarat_umum_terpenuhi", "!kualitatif_sesuai"], "catatan_kualitatif", 0.8, "heuristik", HEUR,
    "Ciri kualitatif menyimpang: verifikasi kemurnian rumpun sebelum membeli")

# --- Persyaratan kuantitatif per kelas (sama untuk semua rumpun; Aceh hanya memakai kelas 1 = minimum)
Q = SNI_ALL + " tabel persyaratan kuantitatif"
for sex in ("jantan", "betina"):
    for k in (1, 2, 3):
        c = [sex, f"tp_k{k}", f"pb_k{k}", f"ld_k{k}"] + ([f"ls_k{k}"] if sex == "jantan" else [])
        add(c, f"kuantitatif_kelas{k}", 1.0, "faktual", Q, f"Ukuran tubuh {sex} memenuhi minimum Kelas {ROMAN[k]}")
for k in (1, 2, 3):
    add([f"kuantitatif_kelas{k}"], "kuantitatif_lolos", 1.0, "faktual", Q, f"Memenuhi minimum Kelas {ROMAN[k]} berarti lolos syarat ukuran")

# --- Kesimpulan kelayakan: bukti kuantitatif + bukti kualitatif (CF gabungan)
for k, cf in ((1, 0.85), (2, 0.75), (3, 0.65)):
    add(["syarat_umum_terpenuhi", f"kuantitatif_kelas{k}"], f"layak_kelas{k}", cf, "heuristik", HEUR,
        f"Persyaratan umum + kuantitatif Kelas {ROMAN[k]} -> layak Kelas {ROMAN[k]}")
    add(["syarat_umum_terpenuhi", f"kuantitatif_kelas{k}", "kualitatif_sesuai"], f"layak_kelas{k}", 0.7, "heuristik", HEUR,
        f"Bukti tambahan: ciri kualitatif sesuai memperkuat Kelas {ROMAN[k]}")
add(["syarat_umum_terpenuhi", "!kuantitatif_lolos"], "tidak_layak", 0.95, "faktual", Q,
    "Ukuran tubuh di bawah minimum standar -> tidak memenuhi SNI")


def stds(rows):
    return {k: {"umur_bulan": v[0], "label": v[1], **v[2]} for k, v in rows.items()}


BALI = {"jantan": stds({
    "205hari": (6.7, "205 hari", {"TP": [90, 86, 83], "PB": [86, 82, 78], "LD": [108, 103, 98]}),
    "12bln": (12, "12 bulan", {"TP": [102, 98, 94], "PB": [96, 92, 87], "LD": [127, 122, 117], "LS": [16, 14, 11]}),
    "24bln": (24, "24 bulan", {"TP": [121, 118, 115], "PB": [121, 117, 112], "LD": [167, 160, 154], "LS": [26, 25, 24]})}),
    "betina": stds({
    "205hari": (6.7, "205 hari", {"TP": [92, 87, 82], "PB": [89, 84, 79], "LD": [113, 107, 100]}),
    "12bln": (12, "12 bulan", {"TP": [99, 95, 91], "PB": [97, 93, 88], "LD": [126, 121, 116]}),
    "18bln": (18, "18 bulan", {"TP": [108, 105, 102], "PB": [109, 106, 102], "LD": [144, 138, 133]}),
    "24bln": (24, "24 bulan", {"TP": [111, 109, 106], "PB": [110, 107, 104], "LD": [151, 145, 139]})})}
ACEH = {"jantan": stds({
    "205hari": (6.7, "205 hari", {"TP": [84], "PB": [79], "LD": [89]}),
    "12bln": (12, "12 bulan", {"TP": [90], "PB": [89], "LD": [103], "LS": [17]}),
    "24bln": (24, "24 bulan", {"TP": [102], "PB": [103], "LD": [128], "LS": [27]})}),
    "betina": stds({
    "205hari": (6.7, "205 hari", {"TP": [82], "PB": [78], "LD": [90]}),
    "12bln": (12, "12 bulan", {"TP": [87], "PB": [84], "LD": [100]}),
    "18bln": (18, "18 bulan", {"TP": [92], "PB": [91], "LD": [109]}),
    "24bln": (24, "24 bulan", {"TP": [96], "PB": [97], "LD": [120]})})}
PO = {"jantan": stds({
    "205hari": (6.7, "205 hari", {"TP": [107, 101, 99], "PB": [102, 93, 88], "LD": [121, 115, 106]}),
    "12bln": (12, "12 bulan", {"TP": [112, 106, 100], "PB": [106, 101, 93], "LD": [134, 126, 117], "LS": [20, 18, 16]}),
    "24bln": (24, "24 bulan", {"TP": [132, 128, 124], "PB": [132, 124, 117], "LD": [160, 152, 147], "LS": [31, 28, 25]})}),
    "betina": stds({
    "205hari": (6.7, "205 hari", {"TP": [100, 97, 92], "PB": [97, 92, 88], "LD": [120, 116, 110]}),
    "12bln": (12, "12 bulan", {"TP": [107, 104, 100], "PB": [107, 100, 95], "LD": [129, 125, 117]}),
    "18bln": (18, "18 bulan", {"TP": [115, 112, 109], "PB": [115, 111, 107], "LD": [140, 130, 120]}),
    "24bln": (24, "24 bulan", {"TP": [123, 120, 117], "PB": [125, 122, 118], "LD": [158, 153, 146]})})}

rumpun = {
    "bali": {"nama": "Sapi Bali", "sni": "SNI 7651-4:2020", "kelas_tunggal": False, "standar": BALI, "kualitatif": QUAL["bali"],
             "catatan": ""},
    "aceh": {"nama": "Sapi Aceh", "sni": "SNI 7651-3:2020", "kelas_tunggal": True, "standar": ACEH, "kualitatif": QUAL["aceh"],
             "catatan": "SNI sapi Aceh hanya menetapkan satu ukuran minimum (tanpa Kelas I/II/III), sehingga hasilnya LAYAK atau TIDAK LAYAK."},
    "po": {"nama": "Sapi Peranakan Ongole (PO)", "sni": "SNI 7651-5:2020", "kelas_tunggal": False, "standar": PO, "kualitatif": QUAL["po"],
           "catatan": "Data PO diambil dari ringkasan SNI 7651-5:2020 oleh BSIP Kepulauan Bangka Belitung karena salinan resmi "
                      "belum dapat diakses saat penyusunan. Verifikasi dengan dokumen SNI asli sebelum dikumpulkan."},
}

label = {
    "bali": "Rumpun sapi Bali", "aceh": "Rumpun sapi Aceh", "po": "Rumpun sapi PO",
    "jantan": "Jenis kelamin jantan", "betina": "Jenis kelamin betina", "sehat": "Sapi sehat",
    "cacat_fisik": "Ada cacat fisik", "silsilah_ada": "Memiliki silsilah", "reproduksi_normal": "Organ reproduksi normal",
    "libido_semen_ok": "Libido, kualitas & kuantitas semen baik", "ambing_ok": "Ambing simetris, 4 puting normal",
    # Bali
    "warna_sesuai": "Warna badan sesuai standar Bali", "lutut_putih": "Keempat lutut ke bawah putih",
    "pantat_putih": "Pantat putih setengah bulan", "ekor_hitam": "Ujung ekor hitam", "garis_belut": "Garis belut hitam di punggung",
    "tanduk_sesuai": "Bentuk tanduk sesuai", "kepala_sesuai": "Bentuk kepala/leher sesuai",
    # Aceh
    "ac_warna": "Warna tubuh merah bata/kecoklatan/kehitaman", "ac_putih": "Sekeliling mata, telinga dalam, bibir atas keputihan",
    "ac_ekor": "Ujung ekor hitam", "ac_badan": "Badan ramping, moncong hitam",
    "ac_kaki": "Kaki bagian dalam keputihan, kuku hitam", "ac_tanduk": "Tanpa tanduk / tanduk ke samping atau melengkung ke atas",
    "ac_telinga": "Telinga kecil tegak ke samping", "ac_leher": "Leher lebih gelap dari tubuh (jantan)",
    "ac_punuk": "Punuk jantan lebih besar dari betina",
    # PO
    "po_warna": "Warna putih; leher & bahu putih keabuan sampai kehitaman", "po_badan": "Badan besar, gelambir panjang, punuk besar, leher pendek",
    "po_kepala": "Kepala lonjong dan bertanduk", "po_mata": "Kulit sekitar mata hitam", "po_telinga": "Telinga kecil tegak ke samping",
    "po_ekor": "Rambut ekor hitam", "po_moncong": "Moncong dominan hitam",
    "syarat_umum_terpenuhi": "Persyaratan umum terpenuhi", "kualitatif_sesuai": "Ciri kualitatif sesuai SNI",
    "catatan_kualitatif": "Ciri kualitatif menyimpang", "tidak_layak": "Tidak layak sebagai bibit",
    "kuantitatif_lolos": "Ukuran tubuh memenuhi standar minimum",
    **{f"{p}_k{k}": f"{n} memenuhi minimum Kelas {ROMAN[k]}" for k in (1, 2, 3) for p, n in
       (("tp", "Tinggi pundak"), ("pb", "Panjang badan"), ("ld", "Lingkar dada"), ("ls", "Lingkar skrotum"))},
    **{f"kuantitatif_kelas{k}": f"Ukuran tubuh memenuhi Kelas {ROMAN[k]}" for k in (1, 2, 3)},
    **{f"layak_kelas{k}": f"Layak bibit Kelas {ROMAN[k]}" for k in (1, 2, 3)},
}
label_tunggal = {"tp_k1": "Tinggi pundak memenuhi minimum", "pb_k1": "Panjang badan memenuhi minimum",
                 "ld_k1": "Lingkar dada memenuhi minimum", "ls_k1": "Lingkar skrotum memenuhi minimum",
                 "kuantitatif_kelas1": "Ukuran tubuh memenuhi standar minimum",
                 "layak_kelas1": "Layak bibit (memenuhi standar minimum SNI)"}

kb = {
    "meta": {"domain": "Peternakan - bibit sapi potong", "cakupan": "Sapi Bali, Aceh, Peranakan Ongole (SNI 7651-x:2020)",
             "sumber": ["SNI 7651-4:2020 Bibit sapi potong - Bagian 4: Bali", "SNI 7651-3:2020 Bibit sapi potong - Bagian 3: Aceh",
                        "SNI 7651-5:2020 Bibit sapi potong - Bagian 5: Peranakan Ongole (ringkasan BSIP Kep. Bangka Belitung)"]},
    "bobot_kelas": {"1": 1.0, "2": 0.85, "3": 0.70},
    "rekomendasi": {
        "1": "SANGAT LAYAK dibeli sebagai bibit (Kelas I): memenuhi persyaratan umum dan ukuran minimum tertinggi SNI.",
        "2": "LAYAK dibeli sebagai bibit (Kelas II): memenuhi persyaratan umum dan ukuran minimum Kelas II.",
        "3": "LAYAK BERSYARAT (Kelas III): hanya memenuhi ukuran minimum; pertimbangkan harga dan seleksi lanjutan.",
        "min": "LAYAK dibeli sebagai bibit: memenuhi persyaratan umum dan ukuran minimum SNI (rumpun ini tidak dibagi kelas).",
        "0": "TIDAK LAYAK dibeli sebagai bibit: tidak memenuhi persyaratan umum atau ukuran minimum SNI."},
    "label_fakta": label, "label_tunggal": label_tunggal, "rumpun": rumpun, "rules": rules}
out = pathlib.Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"
out.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding="utf-8")
print(len(rules), "rules ditulis")
