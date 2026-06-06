# AGENTS.md

Bir agent workbench ile çalışan bir repository içindesin.

Hareket etmeden önce şunları oku:

1. `agent_state.json` — son session'ın nerede durduğu.
2. `task_board.json` — ne devam ediyor, ne sırada.
3. `docs/agent-rules.md` — startup, forbidden, done, uncertainty, approval.
4. `docs/reliability-policy.md` — bu workbench'in emmesi için tasarlandığı failure mode'ları.
5. `docs/handoff-protocol.md` — session sonunun ne üretmesi gerektiği.
6. `docs/reviewer-rubric.md` — tamamlanan işin nasıl yargılandığı.

Verification command: board'daki aktif task'taki `acceptance_criteria`'ya bak.

Pack versiyonu: 1.0.0
