"""Antarmuka Streamlit: Sistem Pakar Penilaian Kualitas Bibit Sapi Potong (SNI 7651: Bali, Aceh, PO)."""
from pathlib import Path

import pandas as pd
import streamlit as st

from src.consultation_log import ConsultationLog
from src.explanation import format_report, why
from src.knowledge_base import KnowledgeBase
from src.konsultasi import jalankan_konsultasi

BASE = Path(__file__).parent
kb = KnowledgeBase(BASE / "data" / "knowledge_base.json")
log = ConsultationLog(BASE / "data" / "history.json")
st.set_page_config(page_title="Sistem Pakar Bibit Sapi Potong", layout="wide")


CSS = """
<style>
html, body, [class*="css"] {letter-spacing:.1px;}
[data-testid="stHeader"] {background:transparent;}
.block-container {padding-top:3.2rem;}
.stApp {background: linear-gradient(180deg,#FBF8F1 0%,#F6F0E0 100%);}
.stApp h2, .stApp h3 {color:#24502D; font-weight:700; letter-spacing:-.2px;}
.stApp p, .stApp li {line-height:1.65;}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#24502D 0%,#1B3B22 100%);}
[data-testid="stSidebar"] * {color:#F6F1E4 !important;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {opacity:.8; font-size:12.5px; line-height:1.5;}
.side-brand {text-align:center; padding:8px 0 16px 0; border-bottom:1px dashed #8FB996; margin-bottom:14px;}
.side-brand svg {width:88px; height:88px; display:block; margin:0 auto 10px auto;}
.side-brand .t {font-weight:700; font-size:16px; line-height:1.35; letter-spacing:.3px;}
.side-brand .s {font-size:12px; opacity:.8; margin-top:2px;}
.hero {display:flex; gap:20px; align-items:center; padding:22px 28px; border-radius:18px 18px 4px 4px;
  background: linear-gradient(120deg,#2F6B3A 0%,#4E8B4A 55%,#A9A04B 100%); color:#FFFDF5;
  box-shadow:0 6px 18px rgba(47,107,58,.25);}
.hero svg {width:68px; height:68px; flex:none; filter: drop-shadow(0 3px 4px rgba(0,0,0,.2));}
.hero .ht {font-size:27px; font-weight:700; line-height:1.25; margin:0; color:#FFFDF5;}
.hero .hs {font-size:15px; margin:5px 0 0 0; opacity:.92; line-height:1.5; color:#FFFDF5;}
.fence {height:16px; margin-bottom:22px; border-radius:0 0 12px 12px;
  background: repeating-linear-gradient(90deg,#8B5E3C 0 7px,transparent 7px 24px),
              linear-gradient(#8B5E3C,#8B5E3C) 0 5px/100% 4px no-repeat,
              linear-gradient(#8B5E3C,#8B5E3C) 0 11px/100% 4px no-repeat;}
[data-testid="stForm"] {background:#FFFDF8; border:1px solid #E2D6BA; border-radius:16px; padding:18px 20px;
  box-shadow:0 2px 8px rgba(120,90,40,.08);}
[data-testid="stMetric"] {background:#FFFDF8; border:1px solid #E2D6BA; border-left:6px solid #2F6B3A;
  border-radius:12px; padding:12px 16px; box-shadow:0 2px 6px rgba(120,90,40,.08);}
.stButton>button, .stDownloadButton>button, [data-testid="stFormSubmitButton"]>button {
  border-radius:10px; font-weight:600; transition:all .15s ease;}
.stButton>button:hover, .stDownloadButton>button:hover {transform:translateY(-1px); box-shadow:0 4px 10px rgba(47,107,58,.25);}
[data-testid="stExpander"] {background:#FFFDF8; border:1px solid #E2D6BA; border-radius:12px;}
.stTabs [data-baseweb="tab"] {font-weight:600;}
.cards {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; align-items:stretch;}
.card {background:#FFFDF8; border:1px solid #E2D6BA; border-radius:14px; padding:18px 20px; min-height:158px;
  box-shadow:0 2px 6px rgba(120,90,40,.08); display:flex; flex-direction:column; box-sizing:border-box;}
.card .ct {display:flex; align-items:center; gap:10px; font-size:17px; font-weight:700; color:#24502D; line-height:1.3;}
.card .n {flex:none; width:28px; height:28px; line-height:28px; text-align:center; border-radius:50%;
  background:#2F6B3A; color:#fff; font-size:14px; font-weight:700;}
.card .cd {margin:10px 0 0 0; font-size:14.5px; line-height:1.6; color:#4A4636;}
@media (max-width: 1000px) {.cards {grid-template-columns:repeat(2,minmax(0,1fr));}}
@media (max-width: 560px) {.cards {grid-template-columns:1fr;}}
.footer {text-align:center; color:#7A6A4A; font-size:12.5px; margin-top:30px;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Logo kepala sapi (SVG, tanpa emoji)
LOGO_SVG = (
    '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Logo sapi">'
    '<circle cx="60" cy="60" r="57" fill="#F6F1E4"/>'
    '<path d="M33 42C20 38 14 26 20 14C23 24 30 29 41 33Z" fill="#C9A66B"/>'
    '<path d="M87 42C100 38 106 26 100 14C97 24 90 29 79 33Z" fill="#C9A66B"/>'
    '<ellipse cx="25" cy="55" rx="14" ry="7.5" transform="rotate(-18 25 55)" fill="#8B5E3C"/>'
    '<ellipse cx="95" cy="55" rx="14" ry="7.5" transform="rotate(18 95 55)" fill="#8B5E3C"/>'
    '<path d="M38 33Q60 24 82 33Q92 52 85 72Q80 94 60 101Q40 94 35 72Q28 52 38 33Z" '
    'fill="#FFFDF5" stroke="#24502D" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M64 31Q82 30 83 46Q84 58 72 60Q60 58 62 44Q62 36 64 31Z" fill="#8B5E3C"/>'
    '<ellipse cx="60" cy="82" rx="20" ry="14" fill="#E9B8A6" stroke="#24502D" stroke-width="2.5"/>'
    '<ellipse cx="52" cy="82" rx="3.2" ry="4.5" fill="#6B3F2E"/>'
    '<ellipse cx="68" cy="82" rx="3.2" ry="4.5" fill="#6B3F2E"/>'
    '<circle cx="47" cy="58" r="4.5" fill="#2B2A26"/><circle cx="73" cy="58" r="4.5" fill="#FFFDF5"/>'
    '<circle cx="73" cy="58" r="2.4" fill="#2B2A26"/>'
    '</svg>')


def hero(judul, sub):
    """Banner halaman bertema peternakan (logo sapi + pagar kandang)."""
    st.markdown(f'<div class="hero">{LOGO_SVG}<div><div class="ht">{judul}</div><div class="hs">{sub}</div></div></div>'
                '<div class="fence"></div>', unsafe_allow_html=True)


def halaman_panduan():
    hero("Panduan & Aturan Penggunaan", "Baca sebentar sebelum memakai sistem agar hasil penilaian akurat")
    st.subheader("Alur penggunaan")
    langkah = [("Pilih sapi", "Pilih jenis kelamin dan kelompok umur terdekat pada menu <b>Konsultasi</b>."),
               ("Ukur & amati", "Isi ukuran tubuh (cm), persyaratan umum, dan ciri kualitatif sapi."),
               ("Atur keyakinan", "Tentukan tingkat keyakinan umur dan penilaian visual (Certainty Factor input)."),
               ("Analisis", "Klik <b>Analisis</b>, lalu baca kesimpulan, skor, dan penjelasan HOW.")]
    kartu = "".join(f'<div class="card"><div class="ct"><span class="n">{i}</span>{t}</div><div class="cd">{d}</div></div>'
                    for i, (t, d) in enumerate(langkah, 1))
    st.markdown(f'<div class="cards">{kartu}</div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("Aturan penggunaan")
    st.markdown("""
