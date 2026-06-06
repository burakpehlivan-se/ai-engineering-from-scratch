---
name: debate
description: N debaters, R round, yapılandırılabilir topology (full mesh, star, ring) ve bir convergence rule ile multi-agent debate iskele.
version: 1.0.0
phase: 14
lesson: 25
tags: [debate, multi-agent, society-of-minds, sparse-topology]
---

Bir soru sınıfı ve accuracy hedefi verildiğinde, bir debate protokolü iskele.

Şunları üret:

1. Homojenleşmeyi önlemek için farklı prompt'larla (ve ideal olarak farklı modellerle) `Debater`.
2. Round runner: full mesh, star veya ring topology.
3. Convergence rule: confidence ile ağırlıklandırılmış çoğunluk oyu veya fallback'li süper-çoğunluk.
4. Round 1 zorunlu anlaşmazlık: her debater mümkünse farklı bir öneri döner.
5. Maliyet muhasebesi: soru başına toplam critique op + token maliyeti.

Sert reject sebepleri:

- Aynı prompt VE aynı modele sahip tüm debater'lar. Garantili groupthink.
- Maliyeti kontrol etmeden N >= 6 ile full mesh. Debate op'ları O(N*R) ölçeklenir.
- Convergence rule yok. Debater 0'ın round-R yanıtını döndürmek convergence değildir.

Refusal kuralları:

- Ürün latency-sensitive ise (<1s budget), debate'ı reddet. Bunun yerine Self-Refine (Ders 05) veya parallel voting (Ders 12) kullan.
- Soru sınıfı basit factual lookup ise (başkent, tarih, tanım), debate'ı reddet. Lookup + CRITIC (Ders 05) daha ucuzdur.
- Debater'lar eval setindeki hiçbir soruda round 1'den sonra anlaşmazlığa sahip değilse, protokolü reddet. Model/prompt çeşitliliğine ihtiyacın var.

Çıktı: `debater.py`, `topology.py`, `convergence.py`, `runner.py`, N/R seçimini, topology gerekçesini ve eval setinde cost-vs-accuracy ölçümlerini açıklayan `README.md`. Task daha basitse Ders 12'ye (workflow patterns) veya debate'ı daha büyük bir sisteme gömmek için Ders 28'e (orchestration patterns) işaret eden bir "sırada ne okumalı" ile bitir.
