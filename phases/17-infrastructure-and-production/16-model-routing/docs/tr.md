# Model Yönlendirme (Routing) — Maliyet Düşürme Primitifi

> Dinamik bir komisyoncu (broker) her isteği değerlendirir (görev türü, token uzunluğu, embedding benzerliği, güven) ve basit sorguları ucuz bir modele, karmaşık olanları sınır (frontier) modele yönlendirir. Model kaskadı (model cascading) olarak da bilinir. Üretim vaka çalışmaları, ABD/BK/AB dağıtımlarında eş kalitede (iso-quality) %20-60 maliyet düşüşü gösteriyor; yüksek hacimli SaaS'te %30 yönlendirme verimliliği iyileşmesi altı haneli yıllık tasarruflara dönüşür. 2026 bağlamı, LLM inference (çıkarım) fiyatlarının yılda ~10 kat düşmesidir — GPT-4 sınıfı bir token, 2022 sonu ile 2026 arasında 20 $/M'den ~0,40 $/M'ye indi. Düşüşün çoğu daha iyi servis yığınlarından (Phase 17 · 04-09) kaynaklanır, donanımdan değil. Yönlendirme, ürün regresyonu olmadan bu fiyat düşüşünü kâr marjına (margin) dönüştürmenin yoludur. Başarısızlık kalıbı ucuz-model sürüklenmesidir (drift): yönlendirme %40'ı daha zayıf bir modele iter, muhakeme görevlerinde kalite %3-5 düşer, kimse bir çeyrek fark etmez. Yönlendirmeleri çevrimdışı değerlendirme setleriyle değil, çevrimiçi kalite metrikleriyle (online quality metrics) yönetin.

**Tür:** Öğren
**Diller:** Python (stdlib, basit kaskad yönlendirici simülatörü)
**Önkoşullar:** Phase 17 · 01 (Yönetilen LLM Platformları), Phase 17 · 19 (AI Ağ Geçitleri)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Model kaskadını açıklayın: güven kontrolüyle ucuz-önce, düşük güvende yükseltme.
- Dört yönlendirme sinyalini (görev sınıflandırması, prompt uzunluğu, bilinen-zor kümeye embedding benzerliği, ilk geçişten öz-güven) sıralayın.
- Hedef yönlendirme bölünmesinde ve kalite kaybı toleransında beklenen birleşik maliyeti hesaplayın.
- Ucuz-model sürüklenmesini yakalayan sürüklenme izleme metriğini (online quality gate) sayın.

## Problem

Servisiniz GPT-5 üzerinde ayda 80.000 dolar harcıyor. Analitiğiniz sorguların %70'inin basit olduğunu gösteriyor: "Paris'te saat kaç?", "bu cümleyi yeniden ifade et." Haiku sınıfı bir model bunları maliyetin %3'ünde mükemmelce hallediyor. %30'u GPT-5'in muhakemesine ihtiyaç duyar — kodlama, matematik, çok adımlı planlama.

%70'i ucuza, %30'u pahalıya yönlendirirseniz, aynı ürün kalitesinde faturanız ~%65 düşer. Bu yönlendirmedir. İnce nokta, kaliteyi düşürmeden komisyoncuyu kurmaktır.

## Kavram

### Dört yönlendirme sinyali

1. **Görev sınıflandırması**: basit/karmaşık/kod üretimi/matematik/sohbet. Kural tabanlı sınıflandırıcı, küçük bir LLM (Haiku sınıfı, 0,25 $/M) veya etiketlenmiş kovalara (bucket) embedding benzerliği olabilir. Çıktı: yol = ucuz / dengeli / sınır.

2. **Prompt uzunluğu**: 4K token'ı aşan prompt'lar tutarlılık için sınır modeli gerektirir. 500 token'ın altındaki prompt'lar genellikle gerektirmez.

3. **Bilinen-zor kümeye embedding benzerliği**: sorgu bilinen-zor kovaya yakınsa (cosine benzerliği > 0,88), doğrudan sınır modeline yükseltin.

4. **İlk geçişten öz-güven**: ucuza gönderin; modelin log-prob'ları (log-olasılıklar — modelin tahmininden ne kadar emin olduğunun ölçüsü) düşük güven gösteriyorsa VEYA reddediyorsa VEYA kaçamak (hedging) dil çıkarıyorsa, sınır modelinde yeniden deneyin. Trafiğin ~%10'unda P95 gecikme ekler ama diğer %90'da %50+ tasarruf sağlar.

### Üç kalıp

**Ön yönlendirme (Pre-route)** (başta sınıflandırıcı): ~5-10 ms gecikme ekler; toplamda en hızlı.

**Kaskad (Cascade)** (ucuz-önce, düşük güvende yükseltme): ~1,2 kat medyan gecikme (ucuz çalıştırma artı doğrulama), yükseltilenlerde ~2 kat. En iyi kalite tabanı.

**Topluluk yönlendirmesi (Ensemble route)** (ucuzu ve sınırı paralel çalıştır, ödül modeli seçsin): en yüksek kalite, en yüksek maliyet; yalnızca kritik A/B için kullanın.

### Uygulama

AI ağ geçitleri (Phase 17 · 19) yönlendirmeyi açar. LiteLLM, yedek düşme ve maliyet yönlendirmesiyle `router` yapılandırmasına sahiptir. Portkey, koruyucular (guards) ve yönlendirme sunar. Kong AI Gateway, eklenti tabanlı yönlendirmeye sahiptir. OpenRouter'ın model pazar yeri bir öneri API'si sunar.

