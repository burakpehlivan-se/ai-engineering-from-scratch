# LLM Yönlendirme Katmanı — LiteLLM, OpenRouter, Portkey

> Sağlayıcı kilidi pahalıdır. Farklı araç çağrısı iş yükleri farklı modellere uyar. Yönlendirme ağ geçitleri tek bir API yüzeyi, yeniden denemeler, yedekleme, maliyet takibi ve korumalar sağlar. 2026'da üç kalıp baskındır: LiteLLM (açık kaynak, kendi barındıran), OpenRouter (yönetilen SaaS), Portkey (üretim düzeyinde, Mart 2026'da açık kaynak). Bu ders karar kriterlerini isimlendirir ve stdlib yönlendirme ağ geçidini yürüyerek gösterir.

**Tür:** Öğren
**Diller:** Python (stdlib, yönlendirme + yedekleme + maliyet takipçisi)
**Ön koşullar:** Faz 13 · 02 (function calling), Faz 13 · 17 (ağ geçitleri)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Kendi barındıran, yönetilen ve üretim düzeyindeki yönlendirme seçeneklerini ayırt et.
- Sağlayıcı başarısızlıklarında öncelik sırasıyla yeniden deneyen bir yedekleme zinciri uygula.
- Sağlayıcılar arasında istek başına maliyet ve token kullanımını takip et.
- Belirli bir üretim kısıtı için LiteLLM, OpenRouter ve Portkey arasında seçim yap.

## Sorun

Sağlayıcı yönlendirmesinin önemli olduğu senaryolar:

1. **Maliyet.** Claude Sonnet, Haiku'nun 3 katına mal olur. Bir sınıflandırma görevi için Haiku yeterli; bir sentez görevi için Sonnet değer. İstek bazında yönlendirin.

2. **Yedekleme.** Bir saat boyunca kötü bir saat dilimi. Her istek başarısız. Anthropic'e otomatik geçiş istiyorsunuz, yeniden dağıtmadan.

3. **Gecikme.** Canlı bir sohbet UI'ı hızlı ilk-token süresi ister. Bir toplu özetleyici istemez. Gecikme SLA'ya göre yönlendirin.

4. **Uyumluluk.** AB kullanıcıları AB bölgelerinde kalmalı. Bölgeye göre yönlendirin.

5. **Deneme.** Aynı iş yükü üzerinde iki modeli A/B test edin. Test kovasına göre yönlendirin.

Her entegrasyon için bunu elle kodlamak tekrarlayıcıdır. Bir yönlendirme ağ geçidi tek bir OpenAI uyumlu API sunar ve geri kalanını ele alır.

## Kavram

### OpenAI uyumlu proxy şekli

Herkes OpenAI-şekli konuşur. Yönlendirme ağ geçidi `/v1/chat/completions` sunar, OpenAI şemasını kabul eder ve dahili olarak Anthropic / Gemini / Cohere / Ollama / herhangi birine proxy yapar. İstemci umursamaz.

### Model takma adları (aliases)

`claude-3-5-sonnet-20251022` yerine, kodunuz `our_smart_model` der. Ağ geçidi takma adları gerçek modellere eşler. Anthropic Claude 4 yayınladığında, takma adı sunucu tarafında değiştirirsiniz; kodunuz dokunulmaz.

### Yedekleme zincirleri

```
birincil: openai/gpt-4o
5xx'te: anthropic/claude-3-5-sonnet
5xx'te: google/gemini-1.5-pro
5xx'te: reddet
```

Ağ geçitleri bunu bir yapılandırmada tanımlar. Yeniden denemeler bir bütçeye karşı sayılır, böylece yedekleme kademeleri maliyeti patlatmaz.

### Anlamsal önbellek (semantic caching)

Birbirinin aynısı veya neredeyse aynısı olan prompt'lar sağlayıcı yerine bir önbelleğe çarpar. Tekrarlayan ajan döngülerinde tasarruf %30 ila %60 olabilir. Anahtarlar embedding tabanlıdır; neredeyse aynısı prompt'lar bir önbellek yuvasını paylaşır.

