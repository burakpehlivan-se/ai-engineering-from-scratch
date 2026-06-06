---
name: skill-classification-diagnostics
description: Bir karışıklık matrisi (confusion matrix) ve sınıf adları verildiğinde, sınıf başına başarısızlıkları yüzeye çıkarın ve en etkili tek düzeltmeyi önerin
version: 1.0.0
phase: 4
lesson: 4
tags: [bilgisayarlı-gör, sınıflandırma, değerlendirme, hata-ayıklama]
---

# Sınıflandırma Tanılamaları

Karışıklık matrisleri için bir okuma merceği. Toplam doğruluk, bir sınıflandırıcının çalıştığını söyler. Karışıklık matrisi, *henüz ne bilmediğini* söyler.

## Ne zaman kullanılır

- Eğitilmiş bir sınıflandırıcının doğrulama performansına ilk bakış.
- Sırada neyi değiştireceğinize karar vermek için eğitim çalıştırmaları arasında.
- Bir modeli göndermeden önce: hiçbir kritik sınıfın sessizce başarısız olmadığını doğrulamak.
- Genel doğruluğun bir puan düştüğü ve nedenini bilmeniz gereken bir üretim regresyonunu ayıklamak.

## Girdiler

- `cm`: CxC karışıklık matrisi (satırlar = gerçek, sütunlar = tahmin edilen).
- `labels`: aynı sırada C sınıf adı listesi.
- İsteğe bağlı `class_priors`: sınıf başına eğitim sıklığı (varsayılan olarak `cm` satır toplamları).

## Adımlar

1. **Sınıf başına metrikleri hesapla.** Sıfıra bölmeyi, o sınıf için metrik tanımsız olarak ele al ve `n/a` olarak raporla; asla sessizce 0 ile değiştirme.
   - precision_i = cm[i,i] / sum(cm[:, i])   (sınıf hiç tahmin edilmediğinde tanımsız)
   - recall_i    = cm[i,i] / sum(cm[i, :])   (sınıfın temel gerçeklik örneği olmadığında tanımsız)
   - f1_i        = 2 * p * r / (p + r)        (herhangi bir bileşen tanımsız olduğunda tanımsız)

2. **F1'e göre en kötü üç sınıfı sırala.** Karışıklık matrisi üçten az sınıfa sahipse, mevcut olduğu kadar sırala. Tüm metrikleri tanımsız olan sınıfları hariç tut.

3. **Satır başına en üst köşegen dışı hücreyi bul** — bu sınıftan en yaygın çalan sınıf. `true -> predicted` olarak raporla.

4. **Her en kötü sınıf için başarısızlık modunu sınıflandır.** Etiketin tekrarlanabilir olması için şu nicel eşikleri kullan:
   - `ambiguity` — başka bir sınıfla çift yönlü karışıklık: hem `cm[i,j] / sum(cm[i, :]) >= 0.15` hem de `cm[j,i] / sum(cm[j, :]) >= 0.15`.
   - `imbalance` — sınıfın eğitim sayısı, en üst karıştırıcısının `< 0.5x`'i.
   - `label_noise` — `|precision_i - recall_i| >= 0.2` ve sınıf dengesizlik / belirsizlik yollarında değil.
   - `systematic` — hiçbir tek karıştırıcı, bu sınıfın hatalarının 0.2 payını aşmıyor; hatalar üç veya daha fazla sınıfa yayılmış.

5. **En etkili tek bir sonraki eylemi öner**:
   - `ambiguity` -> ayırt edici örnekler topla veya sentezle, ayırt edici özelliği koruyan hedefli veri artırma ekle.
   - `imbalance` -> azınlık sınıfını aşırı örnekle veya sınıf ağırlıklı kayıp uygula.
   - `label_noise` -> sınıfın tabakalı bir örneğini denetle; diğer herhangi bir değişiklikten önce yanlış etiketleri düzelt.
   - `systematic` -> sınıf için veriyi artır veya bu sınıfın kaybına daha yüksek ağırlıkla ince ayar yap.

## Rapor

```
[diagnostics]
  aggregate accuracy: X.XX
  macro F1:           X.XX

[top-3 worst classes]
  1. class <name>  F1 = X.XX  prec = X.XX  rec = X.XX
     top confusion: <name> -> <other>  (N cases)
     failure mode:  ambiguity | imbalance | label_noise | systematic
     action:        <tek cümle>

  2. ...
  3. ...

[recommendation]
  single biggest lever: <sınıfı ve düzeltmeyi adlandıran tek cümle>
```

## Kurallar

- En fazla üç sınıf döndür. Daha fazlası sinyali gizler.
- Her en kötü sınıf için baskın karıştırıcıyı adlandır; asla "birçok şeyle karıştırır" olarak özetleme.
- Her öneriyi karışıklık matrisi kanıtına dayandır. Hangi sınıf olduğunu belirtmeden genel "daha fazla veri ekle" yok.
- Kesinlik ve duyarlılık 0.2'den fazla anlaşmazlığa düştüğünde, her zaman etiket gürültüsünü aday olarak işaretle — gerçek sınıflar genellikle eğitimden sonra hizalanmış P ve R'ye sahiptir.
