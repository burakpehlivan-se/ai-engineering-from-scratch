# Generative Models (Generatif Modeller) — Sınıflandırma ve Tarih

> Her görüntü metni, metin modeli, video modeli ve 3D modeli beş kategoriden birine girer. Yanlış kategoriyi seçerseniz haftalarca matematikle savaşırız. Doğru olanı seçerseniz, alanın son on iki yıldaki ilerlemesi kafanızda tertipli bir şekilde istiflenir.

**Tür:** Öğrenme
**Diller:** Python
**Önkoşullar:** Faz 2 (ML Temelleri), Faz 3 (Derin Öğrenme Çekirdeği), Faz 7 · 14 (Transformer'lar)
**Süre:** ~45 dakika

## Problem

Bir generatif model tek bir iş yapar: bilinmeyen bir dağılımdan `p_data(x)` örnekleriyle eğitilmiş verilerden, aynı dağılımdan gelmiş gibi görünen yeni örnekler üretir. Yüzler, cümleler, MIDI dosyaları, protein yapıları — hepsi aynı problemdir eğer biraz dikkatli bakarsanız.

Sorun şu ki `p_data`, milyonlarca boyuta sahip bir uzayda yaşıyor (512x512 RGB bir görüntü yaklaşık 786k boyut), örnekler bu uzayın içindeki ince bir manifoldun üzerinde oturuyor ve belki 10 milyon örneğiniz var. Yoğunluğu kaba kuvvetle çözmek umutsuzdur. Her generatif model, zor bir problemi biraz daha az zor bir problemle değiştiren bir uzlaşıdır.

Son on iki yılda beş aile hayatta kaldı. Her ailenin hangi uzlaşıyı yaptığını bilmek, neden bazı görevlerde başarılı olduğunu ve diğerlerinde çöktüğünü açıklar.

## Kavram

![Generatif modellerin beş ailesi — neyi modellediklerine göre sınıflandırma](../assets/taxonomy.svg)

**1. Açık density (density), tractable (işlenebilir).** `log p(x)` ifadesini gerçekten değerlendirebileceğiniz bir toplam olarak yazın. Autoregressive modeller (PixelCNN, WaveNet, GPT) `p(x) = ∏ p(x_i | x_<i)` olarak çarpanlara ayrır. Normalizing flows (RealNVP, Glow) `p(x)` ifadesini basit bir tabanın invertible dönüşümü olarak oluşturur. Artı: kesin likelihood, temiz eğitim kaybı. Eksi: autoregressive inference sıralıdır (uzun diziler için yavaştır), flows invertible mimarilere ihtiyaç duyar (mimari olarak kısıtlayıcı).

**2. Açık density, yaklaşık.** `log p(x)` ifadesinden aşağısını sınırlayın (ELBO) ve sınırı optimize edin. VAE'ler (Kingma 2013) encoder-decoder ile birlikte bir variational posterior kullanır. Diffusion modelleri (DDPM, Ho 2020) ağırlıklı bir ELBO'yu dolaylı olarak optimize eden bir denoiser eğitir. Diffusion, 2026'da görüntü, video ve 3D için baskın omurga haline gelmiştir.

**3. İmajiner density (density).** Yoğunluğu tamamen atlayın; örnekler üreten bir generator `G(z)` ve gerçek ile sahtekarı ayıran bir discriminator `D(x)` öğrenin. GAN'lar (Goodfellow 2014). Inference'ta hızlıdır (tek bir forward pass) ama eğitim sırasında istikrarsızdır. StyleGAN 1/2/3, sabit-alan fotogerçekçilik için (yüzler, yatak odaları) 2026'da hala en iyi durumdaki teknoloji olmaya devam ediyor.

**4. Skor tabanlı / sürekli zaman.** Log yoğunluğunun gradyanını `∇_x log p(x)` (skor) doğrudan öğrenin. Song & Ermon (2019), skor eşleştirmenin diffusion'ı bir SDE'ye genelleştirdiğini gösterdi. Flow matching (Lipman 2023) 2024-2026'nın yükselen yıldızıdır: simülasyon gerektirmeyen eğitim, daha düz yollar, DDPM'den 4-10x daha hızlı örnek alma. Stable Diffusion 3, Flux, AudioCraft 2 hepsi flow matching kullanır.

**5. Token tabanlı autoregressive discrete kodlar üzerinde.** Yüksek boyutlu veriyi bir VQ-VAE veya residual quantizer ile kısa bir discrete token dizisine sıkıştırın, ardından token dizisini modellemek için bir Transformer kullanın. Parti, MuseNet, AudioLM, VALL-E, Sora'nın patch tokenizer'ı hepsi bunu kullanır. Bu, birinci kategoriye öğretilmiş bir tokenizer'ın eklenmesidir.

## Kısa bir tarihçe

| Yıl | Model | Neden önemliydi |
|------|-------|-----------------|
| 2013 | VAE (Kingma) | Kullanılabilir eğitim kaybına sahip ilk derin generatif model. |
| 2014 | GAN (Goodfellow) | İmajiner density, likelihood yok — çarpıcı keskin örnekler. |
| 2015 | DRAW, PixelCNN | Sıralı görüntü üretimi. |
| 2017 | Glow, RealNVP | Invertible flows; derinlikle kesin likelihood. |
| 2017 | Progressive GAN | İlk megapiksel yüzler. |
| 2019 | StyleGAN / StyleGAN2 | O alan için hala geçilmesi zor olan fotogerçekçi yüzler. |
| 2020 | DDPM (Ho) | Diffusion pratik hale geldi. |
| 2021 | CLIP, DALL-E 1, VQGAN | Metinden görsele geçiş ana akım haline geldi. |
| 2022 | Imagen, Stable Diffusion 1, DALL-E 2 | Latent diffusion + metin koşullandırması = meta. |
| 2022 | ControlNet, LoRA | Öğrenilmiş diffusion üzerinde hassas kontrol. |
| 2023 | SDXL, Midjourney v5, Flow matching | Ölçek + daha iyi dinamikler. |
| 2024 | Sora, Stable Diffusion 3, Flux.1 | Video diffusion; flow matching kazandı. |
| 2025 | Veo 2, Kling 1.5, Runway Gen-3, Nano Banana | Üretim kalitesinde video. |
| 2026 | Consistency + Rectified Flow | Diffusion omurgalarından tek adımlı örnek alma. |

## Beş soruluk triyaj

Yeni bir generatif model makalesi çıktığında, yöntem bölümünü okumadan önce bu beş soruyu yanıtlayın.

1. **Ne modelleniyor?** Pikseller, latent'ler, discrete token'lar, 3D Gaussian'lar, mesh'ler, dalga formları?
2. **Density açık mı yoksa imajiner mi?** `log p(x)` ifadesi yazılıyor mu?
3. **Örnek alma: tek atışlı mı yoksa iteratif mi?** Iteratif daha yavaş inference demektir; tek atışlı genellikle adversarial veya distile edilmiş demektir.
4. **Koşullandırma: koşulsuz, sınıf, metin, görüntü, duruş?** Bu, kaybı ve mimari iskeleti belirler.
5. **Değerlendirme: FID, CLIP score, IS, insan tercihi, görev doğruluğu?** Her birinin bilinen hata modları vardır (Ders 14'e bakın).

Bu beş soruyu bu fazın her dersinde tekrar yanıtlayacaksınız. Sonunda refleks haline gelecekler.

## Kodu Oluştur

Bu dersin kodu hafif bir görselleştirme: örnekleme yöntemleriyle (kernel yoğunluk tahmini, diskret histogram ve en yakın örnekle "GAN benzeri" bir üretici) tek boyutlu bir Gaussian karışımını uygulamalı olarak göstereceksiniz, böylece açık vs imajiner density arasındaki farkı tek ekranda yazdırabileceğiniz bir problemde görebilirsiniz.

`code/main.py` dosyasını çalıştırın. İki modlu bir Gaussian karışımından 2000 örnek çizer ve şöyle yazdırır:

```
explicit density (histogram): p(x in [-0.5, 0.5]) ≈ 0.38
approximate density (KDE):     p(x in [-0.5, 0.5]) ≈ 0.41
implicit (nearest-sample gen): 20 new samples printed, no p(x)
```

Fark edin: ilk ikisi size "bu nokta ne kadar olası?" diye sormanızı sağlar. Üçüncüsü bunu yapamaz. Bu, gelecek her ders için önemli olacak *açık vs imajiner* ayrımıdır.

## Kullan

Hangi aile, hangi görev için, 2026'da?

| Görev | En iyi aile | Neden |
|------|-------------|-----|
| Fotogerçekçi yüzler, dar alan | StyleGAN 2/3 | Hala en keskin, en hızlı inference. |
| Genel metinden görsele | Latent diffusion + flow matching | SD3, Flux.1, DALL-E 3. |
| Hızlı metinden görsele | Rectified flow + distilasyon | SDXL-Turbo, SD3-Turbo, LCM. |
| Metinden videoya | Diffusion Transformer + flow matching | Sora, Veo 2, Kling. |
| Konuşma + müzik | Token tabanlı AR (AudioLM, VALL-E, MusicGen) veya flow matching (AudioCraft 2) | Discrete token'lar ucuza ölçeklenir. |
| 3D sahneler | Gaussian Splatting uydurma, diffusion prior | 3D-GS yeniden oluşturma için, diffusion yeni-görüş için. |
| Yoğunluk tahmini (örnek alma yok) | Flows | Kesin `log p(x)` sunabilen tek aile. |
| Simülasyon / fizik | Flow matching, score SDE | Düz çizgili yollar, yumuşak vektör alanları. |

## Sun

`outputs/skill-model-chooser.md` olarak kaydedin.

Bu beceri bir görev açıklaması alır ve şunları çıktı olarak verir: (1) hangi aile kullanılacağı, (2) üç açık ve üç barındırılan seçeneğin sıralı listesi, (3) dikkat edilmesi olası hata modu ve (4) hesaplama/zaman bütçesi.

## Alıştırmalar

1. **Kolay.** Bu beş ürünün her biri için aileyi ve omurgayı belirleyin: ChatGPT image, Midjourney v7, Sora, Runway Gen-3, ElevenLabs. Kanıt kamuoyuna açık teknik raporlardan olmalıdır.
2. **Orta.** Yarın okuyacağınız makale diffusion'dan 100x daha hızlı örnek alma iddiasında bulunuyor. Hızlanmanın koşullandırma ve yüksek çözünürlükte nasıl ayakta kaldığını kontrol etmek için üç soru yazın.
3. **Zor.** Önemsediğiniz bir alanı seçin (örn. protein yapısı, CAD, moleküller, yörünge). Bu alanın mevcut SOTA modeli için beş soruluk triyajı yanıtlayın ve daha iyi bir modelin neleri değiştireceğini taslak olarak çizin.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|------|-----------------|-----------------------|
| Generative model (Generatif model) | "Yeni bir şeyler yapıyor" | `p_data(x)` için bir örnekleyici öğrenir, isteğe bağlı olarak `log p(x)` sunar. |
| Explicit density (Açık density) | "Değerlendirebilirsiniz" | Model kapalı formda veya işlenebilir bir `log p(x)` sağlar. |
| Implicit density (İmajiner density) | "GAN tarzı" | Sadece bir örnekleyici — verilen bir noktanın `p(x)` değerini değerlendirme yolu yoktur. |
| ELBO | "Evidence lower bound" | `log p(x)` üzerinde işlenebilir bir alt sınır; VAE'ler ve diffusion bunu optimize eder. |
| Score (Skor) | "Log yoğunluğunun gradyanı" | `∇_x log p(x)`; diffusion ve SDE modelleri bu alanı öğrenir. |
| Manifold hipotezi | "Veri bir yüzey üzerinde yaşıyor" | Yüksek boyutlu veri düşük boyutlu bir manifold üzerinde yoğunlaşır; boyut azaltmanın neden işe yaradığı budur. |
| Autoregressive (Otomatik geriye dönük) | "Bir sonraki parçayı tahmin et" | Ortak dağılımı koşullu dağılımların çarpımı olarak çarpanlara ayırır. |
| Latent (Gizli) | "Sıkıştırılmış kod" | Decoder'ın girdiyi yeniden oluşturabileceği düşük boyutlu temsil. |

## Üretim notu: beş aile, beş inference şekli

Her aile farklı bir inference sunucu maliyet eğrisine karşılık gelir. Üretim inference literatürü LLM inference'ı prefill + decode olarak çerçeveler; aynı ayrım burada da geçerlidir:

- **Autoregressive (1. ve 5. kategori).** Sıralı decode gecikmeye hakim olur; KV-cache, sürekli toplu işleme ve spekülatif decode doğrudan uygulanır.
- **VAE / diffusion / flow-matching (2. ve 4. kategori).** LLM anlamında decode yoktur. Maliyet = `adım_sayısı × adım_maliyeti` ve `adım_maliyeti`, tam latent çözünürlüğünde bir transformer veya U-Net forward'ıdır. Üretim ayarları adım sayısı (DDIM / DPM-Solver / distilasyon), toplu boyut ve hassasiyet (bf16 / fp8 / int4).
- **GAN (3. kategori).** Tek bir forward pass. Program yok, KV-cache yok. TTFT ≈ toplam gecikme. Bu yüzden StyleGAN dar-alan UX'inde hala kazanır.

Bir makale özetinde "diffusion'dan daha hızlı" gördüğünüzde, bunu "daha az adım × aynı adım maliyeti" veya "aynı adımlar × daha ucuz adım maliyeti" olarak çevirenin. Geri kalanı pazarlamadır.

## Daha Fazla Kaynak

- [Goodfellow et al. (2014). Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) — GAN makalesi.
- [Kingma & Welling (2013). Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) — VAE makalesi.
- [Ho, Jain, Abbeel (2020). Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) — DDPM makalesi.
- [Song et al. (2021). Score-Based Generative Modeling through SDEs](https://arxiv.org/abs/2011.13456) — diffusion'ın SDE olarak gösterimi.
- [Lipman et al. (2023). Flow Matching for Generative Modeling](https://arxiv.org/abs/2210.02747) — flow matching makalesi.
- [Esser et al. (2024). Scaling Rectified Flow Transformers for High-Resolution Image Synthesis](https://arxiv.org/abs/2403.03206) — Stable Diffusion 3.
