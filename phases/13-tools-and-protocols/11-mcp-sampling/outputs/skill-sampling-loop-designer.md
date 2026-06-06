---
name: sampling-loop-designer
description: Doğru modelPreferences, rate limit ve güvenlik onaylarıyla MCP sampling kullanan bir server-hosted agent loop tasarla.
version: 1.0.0
phase: 13
lesson: 11
tags: [mcp, sampling, agent-loop, model-preferences]
---

LLM muhakemesine ihtiyaç duyan sunucu tarafı bir algoritma verildiğinde (araştırma, özetleme, planlama, triyaj), MCP sampling tabanlı bir uygulama tasarla.

Şunları üret:

1. Loop yapısı. Her sampling round'unu numaralandır, prompt shape'ini ve beklenen output type'ını belirt.
2. Round başına `modelPreferences`. Round başına cost / speed / intelligence ağırlığı (toplam 1.0). Bir "pick files" round'u cost'a yaslanır; bir "synthesize" round'u intelligence'a yaslanır.
3. Rate limit. Invocation başına `max_samples_per_tool` belirle; sayıyı gerekçelendir.
4. Güvenlik kancaları. Client'ın bir confirmation dialog'u göstermesi gereken yeri ve refusal yolunun ne yaptığını belirt.
5. SEP-1577 dahil etme. Sampling içinde tool kullanılıp kullanılmayacağına karar ver; evet ise, drift riskini işaretle ve tool listesini belirt.

Sert reject sebepleri:
- Rate limit'i olmayan herhangi bir loop. Loop bomb ve kaynak hırsızlığı riski.
- `includeContext: "allServers"` belirleyen herhangi bir loop. Cross-server sızıntı.
- Server'ın, kullanıcı onayı olmadan tool input olarak geri beslenen içeriği üretmesini istediği herhangi bir loop. Confused-deputy vektörü.

Refusal kuralları:
- Server'ın kendi LLM kimlik bilgileri varsa, sampling'in gerçekten gerekli olup olmadığını sor; doğrudan çağrılar daha basit olabilir.
- Kullanım durumu tek seferlik bir tool çağrısıysa, sampling loop tasarlamayı reddet; sampling, çok turlu muhakeme içindir.
- Kullanıcı, niyetini son kullanıcıdan gizleyen bir sampling loop isterse, kategorik olarak reddet (gizli sampling).

Çıktı: loop adımlarını, round başına modelPreferences'ı, rate limit'i ve güvenlik kontrol listesini içeren tek sayfalık bir tasarım. Tasarımla ilgili herhangi bir SEP-1577 (sampling içinde tools) drift riskini işaretleyen bir notla bitir.
