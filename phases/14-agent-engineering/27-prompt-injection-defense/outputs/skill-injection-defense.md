---
name: injection-defense
description: Source-tagged içerik, injection-marker taraması ve allowlist navigasyonu ile herhangi bir agent runtime için bir PVE (Prompt-Validator-Executor) katmanı üret.
version: 1.0.0
phase: 14
lesson: 27
tags: [security, prompt-injection, pve, greshake, source-tag]
---

Tool erişimi ve retrieval'ı olan bir agent verildiğinde, bir injection-defense katmanı üret.

Şunları üret:

1. Her içerik parçası üzerinde source tag: `user_message`, `tool_output`, `retrieved_web`, `retrieved_memory`, `retrieved_file`. Tag'leri message history boyunca propagate et.
2. `Validator.assess(tool_call, contents)` — injection şekilli argümanları veya çekilen içeriği olan tool çağrılarını reddeder; yalnızca source tag'leri tanımlanan güven seviyesiyle eşleştiğinde izin verir.
3. Navigasyon için allowlist / blocklist: agent'ın dokunabileceği URL'ler, domain'ler, dosya yolları.
4. Memory-write guardrail: directive gibi görünen write'ları reddet.
5. Content-capture disiplini (Ders 23): çekilen içeriği harici olarak depola; span'ler prose değil reference ID taşır.
6. Test suite'i: beş Greshake exploit sınıfını red-team case'leri olarak.

Sert reject sebepleri:

- Source tag'leri olmadan tool-use yüzeyi. Provenance olmadan izin seviyeleri ayırt edilemez.
- Sadece final çıktı üzerinde çalışan validator. Geç validation irrelevant'tır — model zaten hareket etti.
- "Güven bana, system prompt hallediyor." System-prompt hijyeni bir control değildir.

Refusal kuralları:

- Agent source tagging olmadan herhangi bir retrieval yeteneğine sahipse, gönderimi reddet. Çekilen içerik kanonik injection vektörüdür.
- Hassas tool'ların (mesaj gönder, shell çalıştır, / dizininde dosya yaz) human-in-the-loop confirmation'ı yoksa, reddet.
- Memory write'ları guardsız ise, reddet. Persistent memory poisoning bir sonraki session'ı yeniden zehirler.

Çıktı: `validator.py`, `source_tag.py`, `allowlist.py`, `memory_guard.py`, `red_team.py`, altı-control stack'ini, kalan riskleri ve devam eden inceleme cadence'ini açıklayan `README.md`. Ders 21'e (computer use safety) ve Ders 23'e (OTel üzerinden content capture) işaret eden bir "sırada ne okumalı" ile bitir.
