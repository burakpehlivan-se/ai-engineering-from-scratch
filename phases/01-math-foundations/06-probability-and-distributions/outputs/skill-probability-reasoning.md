---
name: skill-probability-reasoning
description: Verilen bir ML problemi için doğru olasılık dağılımını seç
version: 1.0.0
phase: 1
lesson: 6
tags: [probability, distributions, modeling]
---

# Olasılık Dağılımı Seçimi

Veri modellediğinde, kayıp fonksiyonları tasarladığında veya öncül (prior) dağılımlar belirlerken doğru dağılımı nasıl seçersin.

## Karar Kontrol Listesi

1. Sonuç ayrık mı (kategoriler, sayımlar) yoksa sürekli mi (ölçümler, skorlar)?
2. Sonuç sınırlı mı (ör. [0, 1]) yoksa sınırsız mı?
3. Kaç olası sonuç var? İki mi? k mı? Sonsuz mu?
4. Veriler simetrik mi yoksa çarpık mı?
5. Olaylar bağımsız mı yoksa ilişkili mi?
6. Bir hız mı, sayım mı, oran mı yoksa ölçüm mü modelliyorsun?

## Dağılım karar ağacı

```
Değişken ayrık mı?
 Evet --> Yalnızca 2 sonuç? --> Bernoulli (p)
 | k sonuç, tek deneme? --> Categorical (p1...pk)
 | k sonuç, n deneme? --> Multinomial (n, p1...pk)
 | n denemede başarı sayısı? --> Binomial (n, p)
 | Aralık başına olay sayısı? --> Poisson (lambda)
 | İlk başarıya kadar deneme sayısı? --> Geometric (p)
 | r başarıya kadar deneme sayısı? --> Negative Binomial (r, p)
 Hayır --> Simetrik, çan şeklinde? --> Normal (mu, sigma)
 | Pozitif değerler, sağa çarpık? --> Log-normal veya Exponential
 | [0, 1] aralığında sınırlı? --> Beta (alpha, beta)
 | Pozitif değerler, esnek şekil? --> Gamma (alpha, beta)
 | Olaylar arasındaki süre? --> Exponential (lambda)
 | Ağır kuyruklar mı gerekli? --> Student's t (nu) veya Cauchy
 | Çok değişkenli, çan şeklinde? --> Multivariate Normal
 | Bir simplekste mi (toplamı 1)? --> Dirichlet (alpha)
```

## Gerçek dünya ML senaryolarını dağılımlarla eşleştirme

| Senaryo | Dağılım | Parametreler |
|---|---|---|
| İkili sınıflandırma çıktısı | Bernoulli | p = sigmoid(logit) |
| Çok sınıflı sınıflandırma çıktısı | Categorical | p = softmax(logits) |
| Dil modellerinde token tahmini | Sözlük üzerinde Categorical | p softmax'tan gelir |
| Piksel yoğunluğu (normalize) | Beta veya Uniform [0, 1] | Görüntü istatistiklerine bağlı |
| Bir belgedeki kelime sayısı | Poisson | lambda = ortalama kelime sayısı |
| Kullanıcı istekleri arasındaki süre | Exponential | lambda = istek hızı |
| Ölçüm hatası | Normal | mu = 0, sigma veriden |
| Ağırlık ilk değer ataması | Normal veya Uniform | Kaiming/Xavier kuralları |
| VAE latent uzayı öncülü | Standart Normal | mu = 0, sigma = 1 |
| Oranlar üzerinde Bayesçi öncül | Beta | alpha, beta inanca göre |
| Kategori ağırlıkları üzerinde Bayesçi öncül | Dirichlet | alpha vektörü |
| Regresyon hedeflerinde gürültü | Normal | mu = 0, sigma tahmin edilir |
| Aykırı değerlere dayanıklı regresyon | Student's t | düşük serbestlik derecesi |
| Süre/ömür modellenmesi | Weibull veya Gamma | şekil ve ölçek |
| Belge başına konu dağılımı (LDA) | Dirichlet | seyrek için alpha < 1 |

## Dağılımlar yanlış gittiğinde

- Verilerin sert bir alt sınırı varken Normal kullanmak (ör. fiyatlar, mesafeler). Normal, negatif değerlere sıfır olmayan olasılık atar. Bunun yerine log-normal veya gamma kullan.
- Varyans ortalamadan farklıyken Poisson kullanmak. Poisson, ortalama = varyans varsayar. Varyans > ortalamaysa, negatif binom kullan.
- Çok sınıflı problemler için Bernoulli kullanmak. Bernoulli kesinlikle ikilidir. k > 2 için categorical kullan.
- Gözlemler ilişkiliyken bağımsızlık varsaymak. Zaman serileri, mekansal veriler ve gruplanmış veriler bağımsızlığı ihlal eder. Otoregresif veya hiyerarşik modeller kullan.

## Yaygın hatalar

- PDF değerlerini olasılıklarla karıştırmak. Bir PDF 1'i aşabilir. Olasılık, PDF'in bir aralık üzerinde integralinden gelir.
- Softmax çıktılarının bağımsız Bernoulli olasılıkları değil, kategorik olasılıklar olduğunu unutmak. Yapıları gereği toplamları 1'dir.
- Alan bilgisine sahipken düzgün (uniform) bir öncül kullanmak. Bilgilendirici öncüller, iyi seçilmişlerse varyansı düşürür ve sonucu yanlı kılmaz.
- Log-olasılıkları olasılıkmış gibi değerlendirmek. Log-olasılıklar her zaman negatiftir (veya sıfır). Toplamları 1 değildir.

## Hızlı başvuru: dağılım özellikleri

| Dağılım | Destek | Ortalama | Varyans | Temel özellik |
|---|---|---|---|---|
| Bernoulli(p) | {0, 1} | p | p(1-p) | En basit ayrık |
| Binomial(n, p) | {0..n} | np | np(1-p) | n Bernoulli toplamı |
| Poisson(lam) | {0, 1, 2, ...} | lam | lam | Ortalama = varyans |
| Normal(mu, s^2) | (-inf, inf) | mu | s^2 | Verilen ort/varyans için maks. entropi |
| Exponential(lam) | [0, inf) | 1/lam | 1/lam^2 | Belleksiz (memoryless) |
| Beta(a, b) | [0, 1] | a/(a+b) | ab/((a+b)^2(a+b+1)) | Binomial'a eşlenik |
| Gamma(a, b) | (0, inf) | a/b | a/b^2 | Poisson'a eşlenik |
| Dirichlet(alpha) | Simpleks | alpha_i/sum | (formüle bakın) | Categorical'a eşlenik |
