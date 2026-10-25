"""Logging konsultasi, statistik, dan ekspor hasil (TXT / CSV / PDF)."""
import csv, io, json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List


class ConsultationLog:
    """Menyimpan riwayat konsultasi ke JSON dan menghitung statistik penggunaan rule."""

    def __init__(self, path):
        self.path = Path(path)

    def load(self) -> List[dict]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self, entry: dict) -> dict:
        hist = self.load()
        entry["id"] = f"K{len(hist) + 1:04d}"
        entry["waktu"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hist.append(entry)
        self.path.write_text(json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")
        return entry

    def stats(self) -> dict:
        h = self.load()
        return {"total": len(h),
                "per_status": dict(Counter(e["keputusan"]["status"] for e in h)),
                "per_kelas": dict(Counter(e["keputusan"].get("label_kelas") for e in h if e["keputusan"].get("label_kelas"))),
                "per_rumpun": dict(Counter(e.get("rumpun", "-") for e in h)),
                "rule_terbanyak": Counter(r for e in h for r in set(e["rules_used"])).most_common()}

    @staticmethod
    def filter(history: List[dict], status=None, jenis_kelamin=None, teks="", rumpun=None) -> List[dict]:
        out = []
        for e in history:
            if status and e["keputusan"]["status"] != status:
                continue
            if jenis_kelamin and e["input"]["jenis_kelamin"] != jenis_kelamin:
                continue
            if rumpun and e["input"].get("rumpun") != rumpun:
                continue
            if teks and teks.lower() not in json.dumps(e, ensure_ascii=False).lower():
                continue
            out.append(e)
        return out

    @staticmethod
    def to_csv(history: List[dict]) -> str:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["id", "waktu", "rumpun", "jenis_kelamin", "umur", "TP", "PB", "LD", "LS", "status", "kelas", "cf", "skor", "rules"])
        for e in history:
            i, k = e["input"], e["keputusan"]
            w.writerow([e["id"], e["waktu"], e.get("rumpun", "-"), i["jenis_kelamin"], i["umur_standar"], i.get("TP"), i.get("PB"), i.get("LD"),
                        i.get("LS"), k["status"], k.get("label_kelas", ""), round(k["cf"], 3), k["skor"], " ".join(e["rules_used"])])
        return buf.getvalue()

    @staticmethod
    def to_pdf(text: str) -> bytes:
        """Ekspor laporan ke PDF memakai fpdf2 (opsional; lempar ImportError bila belum terpasang)."""
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)
        for line in text.encode("latin-1", "replace").decode("latin-1").split("\n"):
            pdf.multi_cell(0, 5.5, line or " ", new_x="LMARGIN", new_y="NEXT")
        return bytes(pdf.output())
