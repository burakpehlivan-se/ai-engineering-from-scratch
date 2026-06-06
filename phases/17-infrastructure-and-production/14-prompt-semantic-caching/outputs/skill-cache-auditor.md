---
name: cache-auditor
description: Bir LLM istem şablonunu ve trafik kalıbını önbelleklenebilirlik için denetle. İstem yeniden yapılandırması, TTL seçimi, paralelleştirme düzeltmesi ve semantik-önbellek eşiği öner.
version: 1.0.0
phase: 17
lesson: 14
tags: [caching, prompt-cache, semantic-cache, anthropic, openai, parallelization, ttl]
---

Bir istem şablonu, trafik kalıbı (varış oranı, paralel faktör) ve sağlayıcı (Anthropic, OpenAI, Gemini, self-hosted vLLM) verildiğinde bir önbellek denetimi üret.

Üretilecekler:

1. **Önek yapısı.** Şablonu statik (önbelleklenebilir) ve dinamik (önbelleklenemez) bölümlere ayır. Önek'te şu anda bulunan herhangi bir dinamik içeriği işaretle ve yeniden yazmayı öner.
2. **TTL seçimi.** Anthropic 5-dk (1.25x yazma) vs 1-saat (2x yazma). Varış oranına göre seç — önek bir saat içinde tutarlı olarak yeniden kullanılıyorsa 1-saat kazanır.
3. **Paralelleştirme denetimi.** Paylaşılan önekli paralel istekleri say. N > 2 ve paralelse, serialize-first-then-fanout kalıbını zorunlu kıl. Beklenen fatura azalmasını nicelleştir.
4. **Semantik önbellek seçimi.** L1'in değerinde olup olmadığına karar ver. Açık-uçlu sohbet: muhtemelen değil (düşük isabet). Yapılandırılmış SSS / destek: evet. Kosinüs eşiğini ayarla, 0.95'ten başla; yalnızca yanıt-kalite eval'leri ile aşağı doğru ayarla.
5. **Beklenen tasarruf.** Mevcut trafik ve öngörülen isabet oranları verildiğinde önbellek-yok taban çizgisine karşı aylık $ deltasını hesapla.
6. **Gözlemlenebilir.** Regresyonları yakalayan bir pano metriği: son kayan saat üzerinden L2 önbellek isabet oranı; >%20 düşerse uyar.

**Hard rejects (zorunlu redler):**
- Beklenen isabet oranını ve yazma primini hesaplamadan "%50 tasarruf" iddia etmek. Reddet — katman başına hesapla.
- Basit bir yeniden yazma onu dışarı çıkaracakken dinamik içeriği önekte bırakmak. Onay vermeyi reddet.
- Serialize-first kalıbı olmadan paylaşılan önekli paralel istekleri ateşlemek. Reddet — 5-10x fatura enflasyonunu belirt.

**Reddetme kuralları:**
- İstem token olarak >%80 dinamik içerikse, önbellek tasarrufu vaat etmeyi reddet. En iyi ihtimalle semantik önbellek öner.
- Semantik önbellek eşiği yanıt-kalite eval'i olmadan 0.85'in altına düşürülürse, reddet — halüsinasyon önbellek riski.
- Sağlayıcı açık cache_control'ü desteklemiyorsa (Anthropic-dışı, Gemini-v1-dışı) ve yalnızca otomatik-önbellekleme yapıyorsa, isabet oranının fırsatçı olduğunu, garanti edilmediğini not et.

**Çıktı:** Önek yeniden yazımı, TTL, paralelleştirme kalıbı, L1 eşiği, beklenen tasarruf, gözlemlenebilir listeleyen tek sayfalık bir denetim. Herhangi bir şablon değişikliğinden sonra istemleri yeniden denetleme önerisiyle bitir.
