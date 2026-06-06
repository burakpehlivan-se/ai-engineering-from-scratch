---
name: skill-production-checklist
description: LLM uygulamalarını üretime göndermek için karar çerçevesi -- her bileşeni belirli eşikler ve geç/başarısız kriterleriyle kapsar
version: 1.0.0
phase: 11
lesson: 13
tags: [production, deployment, llm, architecture, scaling, cost, observability, guardrails]
---

# Üretim LLM Kontrol Listesi

Bir LLM uygulamasını gönderirken, bu kontrol listesini sırayla gözden geçirin. Her bölümün belirli eşiklerle geç/başarısız kriterleri vardır.

## 1. Güvenlik (Gönderme Engelleyicileri)

Buradaki her öğe, herhangi bir dağıtımdan önce geçmelidir.

| Kontrol | Geçme Kriteri | Nasıl Doğrulanır |
|-------|--------------|---------------|
| API anahtarları ortam değişkenlerinde | Kod tabanında sıfır sabit kodlanmış anahtar | `grep -r "sk-" --include="*.py"` hiçbir şey döndürmez |
| Girdi guardrail'leri etkin | Prompt enjeksiyon kalıpları engellenmiş | "Tüm önceki talimatları yoksay" gönderin -- engellenen yanıt döner |
| KVK gizleme | TC kimlik, kredi kartı, e-posta kalıpları yakalandı | "TC kimliğim 12345678901" gönderin -- LLM çağrısından önce KVK gizlendi |
| Çıktı filtreleme | Tehlikeli içerik engellendi | Model `DROP TABLE`, `rm -rf`, `exec()` kalıplarını döndüremez |
| Hız sınırlama | Kullanıcı başına istek sınırı uygulandı | Aynı kullanıcıdan 10 saniyede 100 istek -- son 50+ reddedildi |
| Tüm uç noktalarda kimlik doğrulama | Kimliği doğrulanmamış LLM erişimi yok | Token olmadan `curl /v1/chat` 401 döner |
| CORS kısıtlı | Yalnızca üretim alan adlarına izin verilir | `Origin: evil.com` isteği reddedildi |
| Maksimum girdi token'ları | Limitin üzerindeki istekler reddedildi | 50K token girdi gönderin -- 413 veya kırpma döner |

## 2. Güvenilirlik (Birinci Hafta Hayatta Kalma)

Bunlar ilk çağrı üzerindeki olayınızı önler.

| Kontrol | Geçme Kriteri | Nasıl Doğrulanır |
|-------|--------------|---------------|
| Geri çekilmeyle yeniden deneme | 5xx'te 3 yeniden deneme, üstel gecikme | İstek ortasında LLM sahtesini öldürün -- günlüklerde yeniden denemeler görünür |
| Geri dönüş modeli zinciri | Zincirde 2+ model | Birincil model kullanılamaz -- yanıt hâlâ geri dönüşten döner |
| İstek zaman aşımı | Tüm harici çağrılarda maks. 30s | Yavaş LLM sahtesi (60s) -- istek 30s'de zaman aşımına uğrar |
| Kibar bozulma | Önbellek/RAG başarısızlığı hizmeti çökertmez | Önbelleği durdurun -- istekler hâlâ başarılı (daha yavaş, daha pahalı) |
| Sağlık kontrol uç noktası | Bağımlılık durumunu döndürür | `GET /health` `{"status": "healthy", "cache": ..., "llm": ...}` döner |
| Akış (streaming) çalışır | İlk token 500ms altında | İlk-token-zamanı ölçüldü, tutarlı olarak < 500ms |
| Hata mesajları güvenli | Dahili hatalar asla kullanıcıya sızmaz | 500'i zorlayın -- kullanıcı genel hata görür, yığın izi değil |

## 3. Maliyet Kontrolü (Birinci Ay Ekonomisi)

Bunlar 50K dolarlık sürpriz faturanızı önler.

