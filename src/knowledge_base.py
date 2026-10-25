"""Manajemen knowledge base (JSON): muat, simpan, tambah/ubah/hapus rule, validasi, pencarian."""
import json, re
from pathlib import Path
from typing import Dict, List, Optional


class KnowledgeBase:
    """Knowledge acquisition: CRUD rule dengan validasi dan penyimpanan ke file JSON."""

    JENIS = ("faktual", "heuristik")

    def __init__(self, path):
        self.path = Path(path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.meta, self.rules = data["meta"], data["rules"]
        self.rumpun, self.labels = data["rumpun"], data["label_fakta"]
        self.labels_tunggal = data.get("label_tunggal", {})
        self.bobot_kelas, self.rekomendasi = data["bobot_kelas"], data["rekomendasi"]
        self._data = data

    def save(self) -> None:
        self._data["rules"] = self.rules
        self.path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")

    def validate_rule(self, rid: str, rule: dict, creating: bool = True) -> List[str]:
        err = []
        if not re.fullmatch(r"[A-Za-z0-9_]+", rid or ""):
            err.append("ID rule hanya boleh huruf/angka/underscore.")
        if creating and rid in self.rules:
            err.append(f"ID {rid} sudah ada.")
        conds = rule.get("IF")
        if not isinstance(conds, list) or not conds or not all(isinstance(c, str) and c.strip("!") for c in conds):
            err.append("IF harus berisi minimal satu kondisi.")
        then = rule.get("THEN", "")
        if not then or not isinstance(then, str):
            err.append("THEN wajib diisi.")
        elif conds and then in [c.lstrip("!") for c in conds]:
            err.append("THEN tidak boleh sama dengan salah satu kondisi IF.")
        cf = rule.get("CF")
        if not isinstance(cf, (int, float)) or not 0 < cf <= 1:
            err.append("CF harus di antara 0 (tidak termasuk) dan 1.")
        if rule.get("jenis") not in self.JENIS:
            err.append("Jenis harus faktual atau heuristik.")
        if not rule.get("sumber"):
            err.append("Sumber pengetahuan wajib dicantumkan.")
        if not err and self._has_cycle({**self.rules, rid: rule}):
            err.append("Rule menyebabkan siklus penalaran (circular).")
        return err

    @staticmethod
    def _has_cycle(rules: Dict[str, dict]) -> bool:
        graph: Dict[str, set] = {}
        for r in rules.values():
            for c in r["IF"]:
                graph.setdefault(c.lstrip("!"), set()).add(r["THEN"])
        state: Dict[str, int] = {}

        def dfs(n):
            state[n] = 1
            for m in graph.get(n, ()):
                if state.get(m) == 1 or (state.get(m) is None and dfs(m)):
                    return True
            state[n] = 2
            return False
        return any(state.get(n) is None and dfs(n) for n in list(graph))

    def add_rule(self, rid: str, rule: dict) -> List[str]:
        err = self.validate_rule(rid, rule, True)
        if not err:
            self.rules[rid] = rule
            self.save()
        return err

    def update_rule(self, rid: str, rule: dict) -> List[str]:
        if rid not in self.rules:
            return [f"Rule {rid} tidak ditemukan."]
        err = self.validate_rule(rid, rule, False)
        if not err:
            self.rules[rid] = rule
            self.save()
        return err

    def delete_rule(self, rid: str) -> List[str]:
        """Hapus rule; mengembalikan peringatan fakta turunannya yang mungkin masih dipakai rule lain."""
        if rid not in self.rules:
            return [f"Rule {rid} tidak ditemukan."]
        then = self.rules.pop(rid)["THEN"]
        self.save()
        dep = [r for r, v in self.rules.items() if then in [c.lstrip("!") for c in v["IF"]]]
        return [f"Peringatan: fakta '{then}' masih dipakai rule {', '.join(dep)}."] if dep else []

    def search(self, keyword: str = "", jenis: Optional[str] = None) -> Dict[str, dict]:
        """Cari rule berdasarkan kata kunci (gejala/fakta/kesimpulan/deskripsi) dan jenis pengetahuan."""
        kw = keyword.lower().strip()
        out = {}
        for rid, r in self.rules.items():
            hay = " ".join(r["IF"] + [r["THEN"], r.get("deskripsi", "")] +
                           [self.labels.get(c.lstrip("!"), "") for c in r["IF"]]).lower()
            if (not kw or kw in hay) and (not jenis or r["jenis"] == jenis):
                out[rid] = r
        return out
