---
name: skill-evaluation
description: Sınıflandırma ve regresyon modelleri için değerlendirme stratejisi kontrol listesi
version: 1.0.0
phase: 2
lesson: 9
tags: [evaluation, metrics, cross-validation, model-selection]
---

# Model Değerlendirme Stratejisi

Herhangi bir ML modelini doğru değerlendirmek için bir kontrol listesi. En yaygın değerlendirme hatalarından kaçınmak için bu sırayı izle.

## Adım 1: Verileri doğru böl

- Herhangi bir ön işlemeden önce böl (ölçeklendirme, imputation, kodlama)
- Sınıflandırma görevleri için tabakalı (stratified) bölmeler kullan
- Sonunda tam olarak bir kez dokunacağın bir test seti ayır
- Küçük veri kümeleri için, tek bir bölme yerine 5-katlı veya 10-katlı çapraz doğrulama kullan
- Zaman serileri için, zamana dayalı bölmeler kullan (asla karıştırma)

## Adım 2: Doğru metriği seç

### Sınıflandırma

| Durum | Bu metriği kullan | Neden |
|-----------|----------------|-----|
| Dengeli sınıflar, basit karşılaştırma | Doğruluk (accuracy) | Yorumlaması kolay, sınıflar eşit olduğunda anlamlı |
| Yanlış pozitifler maliyetli (spam filtresi, dolandırıcılık uyarıları) | Kesinlik (precision) | İşaretlenen öğelerin gerçekten pozitif olduğunu ölçer |
| Yanlış negatifler maliyetli (kanser taraması, güvenlik) | Duyarlılık (recall) | Gerçek pozitiflerin ne kadarını yakaladığını ölçer |
| Kesinlik ve duyarlılık dengelenecek | F1 Skoru | Harmonik ortalama, aşırı dengesizliği cezalandırır |
| Modelleri eşikler arasında karşılaştırma | AUC-ROC | Eşikten bağımsız sıralama kalitesi |
| Dengesiz veri | F1, AUC-ROC veya PR-AUC | Dengesiz sınıflarla doğruluk yanıltıcıdır |

### Regresyon

| Durum | Bu metriği kullan | Neden |
|-----------|----------------|-----|
| Standart regresyon, aykırı değerler kabul edilebilir | RMSE | Hedefle aynı birimlerde, büyük hataları cezalandırır |
| Aykırı değerlere dayanıklı değerlendirme | MAE | Tüm hataları eşit davranır, aykırı değerler tarafından domine edilmez |
| Modelleri farklı ölçeklerde karşılaştırma | R-kare | Normalleştirilmiş 0-1 ölçeği (açıklanan varyans oranı) |
| İşletme dolar tutarları gerektiriyor | MAE veya RMSE | Doğrudan hata büyüklüğü olarak yorumlanabilir |

## Adım 3: Temelleri oluştur

Modelini değerlendirmeden önce, temel performansı hesapla:
- Sınıflandırma: çoğunluk sınıfı tahmincisi (her zaman en yaygın sınıfı tahmin et)
- Regresyon: eğitim hedefinin ortalamasını her zaman tahmin et
- Bu temelleri yenemeyen herhangi bir model öğrenmiyor demektir

## Adım 4: Çapraz doğrulama yap

- Kararlı tahminler için K-katlı (K=5 veya K=10) kullan
- Sınıflandırma için tabakalı K-katlı kullan
- Katlar arasında ortalama ve standart sapma raporla
- Ortalama=0.85 ve std=0.02 olan bir model, ortalama=0.87 ve std=0.10 olandan daha güvenilirdir

## Adım 5: Modelleri istatistiksel olarak karşılaştır

- Anlamlılığı kontrol etmeden en yüksek ortalık skora sahip modeli seçme
- Çapraz doğrulama katları arasında eşleştirilmiş t-testi kullan
- |t| < 2.78 ise (K=5, df=4, p<0.05 için), fark şans eseri olabilir
- Performans farkları anlamlı olmadığında daha basit olan modeli düşün

## Adım 6: Yaygın hataları kontrol et

- Veri sızıntısı: test veri bilgisi eğitime aktı mı? (bölmeden önce ölçeklendirme, hedeften türetilmiş özellikler)
- Sınıf dengesizliği: doğruluk, kötü azınlık sınıfı performansını mı gizliyor?
- Aşırı uyum: eğitim ve doğrulama performansı arasındaki fark büyük mü?
- Çok fazla değerlendirme: test setine birden fazla kez baktın mı?

## Adım 7: Son performansı raporla

- Eğitim + doğrulama birleşik üzerinde eğit
- Ayrılan test setinde tam olarak bir kez değerlendir
- Seçilen metriği mümkünse güven aralıklarıyla raporla
- Temel karşılaştırmasını belirt (rastgelelik/ortalama'dan ne kadar daha iyi)
