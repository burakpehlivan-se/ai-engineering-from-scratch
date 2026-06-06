# Batch API'ler — %50 İndirim Endüstri Standardı Olarak

> Her büyük sağlayıcı (provider), %50 indirim ve ~24 saatlik teslim süresi sunan asenkron (asynchronous) bir batch API sunar. OpenAI, Anthropic, Google ve çoğu inference platformu (Fireworks batch tier, Together batch) aynı kalıbı uygular. Batch'i prompt caching (ön bellekleme) ile istifleyerek (stack) gece pipeline'ları senkronize-önbelleksiz maliyetin (synchronous-uncached) yaklaşık %10'una düşer. Kural acımasızca basittir: etkileşimli değilse, batch'te çalışmalıdır. İçerik üretim pipeline'ları, doküman sınıflandırma, veri çıkarma, rapor üretimi, toplu etiketleme, katalog etiketleme — 24 saatlik gecikmeyi (latency) tolere eden her iş, batch'e taşınmadığı sürece masada para bırakıyor demektir. 2026 üretim kalıbı, her yeni LLM iş yükünü (workload) üç şeride ayırır: etkileşimli (önbelleklemeli senkron), yarı-etkileşimli (yedek düşmeli asenkron kuyruk), batch (gece, önbellekli giriş istifli). Etkileşimli gibi davranıp dakikalarca gecikmeyi tolere eden iş yükleri çoğunlukla israf eder.

**Tür:** Öğren
**Diller:** Python (stdlib, basit batch-vs-sync maliyet simülatörü)
**Önkoşullar:** Phase 17 · 14 (Prompt ve Semantik Önbellekleme)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Üç sağlayıcı batch API'sini (OpenAI, Anthropic, Google) ve ortak %50 indirim + 24 saat teslim garantilerini sayın.
- Gece sınıflandırma iş yükünde batch + önbellekli giriş istifinin maliyetini hesaplayın ve senkronize-önbelleksiz taban çizgisiyle (baseline) karşılaştırın.
- Bir iş yükünü etkileşimli / yarı-etkileşimli / batch olarak sınıflandırın ve seçimi gerekçelendirin.
- İki tuzağı sayın: kısmi etkileşimlilik (kullanıcı 24 saatten hızlı bekler) ve çıktı şeması kayması (batch dosya formatı sağlayıcıya göre değişir).

## Problem

Ekibiniz her gece bir rapor üretim pipeline'ı çalıştırıyor. 50.000 doküman, her birini özetle, özetleri kümelendir, yönetici özeti taslağı çıkar. Senkron çalıştırmak 4 saat sürüyor ve gecelik maliyet 2.000 dolar. Siz batch API'lerini duyuyorsunuz.

Batch size %50 indirim getirir. Ayrıca sistem prompt'unda (system prompt) prompt caching'i etkinleştirirsiniz (50.000 çağrının tümünde paylaşılır). İkisini istifleyince fatura gecelik 180 dolara düşer — taban çizgisinin ~%9'u. Aynı pipeline, üç yapılandırma değişikliği.

Batch, kimsenin çekmediği en ucuz LLM maliyet koludur. Sebep çoğunlukla örgütseldir: ekipler "gerçek zamanlı" diye düşünür, oysa SLA (Hizmet Düzeyi Anlaşması) aslında "sabah olmadan" şeklindedir. Bu ders, faturanın %90'ını masada bırakmamakla ilgilidir.

## Kavram

### Üç batch API'si

**OpenAI Batch API**: JSONL dosya yüklemesi, istek listesi içerir. 24 saat teslim süresi vaat edilir (pratikte genelde ~2-8 saat). Giriş ve çıkış token'larında (token — modelin işlediği metin birimi) %50 indirim. `/v1/batches` uç noktası. Önbelleğe uygun girişler, üzerine önbellekli giriş fiyatlandırması alır.

**Anthropic Message Batches**: JSONL yüklemesi. 24 saat teslim süresi. %50 indirim. `cache_control`'ü destekler — önbellek yazımları açıktır, okumalar batch içinde otomatik gerçekleşir.

**Google Vertex AI Batch Prediction**: BigQuery veya GCS girişi. Gemini için benzer %50 indirim. Vertex pipeline'larıyla bütünleşir.

### Anlamsal ayrım: asenkron, yavaş değil

Batch, "24 saat içinde döneceğime söz veriyorum" demektir — "bu 24 saat sürecek" değil. Tipik P50 (medyan gecikme) 2-6 saattir. Sağlayıcı, GPU envanteri (GPU inventory) az kullanıldığında, yoğun olmayan zaman dilimlerinde batch'inizi zamanlar.

### Önbellekleme ile istifle

Aynı 4K token'lık sistem prompt'una sahip 50K dokümanlık bir özetleme:

- Senkronize önbelleksiz: 50000 × (giriş × 4000 + çıkış × 200) tam fiyattan.
- Senkronize önbellekli: sistem prompt ilk yazımdan sonra önbelleğe alınır; kalan 49999 için giriş 10 kat ucuzlar.
- Batch önbellekli: yukarıdakilerin hepsi + okuma ve yazma üzerine %50 indirim.

İstif: batch + cache = senkronize önbelleksiz faturanın ~%10'u. Gece çalışan ve paylaşılan sistem prompt'una sahip her iş yükü bunu kullanmalıdır.

### İş yükü sınıflandırması

