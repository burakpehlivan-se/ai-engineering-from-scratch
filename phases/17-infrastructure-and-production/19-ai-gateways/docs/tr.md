# AI Ağ Geçitleri (Gateways) — LiteLLM, Portkey, Kong AI Gateway, Bifrost

> Bir ağ geçidi, uygulamalarınız ile model sağlayıcıları arasında oturur. Temel özellikler sağlayıcı yönlendirmesi, yedek düşme, yeniden denemeler, hız sınırlama, gizli referanslar, gözlemlenebilirlik ve koruyuculardır (guardrails). 2026'da pazar bölünmesi: **LiteLLM**, MIT lisanslı açık kaynak yazılımdır (OSS), 100+ sağlayıcı, OpenAI uyumlu, ancak ~2000 RPS (Saniyedeki İstek Sayısı) civarında bozulur (8 GB bellek, yayınlanmış kıyaslamalarda kademeli arızalar); Python, <500 RPS, dev/prototipler için en iyisi. **Portkey**, kontrol düzlemi konumlandırması (koruyucular, PII (Kişisel Tanımlayıcı Bilgi) sansürleme, jailbreak algılama, denetim izleri), Mart 2026'da Apache 2.0 açık kaynak oldu, istek başına 20-40 ms gecikme ek yükü, aylık 49 $ üretim katmanı. **Kong AI Gateway**, Kong Gateway üzerine kurulu — Kong'un aynı 12 CPU üzerindeki kendi kıyaslaması: Portkey'den %228, LiteLLM'den %859 daha hızlı; ayda model başına 100 $ fiyatlandırma (Plus katmanında maks 5); zaten Kong'daysanız kurumsal uygun. **Bifrost** (Maxim AI) — yapılandırılabilir geri çekilmeyle (backoff) otomatik yeniden denemeler, OpenAI 429'da Anthropic'e yedek düşme. **Cloudflare / Vercel AI Gateways** — yönetilen, sıfır operasyon, temel yeniden deneme. Veri yerleşimi (data residency) kendi-kurulum kararını yönlendirir; Portkey ve Kong OSS + isteğe bağlı yönetilen ile ortada oturur.

**Tür:** Öğren
**Diller:** Python (stdlib, basit ağ geçidi-yönlendirme simülatörü)
**Önkoşullar:** Phase 17 · 01 (Yönetilen LLM Platformları), Phase 17 · 16 (Model Yönlendirme)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Altı temel ağ geçidi özelliğini (yönlendirme, yedek, yeniden deneme, hız sınırları, gizli anahtarlar, gözlemlenebilirlik, koruyucular) sıralayın.
- Dört 2026 ağ geçidini (LiteLLM, Portkey, Kong AI, Bifrost) ölçek tavanlarına ve kullanım durumlarına eşleyin.
- Kong kıyaslamasını (Portkey'e %228, LiteLLM'e %859) alıntılayın ve >500 RPS için neden önemli olduğunu açıklayın.
- Veri yerleşimi ve operasyon bütçesi verildiğinde kendi-kurulum vs yönetilen seçin.

## Problem

Ürününüz OpenAI, Anthropic ve kendi-kurulu Llama'yı çağırıyor. Her sağlayıcının farklı SDK'sı, hata modeli, hız sınırı ve yetkilendirme şeması var. Yük devretme (OpenAI 429'ladığında Anthropic'i dene), tek kimlik bilgisi deposu, birleşik gözlemlenebilirlik ve kiracı başına hız sınırları istiyorsunuz.

Bunu uygulama katmanında yeniden icat etmek, her servisi her sağlayıcıya bağlar. Bir ağ geçidi katmanı, sağlayıcılara yelpaze şeklinde yayan tek bir API'ye (genellikle OpenAI uyumlu) sahip tek bir süreçte toplar.

## Kavram

### Altı temel özellik

