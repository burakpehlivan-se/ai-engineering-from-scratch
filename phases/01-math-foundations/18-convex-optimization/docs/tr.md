> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/18-convex-optimization/docs/en.md)

# Konveks Optimizasyon

> Konveks sorunların bir vadisi vardır. Sinir ağınsa milyonlarcası. Farkı bilmek önemlidir.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 04 (ML İçin Calculas), 08 (Optimizasyon)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Bir fonksiyonun konveks olup olmadığını tanım, ikinci türev ve Hessian kriterleriyle test edin
- Newton yöntemini uygulayın ve ikinci dereceden yakınsamasını gradyan inişiyle karşılaştırın
- Lagrange çarpanlarını kullanarak kısıtlı optimizasyon problemlerini çözün ve KKT koşullarını yorumlayın
- Neden sinir ağı kayıp manzaraları konveks olmasına rağmen SGD'nin hala iyi çözümler bulduğunu açıklayın

## Sorun

Ders 08'de gradyan inişi, momentum ve Adam'ı öğrendiniz. Bu optimize ediciler her yüzeyde aşağı iner. Ama garanti vermezler. Konveks olmayan bir manzarada gradyan inişi kötü bir yerel minimuma inebilir, bir eyer noktasında takılabilir veya sonsuza kadar salınım yapabilirsiniz. Buna rağmen kullandınız çünkü sinir ağıları konveks değildir ve alternatif yoktur.

Ama makine öğrenmesindeki birçok sorun konvekstir. Doğrusal regresyon, lojistik regresyon, SVM'ler, LASSO, ridge regresyonu. Bunlar için daha güçlü bir şey vardır: matematiksel garantilerle optimizasyon. Konveks bir sorunun tam olarak bir vadisi vardır. Aşağı inen herhangi bir algoritma global minimuma ulaşır. Yeniden başlatmaya gerek yok. Öğrenme hızı programına gerek yok. Duaya gerek yok.

## Kavram

### Konveks kümeler

Bir küme S, S'deki her iki nokta için aralarındaki doğru parçasının da tamamen S içindeyse konvekstir.

```
Konveks:                    Konveks değil:
Daire, kare, üçgen          Yıldız, hilal, halka
```

### Konveks fonksiyonlar

Bir fonksiyon, grafiğinin üzerindeki her iki nokta arasındaki doğru parçasının grafikte veya yukarısında kaldığında konvekstir.

```
Konveks:                     Konveks değil:
f(x) = x²                   f(x) = x³
f(x) = |x|                  f(x) = sin(x)
```

#### Açıklama
Konveks fonksiyonların tek bir minimumu vardır. Bu, optimizasyonu kolaylaştırır.

### Gradyan İnişinde Konvekslik

Konveks sorunlarda gradyan inişi:
- Herhangi bir başlangıç noktasından başlayabilir
- Global minimuma garanti edilir
- Öğrenme hızı programı gerekmez

```python
import numpy as np

# Konveks fonksiyon: f(x) = x²
def f(x): return x**2
def df(x): return 2*x

x = 10.0  # Herhangi bir başlangıç
for _ in range(100):
    x = x - 0.1 * df(x)  # Gradyan inişi

print(f"Minimum: {x:.6f}")  # ~0.000000
```

### Newton Yöntemi

İkinci türevi kullanarak daha hızlı yakınsar. Konveks sorunlarda mükemmeldir.

```
x_yeni = x_eski - f''(x)⁻¹ × f'(x)
```

#### Açıklama
Newton yöntemi, gradyan inişinden çok daha hızlı yakınsar ama her adımda Hessian matrisini tersine çevirmeyi gerektirir (pahalıdır).

### Kısıtlı Optimizasyon

Lagrange çarpanlarıyla kısıtlamalar eklenir.

```
L(x, λ) = f(x) + λ × g(x)
```

KKT koşulları: optimalitenin gerekli koşulları.

## Alıştırmalar

1. f(x) = x² + 4x + 4 fonksiyonunun konveks olup olmadığını test edin
2. Newton yöntemini gradyan inişiyle karşılaştırın
3. Basit bir kısıtlı optimizasyon sorununu Lagrange ile çözün

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Konveks | "Kase şeklinde" | Tek bir minimumu olan fonksiyon |
| Konveks olmayan | "Engebeli" | Birden fazla minimumu olan fonksiyon |
| Eyer noktası | "Düz bölge" | Gradyanın sıfır olduğu ama minimum olmadığı nokta |
| Newton yöntemi | "Hızlı çözüm" | İkinci türevi kullanan hızlı optimizasyon |
| KKT koşulları | "Kısıt optimizasyonu" | Kısıtlı optimizasyonun optimalite koşulları |
| Düzenleme | "Basitleştirme" | Basit modelleri tercih eden kısıt |
