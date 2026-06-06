---
name: provider-portability-audit
description: Tek bir sağlayıcı üzerindeki function-calling entegrasyonunu, diğer ikisine taşındığında neyin kırılacağı açısından denetle.
version: 1.0.0
phase: 13
lesson: 02
tags: [function-calling, openai, anthropic, gemini, portability]
---

Tek bir sağlayıcıda (OpenAI, Anthropic veya Gemini) çalışan bir function-calling entegrasyonu verildiğinde, aynı mantığı diğer iki sağlayıcıda gönderirken ortaya çıkan tüm field rename'leri, davranış farklarını ve hard-limit çakışmalarını listeleyen bir portability audit (taşınabilirlik denetimi) üret.

Şunları üret:

1. Declaration diff. Entegrasyondaki her tool için, diğer iki sağlayıcının her biri için gereken envelope / field rename / schema çevirisini göster. Hedef sağlayıcının desteklemediği herhangi bir JSON Schema yapısını işaretle (Gemini: OpenAPI 3.0 alt kümesi; OpenAI strict: `$ref` yok, belirsiz `oneOf` yok).
2. Response diff. Tool call'un her sağlayıcının response shape'inde nerede bulunduğunu (`tool_calls[]` vs `content[]` block vs `parts[]` entry) ve `arguments` alanını ayrıştırmanın kimin sorumluluğunda olduğunu (OpenAI'de string, Anthropic ve Gemini'de object) belgele.
3. `tool_choice` diff. Entegrasyonun mevcut choice ayarını (auto / forbid / force / required), hedef sağlayıcının shape'ine eşle; eksik mode'ları işaretle.
4. Limit çakışmaları. Tool sayısı (128 / 64 / 64), schema derinliği (5 / 10 / pratikte sınırsız) ve argüman başına uzunluk limitlerini raporla. Hedef sağlayıcının limitlerini aşan herhangi bir entegrasyona block severity ver.
5. Strict-mode eşlemesi. Strict-mode semantiğinin hedefte korunup korunmadığını belirt. OpenAI `strict: true`'nun Anthropic'te tam bir karşılığı yoktur; Gemini `responseSchema` yaklaşır ancak request seviyesindedir.

Sert reject sebepleri:
- Non-OpenAI hedeflerde `arguments`'ın string olduğunu varsayan herhangi bir entegrasyon. Sessizce yanlış sonuçlar üretir.
- Anthropic veya Gemini'ye taşınırken router olmadan tool sayısı 64'ü aşan herhangi bir entegrasyon.
- Hedef OpenAI strict mode iken schema'sında `$ref` kullanan herhangi bir entegrasyon.

Refusal kuralları:
- Karşılığı olmayan sağlayıcıya özgü bir özelliğe bağımlı bir entegrasyonu (örneğin OpenAI Responses API stateful turn'ler, Anthropic computer-use block'ları) port etme isteği gelirse reddet ve hangi özelliğin hedef karşılığı olmadığını açıkla.
- Bir kazanan seçmen istenirse reddet. Seçim, host'un strict-mode ihtiyacına, maliyet profiline ve parallel-call gereksinimlerine bağlıdır.

Çıktı: tool başına diff tablosu, limit tablosu ve hedef sağlayıcı başına nihai bir "port verdict" (ship / needs-router / blocked-by-feature) içeren tek sayfalık bir denetim. En yüksek kaldıraçlı migration değişikliğini adlandıran tek bir cümleyle bitir.
