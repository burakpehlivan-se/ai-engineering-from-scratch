---
name: skill-mask-rcnn-head-swapper
description: Özel bir num_classes için torchvision Mask R-CNN üzerinde kutu ve maske kafalarını değiştirmek için tam kodu üretin
version: 1.0.0
phase: 4
lesson: 8
tags: [bilgisayarlı-gör, mask-rcnn, ince-ayar, torchvision]
---

# Mask R-CNN Kafa Değiştirici

Özellikle Mask R-CNN için kafa değiştirme şablon kodunu üretir. Aşağıdaki şablon, yalnızca `maskrcnn_resnet50_fpn` ve `maskrcnn_resnet50_fpn_v2` üzerinde bulunan `model.roi_heads.box_predictor` ve `model.roi_heads.mask_predictor` varsayar. Faster R-CNN'in bir kutu tahmincisi var ama maske tahmincisi yok; RetinaNet `RetinaNetHead` kullanır ve hiç `roi_heads`'i yoktur — her ikisi de farklı beceriler gerektirir.

## Ne zaman kullanılır

- `maskrcnn_resnet50_fpn` veya `maskrcnn_resnet50_fpn_v2`'yi özel bir sınıf kümesinde ince ayar yapma.
- COCO üzerinde eğitilmiş bir Mask R-CNN kontrol noktasını COCO dışı bir sınıf sayısına taşıma.
- `cls_score.out_features` veya `mask_predictor` uyumsuzluğunda çöken bir Mask R-CNN eğitim çalıştırmasını ayıklama.

## Kapsam dışı

- `fasterrcnn_*` — mask_predictor yok. Yalnızca `box_predictor`'ı değiştir; ayrı bir Faster R-CNN kafa değiştirme tarifi kullan.
- `retinanet_*` — `roi_heads` yok; sınıflandırıcı + regresyon kafaları `model.head.classification_head` ve `model.head.regression_head` altında yaşar. RetinaNet'e özgü bir beceri kullan.
- `keypointrcnn_*` — `mask_predictor` yerine `keypoint_predictor` kullanır.

## Girdiler

- `model_name`: torchvision tespit modeli yapıcısı, örn. `maskrcnn_resnet50_fpn_v2`.
- `num_classes`: arka plan dahil. 4 nesne sınıflı bir veri kümesi `num_classes=5` anlamına gelir.
- `freeze`: şunlardan biri: `backbone`, `backbone_fpn`, `none`.

## Adımlar

1. Model yapıcısını ve iki tahmin edici sınıfı (`FastRCNNPredictor`, `MaskRCNNPredictor`) içe aktar.
2. Varsayılan ağırlıklarla önceden eğitilmiş modeli yükle.
3. `model.roi_heads.box_predictor`'ı yeni bir `FastRCNNPredictor(in_features, num_classes)` ile değiştir.
4. `model.roi_heads.mask_predictor`'ı yeni bir `MaskRCNNPredictor(in_features_mask, hidden_layer=256, num_classes)` ile değiştir.
5. İstenen dondurma politikasını uygula.
6. Modül başına eğitilebilir parametreleri listeleyen bir onay bloğu yazdır.

## Çıktı kod şablonu

```python
from torchvision.models.detection import {MODEL_NAME}, {MODEL_WEIGHTS}
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

def build_model(num_classes={NUM_CLASSES}):
 model = {MODEL_NAME}(weights={MODEL_WEIGHTS}. DEFAULT)
 in_features = model.roi_heads.box_predictor.cls_score.in_features
 model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
 in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
 model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, 256, num_classes)

 {FREEZE_BLOCK}

 return model
```

Burada `{FREEZE_BLOCK}` şudur:

- `none` -> boş
- `backbone` ->
 ```python
 for p in model.backbone.parameters():
 p.requires_grad = False
 ```
- `backbone_fpn` ->
 ```python
 for p in model.backbone.parameters():
 p.requires_grad = False
 # FPN parametreleri backbone.fpn içinde yaşar
 ```

## Rapor

```
[head-swap]
 model: <MODEL_NAME>
 num_classes: <N> (arka plan dahil)
 freeze policy: <seçim>
 trainable: <N>
 total: <N>
```

## Kurallar

- `num_classes` önerirken arka planı asla dahil etmeden yapma; her zaman kullanıcıyı hatırlat.
- Mevcut olduğunda her zaman torchvision tespit modellerinin `_v2` varyantlarını kullan; eski olanlardan daha iyi önceden eğitilmiş ağırlıklara sahiptirler.
- Modeli bu beceri içinde somutlaştırma — kod bloğunu üret ve kullanıcının çalıştırmasına izin ver.
- Kullanıcı 10.000'den fazla görüntülük bir veri kümesinde `freeze backbone` isterse, omurgayı da ince ayar yapmayı düşünmesini öner.
