# Inpainting, Outpainting & Görsel Düzenleme

> Metinden-görsel yeni şeyler üretir. Inpainting eski olanları düzeltir. Üretimde fatura kesilebilir görsel işinin %70'i düzenlemedir — arka planı değiştirme, logoyu kaldırma, tuvali genişletme, bir eli yeniden oluşturma. Inpainting, diffüzyonun kendini kanıtladığı yerdir.

**Tür:** İnşa Et
**Diller:** Python
**Ön koşullar:** Faz 8 · 07 (Latent Diffusion), Faz 8 · 08 (ControlNet & LoRA)
**Süre:** ~75 dakika

## Problem

Bir müşteri arka planındaki dikkat dağıtıcı tabelayla birlikte mükemmel bir ürün fotoğrafı gönderir. Tabelayı silmek ve geri kalan her şeyi piksel olarak aynı bırakmak istersiniz. Metinden-görseli sıfırdan çalıştıramazsınız — sonuç farklı renk, farklı aydınlatma, farklı ürün açısı olacaktır. *Yalnızca* maskelenmiş bölgeyi yeniden oluşturmak ve yeniden oluşturmanın çevredeki bağlama saygı göstermesini istersiniz.

İşte bu inpainting. Varyantlar:

- **Inpainting.** Maskenin içinde yeniden oluşturma, dışındaki pikselleri koruma.
- **Outpainting.** Maskenin dışında (veya tuvalin ötesinde) yeniden oluşturma, içindekileri koruma.
- **Görsel düzenleme.** Tüm görseli yeniden oluştur ama orijinale yapısal veya anlamsal sadakati koru (SDEdit, InstructPix2Pix).

2026'daki her diffüzyon pipeline'ı bir inpainting modu sunar. Flux.1-Fill, Stable Diffusion Inpaint, SDXL-Inpaint, DALL-E 3 Edit. Aynı ilkede çalışırlar.

## Kavram

![Inpainting: bağlam-koruyucu yeniden enjeksiyonla mask-farklı gürültü temizleme](../assets/inpainting.svg)

### Naif yaklaşım (ve neden yanlış)

Maskeli standart metinden-görseli çalıştırın. Her örnekleme adımında, gürültülü latent'ın masksız bölgesini ileri diffüze edilmiş temiz görselle değiştirin. Kötü çalışır… Sınır bozulmaları (boundary artifacts) sızar, çünkü model maskelenmiş bölgede ne olduğu hakkında bilgiye sahip değildir.

### Doğru inpainting modeli

9 yerine 4 giriş kanalı alan değiştirilmiş bir U-Net eğitin:

```
input = concat([ noisy_latent (4ch), encoded_image (4ch), mask (1ch) ], dim=channel)
```

#### Açıklama

Ek kanallar, VAE-kodlanmış kaynak görselin bir kopyası ve tek kanallı bir maskedir. Eğitim sırasında görselin rastgele bölgelerini maskeler ve modeli yalnızca maskelenmiş bölgeyi temizlerken masksız bölgeyi temiz bir koşullandırma sinyali olarak vererek eğitirsiniz. Çıkarım sırasında model, maskelenmiş bölgenin etrafında ne olduğunu "görebilir" ve tutarlı tamamlamalar üretir.

SD-Inpaint, SDXL-Inpaint, Flux-Fill tümü bu 9 kanallı (veya eşdeğeri) girdiyi kullanır. Diffusers `StableDiffusionInpaintPipeline`, `FluxFillPipeline`.

### SDEdit (Meng ve ark., 2022) — ücretsiz düzenleme

Kaynak görseldeki gürültüyü ara bir `t`'ye kadar ekleyin, ardından yeni bir prompt ile `t`'den 0'a kadar ters zinciri çalıştırın. Yeniden eğitim gerekmez. Başlangıç `t`'nin seçimi, sadakat ile yaratıcı özgürlük arasında bir ödünleşimdir:

- `t/T = 0.3` → kaynağıyla neredeyse özdeş, küçük stilistik değişiklikler
- `t/T = 0.6` | orta düzey düzenlemeler, kaba yapıyı korur
- `t/T = 0.9` → neredeyse gürültüden üretilmiş, minimal kaynak koruma

### InstructPix2Pix (Brooks ve ark., 2023)

Bir diffüzyon modelini `(input_image, instruction, output_image)` üçlüleri üzerinde fine-tune edin. Çıkarım hem giriş görseli hem de bir metin talimatı ("gün batımı yap", "bir ejderha ekle") ile koşullandırılır. İki CFG ölçeği: görüntü ölçeği ve metin ölçeği.

### RePaint (Lugmayr ve ark., 2022)

Standart koşulsuz bir diffüzyon modelini koruyun. Her ters adımda yeniden örnekleme yapın — zaman zaman daha gürültülü bir duruma atlayın ve yeniden oluşturun. Sınır bozulmalarını önler. Eğitilmiş bir inpainting modeliniz olmadığında kullanılır.