1. **Pilih jenis sapi lebih dulu.** Tersedia sapi Bali (SNI 7651-4:2020), Aceh (SNI 7651-3:2020), dan Peranakan Ongole (SNI 7651-5:2020). Ambang ukuran dan ciri fisik berbeda tiap rumpun, jadi pilih sesuai sapi yang dinilai. Rumpun lain belum didukung.
2. **Kelas bibit.** Bali dan PO dibagi Kelas I/II/III, sedangkan SNI Aceh hanya menetapkan satu ukuran minimum, sehingga hasilnya cukup *memenuhi standar minimum* atau tidak.
3. **Kelompok umur** mengikuti tabel SNI: jantan 205 hari / 12 / 24 bulan, betina 205 hari / 12 / 18 / 24 bulan. Pilih yang terdekat. Umur 205 hari ditentukan dari catatan kelahiran.
4. **Estimasi umur dari gigi seri permanen:** 0 pasang = di bawah 18 bulan, 1 pasang = 18-24 bulan.
5. **Centang hanya yang benar-benar teramati.** Kolom yang tidak dicentang dianggap *tidak terpenuhi*.
6. **Libido/semen** hanya ditanyakan untuk pejantan umur 18 bulan ke atas, **ambing** hanya untuk induk 18 bulan ke atas; pada umur lain dianggap tidak dipersyaratkan.
7. **Ukuran tubuh wajib diisi** dan divalidasi (rentang wajar). Input di luar rentang akan ditolak.
8. **Hasil adalah alat bantu keputusan**, bukan pengganti pemeriksaan dokter hewan atau petugas pembibitan.
9. **Mengubah rule** (menu Basis Pengetahuan) langsung tersimpan ke `data/knowledge_base.json`. Cadangkan file itu dulu dan pastikan sumbernya jelas.
""")
    with st.expander("Cara mengukur sesuai SNI 7651 (sama untuk ketiga rumpun)", expanded=True):
        st.markdown("""
