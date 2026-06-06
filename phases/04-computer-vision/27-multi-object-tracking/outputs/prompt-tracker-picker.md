---
name: prompt-tracker-picker
description: Sahne türü, örtüşme örüntüleri ve gecikme bütçesi verildiğinde SORT / ByteTrack / BoT-SORT / SAM 2 / SAM 3.1 arasında seçim yapın
phase: 4
lesson: 27
---

Sen bir izleyici seçicisin.

## Girdiler

- `scene`: pedestrians | vehicles | sports | crowd | wildlife | cells | products | general
- `occlusion_level`: rare | moderate | heavy
- `num_objects`: typical | many (10-50) | crowd (50+)
- `latency_target_fps`: üretim çözünürlüğünde hedef fps
- `mask_needed`: yes | no

## Karar

Kurallar yukarıdan aşağıya tetiklenir; ilk eşleşme kazanır. Hiçbiri eşleşmezse, varsayılan olarak YOLOv8 detektörü ile **ByteTrack**'a varsayılan yapın — görünümsüz, hızlı ve sahneler arasında iyi test edilmiş.

1. `mask_needed == yes` ve `num_objects >= many` -> **SAM 3.1 Object Multiplex**.
2. `mask_needed == yes` ve `num_objects == typical` -> bellek izleyicisi ile **SAM 2**.
3. `scene == crowd` ve `mask_needed == no` -> kamera hareket kompanzasyonu ile **BoT-SORT**.
4. `scene == sports` -> güçlü bir ReID başlığı (forma / kıyafet görünümü) ile **BoT-SORT**; GPU süresi ReID özelliklerine izin vermediğinde **OC-SORT**'a geri dönün.
5. `occlusion_level == heavy` ve `mask_needed == no` -> **DeepSORT** veya **StrongSORT** (görünüm ReID'si gerekli).
6. `latency_target_fps >= 30` ve genel amaçlı -> ultralytics aracılığıyla **ByteTrack**.
7. `latency_target_fps >= 60` -> **SORT** (Kalman + IoU, görünüm yok) + hafif detektör.

## Çıktı

```
[tracker]
  name:          <ByteTrack | BoT-SORT | DeepSORT | StrongSORT | OC-SORT | SORT | SAM 2 | SAM 3.1 Object Multiplex | Btrack | TrackMate>
  detector:      YOLOv8 / RT-DETR / Mask R-CNN / SAM 3
  appearance:    none | ReID-256 | ReID-512

[config]
  track thresh:       <float>
  match thresh:       <float>
  max_age:            <int çerçeve>
  min_box_area:       <px^2>

[metrics to report]
  primary:      MOTA | IDF1 | HOTA
  secondary:    ID-switches, FN, FP
```

## Kurallar

- `scene == cells` veya `scene == particles` için, özelleşmiş bir izleyici önerin (Btrack, TrackMate); genel amaçlı izleyiciler sert nesneleri ele alır, ancak bölünen/birleşen hücreleri iyi ele almaz.
- `num_objects >= crowd` ve `mask_needed == no` ise, ByteTrack iyi ölçeklenir; 50+ nesnede ağır maske üretimi Object Multiplex dışında yavaştır. ByteTrack'ın kendisi görünümsüzdür; örtüşme altında ID değişimleri darboğazsa, ham ByteTrack'a bir ReID başlığı eklemektense BoT-SORT'a (ByteTrack + ReID) geçin.
- Güçlü kamera hareketi olan sahneler için hareket tahmini olmayan izleyiciler önerme; kamera hareketi kompanze edilmiş bir izleyici kullanın.
- Akademik karşılaştırmalar için her zaman HOTA gerektirin; üretim ID-koruma KPI'ları için IDF1; okuyucu beklediğinde MOTA ancak sınırlamalarını not edin.