| Kontrol | Geçme Kriteri | Nasıl Doğrulanır |
|-------|--------------|---------------|
| İstek başına maliyet izlendi | Her istek token sayısı + USD maliyetini günlüğe kaydeder | İstek günlüğü `input_tokens`, `output_tokens`, `cost_usd` alanlarına sahip |
| Anlamsal önbellek etkin | Tekrarlanan kalıplarda > %20 isabet oranı | 1000 test isteğinden sonra önbellek istatistikleri isabet oranını gösterir |
| Önbellek TTL'i yapılandırıldı | Girişler süresi doluyor (varsayılan: 1 saat) | Giriş eklendi -- TTL'den sonra döndürülmedi |
| Kullanıcı başına maliyet izleme | Maliyet user_id'ye göre toplandı | Pano/API en çok harcayan ilk 10 kullanıcıyı gösterir |
| Maliyet uyarısı | Günlük bütçenin %80'inde uyarı | $10 günlük bütçe ayarlayın, $8.50 değerinde istek gönderin -- uyarı tetiklenir |
| Maliyete göre model yönlendirme | Düşük karmaşıklıktaki sorgular daha ucuz model kullanır | Basit soru gpt-4o-mini'ye, karmaşık gpt-4o'ya yönlendirilir |
| Maksimum çıktı token'ları ayarlandı | Yanıtlar şablon başına sınırlandı | max_output_tokens=512 ile şablon -- yanıt asla aşmaz |

**Maliyet tahmin formülü:**
```
Aylık LLM maliyeti = DAU x kullanıcı_başına_sorgular x 30 x (1 - önbellek_isabet_oranı) x (ortalama_girdi_token x girdi_fiyatı + ortalama_çıktı_token x çıktı_fiyatı) / 1,000,000
```

**Ölçeğe göre kıyaslama eşikleri:**

| DAU | Hedef maliyet/istek | Aylık bütçe |
|-----|-------------------|----------------|
| 1K | < $0.005 | < $750 |
| 10K | < $0.003 | < $4,500 |
| 100K | < $0.001 | < $15,000 |

## 4. Gözlemlenebilirlik (Üretimde Hata Ayıklama)

Göremediklerinizi düzeltemezsiniz.

| Kontrol | Geçme Kriteri | Nasıl Doğrulanır |
|-------|--------------|---------------|
| Yapılandırılmış JSON günlüğe kaydetme | Her istek bir JSON günlük satırı üretir | Günlük şunları içerir: request_id, user_id, model, tokens, latency_ms, cost |
| İstek izleme | Bileşen zamanlamasıyla uçtan uca iz | Tek istek şunları gösterir: guardrail (5ms) + cache (2ms) + llm (3200ms) + eval (1ms) |
| Gecikme izleme | P50, P95, P99 ölçüldü | 1000 istekten sonra: P50 < 2s, P99 < 10s |
| Hata oranı izleme | Hatalar sayıldı ve kategorize edildi | Pano şunları gösterir: %0.5 API hatası, %0.1 guardrail engelleme, %0.01 zaman aşımı |
| Önbellek metrikleri | İsabet oranı, ıskalama oranı, giriş sayısı görünür | `GET /v1/cache/stats` mevcut sayıları döner |
| A/B test metrikleri | Varyant başına kalite metrikleri günlüğe kaydedildi | Her istek karşılaştırma için prompt_template + versiyonu günlüğe kaydeder |
| Değerlendirme günlüğe kaydetme | Kalite sinyalleri istek başına kaydedildi | Yanıt uzunluğu, gecikme, model, şablon versiyonu çevrimdışı analiz için saklanır |

## 5. Prompt Yönetimi

Prompt'lar koddur. Kod gibi davranın.

