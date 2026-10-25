"""Inference Engine: forward chaining (data-driven) dengan Certainty Factor dan jejak penalaran."""
from dataclasses import dataclass, field
from typing import Dict, List

from .working_memory import WorkingMemory

MIN_CF = 0.2  # ambang CF premis agar rule boleh menyala


def combine_cf(old: float, new: float) -> float:
    """CF gabungan bukti paralel: CF = CF1 + CF2 * (1 - CF1)."""
    return old + new * (1 - old)


@dataclass
class InferenceResult:
    trace: List[dict] = field(default_factory=list)
    rules_used: List[str] = field(default_factory=list)
    keputusan: dict = field(default_factory=dict)


class InferenceEngine:
    """Forward chaining dua fase: fase 1 rule monoton, fase 2 rule dengan negasi fakta turunan."""

    def __init__(self, rules: Dict[str, dict], bobot_kelas: Dict[str, float], rekomendasi: Dict[str, str]):
        self.rules, self.bobot, self.rekomendasi = rules, bobot_kelas, rekomendasi
        self.derived = {r["THEN"] for r in rules.values()}

    def _late(self, rule: dict) -> bool:
        return any(c.startswith("!") and c[1:] in self.derived for c in rule["IF"])

    @staticmethod
    def _holds(wm: WorkingMemory, cond: str) -> bool:
        return (not wm.is_true(cond[1:])) if cond.startswith("!") else wm.is_true(cond)

    @staticmethod
    def _cond_cf(wm: WorkingMemory, cond: str) -> float:
        return wm.cf_of(cond.lstrip("!"))

    def run(self, wm: WorkingMemory, kelas_tunggal: bool = False) -> InferenceResult:
        res, fired = InferenceResult(), set()
        phases = ([r for r in sorted(self.rules) if not self._late(self.rules[r])],
                  [r for r in sorted(self.rules) if self._late(self.rules[r])])
        for ids in phases:
            changed = True
            while changed:
                changed = False
                for rid in ids:
                    if rid in fired:
                        continue
                    rule = self.rules[rid]
                    if not all(self._holds(wm, c) for c in rule["IF"]):
                        continue
                    premis = min(self._cond_cf(wm, c) for c in rule["IF"])
                    if premis < MIN_CF:
                        continue
                    fired.add(rid)
                    cf_rule = round(premis * rule["CF"], 4)
                    before = wm.cf_of(rule["THEN"]) if wm.is_true(rule["THEN"]) else 0.0
                    after = combine_cf(before, cf_rule) if before else cf_rule
                    old = wm.get(rule["THEN"])
                    src = f"{old.source}+{rid}" if old and old.source.startswith("rule:") else f"rule:{rid}"
                    wm.assert_fact(rule["THEN"], True, after, src)
                    res.rules_used.append(rid)
                    res.trace.append({"langkah": len(res.trace) + 1, "rule": rid, "IF": rule["IF"],
                                      "THEN": rule["THEN"], "cf_premis": round(premis, 3), "cf_rule": rule["CF"],
                                      "cf_sebelum": round(before, 3), "cf_sesudah": round(after, 3)})
                    changed = True
        res.keputusan = self._decide(wm, kelas_tunggal)
        return res

    def _decide(self, wm: WorkingMemory, tunggal: bool = False) -> dict:
        """Pilih kesimpulan akhir: kelas terbaik yang terbukti, kecuali ada bukti kuat 'tidak layak'."""
        roman = {1: "I", 2: "II", 3: "III"}
        tl = wm.cf_of("tidak_layak") if wm.is_true("tidak_layak") else 0.0
        if tl < 0.5:
            for k in (1, 2, 3):
                if wm.is_true(f"layak_kelas{k}"):
                    cf = wm.cf_of(f"layak_kelas{k}")
                    return {"status": "LAYAK", "kelas": k, "cf": cf, "skor": round(cf * self.bobot[str(k)] * 100, 1),
                            "label_kelas": "Memenuhi standar minimum" if tunggal else f"Kelas {roman[k]}",
                            "fakta_akhir": f"layak_kelas{k}", "rekomendasi": self.rekomendasi["min" if tunggal else str(k)],
                            "catatan": wm.is_true("catatan_kualitatif")}
        return {"status": "TIDAK LAYAK", "kelas": 0, "cf": tl or 1.0, "skor": 0.0, "label_kelas": "",
                "fakta_akhir": "tidak_layak", "rekomendasi": self.rekomendasi["0"], "catatan": False}
