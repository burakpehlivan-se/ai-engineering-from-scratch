# StyleGAN

> Çoğu generator `z`'yi her katmana aynı anda karıştırır. StyleGAN onu ayırdı: önce `z`'yi ara bir `w`'ye eşleyin, sonra `w`'yi her çözünürlük seviyesine *enjekte edin* AdaIN aracılığıyla. Tek bir bu değişiklik latent uzayını ayrıştırdı ve fotogerçekçi yüzleri yedi yıl boyunca çözülmüş bir sorun haline getirdi.

**Tür:** Oluşturma
**Diller:** Python
**Önkoşullar:** Faz 8 · 03 (GAN'lar), Faz 4 · 08 (Normalleştirme), Faz 3 · 07 (CNN'ler)
**Süre:** ~45 dakika

## Problem

Bir DCGAN `z`'yi transposed convoluciónlar yığını üzerinden bir görsele eşler. Sorun: `z` her şeyi kontrol eder — duruş, aydınlatma, kimlik, arka plan — birbirine dolanmış olarak. `z`'nin bir ekseni boyunca hareket ettiğinizde dörtü birden değişir. Modele "aynı kişi, farklı duruş" diyemezsiniz çünkü temsil bu şekilde çarpanlara ayrılmaz.

Karras et al. (2019, NVIDIA) önerdi: `z`'yi doğrudan conv katmanlarına beslemeyi bırakın. Sabit bir `4×4×512` tensörünü ağ girdisi olarak besleyin. `z ∈ Z → w ∈ W` eşleyen 8 katmanlı bir MLP öğrenin. `w`'yi her çözünürlükte *adaptive instance normalization* (AdaIN) aracılığıyla enjekte edin: her conv özellik haritasını normalleştirin, ardından `w`'nin afin projeksiyonlarıyla ölçeklendirin ve kaydırın. Stokastik detay için (cilt gözenekleri, saç telleri) katman başına gürültü ekleyin.

Sonuç: `W` roughly "yüksek seviyeli stil" (duruş, kimlik) ile "ince stil" (aydınlatma, renk) için dik eksene sahiptir. İki görüntü arasında stilleri, görüntü A'nın düşük çözünürlüklü seviyeleri için `w`'sini ve görüntü B'nin yüksek çözünürlüklü seviyeleri için `w`'sini kullanarak değiştirebilirsiniz. Bu, düzenleme, çapraz-alan stilizasyonu ve tüm "StyleGAN-inversion" araştırma hattının kilidini açtı.

## Kavram

![StyleGAN: mapping network + AdaIN + katman başına gürültü](../assets/stylegan.svg)

**Mapping network.** `f: Z → W`, 8 katmanlı MLP. `Z = N(0, I)^512`. `W` Gauss olmak zorunda değildir — veriye adapte olmuş bir şekil öğrenir.

**Synthesis network.** Öğrenilmiş sabit `4×4×512`'den başlar. Her çözünürlük bloğu: `upsample → conv → AdaIN(w_i) → gürültü → conv → AdaIN(w_i) → gürültü`. Çözünürlükler ikiye katlanır: 4, 8, 16, 32, 64, 128, 256, 512, 1024.

**AdaIN.**

```
AdaIN(x, y) = y_scale · (x - mean(x)) / std(x) + y_bias
```

#### Açıklama
Burada `y_scale` ve `y_bias`, `w`'nin afin projeksiyonlarından gelir. Özellik haritası başına normalleştirin, ardından yeniden stillendirin. "Burada stil" ifadesi özellik haritasının birinci ve ikinci derece istatistikleridir.

**Katman başına gürültü.** Her özellik haritasına eklenen tek kanallı Gauss gürültüsü, öğrenilmiş kanal başına faktörle ölçeklendirilir. Global yapıyı etkilemeden stokastik detayı kontrol eder.

