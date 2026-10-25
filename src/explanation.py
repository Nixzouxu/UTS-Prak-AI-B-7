"""Explanation Facility: WHY (mengapa data ditanyakan) dan HOW (bagaimana kesimpulan diperoleh)."""
from typing import Dict, List


def why(fact: str, rules: Dict[str, dict], labels: Dict[str, str]) -> str:
    """Jelaskan mengapa sebuah fakta ditanyakan: rule mana yang memakainya."""
    used = [rid for rid, r in rules.items() if fact in [c.lstrip("!") for c in r["IF"]]]
    if not used:
        return f"'{labels.get(fact, fact)}' belum dipakai rule mana pun."
    tujuan = sorted({labels.get(rules[r]["THEN"], rules[r]["THEN"]) for r in used})
    return (f"'{labels.get(fact, fact)}' diperlukan oleh rule {', '.join(used)} "
            f"untuk menyimpulkan: {'; '.join(tujuan)}.")


def how(goal: str, trace: List[dict], labels: Dict[str, str], _depth: int = 0, _seen=None) -> List[str]:
    """Telusuri rantai penalaran mundur dari kesimpulan `goal` memakai jejak inferensi."""
    _seen = _seen if _seen is not None else set()
    lines = []
    for st in (s for s in trace if s["THEN"] == goal):
        if st["rule"] in _seen:
            continue
        _seen.add(st["rule"])
        pad = "   " * _depth
        conds = " AND ".join(labels.get(c.lstrip('!'), c) if not c.startswith("!") else "TIDAK " + labels.get(c[1:], c[1:])
                             for c in st["IF"])
        lines.append(f"{pad}{st['rule']}: IF {conds} THEN {labels.get(goal, goal)} "
                     f"(CF rule {st['cf_rule']}, CF hasil {st['cf_sesudah']:.2f})")
        for c in st["IF"]:
            if not c.startswith("!"):
                lines += how(c, trace, labels, _depth + 1, _seen)
    return lines


def format_report(entry: dict, labels: Dict[str, str]) -> str:
    """Susun laporan teks hasil konsultasi (dipakai untuk tampilan dan ekspor TXT/PDF)."""
    k = entry["keputusan"]
    out = [f"HASIL KONSULTASI {entry.get('id', '')}", f"Waktu     : {entry.get('waktu', '')}",
           f"Rumpun   : {entry.get('rumpun', '-')} ({entry.get('sni', '-')})",
           f"Kesimpulan: {k['status']}" + (f" - {k['label_kelas']}" if k.get("label_kelas") else ""),
           f"Kepercayaan: {k['cf'] * 100:.1f}%", f"Skor kelayakan: {k['skor']}/100",
           f"Rekomendasi: {k['rekomendasi']}"]
    if k.get("catatan"):
        out.append("Catatan: ciri kualitatif menyimpang dari SNI; verifikasi kemurnian rumpun.")
    out += ["", "Penjelasan (HOW):"] + entry.get("how", []) + ["", "Rules yang menyala: " + ", ".join(entry["rules_used"])]
    return "\n".join(out)
