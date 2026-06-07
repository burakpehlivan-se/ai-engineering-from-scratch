---
name: skill-physical-plausibility-checks
description: Göndermeden önce herhangi bir üretilmiş video üzerinde nesne kalıcılığı, yerçekimi ve süreklilik otomatik kontrolleri
version: 1.0.0
phase: 4
lesson: 28
tags: [video-üretimi, kalite, fizik, değerlendirme]
---

# Fiziksel Plausibilité Kontrolleri

Üretilmiş videonun üretim dağıtımları otomatik koruma rayları gerektirir. İnsan incelemesi ölçeklenmez; fizik kontrolleri klasik başarısızlık modlarını yakalar.

## Ne zaman kullanılır

- Metin veya görüntü istemlerinden video üreten herhangi bir ürün.
- Bir video üretim API uç noktası üzerinde QA otomatikleştirirken.
- İnce ayar veya bir temel model güncellemesinden sonra bir video modelinin kalite kaymasını izlerken.

## Girdiler

- `video`: bir tensör `(T, H, W, 3)` veya bir mp4'e giden yol.
- İsteğe bağlı referans bilgisi: beklenen nesne sayısı, başlangıç sahne açıklaması.

## Kontroller

### 1. Nesne kalıcılığı
Her tespiti çerçeveler arasında SAM 3.1 Object Multiplex ile izleyin. Kararlı bir iz <=3 çerçeve için kaybolup yeniden göründüğünde işaretleyin — model nesneyi geçici olarak kaybetti. Bir nesne çerçeve merkezine yakın (kenarda değil) kaybolduğunda sert başarısızlık; kenarlarda yumuşak başarısızlık.

### 2. Hareket pürüzsüzlüğü
Ardışık çerçeveler arasındaki optik akış çoğunlukla sürekli olmalıdır. Piksel başına ani akış sıçramaları ışınlanmayı gösterir. RAFT ile akışı hesaplayın; 99. yüzdelik akış büyüklüğünün medyanı 10 katından fazla aştığı çerçeveleri işaretleyin.

### 3. Yerçekimi / destek
Katı olarak tespit edilen nesneler (yiyecek, toplar, aletler) için, dikey konumlarının bir kaldırma eylemi yokluğunda azalmadığını kontrol edin. Nesnenin yakınında bir "kavrayan el" tespit edilmedikçe yukarı sürüklenmeyi işaretleyin.

### 4. Kimlik tutarlılığı
İnsanlar veya karakterler için, çerçeveler arasında bir yüz tanıma gömme'si kullanın. Kalıcı bir kimlik için kosinüs benzerliği 5 çerçevelik pencerelerde > 0.8 kalmalıdır. Eşiğin altı, karakterin dönüştüğü anlamına gelir.

### 5. Eller ve uzuvlar
Bir poz tahmin edicisi (Ders 21) çalıştırın. Bir elin > 5 veya < 4 görünür parmağa sahip olduğu; bir kol uzunluğunun çerçeveler arasında ikiye katlandığı; uzuvların bir yüzey içinden geçerek vücudu kestiği çerçeveleri işaretleyin.

### 6. Metin oluşturma (istem metin istediyse)
Kullanıcı istemi tırnak içinde bir dize içeriyorsa, üretilen çerçeveler üzerinde OCR çalıştırın ve istenen dizeye karşı CER hesaplayın. > %20 CER'ı işaretleyin.

## Rapor

```
[plausibility]
 video frames: <T>
 permanence violations: <N>
 smoothness violations: <N>
 gravity violations: <N>
 identity drift: <5 çerçevelik pencere sayısı>
 limb anomalies: <N>
 OCR CER vs requested: <float>

[verdict]
 ship | hold | reject

[samples for review]
 her başarısızlığın oluştuğu çerçeve aralıkları
```

## Kurallar

- Herhangi bir tek kontrolde sert engelleme yapmayın; toplam anomaliler bir eşiği aştığında toplam skorları birleştirin ve videoyu inceleme için tutun.
- Kimlik kaymasını ve kalıcılık ihlallerini en yüksek ağırlıklandırın — kullanıcılar bunları ilk fark eder.
- Zaman içinde kontrol başına başarısızlık oranlarını kaydedin; yükselen bir trend genellikle temel modelin güncellendiği veya istem dağılımının kaydığı anlamına gelir.
- İşaretli videoyu asla silmeyin; model hata ayıklama ve post-mortem'ler için saklayın.
- Hassas içerik (insanlar, çocuklar, kamu figürleri) için, skora bakılmaksızın her videonun insan incelemesini zorunlu kılın.