**Etkileşimli (Interactive)** — kullanıcı yanıtı bekler. TTFT (İlk Token'a Kadar Geçen Süre, Time To First Token) önemlidir. Prompt caching ile senkron çağrı. Batch yapılamaz.

**Yarı-etkileşimli (Semi-interactive)** — kullanıcı görev gönderir, dakikalar içinde kontrol eder. Batch kullanılamıyorsa sync'e düşen asenkron kuyruk. Orta hacimli RAG (Retrieval-Augmented Generation — getirilmiş içerikle zenginleştirilmiş üretim) indekslemeyi düşünün.

**Batch** — kullanıcı sonuçları "sabah olunca" veya "bir saat içinde" bekler. İçerik pipeline'ları, ölçekli sınıflandırma, çevrimdışı analiz. Her zaman batch, her zaman önbellek istifli.

Yaygın hata: pipeline üretimde olduğu için her şeyi etkileşimli sınıflandırmak. Üretim bir gecikme özelliği değil — SLA öyledir.

### Kısmi etkileşimlilik tuzağı

Bazı özellikler etkileşimli görünür ama 5-10 dakikayı tolere eder. Örnek: "yenile" düğmesi olan gecelik müşteri sağlık raporu. Kullanıcı yenile'ye tıklar; 10 dakika beklemek sorun değil. Ekip bunu senkron olarak sunar. 50 eşzamanlı yenileme, batch'lenip e-postayla teslim edilenden 10 kat pahalıya mal olur.

Sormanız gereken soru: "Bu kullanıcı için 24 saat ne anlama gelir?" Cevap "fark etmez" ise, batch'leyin.

### Çıktı şeması tuzağı

Batch dosya formatları sağlayıcıya göre değişir:

- OpenAI: JSONL, satır başına bir istek.
- Anthropic: JSONL, satır başına bir mesaj; yanıt formatı gömülü.
- Vertex: BigQuery tablosu veya TFRecord'lı GCS öneki.

Sağlayıcılar arasında "tek bir batch istemcisi" yazmak, sağlayıcı başına adaptör kodu demektir. Çok sağlayıcılı batch reklamı yapan ağ geçitleri (Portkey, LiteLLM'nin bazı katmanları) hâlâ ham formatı ince bir sarmalayıcıyla (wrapper) sarar.

### Hatırlamanız gereken sayılar

- Sağlayıcılar arası batch indirimi: giriş + çıkış üzerine düz %50.
- Teslim SLA'sı: 24 saat garantili, 2-6 saat tipik P50.
- İstiflenmiş batch + önbellekli giriş: senkronize önbelleksiz maliyetin ~%10'u.
- İş yükü sınıflandırma kuralı: 24 saatlik gecikme kabul edilebilirse, her zaman batch.

## Kullanım

`code/main.py`, 50K dokümanlık bir iş yükü için senkron, senkron+önbellek, batch ve batch+önbellek maliyetlerini hesaplar. Tasarrufu $ ve yüzde olarak raporlar.

## Yaygınlaştırma

Bu ders `outputs/skill-batch-triager.md` üretir. İş yükü özelliklerini verilen sınıflandırmayı etkileşimli/yarı/batch yapar ve tasarrufu tahmin eder.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. 3K token sistem prompt'u ve 500 token çıkışı olan 100K dokümanlık bir pipeline için tam istifin (batch + cache) senkron taban çizgisine göre tasarrufunu hesaplayın.
2. Bildiğiniz gerçek bir üründe üç özellik seçin. Her birini etkileşimli/yarı/batch olarak sınıflandırın.
3. Bir kullanıcı raporunun 3 saat sürdüğünden şikayet ediyor. Bu bir batch yanlış sınıflandırması mı, meşru etkileşimli mi? Karar ölçütünü yazın.
4. Batch API'niz 24 saat döndürme SLA'sı veriyor ama P99 (en yavaş %1'inci dilim) 20 saat. Bunu kullanıcıya nasıl iletirsiniz — uç durumda aşağı akış sisteminin davranışı nedir?
5. Başabaş noktasını (break-even) hesaplayın: paylaşılan önek (shared prefix) hangi uzunlukta batch + cache, kendi ayırdığınız (reserved) GPU üzerinde gece çalıştırmaktan ucuz olur?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| Batch API | "asenkron indirim" | 24 saat teslim süresiyle %50 indirim |
| JSONL | "batch formatı" | Satır başına bir JSON isteği; OpenAI/Anthropic standardı |
| Message Batches | "Anthropic batch" | Anthropic'in batch API ürün adı |
| Batch prediction | "Vertex batch" | Vertex AI'ın batch API ürünü |
| Teslim SLA'sı | "24 saat sözü" | Garanti, tipik değil; tipik olan 2-6 saat |
| İş yükü sınıflandırması | "etkileşimlilik kararı" | Etkileşimli / yarı / batch yönlendirme kararı |
| Çıktı şeması | "yanıt formatı" | Sağlayıcıya göre JSONL düzeni; taşınabilir değil |
| İstiflenmiş indirim | "batch + cache" | İkisi birden geçerliyken önbelleksiz senkron faturanın ~%10'u |

## Ek Okuma

- [OpenAI Batch API](https://platform.openai.com/docs/guides/batch) — JSONL formatı ve `/v1/batches` semantiği.
- [Anthropic Message Batches](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing) — batch formatı ve `cache_control` etkileşimi.
- [Vertex AI Batch Prediction](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/batch-prediction) — Gemini batch semantiği.
- [Finout — OpenAI vs Anthropic API Fiyatlandırması 2026](https://www.finout.io/blog/openai-vs-anthropic-api-pricing-comparison)
- [Zen Van Riel — LLM API Maliyet Karşılaştırması 2026](https://zenvanriel.com/ai-engineer-blog/llm-api-cost-comparison-2026/)
