> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/19-complex-numbers/docs/en.md)

# Yapay Zeka İçin Karmaşık Sayılar

> -1'in karekökü hayali değildir. Döndürmelerin, frekansların ve işaret işleminin yarısının anahtarıdır.

**Tür:** Öğrenme
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 01-04 (doğrusal cebir, calculus)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Dikdörtgen ve kutupsal formda karmaşık aritmetik (toplama, çarpma, bölme, eşlenik) yapın
- Euler formülünü kullanarak karmaşık üsteller ile trigonometrik fonksiyonlar arasında dönüştürün
- Birlikin karmaşık kökleri kullanarak Ayrık Fourier Dönüşümünü uygulayın
- Karmaşık döndürmelerin transformer'larda RoPE ve sinüzoidal konumsal kodlamaların nasıl temelini oluşturduğunu açıklayın

## Sorun

Fourier dönüşümleri hakkında bir makale açıyorsunuz ve her yerde `i` var. Transformer konumsal kodlamalarına bakıyorsunuz ve farklı frekanslarda `sin` ve `cos` görüyorsunuz — karmaşık üstellerin gerçek ve sanal bölümleri. Kuantum hesaplama hakkında okuyorsunuz ve her şeyin karmaşık vektör uzaylarında ifade edildiğini görüyorsunuz.

Karmaşık sayılar soyut görünüyor. -1'in karekökü üzerine inşa edilmiş bir sayı sistemi matematiksel bir hile gibi geliyor. Ama hile değil. Döndürmelerin ve salınımların doğal dilidir. Bir şey döndüğünde, titreştiğinde veya salınım yaptığında, karmaşık sayılar doğru araçtır.

## Kavram

### Karmaşık sayı nedir?

Bir karmaşık sayının iki bölümü vardır: gerçek bölüm ve sanal bölüm.

```
z = a + bi

burada:
  a gerçek bölümdür
  b sanal bölümdür
  i sanal birimdir, i^2 = -1 ile tanımlanır
```

### Karmaşık Aritmetik

```
Toplama:    (a+bi) + (c+di) = (a+c) + (b+d)i
Çarpma:     (a+bi)(c+di) = (ac-bd) + (ad+bc)i
Bölme:      (a+bi)/(c+di) = [(a+bi)(c-di)] / (c²+d²)
```

### Euler Formülü

```
e^(iθ) = cos(θ) + i×sin(θ)
```

#### Açıklama
Bu formül, karmaşık üsteller ile trigonometrik fonksiyonlar arasındaki köprüdür. Fourier dönüşümünün temelini oluşturur.

### Karmaşık Döndürme

Karmaşık çarpma, bir vektörü döndürür.

```
z × e^(iθ) = z'i θ açısı kadar döndürür
```

### Ayrık Fourier Dönüşümü

Bir sinyali frekans bileşenlerine ayırır.

```python
import numpy as np

def dft(x):
    N = len(x)
    X = np.zeros(N, dtype=complex)
    for k in range(N):
        for n in range(N):
            X[k] += x[n] * np.exp(-2j * np.pi * k * n / N)
    return X
```

## Alıştırmalar

1. Karmaşık sayılarla temel aritmetik işlemleri yapın
2. e^(iπ) = -1 olduğunu doğrulayın
3. Basit bir sinyalin DFT'sini hesaplayın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Karmaşık sayı | "Hayali sayı" | Gerçek ve sanal bölümden oluşan sayı |
| Sanal birim (i) | "Kök(-1)" | i² = -1 tanımlı birim |
| Euler formülü | "Üstel-trigonometri köprüsü" | e^(iθ) = cos(θ) + i×sin(θ) |
| DFT | "Frekans analizi" | Sinyali frekans bileşenlerine ayıran dönüşüm |
| Frekans | "Titreşim hızı" | Sinyalin birim zamandaki tekrar sayısı |
| Faz | "Başlangıç noktası" | Sinüs dalgasının döngüdeki konumu |
