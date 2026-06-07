# LLM'ler için FinOps — Birim Ekonomisi ve Çok-Kiracılı Atıf

> Geleneksel FinOps, LLM harcamasında bozulur. Maliyetler token-işlemleridir, kaynak-çalışma-zamanı değil. Etiketler eşleşmez — bir API çağrısı bir varlık değil, bir işlemdir. Mühendislik kararları (prompt tasarımı, bağlam penceresi, çıktı uzunluğu) finansal kararlardır. 2026 oyun kitabının bir günde işaretlenecek üç atıf boyutu vardır: kullanıcı başına (koltuk fiyatlandırması ve genişleme için `user_id`), görev başına (ürün yüzey maliyeti ve önceliklendirme için `task_id` + `route`), kiracı başına (birim ekonomisi ve yenileme için `tenant_id`). Dört token katmanı — prompt, araç, bellek, yanıt — tek kova harcaması gizler. Çok-kiracılı ürünler için yaptırım merdiveni: kiracı başına hız sınırları (beklenen zirvenin 2-3 katı, net 429 + yeniden dene-sonrası); günlük harcama tavanı (sözleşmeli tavanın 1,5-3 katı; hız sıkılaştırma + uyarı tetikler); harcama z-skoru > 4 üzerinde öldürme anahtarları (otomatik duraklatma + sayfa nöbetçisi). Atıf kalıpları: etiketle-topla, telemetri-birleştirici (en yüksek doğruluk), örnekleme-ve-ekstrapolasyon, model-tabanlı tahsis, olay-kaynaklı, gerçek-zamanlı akan. Birim metrik: maliyet başına çözülen sorgu, maliyet başına üretilen eser — $/M token değil. Geriye dönük etiketleme her zaman ıskalar; istek oluşumunda işaretleyin.

**Tür:** Öğren
**Diller:** Python (stdlib, öldürme anahtarlı basit maliyet-atıf simülatörü)
**Önkoşullar:** Phase 17 · 13 (Gözlemlenebilirlik), Phase 17 · 14 (Önbellekleme)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Geleneksel FinOps'un (etiketler + katmanlar) LLM harcamasında neden bozulduğunu açıklayın ve üç yeni atıf boyutunu sayın.
- Dört token katmanını (prompt, araç, bellek, yanıt) sıralayın ve tek-kova faturalamanın maliyeti neden gizlediğini belirtin.
- Çok-kiracılı bir ürün için bir yaptırım merdiveni (hız → harcama tavanı → öldürme anahtarı) tasarlayın.
- $/M token yerine bir birim metrik (çözülen sorgu / eser başına maliyet) seçin.

## Problem

Faturanız 40.000 $ diyor. Bilmiyorsunuz:
- Hangi kiracı harcadı.
- Hangi ürün özelliği sürdü.
- Herhangi bir bireysel kullanıcı kötüye mi kullandı.
- Suçlu prompt şişmesi, araç çağrıları veya bellek amplifikasyonu muydu.

Sağlayıcı tarafında etiketle-topla, etiketlerin satır öğelerine yayıldığı bulut kaynakları (EC2, S3) için çalışır. LLM API çağrıları otomatik etiketlenmez — kullanıcıyı/görevi/kiracıyı çağrı noktasında damgalamanız (stamp) ve boyunca taşımanız gerekir. Geriye dönük atıf her zaman uç durumları ıskalar.

## Kavram

### Üç atıf boyutu

**Kullanıcı başına** (`user_id`): kim ne kadara mal oluyor. Koltuk fiyatlandırmasını, genişleme konuşmalarını sürer, güçlü kullanıcıları tanımlar.

**Görev başına** (`task_id` + `route`): hangi ürün yüzeyi ne kadara mal oluyor. Özellik önceliklendirmesini, pahalı-özellikleri-öldür kararlarını sürer.

**Kiracı başına** (`tenant_id`): hangi müşteri kârlı. Birim ekonomisini, yenileme fiyatlandırmasını, katman eşiklerini sürer.

Hepsini çağrı noktasında bir günde işaretleyin. Geriye dönük her zaman daha kötü.

### Dört token katmanı

| Katman | Örnek | Toplamın tipik %'si |
|--------|-------|---------------------|
| Prompt | sistem + kullanıcı girişi | %40-60 |
| Araç | geri beslenen araç çağrısı sonuçları | %20-40 (ajan iş yükleri) |
| Bellek | önceki konuşma / alınan dokümanlar | %10-30 |
| Yanıt | model çıktısı | %10-30 |

Dördünü birlikte kovalamak optimizasyonu kör eder. Atıf şemanızda ayırın.

### Yaptırım merdiveni

1. **Hız sınırı** kiracı başına. Beklenen zirvenin 2-3 katı. `Retry-After` ile 429 döndürün. Kiracı sürtünme görür; sürpriz fatura yok.
2. **Günlük harcama tavanı** kiracı başına. Sözleşmeli tavanın 1,5-3 katı. Tetikleyici: hız sınırını sıkılaştır + müşteri başarısını uyar.
3. **Öldürme anahtarı** kiracı taban çizgisine göre harcama z-skoru > 4 üzerinde. Kiracıyı otomatik duraklat; sayfa nöbetçisi; ops + CS'e yükselt.

### Atıf kalıpları

- **Etiketle-topla**: meta veri başlıklarını damgala; sonra topla. Basit; kaba.
- **Telemetri birleştirici**: izleri iz-ID'leri aracılığıyla faturaya birleştir. En yüksek doğruluk. Olgun ekiplerin yaptığı.
- **Örnekleme + ekstrapolasyon**: %5-10 örnekle, çarp. Kaba harcama için maliyet-etkin; kuyrukları ıskalar.
- **Model-tabanlı tahsis**: maliyet sürücüsünü çıkarmak için gerileme. Etiketsiz eski veri için.
- **Olay-kaynaklı**: bir akıştaki (Kafka / Kinesis) maliyet olarak olaylar. Gerçek zamanlı.
- **Gerçek-zamanlı akan**: pano alt-saniye güncellemeleri.

