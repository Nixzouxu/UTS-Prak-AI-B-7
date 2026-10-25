"""Working Memory: menyimpan fakta (input, turunan otomatis, hasil inferensi) beserta CF dan asal-usulnya."""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Fact:
    """Satu fakta di memori kerja."""
    name: str
    value: bool
    cf: float = 1.0
    source: str = "input"  # 'input' | 'auto' | 'rule:<ID>[+<ID>]'


class WorkingMemory:
    """Penyimpan fakta dengan struktur dictionary + jejak pembaruan (timeline)."""

    def __init__(self):
        self._facts: Dict[str, Fact] = {}
        self.timeline: List[str] = []

    def assert_fact(self, name: str, value: bool = True, cf: float = 1.0, source: str = "input") -> None:
        if not 0.0 <= cf <= 1.0:
            raise ValueError(f"CF fakta '{name}' harus 0..1, diterima {cf}")
        self._facts[name] = Fact(name, bool(value), round(cf, 4), source)
        self.timeline.append(f"[{source}] {name} = {bool(value)} (CF {cf:.2f})")

    def get(self, name: str):
        return self._facts.get(name)

    def is_true(self, name: str) -> bool:
        f = self._facts.get(name)
        return bool(f and f.value)

    def cf_of(self, name: str) -> float:
        f = self._facts.get(name)
        return f.cf if f else 1.0

    def facts(self) -> Dict[str, Fact]:
        return dict(self._facts)


def validate_inputs(inp: dict, cfg: dict) -> List[str]:
    """Validasi input pengguna terhadap konfigurasi rumpun `cfg`; kembalikan daftar error (kosong bila valid)."""
    err = []
    if inp.get("jenis_kelamin") not in ("jantan", "betina"):
        return ["Jenis kelamin harus jantan atau betina."]
    std = cfg["standar"][inp["jenis_kelamin"]].get(inp.get("umur_standar"))
    if std is None:
        return ["Kelompok umur tidak valid untuk rumpun dan jenis kelamin ini."]
    ranges = {"TP": (50, 200), "PB": (40, 200), "LD": (60, 260), "LS": (5, 50)}
    for p, (lo, hi) in ranges.items():
        if p == "LS" and "LS" not in std:
            continue
        v = inp.get(p)
        if v is None or not (lo <= v <= hi):
            err.append(f"{p} harus diisi dalam rentang {lo}-{hi} cm.")
    for c in ("cf_umur", "cf_visual"):
        if not 0.0 <= inp.get(c, 1.0) <= 1.0:
            err.append(f"{c} harus 0..1.")
    return err


def build_working_memory(inp: dict, cfg: dict) -> WorkingMemory:
    """Ubah input menjadi fakta; ukuran tubuh dikonversi menjadi fakta kelas (tp_k1 dst) sesuai standar rumpun."""
    wm = WorkingMemory()
    sex, rumpun = inp["jenis_kelamin"], inp["rumpun"]
    std = cfg["standar"][sex][inp["umur_standar"]]
    bulan = std["umur_bulan"]
    cf_umur, cf_vis = inp.get("cf_umur", 1.0), inp.get("cf_visual", 1.0)
    wm.assert_fact(rumpun, True, 1.0, "input")
    wm.assert_fact(sex, True, 1.0, "input")
    for f in ("sehat", "cacat_fisik", "silsilah_ada", "reproduksi_normal"):
        wm.assert_fact(f, inp.get(f, False), 1.0, "input")
    for f in cfg["kualitatif"][sex]:
        wm.assert_fact(f, inp.get(f, False), cf_vis, "input")
    # Fakta yang hanya dipersyaratkan pada umur tertentu (n/a -> dianggap terpenuhi)
    needs_libido = sex == "jantan" and bulan >= 18
    needs_ambing = sex == "betina" and bulan >= 18
    wm.assert_fact("libido_semen_ok", inp.get("libido_semen_ok", False) if needs_libido else True, 1.0,
                   "input" if needs_libido else "auto")
    wm.assert_fact("ambing_ok", inp.get("ambing_ok", False) if needs_ambing else True, 1.0,
                   "input" if needs_ambing else "auto")
    # Ukuran tubuh -> fakta kelas (CF mengikuti keyakinan penentuan umur). Rumpun tanpa kelas hanya memiliki k1.
    for p, key in (("TP", "tp"), ("PB", "pb"), ("LD", "ld"), ("LS", "ls")):
        if p in std:
            for k in range(1, len(std[p]) + 1):
                wm.assert_fact(f"{key}_k{k}", inp[p] >= std[p][k - 1], cf_umur, "auto")
        elif p == "LS" and sex == "jantan":  # skrotum tidak dipersyaratkan pada umur ini
            for k in (1, 2, 3):
                wm.assert_fact(f"ls_k{k}", True, 1.0, "auto")
    return wm
