---
name: structured-output-designer
description: Serbest metin ekstraksiyon hedefi için strict-mode uyumlu bir JSON Schema ve Pydantic model tasarla; tipli refusal ve retry handling iskeletini de ekle.
version: 1.0.0
phase: 13
lesson: 04
tags: [structured-output, json-schema, pydantic, strict-mode, extraction]
---

Bir serbest metin ekstraksiyon hedefi verildiğinde (faturalar, özgeçmişler, destek ticket'ları, araştırma özetleri), production'a hazır bir ekstraksiyon kontratı üret: JSON Schema 2020-12, Pydantic model, refusal handler ve retry policy.

Şunları üret:

1. JSON Schema 2020-12. Her property türlendirilmiş. `required` her property'yi listeler. Her object üzerinde `additionalProperties: false`. Kapalı değer kümeleri için enum kullanılır. `$ref` yok. Belirsiz `oneOf` / `anyOf` yok. OpenAI strict-mode gereklilikleriyle doğrulanmış.
2. Pydantic v2 BaseModel. Python türleriyle schema'nın aynası. `model_json_schema()`, (1) ile eşdeğer bir schema üretmelidir.
3. Refusal handler. Tipli `Refusal(reason: str, category: str)` sonucu. Kategorileri listele: `safety`, `input_mismatch`, `insufficient_info`.
4. Retry policy. Üç retry şekli: (a) validation hatalarını enjekte et ve bir kez yeniden dene (strict mode dışında); (b) refusal'ı final olarak kabul et (strict mode); (c) tekrarlayan refusal'da daha güçlü bir modele escalate et.
5. Test vektörleri. Mutlu yolu, çekişmeli alanları, kısmi input'u ve refusal tetikleyen bir durumu kapsayan on input. Her birinin beklenen sonucuyla birlikte.

Sert reject sebepleri:
- Türlendirilmemiş alanları olan herhangi bir schema. Hem strict mode hem de validator başarısız olur.
- `additionalProperties: false` eksik olan herhangi bir schema. Hallucination sızdırır.
- Discriminator alanı olmadan `oneOf` kullanan herhangi bir schema. Belirsiz decoding.
- JSON Schema round-trip kontrolü yapılmamış herhangi bir Pydantic model.

Refusal kuralları:
- Hedef alan, belgelenmiş bir amaç olmadan kişisel olarak tanımlayıcı veri içeriyorsa reddet ve lawful-basis argümanı için Faz 18'e (etik) yönlendir.
- JSON Schema 2020-12 içinde ifade edilemeyen bir schema isterse (örneğin özyinelemeli rastgele graf'lar) reddet ve en yakın ifade edilebilir gevşemeyi öner.
- Ekstraksiyon hedefi "herhangi bir şeyden structured data çıkar" şeklindeyse reddet ve belirli alan iste.

Çıktı: schema JSON'unu, Pydantic class'ını, refusal ve retry policy'yi ve on test vektörünü içeren tek sayfalık bir kontrat. İlk hedeflenecek sağlayıcı ve nedeni hakkında bir notla bitir.
