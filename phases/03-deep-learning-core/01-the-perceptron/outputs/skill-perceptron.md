---
name: skill-perceptron
description: Algılayıcı (perceptron) desenini ve tek katmanlı ile çok katmanlı mimarilerin ne zaman kullanılacağını anlayın
version: 1.0.0
phase: 3
lesson: 1
tags: [algılayıcı, sinir-ağları, sınıflandırma, derin-öğrenme]
---

# Algılayıcı (Perceptron) Deseni

Bir algılayıcı, girdilerin ağırlıklı toplamını artı bir bias (önyargı) değerini hesaplar, ardından ikili bir çıktı üretmek için bir basamak fonksiyonu uygular. Sinir ağlarının temel yapı taşıdır.

```
output = step(w1*x1 + w2*x2 + ... + wn*xn + bias)
```

## Tek bir algılayıcının yeterli olduğu durumlar

- Sorun doğrusal olarak ayrılabilir: iki sınıfı düz bir çizgi (veya hiperdüzlem) ayırabilir
- Mantık kapıları: AND, OR, NOT, NAND
- Basit eşik kararları: "Skor X'in üzerinde mi?"
- Örtüşmeyen iki bölgede kümelenen veriler üzerinde ikili sınıflandırıcılar

## Birden çok kata ihtiyaç duyduğunuz durumlar

- Sorun doğrusal olarak ayrılabilir değil: sınıfları ayıran tek bir çizgi yok
- XOR ve eşlik (parity) problemleri
- "Bu ama şu değil" akıl yürütmesi gerektiren görevler (koşul kombinasyonları)
- Gerçek dünya sınıflandırması: görüntü, metin, ses — neredeyse her zaman doğrusal değil

## Karar kontrol listesi

1. Verinizi çizin veya inceleyin. Sınıflar arasına tek bir düz sınır çizebilir misiniz?
 - Evet: tek algılayıcı çalışır
 - Hayır: en az iki kata ihtiyacınız var
2. Sorun, daha basit doğrusal kararların AND/OR birleşimine ayrıştırılabilir mi?
 - Bu ayrıştırma size minimum ağ yapısını söyler
 - XOR = (A OR B) AND (NOT (A AND B)) = 2 katmanda 3 algılayıcı
3. İkiden fazla sınıfı olan sorunlar için sınıf başına bir çıktı düğümü gerekir

## Eğitim kuralı

```
error = expected - predicted
weight_new = weight_old + learning_rate * error * input
bias_new = bias_old + learning_rate * error
```

Tahmin doğruysa, hiçbir şey değişmez. Yanlışsa, ağırlıklar hatayı azaltacak şekilde kayar. Bu yalnızca tek katmanlı algılayıcılar için çalışır. Çok katmanlı ağlar geri yayılım (backpropagation) gerektirir.

## Sık yapılan hatalar

- Doğrusal olmayan desenleri tek bir algılayıcıyla öğrenmeye çalışmak (asla yakınsamaz)
- Öğrenme hızını çok yüksek ayarlamak (ağırlıklar salınır) veya çok düşük ayarlamak (eğitim çok uzun sürer)
- Bias terimini unutmak (onsuz, karar sınırı orijinden geçmek zorundadır)
- Algılayıcı yakınsamasını (doğrusal olarak ayrılabilir veri için garantili) genel sinir ağı yakınsamasıyla (garanti değil) karıştırmak
