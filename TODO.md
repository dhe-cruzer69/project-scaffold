# AriexCore Model-Fleet Engine — Task Tracking

## Goal
Turn the existing generic `src/arx/ai/` provider router into a working
**AriexCore multi-model fleet**: 5 expert models (Meaw, Fab, Ops, Sony, Helex)
sharing provider backends, driven by an intelligent auto-router with
model cascading — modeled on `ARIEXCORE_BLUEPRINT.md`.

## Tasks
- [x] Analyze existing `src/arx/ai/` provider/router layer
- [x] Create `src/arx/ai/models.py` — 5 expert model definitions
- [x] Create `src/arx/ai/fleet.py` — ModelFleet orchestrator
- [x] Extend `src/arx/ai/router.py` — auto-router + cascading
- [x] Update `src/arx/ai/__init__.py` — export new components
- [x] Create `test_fleet.py` — self-test for routing/cascading/health
- [x] Run `python test_fleet.py` to verify
  - ✅ 5 experts registered
  - ✅ auto-router classification correct (all 5 capabilities)
  - ✅ cascade ladder (helex → sony → meaw) works
  - ✅ health reporting works
  - ✅ backward compatibility with generic `ai` router preserved
  - ⚠️ local Ollama `/api/chat` returns 404 (pre-existing env issue, not code)
- [x] Run `test_ai.py` backward compatibility check
  - ⚠️ same Ollama 404 — pre-existing, unrelated to fleet changes
