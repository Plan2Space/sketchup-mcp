"""Decisoes de banheiro tomadas pelo Felipe (origem `user_request`), aplicadas sobre o layout do banheiro.

Mesmo padrao de `tools/rooms/bedroom/layout_decisions.py`: o builder propoe; quando a proposta reprova um gate e a saida muda o
produto do comodo, a escolha e do Felipe e fica registrada AQUI, com medida, unidade, origem e data — nunca como ajuste solto
dentro do algoritmo. Cada decisao vale para UMA planta (`consensus.source`) e UM comodo.

Decisoes:
  suite01-bath-walkin-2026-11-22: no Banho 01 (r005, banho da Suite 01) da planta_74 o box tem 1,02 m de frente. Fixo de 0,46 m
  + folha de correr de 0,61 m deixava 0,33 m de entrada (functional_clearance `shower.entry_width` INVALID, minimo 0,60 m), e
  porta de correr nesse vao nunca passa de ~0,47 m. O Felipe escolheu no chat: WALK-IN FIXO — so vidro fixo, sem folha; o vidro
  ocupa a frente menos o vao minimo (1,02 - 0,60 = 0,42 m), no extremo oposto a porta do comodo.
"""
from __future__ import annotations

DECISIONS: tuple[dict, ...] = (
    {"id": "suite01-bath-walkin-2026-11-22", "plant": "planta_74", "room_id": "r005",
     "origin": "user_request", "decided": "2026-11-22", "box_style": "walk_in",
     # minimo do registro FP-054 F1C (`shower.entry_width`, mesmo limite que o functional_clearance julga)
     "entry_min": {"value": 0.60, "unit": "m", "origin": "derived"}},
)
FIXED_PANEL_MIN_M = 0.30          # abaixo disso o "fixo" nao segura respingo: walk-in recusado, nao inventado


class WalkInError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _plant(con: dict) -> str:
    return str(con.get("source") or "").rsplit(".", 1)[0]


def decisions_for(con: dict, room_id: str) -> list[dict]:
    plant = _plant(con)
    return [d for d in DECISIONS if d["plant"] == plant and d["room_id"] == room_id]


def box_decision(con: dict, room_id: str) -> dict | None:
    return next((d for d in decisions_for(con, room_id) if d.get("box_style")), None)


def box_style(con: dict, room_id: str) -> str:
    d = box_decision(con, room_id)
    return d["box_style"] if d else "sliding"


def walk_in_fixed_m(front_m: float, entry_min_m: float) -> float:
    """Largura do vidro fixo do walk-in = frente - vao minimo. Recusa (codigo estavel) se o vidro ficar curto demais."""
    fixed = round(front_m - entry_min_m, 4)
    if fixed < FIXED_PANEL_MIN_M:
        raise WalkInError("WALKIN_FIXED_PANEL_TOO_SHORT",
                          f"frente {front_m:.3f} m - vao {entry_min_m:.2f} m = {fixed:.3f} m < {FIXED_PANEL_MIN_M} m")
    return fixed
