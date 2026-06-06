---
name: parallel-call-safety-check
description: Bir tool registry'sini güvenli paralelleştirme açısından denetle. Her tool'u parallel_safe olarak işaretle, sıralama bağımlılıklarını not et ve downstream rate-limit riskini bildir.
version: 1.0.0
phase: 13
lesson: 03
tags: [parallel-tool-calls, streaming, correlation, rate-limits]
---

Bir tool registry'si (isim, açıklama ve executor'lara sahip tool listesi) verildiğinde, `parallel_safe: bool`, `ordering_deps: [tool_name]` ve `rate_limit_group: name` alanları eklenmiş notlandırılmış bir kopya döndür.

Şunları üret:

1. Tool başına sınıflandırma. Her tool için karar ver: aynı turda paralel çalıştırılması güvenli mi (pure read'ler, farklı kaynaklar); güvensiz mi (mutation'lar, paylaşılan kaynaklar, dış rate limit'ler).
2. Bağımlılık grafı. Bir tool'un çıktısının başka bir tool'un girdisine beslenmesi gereken çiftleri tespit et. Bir tur içinde paralelleştirilemez. `ordering_deps` ile işaretle.
3. Rate-limit gruplandırması. Aynı downstream API'sine giden tool'lar bir grup paylaşır. Host, tool başına değil grup başına eşzamanlılığı sınırlandırmalıdır.
4. Güvenlik önerileri. Her güvensiz tool için, o tur için parallel'in kapatılmasını mı, sıraya alınmasını mı yoksa kaynağa göre shard'lanmasını mı önerdiğini belirt.
5. Sağlayıcıya özgü bayraklar. Set içinde herhangi bir güvensiz tool varsa, OpenAI'de `parallel_tool_calls=false` veya Anthropic'te `disable_parallel_tool_use=true` öner.

Sert reject sebepleri:
- Denetimden sonra sınıflandırma içermeyen herhangi bir registry. Default-deny; bilinmiyor demek güvensiz demektir.
- Paylaşılan bir kaynak üzerinde `parallel_safe: true` olarak işaretlenmiş herhangi bir write-path tool. Race condition oluşturur.
- `rate_limit_group` olmadan rate-limit'li bir dış API'ye giden herhangi bir tool.

Refusal kuralları:
- Tüm tool'ları inceleme yapmadan parallel-safe işaretleme isteği gelirse reddet.
- Registry, aynı kaynak üzerinde consequential tool'lar içeriyorsa (aynı path üzerinde `delete_file` ve `write_file`), paralelleştirmeyi reddet ve sandbox seviyesinde serileştirme için Faz 14 · 09'a yönlendir.
- Kullanıcı, tool'larının asla race etmediğini iddia ederse, kanıt iste (test'ler, log'lar veya formal bir argüman). Race'ler üretimde sessizce gerçekleşir.

Çıktı: tool başına eklenen üç yeni alanı içeren JSON blob olarak revize edilmiş bir registry, ardından en yüksek riskli paralelleştirme seçimini ve önerilen mitigation'ı adlandıran kısa bir özet. Mevcut tur için önerilen bir `tool_choice` override ile bitir.
