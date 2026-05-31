# GAN'lar — Generator (Üretici) vs Discriminator (Ayırt Edici)

> Goodfellow'un 2014'teki hilesi yoğunluğu tamamen atlamaktı. İki ağ. Birincisi sahteleri üretir. İkincisi onları yakalar. Sahteler gerçeklerden ayırt edilemez hale gelene kadar savaşırlar. Bu çalışmamalı. Genellikle çalışmaz. Çalıştığında ise, örnekler dar alanlar için literatürün hala en keskin olanlarıdır.

**Tür:** Oluşturma
**Diller:** Python
**Önkoşullar:** Faz 3 · 02 (Backprop), Faz 3 · 08 (Optimizasyoncular), Faz 8 · 02 (VAE)
**Süre:** ~75 dakika

## Problem

VAE'ler bulanık örnekler üretir çünkü MSE decoder kaybı *ortalama* görüntü için Bayes-optimaldir — ve birçok olası rakamın ortalaması bulanık bir rakamdır. *Olasılığı* ödüllendiren bir kayıp istersiniz, herhangi bir hedefe piksel bazlı yakınlığı değil. Olasılık için kapalı formda bir ifade yoktur. Onu öğrenmeniz gerekir.

Goodfellow'un fikri: gerçek görüntüleri sahtelerden ayırt etmek için bir sınıflandırıcı `D(x)` eğitin. `D`'yi kandırmak için bir generator `G(z)` eğitin. `G` için kayıp sinyali, `D`'nin bir şeyin gerçek görünmesini sağlayan şey olarak şu anda düşündüğü şeydir. Bu sinyal `G` geliştikçe değişen bir hedefin peşinden koşar. Her iki ağ da yakınsarsa, `G`, `log p(x)`'i hiç yazmadan veri dağılımını öğrenmiş olur.

Bu adversarial (düşmancıl) eğitimdir. Matematik bir minimax oyunudur:

```
min_G max_D  E_real[log D(x)] + E_fake[log(1 - D(G(z)))]
```

#### Açıklama
Bu, generator'un kaybını minimize ederken discriminator'un kaybını maximize etmeye çalışan bir oyun tanımıdır.

2026'da GAN'lar artık SOTA generator değildir (diffusion ve flow matching o tacı yemiştir). Ama StyleGAN 2/3 hala şimdiye kadar yayınlanmış en keskin yüz modelleridir, GAN discriminator'ları diffusion eğitiminde *algısal kayıplar* olarak kullanılır ve adversarial eğitim hızlı 1-adımlı distilasyonları (SDXL-Turbo, SD3-Turbo, LCM) destekler ve size gerçek zamanlı diffusion sunmanızı sağlar.

## Kavram

![GAN eğitimi: generator ve discriminator minimax içinde](../assets/gan.svg)

**Generator `G(z)`.** Bir gürültü vektörünü `z ~ N(0, I)` bir örnek `x̂`'ye eşler. Decoder şeklinde bir ağ (dense veya transposed conv).

**Discriminator `D(x)`.** Bir örneği skaler bir olasılığa (veya puana) eşler. Gerçek → 1, sahte → 0.

**Kayıp.** İki alternans güncellemesi:

- **`D`'yi eğit:** `loss_D = -[ log D(x) + log(1 - D(G(z))) ]`. Gerçek=1, sahte=0 üzerinde ikili cross-entropy.
- **`G`'yi eğit:** `loss_G = -log D(G(z))`. Bu Goodfellow'un kullandığı *doymamış* formdur (orijinal `log(1 - D(G(z)))` ifadesi `D` kendinden emin olduğunda doyar ve gradyanları öldürür).

**Eğitim döngüsü.** `D`'nin bir adımı, `G`'nin bir adımı. Tekrarla.

**Neden çalışır.** `G` `p_data`'yı mükemmel eşlerse, `D` şanstan daha iyi yapamaz ve her yerde 0.5 çıktı verir; `G` daha fazla gradyan almaz. Denge.