1. **Sağlayıcı yönlendirmesi** — OpenAI, Anthropic, Gemini, kendi-kurulu vb. tek bir API'nin arkasında.
2. **Yedek düşme** — 429, 5xx veya kalite arızasında başka yerde yeniden deneme.
3. **Yeniden denemeler** — üstel geri çekilme, sınırlı denemeler.
4. **Hız sınırları** — kiracı, anahtar ve model başına.
5. **Gizli referanslar** — kimlik bilgilerini çalışma zamanında kasadan çekin (uygulamada asla).
6. **Gözlemlenebilirlik** — OTel + GenAI öznitelikleri (Phase 17 · 13) + maliyet atfı.
7. **Koruyucular** — PII sansürleme, jailbreak algılama, izin verilen-konu filtreleri.

### LiteLLM — MIT OSS, Python

- 100+ sağlayıcı, OpenAI uyumlu, yönlendirici yapılandırması, yedek düşme, temel gözlemlenebilirlik.
- Kong'un kıyaslamasında ~2000 RPS'te bozulur; 8 GB bellek ayakizi, sürekli yük altında kademeli arızalar.
- En uygun: Python uygulaması, <500 RPS, dev/staging ağ geçitleri, deneysel yönlendirme.
- Maliyet: OSS için 0 $; bulut ücretsiz katman var.

### Portkey — kontrol düzlemi konumlandırması

- Mart 2026 itibarıyla Apache 2.0 OSS. Koruyucular, PII sansürleme, jailbreak algılama, denetim izleri.
- İstek başına 20-40 ms gecikme ek yükü.
- Saklama + SLA ile üretim katmanı için ayda 49 $.
- En uygun: koruyucular + gözlemlenebilirlik paketine ihtiyaç duyan düzenlenmiş endüstriler.

### Kong AI Gateway — ölçek oyuncusu

- Kong Gateway (olgun API ağ geçidi ürünü, lua+OpenResty) üzerine kurulu.
- Kong'un 12-CPU eşdeğeri üzerindeki kendi kıyaslaması: Portkey'den %228, LiteLLM'den %859 daha hızlı.
- Fiyatlandırma: ayda model başına 100 $, Plus katmanında maks 5.
- En uygun: zaten Kong'da; >1000 RPS; lisanslamaya istekli.

### Bifrost (Maxim AI)

- Yapılandırılabilir geri çekilmeyle otomatik yeniden denemeler.
- OpenAI 429'da Anthropic'e yedek düşme kanonik bir tarif.
- Daha yeni katılımcı; ticari.

### Cloudflare AI Gateway / Vercel AI Gateway

- Yönetilen, sıfır operasyon. Temel yeniden deneme ve gözlemlenebilirlik.
- En uygun: Cloudflare/Vercel üzerinde kenarda sunulan JavaScript uygulamaları.
- Koruyucular ve hız sınırları konusunda Kong/Portkey ile karşılaştırıldığında sınırlı.

### Kendi-kurulum vs yönetilen

Veri yerleşimi zorlayıcı işlevdir. Sağlık ve finans varsayılan olarak kendi-kurulumdur (LiteLLM veya Portkey OSS veya Kong). Tüketici ürünleri varsayılan olarak yönetilen (Cloudflare AI Gateway) veya orta katman (Portkey yönetilen) kullanır. Karma: düzenlenmiş kiracı için kendi-kurulum, diğerleri için yönetilen.

### Gecikme bütçesi

- LiteLLM: tipik 5-15 ms ek yük.
- Portkey: 20-40 ms ek yük.
- Kong: 3-8 ms ek yük.
- Cloudflare/Vercel: 1-3 ms ek yük (kenar avantajı).

Ağ geçidi gecikmesi doğrudan TTFT'ye eklenir. TTFT P99 < 100 ms SLA için, Kong veya Cloudflare. P99 < 500 ms için, herhangi biri.

### Hız sınırı semantiği önemlidir

Basit token-kovası (token-bucket) orta ölçeğe kadar çalışır. Çok-kiracılı, kayan pencere (sliding-window) + patlama ödeneği + kiracı başına katmanlama gerektirir. LiteLLM token-kovası gönderir; Kong kayan pencere gönderir; Portkey katmanlı gönderir.

### Ağ geçidi + gözlemlenebilirlik + yönlendirme birleşir

