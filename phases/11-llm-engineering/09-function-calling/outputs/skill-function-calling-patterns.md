---
name: skill-function-calling-patterns
description: Üretimde fonksiyon çağırma uygulamak için karar çerçevesi -- araç tasarımı, hata işleme, güvenlik ve sağlayıcı kalıpları
version: 1.0.0
phase: 11
lesson: 09
tags: [function-calling, tool-use, agents, mcp, security, openai, anthropic]
---

# Fonksiyon Çağırma Kalıpları

Araçlar kullanan bir LLM uygulaması oluştururken, bu karar çerçevesini uygulayın.

## Fonksiyon Çağırma Ne Zaman Kullanılır

**Fonksiyon çağırmayı şu durumlarda kullanın:**
- Modelin gerçek zamanlı verilere ihtiyacı var (hava durumu, hisse senedi fiyatları, veritabanı sorguları)
- Görev yan etkiler gerektiriyor (e-posta gönderme, kayıt oluşturma, kod dağıtma)
- Model, kullanıcı niyetine dayalı olarak birden fazla eylem arasında seçim yapmalıdır
- Harici sistemlerle etkileşen bir ajan oluşturuyorsunuz

**Bunun yerine yapılandırılmış çıktıları şu durumlarda kullanın:**
- Metinden veri çıkarmanız gerekiyor (harici çağrı gerekmez)
- Çıktı nihai üründür, ara adım değil
- Seçilecek birden fazla araç değil, tek bir şemanız var

**İkisini de şu durumlarda kullanın:**
- Model bir araç çağırır, sonra araç sonucunu belirli bir çıktı formatına yapılandırır

## Araç Tasarım Kılavuzları

1. **Bir araç, bir eylem.** Sorguları, eklemeleri, güncellemeleri ve silmeleri ele alan `manage_database` adlı bir araç çok geniştir. `query_records`, `insert_record`, `update_record` olarak ayırın. Model belirli araçlarla daha iyi seçim yapar.

2. **Açıklamalar prompt'lardır.** Model, seçime karar vermek için araç açıklamalarını okur. Bunları bir junior geliştiriciye talimat yazar gibi yazın. Aracın sadece ne yaptığını değil, ne döndürdüğünü dahil edin.

3. **Enum'larla kısıtlayın.** Bir parametrenin 3-10 geçerli değeri varsa, enum kullanın. Model dizgi uyduracak -- "celsius", "Celsius", "C", "metric" -- siz kısıtlamadıkça.

4. **Daha az araç daha iyidir.** GPT-4o 5-10 aracı iyi işler. 20+ araçta, seçim doğruluğu düşer. 50+ araçta, %10-15 yanlış araç seçimi bekleyin. İlgili işlevselliği gruplayın veya bir yönlendirme katmanı kullanın.

5. **Gerekli, gerçekten gerekli demektir.** Bir parametreyi yalnızca araç onsuz gerçekten çalışamıyorsa gerekli olarak işaretleyin. İyi varsayılanlara sahip isteğe bağlı parametreler araç çağrısı hatalarını azaltır.

## Sağlayıcıya Özgü Kalıplar

### OpenAI (GPT-4o, o3, GPT-4o-mini)

```python
tools=[{"type": "function", "function": {"name": ..., "parameters": ...}}]
tool_choice="auto"       # model karar verir
tool_choice="required"   # en az bir araç çağırmalıdır
tool_choice={"type": "function", "function": {"name": "belirli_arac"}}
```

- Paralel araç çağrılarını destekler (bir yanıtta birden fazla `tool_calls`)
- Araç çağrısı kimlikleri sonuçlarla birlikte geri geçilmelidir
- `gpt-4o-mini` 10x daha ucuzdur ve basit araç yönlendirmesini iyi işler
- Yapılandırılmış çıktı modu, garantili şema uyumu için araç parametreleriyle çalışır

### Anthropic (Claude 3.5 Sonnet, Claude 4 Opus)

```python
tools=[{"name": ..., "description": ..., "input_schema": ...}]
tool_choice={"type": "auto"}     # model karar verir
tool_choice={"type": "any"}      # en az bir araç çağırmalıdır
tool_choice={"type": "tool", "name": "belirli_arac"}
```

- Araç çağrıları `type: "tool_use"` ile içerik blokları olarak görünür
- Sonuçlar `type: "tool_result"` ile kullanıcı mesajlarına gider
- Alan adı `input_schema`'dır, `parameters` değil (yaygın geçiş hatası)
- Yanıt başına birden fazla araç çağrısını destekler

### Google (Gemini 2.0 Flash, Gemini 2.0 Pro)

```python
function_declarations=[{"name": ..., "description": ..., "parameters": ...}]
function_calling_config={"mode": "AUTO"}   # veya "ANY" veya "NONE"
```

- Üst düzeyde `function_declarations` kullanır
- Sonuçlar `function_response` parçaları aracılığıyla döndürülür
- Paralel fonksiyon çağırmayı destekler

### Açık kaynak modeller (Llama 3, Hermes, Qwen)

