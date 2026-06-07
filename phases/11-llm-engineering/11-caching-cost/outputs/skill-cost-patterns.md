---
name: skill-cost-patterns
description: LLM maliyet optimizasyonu için karar çerçevesi -- önbellekleme stratejileri, hız sınırlama, model yönlendirme ve bütçe kontrolleri
version: 1.0.0
phase: 11
lesson: 11
tags: [caching, cost-optimization, rate-limiting, model-routing, budget, llm-ops]
---

# LLM Maliyet Optimizasyon Kalıpları

Maliyetleri kontrol etmesi gereken bir LLM uygulaması oluştururken şu karar çerçevesini uygulayın.

## Ne zaman optimize edin

**Şu durumlarda hemen optimize edin:**
- Aylık LLM harcaması $500'ü veya altyapı bütçesinin %10'unu aşıyor
- Tüketici ürünü için sorgu başına maliyet $0.01'in üzerinde
- Sistem prompt'unuz 1.000 token'in üzerinde ve her istekle gönderiliyor
- Sorguların %30'undan fazlası kopya veya yakın kopya
- 100'den 10.000+ günlük kullanıcıya ölçekleniyorsunuz

**Şu durumlarda henüz optimize etmeyin:**
- 100'den az DAU'nuz var ve hâlâ ürün-pazar uyumunu doğruluyorsunuz
- Aylık harcama $100'ün altında ve yavaş büyüyor
- Hâlâ prompt tasarımı üzerinde yineleme yapıyorsunuz (önbellekleme sizi bir prompt'a kilitler)

## Önbellekleme stratejisi seçimi

### Tam önbellekleme

**Şu durumlarda kullanın:** sıcaklık=0, özdeş prompt'lar tekrarlanıyor, deterministik çıktılar gerekli.

```python
key = sha256(json.dumps({"model": m, "messages": msgs, "temp": 0}))
```

- Uygulama: 30 dakika
- İsabet oranı: Çoğu uygulama için %10-25, SSS botları için %40-60
- Gecikme: <1ms (sözlük araması)
- Risk: Alttaki veri değişirse yanıtlar eskimiş olur

**Şu durumlarda atlayın:** sıcaklık > 0, her sorgu benzersiz, gerçek zamanlı veri gerekli.

### Anlamsal önbellekleme

**Şu durumlarda kullanın:** kullanıcılar aynı soruyu farklı kelimelerle soruyor, SSS-ağırlıklı ürünler, müşteri desteği.

- Uygulama: 2-4 saat (gömme + benzerlik + depolama)
- İsabet oranı: Tam önbelleğin üzerine %15-35
- Gecikme: 10-50ms (gömme + ANN arama)
- Risk: Yanlış pozitifler (benzer ama farklı bir soru için yanlış önbelleğe alınmış cevap döndürme)

**Eşik kılavuzları:**
- 0.98+: çok muhafazakâr, neredeyse hiç yanlış pozitif yok, daha düşük isabet oranı
- 0.95: olgusal S/C için iyi denge
- 0.90: agresif, daha yüksek isabet oranı ancak yanlış cevap riski
- 0.85: yalnızca düşük riskli uygulamalar için (öneriler, otomatik tamamlama)

**Şu durumlarda atlayın:** her sorgunun benzersiz bağlamı var (kod üretimi), yanıtlar en son verileri yansıtmalı, sorgu alanı sınırsız.

### Sağlayıcı prompt önbelleği

**Şu durumlarda kullanın:** sistem prompt > 1.024 token (OpenAI) veya modele özgü minimum, aynı önek (prefix) tekrarlı olarak gönderiliyor.

| Sağlayıcı | Eylem | Tasarruf |
|----------|--------|---------|
| Anthropic | Sistem mesajına `cache_control: {"type": "ephemeral"}` ekleyin | Önbelleğe alınmış önek üzerinde %90 (%25 yazma primi sonrası) |
| OpenAI | Hiçbir şey (otomatik) | Önbelleğe alınmış önek üzerinde %50 |
| Google | Açık TTL ile Bağlam Önbelleği API'sini kullanın | Önbelleğe alınmış bağlam üzerinde ~%75 |

**Şu durumlarda atlayın:** sistem prompt istek başına değişiyor, prompt minimum uzunluğun altında.

## Model yönlendirme kuralları

### Anahtar kelime tabanlı (basit, hızlı)

```
basit: <= 5 kelime VEYA SSS anahtar kelimeleriyle eşleşir -> gpt-4o-mini ($0.15/$0.60)
orta: genel sorgular, özetler -> claude-sonnet ($3/$15)
karmaşık: "analiz et", "karşılaştır", "hata ayıkla" -> gpt-4o ($2.50/$10)
```

- Uygulama: 1 saat
- Doğruluk: %70-80
- Tasarruf: Model maliyetlerinin %40-60'ı

### Gömmeye dayalı (daha doğru)

Kategori başına 50-100 etiketlenmiş sorgu gömün. Yeni sorguları en yakın komşuya göre sınıflandırın.

- Uygulama: 4-8 saat
- Doğruluk: %85-92
- Tasarruf: Model maliyetlerinin %50-70'si
- Ek maliyet: Sınıflandırma gömme vektörleri için ~$0.02/1M token (ihmal edilebilir)

### Makine öğrenmesi tabanlı (üretim kalitesi)

Tarihsel sorgu/model çiftleri üzerinde küçük bir sınıflandırıcı (lojistik regresyon veya küçük BERT) eğitin.

- Uygulama: 1-2 hafta
- Doğruluk: %90-95
- Tasarruf: Model maliyetlerinin %60-75'i
- Gerektirir: Üretim trafiğinden etiketlenmiş eğitim verisi

## Hız sınırlama yapılandırması

### Kademeye göre token kovası parametreleri

| Kademe | Kova Boyutu | Dolum Hızı | Maks. RPM | Günlük Sınır |
|------|-------------|-------------|---------|-----------|
| Ücretsiz | 50K token | 500/sn | 10 | 50K |
| Pro | 500K token | 5K/sn | 60 | 500K |
| Kurumsal | 5M token | 50K/sn | 300 | 5M |

### Uygulama kontrol listesi

1. Çok örnekli uygulamalar için kovaları Redis'te (bellek içi değil) saklayın
2. Yarış koşullarını önlemek için atomik işlemler (MULTI/EXEC) kullanın
3. Reddetme yanıtlarıyla birlikte `Retry-After` başlığını döndürün
4. Reddedilen istekleri bir metrik olarak izleyin (>%5 reddetme = kademe limitleri çok sıkı)
5. Kibar bozulma (graceful degradation) uygulayın: önce pahalı model isteklerini reddedin, ucuz model erişimini koruyun

## Bütçe kontrolleri

### Üç eşikli devre kesici

| Eşik | Eylem | Geri alınabilir |
|-----------|--------|------------|
| Aylık bütçenin %70'i | Uyarıyı günlüğe kaydedin, ekibi Slack/PagerDuty üzerinden uyarın | Evet (otomatik) |
| Aylık bütçenin %85'i | Tüm trafiği en ucuz modele yönlendirin | Evet (otomatik, sonraki fatura döngüsü) |
| Aylık bütçenin %95'i | Yalnızca önbelleğe alınmış yanıtlar sunun, yeni LLM çağrılarını reddedin | Evet (manuel sıfırlama veya sonraki döngü) |

### Kullanıcı başına maliyet izleme

Kullanıcı başına kümülatif maliyeti izleyin. Medyanın 10 katını aşan kullanıcıları işaretleyin. Yaygın nedenler:
- Meşru güçlü kullanıcı (kademelerini yükseltin)
- Prompt enjeksiyonu döngüsü (bot otomatik istekler gönderiyor)
- Verimsiz entegrasyon (istemci her hatada yeniden deniyor)

## Maliyet izleme alanları

Her API çağrısını şu alanlarla günlüğe kaydedin:

```json
{
 "timestamp": "2026-04-02T10:30:00Z",
 "model": "gpt-4o",
 "input_tokens": 1523,
 "output_tokens": 487,
 "cached_input_tokens": 1024,
 "latency_ms": 1847,
 "cost_usd": 0.006142,
 "user_id": "user_abc123",
 "cache_status": "partial_hit",
 "request_category": "customer_support",
 "complexity_class": "medium",
 "routed_from": "gpt-4o"
}
```

### Panoda (dashboard) gösterilecek anahtar metrikler

- **Sorgu başına maliyet** (P50, P95, P99) -- modele, özelliğe, kullanıcı kademesine göre
- **Önbellek isabet oranı** -- tam ve anlamsal, zaman içindeki eğilim
- **Model dağılımı** -- modele göre trafik yüzdesi, model başına maliyet
- **Bütçe yanma hızı** -- mevcut harcama, mevcut hızda projekte edilen aylığa karşı
- **Reddetme oranı** -- hız sınırı alan isteklerin yüzdesi, kademeye göre

## Yaygın hatalar

| Hata | Neden zarar verir | Çözüm |
|---------|-------------|-----|
| Sıcaklık > 0 ile önbellekleme | Deterministik olmayan çıktılar, eski önbellek yanlış çeşitlilik verir | Yalnızca sıcaklık=0 çağrılarını önbelleğe alın veya önbelleğe alınmış yanıtların rastgeleliği kaybettiğini kabul edin |
| Anlamsal önbellek eşiği çok düşük | Yüzeysel olarak benzer sorgular için yanlış cevaplar döndürür | 0.95'ten başlayın, yalnızca yanlış pozitif oranını ölçtükten sonra düşürün |
| Önbellek geçersiz kılma yok | Alttaki veriler değiştiğinde yanıtlar eskir | TTL ayarlayın (dinamik veri için 1 saat, statik için 24 saat), veri güncellemelerinde geçersiz kılın |
| Tüm trafiği en ucuz modele yönlendirme | Kalite düşer, kullanıcılar fark eder | Karmaşıklığa göre yönlendirin, kademe başına kaliteyi ölçün, minimum kalite eşikleri belirleyin |
| Kullanıcı başına limit yok | Tek bir kötüye kullanan kullanıcı tüm bütçeyi yakar | Her zaman, cömert olsa bile, kullanıcı başına kotalar uygulayın |
| Çıktı token'larını yok sayma | Çıktı, token başına girdiden 2-5 kat daha pahalıdır | `max_tokens`'ı uygun şekilde ayarlayın, durdurma dizilerini (stop sequences) kullanın, çıktıları sıkıştırın |
| Prompt kararlı olmadan önbellekleme | Önbellek eski prompt'lardan gelen yanıtlarla dolar | Yalnızca prompt kesinleştikten sonra önbelleği etkinleştirin, prompt değişikliklerinde önbelleği boşaltın |

## Fiyat referansı (Nisan 2026 itibarıyla)

| Model | Girdi ($/1M) | Çıktı ($/1M) | Önbelleğe Alınmış Girdi ($/1M) | En İyisi |
|-------|-------------|--------------|--------------------|---------|
| gpt-4.1-nano | $0.10 | $0.40 | $0.025 | Yüksek hacimli basit görevler |
| gpt-4o-mini | $0.15 | $0.60 | $0.075 | Basit yönlendirme, sınıflandırma |
| gemini-2.5-flash | $0.15 | $0.60 | $0.0375 | Bütçeye uygun multimodal |
| claude-haiku-3.5 | $0.80 | $4.00 | $0.08 | Hızlı orta kademe görevler |
| o4-mini | $1.10 | $4.40 | $0.275 | Bütçeye uygun akıl yürütme |
| gemini-2.5-pro | $1.25 | $10.00 | $0.3125 | Uzun bağlam, multimodal |
| gpt-4o | $2.50 | $10.00 | $1.25 | Genel amaçlı, fonksiyon çağırma |
| claude-sonnet-4 | $3.00 | $15.00 | $0.30 | Dengeli kalite/maliyet |
| claude-opus-4 | $15.00 | $75.00 | $1.50 | Maksimum kalite, karmaşık akıl yürütme |
