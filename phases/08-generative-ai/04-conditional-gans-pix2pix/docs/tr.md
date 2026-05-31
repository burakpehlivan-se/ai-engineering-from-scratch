# Koşullu GAN'lar ve Pix2Pix

> 2014-2017 arasındaki ilk büyük açılım, bir GAN'ın ne ürettiğini kontrol etmekti. Bir etiket, bir görüntü veya bir cümle ekleyin. Pix2Pix görüntü versiyonunu yaptı ve hala dar görüntüden görsele görevlerde her genel metinden görsele modelini geçiyor.

**Tür:** Oluşturma
**Diller:** Python
**Önkoşullar:** Faz 8 · 03 (GAN'lar), Faz 4 · 06 (U-Net), Faz 3 · 07 (CNN'ler)
**Süre:** ~75 dakika

## Problem

Koşulsuz GAN keyfi yüzler üretir. Demo için faydalı, üretimde işe yaramaz. İstediğiniz şey: *bir eskizi fotoğrafa dönüştürmek*, *bir haritayı hava fotoğrafına dönüştürmek*, *bir gündüz sahnesini geceye dönüştürmek*, *gri tonlamalı bir görüntüyü renklendirmek*. Tüm bu görevlerde, bir girdi görüntüsü `x` alırsınız ve bazı anlamsal karşılıklılıklar içeren `y` çıktısı vermeniz gerekir. Her `x` için birçok olası `y` vardır. Ortalama kare hata (MSE) bunları çamur haline getirir. Adversarial kayıp bunu yapmaz, çünkü "gerçek görünüyor" ifadesi keskindir.

Koşullu GAN (Mirza & Osindero, 2014) hem `G`'ye hem de `D`'ye bir koşul `c` ekler. Pix2Pix (Isola et al., 2017) bunu özelleştirdi: koşul tam bir girdi görüntüsüdür, generator bir U-Net'tir, discriminator *yama tabanlı* bir sınıflandırıcıdır (PatchGAN) ve kayıp adversarial + L1'dir. Bu tarif, 2026'da bile *eşleştirilmiş verilerle* eğitildiği için dar görüntüden görsele alanlarda sıfırdan metinden görsele modellerini geçer — ihtiyacınız olan sinyale tam olarak sahipsiniz.

## Kavram

![Pix2Pix: U-Net generator, PatchGAN discriminator](../assets/pix2pix.svg)

**Koşullu G.** `G(x, z) → y`. Pix2Pix'te, `z` G içinde dropout'tur (girdi gürültüsü yok — Isola, açıkça gürültünün görmezden gelindiğini buldu).

**Koşullu D.** `D(x, y) → [0, 1]`. Girdi *çift* (koşul, çıktı)'dır. Bu anahtardır: D, `y`'nin `x` ile tutarlı olup olmadığını yargılamalıdır, sadece `y`'nin gerçek görünüp görünmediğini değil.

**U-Net generator.** Darboğaz boyunca skip bağlantılı encoder-decoder. Girdi ve çıktının düşük seviyeli yapıyı (kenarlar, siluet) paylaştığı görevler için kritiktir. Skip'ler olmadan, yüksek frekans detayı kaybolur.

**PatchGAN discriminator.** Tek bir gerçek/sahte skoru çıktı vermek yerine, D `N×N` bir ızgara çıktı verir, her hücre yaklaşık 70×70 piksellik bir reseptif alanı yargılar. Ortalama alınır. Bu Markov rastgele alanı varsayımdır: gerçekçilik yereldir. Daha hızlı eğitilir, daha az parametre, daha keskin çıktı.

**Kayıp.**

```
loss_G = -log D(x, G(x)) + λ · ||y - G(x)||_1
loss_D = -log D(x, y) - log (1 - D(x, G(x)))
```

#### Açıklama
L1 terimi eğitimi stabilize eder ve G'yi bilinen hedefe doğru iter. L1, L2'den daha keskin kenarlar verir (medyanlar, ortalamalar). `λ = 100` Pix2Pix varsayılan değeriydi.

## CycleGAN — çiftleriniz olmadığında

Pix2Pix eşleştirilmiş `(x, y)` verisi gerektirir. CycleGAN (Zhu et al., 2017) bunu bir ekstra kayıp karşılığında bırakır: *döngü tutarlılığı* kaybı. İki generator `G: X → Y` ve `F: Y → X`. `F(G(x)) ≈ x` ve `G(F(y)) ≈ y` olacak şekilde eğitin. Bu, çiftli örnekler olmadan atları zebralara, yazıları kışa çevirmenizi sağlar.

