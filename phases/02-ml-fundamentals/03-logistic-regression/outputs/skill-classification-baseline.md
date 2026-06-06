---
name: skill-classification-baseline
description: Karmaşık modellere geçmeden önce güçlü bir sınıflandırma temeli oluştur
version: 1.0.0
phase: 2
lesson: 3
tags: [classification, logistic-regression, baseline, preprocessing]
---

# Sınıflandırma Temeli Kılavuzu

Karmaşık modelleri denemeden önce, lojistik regresyonla bir temel oluştur. Saniyeler içinde eğitilir, olasılık üretir ve tamamen yorumlanabilirdir. Şaşırtıcı sayıda gerçek dünya problemi bundan daha karmaşık bir şeye asla ihtiyaç duymaz.

## Karar Kontrol Listesi

1. Karar sınırı büyük olasılıkla doğrusal mı?
   - Evet: lojistik regresyon muhtemelen yeterli olacaktır
   - Hayır: yine de iyileşmeyi ölçmek için onu temel olarak istersin

2. Kaç özelliğin var?
   - 50'nin altında: standart lojistik regresyon yeterlidir
   - 50 ile 10.000 arası: L2 düzenlileştirme (Ridge) ekle
   - 10.000'in üzerinde (ör. TF-IDF metin özellikleri): L1 düzenlileştirme (Lasso) veya LinearSVC kullan

3. Veri kümesi dengesiz mi?
   - 5:1 oranının altı: muhtemelen ayarlama olmadan yeterlidir
   - 5:1 ile 50:1 arası: sklearn'de `class_weight="balanced"` kullan
   - 50:1'in üzerinde: sınıf ağırlıklandırmasını uygun metrikle (kesinlik, duyarlılık veya F1) birleştir

4. Özellikler farklı ölçeklerde mi?
   - Lojistik regresyondan önce her zaman standardize et. Gradyan tabanlı optimizasyon kullanır ve ölçeklenmemiş özellikler yakınsamayı yavaşlatır veya karar sınırını bozar.

5. Eksik değerler var mı?
   - Yerleştirmeden önce imputation (değer atama) yap. Lojistik regresyon NaN ile başa çıkamaz.
   - Sayısal sütunlar için medyan, kategorik olanlar için mod (en sık değer) imputation kullan.

## Lojistik regresyon ne zaman yeterlidir

- Çoğunlukla doğrusal özellik ilişkileri olan ikili sınıflandırma
- Olasılık çıktılarına ihtiyacın var (sadece sınıf etiketleri değil)
- Yorumlanabilirlik gerekli (katsayılar, standardizasyondan sonra özellik önem yönünü ve göreceli büyüklüğünü gösterir)
- Eğitim verisi küçük (yüzlerden düşük binlerce örneğe)
- Gerçek zamanlı sunum için hızlı bir modele ihtiyacın var (çıkarımda tek bir iç çarpım)
- Düzenleyici veya uyumluluk gereksinimleri açıklanabilirlik talep ediyor

## Ne zaman yükseltilmeli

- Doğruluk, hedefin çok altında plato yapıyor ve özellik mühendisliğini denedin
- Özellikler ile hedef arasındaki ilişki açıkça doğrusal değil (artık grafiklerini kontrol et)
- Büyük tablo verilerin var (10k+ satır): gradyan artırma (XGBoost veya LightGBM) dene
- Özellikler, polinom özelliklerinin yakalayamadığı karmaşık etkileşimlere sahip
- Görüntü, metin veya sıralı verilerin var: ham girdiler üzerinde lojistik regresyon çalışmayacaktır

## Sınıflandırma temeli için ön işleme adımları

1. **Eğitim/test bölmesi** önce, herhangi bir ön işlemeden önce. Bu veri sızıntısını önler.
2. **Eksik değerleri ele al**: sayısal için medyan imputation, kategorik için mod imputation.
3. **Kategorik olanları kodla**: düşük kardinalite (10 değerin altında) için one-hot, daha yüksek için target encoding. Target encoding'i yalnızca eğitim katlarında (out-of-fold encoding kullanarak) sızıntıyı önlemek için yerleştir.
4. **Sayısal olanları ölçeklendir**: StandardScaler (sıfır ortalama, birim varyans). Eğitim üzerinde yerleştir, ikisini de dönüştür.
5. **Lojistik regresyonu yerleştir** `C=1.0` ile (varsayılan düzenlileştirme).
6. **Değerlendir**: karışıklık matrisi, kesinlik, duyarlılık, F1. Yalnızca doğruluk değil.
7. **Eşiği ayarla**: varsayılan 0.5 nadiren en uygunudur. 0.1 ile 0.9 arasını tara ve kesinlik/duyarlılık önceliğinle eşleşen eşiği seç.

## Yaygın hatalar

- Dengesiz verilerde yalnızca doğruluğu değerlendirmek (çoğunluk sınıfını tahmin eden bir model yüksek puan alır ama işe yaramaz)
- Özellikleri ölçeklendirmeyi unutmak (ölçeklenmemiş özelliklerle lojistik regresyon yavaş eğitilir ve daha kötü bir çözüme yakınsar)
- Karar eşiğini ayarlamak için test setini kullanmak (doğrulama veya çapraz doğrulama kullan)
- Temeli atlayıp doğrudan XGBoost'a geçmek (yorumlanabilirliği kaybedersin ve referans noktan olmaz)
- Çoklu doğrusallığı (multicollinearity) kontrol etmemek (yüksek oranda ilişkili özellikler katsayı varyansını şişirir)

## Hızlı başvuru

| Senaryo | Model | Düzenlileştirme | Temel ayar |
|----------|-------|---------------|-------------|
| Az özellik, yorumlanabilir | LogisticRegression | L2 (varsayılan) | C=1.0 |
| Çok özellik, bazıları ilgisiz | LogisticRegression | L1 | penalty="l1", solver="saga" |
| Yüksek boyutlu seyrek (metin) | SGDClassifier | L1 veya ElasticNet | loss="log_loss" |
| Dengesiz sınıflar | LogisticRegression | L2 | class_weight="balanced" |
| Olasılıklara ihtiyaç | LogisticRegression | L2 | predict_proba() |
| Yalnızca sınıf etiketleri gerekli | LinearSVC | L2 | Büyük veri için LR'den daha hızlı |
