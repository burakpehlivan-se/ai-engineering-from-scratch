> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/15-statistics-for-ml/docs/en.md)

# Makine Öğrenmesi İçin İstatistik

> İstatistik, modelinizin gerçekten çalışıp çalışmadığını yoksa sadece şanslı olup olmadığını anlamanızı sağlayan yoldur.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 06 (Olasılık ve Dağılımlar), 07 (Bayes Teoremi)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Sıfırdan tanımlayıcı istatistikleri, Pearson/Spearman korelasyonunu ve kovaryans matrislerini hesaplayın
- Hipotez testleri (t-testi, ki-kare) yapın ve p-değerlerini ve güven aralıklarını doğru yorumlayın
- Dağılım varsayımı olmadan herhangi bir metrik için güven aralıkları oluşturmak için bootstrap yeniden örnekleme kullanın
- Etki büyüklüğü ölçümleriyle istatistiksel anlamlılığı pratik anlamlılıktan ayırt edin

## Sorun

İki model eğittiniz. Model A test setinde 0.87 puan alıyor. Model B 0.89 puan alıyor. Model B'yi dağıtıyorsunuz. Üç hafta sonra, üretim metrikleri eskisinden kötü. Ne oldu?

Model B aslında Model A'yı geçmedi. 0.02'lik fark gürültüydü. Test setiniz çok küçüktü veya varyans çok yüksekti veya her ikisi birden. İyileştirme olarak süslenmiş rastgeleliği çıkardınız.

Bu sürekli olur. Kaggle liderlik tablosu sarsıntıları. Tekrar üretilemeyen makaleler. Birkaç yüz örneğe dayanarak kazananlar ilan eden A/B testleri. Kök neden her zaman aynıdır: biri istatistiği atladı.

İstatistik, sinyali gürültüden ayırt etmeniz için araçları verir. Bir farkın gerçek olup olmadığını, ne kadar kendine güvenebileceğinizi ve bir sonuca güvenmeden önce ne kadar veriye ihtiyacınız olduğunu söyler. Her ML hattı, her model karşılaştırması, her deney istatistik gerektirir. Onun olmadan, tahmin yürüyorsunuz.

## Kavram

### Tanımlayıcı İstatistikler: Verinizi Özetleme

Herhangi bir şeyi modellemeden önce verinizin neye benzediğini bilmeniz gerekir. Tanımlayıcı istatistikler, bir veri setini形状ını yakalayan birkaç sayıya sıkıştırır.

**Merkezi eğilim ölçüleri** "orta nokta nerede?" sorusunu yanıtlar

```
Ortalama: tüm değerlerin toplamı / sayı
          μ = (1/n) × Σ x_i

Mediana: sıralandığında orta değer
         Aykırı değerlerden kararlıdır. [1, 2, 3, 4, 1000] ise ortalama 202'dir ama mediana 3'tür

Mod: en sık görülen değer
```

**Yayılım ölçüleri** "veri ne kadar dağılmış?" sorusunu yanıtlar

```
Varyans: ortalamadan ortalama kare sapma
         σ² = (1/n) × Σ (x_i - μ)²

Standart sapma: varyansın karekökü
                 σ = √(σ²)

Aralık: max - min
```

### Korelasyon

İki değişken arasındaki ilişkinin gücünü ve yönünü ölçer.

```
Pearson korelasyonu: doğrusal ilişki (−1 ile 1 arası)
r = Σ((x_i - x̄)(y_i - ȳ)) / √(Σ(x_i - x̄)² × Σ(y_i - ȳ)²)

Spearman korelasyonu: monoton ilişki (sıralara dayalı)
```

### Hipotez Testleri

İstatistiksel olarak anlamlı bir fark olup olmadığını test eder.

```
Sıfır hipotezi (H₀): Fark yoktur
Alternatif hipotez (H₁): Vardır

p-değeri: H₀ doğruysa gözlenen verinin veya daha aşırısının olma olasılığı
p < 0.05 ise H₀ reddedilir (genellikle)
```

#### Açıklama
p-değeri, sonucun rastgele olma olasılığını ölçer. Düşük p-değeri, sonucun gerçek olma olasılığının yüksek olduğunu gösterir.

### Güven Aralıkları

Gerçek parametrenin bulunma olasılığı yüksek olan aralığı gösterir.

```
%95 güven aralığı: ortalama ± 1.96 × standart_hata
```

### Bootstrap

Örneklem dağılımını bilmeden güven aralıkları oluşturmak için kullanılır. Veriyi tekrar tekrar örnekleme yaparak dağılımı keşfeder.

## Alıştırmalar

1. Bir veri seti için tanımlayıcı istatistikleri hesaplayın
2. İki model arasındaki fark için t-testi yapın
3. Bootstrap kullanarak bir metrik için güven aralığı oluşturun

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Ortalama | "Orta değer" | Tüm değerlerin toplamının sayılması |
| Mediana | "Sıradaki değer" | Sıralandığında ortadaki değer |
| Varyans | "Dağınıklık" | Verinin ortalamadan ne kadar sapdığının ölçüsü |
| Korelasyon | "İlişki gücü" | İki değişken arasındaki ilişkinin gücü ve yönü |
| p-değeri | "Anlamlılık" | Sonucun rastgele olma olasılığı |
| Güven aralığı | "Tahmin aralığı" | Gerçek parametrenin bulunma olasılığı yüksek olan aralık |
| Bootstrap | "Yeniden örnekleme" | Veriden tekrar tekrar örnek alarak dağılımı keşfetme |