### Korumalar (Guardrails)

Ağ geçidi düzeyinde:

- **Kişisel Bilgi sansürleme.** Prompt'ları göndermeden önce regex veya ML tabanlı geçiş.
- **Politika ihlalleri.** Yasaklanmış içerik içeren prompt'ları reddet.
- **Çıktı filtreleri.** Sızıntıları tamamlamalardan temizle.

Portkey ve Kong her ikisi de görüş sahibi korumalar sunar. LiteLLM onları isteğe bağlı bırakır.

### Anahtar başına hız sınırları

Bir API anahtarı = bir ekip. Anahtar başına bütçeler, bir ekibin paylaşılan kotasını tüketmesini önler. Çoğu ağ geçidi bunu destekler.

### Kendi barındırma vs yönetilen fedakarlıklar

| Faktör | LiteLLM (kendi barındıran) | OpenRouter (yönetilen) | Portkey (üretim) |
|--------|----------------------|----------------------|----------------------|
| Kod | Açık kaynak, Python | Yönetilen SaaS | Açık kaynak (Mar 2026) + yönetilen |
| Kurulum | Bir proxy dağıtın | Kaydolun | Her ikisi |
| Sağlayıcılar | 100+ | 300+ | 100+ |
| Faturalandırma | Kendi anahtarlarınız | OpenRouter kredileri | Kendi anahtarlarınız |
| Gözlemlenebilirlik | OpenTelemetry | Pano | Tam OTel + Kişisel Bilgi sansürleme |
| En iyi | Tam kontrol isteyen ekipler | Hızlı prototipleme | Uyumlulukla üretim |

LiteLLM, bir SRE ekibiniz varsa ve veri egemenliği istiyorsanız kazanır. OpenRouter, tek bir abonelik ve altyapı istemediğinizde kazanır. Portkey, kutudan çıktığı anda korumalar ve uyumluluk gerektiğinde kazanır.

### Maliyet takibi

Her istek `provider`, `model`, `input_tokens`, `output_tokens` taşır. Model başına token başına fiyatlarla çarpın (ağ geçidinin tuttuğu fiyat sayfasından çekilir). Kullanıcı başına / ekip başına / proje başına toplama.

### MCP artı yönlendirme

Bir ağ geçidi hem LLM çağrılarını hem de MCP örnekleme isteklerini yönlendirebilir. Bir örnekleme isteğinin modelPreferences'ı belirli bir modeli tercih ettiğinde, ağ geçidi doğru arka plana çevirir. Bu, Faz 13 · 17 (MCP ağ geçidi) ile bu dersteki yönlendirme ağ geçidinin bazen tek bir hizmete birleştiği yerdir.

### Yönlendirme stratejileri

- **Statik öncelik.** Listede ilk; hatada yedekle.
- **Yük dengeleme.** Round-robin veya ağırlıklı.
- **Maliyet-farkındalığı.** Gecikme / kaliteyi karşılayan en ucuz modeli seç.
- **Gecikme-farkındalığı.** Son N dakikadaki en hızlı modeli seç.
- **Görev-farkındalığı.** Prompt sınıflandırıcısı kodlamayı bir modele, özetlemeyi diğerine yönlendirir.

## Kullan

`code/main.py`, yaklaşık 150 satırda bir yönlendirme ağ geçidi uygular: OpenAI-şekilli istekleri kabul eder, sağlayıcı başına Stub'lara çevirir, öncelikli bir yedekleme zinciri çalıştırır, istek başına maliyeti takip eder ve girdiler üzerinde Kişisel Bilgi sansürleme geçişi uygular. Üç senaryoyla çalıştırın: normal istek, birincil sağlayıcı kesintisi tetikleyen yedekleme, sansürleme tarafından yakalanan Kişisel Bilgi sızıntısı.

Neye bakılmalı:

