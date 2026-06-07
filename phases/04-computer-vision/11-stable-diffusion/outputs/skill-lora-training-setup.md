---
name: skill-lora-training-setup
description: Altyazılar, rank, toplu iş boyutu ve öğrenme hızı dahil özel bir veri kümesi için tam bir LoRA eğitim yapılandırması yazın
version: 1.0.0
phase: 4
lesson: 11
tags: [bilgisayarlı-gör, kararlı-difüzyon, lora, ince-ayar]
---

# LoRA Eğitim Kurulumu

İnce ayar niyetinin açıklamasını, `diffusers` veya `kohya_ss`'ye geçmeye hazır somut bir eğitim yapılandırmasına dönüştürün.

## Ne zaman kullanılır

- Bir özne (kişi, nesne, karakter), bir stil (sanatçı, marka) veya bir kavram (poz, aydınlatma) için LoRA eğitirken.
- Mevcut bir LoRA'yı daha fazla veriyle genişletirken.
- Çıktısı eğitim görüntülerini yetersiz veya aşırı uyum yapan bir LoRA çalıştırmasını ayıklarken.

## Girdiler

- `purpose`: subject | style | concept
- `num_images`: kaç eğitim görüntüsü mevcut
- `base_model`: SD 1.5 | SDXL | SD3 | FLUX
- `gpu_vram_gb`: 8 | 12 | 16 | 24 | 48+
- `caption_source`: manual | BLIP2-generated | dataset-native

## Rank seçici

| Amaç | Rank | Alpha |
|---------|------|-------|
| Özne | 8-16 | rank |
| Stil | 16-32 | rank * 2 |
| Kavram | 32-64 | rank |

Daha yüksek rank = daha fazla kapasite, küçük veri kümelerinde daha fazla aşırı uyum riski. Alpha, LoRA'nın etki gücünü ölçekler; `alpha == rank` güvenli varsayılandır. Stiller belgelenmiş istisnadır: `alpha == rank * 2`, stili çok sert pişirme riski pahasına daha güçlü bir stil itişi verir — yalnızca özne aslına uygunluğu amaç olmadığında kullanın.

## Eğitim adım hedefi

- 5-20 görüntülü `subject`: 500-1500 adım.
- 30-100 görüntülü `style`: 1500-4000 adım.
- 100+ görüntülü `concept`: 4000-10000 adım.

Aşırıya kaçmanın bedeli ağırdır — eğitim görüntülerini ezberlemiş bir LoRA genelleyemez.

## Öğrenme hızı

- Metin kodlayıcı LoRA: SD 1.5 için `1e-4`, SDXL için `5e-5`.
- U-Net LoRA: SD 1.5 için `1e-4`, SDXL için `1e-4`.
- FLUX / SD3: transformer için `5e-5`, metin kodlayıcılar genellikle dondurulur.
- `num_images < 15` (subject) olduğunda veya 3000'den fazla adım eğitirken LR'yi yarıya indirin; küçük veri kümeleri ve uzun çalıştırmalar ikisi de daha yumuşak bir güncellemeden yararlanır.

## Takvim

- `cosine_with_warmup` (varsayılan): ilk %5-10 adımda ısınma, ardından kosinüs azalma. `steps >= 1000` olduğunda kullanın; azalma kuyruğu daha keskin son örnekler verir.
- `constant`: yalnızca çok kısa çalıştırmalar (`steps < 500`) için veya yeniden tavlama yapmadan mevcut öğrenilmiş özellikleri korumak istediğinizde önceki bir LoRA'yı sürdürürken.

## Altyazı formatı

- Özne: her altyazının başına benzersiz bir tetikleyici token ("myperson") ekleyin. Mevcut kavramların üzerine yazmaması için tetikleyici token'ı nadir tutun. Gerçek kelimelerden ve yaygın isimlerden kaçının.
- Stil: her altyazının sonuna benzersiz bir stil etiketi ekleyin ("...in mystyle style"). Etiketin kendisini nadir bir tetikleyici token olarak ele alın — zaten gerçek bir kavrama eşlenen `impressionism` değil, `mystyle`.
- Kavram: kavramı her altyazıda tanımlayın; tetikleyici token yok. Kavramın kendisi (örn. "low-angle shot") çapadır.

## Çıktı yapılandırması

```yaml
model:
 base: <base_model HF kimliği>
 precision: fp16 | bf16

lora:
 rank: <int>
 alpha: <int>
 targets: unet.cross_attention # ve/veya unet.to_q, to_k, to_v, to_out

training:
 steps: <int>
 batch_size: <int, gpu_vram_gb'ye göre ayarlı>
 grad_accum: <int, genellikle >=16 GB'de 1, <=12 GB'de 4>
 learning_rate: <float>
 optimizer: AdamW8bit | AdamW
 scheduler: cosine_with_warmup | constant
 warmup_steps: <int>
 save_every: <int>

data:
 images_dir: <yol>
 caption_source: <manual | BLIP2 | native>
 trigger_token: <purpose==subject ise dize>
 resolution: <SD 1.5 için 512, SDXL için 1024>
 aspect_ratio_bucketing: true
 augmentation:
 flip: true
 color_jitter: false

validation:
 prompts:
 - "<trigger> ...test prompt..."
 - "<trigger> in a different scene"
 every_steps: 250
```

## Rapor

```
[lora setup]
 purpose: <subject|style|concept>
 base: <model>
 rank: <int>
 steps: <int>
 batch: <int> grad_accum: <int>
 lr: <float>
 vram est.: <float> GB
```

## Kurallar

- Asla `rank > 64` önerme; bunun üzerinde LoRA mini bir ince ayar haline gelir ve "adaptör" doğasını kaybeder.
- `num_images < 5` için, güçlü şekilde uyarın — 1-3 görüntüdeki kimlik LoRA'ları her zaman aşırı uyar.
- `gpu_vram_gb < 12` için, AdamW8bit ve gradyan kontrol noktası (gradient checkpointing) gerektir.
- `base_model == FLUX` ve `gpu_vram_gb < 24` ise, `schnell` varyantına yönlendirin ve eğitimin daha yavaş olduğunu not edin.
- Doğrulama istemlerini asla atlamayın; örnek ızgaraları olmayan bir LoRA'yı değerlendirmek imkansızdır.
