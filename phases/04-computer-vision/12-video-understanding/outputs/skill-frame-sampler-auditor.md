---
name: skill-frame-sampler-auditor
description: Bir video hattının çerçeve örnekleyicisini off-by-one, kısa klip işleme ve kırpma tutarlılığı için denetleyin
version: 1.0.0
phase: 4
lesson: 12
tags: [bilgisayarlı-gör, video, örnekleme, hata-ayıklama]
---

# Çerçeve Örnekleyici Denetçisi

Çerçeve örnekleme, video hatlarının bozulduğu yerdir. Buradaki hatalar, her aşağı akış metriğine yayılır.

## Ne zaman kullanılır

- Yeni bir video veri yükleyicisi yazarken.
- Bir makaleden sayıları yeniden üretirken ve eğitim doğruluğu rapor edilenden düşük olduğunda.
- Değerlendirme doğruluğu çalıştırmalar arasında kararsız olan bir video modelini ayıklarken.

## Girdiler

- `sampler_code`: (num_frames_total, T) alıp T indeks döndüren Python fonksiyonu.
- `T`: hedef klip uzunluğu.
- İsteğe bağlı test durumları: egzersiz yapılacak `num_frames_total` değerleri (örn. `[3, T-1, T, T+1, 30, 300, 3000]`).

## Kontroller

### 1. Kısa klip işleme
`num_frames_total < T` besleyin. Döndürülen her indeks `[0, num_frames_total - 1]` aralığında olmalıdır. Standart doldurma politikası, kalan konumlar için son çerçeveyi tekrarlamaktır.

### 2. Sınır indeksleri
`num_frames_total == T` besleyin. Döndürülen indeksler tam olarak `[0, 1, ..., T-1]` olmalıdır.

### 3. Düzgün dağılım
`num_frames_total == 10 * T` besleyin. Döndürülen indeksler monoton artan ve kabaca eşit aralıklı olmalıdır.

### 4. Yoğun pencere sınırları
Yoğun örnekleme için, `num_frames_total == 3 * T` besleyin. Döndürülen indeksler bitişik bir pencere oluşturmalı, klibin sonunu asla aşmamalıdır.

### 5. Deterministiklik
Örnekleyiciyi aynı girdilerle ve (deterministik örnekleyiciler için) aynı RNG ile iki kez çağırın. İndeksler eşleşmelidir.

### 6. Kırpma tutarlılığı
Hat aynı zamanda çerçeve başına uzamsal bir kırpma da döndürüyorsa, aynı klip için aynı tohumla örnekleyiciyi iki kez çalıştırın ve her çerçevenin aynı kırpma kutusunu (aynı `(x, y, w, h)`) kullandığını onaylayın. Bir klip içinde çerçeve başına farklı kırpmalar, zamansal tutarlılığı bozar ve klasik bir sessiz hatadır. Kabul edilebilir varyasyon: *klip başına* uygulanan, klip içinde tutarlı veri artırma.

## Rapor

```
[sampler audit]
 name: <fonksiyon adı>
 T: <int>

[short-clip handling]
 passed | failed (<detaylar>)

[boundary]
 passed | failed

[uniform spacing]
 passed | failed (<boşlukların stddev'i>)

[dense window]
 passed | failed (<detaylar>)

[determinism]
 passed | failed

[crop consistency]
 passed | failed (<çerçeve başına kırpma değişiyor: evet/hayır>)

[verdict]
 ok | düzeltme gerekli
```

## Kurallar

- Kısa klip işleme aralık dışı indeksler döndürüyorsa, bir örnekleyiciyi asla "ok" olarak işaretleme.
- Yoğun örnekleyiciler, `num_frames_total - 1`'i aşan bir pencere döndürmemelidir.
- Örnekleyici stokastikse (yoğun), deterministliği yalnızca açık tohumlanmış bir RNG ile test edin.
- Kurallı politikaları önerin, ancak sessizce düzeltmeyin: son çerçeveyle doldurun, pencereyi sonuna kelepçeleyin, yarı-açık aralıkları yuvarlayın.
