---
name: skill-imbalanced-data
description: Dengesiz sınıflandırma problemlerini ele alma karar kontrol listesi
version: 1.0.0
phase: 2
lesson: 17
tags: [imbalanced-data, smote, class-weights, threshold-tuning, evaluation]
---

# Dengesiz Veri Stratejisi

Dengesiz sınıflandırmayı ele almak için bir karar kontrol listesi. Problemin için doğru yaklaşımı seçmek için bu sırayı izle.

## Adım 1: Dengesizliği ölç

- Sınıf başına örnek say
- Dengesizlik oranını hesapla (çoğunluk / azınlık)
- Hafif: oran < 3:1 (ör. 70/30)
- Orta: oran 3:1 ile 20:1 arası (ör. 95/5)
- Şiddetli: oran > 20:1 (ör. 99/1)

## Adım 2: Doğru metriği seç

Dengesiz veri kümeleri için doğruluk yerine kesinlik (precision)/duyarlılık (recall)/F1 tercih et. Problemine göre seç:

| Durum | Birincil Metrik | İkincil Metrik |
|-----------|---------------|-----------------|
| Pozitifleri kaçırmak çok maliyetli (dolandırıcılık, hastalık) | Duyarlılık (Recall) | F2 skoru |
| Yanlış alarmlar maliyetli (spam filtresi, öneriler) | Kesinlik (Precision) | F0.5 skoru |
| İkisi de kabaca eşit derecede önemli | F1 skoru | MCC |
| Tek bir sıralama metriğine ihtiyacın var | AUPRC | AUC-ROC |
| Veri kümeleri arasında karşılaştırma yapman gerekiyor | MCC | AUPRC |

## Adım 3: Bir yeniden dengeleme stratejisi seç

### Dengesizlik şiddetine göre

| Dengesizlik | İlk Dene | İkinci Dene | Kaçın |
|-----------|-----------|------------|-------|
| Hafif (< 3:1) | Sınıf ağırlıkları | Eşik ayarı | Aşırı örnekleme (gerekli değil) |
| Orta (3:1 ile 20:1 arası) | SMOTE + sınıf ağırlıkları | Üzerine eşik ayarı | Az örnekleme (çok fazla veri kaybı) |
| Şiddetli (> 20:1) | SMOTE + sınıf ağırlıkları + eşik | Dengeli bagging ensemble | Yalnızca az örnekleme |

### Veri kümesi boyutuna göre

| Veri Kümesi Boyutu | Tercih Edilen Strateji | Neden |
|-------------|-------------------|--------|
| < 1.000 örnek | Aşırı örnekleme veya SMOTE | Çoğunluk verisini kaybedemez |
| 1.000 - 10.000 | SMOTE + eşik ayarı | k-NN için yeterli azınlık örneği |
| > 10.000 | Sınıf ağırlıkları veya az örnekleme | Hızlı, yeterli azınlık verisi |

## Adım 4: Tekniği uygula

### Sınıf ağırlıkları (her zaman ilk dene)
- sklearn'de: `class_weight='balanced'`
- Veri değişikliği gerekmez
- Herhangi bir kayıp tabanlı modelle çalışır
- Beklentide aşırı örneklemeye eşdeğerdir

### SMOTE
- Yalnızca eğitim verisine uygula (asla test/doğrulama)
- k=5 komşu kullan (varsayılan)
- En iyi sonuçlar için sınıf ağırlıklarıyla birleştir
- Sınır yakınındaki gürültülü sentetik noktalara dikkat et

### Eşik ayarı
- Modeli eğit, doğrulama seti üzerinde tahmin edilen olasılıkları al
- Eşikleri 0.05 ile 0.95 arasında tara
- Seçilen metriği en üst düzeye çıkaran eşiği seç
- Her zaman doğrulama verisinde ayarla, asla test verisinde değil

## Adım 5: Doğru şekilde doğrula

- Tabakalı (stratified) çapraz doğrulama kullan (her katta sınıf oranlarını korur)
- Metrikleri orijinal (yeniden örneklenmemiş) test seti üzerinde raporla
- Bölmeden önce asla SMOTE uygulama -- yalnızca eğitim katlarında
- "Her zaman çoğunluğu tahmin et" temeliyle karşılaştır

## Adım 6: Kaçınılması gereken yaygın hatalar

- Eğitim/test bölmesinden önce tüm veri kümesine SMOTE uygulamak (veri sızıntısı)
- Değerlendirme metriği olarak doğruluğu kullanmak
- Önce sınıf ağırlıklarını denememek (en basit yaklaşım, genellikle yeterli)
- Aşırı örnekleme yapıp sonra çapraz doğrulama yapmak (sentetik noktalar katlar arasında sızar)
- Eşik ayarını göz ardı etmek (ücretsiz performans, yeniden eğitim gerekmez)
- Küçük veri kümelerinde rastgele az örnekleme kullanmak (çok fazla veri atar)

## Hızlı Karar Ağacı

1. Dengesizlik oranı < 3:1 mi? -> Yalnızca sınıf ağırlıklarını dene
2. Veri kümesi > 10.000 örnek mi? -> Sınıf ağırlıkları + eşik ayarı
3. Veri kümesi < 1.000 örnek mi? -> SMOTE + sınıf ağırlıkları
4. Aksi halde -> SMOTE + sınıf ağırlıkları + eşik ayarı
5. Hala yeterli değil mi? -> Dengeli bagging ensemble