2026'da, eşleşmemiş görüntüden görsele çoğunlukla CycleGAN yerine diffusion (ControlNet, IP-Adapter) ile yapılır, ama döngü-tutarlılığı fikri neredeyse her eşleşmemiş alan uyumlama makalesinde hayatta kalır.

## Kodu Oluştur

`code/main.py`, 1 boyutlu veri üzerinde küçük bir koşullu GAN uygular. Koşul `c` bir sınıf etiketidir (0 veya 1). Görev: verilen sınıf için koşullu dağılımdan bir örnek üretmek.

### Adım 1: her iki G ve D girişine koşul ekle

```python
def G(z, c, params):
    return mlp(concat([z, one_hot(c)]), params)

def D(x, c, params):
    return mlp(concat([x, one_hot(c)]), params)
```

#### Açıklama
One-hot kodlama en basit yoldur. Daha büyük modeller öğrenilmiş embedding'ler, FiLM modülasyonu veya cross-attention kullanır.

### Adım 2: koşullu olarak eğit

```python
for step in range(steps):
    x, c = sample_real_conditional()
    noise = sample_noise()
    update_D(x_real=x, x_fake=G(noise, c), c=c)
    update_G(noise, c)
```

#### Açıklama
Generator, verilen koşul için gerçek dağılımı *eşlemelidir*, marjinali değil.

### Adım 3: sınıf başına çıktıyı doğrula

```python
for c in [0, 1]:
    samples = [G(noise, c) for noise in batch]
    mean_c = mean(samples)
    assert_near(mean_c, real_mean_for_class_c)
```

#### Açıklama
Her sınıfın çıktısının gerçek ortalamaya yakın olup olmadığını kontrol eder.

## Tuzaklar

- **Koşul görmezden geliniyor.** G marjinali öğrenir, D hiçbir zaman cezalandırmaz çünkü koşul sinyali zayıftır. Çözüm: D'yi daha agresif koşullandırın (erken katman, sadece geç), projection discriminator kullanın (Miyato & Koyama 2018).
- **L1 ağırlığı çok düşük.** G, gerçekçi görünmesine rağmen sadık olmayan rastgele çıktılara kayar. Pix2Pix tarzı görevler için λ≈100 ile başlayın.
- **L1 ağırlığı çok yüksek.** G bulanık çıktılar üretir çünkü L1 hâlâ bir L_p normudur. Eğitim stabilleştikten sonra aşağı anneal edin.
- **D'de ground-truth sızıntısı.** D girdisi olarak sadece `y`'yi değil, `(x, y)` çiftini birleştirin. Bunu yapmazsanız D tutarlılığı kontrol edemez.
- **Sınıf başına mode collapse.** Her sınıf bağımsız olarak çökebilir. Sınıf koşullu çeşitlilik kontrolleri çalıştırın.

## Kullan

2026 görüntüden görsele görevlerinin durumu:

| Görev | En iyi yaklaşım |
|------|---------------|
| Eskiz → fotoğraf, aynı alan, eşleştirilmiş veri | Pix2Pix / Pix2PixHD (hâlâ hızlı, hâlâ keskin) |
| Eskiz → fotoğraf, eşleşmemiş | Scribble koşullandırma modeliyle ControlNet |
| Anlamsal bölütleme → foto | SPADE / GauGAN2 veya SD + ControlNet-Seg |
| Stil aktarımı | IP-Adapter veya LoRA ile diffusion; GAN yöntemleri miras |
| Derinlik → foto | Stable Diffusion üzerinde ControlNet-Depth |
| Süper çözünürlük | Real-ESRGAN (GAN), ESRGAN-Plus veya SD-Upscale (diffusion) |
| Renklendirme | ColTran, diffusion tabanlı renklendiriciler veya Pix2Pix-color |
| Gündüz → gece, mevsimler, hava | CycleGAN veya ControlNet tabanlı |

Pix2Pix, (a) binlerce eşleştirilmiş örneğiniz olduğunda, (b) görev dar ve tekrarlanabilir olduğunda ve (c) hızlı inference gerektiğinde hâlâ doğru araçtır. Genel açık alan görevlerinde diffusion kazanır.

