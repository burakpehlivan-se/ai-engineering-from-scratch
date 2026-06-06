# Inference Platform Ekonomisi — Fireworks, Together, Baseten, Modal, Replicate, Anyscale

> 2026 inference pazarı artık GPU süresi kiralaması değil. Üçe ayrılır: özel silikon (Groq, Cerebras, SambaNova), GPU platformları (Baseten, Together, Fireworks, Modal) ve API-öncelikli pazar yerleri (Replicate, DeepInfra). Fireworks, fiyatı 1 Mayıs 2026'da GPU başına 1$/saat artırdı ve 4 milyar dolar değerleme ile günde 10T+ token işleyerek hacim-temelli modelin işlediğini gösterdi. Baseten, Ocak 2026'da 5 milyar dolar değerlemede 300 milyon dolarlık Seri E turunu kapattı. Rekabet konumlandırma kuralı basit: Fireworks gecikmeyi optimize eder, Together katalog genişliğini, Baseten kurumsal kaliteyi, Modal Python-yerel geliştirici deneyimini, Replicate multimodal erişimi, Anyscale dağıtık Python'ı optimize eder. Bu ders size bir kurucuya verebileceğiniz bir matris sunar.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak çağrı başına ekonomi karşılaştırıcısı)
**Önkoşullar:** Faz 17 · 01 (Yönetilen LLM Platformları), Faz 17 · 04 (vLLM Serving Internals)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Üç pazar segmentini (özel silikon, GPU platformları, API-öncelikli) adlandırın ve her satıcıyı bir segmente eşleyin.
- "Token başına" API fiyatlandırma modelinin neden serving motorunun maliyet eğrisine doğru sıkıştığını, donanımınkine değil, açıklayın.
- En az üç satıcıda etkin çağrı başına maliyeti hesaplayın ve dakika başına (Baseten, Modal) ücretin token başına ücreti ne zaman yendiğini açıklayın.
- Belirli bir iş yükü için hangi platformun doğru varsayılan olduğunu belirleyin (sunucusuz ani yük, sabit yüksek verim, ince ayarlı varyantlar, multimodal).

## Sorun

Yönetilen hiper ölçekleyici platformlarını değerlendirdiniz. Daha dar, daha hızlı bir sağlayıcıya ihtiyacınız olduğuna karar verdiniz — gecikme için Fireworks, genişlik için Together, ince ayarlı özel model için Baseten. Şimdi altı gerçek seçeneğiniz var ve fiyatlandırma sayfaları uyuşmuyor. Fireworks $/M token gösterir; Baseten $/dakika; Modal $/saniye; Replicate $/tahmin. İş yükünü modelleden bunları başa baş karşılaştıramazsınız.

Daha kötüsü, her fiyatlandırma sayfasının arkasındaki iş modeli farklıdır. Fireworks kendi özel motorunu (FireAttention) paylaşılan GPU'larda çalıştırır; token başına oran, kendi kullanım eğrisini yansıtır. Baseten size Truss + ayrılmış GPU'lar verir; dakika başına ücretlendirme münhasırlığı yansıtır. Modal gerçek Python sunucusuz — saniye başına faturalandırma, saniye altı cold start (soğuk başlatma) ile. Aynı çıktı (bir LLM yanıtı), üç farklı maliyet fonksiyonu.

Bu ders altısını modeller ve her birinin ne zaman kazandığını söyler.

## Kavram

### Üç segment

