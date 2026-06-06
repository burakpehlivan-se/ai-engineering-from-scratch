---
name: skill-image-tensor-inspector
description: Herhangi bir görüntü şeklindeki tensörü veya diziyi inceleyin ve dtype, düzen, aralık ve ham, normalleştirilmiş veya standartlaştırılmış görünüp görünmediğini raporlayın
version: 1.0.0
phase: 4
lesson: 1
tags: [bilgisayarlı-görü, hata-ayıklama, ön-işleme, tensörler]
---

# Görüntü Tensörü Denetçisi

Görüntü işleme hattının (vision pipeline) herhangi bir noktasında, bir görüntü şeklinde diziyi tuttuğunuzda ve tam olarak hangi durumda olduğunu bilmeniz gereken her an için tanısal bir beceri.

## Ne zaman kullanılır

- Önceden eğitilmiş bir model çöp tahminler döndürüyor ve ön işlemeden şüpheleniyorsunuz.
- Bir hattı OpenCV ve torchvision arasında taşıyorsunuz ve kanal sırası belirsiz.
- Birden çok çerçeveden katmanları istifliyorsunuz ve toplu iş ekseni (batch axis) yanlış yerde görünmeye devam ediyor.
- Kaybın `log(num_classes)`'ta takılı kaldığı bir eğitim döngüsünü hata ayıklıyorsunuz.

## Girdiler

- `x`: herhangi bir 2-B, 3-B veya 4-B dizi benzeri (NumPy, PyTorch, JAX).
- İsteğe bağlı `expected`: kontrol edilecek değişmezlerin bir sözlüğü, örn. `{"layout": "CHW", "range": "standardized"}`.

## Adımlar

1. **Backend'i çöz** — `x`'in NumPy, Torch veya JAX olup olmadığını tespit et. Orijinali değiştirmeden inceleme için NumPy'ye dönüştür.

2. **Dereceyi sınıflandır**:
   - derece 2 -> tek kanallı görüntü (H, W).
   - derece 3 -> son eksen 1, 3 veya 4 ise ve diğer ikisinden kesinlikle küçükse `HWC`; aksi halde `CHW`.
   - derece 4 -> eksen 1 {1, 3, 4} kümesindeyse **ve** eksen 2 veya eksen 3, 16'dan büyükse `NCHW`'yi tercih et; aksi halde `NHWC`'yi tercih et. Salt eksen-1 kontrolü, `(3, 4, 224, 3)` gibi küçük görüntülü NHWC toplu işlerini yanlış sınıflandırır.
   - Belirsiz durumları (örn. `(1, 3, 3, 3)`) her zaman `ambiguous` olarak işaretle, tahmin etme; arayanın `expected` sağlamasını iste.

3. **dtype ve aralığı sınıflandır**:
   - `uint8` [0, 255] aralığında -> `raw`.
   - `float*` min >= 0 ve max <= 1.01 -> `normalized`.
   - `float*` min < 0 ve |ortalama| < 0.5 ve 0.5 <= std <= 1.5 -> `standardized`.
   - Başka her şey -> `unusual`, histogramı yazdır.

4. **Kanal başına istatistikler** — kanal başına ortalama ve std raporla. Dizi standartlaştırılmış görünüyorsa ImageNet ortalama/std'siyle karşılaştır ve bir eşleşme güveni sun.

5. **Tam bu blokta raporla**:

```
[inspector]
  backend:   numpy | torch | jax
  rank:      2 | 3 | 4
  layout:    HW | HWC | CHW | NHWC | NCHW
  dtype:     <dtype>
  shape:     <shape>
  range:     raw | normalized | standardized | unusual
  min/max:   <min> / <max>
  per-channel mean: [ ... ]
  per-channel std:  [ ... ]
  likely source:    camera | PIL | OpenCV | torchvision | random init
  likely target:    display | training | inference
```

6. **`likely target`'a göre bir sonraki eylemi öner**:
   - `display` için: HWC'ye devşir (transpose), kırp, uint8'e dönüştür.
   - `training` için: veri kümesi istatistikleriyle standartlaştır, CHW'ye devşir, toplu iş ekseni ekle.
   - `inference` için: model kartındaki tam değişmezlerle eşleştir.

## Kurallar

- Girdiyi asla mutasyona uğratma. Yalnızca tanılamaları yazdır.
- `expected` sağlanırsa, her uyumsuzluğu `[expected X got Y]` ile işaretle.
- Düzen veya kanal sırası belirsiz olduğunda sessiz başarısızlık risklerini belirt.
- Bir seferde yalnızca bir eylem öner, seçenek listesi değil.