## İnşa Et

`code/main.py`, 5 boyutlu veri üzerinde oyuncak bir 1-D inpainting şeması uygular. Her örneğin iki kümeden birinden gelen 5 float olduğu 5-D karma veri üzerinde bir DDPM eğitiriz. Çıkarım sırasında 5 boyutun 2'sini "maskeleriz", her adımda masksız üçünün gürültülü-ileri versiyonunu enjekte ederiz ve yalnızca maskelenmiş boyutları yeniden oluştururuz.

### Adım 1: 5-D DDPM verisi

```python
def sample_data(rng):
    cluster = rng.choice([0, 1])
    center = [-1.0] * 5 if cluster == 0 else [1.0] * 5
    return [c + rng.gauss(0, 0.2) for c in center], cluster
```

#### Açıklama

Her örnek, 5 boyutlu bir vektördür ve iki kümeden birine aittir. Bu, basit bir veri akışı sağlar.

### Adım 2: tüm 5 boyutta gürültü temizleyiciyi eğitin

Standart DDPM. Ağ, 5-D gürültülü girdi için 5-D gürültü tahmini üretir.

### Adım 3: çıkarımda mask-farklı ters işlem

```python
def inpaint_step(x_t, mask, clean_image, alpha_bars, t, rng):
    # replace unmasked dims with a freshly noised version of the clean source
    a_bar = alpha_bars[t]
    for i in range(len(x_t)):
        if not mask[i]:
            x_t[i] = math.sqrt(a_bar) * clean_image[i] + math.sqrt(1 - a_bar) * rng.gauss(0, 1)
    # ...then run the normal reverse step on x_t
```

#### Açıklama

Bu naif yaklaşımdır ve oyuncak 1-D veri üzerinde çalışır. Gerçek görsel inpainting'i 9 kanallı girdiyi kullanır, çünkü doku tutarlılığı çok daha önemlidir.

### Adım 4: outpainting

Outpainting, maskesi ters çevrilmiş inpaintingdir: yeni (önceki var olmayan) tuvali maskeler, geri kalanını orijinelle doldurursunuz. Aynı eğitim hedefi.

## Tuzaklar

- **Dikişler.** Naif yaklaşım, gradyan bilgisi maskenin üzerinden geçemediği için görünür sınırlar bırakır. Çözüm: maskeyi 8-16 piksel genişletin veya düzgün bir inpainting modeli kullanın.
- **Maske sızıntısı.** Koşullandırma görselinin masksız bölgesi düşük kaliteli veya gürültülüyse, maskenin içindeki üretimi kirletir. Hafifçe gürültü temizleyin veya bulanıklaştırın.
- **CFG mask boyutuyla etkileşir.** Küçük bir maske üzerinde yüksek CFG = doymuş yama. Küçük düzenlemeler için CFG'yi azaltın.
- **SDEdit sadakat kayalığı.** `t/T = 0.5`'ten `t/T = 0.6`'ya geçiş, konunun kimliğini kaybedebilir. Tarama yapın ve checkpoint alın.
- **Prompt uyumsuzluğu.** Prompt *tüm* görseli tanımlamalıdır, yalnızca yeni içeriği değil. "Bir koltuğa oturan bir kedi" değil "bir kedi".

## Kullan

| Görev | Pipeline |
|-------|----------|
| Nesne kaldırma, küçük maske | SD-Inpaint veya Flux-Fill, standart prompt |
| Gökyüzü değiştirme | SD-Inpaint + "gün batımında mavi gökyüzü" |
| Tuvali genişletme | SDXL outpaint modu (8px feather) veya outpaint maskeli Flux-Fill |
| El / yüz yeniden oluşturma | Konuyu yeniden tanımlayan prompt + ControlNet-Openpose ile SD-Inpaint |
| Bir bölgenin stilini değiştirme | Maskelenmiş bölge üzerinde `t/T=0.5` ile SDEdit |
| "Gün batımı yap" | InstructPix2Pix veya Flux-Kontext |
| Arka plan değiştirme | SAM maskesi → SD-Inpaint |
| Ultra yüksek sadakat | En zor durumlar için Flux-Fill veya GPT-Image (barındırılan) |

SAM (Meta'nın Segment Anything'i, 2023) + diffüzyon inpaint, 2026 arka plan kaldırma pipeline'ıdır. SAM 2 (2024) video üzerinde çalışır.

## Teslim Et

`outputs/skill-editing-pipeline.md` dosyasını kaydedin. Skill orijinal bir görsel + düzenleme açıklaması + isteğe bağlı maske (veya SAM promptu) alır ve çıktı olarak şunları verir: mask oluşturma yaklaşımı, taban model, CFG ölçekleri (görsel + metin), SDEdit-t veya inpainting modu ve QA kontrol listesi.

## Alıştırmalar

