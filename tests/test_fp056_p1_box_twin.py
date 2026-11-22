"""FP-056 P1: o gemeo em caixas (gate de proposta antes do SketchUp) reproduz os defeitos medidos no MODELO CONSTRUIDO."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# unico desvio aceito: medida a 0,1 mm do limiar (o construido mediu 0,52 mm na PAREDE; o gemeo 0,6 mm na CONTENCAO) —
# dentro do ruido de arredondamento da exportacao. Registrado, nao escondido.
BORDERLINE = {"r004|CONTAINMENT|backsplash"}
# mudanca DELIBERADA posterior a linha de base da FP-055 P4 (que fica intacta como retrato historico): o box walk-in do Banho 01
# (decisao Felipe 2026-11-22, bathroom/layout_decisions) tira o sistema de correr; a parte do box que ainda entra na laje (D-007)
# cai de 0,062 m para 0,041 m (CONTAINMENT) e de 0,051 m para 0,041 m (WALL). So estas duas chaves do r005|Box mudam.
CHANGED_SINCE_BASELINE = {"r005|CONTAINMENT|Box": 0.04095, "r005|WALL|Box": 0.04095}


@pytest.mark.planta74_scale
def test_box_twin_reproduces_the_built_defects_of_the_rooms_not_touched_by_the_fix():
    from tools.furnish_apartment import collect_boxes
    from tools.rooms.shared.project_paths import PLANTA_74_CONSENSUS
    from tools.validation import box_geometry as bx
    from tools.validation import defect_baseline as db
    con = json.loads(PLANTA_74_CONSENSUS.read_text("utf-8"))
    with contextlib.redirect_stdout(io.StringIO()):
        boxes, _ = collect_boxes(con)
    rooms = {r["id"]: str(r.get("name") or r["id"]) for r in con["rooms"] if r["id"] != "r001"}   # r001 = A.S. (RC-B)
    reps = bx.validate_boxes(con, boxes, PLANTA_74_CONSENSUS, rooms)
    base = [b for b in json.loads((ROOT / "artifacts/review/fp055/p4/defect_baseline.json").read_text("utf-8"))["defects"]
            if b["room_id"] != "r001"]
    got = {db.key(rid, f): db.measure(f) for rid, r in reps.items() for f in r["findings"]
           if f.get("check") in ("CONTAINMENT", "WALL", "OBJECTS", "DOOR") and (f.get("module") or f.get("modules")
                                                                              or f.get("door"))}
    assert set(got) - BORDERLINE == {b["key"] for b in base}
    for b in base:
        tol = 0.5 if b["unit"] == "deg" else 0.0002
        expected = CHANGED_SINCE_BASELINE.get(b["key"], b["measure"])
        assert abs(got[b["key"]] - expected) <= tol, (b["key"], got[b["key"]], expected)


@pytest.mark.planta74_scale
def test_service_fix_resolves_four_as_defects_and_the_omitted_counter_stays_a_program_regression():
    from tools.furnish_apartment import collect_boxes
    from tools.rooms.shared.project_paths import PLANTA_74_CONSENSUS
    from tools.validation import box_geometry as bx
    from tools.validation import defect_baseline as db
    con = json.loads(PLANTA_74_CONSENSUS.read_text("utf-8"))
    with contextlib.redirect_stdout(io.StringIO()):
        boxes, _ = collect_boxes(con)
    rep = bx.validate_boxes(con, boxes, PLANTA_74_CONSENSUS, {"r001": "A.S. | TERRACO SOCIAL | TERRACO TECNICO"})
    base = json.loads((ROOT / "artifacts/review/fp055/p4/defect_baseline.json").read_text("utf-8"))["defects"]
    program = json.loads((ROOT / "artifacts/review/fp056/p2/program_baseline.json").read_text("utf-8"))["program"]
    r = db.regression(rep, base, program)
    assert not r["new"] and not r["worse"]
    # 4 corrigidos por POSICAO; a bancada gourmet foi OMITIDA (circulacao) — o defeito dela sumiu com a peca, nao foi
    # corrigido, e a perda de programa fica reprovada ate a decisao AS-1 do Felipe (docs/reports/fp056/p2/README.md)
    assert set(r["resolved"]) == {"r001|CONTAINMENT|Armario de servico", "r001|CONTAINMENT|Condensadora",
                                  "r001|CONTAINMENT|Jardineira", "r001|CONTAINMENT|Maquina de lavar"}
    assert r["vanished_with_piece"] == ["r001|CONTAINMENT|Bancada gourmet"]
    assert r["status"] == "FAIL" and r["missing_program"] == ["r001|PROGRAM|Bancada gourmet", "r001|PROGRAM|Banqueta"]
