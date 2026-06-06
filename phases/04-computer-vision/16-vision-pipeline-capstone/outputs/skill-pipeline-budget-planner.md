---
name: skill-pipeline-budget-planner
description: Hedef gecikme ve çıktı verildiğinde, her işlem hattı aşamasına bir zaman bütçesi atayın ve bütçesini ilk kaçıracak aşamayı işaretleyin
version: 1.0.0
phase: 4
lesson: 16
tags: [görü, işlem hattı, performans, dağıtım]
---

# İşlem Hattı Bütçe Planlayıcısı

Bir gecikme/çıktı hedefini aşama aşama bütçeye dönüştürün, böylece her ekip üyesi hangi sayıya doğru mühendislik yaptığını bilir.

## Ne zaman kullanılır

- Her bir aşama için beklentileri belirlemek üzere yeni bir görüntü hizmeti inşa etmeden önce.
- Hangi aşamanın bütçesinden en uzak olduğunu görmek için ilk kıyaslamadan sonra.
- Bir SLA değiştiğinde ve bütçelerin yeniden müzakere edilmesi gerektiğinde.

## Girdiler

- `p95_latency_target_ms`: istek başına bütçe.
- `target_qps`: kopya başına çıktı.
- `stages`: `{ name: str, current_ms: float }` listesi.

## Tahsis kuralları

Mevcut ölçümler sağlanmadıysa, yedi standart aşama boyunca varsayılan tahsis:

| Aşama | Pay |
|-------|-----|
| çözme + ön işleme | %15 |
| detektör ileri | %55 |
| tespitleri son işleme (NMS, sıkıştırma) | %5 |
| sınıflandırıcı için kırpma + yeniden boyutlandırma | %5 |
| sınıflandırıcı ileri | %15 |
| şema doğrulama | <%1 |
| yanıt serileştirme | %4 |

GPU'ya bağlı işlem hatlarında (bulut), detektör payı sıklıkla %70'e yükselir. CPU'da, ön işleme ve sınıflandırıcı toplu işleri daha fazla yer.

## Rapor

```
[budget plan]
  p95 target:  <ms>
  throughput:  <replika başına qps>

| stage               | target_ms | current_ms | headroom | gate |
|---------------------|-----------|------------|----------|------|
| decode+preprocess   | ...       | ...        | ...      | ok|X |
| detector            | ...       | ...        | ...      | ok|X |
| ...                 | ...       | ...        | ...      |      |

[bottleneck]
  stage:  <isim>
  miss:   <bütçenin üzerinde ms>
  lever:  <spesifik eylem>

[levers]
  decode+preprocess:   Pillow-SIMD, libjpeg-turbo, NVJPEG ile GPU'da çözme
  detector:            daha küçük omurga, daha düşük giriş çözünürlüğü, INT8, TensorRT
  postprocess:         GPU tarafında NMS (torchvision.ops), füzyon maskeleri
  crop+resize:         grid_sample ile GPU kırpması, toplu enterpolasyon
  classifier:          daha küçük omurga, INT8, sıcak önbellek, toplu iş
  schema:              sıcak yolda doğrulamayı atla, yalnızca sınırlarda doğrula
  response:            orjson, akış protobuf
```

## Kurallar

- Şema doğrulamasını üretim yolundan düşürmeyi asla önerme; bunun yerine sınıra taşımayı öner.
- Ön işleme bütçesini kaçırırsa, modeli değiştirmeden önce her zaman Pillow-SIMD veya NVJPEG'i deneyin.
- Detektör ıskalaması hedefin %30'undan fazlaysa, mevcut olanı optimize etmek yerine modelleri değiştirin.
- `current_ms > 1.1 * target_ms` olduğunda geçidi `X` olarak işaretleyin; bütçenin %10'u içindeyse `ok` olarak işaretleyin.
