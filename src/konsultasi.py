"""Pipeline konsultasi: validasi -> working memory -> inferensi -> penjelasan."""
from .explanation import how
from .inference_engine import InferenceEngine
from .knowledge_base import KnowledgeBase
from .working_memory import build_working_memory, validate_inputs


def jalankan_konsultasi(kb: KnowledgeBase, inp: dict) -> dict:
    """Jalankan satu sesi konsultasi dan kembalikan entri hasil lengkap (siap disimpan ke log)."""
    cfg = kb.rumpun.get(inp.get("rumpun"))
    if cfg is None:
        raise ValueError("Rumpun sapi tidak dikenal.")
    err = validate_inputs(inp, cfg)
    if err:
        raise ValueError("; ".join(err))
    tunggal = cfg["kelas_tunggal"]
    wm = build_working_memory(inp, cfg)
    engine = InferenceEngine(kb.rules, kb.bobot_kelas, kb.rekomendasi)
    res = engine.run(wm, tunggal)
    labels = {**kb.labels, **(kb.labels_tunggal if tunggal else {})}
    return {"input": inp, "rumpun": cfg["nama"], "sni": cfg["sni"], "keputusan": res.keputusan, "trace": res.trace,
            "rules_used": res.rules_used, "how": how(res.keputusan["fakta_akhir"], res.trace, labels),
            "working_memory": {n: {"value": f.value, "cf": f.cf, "source": f.source} for n, f in wm.facts().items()}}
