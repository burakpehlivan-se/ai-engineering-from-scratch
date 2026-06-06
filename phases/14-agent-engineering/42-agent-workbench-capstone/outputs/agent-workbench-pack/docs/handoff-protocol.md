# Handoff Protokolü

Her session şunları içeren bir handoff paketiyle sonlanır:

- summary
- changed_files
- commands_run
- failed_attempts
- open_risks (severity + detail)
- next_action (tek somut adım)
- verdict_pointer (verification + review raporlarına path)

Paket hem handoff.md (insanlar) hem de handoff.json (bir sonraki agent) olarak gelir.
Eksik field'lar session-end hook'unu durdurur.
