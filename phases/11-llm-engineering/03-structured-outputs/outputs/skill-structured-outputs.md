---
name: skill-structured-outputs
description: Sağlayıcıya, güvenilirliğe ve karmaşıklığa göre doğru yapılandırılmış çıktı stratejisini seçme karar çerçevesi
version: 1.0.0
phase: 11
lesson: 03
tags: [structured-output, json, schema, constrained-decoding, pydantic, function-calling]
---

# Yapılandırılmış Çıktı Stratejisi

Yapılandırılmış veri gerektiren bir LLM uygulaması oluştururken, bu karar çerçevesini uygulayın.

## Her Yaklaşım Ne Zaman Kullanılır

**Prompt-tabanlı ("JSON Döndür"):** Yalnızca prototipleme. Ara sıra ayrıştırma hatalarının tolere edilebilir olduğu dahili araçlar için kabul edilebilir. Try/except ile yeniden deneme ekleyin. Üretim pipeline'larında asla kullanmayın.

**JSON modu (API bayrağı):** Garantili geçerli JSON'a ihtiyacınız var, ancak şema basit veya esnek. Şekli uygulama tarafında doğruladığınızda çalışır. Mevcut: OpenAI, Anthropic (araç kullanımı aracılığıyla), Google.

**Şema modu (kısıtlı kod çözme - constrained decoding):** Her çıktının belirli bir şemayla eşleşmesi gereken üretim sistemleri. Sıfır ayrıştırma hatası. Sıfır şema ihlali. Herhangi bir üretim çıkarma veya sınıflandırma görevi için varsayılan olarak bunu kullanın. Mevcut: OpenAI yapılandırılmış çıktıları, Outlines, Guidance.

**Fonksiyon çağırma / araç kullanımı:** Modelin sadece parametreleri doldurması değil, hangi fonksiyonu çağıracağını seçmesi gerekir. Birden fazla şemanız var ve model uygun olanı seçer. Ayrıca mevcut araç/fonksiyon altyapısıyla entegre olurken de kullanın.

**Instructor kütüphanesi:** Herhangi bir sağlayıcıda otomatik yeniden deneme ile Pydantic doğrulaması istiyorsunuz. Python projeleri için en iyi DX. OpenAI, Anthropic, Google ve açık kaynak modelleri sarar.

## Sağlayıcıya Özgü Kılavuz

**OpenAI:** `json_schema` türüyle `response_format` kullanın. Kısıtlı kod çözme yerleşiktir. Pydantic modelleri doğrudan çalışır. En güvenilir yapılandırılmış çıktı uygulaması.

**Anthropic:** Yapılandırılmış çıktı için araç kullanımını kullanın. İstenen şemayla tek bir araç tanımlayın. Model, şemayla eşleşen araç çağrısı argümanlarını döndürür. Güvenilir, ancak araç kullanımı API kalıbını gerektirir.

**Açık kaynak modeller (vLLM, Ollama):** Kısıtlı kod çözme için Outlines veya Guidance kullanın. Bu kütüphaneler JSON Schema'larını, üretim sırasında geçersiz tokenleri maskeleyen sonlu durum makinelerine derler. Çıkarımın yerel olarak çalıştırılmasını gerektirir.

## Şema Tasarım Kılavuzları

1. Mümkün olduğunda şemaları düz tutun. 2 seviyenin ötesindeki iç içe geçmiş nesneler çıkarma hatalarını artırır.
2. Kategorik alanlar için enum kullanın. Modelin doğru dizgiyi uydurmasına güvenmeyin.
3. Belirsiz alanları açık null desteğiyle gerekli yapın, isteğe bağlı yerine. Modeli bir karar vermeye zorlar.
4. Şema özelliklerine açıklamalar ekleyin. Model bunları talimat olarak okur.
5. Gerekli olmadıkça birleşim (union) türlerinden (oneOf/anyOf) kaçının. Kod çözme karmaşıklığını artırırlar.
6. Sayılara minimum/maksimum ayarlayın. Halüsinasyonlu aşırı değerleri yakalar.
7. Boş veya sınırsız çıktıları önlemek için dizilerde minItems/maxItems kullanın.

## Yaygın Başarısızlık Kalıpları ve Çözümleri

- **Model JSON'ı markdown çitlerine sarar**: prompt-tabanlı'dan JSON moduna veya şema moduna geçin
- **Şema-geçerli ama olgusal olarak yanlış**: çıkarma sonrasında bir LLM-as-judge doğrulama adımı ekleyin
- **Tutarsız enum değerleri**: kısıtlı kod çözmeye geçin veya son işlem normalleştirmesi ekleyin
- **Eksik isteğe bağlı alanlar**: onları gerekli yapın veya uygulama kodunda varsayılan değerler ekleyin
- **Çok yavaş çıkarma**: kısıtlı kod çözme %5-15 gecikme ekler, gecikmeye duyarlıysa şema karmaşıklığını azaltın
- **Çeşitli öğeleri olan büyük diziler**: girdiyi parçalara ayırın ve parça başına çıkarın, sonra sonuçları birleştirin

## Güvenilirlik Merdiveni

| Yaklaşım | Ayrıştırma Başarısı | Şema Eşleşmesi | Kurulum Çabası |
|----------|-------------|-------------|--------------|
| Prompt-tabanlı | ~%90 | ~%80 | 1 dakika |
| JSON modu | %100 | ~%90 | 5 dakika |
| Şema modu | %100 | ~%99 | 15 dakika |
| Kısıtlı kod çözme | %100 | %100 | 30 dakika |
| Instructor + yeniden deneme | %100 | ~%99.5 | 10 dakika |