**Neden bozulur.** Mode collapse (`G`, `D`'nin sınıflandıramayacağı bir mod bulur ve sonsuza kadar onu basar), kaybolan gradyan (`D` çok hızlı öğrenir ve `log D` doyurur), eğitim istikrarsızlığı (öğrenme oranları, toplu boyutlar, her şey).

## GAN'ları çalıştıran varyantlar

| Yıl | İnovasyon | Düzeltme |
|------|------------|-----|
| 2015 | DCGAN | Conv/deconv, batch norm, LeakyReLU — ilk stabil mimari. |
| 2017 | WGAN, WGAN-GP | BCE'yi Wasserstein mesafesi + gradyan cezasıyla değiştir. Kaybolan gradyanı düzeltir. |
| 2017 | Spectral normalization | Discriminator'ı Lipschitz ile sınırla. 2026'da hala kullanılıyor. |
| 2018 | Progressive GAN | Önce düşük çözünürlüklü eğit, katman ekle. İlk megapiksel sonuçlar. |
| 2019 | StyleGAN / StyleGAN2 | Mapping network + adaptive instance norm. Sabit-alan fotogerçekçilik için en iyi. |
| 2021 | StyleGAN3 | Alias-free, translation-equivariant — 2026'da hala altın standart. |
| 2022 | StyleGAN-XL | Koşullu, sınıf farkındalıklı, daha büyük ölçek. |
| 2024 | R3GAN | Daha güçlü regularization ile yeniden markalaşma; 1024²'de hile olmadan çalışır. |

## Kodu Oluştur

`code/main.py`, 1 boyutlu veri üzerinde küçük bir GAN eğitir: iki Gauss'un karışımı. Generator ve discriminator tek gizli katmanlı MLP'lerdir. Forward, backward ve minimax döngüsünü el ile uygularız. Amaç, iki temel hata modunu (mode collapse + kaybolan gradyan) oldukları anda görmektir.

### Adım 1: doymamış kayıp

Vanilla Goodfellow kaybı `log(1 - D(G(z)))`, D G'nin sahtesini yüksek güvenle sahte olarak sınıflandırdığında 0'a gider. O noktada G için gradyan temelde sıfırdır — G iyileşemez. Doymamış form `-log D(G(z))` ters asimptotiğe sahiptir: D kendinden emin olduğunda patlar, G'ye güçlü bir sinyal verir.

```python
def g_loss(d_fake):
    # maximize log D(G(z))  <=>  minimize -log D(G(z))
    return -sum(math.log(max(p, 1e-8)) for p in d_fake) / len(d_fake)
```

#### Açıklama
Generator kaybı, discriminator'un sahte olarak sınıflandırma olasılığının logaritmasının tersidir.

### Adım 2: generator adımına bir discriminator adımı

```python
for step in range(steps):
    # train D
    real_batch = sample_real(batch_size)
    fake_batch = [G(z) for z in sample_noise(batch_size)]
    update_D(real_batch, fake_batch)

    # train G
    fake_batch = [G(z) for z in sample_noise(batch_size)]  # fresh fakes
    update_G(fake_batch)
```

#### Açıklama
G için taze sahteler, yoksa gradyanlar eski olur.

### Adım 3: mode collapse'a dikkat et

```python
if step % 200 == 0:
    samples = [G(z) for z in sample_noise(500)]
    mode_a = sum(1 for s in samples if s < 0)
    mode_b = 500 - mode_a
    if min(mode_a, mode_b) < 50:
        print("  [!] mode collapse: one mode is starved")
```

#### Açıklama
Klasik belirti: iki gerçek moddan biri üretilmeyi durdurur. Discriminator düzeltmeyi durdurur çünkü sahte olarak hiç görülmemiştir.

## Tuzaklar

- **Discriminator çok güçlü.** D'nin öğrenme oranını 2-5x kısaltın veya instance/layer gürültüsü ekleyin. D >95% doğruluğa ulaşırsa, G ölmüştür.
- **Generator bir modu ezbere.** D girişlerine gürültü ekleyin, minibatch-discriminator katmanı kullanın veya WGAN-GP'ye geçin.
- **Batch norm istatistik sızıntısı.** Gerçek batch + sahte batch aynı BN katmanından geçtiğinde istatistiklerini karıştırır. Bunun yerine instance norm veya spectral norm kullanın.
- **Inception-score kandırmacası.** FID ve IS düşük örnek sayılarında gürültülüdür. Değerlendirmede ≥10k örnek kullanın.
- **Tek atışlı örnek alma koşullu görevler için yalandır.** Kullanılabilir çıktılar elde etmek için hala CFG ölçekleri, kıstırma hileleri ve yeniden örnekleme gerekir.

## Kullan

2026 GAN yığını:

| Durum | Seçin |
|-----------|------|
| Fotogerçekçi insan yüzleri, sabit duruş | StyleGAN3 (en keskin, en küçük) |
| Anime / stilize yüzler | StyleGAN-XL veya Stable Diffusion LoRA |
| Görüntüden görsele çeviri | Pix2Pix / CycleGAN (Faz 8 · 04) veya ControlNet (Faz 8 · 08) |
| Hızlı 1-adımlı metinden görsele | Diffusion'ın adversarial distilasyonu (SDXL-Turbo, SD3-Turbo) |
| Diffusion eğitmeni içinde algısal kayıp | Görüntü kırpma çalışmaları üzerinde küçük GAN discriminator |
| Çok modlu, açık uçlu herhangi bir şey | Yapmayın — diffusion veya flow matching kullanın |

GAN'lar keskin ama dardır. Alanınız açıldığında — fotoğraflar, keyfi metin istekleri, video — diffusion'a geçin. Adversarial hilesi bağımsız bir generator olarak değil, bir bileşen olarak (algısal kayıplar, distilasyon) yaşamaya devam ediyor.

## Sun

`outputs/skill-gan-debugger.md` olarak kaydedin. Beceri başarısız bir GAN çalışmasını (kayıp eğrileri, örnek ızgarası, veri seti boyutu) alır ve olası nedenlerin sıralı listesini, tek satırlık düzeltmeleri ve yeniden çalıştırma protokolünü çıktı olarak verir.

## Alıştırmalar

1. **Kolay.** `code/main.py` dosyasını stok ayarlarıyla çalıştırın. Ardından `D_LR = 5 * G_LR` ayarlayın ve tekrar çalıştırın. G'nin kaybı ne kadar hızlı sabit bir değere çöker?
2. **Orta.** Goodfellow BCE kaybını WGAN kaybıyla değiştirin: `loss_D = E[D(fake)] - E[D(real)]`, `loss_G = -E[D(fake)]`, ve D'nin ağırlıklarını `[-0.01, 0.01]` aralığında kırpın. Eğitim daha mı stabil? Duvar saati yakınsamasını karşılaştırın.
3. **Zor.** 1 boyutlu örneği 2 boyutlu veriye genişletin (halka üzerinde 8 Gauss karışımı). Generator'un 1k, 5k, 10k adımlarda 8 moddan kaçını yakaladığını izleyin. Minibatch discriminasyonu uygulayın ve yeniden ölçün.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|------|-----------------|-----------------------|
| Generator (Üretici) | "G" | Gürültüden örneğe ağ, `G: z → x̂`. |
| Discriminator (Ayırt edici) | "D" | Sınıflandırıcı `D: x → [0, 1]`, gerçek vs sahte. |
| Minimax | "Oyun" | Ortak bir hedefin `min_G max_D` optimizasyonu. |
| Non-saturating loss (Doymamış kayıp) | "Düzeltme" | G için `log(1 - D(G(z)))` yerine `-log D(G(z))` kullanın. |
| Mode collapse (Mod çökmesi) | "G bir şeyi ezberledi" | Generator çeşitli verilere rağmen az sayıda farklı çıktı üretir. |
| WGAN | "Wasserstein" | BCE'yi Earth-Mover mesafesi + gradyan cezasıyla değiştirin; daha yumuşak gradyan. |
| Spectral norm (Spektral norm) | "Lipschitz hilesi" | D'nin ağırlık normlarını eğimini sınırlamak için kısıtla; eğitimi stabilizes eder. |
| StyleGAN | "Çalışan o" | Mapping network + AdaIN; yüzler için en iyi sınıf, 2026'da hala. |

## Üretim notu: tek atışlı inference GAN'ın kalıcı avantajıdır

GAN'lar artık açık alan üretimi için örnek kalitesinde kazanmıyor ama inference maliyetinde hala kazanıyor. Üretim inference literatürü sözlüğünde bir GAN şunlara sahiptir:

- **Prefill yok, decode aşaması yok.** Tek bir `G(z)` forward pass'ı. TTFT ≈ toplam gecikme.
- **KV-cache baskısı yok.** Tek durum ağırlıklardır. Toplu boyut aktivasyon belleğiyle sınırlıdır, cache ile değil.
- **Basit sürekli toplu işleme.** Her istek aynı sabit FLOPs'u aldığı için, sunucunun hedef meşguliyetindeki statik toplu genellikle optimaldir. Uçuşta zamanlayıcıya gerek yoktur.

Bu yüzden GAN distilasyonu (SDXL-Turbo, SD3-Turbo, ADD, LCM) 2026'da hızlı metinden görsele yönelik baskın tekniktir: 20-50 adımlık bir diffusion hattını diffusion tabanının dağılımını koruyarak 1-4 GAN tarzı forward pass'a düşürür. Adversarial kayıp, yavaş generator'ları hızlıya dönüştürmek için eğitim zamanı bir ayar olarak hayatta kalır.

## Daha Fazla Kaynak

- [Goodfellow et al. (2014). Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) — orijinal GAN makalesi.
- [Radford et al. (2015). Unsupervised Representation Learning with DCGAN](https://arxiv.org/abs/1511.06434) — ilk stabil mimari.
- [Arjovsky, Chintala, Bottou (2017). Wasserstein GAN](https://arxiv.org/abs/1701.07875) — WGAN.
- [Miyato et al. (2018). Spectral Normalization for GANs](https://arxiv.org/abs/1802.05957) — SN.
- [Karras et al. (2020). Analyzing and Improving the Image Quality of StyleGAN](https://arxiv.org/abs/1912.04958) — StyleGAN2.
- [Karras et al. (2021). Alias-Free Generative Adversarial Networks](https://arxiv.org/abs/2106.12423) — StyleGAN3.
- [Sauer et al. (2023). Adversarial Diffusion Distillation](https://arxiv.org/abs/2311.17042) — SDXL-Turbo.
