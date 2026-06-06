---
name: mcp-threat-model
description: Bir MCP deployment'ı için, uygulanabilir saldırı sınıflarını, mevcut savunmaları ve Rule-of-Two ihlallerini adlandıran bir threat model üret.
version: 1.0.0
phase: 13
lesson: 15
tags: [mcp, security, tool-poisoning, threat-model, rule-of-two]
---

Bir MCP deployment'ı verildiğinde (server listesi, tool listesi, izin listesi), bir threat model üret.

Şunları üret:

1. Saldırı uygulanabilirliği. Yedi saldırı sınıfının her biri için (tool poisoning, rug pull, shadowing, MPMA, parasitic toolchain, sampling attacks, supply-chain masquerade), uygulanabilirliği tek cümlelik gerekçeyle yüksek / orta / düşük olarak derecelendir.
2. Savunma envanteri. Halihazırda mevcut savunmaları listele (hash pinning, statik detector, gateway, signed registry, MELON, Rule-of-Two enforcement).
3. Rule of Two denetimi. Her tool'u untrusted / sensitive / consequential olarak sınıflandır ve tek bir turda üçünün herhangi bir kombinasyonunu işaretle.
4. Eksik savunmalar. Mevcut tehdit profili göz önüne alındığında henüz uygulanmamış en yüksek kaldıraçlı savunmayı adlandır.
5. Runbook. Ekibin güvenlik duruşunu iyileştirmek için önümüzdeki hafta atması gereken üç eylem.

Sert reject sebepleri:
- "Saldırı sınıfı X uygulanmaz çünkü bu server'a güveniyoruz" diyen herhangi bir threat model. Bir server'ın compromise edileceğini varsay.
- Sessiz üzerine yazan namespace çözümlemesi kullanan herhangi bir deployment.
- Sampling etkin ama oturum başına rate limiter olmayan herhangi bir deployment.

Refusal kuralları:
- Deployment'ta onaylı tool açıklamalarının dokümantasyonu yoksa, reddet ve önce hash pinning'i zorunlu kıl.
- Deployment, public unsigned MCP registry'leri kullanıyorsa, supply-chain riskini işaretle ve verified bir registry'e migration öner.
- Herhangi bir tool untrusted input, sensitive data ve consequential action'ı birleştiriyorsa, onaylamayı reddet ve bölme talep et.

Çıktı: saldırı uygulanabilirlik tablosu, savunma envanteri, Rule-of-Two flag listesi ve üç eylemli runbook içeren tek sayfalık bir threat model. Bu deployment için en yüksek değerli tek güvenlik eklemesiyle bitir.
