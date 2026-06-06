# Chameleon ve Erken Birleşmeli (Early-Fusion) Yalnızca Token Multimodal Modelleri

> Bugüne kadar gördüğümüz her VLM görüntüleri ve metni ayrı tutar. Görsel token'lar bir görüntü kodlayıcısından gelir, bir projeksiyoncudan geçer, sonra LLM içinde metinle karşılaşır. Görüntü ve metin sözlükleri asla kesişmez. Chameleon (Meta, Mayıs 2024) sordu: ya kesişirlerse? Paylaşımlı bir sözlükten (vocabulary) disket token'lar üreten bir VQ-VAE eğitin. Artık her multimodal belge tek bir dizidir — görüntü token'ları ve metin token'ları aralıklı, tek bir otoregresif kayıp. Yan etki: model karmaşık-modaliteli çıktılar üretebilir — tek bir çıkarım çağrısında metin ve görüntü token'arı arasında geçiş yapabilir. Bu ders erken-birleşme (early fusion) tezini inceler ve baştan sona oyuncu bir versiyonu uygular.

**Tür:** İnşa Et
**Diller:** Python (stdlib, VQ-VAE tokenize edici + aralıklı çözümleyici)
**Önkoşullar:** Faz 12 · 05, Faz 8 (Generatif Yapay Zeka)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Paylaşımlı sözlük + tek kaybın modelin yapabileceklerini neden değiştirdiğini açıklama.
- Bir VQ-VAE'nin bir görüntüyü bir transformer'ın sonraki-token hedefiyle uyumlu bir disket dizisine nasıl tokenize ettiğini tasvir etme.
- Chameleon'ın eğitim kararlılığı hilelerini adlandırma: QK-Norm, bırakma (dropout) yerleşimi, LayerNorm sıralaması.
- Chameleon'ı BLIP-2'nin Q-Former yaklaşımıyla karşılaştırma ve her birinin ne zaman doğru seçim olduğunu tasvir etme.

## Sorun

Adaptörlü VLM'ler (LLaVA, BLIP-2, Qwen-VL) metni ve görüntüyü iki farklı şey olarak ele alır. Bir metin token'ı `embed(text_token)`'ten geçer; bir görüntü `visual_encoder(image) → projector → ... pseudo_token`'lardan. Modelin iki girdi yolu vardır ve bir yerde birleşirler.

Üç sonuç:

1. LLM yalnızca görüntüleri tüketebilir, üretemez. Çıktı yalnızca metindir.
2. Karmaşık-modaliteli belgeler (bir makaledeki paragraflar ve görüntüler arası) beceriksizdir — multimodal girdiyi modelin dışında ayrıştırırsınız veya nesiller zincirlersiniz.
3. Dağılımsal uyumsuzluk. Görsel token'lar ve metin token'ları gizli uzayın farklı bölgelerinde yaşar, ince hizalama sorunları yaratır.

Chameleon varsayımı reddeder: görüntüler yalnızca paylaşımlı sözlükten disket token dizileridir. Modeli aralıklı belgelerde, tek kayıpla, tek otoregresif çözümleyiciyle eğitin ve karmaşık-modaliteli üretimin kilidini ücretsiz açın.

## Kavram

### VQ-VAE görüntü tokenize edici olarak

Tokenize edici bir vektör-nicelleştirilmiş (vector-quantized) değişken otokodlayıcıdır (variational autoencoder). Mimari:

- Kodlayıcı: CNN + ViT, görüntüyü uzamsal bir özellik haritasına haritalar, örneğin 256 boyutunda 32x32 özellik.
- Sözlük (codebook): K vektörlük öğrenilmiş sözlük (Chameleon 8192 kullanır),同样 256 boyutlu.
- Nicelleştirme: her uzamsal özellik için en yakın sözlük girdisini L2 mesafesine göre arayın. Sürekli özelliği tamsayı indeksiyle değiştirin.
- Çözümleyici: nicelleştirilmiş özellikleri piksellere geri götüren CNN.

Eğitim: VAE yeniden oluşturma kaybı + bağlılık kaybı (commitment loss) + sözlük kaybı. Sözlük indeksleri görüntü için bir disket alfabe oluşturur.