Phase 17 · 13 (gözlemlenebilirlik) + 16 (model yönlendirme) + 19 (ağ geçitleri) üretimde aynı katmandır. Üçünü birden kapsayan bir araç seçin veya dikkatlice bağlayın: çoğu 2026 dağıtımı, bölünmüş roller için Helicone (gözlemlenebilirlik) veya Portkey (koruyucular) ile Kong (ölçek)'u birleştirir.

### Hatırlamanız gereken sayılar

- LiteLLM: ~2000 RPS'te bozulur, 8 GB bellek.
- Portkey: 20-40 ms ek yük; Mart 2026'dan beri Apache 2.0.
- Kong: Portkey'den %228, LiteLLM'den %859 daha hızlı.
- Kong fiyatlandırması: ayda model başına 100 $, Plus'ta maks 5.
- Cloudflare/Vercel: kenarda 1-3 ms ek yük.

## Kullanım

`code/main.py`, 429/5xx enjeksiyonu altında 3 sağlayıcıda yedek düşmeyle ağ geçidi yönlendirmesini simüle eder. Gecikme, yeniden deneme oranı ve yedek isabet oranını raporlar.

## Yaygınlaştırma

Bu ders `outputs/skill-gateway-picker.md` üretir. Ölçek, operasyon duruşu, uyumluluk ve gecikme bütçesi verildiğinde bir ağ geçidi seçer.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. OpenAI→Anthropic→kendi-kurulum yedek düşmesini yapılandırın. %5 sağlayıcı hata oranında beklenen isabet oranı nedir?
2. SLA'nız 300 ms taban çizgisi üzerinde TTFT P99 < 200 ms. Hangi ağ geçitleri bütçe içinde kalır?
3. Bir sağlık müşterisi kendi-kurulum + PII sansürleme + denetim gerektiriyor. Portkey OSS veya Kong seçin.
4. LiteLLM vs Kong karşılaştırması: bir ekip hangi RPS tavanında göç etmelidir?
5. Çok-kiracılı bir SaaS için hız sınırı politikası tasarlayın: ücretsiz katman, deneme katmanı, ücretli katman. Token-kovası mı kayan pencere mi?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| Ağ geçidi | "API komisyoncusu" | Uygulamalar ile sağlayıcılar arasında oturan süreç |
| LiteLLM | "MIT olanı" | Python OSS, 100+ sağlayıcı, 2K RPS'te bozulur |
| Portkey | "koruyucu ağ geçidi" | Kontrol düzlemi + gözlemlenebilirlik, Apache 2.0 |
| Kong AI Gateway | "ölçek olanı" | Kong Gateway üzerine kurulu, kıyaslama lideri |
| Bifrost | "Maxim'in ağ geçidi" | Yeniden denemeler + Anthropic yedek tarifi |
| Cloudflare AI Gateway | "kenar yönetilen" | Kenara dağıtılmış yönetilen ağ geçidi, sıfır operasyon |
| PII sansürleme | "veri temizleme" | Modele göndermeden önce regex + NER maskesi |
| Jailbreak algılama | "prompt enjeksiyon koruyucusu" | Kullanıcı girişinde sınıflandırıcı |
| Denetim izi | "düzenlenmiş günlük" | Her LLM çağrısının değişmez kaydı |
| Token-kovası | "basit hız sınırı" | Yeniden doldurma tabanlı hız sınırlayıcı |
| Kayan pencere | "hassas hız sınırı" | Zaman pencereli hız sınırlayıcı; daha iyi adalet |

## Ek Okuma

- [Kong AI Gateway Kıyaslaması](https://konghq.com/blog/engineering/ai-gateway-benchmark-kong-ai-gateway-portkey-litellm)
- [TrueFoundry — AI Ağ Geçitleri 2026 Karşılaştırması](https://www.truefoundry.com/blog/a-definitive-guide-to-ai-gateways-in-2026-competitive-landscape-comparison)
- [Techsy — En İyi LLM Ağ Geçidi Araçları 2026](https://techsy.io/en/blog/best-llm-gateway-tools)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- [Portkey GitHub](https://github.com/Portkey-AI/gateway)
- [Kong AI Gateway docs](https://docs.konghq.com/gateway/latest/ai-gateway/)
