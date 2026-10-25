"""Skenario pengujian (>=5 test case). Jalankan: python -m tests.test_cases  (dari root proyek)."""
from pathlib import Path
from src.knowledge_base import KnowledgeBase
from src.konsultasi import jalankan_konsultasi

KB = KnowledgeBase(Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json")
# Semua ciri kualitatif semua rumpun diset benar; fakta yang tidak relevan untuk rumpun terpilih diabaikan.
QUAL_ALL = {f: True for cfg in KB.rumpun.values() for sx in cfg["kualitatif"].values() for f in sx}
OK = dict(QUAL_ALL, sehat=True, cacat_fisik=False, silsilah_ada=True, reproduksi_normal=True, libido_semen_ok=True,
          ambing_ok=True, cf_umur=1.0, cf_visual=1.0)


def c(rumpun, jk, umur, TP, PB, LD, LS=None, **kw):
    return dict(OK, rumpun=rumpun, jenis_kelamin=jk, umur_standar=umur, TP=TP, PB=PB, LD=LD, LS=LS, **kw)


CASES = [  # (nama, input, status diharapkan, kelas diharapkan)
 ("T1 Bali jantan 12 bln Kelas I", c("bali", "jantan", "12bln", 102, 96, 127, 16), "LAYAK", 1),
 ("T2 Bali betina 18 bln Kelas II", c("bali", "betina", "18bln", 105, 106, 138), "LAYAK", 2),
 ("T3 Bali jantan 205 hari Kelas III", c("bali", "jantan", "205hari", 83, 78, 98), "LAYAK", 3),
 ("T4 Bali jantan 24 bln skrotum 23 (<24)", c("bali", "jantan", "24bln", 121, 121, 167, 23), "TIDAK LAYAK", 0),
 ("T5 Bali betina sakit", c("bali", "betina", "12bln", 99, 97, 126, sehat=False), "TIDAK LAYAK", 0),
 ("T6 Bali betina 24 bln ambing tidak simetris", c("bali", "betina", "24bln", 111, 110, 151, ambing_ok=False), "TIDAK LAYAK", 0),
 ("T7 Bali Kelas I, ciri kualitatif menyimpang", c("bali", "jantan", "12bln", 102, 96, 127, 16, warna_sesuai=False), "LAYAK", 1),
 ("T8 Aceh jantan 12 bln memenuhi minimum", c("aceh", "jantan", "12bln", 90, 89, 103, 17), "LAYAK", 1),
 ("T9 Aceh jantan 12 bln skrotum 16 (<17)", c("aceh", "jantan", "12bln", 90, 89, 103, 16), "TIDAK LAYAK", 0),
 ("T10 Aceh betina 18 bln memenuhi minimum", c("aceh", "betina", "18bln", 92, 91, 109), "LAYAK", 1),
 ("T11 PO jantan 24 bln Kelas I", c("po", "jantan", "24bln", 132, 132, 160, 31), "LAYAK", 1),
 ("T12 PO betina 12 bln Kelas II", c("po", "betina", "12bln", 104, 100, 125), "LAYAK", 2),
 ("T13 PO betina 205 hari TP 91 (<92)", c("po", "betina", "205hari", 91, 97, 120), "TIDAK LAYAK", 0),
 ("T14 Ukuran yang sama dengan T1 dinilai PO: hanya Kelas III", c("po", "jantan", "12bln", 102, 96, 127, 16), "LAYAK", 3),
]

if __name__ == "__main__":
    benar = 0
    for nama, inp, st, kl in CASES:
        h = jalankan_konsultasi(KB, inp)["keputusan"]
        ok = h["status"] == st and h["kelas"] == kl
        benar += ok
        print(f"{'OK   ' if ok else 'GAGAL'} {nama}: {h['status']} {h['label_kelas']} CF {h['cf']:.2f} skor {h['skor']}"
              f"{' [catatan kualitatif]' if h['catatan'] else ''}")
    print(f"Akurasi: {benar}/{len(CASES)} = {benar / len(CASES) * 100:.0f}%")
