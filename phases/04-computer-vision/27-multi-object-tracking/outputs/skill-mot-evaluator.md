---
name: skill-mot-evaluator
description: Temel doğruluk izleri üzerinde MOTA / IDF1 / HOTA için eksiksiz bir değerlendirme koşum takımı yazın
version: 1.0.0
phase: 4
lesson: 27
tags: [mot, değerlendirme, izleme, metrikler]
---

# MOT Değerlendirici

İzleyicinizin çıktısını, literatüre karşı adil bir şekilde karşılaştırabilmeniz için standart MOTA/IDF1/HOTA işlem hattına sarın.

## Ne zaman kullanılır

- MOT17 / MOT20 / DanceTrack / SportsMOT üzerinde yeni bir izleyiciyi kıyaslarken.
- Kendi çekimlerinizde ByteTrack'ı BoT-SORT'a ve SAM 2'ye karşılaştırırken.
- Bir makale veya PR açıklaması için tekrarlanabilir bir sayı üretirken.

## Girdiler

- `predictions`: çerçeve başına `(track_id, x, y, w, h, confidence)` demetlerinin listesi.
- `ground_truth`: çerçeve başına `(gt_id, x, y, w, h)` demetlerinin listesi.
- `iou_threshold`: MOTA için tipik 0.5; HOTA bir tarama kullanır.
- `evaluator`: `py-motmetrics` (MOTA, IDF1) veya `TrackEval` (HOTA).

## Çıktı biçimi sözleşmesi

Hem `py-motmetrics` hem de `TrackEval` belirli bir disk üstü biçimi bekler:

```
# predictions.txt
<frame>,<track_id>,<x>,<y>,<w>,<h>,<confidence>,-1,-1,-1

# ground_truth.txt
<frame>,<gt_id>,<x>,<y>,<w>,<h>,1,-1,-1,-1
```

Çerçeveler 1-indekslidir, kutular (x1, y1, x2, y2) değil (x, y, w, h) şeklindedir. Dönüştürme, çoğu entegrasyon hatasının yaşadığı yerdir.

## Adımlar

1. İzleyicinizin çıktısını MOT Challenge metin biçimine dönüştürün.
2. Her iki dosya üzerinde `py-motmetrics.io.loadtxt` çalıştırın.
3. `mm.metrics.create().compute()` ile MOTA + IDF1 hesaplayın.
4. HOTA için, aynı dosyalar ve `Metrics: HOTA` ile `TrackEval` çağırın.
5. Sonuçları panolar için JSON olarak kaydedin.

## Uygulama taslağı

```python
import motmetrics as mm

def evaluate_mota_idf1(pred_path, gt_path):
 gt = mm.io.loadtxt(gt_path, fmt="mot15-2D")
 pred = mm.io.loadtxt(pred_path, fmt="mot15-2D")
 acc = mm.utils.compare_to_groundtruth(gt, pred, dist="iou", distth=0.5)
 metrics = mm.metrics.create().compute(
 acc, metrics=["num_frames", "mota", "motp", "idf1", "idp", "idr", "num_switches"]
 )
 return metrics


def write_mot_txt(predictions, path):
 with open(path, "w") as f:
 for frame_idx, detections in enumerate(predictions, start=1):
 for tid, x, y, w, h, conf in detections:
 f.write(f"{frame_idx},{tid},{x:.2f},{y:.2f},{w:.2f},{h:.2f},{conf:.3f},-1,-1,-1\n")
```

## Rapor

```
[mot evaluation]
 frames: <int>
 gt tracks: <int>
 pred tracks: <int>

[metrics]
 MOTA: <float>
 MOTP: <float>
 IDF1: <float>
 IDP/IDR: <float/float>
 ID switches: <int>
 HOTA: <float> (TrackEval'den)
```

## Kurallar

- Çıktı metin dosyasında her zaman 1-indeksli çerçeveler kullanın; MOT araçları bunu bekler.
- Yazmadan önce (x1, y1, x2, y2)'yi (x, y, w, h)'ye dönüştürün.
- Modern karşılaştırmalar için yalnızca MOTA raporlamayın; IDF1 ve HOTA'yı dahil edin.
- MOT17'de özel ve genel tespitlere dikkat edin — ayrı ayrı değerlendirilirler ve karıştırmak skorları şişirir.
- Dizi başına skorları kaydedin; toplam, tek zor dizilerdeki başarısızlıkları gizler.
