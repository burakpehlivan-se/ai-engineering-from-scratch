---
name: skill-residual-block-reviewer
description: Bir PyTorch artık bloğunu (residual block) atlama bağlantısı doğruluğu, BN yerleşimi, aktivasyon sırası ve şekil hizalaması için inceleyin
version: 1.0.0
phase: 4
lesson: 3
tags: [bilgisayarlı-gör, resnet, kod-içeleme, pytorch]
---

# Artık Blok (Residual Block) İnceleyicisi

Bir artık blok uyguladığını iddia eden herhangi bir PyTorch `nn.Module`'ü için odaklı bir inceleyici. Bozuk her ResNet yeniden yazımının neredeyse tamamından sorumlu dört hatayı yakalar.

## Ne zaman kullanılır

- Birisi özel bir BasicBlock veya Bottleneck yazdı ve kayıp NaN veya doğruluk takılı.
- Bir bloğu bir çerçeveden diğerine taşıyorsunuz ve eşdeğerliği doğrulamak istiyorsunuz.
- ResNet iç yapısını değiştiren bir PR'ı inceliyorsunuz (pre-activation, squeeze-excite, anti-alias).
- Bir model CIFAR boyutunda girdide sorunsuz gönderiliyor ama kısayol (shortcut) yanlış olduğu için ImageNet çözünürlüğünde çöküyor.

## Girdiler

- Kaynak metin veya içe aktarılabilir bir yol olarak PyTorch sınıf tanımı.
- İsteğe bağlı `variant`: `basic` | `bottleneck` | `preact` | `seblock`.

## Dört Kontrol

### 1. Kısayol şekil hizalaması

`stride != 1` veya `in_channels != out_channels` olan herhangi bir blok için, kısayol yolu **mutlaka** şekil eşleştiren bir modül olmalı — tipik olarak 1x1 evrişim artı BN. Bu durumda çıplak `nn.Identity()`, ileri geçişte garantili bir şekil uyumsuzluğu hatasıdır.

Tanısal:
```
[shortcut]
  detected:  nn.Identity | 1x1 Conv + BN | 1x1 Conv + BN + ReLU | diğer
  required:  (stride != 1 veya in_c != out_c) ise şekil eşleştiren Conv, değilse Identity
  verdict:   ok | wrong | unnecessarily heavy
```

### 2. Toplamaya göre BN yerleşimi

`out + shortcut(x)` toplaması, son ReLU'dan **önce** (post-activation, orijinal ResNet) gerçekleşmeli veya son ReLU tamamen yok olmalıdır (pre-activation ResNet v2). Ana dalda ReLU uygulayan ve ardından ham bir kısayol ekleyen bir blok, asimetrik bir aktivasyon aralığı üretir ve eğitime zarar verir.

Tanısal:
```
[activation order]
  pattern:  post-act (conv-BN-ReLU-conv-BN-add-ReLU) | pre-act (BN-ReLU-conv-BN-ReLU-conv-add) | diğer
  verdict:  ok | suspect
```

### 3. Evrişim katmanlarında bias

Hemen ardından BatchNorm gelen evrişimler `bias=False` olmalıdır. BN'nin beta'sı zaten bias'ı parametreleştirir, bu yüzden fazladan bir evrişim bias'ı parametre israf eder ve yakınsamayı yavaşlatabilir.

Tanısal:
```
[bias]
  BN ve bias=True olan evrişimler: <sayı>
  önerilen düzeltme: bu katmanlarda bias=False ayarla
```

### 4. Yerinde (in-place) ReLU ve autograd

Kısayola eklenecek tensör üzerindeki `nn.ReLU(inplace=True)`, artık toplama için gerekli olabilecek değerlerin üzerine yazar. Eklemeden önce yeni bir tensör üreten bir katman tarafından takip edilmeyen herhangi bir `inplace=True`'yu işaretle.

Tanısal:
```
[in-place]
  riskli yerinde işlemler: <liste>
  düzeltme: artık eklemeden önce inplace=False
```

## Rapor

```
[block-review]
  variant:       basic | bottleneck | preact | se | other
  shortcut:      ok | wrong | heavy
  activation:    ok | suspect
  bias-bn:       ok | bias=False gereken <N> evrişim
  in-place:      ok | <N> riskli işlem
  summary:       tek cümle
```

## Kurallar

- Bloğu yeniden yazma. Yalnızca raporla.
- Blok doğruysa, her yerde `ok` de ve dur. Öneri yok.
- Birden fazla şey yanlışsa, yukarıdaki sırayla listele (en yaygın çökme nedeni olduğu için önce kısayol).
- Kullanıcı belirttiğinde, kasıtlı bir pre-activation veya squeeze-excite varyantını asla yanlış olarak işaretleme.
