---
name: skill-svm-kernel-chooser
description: Probleminiz için doğru SVM çekirdeğini seçin ve C ile gamma'yı ayarlayın
version: 1.0.0
phase: 2
lesson: 5
tags: [svm, kernel, classification, hyperparameter-tuning]
---

# SVM Çekirdek Seçimi Kılavuzu

SVM'ler iki seçimle tanımlanır: çekirdek (karar sınırının şeklini belirler) ve düzenlileştirme parametreleri (marj genişliği ile sınıflandırma hataları arasındaki dengeyi kontrol eder). Bunları doğru ayarlamak, işe yaramaz bir model ile güçlü bir model arasındaki farktır.

## Karar Kontrol Listesi

1. Veriler doğrusal olarak ayrılabilir mi (veya yakını mı)?
 - Evet: doğrusal çekirdek kullan. Daha hızlı ve daha yorumlanabilir.
 - Hayır: 2. adıma geç.

2. Özellik sayısı örnek sayısına göre nasıl?
 - Özellikler >> örnekler (ör. TF-IDF ile metin): doğrusal çekirdek kullan. Yüksek boyutlu veriler genellikle doğrusal olarak ayrılabilir. RBF, fayda sağlamadan karmaşıklık ekler.
 - Örnekler >> özellikler (ör. 10-50 özellikli tablo verileri): RBF çekirdek varsayılan seçimdir.

3. Karar sınırının pürüzsüz olması bekleniyor mu?
 - Pürüzsüz, sürekli sınır: RBF çekirdek
 - Polinom şeklinde sınır: polinom çekirdek (derece 2 veya 3 ile başla)
 - Alan bilgisi belirli etkileşim terimleri öneriyorsa: eşleşen dereceli polinom çekirdek

4. Veri kümesi ne kadar büyük?
 - 10.000 örneğin altında: her çekirdek çalışır, RBF güvenli varsayılan
 - 10.000 ile 100.000 arası: doğrusal çekirdek veya LinearSVC (primal formülasyon, epoch başına O(n))
 - 100.000'in üzerinde: çekirdek SVM kullanma. Doğrusal SVM, gradyan artırma veya sinir ağlarına geç.

5. Özellikleri ölçeklendirdin mi?
 - SVM'ler özellik ölçeklendirmesi gerektirir. Yerleştirmeden önce her zaman standardize et (sıfır ortalama, birim varyans). Ölçeklenmemiş özellikler marj geometrisini bozar.

## Çekirdek seçim akış şeması

```
Başla
 |
 v
Özellikler > 1000 veya özellikler >> örnekler?
 Evet --> Doğrusal çekirdek (hız için LinearSVC)
 Hayır --> Veri kümesi < 10k örnek?
 Evet --> Önce RBF'yi dene (en iyi genel amaçlı çekirdek)
 Hayır --> Doğrusal çekirdek (çekirdek SVM'ler O(n^2) ile O(n^3))
```

RBF iyi çalışmazsa, polinom derece 2-3'ü dene. O da başarısız olursa, problem SVM'lere uygun olmayabilir.

## C ayarı (düzenlileştirme)

C, yanlış sınıflandırmaların cezasını kontrol eder. Düzenlileştirme gücüyle ters orantılıdır.

| C değeri | Etki | Ne zaman kullanılır |
|---------|--------|-------------|
| 0.001 - 0.01 | Geniş marj, çok ihlale izin verilir | Gürültülü veri, genelleme isteniyor |
| 0.1 - 1.0 | Dengeli | İyi başlangıç aralığı |
| 10 - 1000 | Dar marj, az ihlal | Temiz veri, yüksek doğruluk gerekli |

Ayar stratejisi:
- C=1.0 ile başla
- Log ölçeğinde ara: [0.001, 0.01, 0.1, 1, 10, 100, 1000]
- En iyi değeri seçmek için çapraz doğrulama kullan
- En iyi C aralığın kenarındaysa, o yönde aralığı genişlet

## Gamma ayarı (RBF çekirdek)

Gamma, tek bir eğitim noktasının etkisinin ne kadar uzağa ulaştığını kontrol eder. Gauss'un genişliğini tanımlar.

| gamma değeri | Etki | Ne zaman kullanılır |
|-------------|--------|-------------|
| Küçük (0.001) | Her nokta geniş bir alanı etkiler. Pürüzsüz, basit sınır | Yetersiz uyum veya az özellik |
| Orta (auto: 1/n_features) | sklearn varsayılanı. Makul başlangıç noktası | Genel kullanım |
| Büyük (10+) | Her nokta yalnızca yakındaki noktaları etkiler. Karmaşık, kıvrımlı sınır | Aşırı uyum riski |

Ayar stratejisi:
- gamma="scale" (1 / (n_features * X.var()), sklearn varsayılanı) ile başla
- Log ölçeğinde ara: [0.001, 0.01, 0.1, 1, 10]
- Düşük gamma + yüksek C aşırı uymaya meyilli
- Yüksek gamma + düşük C yetersiz uymaya meyilli

## C ve gamma'nın birlikte ayarlanması

C ve gamma etkileşir. Her zaman birlikte ayarla, bağımsız değil.

Önerilen yaklaşım:
1. Kaba grid araması: C [0.01, 0.1, 1, 10, 100], gamma [0.001, 0.01, 0.1, 1, 10] (25 kombinasyon)
2. En iyi bölgeyi bul
3. En iyi bölgenin etrafında ince grid araması (ör. C [5, 10, 20, 50], gamma [0.05, 0.1, 0.2])
4. Her yerde 5-katlı çapraz doğrulama kullan

## Yaygın hatalar

- Yüksek boyutlu seyrek veride RBF çekirdek kullanmak (doğrusal daha iyi ve 100x daha hızlı)
- Özellikleri ölçeklendirmeyi unutmak (SVM'deki en yaygın tek hata)
- Gürültülü veride C'yi çok yüksek ayarlamak (sınırı öğrenmek yerine gürültüyü ezberler)
- 50k örnekten büyük veri kümelerinde çekirdek SVM kullanmak (eğitim süresi yasaklayıcıdır)
- C ve gamma'yı birlikte ayarlamamak (birbirini telafi ederler)
- Polinom derece 5+ varsaymak (aşırı agresif uyar, önce 2 veya 3'ü dene)

## Hızlı başvuru

| Çekirdek | Ne zaman kullanılır | Temel parametreler | Eğitim karmaşıklığı |
|--------|------------|----------------|-------------------|
| Doğrusal | Metin/TF-IDF, çok özellik, büyük veri | Yalnızca C | Epoch başına O(n) |
| RBF | Genel amaçlı, 10k örneğin altında | C, gamma | O(n^2) ile O(n^3) |
| Polinom | Bilinen polinom ilişkileri | C, derece, coef0 | O(n^2) ile O(n^3) |
| Sigmoid | Nadiren yararlı (iki katmanlı sinir ağına denk) | C, gamma, coef0 | O(n^2) ile O(n^3) |
