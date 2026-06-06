# Agent Workbench Pack

Güvenilir agent işi isteyen herhangi bir repo için drop-in workbench.

## Ne elde edersin

- Pack'in geri kalanına kısa router olan `AGENTS.md`.
- `docs/` kurallar, reliability policy, handoff protocol, reviewer rubric.
- State, board ve scope kontratı için `schemas/` JSON Schema'ları.
- `scripts/` init, feedback runner, verification gate, handoff generator.
- `bin/install.sh` idempotent installer.

## Hızlı başlangıç

```
bin/install.sh
$EDITOR task_board.json
python3 scripts/init_agent.py
```

## Versiyonlama

`VERSION` dosyası kontrattır. Major bump'lar bir state migration gerektirir.
