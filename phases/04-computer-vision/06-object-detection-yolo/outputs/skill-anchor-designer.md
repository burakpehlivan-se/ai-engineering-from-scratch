---
name: skill-anchor-designer
description: Verilen temel gerçeklik kutusu veri kümesi, (w, h) üzerinde k-means çalıştırın ve FPN seviyesi başına çapa setlerini ve kapsam istatistiklerini döndürün
version: 1.0.0
phase: 4
lesson: 6
tags: [bilgisayarlı-gör, tespit, çapalar, kmeans]
---

# Çapa Tasarımcısı

Çapalar, çapa tabanlı bir tespit edicideki tek en veri kümesine özgü hiperparametredir. Varsayılan COCO çapaları, hücre kültürü görüntüleri, uydu karoları veya küçük nesne gözetiminde daha kötü performans gösterir. Bu beceri, aslında hedef verilerle eşleşen çapalar türetir.

## Ne zaman kullanılır

- Yeni bir veri kümesinde ilk eğitim çalıştırmasından önce.
- Aksi takdirde sağlıklı bir modelde çok küçük veya çok büyük nesneler üzerindeki duyarlılık zayıf olduğunda.
- Kutu boyutu dağılımının kaymış olabileceği büyük bir veri kümesi genişlemesinden sonra.

## Girdiler

- `boxes`: ya `(cx, cy, w, h)` ya da `(x1, y1, x2, y2)` biçiminde şekil (N, 4) numpy dizisi; en az 1000 pozitif kutu önerilir.
- `num_anchors_per_level`: genellikle 3.
- `num_fpn_levels`: genellikle 3 (P3, P4, P5) veya 4.
- `input_size`: eğitim çözünürlüğü HxW.
- İsteğe bağlı `strides`: seviye başına stride'lar; atlandığında, `[8, 16, 32, 64]`'ün ilk `num_fpn_levels` girdisini al. Tespit edicinin FPN'si farklı stride'lara sahipse açıkça daha uzun veya daha kısa bir dizi geçir.

## Adımlar

1. **Kutuları normalleştir** `input_size`'da piksel birimlerinde `(w, h)` çiftlerine. w veya h < 2 piksel olanları düşür.

2. **`(w, h)` çiftleri üzerinde k-means çalıştır**, `k = num_anchors_per_level * num_fpn_levels` ile. Mesafe fonksiyonu olarak `1 - IoU(box, cluster)` kullan, Öklid mesafesi değil — `(w, h)` üzerindeki Öklid, ince uzun kutuları ve kare kutuları bir araya getirir. Tüm kutular eşit katkıda bulunur (ağırlıksız); sınıf dengesiz bir veri kümeniz varsa ve daha büyük kutu duyarlılığı istiyorsanız, ağırlık vektörü geçmek yerine nadir sınıf kutularını girdi dizisinde tekrarlayın.

3. **Kümeleri alana göre artan sırayla sırala.** `num_anchors_per_level` ile `num_fpn_levels` grubuna böl. En küçük alanlar en yüksek çözünürlüklü seviyeye (en küçük stride) gider.

4. **Seviye başına kapsam istatistiklerini hesapla**:
   - O seviyedeki en iyi çapasına göre her temel gerçeklik kutusunun `median IoU`'su.
   - `recall@IoU=0.5` — en iyi çapasının IoU >= 0.5 olduğu kutuların yüzdesi.
   - `area coverage` — alanı seviyenin `[anchor_min_area / 4, anchor_max_area * 4]` aralığına düşen kutuların oranı.

5. **Seviye başına çapaları raporla** ve `recall@IoU=0.5 < 0.9` olan seviyeleri işaretle; o seviyenin çapaları verilerle iyi eşleşmiyor ve yeniden ayarlanmalı veya seviye başına çapa sayısı artırılmalıdır.

## Rapor formatı

```
[anchor-designer]
  total boxes:         <N>
  clusters:            <k>
  distance metric:     1 - IoU

[level P3  stride=8]
  anchors (w, h):      [(A, B), (C, D), (E, F)]
  median IoU:          <X>
  recall@IoU=0.5:      <X>
  coverage:            <X>
  flag:                ok | retune

[level P4  stride=16]
  ...

[summary]
  overall recall@IoU=0.5: <X>
  smallest anchor:        <w x h>
  largest anchor:         <w x h>
  recommendation:         <herhangi bir seviye işaretlendiyse tek cümle>
```

## Kurallar

- Her zaman IoU tabanlı mesafe kullan; Öklid k-means, görsel olarak makul ama ampirik olarak daha kötü çapalar üretir.
- Kümeleri alana göre sırala, sonra seviyelere artan sırayla ata.
- `num_anchors_per_level = 1` olduğunda, k-means'i tamamen atla: kutuları alan niceliğine göre `num_fpn_levels` bölmesine ayır (örn. 3 seviye için üçte birlik dilimler) ve her seviyenin çapasını bölme başına ortanca (w, h) olarak ayarla. Bu, küçük veri kümelerinde `k = num_fpn_levels` ile k-means çalıştırmaktan daha sağlamdır.
- Asla negatif çapa boyutları çıktılama; 1'de sıkıştır.
- Veri kümesi < 200 kutuya sahipse, kullanıcıyı çapa aramasının güvenilir olmadığı konusunda uyar ve daha fazla eğitim verisiyle varsayılan COCO çapalarını kullanmasını öner.
