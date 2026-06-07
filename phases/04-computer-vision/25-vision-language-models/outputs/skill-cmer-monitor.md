---
name: skill-cmer-monitor
description: Bir üretim VLM uç noktasını Çapraz-Modlu Hata Oranı (CMER) izleme, panolar ve uyarılarla donatın
version: 1.0.0
phase: 4
lesson: 25
tags: [vlm, üretim, izleme, halüsinasyon]
---

# CMER Monitörü

Çapraz-modlu hizalamayı birinci sınıf bir üretim KPI'sı olarak ele alın.

## Ne zaman kullanılır

- Görüntülere dayalı metin üreten herhangi bir VLM uç noktasını dağıtırken.
- Halüsinasyonlu yanıt raporlarını araştırırken.
- Bir girdi dağılımı kaymasının model temellendirmesini bozup bozmadığını izlerken.

## Girdiler

- `vlm_output`: üretilen metin.
- `text_confidence`: softmax sonrası token başına ortalama olasılık, `[0, 1]` aralığında. `exp(mean(log_probs))` olarak hesaplayın. Ham logit'leri geçmeyin; ham logit'ler sınırsızdır ve `conf_threshold` bir olasılık varsayar.
- `image_embedding`: görüntünün CLIP ailesi gömme'si (DINOv3, SigLIP, CLIP).
- `text_embedding`: üretilen metnin CLIP ailesi gömme'si.
- İsteğe bağlı `prompt_type`: gruplama için etiket (vqa / ocr / captioning / agent).

## İstek başına hesaplama

```python
import torch

def cmer_flag(image_emb, text_emb, text_conf, sim_thr=0.25, conf_thr=0.8):
 if image_emb.shape != text_emb.shape:
 raise ValueError(f"emb shape mismatch: {image_emb.shape} vs {text_emb.shape}")
 image_emb = image_emb / (image_emb.norm() + 1e-8)
 text_emb = text_emb / (text_emb.norm() + 1e-8)
 sim = float((image_emb * text_emb).sum())
 flagged = (text_conf > conf_thr) and (sim < sim_thr)
 return {"sim": sim, "flagged": flagged}
```

Gömme'ler bağımsız bir CLIP ailesi kodlayıcıdan 1 boyutlu PyTorch tensörleridir (`torch.float32`). NumPy dizileri kullanıyorsanız, `.norm()`'u `np.linalg.norm(...)` ile değiştirin ve çıktıyı uygun şekilde dönüştürün.

`sim`, `text_conf`, `flagged`, `prompt_type`, `timestamp`, `model_version`, `request_id`'yi izleme işlem hattınıza kaydedin (Prometheus, DataDog, OpenTelemetry).

## Toplam metrik

```
CMER = (penceredeki işaretli istekler) / (penceredeki toplam istekler)
```

Uç nokta başına, `prompt_type` başına, model sürümü başına raporlayın.

## Uyarı eşikleri

- Temel CMER: 7 günlük normal trafik üzerinde belirleyin.
- Uyarı: 1 saat boyunca CMER >= temelin 1.5 katı.
- Kritik: 30 dakika boyunca CMER >= temelin 2 katı veya herhangi bir pencere için mutlak > %15.

## Pano panelleri

1. Zaman içinde CMER (5 dakikalık kova, 7 günlük pencere).
2. `prompt_type`'a göre CMER (yığılmış çubuk).
3. Saat başına `sim` dağılımı (histogram).
4. En çok halüsinasyonlu çıktılar (insan incelemesi için günde 20 işaretli yanıt örneği).

## CMER sıçradığında eylemler

1. İşaretli istekleri örnekleyin.
2. Model sürümünün yanlışlıkla değişmediğini doğrulayın.
3. Girdi dağılımını kontrol edin (yeni dosya biçimi? yeni görüntü kaynağı? farklı sıkıştırılmış?).
4. Etkilenen trafiği sıçrama çözülene kadar insan incelemesine yönlendirin.
5. Sıçrama kalıcıysa, modeli ince ayar yapın veya değiştirin; uyarıyı bastırmayın.

## Kurallar

- CMER'yi asla VLM'nin kendi gömme'lerini kullanarak hesaplamayın; bağımsız bir kodlayıcı (DINOv3, SigLIP veya CLIP-L/14) kullanın. Aksi takdirde modelin öz-tutarlılığını değil, hizalamasını ölçersiniz.
- Yalnızca `flagged` bitini değil, her zaman ham `sim` değerini kaydedin; dağılım kaymaları işaret oranı değişmeden önce alt çeyrekte ortaya çıkar.
- Bir VLM uç noktasını CMER izleme olmadan göndermeyin; halüsinasyonlar baskın üretim başarısızlık modudur ve bu metrik olmadan sessizdir.
- Hassas alanlar (tıbbi, hukuki, finansal) için, `sim_threshold`'u 0.35 veya daha yükseğe yükseltin; bayrak koşulu `sim < sim_threshold`'dur, bu nedenle daha yüksek bir eşik daha fazla çıktıyı potansiyel olarak temelsiz olarak yakalar — yüksek riskli kullanım için doğru varsayılan.
