---
name: skill-ensemble-builder
description: Probleminiz için doğru ensemble yöntemini seçin ve yapılandırın
version: 1.0.0
phase: 2
lesson: 11
tags: [ensemble, bagging, boosting, random-forest, xgboost, stacking]
---

# Ensemble Yöntemi Seçim Kılavuzu

Ensemble'ler, herhangi bir tek modelden daha iyi tahminler üretmek için birden çok modeli birleştirir. Soru her zaman şudur: hangi tür ensemble ve ne zaman?

## Karar Kontrol Listesi

1. Mevcut modelinizdeki ana sorun nedir?
   - Yüksek varyans (aşırı uyum): bagging (Rastgele Orman) kullan
   - Yüksek yanlılık (yetersiz uyum): boosting (Gradyan Artırma, XGBoost) kullan
   - İkisi de veya maksimum doğruluk istiyorsun: stacking kullan

2. Ne kadar verin var?
   - 1.000 satırın altında: Rastgele Orman (sağlam, yanlış yapılandırmak zor)
   - 1.000 ile 100.000 arası: XGBoost veya LightGBM (tablo için genel olarak en iyi)
   - 100.000'in üzerinde: LightGBM (en hızlı gradyan artırma, büyük veriyi iyi işler)

3. Ne kadar ayar süresi yatırabilirsin?
   - Minimum: Rastgele Orman varsayılanlarla (neredeyse her zaman çalışır)
   - Orta: XGBoost learning_rate=0.1 ile, erken durdurmayla n_estimators'ı ayarla
   - Maksimum: LightGBM veya XGBoost Bayesçi hiperparametre aramasıyla

4. Yorumlanabilirliğe ihtiyacın var mı?
   - Evet: tek karar ağacı veya küçük Rastgele Orman özellik önemiyle
   - Kısmi: SHAP değerleriyle gradyan artırma
   - Hayır: stacking veya derin ensemble'ler

5. Veri gürültülü ve birçok aykırı değer var mı?
   - Evet: Rastgele Orman (bagging gürültüye dayanıklıdır)
   - Hayır: gradyan artırma (temiz veride doğruluğu daha ileri taşıyabilir)

## Her yöntemin ne zaman kullanılacağı

**Rastgele Orman (Bagging)**: güvenli ilk seçimin. Bootstrap örnekler üzerinde birçok ağaç eğitir ve ortalamasını alır. Yanlılığı artırmadan varyansı azaltır. Orta veride aşırı uymak neredeyse imkansız. Minimum ayar gerekir: n_estimators=100-500 ayarla ve varsayılanları bırak.

**AdaBoost**: örnek yeniden ağırlıklandırmasıyla sıralı boosting. Basit temel öğrenicilerle (karar gövdeleri) iyi çalışır. Yanlış sınıflandırılan noktaları yukarı ağırlıklandırdığı için aykırı değerlere ve gürültülü etiketlere duyarlıdır. Pratikte büyük ölçüde gradyan artırma tarafından yerinden edilmiştir.

**Gradyan Artırma**: her yeni ağacı o ana kadar ensemblenin artıklarına (residuals) uydurur. Yanlılığı azaltır. Tablo verileri için en güçlü yöntem. Ayarlama gerektirir: learning_rate, n_estimators, max_depth, min_child_weight, subsample.

**XGBoost**: düzenlileştirme, ikinci dereceden optimizasyon ve sistem düzeyinde hızlandırmalarla gradyan artırma. Eksik değerleri doğal olarak işler. Tablo verileri üzerinde Kaggle yarışmaları ve üretim ML için varsayılan.

**LightGBM**: yaprak odaklı büyümeyle (seviye odaklı yerine) gradyan artırma. Büyük veri kümelerinde XGBoost'tan daha hızlı. Histogram tabanlı bölmeler kullanır. 50k satırın üzerindeki veri kümeleri için en iyi.

**CatBoost**: yerel kategorik özellik işlemeyle gradyan artırma. One-hot kodlamaya gerek yok. Birçok kategorik özelliğiniz olduğunda iyi.

**Stacking**: birden çok çeşitli temel modelin tahminleri üzerinde bir meta-öğrenici eğitir. Mümkün olan en iyi doğruluğa ihtiyacın olduğunda ve hesaplama gücün olduğunda kullan. Sızıntıdan kaçınmak için temel model tahminlerini her zaman çapraz doğrulama yoluyla üret.

**Voting (oylama)**: en basit ensemble. Hard voting (çoğunluk sınıfı) veya soft voting (ortalama olasılıklar). Meta-öğrenici olmadan 2-3 çeşitli modeli birleştirmenin hızlı bir yolu.

## Yaygın hatalar

- Erken durdurma olmadan gradyan artırma kullanmak (çok fazla tur çalışmasına izin verirsen aşırı uyar)
- learning_rate'i çok yüksek ayarlamak (0.3'ün üzeri genellikle kararsızlığa neden olur)
- Gradyan artırma için max_depth'i ayarlamamak (sınırsız veya çok derin ağaçların varsayılanı aşırı uyar)
- Hep aynı tipte modellerle stacking (çeşitlilik stacking'in amacıdır)
- Gürültülü veride AdaBoost kullanmak (aykırı değerler her turda daha yüksek ağırlık alır)
- Rastgele Orman'ın yetersiz uyumu düzelteceğini beklemek (varyansı azaltır, yanlılığı değil)

## Yönteme göre ayar öncelikleri

**Rastgele Orman:**
1. n_estimators: 100-500 (daha fazlası nadiren daha kötüdür, sadece daha yavaş)
2. max_depth: Yok (ağaçların tam büyümesine izin ver) veya hız için 10-20'de sınırla
3. max_features: Sınıflandırma için "sqrt", regresyon için "log2" veya n/3

**XGBoost / LightGBM:**
1. learning_rate: 0.01-0.3 (daha fazla ağaç için hesaplama gücün varsa düşük daha iyi)
2. n_estimators: tahmin etmek yerine bir doğrulama setinde erken durdurma kullan
3. max_depth: 3-8 (6 ile başla)
4. min_child_weight / min_data_in_leaf: 1-20 (yüksek olan aşırı uyumu önler)
5. subsample: 0.7-1.0
6. colsample_bytree: 0.7-1.0
7. reg_alpha (L1) ve reg_lambda (L2): 0-10

## Hızlı başvuru

| Yöntem | Azalttığı | Hız | Ayar çabası | En iyi |
|--------|---------|-------|--------------|----------|
| Rastgele Orman | Varyans | Hızlı | Düşük | Gürültülü veri, hızlı temel |
| AdaBoost | Yanlılık | Hızlı | Düşük | Basit temel öğreniciler, temiz veri |
| Gradyan Artırma | Yanlılık | Orta | Yüksek | Tablo verileri, yarışmalar |
| XGBoost | İkisi de | Hızlı | Yüksek | Üretim tablo ML |
| LightGBM | İkisi de | En hızlı | Yüksek | Büyük veri kümeleri (50k+ satır) |
| CatBoost | İkisi de | Orta | Orta | Birçok kategorik özellik |
| Stacking | İkisi de | Yavaş | Yüksek | Maksimum doğruluk, çeşitli modeller |
| Voting | Varyans | Hızlı | Yok | 2-3 modelin hızlı birleşimi |
