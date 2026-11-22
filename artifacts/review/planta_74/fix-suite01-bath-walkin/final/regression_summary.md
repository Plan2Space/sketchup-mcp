# SKP Proof-of-Progress Summary — fix-suite01-bath-walkin (2026-11-22)

## Change

No Banho 01 (`r005`, banho da Suíte 01) da planta_74 o box tem 1,02 m de frente. Vidro fixo de 0,46 m + folha de correr de
0,61 m deixava 0,33 m de entrada: `functional_clearance` `shower.entry_width` **INVALID** (mínimo 0,60 m). Porta de correr
nesse vão nunca passa de ~0,47 m. Decisão do Felipe no chat (2026-11-22): **walk-in fixo**. Registrada em
`tools/rooms/bathroom/layout_decisions.py` com origem `user_request`, só para `planta_74/r005`. Nenhuma parede, abertura ou
cômodo muda; os outros banhos ficam com o box de correr. Vaso (Roca The Gap) e bancada (Celite Elite) seguem a curadoria de
2026-08-08 e **não** foram alterados.

## Canonical input

- **PDF**: `projects/planta_74/source/planta_74.pdf` (não lido nem alterado)
- **Consensus**: `fixtures/planta_74/consensus_with_human_walls_and_soft_barriers.json`
  - SHA256 (LF): `69dbbf0394b5197321e511d5518cf6bb0ae6772879a6edfb285d4be36f3fe2be`
- **Builder commit before**: `b1be3a0f` (`develop`)
- **Builder commit after**: `b7a27a9f` (commit sob prova, árvore limpa)
- **SU version**: 26.0.429

## Artifacts

### Before

- **SKP**: o `develop` (`b1be3a0f`) materializa o mesmo apartamento com o box de correr (`su_furnish` de 2026-11-22, em `runs/`);
  o "antes" fiel desta mudança é o snapshot FP-047 das caixas do mesmo pipeline (`snapshot_sha256 561f8cf0…`, 390 peças).

### After

- **SKP**: `artifacts/review/planta_74/fix-suite01-bath-walkin/final/planta_74_after.skp`
  (sha256 `4e5506eafb2c5338277dc93a54741b4ab3db32b554f3262916eb84eeb59a8d6b`, 3.345.902 bytes)
- **Top render**: `model_top_after.png` (apartamento), `suite01_top_after.png` (Suíte 01 + Banho 01), `banho01_top_after.png`
- **Iso render**: `model_iso_after.png`
- **Vistas internas do banho**: `banho01_walkin_entrada.png`, `banho01_walkin_lateral.png`
- **Inspeção do modelo reaberto** (outro processo, PID 21064): 86 grupos de topo; `BANHO 01 › Box` = `box_vidro` 0,341 m,
  `kb_perfil` de parede (2,43 m), barra estabilizadora (`kb_perfil` 0,80 m no topo), `kb_piso_box`, chuveiro; **sem**
  `kb_folha`, `kb_trilho`, `kb_guia`, `kb_puxador`.

## Before / After comparison

| Eixo | Before | After | Verdict | Evidência específica |
|---|---|---|---|---|
| `wall_fidelity` | consensus inalterado | consensus inalterado | N/A | nenhuma parede tocada; nova linha de base FP-044 (`../fp044_baseline.json`): canônicos idênticos, só `BANHO 01` muda |
| `door_fidelity` | aberturas | aberturas | N/A | nenhuma abertura tocada; pré-voo `room_collisions` PASS |
| `shower_entry` | 0,33 m INVALID | **0,60 m** | PASS | `functional_clearance.evaluate_room(r005)` `shower.entry_width` mede o vão pelo espaço livre real (revestimento de pedra incluso); teste `test_functional_clearance_no_longer_flags_the_suite_box_entry` |
| `furniture_layout` | 390 peças | 385 peças | PASS | diff FP-047: 9 deltas, **todos em `BANHO 01 / Box`** (5 removidas: folha, puxador, guia, trilho, perfil da folha; 4 modificadas: vidro fixo, perfis, piso); os outros 7 cômodos idênticos |
| `wall_penetration` | Box 0,062 m (D-007) | Box 0,041 m | PASS (melhora) | gêmeo em caixas FP-056: `r005|CONTAINMENT|Box` 0,062 → 0,041 e `r005|WALL|Box` 0,051 → 0,041; resto da linha de base FP-055 P4 idêntico |
| `materialization` | — | `.skp` salvo, fechado, reaberto em outro processo | PASS | 385/385 placeholders posicionados; inspeção acima |

## Veredito

**PASS (L1 + L2).** Visual: `PENDING_HUMAN` — o Felipe decide no chat.
