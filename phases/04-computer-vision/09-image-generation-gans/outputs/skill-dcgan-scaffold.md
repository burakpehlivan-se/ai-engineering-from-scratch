---
name: skill-dcgan-scaffold
description: z_dim, image_size ve num_channels'tan tam bir DCGAN iskele (scaffold) yazın, eğitim döngüsü ve örnek kaydedici dahil
version: 1.0.0
phase: 4
lesson: 9
tags: [bilgisayarlı-gör, gan, dcgan, iskele]
---

# DCGAN İskelesi

Üç parametre verildiğinde, hedef görüntü çözünürlüğü için mimarisi doğru boyutlandırılmış, çalıştırılabilir bir DCGAN proje iskeleti yayın.

## Ne zaman kullanılır

- Küçük bir veri kümesinde yeni bir üretken deneye başlarken.
- Çalışan minimal bir örnekle DCGAN temellerini öğretirken.
- Koşullu GAN'ları prototiplerken (etiket enjeksiyonu aynı iskele içinde gerçekleşir).

## Girdiler

- `image_size`: 32, 64, 128'den biri (iki kuvveti olmalı).
- `num_channels`: 1 (gri tonlama) veya 3 (RGB).
- `z_dim`: tipik olarak 64 veya 128.
- `with_spectral_norm`: yes | no; varsayılan yes.

## Mimari boyutlandırma

G'deki transpoze evrişim bloklarının ve D'deki adımlı evrişim bloklarının sayısı `image_size`'a bağlıdır:

| image_size | G blokları | D blokları |
|------------|----------|----------|
| 32         | 4        | 4        |
| 64         | 5        | 5        |
| 128        | 6        | 6        |

Her ek blok, uzamsal boyutu ikiye katlar (G) veya yarıya indirir (D). Özellik sayısı 32'den başlar ve `feat_base * 2^block_index` ile ölçeklenir.

## Çıktı dosyaları

- `model.py` — Üreteç + Ayırıcı sınıfları
- `train.py` — eğitim döngüsü, kayıp, optimize edici kurulumu
- `sample.py` — örnek ızgara kaydedici
- `config.json` — hiperparametreler
- `README.md` — 10 satırlık hızlı başlangıç

## Rapor

```
[scaffold]
  image_size:       <int>
  num_channels:     <int>
  z_dim:            <int>
  spectral_norm:    yes | no

[arch]
  G blocks:         <N>, channels: [list]
  D blocks:         <N>, channels: [list]
  G params (est):   <N>
  D params (est):   <N>

[training defaults]
  optimizer:   Adam(lr=2e-4, betas=(0.5, 0.999))
  batch_size:  64
  epochs:      50
  sample_every: 1 epoch

[files written]
  - model.py
  - train.py
  - sample.py
  - config.json
  - README.md
```

## Kurallar

- Her zaman G'nin çıktısında `nn.Tanh()` kullanın ve eğitim sırasında verileri [-1, 1] aralığına ölçekleyin.
- D'de her zaman `LeakyReLU(0.2)` kullanın.
- `with_spectral_norm == yes` olduğunda, D'deki her evrişimi `spectral_norm()` ile sarın ve D'den BatchNorm'u kaldırın. BatchNorm'u G'de tutun.
- image_size > 128 için asla iskele yayınlamayın — DCGAN bundan büyük kararsızlaşır; kullanıcıyı StyleGAN veya bir difüzyon modeline yönlendirin.