**Kıstırma hilesi.** Inference'ta, `z` örnekle, `w = mapping(z)` hesapla, ardından `w' = ŵ + ψ·(w - ŵ)` yazın, burada `ŵ` birçok örnek üzerindeki ortalama `w`'dir. `ψ < 1` çeşitliliği kaliteyle değiştirir. Neredeyse her StyleGAN demosu `ψ ≈ 0.7` kullanır.

## StyleGAN 1 → 2 → 3

| Versiyon | Yıl | İnovasyon |
|---------|------|------------|
| StyleGAN | 2019 | Mapping network + AdaIN + gürültü + ilerlemeli büyüme. |
| StyleGAN2 | 2020 | Weight demodulation AdaIN'i değiştirir (damla artifact'larını düzeltir); skip/residual mimari; yol-uzunluk regularizasyonu. |
| StyleGAN3 | 2021 | Alias-free convolución + eşdeğer çekirdekler; dokunun piksel ızgarasına yapışmasını ortadan kaldırır. |
| StyleGAN-XL | 2022 | Koşullu, 1024², ImageNet. |
| R3GAN | 2024 | Daha güçlü regularization ile yeniden markalaşma; FFHQ-1024'te diffusion ile arasındaki boşluğu 20x daha az parametreyle kapatıyor. |

2026'da StyleGAN3 (a) yüksek FPS'de dar-alan fotogerçekçilik, (b) few-shot alan uyumlama (100 görüntüyle yeni bir veri setinde eğitme, mapping'i dondur), (c) inversion tabanlı düzenleme (gerçek bir fotoğrafı yeniden oluşturan `w`'yi bulma, ardından o `w`'yi düzenleme) için varsayılan olmaya devam ediyor. Açık alan metinden görsele için bu araç değil — diffusion'dır.

## Kodu Oluştur

`code/main.py`, 1 boyutlu oyuncak bir "style-GAN lite" uygular: bir mapping MLP, öğrenilmiş sabit bir vektör alıp `w`'den türetilen ölçek/kaydırma ile modüle eden bir synthesis fonksiyonu ve katman başına gürültü. `w`'yi afin modülasyonuyla enjekte etmenin generator'un girdisine `z` eklemekle eşdeğer veya daha iyi olduğunu gösterir.

### Adım 1: mapping network

```python
def mapping(z, M):
    h = z
    for i in range(num_layers):
        h = leaky_relu(add(matmul(M[f"W{i}"], h), M[f"b{i}"]))
    return h
```

#### Açıklama
Mapping network, gizli uzayı veri istatistiklerinden ayırır.

### Adım 2: adaptive instance normalization

```python
def adain(x, w_scale, w_bias):
    mu = mean(x)
    sd = std(x)
    x_norm = [(xi - mu) / (sd + 1e-8) for xi in x]
    return [w_scale * xi + w_bias for xi in x_norm]
```

#### Açıklama
Özellik haritası başına ölçek ve kaydırma, `w`'den doğrusal projeksiyonla gelir.

### Adım 3: katman başına gürültü

```python
def add_noise(x, sigma, rng):
    return [xi + sigma * rng.gauss(0, 1) for xi in x]
