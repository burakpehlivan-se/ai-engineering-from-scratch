---
name: skill-gradient-computation
description: Yaygın ML kayıp fonksiyonlarının gradyanlarını hesapla ve doğru türev yaklaşımını seç
version: 1.0.0
phase: 1
lesson: 4
tags: [calculus, gradients, backpropagation]
---

# ML için Gradyan Hesaplama

Sinir ağlarında kullanılan kayıp fonksiyonlarının, aktivasyon fonksiyonlarının ve katman işlemlerinin gradyanlarını hesaplamak için pratik bir başvuru.

## Karar Kontrol Listesi

1. Fonksiyon basit temel yapılardan mı (kuvvet, exp, log, trigonometrik) oluşuyor? Analitik türevleri ve zincir kuralını (chain rule) kullan.
2. Fonksiyon özel veya kara kutu (black-box) bir işlem mi? Sayısal türev kullan: `(f(x+h) - f(x-h)) / (2h)`, h = 1e-7.
3. Fonksiyon PyTorch/JAX'ta tensor işlemlerinden mi oluşuyor? Autograd (otomatik türev) halleder. Sayısal kontrol ile doğrula.
4. Bir skaler kaybın bir ağırlık matrisine göre gradyanını mu hesaplaman gerekiyor? Hesaplama grafiğinde (computation graph) zincir kuralını düğüm düğüm uygula.
5. Türevi alınamaz bir işlem mi var (argmax, yuvarlama, örnekleme)? Düz-arka tahmincisi (straight-through estimator) veya yeniden parametrelendirme (reparameterization) hilesi kullan.

## Her yaklaşımın ne zaman kullanılacağı

| Yaklaşım | Ne zaman kullanılır | Maliyet |
|---|---|---|
| Analitik (elle türetilmiş) | Basit fonksiyonlar, autograd çıktısını doğrulama | Çalışma zamanında bedava |
| Sayısal (sonlu farklar) | Hata ayıklama, gradyan kontrolü, kara kutu fonksiyonlar | n parametre için 2n ileri geçiş |
| Otomatik türev (autograd) | Herhangi bir türevlenebilir hesaplama grafiği (varsayılan) | Tek bir geriye geçiş |
| Sembolik (SymPy, Mathematica) | Makaleler için kapalı form (closed-form) gradyan türetme | Yalnızca derleme zamanı |

## Hızlı başvuru: yaygın türevler

| Fonksiyon | f(x) | f'(x) | ML bağlamı |
|---|---|---|---|
| MSE kaybı | (1/n) sum(y_hat - y)^2 | (2/n)(y_hat - y) | Regresyon |
| Çapraz entropi (ikili) | -(y log(p) + (1-y) log(1-p)) | p - y (sigmoid sonrası) | İkili sınıflandırma |
| Çapraz entropi (çok sınıflı) | -log(p_true_class) | p - one_hot(y) (softmax sonrası) | Çok sınıflı sınıflandırma |
| Sigmoid | 1 / (1 + e^(-x)) | sigma(x) * (1 - sigma(x)) | Çıktı geçitleri, ikili çıktı |
| Tanh | (e^x - e^(-x)) / (e^x + e^(-x)) | 1 - tanh(x)^2 | Gizli aktivasyonlar (eski) |
| ReLU | max(0, x) | x > 0 ise 1, x < 0 ise 0 | Varsayılan gizli aktivasyon |
| Sızıntılı (Leaky) ReLU | max(0.01x, x) | x > 0 ise 1, x < 0 ise 0.01 | Ölü nöronlardan kaçınma |
| GELU | x * Phi(x) | Phi(x) + x * phi(x) | Transformer'lar |
| Softmax_i | e^(x_i) / sum(e^(x_j)) | i=j için s_i(1 - s_i), i!=j için -s_i*s_j | Çıktı katmanı (Jacobian) |
| Log-softmax | x_i - log(sum(e^(x_j))) | i. giriş için 1 - softmax(x_i) | Sayısal olarak kararlı CE |
| Doğrusal katman | y = Wx + b | dL/dW = dL/dy * x^T, dL/db = dL/dy | Her katman |
| L2 düzenlileştirme (regularization) | lambda * sum(w^2) | 2 * lambda * w | Ağırlık azalması (weight decay) |
| L1 düzenlileştirme | lambda * sum(\|w\|) | lambda * sign(w) | Seyreklik (sparsity) |

## Yaygın hatalar

- Batch ortalamalı kayıplarda (MSE, çapraz entropi) 1/n çarpanını unutmak. Gradyan batch boyutuyla ölçeklenir.
- Softmax gradyanını vektör olarak hesaplamak, oysa gerçekte bir Jacobian matrisidir. Çapraz entropi + softmax birleştiğinde gradyan (p - y) olarak sadeleşir ve tam Jacobian'dan kaçınılır.
- Zincir kuralını yanlış sırada uygulamak. Kayıptan geriye doğru çalış: dL/dW = dL/dy * dy/dW.
- Sayısal türevler için çok büyük (h = 0.1) veya çok küçük (h = 1e-15) h kullanmak. float64 için h = 1e-7'de kal.
- ReLU'nun tam olarak x = 0'da tanımsız gradyana sahip olduğunu unutmak. Pratikte 0 veya 0.5 olarak ayarla.

## Gradyan kontrolü reçetesi (gradient checking)

```
For each parameter w:
 numeric_grad = (loss(w + h) - loss(w - h)) / (2h)
 auto_grad = backward pass value
 relative_error = |numeric - auto| / max(|numeric|, |auto|, 1e-8)
 assert relative_error < 1e-5
```

1e-3'ün üzerindeki göreli hata, bir şeylerin yanlış olduğu anlamına gelir. 1e-5 ile 1e-3 arasında, araştır.