Chameleon için: bir görüntü 8192'lik sözlükten çekilen 32*32 = 1024 token olur. Metin token'larıyla (LLM'in BPE sözlüğünden, örneğin 32000) birleştirilir. Son sözlük: 40192. Transformer tek bir dizi, tek bir kayıp görür.

### Paylaşımlı sözlük

Chameleon'ın sözlüğü metin token'larını, görüntü token'larını ve modalite ayraçlarını (separators) birleştirir. Her token'ın tek bir ID'si vardır. Girdi gömme katmanı her ID'yi D boyutlu bir gizli vektöre haritalar. Çıktı projeksiyonu gizliyi sözlük logit'lerine geri haritalar. Softmax hangi modalite olursa olsun bir sonraki token'ı seçer.

Ayraçlar önemlidir: `<image>` ve `</image>` etiketleri görüntü-token dizisini çeperler. Üretim sırasında model `<image>` çıkarsa, aşağı akış yazılımı sonraki 1024 token'ın piksel oluşturmak için çözümleyiciye gönderilecek VQ indeksleri olduğunu bilir.

### Karmaşık-modaliteli üretim

Çıkarım paylaşımlı sözlükte sonraki-token tahminidir. Örnek istem: "Bir kedi çiz ve tanımla." Chameleon şunları üretir:

```
<image> 4821 1029 2891 ... (1024 image tokens) </image>
The cat is orange, sitting on a windowsill...
```

#### Açıklama
Model sırayı bağımsız olarak seçer — önce görüntü, sonra metin, önce metin, sonra görüntü veya aralıklı üretebilir. Aynı çözümleyici, aynı kayıp.

Adaptör VLM'lerde üretim yalnızca metindir. Chameleon model çıktı modaliteleri sorusunu yeniden açar.

### Eğitim kararlılığı — QK-Norm, bırakma, LayerNorm sıralaması

Erken-birleşme eğitimi ölçekte kararsızdır. Chameleon makalesi üç hileyi belgeler:

- QK-Norm. Dikkat içindeki sorgu ve anahtar projeksiyonlarına nokta çarpımı öncesi LayerNorm uygulayın. Derinlikte logit büyüklüğü patlamasını önler. 2024 sonrası büyük modeller tarafından kullanılır.
- Bırakma yerleşimi. Yalnızca dikkat ve MLP'den sonra değil, her artıklık eklemesinden (residual-add) sonra bırakma. Görüntü token'larından gelen gradyanlar baskın olabileceğinden daha fazla düzenlileştirme (regularization) gerekir.
- LayerNorm sıralaması. Artıklık dalında Pre-LN (standart), artı son bloğun atlanma bağlantısında ekstra LN. Son katman gradyan akışını kararlaştırır.

Bu hileler olmadan 34B parametrelik Chameleon eğitimi birçok kontrol noktasında sapıyordu. Bunlarla yakınsıyor. Eğitim tarifi mimari kadar katkıdır.

### Tokenize edicinin yeniden oluşturma tavanı

VQ-VAE kayıplıdır. 8192 sözlük girdisi ve 512x512 görüntü için 1024 token'da yeniden oluşturma PSNR'si yaklaşık 26-28 dB'de tavan yapar. Bu tanınabilir görüntü üretimi için yeterlidir ama sürekli uzay difüzyonundan (Stable Diffusion 3 32+ dB elde eder) görsel olarak daha düşüktür.

Tokenize edici darboğazdır. Daha iyi tokenize ediciler (MAGVIT-v2, IBQ, SBER-MoVQGAN) tavanı yükseltir. Emu3 (Ders 12.12) yalnızca daha iyi bir tokenize ediciyle SDXL kalitesinde üretime ulaşır.

### Chameleon vs BLIP-2 / LLaVA

Chameleon (erken birleşme, paylaşımlı sözlük):
- Tek kayıp, tek çözümleyici.
- Karmaşık-modaliteli çıktı üretir.
- Tokenize edici kalite tavanıdır.
- Pahalı: her üretilen görüntü için çıkarım yolunda VQ-VAE çözümleyicisi.

BLIP-2 / LLaVA (geç birleşme, ayrı kuleler):
- Görüntü girdi, yalnızca metin çıktı.
- Önceden eğitilmiş LLM'i yeniden kullanır.
- Anlama için tokenize edici darboğazı yok.
- Ucuz: tek ileri geçiş.

Göreve göre seçin. Görüntü üretimi gerekiyorsa Chameleon ailesi. Yalnızca anlama gerekiyorsa adaptör-VLM daha basittir ve daha fazla önceden eğitilmiş hesaplama yeniden kullanır.

### Fuyu ve AnyGPT

Fuyu (Adept, 2023) ilgili bir yaklaşımdır: ayrı görüntü kodlayıcısını tamamen atlar, ham yama token'larını LLM'in girdi projeksiyonundan sanki token'larmış gibi besler, tokenize edici yok. Chameleon'dan daha basit, paylaşımlı sözlük çıktı üretimini kaybeder.

AnyGPT (Zhan ve diğerleri, 2024) Chameleon'ı dört modale genişletir: metin, görüntü, konuşma, müzik. Her biri için aynı VQ-VAE hilesi, paylaşımlı transformer. Her şeyden her şeye üretim. Ders 12.16'da daha fazla ele alınır.

## Kullan

`code/main.py` oyuncu bir uçtan uca erken-birleşme modeli inşa eder:

- 8x8 yamaları sözlük indekslerine (K=16) haritalayan küçük bir VQ-VAE tarzı nicelleştirici.
- (metin id'leri 0..31) + (görüntü id'leri 32..47) + (ayraçlar 48, 49)组成的 paylaşımlı sözlük.
- Sentetik açıklamalar + görüntü-token dizileri üzerinde eğitilmiş oyuncu bir otoregresif çözümleyici (bigram tablosu).
- Bir istem verildiğinde art arda metin + görüntü token'ları üreten örnekleme döngüsü.

Kod transformer'ı kasıtlı olarak küçük tutar (bigram'lar), böylece sinyal akışını baştan sona izleyebilirsiniz.