Sapi harus **berdiri sempurna** (keempat kaki tegak membentuk persegi panjang) di atas lantai yang rata.

| Ukuran | Cara mengukur | Alat |
|---|---|---|
| Tinggi pundak (TP) | Jarak tegak lurus dari tanah ke titik tertinggi pundak, di belakang punuk, sejajar kaki depan | Tongkat ukur |
| Panjang badan (PB) | Jarak dari bongkol bahu (tuberositas humeri) sampai ujung tulang duduk (tuber ischii) | Tongkat ukur |
| Lingkar dada (LD) | Lingkarkan pita pada dada di belakang punuk | Pita ukur |
| Lingkar skrotum (LS) | Lingkarkan pita pada bagian tengah skrotum (khusus jantan 12 & 24 bulan) | Pita ukur |
""")
    with st.expander("Cara membaca hasil"):
        st.markdown("""
- **Kelas I / II / III** (Bali, PO): kelas tertinggi yang ukuran tubuhnya memenuhi minimum SNI dan lolos persyaratan umum. Untuk Aceh, hasilnya *memenuhi standar minimum*.
- **Tingkat kepercayaan (CF)**: seberapa yakin sistem pada kesimpulan, gabungan CF rule dan CF input Anda.
- **Skor kelayakan (0-100)**: CF dikalikan bobot kelas (I = 1,0; II = 0,85; III = 0,70) dan 100.
- **Catatan kualitatif**: ciri fisik menyimpang dari standar rumpun Bali; periksa kemurnian rumpunnya.
- **HOW / jejak inferensi**: daftar rule yang menyala beserta urutan penalarannya.
""")
    st.info("Keterbatasan: CF rule heuristik dan bobot kelas adalah perkiraan penyusun dan belum divalidasi pakar. "
            "Data PO bersumber dari ringkasan SNI 7651-5:2020; verifikasi dengan dokumen SNI asli.")


def w(fact):  # teks WHY untuk tooltip input
    return why(fact, kb.rules, kb.labels)


def halaman_konsultasi():
    hero("Konsultasi Penilaian Bibit Sapi Potong", "Pilih jenis sapi, isi data pengamatan, dan dapatkan penilaian sesuai SNI 7651")
    rumpun = st.selectbox("Jenis sapi (rumpun)", list(kb.rumpun), format_func=lambda r: f"{kb.rumpun[r]['nama']} - {kb.rumpun[r]['sni']}")
    cfg = kb.rumpun[rumpun]
    st.caption(f"Acuan: {cfg['sni']}. Ikon (?) pada tiap isian menjelaskan WHY data tersebut ditanyakan.")
    if cfg["catatan"]:
        st.info(cfg["catatan"])
    jk = st.radio("Jenis kelamin", ["jantan", "betina"], horizontal=True)
    opsi = cfg["standar"][jk]
    umur = st.selectbox("Kelompok umur standar SNI", list(opsi), format_func=lambda k: opsi[k]["label"],
                        help="Pilih kelompok umur terdekat. Umur 205 hari berdasarkan catatan kelahiran.")
    std = opsi[umur]
    with st.form("form_konsultasi"):
        st.subheader("Ukuran tubuh (cm)")
        c = st.columns(4)
        inp = {"rumpun": rumpun, "jenis_kelamin": jk, "umur_standar": umur}
        inp["TP"] = c[0].number_input("Tinggi pundak", 0.0, 250.0, 0.0, 0.5, help=w("tp_k1"))
        inp["PB"] = c[1].number_input("Panjang badan", 0.0, 250.0, 0.0, 0.5, help=w("pb_k1"))
        inp["LD"] = c[2].number_input("Lingkar dada", 0.0, 300.0, 0.0, 0.5, help=w("ld_k1"))
        if "LS" in std:
            inp["LS"] = c[3].number_input("Lingkar skrotum", 0.0, 60.0, 0.0, 0.5, help=w("ls_k1"))
        st.subheader("Persyaratan umum")
        g = st.columns(3)
        inp["sehat"] = g[0].checkbox("Sapi sehat", help=w("sehat"))
        inp["cacat_fisik"] = g[1].checkbox("Ada cacat fisik", help=w("cacat_fisik"))
        inp["silsilah_ada"] = g[2].checkbox("Memiliki silsilah", help=w("silsilah_ada"))
        inp["reproduksi_normal"] = g[0].checkbox("Organ reproduksi normal", help=w("reproduksi_normal"))
        if jk == "jantan" and std["umur_bulan"] >= 18:
            inp["libido_semen_ok"] = g[1].checkbox("Libido & semen baik", help=w("libido_semen_ok"))
        if jk == "betina" and std["umur_bulan"] >= 18:
            inp["ambing_ok"] = g[1].checkbox("Ambing simetris, 4 puting normal", help=w("ambing_ok"))
        st.subheader("Ciri kualitatif")
        q = st.columns(3)
        for i, f in enumerate(cfg["kualitatif"][jk]):
            inp[f] = q[i % 3].checkbox(kb.labels[f], help=w(f))
        st.subheader("Tingkat keyakinan (Certainty Factor input)")
        k = st.columns(2)
        inp["cf_umur"] = k[0].select_slider("Penentuan umur", [0.6, 0.8, 1.0], 1.0,
                                            format_func=lambda v: {0.6: "Perkiraan kasar", 0.8: "Dari gigi seri", 1.0: "Catatan kelahiran"}[v])
        inp["cf_visual"] = k[1].select_slider("Penilaian visual", [0.5, 0.7, 0.9, 1.0], 0.9)
        kirim = st.form_submit_button("Analisis", type="primary")
    if kirim:
        try:
            hasil = jalankan_konsultasi(kb, inp)
            st.session_state["hasil"] = log.save(hasil)
        except ValueError as e:
            st.error(f"Input tidak valid: {e}")
    if "hasil" in st.session_state:
        tampil_hasil(st.session_state["hasil"])


def tampil_hasil(e):
    k = e["keputusan"]
    (st.success if k["status"] == "LAYAK" else st.error)(
        f"**{k['status']}**" + (f" - {k['label_kelas']}" if k.get("label_kelas") else "") + f"  |  {e.get('rumpun', '')}")
    m = st.columns(3)
    m[0].metric("Tingkat kepercayaan", f"{k['cf'] * 100:.1f}%")
    m[1].metric("Skor kelayakan", f"{k['skor']}/100")
    m[2].metric("Rules menyala", len(e["rules_used"]))
    st.write("**Rekomendasi:**", k["rekomendasi"])
    if k.get("catatan"):
        st.warning("Ciri kualitatif menyimpang dari SNI: verifikasi kemurnian rumpun sebelum membeli.")
    with st.expander("HOW - bagaimana kesimpulan ini diperoleh", expanded=True):
        st.code("\n".join(e["how"]) or "-", language="text")
    with st.expander("Jejak inferensi forward chaining (step-by-step)"):
        st.dataframe(pd.DataFrame(e["trace"]), width="stretch")
    with st.expander("Working memory (fakta akhir)"):
        st.dataframe(pd.DataFrame(e["working_memory"]).T, width="stretch")
    teks = format_report(e, kb.labels)
    d = st.columns(3)
    d[0].download_button("Unduh TXT", teks, f"{e['id']}.txt")
    d[1].download_button("Unduh CSV", log.to_csv([e]), f"{e['id']}.csv", "text/csv")
    try:
        d[2].download_button("Unduh PDF", log.to_pdf(teks), f"{e['id']}.pdf", "application/pdf")
    except ImportError:
        d[2].caption("Pasang fpdf2 untuk ekspor PDF.")


def halaman_basis_pengetahuan():
    hero("Basis Pengetahuan & Akuisisi Pengetahuan", "Kelola rule IF-THEN, sumber, dan standar ukuran SNI")
    t1, t2, t3, t4 = st.tabs(["Cari & filter rule", "Tambah rule", "Ubah / hapus rule", "Database standar SNI"])
    with t1:
        c = st.columns([3, 1])
        kw = c[0].text_input("Cari (gejala/fakta/kesimpulan)")
        jn = c[1].selectbox("Jenis", ["semua", "faktual", "heuristik"])
        hasil = kb.search(kw, None if jn == "semua" else jn)
        st.dataframe(pd.DataFrame([{"ID": i, "IF": " AND ".join(r["IF"]), "THEN": r["THEN"], "CF": r["CF"],
                                    "Jenis": r["jenis"], "Sumber": r["sumber"]} for i, r in hasil.items()]),
                     width="stretch")
    with t2:
        with st.form("tambah"):
            rid = st.text_input("ID rule (mis. R25)")
            cond = st.text_input("IF (pisahkan koma; awali ! untuk negasi)")
            then = st.text_input("THEN")
            cf = st.number_input("CF", 0.0, 1.0, 0.8, 0.05)
            jenis = st.selectbox("Jenis pengetahuan", kb.JENIS)
            sumber, desk = st.text_input("Sumber"), st.text_input("Deskripsi")
            if st.form_submit_button("Simpan rule"):
                err = kb.add_rule(rid, {"IF": [x.strip() for x in cond.split(",") if x.strip()], "THEN": then.strip(),
                                        "CF": cf, "jenis": jenis, "sumber": sumber, "deskripsi": desk})
                st.error("\n".join(err)) if err else st.success(f"Rule {rid} disimpan ke JSON.")
    with t3:
        rid = st.selectbox("Pilih rule", list(kb.rules))
        r = kb.rules[rid]
        cond = st.text_input("IF", ", ".join(r["IF"]), key=f"if{rid}")
        then = st.text_input("THEN", r["THEN"], key=f"th{rid}")
        cf = st.number_input("CF", 0.0, 1.0, float(r["CF"]), 0.05, key=f"cf{rid}")
        c = st.columns(2)
        if c[0].button("Perbarui"):
            err = kb.update_rule(rid, {**r, "IF": [x.strip() for x in cond.split(",") if x.strip()], "THEN": then.strip(), "CF": cf})
            st.error("\n".join(err)) if err else st.success("Rule diperbarui.")
        if c[1].button("Hapus"):
            for m in kb.delete_rule(rid) or ["Rule dihapus. Muat ulang halaman."]:
                st.warning(m)
    with t4:
        r = st.selectbox("Rumpun", list(kb.rumpun), format_func=lambda x: kb.rumpun[x]["nama"], key="std_rumpun")
        cfg = kb.rumpun[r]
        for sex, d in cfg["standar"].items():
            st.subheader(f"Persyaratan minimum kuantitatif - {cfg['nama']} {sex}")
            rows = []
            for v in d.values():
                for p in ("TP", "PB", "LD", "LS"):
                    if p in v:
                        row = {"Umur": v["label"], "Parameter": p}
                        if cfg["kelas_tunggal"]:
                            row["Minimum"] = v[p][0]
                        else:
                            row.update({"Kelas I": v[p][0], "Kelas II": v[p][1], "Kelas III": v[p][2]})
                        rows.append(row)
            st.dataframe(pd.DataFrame(rows), width="stretch")
        st.caption("TP: tinggi pundak, PB: panjang badan, LD: lingkar dada, LS: lingkar skrotum (cm). Acuan: " + cfg["sni"])
        if cfg["catatan"]:
            st.info(cfg["catatan"])


def halaman_riwayat():
    hero("Riwayat Konsultasi & Statistik", "Catatan penilaian sebelumnya dan rule yang paling sering dipakai")
    hist = log.load()
    if not hist:
        st.info("Belum ada konsultasi.")
        return
    s = log.stats()
    m = st.columns(3)
    m[0].metric("Total konsultasi", s["total"])
    m[1].metric("Layak", s["per_status"].get("LAYAK", 0))
    m[2].metric("Tidak layak", s["per_status"].get("TIDAK LAYAK", 0))
    st.subheader("Rule yang paling sering digunakan")
    st.bar_chart(pd.DataFrame(s["rule_terbanyak"], columns=["Rule", "Jumlah"]).set_index("Rule"))
    c = st.columns(4)
    stt = c[0].selectbox("Status", ["semua", "LAYAK", "TIDAK LAYAK"])
    jk = c[1].selectbox("Jenis kelamin", ["semua", "jantan", "betina"])
    rp = c[2].selectbox("Rumpun", ["semua"] + list(kb.rumpun), format_func=lambda x: "semua" if x == "semua" else kb.rumpun[x]["nama"])
    teks = c[3].text_input("Cari teks")
    hasil = log.filter(hist, None if stt == "semua" else stt, None if jk == "semua" else jk, teks, None if rp == "semua" else rp)
    st.dataframe(pd.read_csv(__import__("io").StringIO(log.to_csv(hasil))), width="stretch")
    st.download_button("Unduh riwayat (CSV)", log.to_csv(hasil), "riwayat_konsultasi.csv", "text/csv")


st.sidebar.markdown(f'<div class="side-brand">{LOGO_SVG}<div class="t">Sistem Pakar<br>Bibit Sapi Potong</div>'
                    '<div class="s">SNI 7651: Bali, Aceh, PO</div></div>', unsafe_allow_html=True)
MENU = {"Panduan Penggunaan": halaman_panduan, "Konsultasi": halaman_konsultasi,
        "Basis Pengetahuan": halaman_basis_pengetahuan, "Riwayat & Statistik": halaman_riwayat}
menu = st.sidebar.radio("Menu", list(MENU), index=1)
st.sidebar.caption("Sistem Pakar Rule-Based (forward chaining + Certainty Factor)")
MENU[menu]()
st.markdown('<div class="footer">Sistem Pakar Penilaian Bibit Sapi Potong - SNI 7651 - INF313 Kecerdasan Artifisial</div>',
            unsafe_allow_html=True)