**Özel silikon** — Groq (LPU), Cerebras (WSE), SambaNova (RDU). Tipik olarak aynı modelde GPU-temelli kümeye göre 5-10x daha hızlı decode. Token başına daha yüksek fiyat (Groq Llama-70B'de 2025 sonunda ~$0,99/M idi) ancak gecikmeye duyarlı kullanım durumları için yenilmez. Groq, sesli agentlar ve gerçek zamanlı çeviri için üretim tercihidir.

**GPU platformları** — Baseten, Together, Fireworks, Modal, Anyscale. NVIDIA (H100, H200, 2026'da B200) veya bazen AMD üzerinde çalışır. "Ham GPU kiralama" (RunPod, Lambda) ile "hiper ölçekleyici yönetilen servis" (Bedrock) arasındaki ekonomik katman.

**API-öncelikli pazar yerleri** — Replicate, DeepInfra, OpenRouter, Fal. Geniş katalog, tahmin başına veya saniye başına ödeme, ilk çağrıya kadar geçen süreye (time-to-first-call) vurgu yapar.

### Fireworks — gecikme optimize edilmiş GPU platformu

- FireAttention motoru (özel); eşdeğer konfigürasyonlarda vLLM'den 4x daha düşük gecikme olarak pazarlanır.
- Etkileşimli olmayan iş yükleri için batch katmanı, sunucusuz oranın yaklaşık %50'si.
- İnce ayarlı model, temel modelle aynı oranda sunulur — LoRA'nız için prim ücretlendiren sağlayıcılara karşı gerçek bir farklılaştırıcı.
- 2026 ortası: 1 Mayıs 2026'dan itibaren geçerli olmak üzere on-demand GPU kirasını saatte 1$ artırdı. Ölçekte hacim fiyatlandırması pazarlığa açık.
- Finansal sinyal: 4 milyar dolar değerleme, günde 10T+ token işleniyor.

### Together — genişlik optimize edilmiş

- Yukarı akış yayınından günler içinde 200+ model, açık kaynak sürümler dahil.
- Eşdeğer LLM modellerinde Replicate'ten %50-70 daha ucuz — "AI Native Cloud" konumlandırması hacim ve katalogtur.
- Tek bir API'de inference, ince ayar ve eğitim.

### Baseten — kurumsal kalite optimize edilmiş

- Truss çerçevesi: bağımlılıklar, sırlar, serving konfigürasyonu tek bir manifest'te model paketleme.
- GPU aralığı T4'ten B200'e kadar. Makul cold-start azaltma ile dakika başına faturalandırma.
- SOC 2 Type II, HIPAA-hazır. Yaygın fintech ve sağlık tercihi.
- 5 milyar dolar değerleme, Ocak 2026 Seri E (CapitalG, IVP, NVIDIA'dan 300 milyon dolar).

### Modal — Python-yerel optimize edilmiş

- Saf Python'da altyapı-kod olarak. Bir fonksiyonu `@modal.function(gpu="A100")` ile dekore edin ve tek bir komutla dağıtın.
- Saniye başına faturalandırma. Ön ısıtma ile cold start'lar 2-4s; küçük modeller için <1s.
- 1,1 milyar dolar değerlemede 87 milyon dolarlık Seri B (2025). Bağımsız anketlerde en güçlü geliştirici deneyimi puanı.

### Replicate — multimodal genişlik

- Tahmin başına ödeme. Görüntü, video ve ses modelleri için varsayılan platform.
- Entegrasyon ekosistemi (Zapier, Vercel, CMS eklentileri).
- LLM token başına oranlarda daha az rekabetçi ama multimodal çeşitlilikte kazanıyor.

### Anyscale — Ray-yerel

- Ray üzerine kurulu; RayTurbo, Anyscale'ın tescilli inference motorudur (vLLM ile rekabet eder).
- Inference adımının daha büyük bir graf üzerinde tek bir düğüm olduğu dağıtık Python iş yükleri için en iyisi.
- Yönetilen Ray kümeleri; Ray AIR ve Ray Serve ile sıkı entegrasyon.

### Token başına ve dakika başına — hangisi ne zaman kazanır

Token başına, iş yükü gecikmeye duyarsız ve ani yüklü (bursty) olduğunda mantıklıdır — yalnızca kullandığınız için ödeme yaparsınız. Dakika başına, kullanım yüksek ve öngörülebilir olduğunda mantıklıdır — GPU'yu doyurmaya başladığınızda token başına ücreti yenersiniz.

Kaba kural: ayrılmış bir GPU'nun sürekli kullanımının ~%30'unun üzerindeki iş yükleri için dakika başına (Baseten, Modal) token başına (Fireworks, Together)'i yenmeye başlar. Altında, boş için ödeme yapmaktan kaçındığınız için token başına kazanır.

### Özel motor gerçek settir

vLLM ve SGLang üzerindeki her platform özel bir motor iddia eder. FireAttention, RayTurbo, Baseten'in inference yığını. Özel motor iddiaları pazarlamayı gölgeler — dürüst çerçeveleme, vLLM + SGLang'nin açık kaynak inference'ın yaklaşık %80'ini temsil ettiğidir ve platform katmanındaki farklılaştırıcılar DX, atıf ve SLA'lardır.

### Hatırlamanız gereken sayılar

- Fireworks GPU kirası: 1 Mayıs 2026'dan itibaren geçerli 1$/saat artış.
- Fireworks iddiası: eşdeğer konfigürasyonlarda vLLM'den 4x daha düşük gecikme.
- Together: LLM'lerde Replicate'ten %50-70 daha ucuz.
- Baseten değerlemesi: 5 milyar dolar (Seri E, Ocak 2026, 300 milyon dolarlık tur).
- Modal değerlemesi: 1,1 milyar dolar (Seri B, 2025).
- Dakika başına, token başına'yı sürekli kullanımın ~%30 üzerinde yener.

## Kullan

`code/main.py`, altı satıcıyı sentetik bir iş yükü üzerinde fiyatlandırma modellerinde karşılaştırır. $/gün ve etkin $/M token raporlar. Token başına ve dakika başına arasındaki başabaş noktasını bulmak için çalıştırın.

## Üret

Bu ders `outputs/skill-inference-platform-picker.md` üretir. İş yükü profili, SLA ve bütçe verildiğinde, birincil inference platformunu seçer ve ikinciyi adlandırır.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. 70B modeli tek bir H100'de, hangi sürekli kullanım oranında Baseten (dakika başına) Fireworks'u (token başına) yener? Çapraz noktayı kendiniz türetin ve kural parmak kuralıyla karşılaştırın.
2. Ürününüz görüntü oluşturma artı sohbet artı konuşmadan-metne hizmet veriyor. Her modalite için platform seçin ve onları birleştiren ağ geçidi örüntüsünü adlandırın.
3. Fireworks, birincil modelinizde fiyatları saatte 1$ artırıyor. Trafiğinizin %40'ı batch katmanına (%50 indirimli) taşınırsa, birleşik maliyet etkisini modelleyin.
4. Düzenlenmiş bir müşteri SOC 2 Type II + HIPAA + ayrılmış GPU'lar gerektiriyor. Hangi üç platform uygulanabilir ve hangisi FinOps'ta kazanıyor?
5. Fireworks sunucusuz, Together on-demand, Baseten ayrılmış ve Replicate API üzerinde Llama 3.1 70B için 1.000 tahmin başına maliyeti karşılaştırın. 10 tahmin/gün'de hangisi en ucuz? 10.000'de?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| Özel silikon | "GPU olmayan çipler" | Groq LPU, Cerebras WSE, SambaNova RDU — decode için optimize edilmiş |
| FireAttention | "Fireworks motoru" | Özel attention çekirdeği; vLLM'den 4x daha düşük gecikme olarak pazarlanıyor |
| Truss | "Baseten'in formatı" | Model paketleme manifest'i; bağımlılıklar + sırlar + serving konfigürasyonu |
| Token başına | "API fiyatlandırması" | Tüketilen tokenlara göre ücret; boş için ödeme yok |
| Dakika başına | "ayrılmış fiyatlandırma" | Duvar saati GPU süresine göre ücret; yüksek kullanımda kazanır |
| Tahmin başına | "Replicate fiyatlandırması" | Model çağrısı başına ücret; görüntü/video için yaygın |
| RayTurbo | "Anyscale motoru" | Ray üzerinde tescilli inference; Ray kümelerinde vLLM ile rekabet eder |
| Batch katmanı | "%50 indirim" | Azaltılmış oranda etkileşimli olmayan kuyruk; Fireworks, OpenAI'de yaygın |
| Temel oranda ince ayar | "Fireworks LoRA" | LoRA-sunulan istekleri temel model oranında ücretlendir (farklılaştırıcı) |

## İleri Okuma

- [Fireworks Pricing](https://fireworks.ai/pricing) — token başına oranlar, batch katmanı, GPU kirası.
- [Baseten Pricing](https://www.baseten.co/pricing/) — dakika başına oranlar, taahhütlü kapasite, kurumsal katmanlar.
- [Modal Pricing](https://modal.com/pricing) — saniye başına GPU oranları ve ücretsiz katman.
- [Together AI Pricing](https://www.together.ai/pricing) — model kataloğu ve token başına oranlar.
- [Anyscale Pricing](https://www.anyscale.com/pricing) — RayTurbo ve yönetilen Ray fiyatlandırması.
- [Northflank — Fireworks AI Alternatives](https://northflank.com/blog/7-best-fireworks-ai-alternatives-for-inference) — karşılaştırmalı değerlendirme.
- [Infrabase — AI Inference API Providers 2026](https://infrabase.ai/blog/ai-inference-api-providers-compared) — satıcı manzarası.