### X başına maliyet birim metriktir

$/M token satıcı konuşmasıdır. Ürün metrikleri:

- Çözülen destek bileti başına maliyet.
- Üretilen makale başına maliyet.
- Başarılı ajan görevi başına maliyet.
- Kullanıcı-oturum-dakikası başına maliyet.

Maliyeti bir ürün sonucuna bağlayın. Aksi takdirde optimizasyon çıpaya bağlı değildir.

### Maliyet atıf izi şekli

```
trace_id: abc123
 user_id: u_42
 tenant_id: t_7
 task_id: task_classify_doc
 route: model_haiku
 layers:
 prompt_tokens: 1800
 tool_tokens: 600
 memory_tokens: 400
 response_tokens: 150
 cost_usd: 0.0135
 cached_input: true
 batch: false
```

#### Açıklama

Bu iz (trace) şekli, tek bir LLM çağrısının maliyet atfı için ne taşıdığını gösterir: `user_id` (kullanıcı), `tenant_id` (kiracı), `task_id` (görev) ve `route` (hangi modelin çalıştırıldığı) boyut etiketleri; `layers` altında dört token katmanı (prompt, tool, memory, response) için ayrı token sayıları; `cost_usd` ile somut maliyet; ayrıca `cached_input` ve `batch` gibi optimizasyon bayrakları.

Her çağrıda yayınla. Veri gölünde sakla. Boyut başına topla. Phase 17 · 13 gözlemlenebilirlik yığını bunun yaşadığı yerdir.

### Birleşik-tasarruf yığını

İstif: önbellek + batch + yönlendirme + ağ geçidi. Dördüyle:

- Önbellek L2 (Phase 17 · 14): ~10 kat ucuz giriş.
- Batch (Phase 17 · 15): %50 indirim.
- Ucuz modele yönlendir (Phase 17 · 16): %60 maliyet azalması.
- Ağ geçidi verimliliği (Phase 17 · 19): artıklık + yeniden denemeler.

En iyi durum istiflenmiş: saf taban çizgisinin ~%5-10'u. Çoğu ekip 2-3 kolu çalıştırır; az hepsini istifler.

### Hatırlamanız gereken sayılar

- Atıf boyutları: kullanıcı, görev, kiracı.
- Dört token katmanı: prompt, araç, bellek, yanıt.
- Öldürme anahtarı: harcama z-skoru > 4.
- Birim metrik: çözülen sorgu başına maliyet, $/M token değil.
- İstiflenmiş optimizasyonlar: taban çizgisinin ~%5-10'u mümkün.

## Kullanım

`code/main.py`, üç katmanlı yaptırım merdiveniyle çok-kiracılı bir LLM servisini simüle eder. Kötüye kullanan bir kiracı enjekte eder ve öldürme anahtarının ateşlenmesini gösterir.

## Yaygınlaştırma

Bu ders `outputs/skill-finops-plan.md` üretir. Ürün ve ölçek verildiğinde, atıf şemasını ve yaptırım merdivenini tasarlar.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Öldürme anahtarı hangi z-skorunda ateşlenir? Eşiği nasıl seçersiniz?
2. Kiracı başına, görev başına bir maliyet panosu tasarlayın. İlk inşa ettiğiniz 5 görünüm nedir?
3. En büyük kiracınız birim-ekonomisi-negatif. Müşteri etkisine göre sıralanmış üç müdahale önerin.
4. Bir destek ürünü için bilet başına maliyeti hesaplayın: bilet başına 3M token, ~800 bilet/gün, GPT-5 önbellekli oran.
5. Geriye dönük etiketlemenin asla işe yarayıp yaramayacağını tartışın. Ne zaman kabul edilebilir?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| Kullanıcı başına atıf | "kullanıcı-düzey maliyet" | Her çağrıda damgalanmış `user_id` |
| Görev başına atıf | "özellik maliyeti" | `task_id` + `route` ürün yüzeyini tanımlar |
| Kiracı başına atıf | "müşteri maliyeti" | `tenant_id`; birim ekonomisini sürer |
| Dört token katmanı | "maliyet katmanları" | prompt + araç + bellek + yanıt |
| Hız sınırı | "429 koruyucu" | Ağ geçidinde uygulanan kiracı başına tavan |
| Günlük harcama tavanı | "günlük tavan" | Uyarıyla kiracı-kapsamlı bütçe |
| Öldürme anahtarı | "otomatik duraklatma" | Harcama z-skoru > 4 otomatik askıya almayı tetikler |
| Çözülen başına maliyet | "ürün birim metriği" | Maliyet token'lara değil ürün sonucuna bağlı |
| Telemetri birleştirici | "izden faturaya" | En yüksek doğruluklu atıf kalıbı |
| İstiflenmiş optimizasyon | "önbellek+batch+yönlendirme+ağ geçidi" | Taban çizgisinin ~%5-10'una birleşik tasarruf |

## Ek Okuma

- [FinOps Foundation — AI için FinOps Genel Bakış](https://www.finops.org/wg/finops-for-ai-overview/)
- [FinOps School — Birim Başına Maliyet 2026 Kılavuzu](https://finopsschool.com/blog/cost-per-unit/)
- [Digital Applied — LLM Ajan Maliyet Atfı 2026](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026)
- [PointFive — Azure OpenAI'da Yönetilen LLM'ler](https://www.pointfive.co/blog/finops-for-ai-economics-of-managed-llms-in-azure-open-ai)