## Teslimat

Bu ders `outputs/skill-tokenizer-vs-adapter-picker.md` dosyasını üretir. Bir ürün şartnamesi (yalnızca anlama vs anlama + üretme, gerekli görüntü kalitesi, maliyet bütçesi) verildiğinde, Chameleon ailesi (erken birleşme) ile LLaVA ailesi (geç birleşme) arasında seçim yapar ve nicel kural-of-thumbs ile gerekçelendirir.

## Alıştırmalar

1. Chameleon 8192 sözlük girdisi ve 512x512 görüntü için 1024 token kullanır. 24-bit RGB görüntüye kıyasla sıkıştırma oranını tahmin edin. Kayıplı mı? Ne kadar kayıplı?

2. Aynı VQ-VAE yoğunluğuyla 4K görüntü (3840x2160) kaç görüntü token'ı üretir? Chameleon tarzı bir model 4K görüntüyü tek bir çıkarım çağrısında üretebilir mi? İlk olarak ne kırılır — bağlam, tokenize edici kalitesi yoksa KV önbellek?

3. QK-Norm'u saf Python'da uygulayın. 64 boyutlu bir sorgu ve anahtar verildiğinde, LayerNorm öncesi ve sonrası nokta çarpımını gösterin. Derinlikte büyüklük kontrolü neden önemlidir?

4. Chameleon Bölüm 2.3'ü okuyun, QK-Norm olmadan 34B'de gözlenen tam başarısızlık modunu açıklayın. "Norm patlaması" imzası neydi?

5. Çözümleyiciyi, yalnızca metin istemi verildiğinde karmaşık-modaliteli yanıt üretecek şekilde genişletin. Eğitim verisi dağılımı %60 metin-önce / %40 görüntü-önce verildiğinde modelin ne sıklıkla görüntü-önce vs metin-önce seçtiğini ölçün.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Erken birleşme (Early fusion) | "Birleşik token'lar" | Görüntüler baştan itibaren transformernın sözlüğünü paylaşan disket token'lara dönüştürülür |
| VQ-VAE | "Görüntü tokenize edici" | Görüntüleri transformer'ın tahmin edebileceği tamsayı indekslerine haritalayan CNN + ViT + sözlük |
| Paylaşımlı sözlük | "Tek sözlük" | Metin + görüntü + modalite ayraçlarını kapsayan tek bir token ID uzayı |
| QK-Norm | "Dikkat kararlaştırıcı" | Sorgu ve anahtara nokta çarpımı öncesi uygulanan LayerNorm, norm patlamasını önler |
| Karmaşık-modaliteli üretim | "Metin + görüntü çıkışı" | Tek bir geçişte aralıklı metin ve görüntü token'ları üreten çıkarım |
| Sözlük boyutu | "K girdi" | VQ-VAE'nin nicelleştirebileceği disket vektör sayısı; sıkıştırma ile hassasiyet arasında takas |
| Tokenize edici tavanı | "Yeniden oluşturma sınırı" | VQ token'larının çözelbildiği en iyi PSNR; modelin görüntü kalitesini sınırlar |

## İleri Okuma

- [Chameleon Ekibi — Chameleon: Karmaşık-Modaliteli Erken-Birleşme Temel Modelleri (arXiv:2405.09818)](https://arxiv.org/abs/2405.09818)
- [Aghajanyan ve diğerleri — CM3 (arXiv:2201.07520)](https://arxiv.org/abs/2201.07520)
- [Yu ve diğerleri — CM3Leon (arXiv:2309.02591)](https://arxiv.org/abs/2309.02591)
- [Zhan ve diğerleri — AnyGPT (arXiv:2402.12226)](https://arxiv.org/abs/2402.12226)
- [Adept — Fuyu-8B blogu (adept.ai)](https://www.adept.ai/blog/fuyu-8b)
