---
name: skill-segmentation-mask-inspector
description: Sınıf dağılımını, tahmin edilen maske istatistiklerini ve büyük olasılıkla yetersiz tahmin edilen veya sınır bulanıklaştırılmış sınıfları raporlayın
version: 1.0.0
phase: 4
lesson: 7
tags: [bilgisayarlı-gör, segmentasyon, hata-ayıklama, değerlendirme]
---

# Segmentasyon Maskesi Denetçisi

"Kayıp azaldı" ile "maskeler aslında doğru görünüyor" arasındaki boşluk için bir tanısal.

## Ne zaman kullanılır

- mIoU iyi göründüğü ama görsel inceleme aksini söylediği bir eğitim çalıştırmasından hemen sonra.
- Dağıtımdan önce: tahminlerin sınıf dengesini temel gerçekliğe karşı kontrol etme.
- Büyük nesneler için sınıf başına IoU yüksek, küçük olanlar için düşük olduğunda.
- Piksel sayısında küçük oldukları için IoU'da görünmeyen sınır eserlerini ayıklama.

## Girdiler

- `preds`: tahmin edilen sınıf kimliklerinin (N, H, W) tensörü.
- `targets`: temel gerçeklik sınıf kimliklerinin (N, H, W) tensörü.
- `num_classes`: tamsayı.
- İsteğe bağlı `class_names`: C dizi listesi.

## Adımlar

1. **Sınıf piksel histogramları.** `preds` ve `targets` için sınıf başına piksel yüzdesini hesaplayın. `|pred% - gt%| / max(gt%, 1e-6) > 0.30` olan herhangi bir sınıfı işaretleyin (göreceli sapma %30'un üzerinde). Temel gerçeklikte bulunmayan sınıflar (`gt% == 0`) için, doğrudan `0.3`'ün üzerindeki herhangi bir tahmin payını işaretleyin.

2. **Sınıf başına IoU** ve **sınıf başına sınır F1**. Sınır F1, her maskeyi 3 piksel genişleterek, kesişim alıp puanlayarak hesaplanır. IoU > 0.7 ancak sınır F1 < 0.5 olan sınıflar kenarları bulanıklaştırır.

3. **Küçük nesne duyarlılığı.** Her temel gerçeklik bağlı bileşenini boyut kovalarına ayırın (çok küçük < 100 px, küçük < 1000 px, orta < 10000 px, büyük >= 10000 px). Sınıf başına kova başına duyarlılığı raporlayın. Büyük nesne duyarlılığı 0.9'un üzerindeyken küçük nesne duyarlılığının 0.3'ün altında olması, bir çözünürlük / alıcı alan sorununa işaret eder.

4. **Karışıklık çiftleri.** Her sınıf için, en sık karıştığı sınıfı bulun (temel gerçeklik maskesi içinde en yaygın yanlış tahmin edilen sınıf). İlk 3 çifti raporlayın.

5. **Doygunluk kontrolü (`probs` veya `logits` gerektirir, yalnızca `preds` değil).** Arayan, ham piksel başına olasılık dağılımı `probs: (N, C, H, W)`'i geçerse, `probs.max(dim=1) > 0.99` olan piksellerin oranını sınıf başına hesaplayın. Yüksek doygunluk (bir sınıfın piksellerinin >0.9'u) aşırı güvene işaret eder — etiket yumuşatma veya kalibrasyon adayı. Yalnızca argmax'lanmış `preds` kullanılabilir olduğunda, bu adımı atlayın ve raporda belirtin.

## Rapor formatı

```
[mask-inspector]
 classes: C

[class distribution]
 name gt % pred % delta
 ...

[metrics]
 class IoU bF1 recall_tiny recall_small recall_medium recall_large
 ...

[confusion pairs]
 class A confused with class B: <N> piksel (en yaygın)
 class B confused with class A: <N> piksel
 ...

[verdict]
 most impactful issue: <tek cümle>
```

## Kurallar

- Sınıf satırlarını azalan gt piksel payına göre sıralayın, böylece en sık sınıflar ilk gelir.
- IoU < 0.4 veya sınır F1 < 0.3 olan sınıfları `critical` olarak işaretleyin.
- Küçük nesne duyarlılığı baskın başarısızlık olduğunda, şunları önerin: daha yüksek çözünürlüklü eğitim, son kodlayıcı aşamasında daha küçük stride veya bir özellik piramidi kod çözücüsü.
- Sınır F1 baskın başarısızlık olduğunda, şunları önerin: sınıra duyarlı kayıp (Lovasz veya BoundaryLoss), yatay çevirme ile TTA ve stride'sız kod çözücü.
- Sınıf indekslerini asla tek tanımlayıcı olarak çıktılama; `class_names` sağlanırsa, her satırda kullanın.