| Kontrol | Geçme Kriteri | Nasıl Doğrulanır |
|-------|--------------|---------------|
| Versiyonlanmış şablonlar | Her şablonun bir adı + versiyon dizesi var | Şablon değişikliği yeni versiyon oluşturur, eski versiyon korunur |
| A/B test desteği | Deterministik kullanıcı karmasına göre trafik bölünür | Aynı kullanıcı deney içinde her zaman aynı varyantı görür |
| Geri alma yeteneği | Önceki versiyona < 1 dakika içinde dön | Deney yapılandırmasını değiştirin -- trafik anında kayar |
| Şablon doğrulama | Değişkenler oluşturmadan önce doğrulanır | Şablonda eksik değişken KeyError değil, net hata verir |
| Sistem prompt ayrımı | Sistem ve kullanıcı mesajları ayrı alanlarda | Sistem prompt kullanıcı mesajına birleştirilmiyor |

## 6. Ölçeklendirmeye Hazırlık

Lansmanda gerekli değil. 10x'te gerekli.

| Kontrol | Geçme Kriteri | Nasıl Doğrulanır |
|-------|--------------|---------------|
| Asenkron LLM çağrıları | API çağrılarında iş parçacığı engelleme yok | 50 eşzamanlı istek -- sunucu CPU'su < %30 kalır |
| Bağlantı havuzu | HTTP bağlantıları yeniden kullanıldı | Ağ izi, LLM sağlayıcısına kalıcı bağlantılar gösterir |
| Yatay ölçekleme | Durumsuz sunucu tasarımı | Yük dengeleyicinin arkasında 2 örnek -- tüm istekler başarılı |
| Kuyruk desteği | Gerçek zamanlı olmayan görevler kuyruğa gider | Özetleme isteği job_id döner, sonuç yoklama ile kullanılabilir |
| Yük testi yapıldı | 100 eşzamanlı kullanıcı, < %5 hata oranı | `wrk` veya `locust` testi hedef eşzamanlılıkta geçer |

## Yeni projeler için uygulama sırası

1. **1. Gün:** API sunucusu + prompt şablonları + yeniden denemeli tek LLM çağrısı
2. **2. Gün:** Girdi guardrail'leri + çıktı guardrail'leri + hata işleme
3. **3. Gün:** Anlamsal önbellek + istek başına maliyet izleme
4. **4. Gün:** Akış (SSE) + sağlık kontrol uç noktası
5. **5. Gün:** Yapılandırılmış günlüğe kaydetme + istek izleme + değerlendirme günlüğü
6. **2. Hafta:** A/B testi + prompt versiyonlama + geri alma
7. **3. Hafta:** Geri dönüş modeli zinciri + kibar bozulma
8. **4. Hafta:** Yük testi + asenkron optimizasyon + yatay ölçekleme

## Hızlı tanılama

Üretimde bir şey yanlışsa, şu sırayla kontrol edin:

1. **Kullanıcılar hatalardan şikayet ediyor mu?** Sağlık uç noktasını, sonra günlüklerdeki hata oranını, sonra LLM sağlayıcısı durum sayfasını kontrol edin
2. **Yanıtlar yavaş mı?** P99 gecikmesini, sonra önbellek isabet oranını, sonra izlerdeki LLM yanıt sürelerini kontrol edin
3. **Maliyet artıyor mu?** İstek başına maliyet eğilimini, sonra önbellek isabet oranını, sonra maliyete göre en iyi kullanıcıları, sonra token sayısını artıran prompt şablonu değişikliklerini arayın
4. **Kalite düştü mü?** Yeni bir prompt versiyonunun dağıtılıp dağıtılmadığını, RAG geri getirme doğruluğunun değişip değişmediğini, model sağlayıcısının varsayılan model versiyonunu değiştirip değiştirmediğini kontrol edin
5. **Güvenlik olayı mı?** Guardrail engelleme oranını kontrol edin (ani düşüş = guardrail'ler devre dışı), olağandışı kalıplar için istek günlüklerini kontrol edin, API anahtarlarını hemen döndürün
