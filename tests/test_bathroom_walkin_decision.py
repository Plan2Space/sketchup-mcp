"""Box walk-in do Banho 01 (Suite 01) da planta_74 — decisao do Felipe no chat, 2026-11-22.

Achado: com frente de 1,02 m, fixo de 0,46 m + folha de correr de 0,61 m deixava entrada de 0,33 m (functional_clearance
`shower.entry_width` INVALID, minimo 0,60 m); porta de correr nesse vao nunca passa de ~0,47 m. Escolha do Felipe: walk-in
fixo (so vidro fixo, sem folha), vao livre de 0,60 m. Vale SO para planta_74/r005; os outros banhos ficam como estao.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

pytestmark = pytest.mark.planta74_scale

CON = Path("fixtures/planta_74/consensus_with_human_walls_and_soft_barriers.json")
SLIDING_ONLY = {"kb_folha", "kb_puxador", "kb_guia", "kb_trilho"}


def _con():
    return json.loads(CON.read_text("utf-8"))


def _box(room_id):
    from tools.rooms.bathroom.layout import build_boxes
    boxes, out = build_boxes(_con(), room_id)
    parts = [b for b in boxes if b.get("module") == "Box"]
    iface = next(i for i in out["functional_interfaces"] if i["module"] == "Box")
    return parts, iface, out


def _seg_len_m(iface):
    (ax, ay), (bx, by) = iface["segment_in"]
    return math.hypot(bx - ax, by - ay) * 0.0254


def test_the_walkin_decision_is_registered_only_for_the_suite_bathroom():
    from tools.rooms.bathroom import layout_decisions as ld
    con = _con()
    [d] = ld.decisions_for(con, "r005")
    assert d["origin"] == "user_request" and d["box_style"] == "walk_in" and d["decided"] == "2026-11-22"
    assert d["entry_min"] == {"value": 0.60, "unit": "m", "origin": "derived"}
    assert ld.decisions_for(con, "r006") == [] and ld.decisions_for(con, "r007") == []
    assert ld.box_style(con, "r006") == "sliding" and ld.box_style(con, "r005") == "walk_in"


def test_suite_bathroom_box_is_walkin_with_a_free_entry_of_at_least_60cm():
    parts, iface, out = _box("r005")
    kinds = {p["kind"] for p in parts}
    assert "box_vidro" in kinds and not (kinds & SLIDING_ONLY)
    assert _seg_len_m(iface) >= 0.60 - 1e-3 and "walk-in" in iface["note"]
    assert out["box_style"] == "walk_in"


def test_suite_bathroom_fixed_glass_is_the_front_minus_the_entry():
    parts, iface, _ = _box("r005")
    glass = next(p for p in parts if p["kind"] == "box_vidro")
    xs = [c[0] for c in glass["corners"]]
    ys = [c[1] for c in glass["corners"]]
    long_side_m = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.0254
    # frente 1,02 m - 0,60 m de vao - a ponta que o revestimento de pedra da parede come (medida pela regra do gate)
    assert 0.30 <= long_side_m <= 0.42, long_side_m
    assert "fixo 0.3" in iface["note"]


def test_other_bathrooms_keep_the_sliding_box():
    parts, iface, out = _box("r006")
    assert "kb_folha" in {p["kind"] for p in parts} and out["box_style"] == "sliding"


def test_walkin_refuses_a_front_too_short_for_a_fixed_panel():
    from tools.rooms.bathroom.layout_decisions import WalkInError, walk_in_fixed_m
    assert walk_in_fixed_m(1.02, 0.60) == pytest.approx(0.42)
    with pytest.raises(WalkInError) as e:
        walk_in_fixed_m(0.85, 0.60)                            # sobraria 0,25 m de vidro: menos que o minimo do painel
    assert e.value.code == "WALKIN_FIXED_PANEL_TOO_SHORT"


def test_functional_clearance_no_longer_flags_the_suite_box_entry():
    import contextlib
    import io

    from tools.furnish_apartment import collect_boxes
    from tools.validation import functional_clearance as fc
    con = _con()
    with contextlib.redirect_stdout(io.StringIO()):
        boxes, _ = collect_boxes(con)
        ifaces = fc.collect_interfaces(con, boxes)
    evals = fc.evaluate_room(con, boxes, "r005", "BATHROOM", "BANHO 01", ifaces)
    [entry] = [e for e in evals if e.object_id == "Box" and e.constraint_id == "shower.entry_width"]
    assert entry.verdict in ("VALID", "PREFERRED"), (entry.verdict, entry.measured)