1. **Kolay.** `code/main.py`'de boyutların maskelenme oranını 0.2'den 0.8'e değiştirin. Hangi oranda inpaint kalitesi (maskelenmiş boyutlardaki artık değer) koşulsuz üretime eşit olur?
2. **Orta.** RePaint uygulayın: her 10. ters adımda 5 adım geri atlayın (gürültü ekleyin) ve yeniden temizleyin. Sınır artık değerini azaltıp azaltmadığını ölçün.
3. **Zor.** Hugging Face diffusers ile karşılaştırın: SD 1.5 Inpaint + ControlNet-Openpose ile Flux.1-Fill'i 20 yüz yeniden oluşturma görevinde. Poz uyumunu ve kimlik korumasını ayrı ayrı puanlayın.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Inpainting | "Deliği doldur" | Maskenin içinde yeniden oluşturma; dışındaki pikselleri koruma. |
| Outpainting | "Tuvali genişlet" | Tuvalin dışında yeniden oluşturma; içindekileri koruma. |
| 9 kanallı U-Net | "Doğru inpainting modeli" | `noisy \| encoded-source \| mask` girdisine sahip U-Net. |
| SDEdit | "Gürültü seviyeli img2img" | Zamana `t` kadar gürültü, yeni prompt ile temizleme. |
| InstructPix2Pix | "Yalnızca metinle düzenleme" | (görsel, talimat, çıktı) üçlüleri üzerinde fine-tune edilmiş diffüzyon. |
| RePaint | "Yeniden eğitim yok" | Dikişleri azaltmak için ters işlem sırasında periyodik olarak yeniden gürültülendirme. |
| SAM | "Segment Anything" | Tıklamalar veya kutularla maske üreteci; inpaint ile eşleştirilir. |
| Flux-Kontext | "Bağlamla düzenleme" | Düzenlemeler için bir referans görsel + talimat kabul eden Flux varyantı. |

## Üretim notu: düzenleme pipeline'ları gecikmeye duyarlı

Bir görseli düzenleyen kullanıcılar 5 saniyenin altında tur süresi bekler. 1024²'ünde 30 adımlı SDXL-Inpaint, L4 üzerinde 3-4 saniye, artı SAM maskesi oluşturma (~200 ms) ve VAE encode/decode (~500 ms toplam). Üretim çerçevesinde bu, throughput-bound değil TTFT-bound'tur — batch 1, düşük eşzamanlılık (concurrency), her aşamayı en aza indirin:

- **SAM-H yavaştır.** SAM-H 1024²'ünde ~200 ms; SAM-ViT-B kalite kaybıyla ~40 ms. SAM 2 (video) zamansal yük ekler; tek görsel düzenlemeler için kullanmayın.
- **Mümkünse encode'dan kaçının.** `pipe.image_processor.preprocess(img)` latent'lere kodlar. Önceki üretimin latent'lerine sahipseniz (yinelemeli düzenleme arayüzlerinde tipik), doğrudan `latents=...` ile ileterek bir VAE encode'undan kaçınırınız.
- **Maske genişletme throughput için de önemlidir.** Küçük bir maske, U-Net ileri geçişinin çoğunun boşa harcanması demektir (masksız pikseller zaten kısıtlanmıştır). `diffusers`' `StableDiffusionInpaintPipeline` yine de tüm U-Net'i çalıştırır; yalnızca 9 kanallı doğru-inpaint varyantları maskeli hesaplamadan yararlanır.
- **Flux-Kontext 2025'in cevabıdır.** `(source_image, instruction)` üzerinde tek ileri geçiş — ayrı maske yok, SDEdit gürültü taraması yok. H100 üzerinde ~1.5 s'de bir düzenleme teslim eder. Mimari ders: aşamaları çökertin.

## Daha Fazla Kaynak

- [Lugmayr ve ark. (2022). RePaint: Inpainting using Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2201.09865) — eğitimsiz inpainting.
- [Meng ve ark. (2022). SDEdit: Guided Image Synthesis and Editing with Stochastic Differential Equations](https://arxiv.org/abs/2108.01073) — SDEdit.
- [Brooks, Holynski, Efros (2023). InstructPix2Pix](https://arxiv.org/abs/2211.09800) — metin talimatlı düzenleme.
- [Kirillov ve ark. (2023). Segment Anything](https://arxiv.org/abs/2304.02643) — SAM, maske kaynağı.
- [Ravi ve ark. (2024). SAM 2: Segment Anything in Images and Videos](https://arxiv.org/abs/2408.00714) — video SAM.
- [Hertz ve ark. (2022). Prompt-to-Prompt Image Editing with Cross-Attention Control](https://arxiv.org/abs/2208.01626) — attention düzeyinde düzenleme.
- [Black Forest Labs (2024). Flux.1-Fill and Flux.1-Kontext](https://blackforestlabs.ai/flux-1-tools/) — 2024 araçları.