- `ROUTES` dict: takma ad -> somut sağlayıcıların öncelik sıralı listesi.
- Yedekleme döngüsü 5xx'te yeniden dener.
- Maliyet takipçisi token kullanımını model başına oranlarla çarpar.
- Kişisel Bilgi sansürü SSN şeklindeki kalıpları iletmeden önce temizler.

## Sun

Bu ders `outputs/skill-routing-config-designer.md` dosyasını üretir. Bir iş yükü profili (gecikme, maliyet, uyumluluk) verildiğinde, beceri LiteLLM / OpenRouter / Portkey seçer ve bir yönlendirme yapılandırması üretir.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. Kesinti senaryosunu tetikleyin; yedeklemenin ikinci sağlayıcıya düştüğünü ve maliyetin doğru şekilde atandığını doğrulayın.

2. Anlamsal önbellekleme ekleyin: prompt'un SHA256'sı bir arama anahtarıdır; önbellek vurmaları anında döner. Tekrarlanan bir çağrıda maliyet tasarrufunu ölçün.

3. "kod ..." prompt'larını zekâya öncelik veren bir takma aday yönlendiren ve "özetle ..." prompt'larını hız öncelikli bir takma adaya yönlendiren bir prompt sınıflandırıcısı ekleyin.

4. Ekip başına bütçeler tasarlayın: her ekibin aylık harcama üst sınırı var; ağ geçidi üst sınıra ulaşıldığında istekleri reddeder. Bir zorlama tane boyutu seçin (istek başına veya pencere tabanlı).

5. LiteLLM, OpenRouter ve Portkey belgelerini yan yana okuyun. Her birinin diğer ikisinin sunmadığı tek özelliği adlandırın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Routing gateway (Yönlendirme ağ geçidi) | "LLM proxy" | Birçok sağlayıcının önünde tek-API-yüzeysel katman |
| OpenAI-compatible | "OpenAI şemasını konuşuyor" | `/v1/chat/completions` shape'ini kabul eder, herhangi bir arka plana çevirir |
| Model alias | "our_smart_model" | Kodunuzdaki ad, ağ geçidi tarafından somut bir modele eşlenir |
| Fallback chain (Yedekleme zinciri) | "Yeniden deneme listesi" | Başarısızlıkta denenmesi gereken sıralı sağlayıcı listesi |
| Semantic caching (Anlamsal önbellek) | "Prompt-embedding önbelleği" | Anahtar, prompt'un embedding'idir; neredeyse aynısı olanlar vurur |
| Guardrails (Korumalar) | "Girdi/çıktı filtreleri" | Kişisel Bilgi'yi sansürle, politika ihlallerini reddet |
| Per-key rate limit (Anahtar başına hız sınırı) | "Ekip bütçesi" | Bir API anahtarıyla sınırlı kota |
| Cost tracking (Maliyet takibi) | "İstek başına harcama" | Token kullanımı x model başına fiyat toplama |
| LiteLLM | "Açık proxy" | Kendi barındırılabilir OSS yönlendirme ağ geçidi |
| OpenRouter | "Yönetilen SaaS" | Kredi tabanlı faturalandırmayla barındırılmış ağ geçidi |
| Portkey | "Üretim seçeneği" | Kutudan çıktığı anda korumalarla açık kaynak + yönetilen |

## İleri Okuma

- [LiteLLM — docs](https://docs.litellm.ai/) — kendi barındırmalı yönlendirme ağ geçidi
- [OpenRouter — quickstart](https://openrouter.ai/docs/quickstart) — yönetilen yönlendirme SaaS'ı
- [Portkey — docs](https://portkey.ai/docs) — korumalarla üretim yönlendirmesi
- [TrueFoundry — LiteLLM vs OpenRouter](https://www.truefoundry.com/blog/litellm-vs-openrouter) — karar kılavuzu
- [Relayplane — LLM gateway comparison 2026](https://relayplane.com/blog/llm-gateway-comparison-2026) — satıcı anketi