```

#### Açıklama
Kanal başına sigma öğrenilebilir.

## Tuzaklar

- **Damla artifact'ları.** StyleGAN 1, AdaIN mean'ı sıfırladığı için özellik haritalarında damlacık benzeri bir leke üretti. StyleGAN 2'nin weight demodulation'ı bunu conv ağırlıklarını ölçeklendirerek düzeltir.
- **Doku yapışması.** StyleGAN 1 ve 2 dokuları piksel koordinatlarını takip eder, nesne koordinatlarını değil (yorumlama yaparken görünür). StyleGAN 3'ün alias-free convolución'ları bunu pencerelei süzgeçlerle düzeltir.
- **Mod kapsamı.** Kıstırma `ψ < 0.7` temiz görünür ama dar bir koniden örnek alır; çeşitlilik istiyorsanız `ψ = 1.0` kullanın.
- **Inversion kayıplıdır.** Gerçek bir fotoğrafı `W` içine tersine çevirmek genellikle optimizasyon veya bir encoder (e4e, ReStyle, HyperStyle) ile yapılır. Sonuçlar birçok iterasyon sonra sapar.

## Kullan

| Kullanım durumu | Yaklaşım |
|----------|----------|
| Fotogerçekçi insan yüzleri (anime, ürün, dar) | StyleGAN3 FFHQ / özel ince ayar |
| Fotoğraftan yüz düzenleme | e4e inversion + StyleSpace / InterFaceGAN yönleri |
| Yüz değiştirme / yeniden canlandırma | StyleGAN + encoder + birleştirme |
| Avatar hatları | Düşük veri ince ayarı için ADA'lı StyleGAN3 |
| Birkaç görüntüden alan uyumlama | Mapping network'ü dondur, synthesis'i ince ayarla |
| Çok modlu veya metin koşullu üretim | Yapmayın — diffusion kullanın |

"Kişinin yüzünün fotoğrafı" yanıtı olan ürün演示leri için, StyleGAN inference maliyetinde (tek forward pass, 4090'da <10ms) ve aynı kalite çubuğunda keskinlikte diffusion'ı yener.

## Sun

`outputs/skill-stylegan-inversion.md` olarak kaydedin. Beceri gerçek bir fotoğraf alır ve çıktıyı verir: inversion yöntemi (e4e / ReStyle / HyperStyle), beklenen latent kaybı, düzenleme bütçesi (artifact'lar oluşmadan `W`'de ne kadar hareket edilebildiği) ve bilinen iyi düzenleme yönlerinin listesi (yaş, ifade, duruş).

## Alıştırmalar

1. **Kolay.** `code/main.py` dosyasını `adain_on=True` ve `adain_on=False` ile çalıştırın. Sabit latent vs bozulmuş latent için çıktıların yayılımını karşılaştırın.
2. **Orta.** Karıştırma regularizasyonunu uygulayın: bir eğitim batch'i için `w_a`, `w_b` hesaplayın ve synthesis'in ilk yarısında `w_a`, ikinci yarısında `w_b` uygulayın. Decoder ayrıştırılmış stiller öğrenir mi?
3. **Zor.** Önceden eğitilmiş bir StyleGAN3 FFHQ modeli (ffhq-1024.pkl) alın. Etiketli örnekler üzerinde bir SVM eğiterek "gülümseme"yi kontrol eden `w` yönünü bulun; kimlik sapmadan ne kadar ileri itebileceğinizi bildirin.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|------|-----------------|-----------------------|
| Mapping network | "MLP" | `f: Z → W`, 8 katman, latent geometrisini veri istatistiklerinden ayırır. |
| W space | "Stil uzayı" | Mapping network'ün çıktısı; yaklaşık olarak ayrıştırılmış. |
| AdaIN | "Adaptive instance norm" | Özellik haritasını normalleştir, ardından `w` projeksiyonuyla ölçekle + kaydır. |
| Truncation trick (Kıstırma hilesi) | "Psi" | `w = mean + ψ·(w - mean)`, ψ<1 çeşitliliği kaliteyle değiştirir. |
| Path-length regularization (Yol-uzunluk regularizasyonu) | "PL reg" | `w`'deki birim değişiklik başına görüntüdeki büyük değişiklikleri cezalandırır; `W`'yi daha pürüzsüz yapar. |
| Weight demodulation | "StyleGAN2 düzeltmesi" | Aktivasyonlar yerine conv ağırlıklarını normalleştir; damla artifact'larını öldürür. |
| Alias-free | "StyleGAN3 hilesi" | Pencerelei süzgeçler; dokunun piksel ızgarasına yapışmasını ortadan kaldırır. |
| Inversion (Tersine çevirme) | "Gerçek görüntü için w bul" | `x → w` Optimize veya encode et ki `G(w) ≈ x` olsun. |

## Üretim notu: StyleGAN neden 2026'da hala sunuluyor

4090'daki StyleGAN3, 1024² FFHQ yüzünü 10 ms'den kısa sürede üretir — `num_steps = 1`, VAE decode yok, cross-attention pass yok. Üretim terimleriyle bu, herhangi bir görüntü üreticisinin taban gecikmesidir. Aynı çözünürlükte 50 adımlık SDXL + VAE-decode hattı yaklaşık 3 saniyedir. Bu **300x farktır** ve dar-alan ürünleri (avatar hizmetleri, kimlik belgesi hatları, stok yüz üretimi) için TCO'da kazanır.

İki operasyonel sonuç:

- **Zamanlayıcı yok, toplayıcı yok.** Hedef meşguliyetteki statik toplu optimaldir. Sürekli toplu işleme (LLM'ler ve diffusion için gerekli) sıfır fayda sağlar çünkü her istek aynı FLOPs'u alır.
- **Kıstırma `ψ` güvenlik ayarıdır.** `ψ < 0.7` mapping network'ün aralığının dar bir konisinden örnek alır. Bu, örnekleme varyansı üzerinde sunma katmanının sahip olduğu tek kaldıraçtır. Yoğunlukta `ψ`'yi düşürün, premium kullanıcılar için yükseltin.

## Daha Fazla Kaynak

- [Karras et al. (2019). A Style-Based Generator Architecture for GANs](https://arxiv.org/abs/1812.04948) — StyleGAN.
- [Karras et al. (2020). Analyzing and Improving the Image Quality of StyleGAN](https://arxiv.org/abs/1912.04958) — StyleGAN2.
- [Karras et al. (2021). Alias-Free Generative Adversarial Networks](https://arxiv.org/abs/2106.12423) — StyleGAN3.
- [Tov et al. (2021). Designing an Encoder for StyleGAN Image Manipulation](https://arxiv.org/abs/2102.02766) — e4e inversion.
- [Sauer et al. (2022). StyleGAN-XL: Scaling StyleGAN to Large Diverse Datasets](https://arxiv.org/abs/2202.00273) — StyleGAN-XL.
- [Huang et al. (2024). R3GAN: The GAN is dead; long live the GAN!](https://arxiv.org/abs/2501.05441) — modern minimal GAN tarifi.
