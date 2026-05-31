# ControlNet, LoRA & Conditioning

> Tek başına metin beceriksiz bir kontrol sinyalidir. ControlNet, önceden eğitilmiş bir diffüzyon modelini klonlamanızı ve onu bir derinlik haritası (depth map), poz iskeleti (pose skeleton), çizim veya kenar görüntüsüyle yönlendirmenizi sağlar. LoRA, 2 milyar parametreli bir modeli yalnızca 10 milyon parametre eğiterek fine-tune etmenizi sağlar. Birlikte, Stable Diffusion'ı bir oyuncaktan 2026'nın her ajansında teslim edilen görüntü pipeline'ına dönüştürdüler.

**Tür:** İnşa Et
**Diller:** Python
**Ön koşullar:** Faz 8 · 07 (Latent Diffusion), Faz 10 (Sıfırdan LLM'ler — LoRA temeli için)
**Süre:** ~75 dakika

## Problem

"Bir köpekle meşgul bir sokakta yürüyen kırmızı elbiseli bir kadın" gibi bir prompt, modele köpeğin *nerede*, kadının *hangi pozda* veya sokağın *perspektifi* hakkında hiçbir bilgi vermez. Bir görseli tanımlamak için gerekenlerin yaklaşık %10'unu metin sabitler. Geri kalanı görseldir ve kelimelerle verimli bir şekilde tanımlanamaz.

Her sinyal için (poz, derinlik, canny, segmentasyondan) sıfırdan yeni bir koşullu model eğitmek maliyet olarak karşılanamaz. 2.6B parametreli SDXL omurgasını donmuş tutmak, koşullandırmayı okuyan küçük bir yan ağ eklemek ve omuzuradaki ara özellikleri hafifçe kaydırmak istersiniz. İşte bu ControlNet'tir.

Ayrıca modeli tamamen yeniden eğitmeden yeni kavramları (yüzünüz, ürününüz, stiliniz) öğretmek istersiniz. 100 kat daha küçük bir delta istersiniz. İşte bu LoRA — mevcut attention ağırlıklarına takılan düşük dereceli adaptörlerdir (low-rank adapters).

ControlNet + LoRA + metin = 2026 uygulayıcısının araç seti. Üretim görüntü pipeline'larının çoğu, bir SDXL / SD3 / Flux tabanı üzerine 2-5 LoRA, 1-3 ControlNet ve bir IP-Adapter katmanları ekler.

## Kavram

![ControlNet encoder'ı klonlar; LoRA düşük dereceli delta'lar ekler](../assets/controlnet-lora.svg)

### ControlNet (Zhang ve ark., 2023)

Önceden eğitilmiş bir SD'yi alın. U-Net'in encoder yarısını *klonlayın*. Orijinali dondurun. Klonu, ek bir koşullandırma girdisi (kenarlar, derinlik, poz) kabul edecek şekilde eğitin. Klonu orijinalin decoder yarısına *sıfır-evrişimli* (zero-convolution) skip bağlantılarıyla geri bağlayın (1×1 conv'lar sıfırla başlatılmış — başlangıçta no-op, bir delta öğrenir).

```
SD U-Net decoder:   ... ← orig_enc_features + zero_conv(controlnet_enc(condition))
```

#### Açıklama

Sıfır-evrişim başlangıcı, ControlNet'in kimlik (identity) olarak başlaması anlamına gelir — eğitimin öncesinde bile zarar vermez. 1M (prompt, koşul, görsel) üçlüsüyle standart diffüzyon kaybı üzerinde eğitilir.

Modalite başına ControlNet'ler küçük yan modeller olarak sunulur (SDXL için ~360M, SD 1.5 için ~70M). Çıkarım sırasında bunları birleştirebilirsiniz:

```
features += weight_a * control_a(depth) + weight_b * control_b(pose)
```

### LoRA (Hu ve ark., 2021)

Modeldeki herhangi bir lineer katman `W ∈ R^{d×d}` için `W`'yi dondurun ve düşük dereceli bir delta ekleyin:

```
W' = W + ΔW,  ΔW = B @ A,  A ∈ R^{r×d},  B ∈ R^{d×r}
```

#### Açıklama

Burada `r << d`. Attention için 4-16 arası derece (rank) standarttır, ağır fine-tune'lar için 64-128. Yeni parametre sayısı: `d²` yerine `2 · d · r`. `d=640`, `r=16` olan SDXL attention için: adaptör başına 410k yerine 20k parametre — 20 kat azalma. Tüm model genelinde: LoRA genellikle 20-200MB, taban 5GB'a kıyasla.

Çıkarım sırasında LoRA'yı ölçekleyebilirsiniz: `W' = W + α · B @ A`. `α = 0.5-1.5` normaldir. Birden fazla LoRA toplanarak (additif) istiflenir (sıradan uyarı: doğrusal olmayan biçimde etkileşirler).

### IP-Adapter (Ye ve ark., 2023)

Bir *görseli* koşullandırma olarak (metinle birlikte) kabul eden küçük bir adaptör. CLIP görüntü encoder'ını kullanarak görüntü token'ları üretir, bunları metin token'larıyla birlikte cross-attention'a enjekte eder. Taban model başına ~20MB. LoRA olmadan "bu referansın stilinde bir görsel üret" yapmanıza olanak tanır.

## Birleştirilebilirlik matrisi

| Araç | Neyi kontrol eder | Boyut | Ne zaman kullanılır |
|------|-------------------|-------|---------------------|
| ControlNet | Uzamsal yapı (poz, derinlik, kenarlar) | 70-360MB | Kesin yerleşim, kompozisyon |
| LoRA | Stil, konu, kavram | 20-200MB | Kişiselleştirme, stil |
| IP-Adapter | Referans görselinden stil veya konu | 20MB | Metin tanımlayamadığı görünüm |
| Textual Inversion | Tek kavram yeni bir token olarak | 10KB | Eski yöntem, büyük ölçüde LoRA ile değiştirildi |
| DreamBooth | Bir konu üzerinde tam fine-tune | 2-5GB | Güçlü kimlik, yüksek hesaplama |
| T2I-Adapter | Daha hafif ControlNet alternatifi | 70MB | Kenar cihazları, çıkarım bütçesi |

ControlNet ≈ uzamsal. LoRA ≈ anlamsal. Her ikisini de kullanın.

## İnşa Et

`code/main.py`, iki mekanizmayı 1-D üzerinde simüle eder:

1. **LoRA.** Önceden eğitilmiş lineer katman `W`. Dondurun. Hedef lineer katmanla eşleşecek şekilde düşük dereceli `B @ A` eğitin. `r = 1`'in rank-1 düzeltmeyi tam olarak öğrenmek için yeterli olduğunu gösterin.

2. **ControlNet-lite.** "Dondurulmuş taban" tahmincisi ve ek bir sinyal okuyan "yan ağ". Yan ağın çıktısı sıfırla başlatılabilir bir skaler tarafından kontrol edilir (bizim sıfır-evrişim versiyonumuz). Eğitin ve kapının (gate) nasıl açıldığını izleyin.

### Adım 1: LoRA matematiği

```python
def lora(W, A, B, x, alpha=1.0):
    # W is frozen; A, B are the trainable low-rank factors.
    return [W[i][j] * x[j] for i, j in ...] + alpha * (B @ (A @ x))
```

#### Açıklama

`W` dondurulmuş; `A`, `B` eğitilebilir düşük dereceli çarpanlardır. `alpha` LoRA'nın gücünü kontrol eder.

### Adım 2: sıfır-başlangıçlı yan ağ

```python
side_out = control_net(x, condition)
gated = gate * side_out  # gate initialized to 0
h = base(x) + gated
```

#### Açıklama

0. adımda çıktı tabanla özdeştir. Erken eğitim `gate`'i yavaşça günceller — felaketli sapma (catastrophic drift) olmaz.

## Tuzaklar

- **LoRA'ları aşırı ölçeklendirme.** `α = 2` veya `α = 3`, aşırı stilize / bozuk çıktılar üreten yaygın bir "güçlendir" numarasıdır. `α ≤ 1.5` tutun.
- **ControlNet ağırlık çatışması.** 1.0 ağırlığında bir Pose ControlNet ve 1.0 ağırlığında bir Depth ControlNet kullanmak genellikle aşırıya kaçar. Ağırlıkların toplamı ≈ 1.0 güvenli bir varsayımdır.
- **Yanlış taban üzerinde LoRA.** SDXL LoRA'ları, attention boyutları eşleşmediği için SD 1.5 üzerinde sessizce no-op olur. Diffusers 0.30+ uyarı verecektir.
- **Textual Inversion sapması.** Bir checkpoint üzerinde eğitilmiş token'lar başka bir checkpoint üzerinde ciddi şekilde sapar. LoRA daha taşınabilir.
- **LoRA ağırlık birleştirme ve depolama.** LoRA'yı daha hızlı çıkarım için taban model ağırlıklarına dahil edebilirsiniz (çalışma zamanı ekleme gerekmez), ancak `α`'yı çalışma zamanında ölçekleme yeteneğini kaybedersiniz. Her iki sürümü de saklayın.

## Kullan

| Hedef | 2026 pipeline'ı |
|-------|-----------------|
| Bir markanın sanat stilini yeniden üretmek | rank 32'de ~30 özenle seçilmiş görsel üzerinde eğitilmiş LoRA |
| Yüzümü üretilmiş bir görselde kullanmak | DreamBooth veya LoRA + IP-Adapter-FaceID |
| Belirli poz + prompt | ControlNet-Openpose + SDXL + metin |
| Derinlik-aware kompozisyon | ControlNet-Depth + SD3 |
| Referans + prompt | IP-Adapter + metin |
| Kesin yerleşim | ControlNet-Scribble veya ControlNet-Canny |
| Arka plan değiştirme | ControlNet-Seg + Inpainting (Ders 09) |
| Hızlı 1-adımlı stil | SDXL-Turbo üzerinde LCM-LoRA |

## Teslim Et

`outputs/skill-sd-toolkit-composer.md` dosyasını kaydedin. Skill bir görev (girdi varlıkları: prompt, isteğe bağlı referans görsel, isteğe bağlı poz, isteğe bağlı derinlik, isteğe bağlı çizim) alır ve araç stack'ini, ağırlıkları ve tekrarlanabilir bir seed protokolünü çıktı olarak verir.

## Alıştırmalar

1. **Kolay.** `code/main.py`'de LoRA rankını `r = 1`'den `r = 4`'e değiştirin. Hangi rankta LoRA rank-2 hedef delta'sıyla tam olarak eşleşir?
2. **Orta.** İki farklı hedef dönüşüm üzerinde iki ayrı LoRA eğitin. Birlikte yükleyin ve toplanarak (additif) etkileşimlerini gösterin. Etkileşim ne zaman doğrusallığı bozar?
3. **Zor.** Diffusers ile istifleyin: SDXL-base + Canny-ControlNet (ağırlık 0.8) + stil LoRA (α 0.8) + IP-Adapter (ağırlık 0.6). Stack ağırlıkları değişirken FID-vs-prompt-uyumu (prompt adherence) ödünleşimini ölçün.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| ControlNet | "Uzamsal kontrol" | Klonlanmış encoder + sıfır-evrişim skip'leri; koşullandırma görselini okur. |
| Zero convolution | "Kimlik olarak başlar" | Sıfırla başlatılmış 1×1 conv; ControlNet no-op olarak başlar. |
| LoRA | "Düşük dereceli adaptör" | `W + B @ A`, `r << d`; tam fine-tune'dan 100 kat daha az parametre. |
| rank r | "Ayar düğmesi" | LoRA sıkıştırması; 4-16 tipik, ağır kişiselleştirme için 64+. |
| α | "LoRA gücü" | LoRA delta'sının çalışma zamanı ölçeklendirmesi. |
| IP-Adapter | "Referans görseli" | CLIP-görüntü token'ları aracılığıyla küçük görüntü-koşullandırma adaptörü. |
| DreamBooth | "Tam konu fine-tune'u" | ~30 görselde bir konu üzerinde tüm modeli eğitmek. |
| Textual Inversion | "Yeni token" | Yalnızca yeni bir kelime embedding'i öğrenmek; eski, büyük ölçüde LoRA ile değiştirildi |

## Üretim notu: LoRA takasları, ControlNet şeritleri, çok kiracılı hizmet

Gerçek bir metinden-görsel SaaS'u, aynı checkpoint üzerinde yüzlerce LoRA ve bir düzine ControlNet sunar. Hizmet sorunu, LLM çok kiracılığına (multi-tenancy) çok benzer (üretim literatürü LLM durumunu continuous batching ve LoRAX / S-LoRA altında ele alır):

- **LoRA'ları sıcak olarak değiştirin, birleştirmeyin.** `W' = W + α·B·A`'yı tabana birleştirmek adım başına ~%3-5 daha hızlı çıkarım sağlar, ancak `α`'yı ve tabanı dondurur. LoRA'ları VRAM'de rank-r delta'ları olarak sıcak tutun; diffusers istek başına aktivasyon için `pipe.load_lora_weights()` + `pipe.set_adapters([...], adapter_weights=[...])` sunar. Değiştirme maliyeti `2 · d · r · katman_sayısı` ağırlığıdır — MB ölçeğinde, saniyenin altında.
- **ControlNet ikinci bir attention şeridi olarak.** Klonlanmış encoder tabanla paralel çalışır. Her biri 1.0 ağırlığında iki ControlNet = adım başına iki ek ileri geçiş, birleşik bir geçiş değil. Batch-size_headroom karesel olarak düşer. Aktif ControlNet başına ~1.5× adım maliyeti için bütçe ayırın.
- **Kantize LoRA'lar da.** Tabanı kantize ettiyseniz (Ders 07, 8GB üzerinde Flux'a bakın), LoRA delta'sı da 8-bit veya 4-bit'e temiz bir şekilde kantize edilir. QLoRA tarzı yükleme, 4-bit Flux tabanı üzerine 5-10 LoRA istiflemenizi belleği patlatmadan sağlar.

Flux'a özgü: Niels'in Flux-on-8GB notebook'u tabanı 4-bit'e kantize eder; bu kantize taban üzerine bir stil LoRA (`pipe.load_lora_weights("user/style-lora")`) `weight_name="pytorch_lora_weights.safetensors"` ile eklemek hala çalışır. 2026'da çoğu SaaS ajansının teslim ettiği reçete budur.

## Daha Fazla Kaynak

- [Zhang, Rao, Agrawala (2023). Adding Conditional Control to Text-to-Image Diffusion Models](https://arxiv.org/abs/2302.05543) — ControlNet.
- [Hu ve ark. (2021). LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) — LoRA (özellikle LLM'ler için; diffüzyona taşınmıştır).
- [Ye ve ark. (2023). IP-Adapter: Text Compatible Image Prompt Adapter](https://arxiv.org/abs/2308.06721) — IP-Adapter.
- [Mou ve ark. (2023). T2I-Adapter: Learning Adapters to Dig Out More Controllable Ability](https://arxiv.org/abs/2302.08453) — ControlNet'in daha hafif alternatifi.
- [Ruiz ve ark. (2023). DreamBooth: Fine Tuning Text-to-Image Diffusion Models for Subject-Driven Generation](https://arxiv.org/abs/2208.12242) — DreamBooth.
- [HuggingFace Diffusers — ControlNet / LoRA / IP-Adapter docs](https://huggingface.co/docs/diffusers/training/controlnet) — referans pipeline'ları.
