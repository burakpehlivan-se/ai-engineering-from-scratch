---
name: skill-freeze-inspector
description: Hangi parametrelerin eğitilebilir olduğunu, hangi BatchNorm katmanlarının eval modunda olduğunu ve optimize edicinin eğitilebilir parametreleri gerçekten tüketip tüketmediğini raporlayın
version: 1.0.0
phase: 4
lesson: 5
tags: [bilgisayarlı-gör, aktarmalı-öğrenme, hata-ayıklama, pytorch]
---

# Dondurma Denetçisi

Aktarmalı öğrenme hataları üç yerde gizlenir: dondurulması gereken ama dondurulmayan parametreler, eğitilebilir olması gereken ama eğitilebilir olmayan parametreler ve dondurma durumu değişmeden önce kurulan optimize ediciler. Bu beceri, üçünü de tek geçişte yüzeye çıkarır.

## Ne zaman kullanılır

- Bir parametre alt kümesinde `requires_grad` ayarladıktan hemen sonra.
- Bir ince ayar çalıştırmasının ilk eğitim adımından önce.
- `freeze_bn_stats` veya BN modunu değiştiren herhangi bir yardımcıyı çağırdıktan sonra.
- Doğrulama doğruluğu rastgele bir yerde takılı kaldığında ve gerçekte hiçbir şeyin eğitilmediğinden şüphelendiğinde.

## Girdiler

- `model`: bir PyTorch `nn. Module`.
- `optimizer`: eğitim için kullanılacak olan optimize edici.
- İsteğe bağlı `expected_frozen_prefixes`: dondurulması gereken parametre adı öneklerinin listesi (örn. `["conv1", "bn1", "layer1"]`).

## Adımlar

1. **Parametreleri yürü.** Her `(name, param)` için:
 - `requires_grad`'ı kaydet
 - `shape` ve `numel`'i kaydet

2. **Modülleri yürü.** Her modül için:
 - BatchNorm ise, eval modunda olup olmadığını ve afin parametrelerinin eğitilebilir olup olmadığını kaydet.

3. **Optimize ediciyi incele.** Her parametre grubu için:
 - `params` öğesini `id(p)` kümesine düzleştir.
 - `requires_grad == True` olan tüm parametreler için `id(p)` kümesiyle karşılaştır.

4. **Dört başarısızlık modunu tespit et**:
 - `leaked_train`: bir parametre `requires_grad=True`'ya sahip ancak optimize edicide görünmüyor (gradyan hesaplanıyor ama asla uygulanmıyor).
 - `ghost_train`: bir parametre optimize edicide görünüyor ancak `requires_grad=False` (optimize edici durumu israf; daha sonra requires_grad'ı yeniden etkinleştirirseniz hatalara da neden olabilir).
 - `bn_mismatch`: ya (a) bir BN katmanı eğitim modundayken (çalışma istatistiklerini biriktirir) afin parametreleri (`weight`, `bias`) dondurulmuş, ya da (b) bir BN katmanı eval modundayken (istatistikleri dondurulmuş) afin parametreleri eğitilebilir. Her iki durum da tutarsızdır ve neredeyse her zaman bir hatadır.
 - `expected_vs_actual`: `expected_frozen_prefixes`'te listelenen herhangi bir önekin hâlâ eğitilebilir bir parametresi var.

## Rapor

```
[freeze-inspector]
 model trainable params: <N>
 model frozen params: <N>
 batchnorm layers in eval mode: <count>
 batchnorm layers in train mode: <count>

[optimizer coverage]
 trainable params fed to optimizer: <M> of <N>
 leaked_train: <isim listesi> (eğitilebilir ama optimize edicide yok)
 ghost_train: <isim listesi> (optimize edicide ama dondurulmuş)

[bn audit]
 mismatched layers: <isim listesi>

[expectations]
 expected_frozen_prefixes: <...>
 violating params: <liste>

[verdict]
 ok | <en ciddi sorunun tek satır özeti>
```

## Kurallar

- Yalnızca parametre adlarını raporla; ağırlıkların kendisini asla yazdırma.
- Her listeyi parametre adına göre alfabetik olarak sırala.
- Optimize edici kapsamı %100 ise ve uyumsuzluk yoksa, `ok` döndür ve dur.
- `leaked_train` için, her zaman dondurma durumu değiştikten sonra optimize ediciyi yeniden oluşturmayı öner.
- `ghost_train` için, parametre grubunu kaldırmayı veya niyet eğitmekse `requires_grad=True` ayarlamayı öner.