## Sun

`outputs/skill-img2img-chooser.md` olarak kaydedin. Beceri bir görev açıklaması, veri durumu (eşleşmiş vs eşleşmemiş, N örnek) ve gecikme/kalite bütçesi alır, ardından çıktıyı verir: yaklaşım (Pix2Pix, CycleGAN, ControlNet varyantı, SDXL + IP-Adapter), eğitim verisi gereksinimleri, inference maliyeti ve değerlendirme protokolü (LPIPS, FID, göreve özel).

## Alıştırmalar

1. **Kolay.** `code/main.py` dosyasını değiştirerek üçüncü bir sınıf ekleyin. G'nin her sınıfın gürültüsünü doğru moda eşlediğini doğrulayın.
2. **Orta.** 1 boyutlu ortamda L1'i algısal stil kaybıyla değiştirin (örn. özellik çıkaran olarak hareket eden küçük dondurulmuş D). Koşullu dağılımdaki keskinliği değiştirir mi?
3. **Zor.** 1 boyutlu ortamda bir CycleGAN taslağı çizin: iki dağılım, iki generator, döngü kaybı. Eşleşmemiş veri olmadan aralarında geçiş yaptığını gösterin.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|------|-----------------|-----------------------|
| Koşullu GAN | "Etiketli GAN" | G(z, c), D(x, c). Her iki ağ da koşulu görür. |
| Pix2Pix | "Görüntüden görsele GAN" | U-Net G ve PatchGAN D + L1 kaybıyla eşleştirilmiş cGAN. |
| U-Net | "Skip'li encoder-decoder" | Simetrik conv ağı; skip'ler yüksek frekansı korur. |
| PatchGAN | "Yerel gerçekçilik sınıflandırıcısı" | D global skor yerine yama başına skor çıktı verir. |
| CycleGAN | "Eşleşmemiş görüntü çevirisi" | İki G + döngü-tutarlılığı kaybı; eşleşmemiş veri yok. |
| SPADE | "GauGAN" | Ara aktivasyonları anlamsal haritayla normalleştirir; bölümlemeden görsele. |
| FiLM | "Özellik bazlı doğrusal modülasyon" | Koşuldan özellik başına afine dönüşüm; ucuz koşullandırma. |

## Üretim notu: Pix2Pix gecikme sınırlı bir temel olarak

Eşleşmiş veriniz ve dar bir göreviniz olduğunda (eskiz → işleme, anlamsal harita → foto, gündüz → gece), Pix2Pix'in tek atışlı inference'ı gecikme açısından diffusion'ı bir büyüklük sırası kadar yener. Üretim karşılaştırması genellikle şöyledir:

| Yol | Adımlar | Tek L4'te 512² tipik gecikme |
|------|-------|----------------------------------------|
| Pix2Pix (U-Net forward) | 1 | ~30 ms |
| SD-Inpaint veya SD-Img2Img | 20 | ~1.2 s |
| SDXL-Turbo Img2Img | 1-4 | ~0.15-0.35 s |
| ControlNet + SDXL tabanı | 20-30 | ~3-5 s |

Pix2Pix statik toplularda (her istek aynı FLOPs) verimlilikte kazanır. Diffusion kalite ve genellemede kazanır. Modern yaklaşım genellikle dar görev için damıtılmış bir Pix2Pix tarzı model sunmak ve kuyruk girdileri için bir diffusion yedeği tutmaktır.

## Daha Fazla Kaynak

- [Mirza & Osindero (2014). Conditional Generative Adversarial Nets](https://arxiv.org/abs/1411.1784) — cGAN makalesi.
- [Isola et al. (2017). Image-to-Image Translation with Conditional Adversarial Networks](https://arxiv.org/abs/1611.07004) — Pix2Pix.
- [Zhu et al. (2017). Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks](https://arxiv.org/abs/1703.10593) — CycleGAN.
- [Wang et al. (2018). High-Resolution Image Synthesis with Conditional GANs](https://arxiv.org/abs/1711.11585) — Pix2PixHD.
- [Park et al. (2019). Semantic Image Synthesis with Spatially-Adaptive Normalization](https://arxiv.org/abs/1903.07291) — SPADE / GauGAN.
- [Miyato & Koyama (2018). cGANs with Projection Discriminator](https://arxiv.org/abs/1802.05637) — projection D.