- Standartlaştırılmış format yok -- modele ve sunma çerçevesine göre değişir
- Hermes formatı (NousResearch) en yaygın ince ayar konvansiyonudur
- vLLM, desteklenen modeller için OpenAI uyumlu araç çağırmayı destekler
- Ollama, uyumlu modellerle temel araç çağırmayı destekler
- Üretimden önce araç seçim doğruluğunu test edin -- açık modeller Berkeley Fonksiyon Çağırma Liderlik Sıralaması'nda GPT-4o'dan %15-30 daha az doğrudur

## Hata İşleme Kalıpları

### Yapılandırılmış hataları döndürün

```json
{"error": true, "message": "'Toky' şehri bulunamadı. 'Tokyo' mu demek istediniz?", "code": "NOT_FOUND", "suggestions": ["Tokyo"]}
```

Eyleme dönüştürülebilir bilgi dahil edin. "Bulunamadı" kötüdür. "Bulunamadı, X mi demek istediniz?" iyidir. Model, kendini düzeltmek için hata mesajlarını kullanır.

### Yeniden deneme stratejisi

1. Araç çağrısı düzeltilebilir bir hatayla başarısız olur (yazım hatası, yanlış enum değeri)
2. Hatayı modele bir araç sonucu olarak gönderin
3. Model ayarlar ve yeniden dener
4. Araç çağrısı başına maksimum 3 yeniden deneme
5. 3 başarısızlıktan sonra, hatayı kullanıcıya döndürün

### Zaman aşımı işleme

Tüm araç yürütmelerinde zaman aşımı ayarlayın. 30 saniye makul bir varsayılandır. Bir araç zaman aşımına uğrarsa, modelin kullanıcıyı bilgilendirebilmesi için yapılandırılmış bir zaman aşımı hatası döndürün, böylece takılı kalmaz.

## Güvenlik Kontrol Listesi

| Kontrol | Neden | Nasıl |
|-------|-----|-----|
| İzin verilen fonksiyonlar listesi | Keyfi kod yürütmeyi önlemek | Yalnızca kullanıcının ihtiyaç duyduğu araçları kaydedin |
| Argüman türlerini doğrulayın | Tür karışıklığı saldırılarını önlemek | Yürütmeden önce türleri kontrol edin |
| Dize argümanlarını temizleyin | Enjeksiyonu önlemek | Özel karakterleri reddedin veya kaçış |
| Veritabanı sorgularını parametreleştirin | SQL enjeksiyonunu önlemek | Model tarafından üretilen SQL'i asla doğrudan geçmeyin |
| Araç sonuçlarını filtreleyin | Veri sızıntısını önlemek | API anahtarlarını, KVK'yı, dahili hataları kaldırın |
| Araç çağrılarını hız sınırlayın | Kontrolden çıkmış döngüleri önlemek | Konuşma başına maksimum 10-20 çağrı |
| Tüm araç çağrılarını günlüğe kaydedin | Denetim izi | Araç adını, argümanları, sonucu, zaman damgasını saklayın |
| Yol geçişini engelleyin | Dosya sistemi erişimini önlemek | Dosya araçlarında `..` ve mutlak yolları reddedin |
| Kod yürütmeyi korumalı alana alın | Sistem erişimini önlemek | Kapsayıcıları veya kısıtlı builtins'leri kullanın |
| Dönüş boyutunu doğrulayın | Bağlam doldurmayı önlemek | 10KB'nin üzerindeki sonuçları kırpın |

## Performans Optimizasyonu

- **Paralel çağrılar:** Model birden fazla bağımsız araç istediğinde, bunları `asyncio.gather()` veya `concurrent.futures` ile eşzamanlı yürütün
- **Önbellekleme:** Aynı oturumda özdeş argümanlar için araç sonuçlarını önbelleğe alın (hava durumu 60 saniyede değişmez)
- **Akış (streaming):** Araç sonuçları getirilirken modelin son yanıtını akışla gönderin
- **Araç budama:** Bağlam sıkışıksa, yalnızca mevcut sorguyla ilgili araç tanımlarını dahil edin (filtreleme için bir sınıflandırıcı kullanın)
- **Yönlendirme için daha küçük modeller:** Araç seçimi için `gpt-4o-mini` veya `claude-3-5-haiku` kullanın, sonra sonuçları sentez için daha güçlü bir modele geçirin

## Yaygın Başarısızlık Kalıpları

| Başarısızlık | Neden | Çözüm |
|---------|-------|-----|
| Yanlış araç seçildi | Belirsiz açıklamalar | Açıklamaları belirli tetikleyici kelimelerle yeniden yazın |
| Eksik gerekli argümanlar | Model bir parametreyi unuttu | Parametre açıklamalarına net örnekler ekleyin |
| Sonsuz araç döngüsü | Model aynı aracı çağırmaya devam ediyor | Maksimum iterasyon (5-10) ayarlayın ve tekrarlanan çağrıları tespit edin |
| Halüsinasyonlu argümanlar | Model makul ama yanlış değerler uyduruyor | Enum'lar kullanın, bilinen değerlere karşı doğrulayın |
| Araç sonucu çok büyük | API 100KB veri döndürdü | Geri beslemeden önce kırpın veya özetleyin |
| Model araç sonucunu yok sayıyor | Sonuç formatı kafa karıştırıcı | Net alan adlarıyla temiz JSON döndürün |
