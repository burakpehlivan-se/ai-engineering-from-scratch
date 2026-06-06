---
name: skill-naive-bayes-chooser
description: Sınıflandırma görevin için doğru Naive Bayes varyantını seç
phase: 2
lesson: 14
---

Sen olasılıksal sınıflandırma konusunda uzmansın. Biri bir Naive Bayes varyantı seçmesi gerektiğinde, onu bu karar sürecinden geçir.

## Karar Kontrol Listesi

### Adım 1: Özelliklerin nelerdir?

- **Kelime sayıları veya TF-IDF değerleri** -> MultinomialNB
- **Sürekli ölçümler (sıcaklık, boy, sensör okumaları)** -> GaussianNB
- **İkili göstergeler (kelime var/yok, onay kutusu durumları)** -> BernoulliNB
- **Karışık tipler** -> Alt kümelere ayır veya tümünü tek bir tipe dönüştür

### Adım 2: Ne kadar verin var?

- **1.000 örneğin altında**: Naive Bayes güçlü bir seçimdir. Güçlü önceliği (bağımsızlık varsayımı) aşırı uyumu engeller.
- **1.000 ile 50.000 arası örnek**: NB hala rekabetçidir. Lojistik regresyonla karşılaştır.
- **50.000'in üzerinde örnek**: Lojistik regresyon veya gradyan artırma muhtemelen NB'den daha iyi performans gösterecektir. NB'yi temel olarak kullan.

### Adım 3: Smoothing ayarla

- alpha=1.0 (Laplace smoothing) ile başla.
- Yeterli veriniz varsa ve doğruluk düşükse, alpha=0.1 veya 0.01 dene.
- Model aşırı uyuyorsa (eğitim >> test doğruluğu), alpha'yı 5.0 veya 10.0'a yükselt.
- Smoothing'i her zaman çapraz doğrulamayla doğrula, tek bir eğitim/test bölmesiyle değil.

### Adım 4: Varsayımları kontrol et

- **MultinomialNB**: Özellikler negatif olmamalıdır. Negatif değerleriniz varsa, kaydır veya GaussianNB kullan.
- **GaussianNB**: Özellikler her sınıf içinde kabaca çan şeklinde (normal dağılıma yakın) olduğunda en iyi çalışır. Histogramlarla kontrol et.
- **BernoulliNB**: Önce özelliklerini ikilileştir. Eşiği dikkatlice seç (metin için: var=1, yok=0).

## Yaygın Hatalar

1. **Metin verisinde GaussianNB kullanmak.** Kelime sayıları Gaussian değildir. MultinomialNB kullan.
2. **Laplace smoothing'i unutmak.** Tek bir görülmemiş kelime tüm olasılığı sıfırlar. Her zaman yumuşat.
3. **Olasılık çıktılarına güvenmek.** NB olasılıkları kötü kalibre edilmiştir. Sıralama için kullan, güven skorları olarak değil. Kalibre edilmiş olasılıklara ihtiyacın varsa, CalibratedClassifierCV kullan.
4. **Sınıf dengesizliğini göz ardı etmek.** NB öncelikleri sınıf frekanslarını yansıtır. %99 negatif ve %1 pozitif ile, öncelik olabilirliği (likelihood) bastırır. Öncelikleri manuel olarak ayarla veya yeniden örnekle.

## Hızlı Başvuru

| Soru | MultinomialNB | GaussianNB | BernoulliNB |
|----------|:---:|:---:|:---:|
| Metin sınıflandırması? | Evet | Hayır | Belki (kısa metin) |
| Sürekli özellikler? | Hayır | Evet | Hayır |
| İkili özellikler? | Hayır | Hayır | Evet |
| Çok hızlı eğitim gerekli? | Evet | Evet | Evet |
| Küçük eğitim seti? | İyi | İyi | İyi |
| Kalibre edilmiş olasılıklar gerekli? | Hayır | Hayır | Hayır |

## Naive Bayes Ne Zaman KULLANILMAZ

- Özellikler yüksek düzeyde ilişkili ve ilişkileri işleyen bir model için yeterli veriniz var (lojistik regresyon, gradyan artırma)
- Mümkün olan en iyi doğruluğa ihtiyacın var ve bol miktarda verin var
- Özellikleriniz görüntüler, diziler veya grafikler (sinir ağları kullan)
- Özellik etkileşimlerini yakalayan bir modele ihtiyacın var (ağaç tabanlı yöntemler kullan)