Açık kaynak: RouteLLM (LMSYS), Not Diamond (ticari), Prompt Mule.

### 2026 fiyat eğrisi

| Model sınıfı | 2022 sonu | 2026 | Değişim |
|--------------|-----------|------|---------|
| GPT-4 kalitesi | ~20 $/M | ~0,40 $/M | 50 kat ucuz |
| Sınır (GPT-5, Claude 4) | — | ~3-10 $/M | yeni katman |

İyileşmenin çoğu servis verimliliğidir — Phase 17 · 04-09'daki temel dersler sağlayıcı tarafı maliyet düşüşlerine dönüştü. Yönlendirme, tüm kullanıcılarınız ucuz katmana geçmeden bu kazançları uygulama katmanında yakalamanızı sağlar.

### Sürüklenme asıl risktir

Yönlendirmeniz %40'ı ucuz modele gönderir. Altı ay içinde görev dağılımı kayar (kullanıcılar daha karmaşıklaşır, daha uzun sorular sorar). Yönlendirici fark etmez çünkü sınıflandırıcısı Q1 verisiyle eğitilmiştir. Kalite sessizce düşer. Kimse yeterince yüksek sesle şikayet etmez. Bir rakip kıyaslaması kaybettiğinizde öğrenirsiniz.

Yönlendirmeleri çevrimiçi kalite metrikleriyle yönetin:

- Yol başına kullanıcı başparmak yukarı/aşağı (thumbs-up/down).
- Her yol için ayrılmış %5 örneklemde otomatik LLM-hakemi (judge).
- Yükseltme oranı: kaskad yukarı yönlendirme oranı >%30 ise, ucuz model aşırı yönlendiriliyor.
- Yol başına reddetme oranı.

### Hatırlamanız gereken sayılar

- 2026 yönlendirme tasarrufu, eş kalitede: vaka çalışmalarında %20-60.
- LLM fiyat düşüşü 2022-2026: yıllık toplam ~10 kat.
- GPT-4 kalitesi 2022 vs 2026: ~20 $/M → ~0,40 $/M.
- Kaskad gecikme etkisi: ~1,2 kat medyan, yükseltilenlerde ~2 kat (trafiğin ~%10'u).

## Kullanım

`code/main.py`, karma bir iş yükünde ön yönlendirme, kaskad ve topluluğu simüle eder. Birleşik maliyeti, kalite kaybını ve yükseltme oranını raporlar.

## Yaygınlaştırma

Bu ders `outputs/skill-router-plan.md` üretir. İş yükü ve kalite bütçesi verildiğinde, bir yönlendirme kalıbı ve sinyalleri seçer.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Hangi doğruluk tabanında kaskad, ön yönlendirmeyi geçer?
2. Kullanıcı tabanınız %30 kurumsal (karmaşık sorgular), %70 ücretsiz katman (basit). Yönlendirme bölünmesini tasarlayın. Çevrimiçi metriği ne yönetir?
3. Bir yönlendirme kaliteyi %2 düşürür ama %40 tasarruf sağlar. Yayınlanır mı? Ürüne bağlıdır — iki tarafı da savunun.
4. OpenAI / Anthropic API'lerinden logprob'ları kullanarak bir güven kontrolü uygulayın. Başlangıç eşiği (threshold) nedir?
5. Altı ayda yükseltme oranı %8'den %22'ye çıkıyor. Üç neden ve her birinin çözümünü tanımlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| Model yönlendirme | "maliyet komisyoncusu" | İstek başına dinamik model seçimi |
| Model kaskadı | "ucuz-önce yükseltme" | Ucuzu çalıştır, düşük güvende sınıra geç |
| Ön yönlendirme | "önce sınıflandır" | Başta sınıflandırıcı; yeniden çalıştırma yok |
| Topluluk yönlendirmesi | "paralel seçim" | Birden çok çalıştır, ödül modeli en iyisini seçer |
| Yükseltme oranı | "yukarı yönlendirilen %" | Kaskad isteklerinin yükseltilen kesri |
| RouteLLM | "LMSYS yönlendirici" | OSS yönlendirici kitaplığı |
| Not Diamond | "ticari yönlendirici" | SaaS model yönlendirme ürünü |
| Sürüklenme | "ucuz sürüklenmesi" | Yönlendiricinin fark etmediği dağılım kayması |
| Online quality gate | "canlı kontrol" | Canlı trafiği örnekleyen otomatik LLM-hakemi |

## Ek Okuma

- [AbhyashSuchi — Model Routing LLM 2026 En İyi Uygulamaları](https://abhyashsuchi.in/model-routing-llm-2026-best-practices/)
- [Lukas Brunner — Inference Optimizasyonunun Yükselişi 2026](https://dev.to/lukas_brunner/the-rise-of-inference-optimization-the-real-llm-infra-trend-shaping-2026-4e4o)
- [RouteLLM makalesi / kodu](https://github.com/lm-sys/RouteLLM)
- [Not Diamond — model yönlendirme](https://www.notdiamond.ai/)
- [OpenRouter](https://openrouter.ai/) — yönlendirme temelleri olan çok modelli ağ geçidi.
