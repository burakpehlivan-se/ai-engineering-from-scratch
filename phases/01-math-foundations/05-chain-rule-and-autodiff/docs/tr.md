> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/05-chain-rule-and-autodiff/docs/en.md)

# Zincir Kuralı ve Otomatik Türev

> Zincir kuralı, her öğrenen sinir ağının arkasındaki motor.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 04 (Türevler ve Gradyanlar)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- İşlemleri kaydeden ve ters mod otomatik türevle gradyanları hesaplayan minimal bir otomatik gradyan motoru (Value sınıfı) oluşturun
- Topolojik sıralama kullanarak hesaplama grafiği üzerinden ileri ve geri geçişler uygulayın
- Sadece sıfırdan yazılmış otomatik gradyan motoru kullanarak XOR üzerinde çok katmanlı bir algılayıcı oluşturun ve eğitin
- Sayısal sonlu farklarla karşılaştırma yaparak otomatik türevin doğruluğunu doğrulayın

## Sorun

Basit fonksiyonların türevlerini hesaplayabilirsiniz. Ama bir sinir ağı basit bir fonksiyon değildir. Yüzlerce fonksiyonun birleşimidir: matris çarpımı, sapma ekleme, aktivasyon uygulama, tekrar matris çarpımı, softmax, çapraz entropi kaybı. Çıktı, bir fonksiyonun fonksiyonunun fonksiyonudur.

Ağı eğitmek için, her bir ağırlığa göre kaybın gradyanına ihtiyacınız vardır. Bunu milyonlarca parametre için elle yapmak imkansızdır. Sayısal olarak (sonlu farklar) yapmak çok yavaştır.

Zincir kuralı size matematiği verir. Otomatik türev size algoritmayı verir. Birlikte, tek bir ileri besleme süresine orantılı bir sürede keyfi fonksiyon bileşimlerinden kesin gradyanlar hesaplamanızı sağlar.

Bu, PyTorch, TensorFlow ve JAX'ın nasıl çalıştığıdır. Siz bunun küçültülmüş bir versiyonunu sıfırdan oluşturacaksınız.

## Kavram

### Zincir Kuralı

Eğer `y = f(g(x))` ise, `y`'nin `x`'e göre türevi:

```
dy/dx = dy/dg * dg/dx = f'(g(x)) * g'(x)
```

Zincir boyunca türevleri çarpın. Her bağlantı kendi yerel türevini katkıda bulunur.

Örnek: `y = sin(x^2)`

```
g(x) = x^2       g'(x) = 2x
f(g) = sin(g)     f'(g) = cos(g)

dy/dx = cos(x^2) * 2x
```

Daha derin bileşimler için, zincir uzar:

```
y = f(g(h(x)))

dy/dx = f'(g(h(x))) * g'(h(x)) * h'(x)
```

Bir sinir ağının her katmanı bu zincirdeki bir bağlantıdırr.

### Hesaplama Grafikleri

Bir hesaplama grafiği zincir kuralını görsel yapar. Her işlem bir düğüm olur. Veri grafik boyunca ileri akar. Gradyanlar geriye akar.

```mermaid
graph LR
    A[girdi] --> B[x²]
    B --> C[sin(x²)]
    C --> D[kayıp]
    D --> C2[geri yayılım]
    C2 --> B2[geri yayılım]
    B2 --> A2[gradyan]
```

İleri besleme: x → x² → sin(x²) → kayıp
Geri yayılım: kayıp → cos(x²) → 2x → gradyan

### Otomatik Türev (Autograd)

Otomatik türev, zincir kuralını otomatik olarak uygulayan bir sistemdir. Siz ileri beslemeyi yazarsınız, çerçeve tüm türevleri hesaplar.

PyTorch'ta:
```python
import torch

x = torch.tensor(2.0, requires_grad=True)
y = x ** 2 + 3 * x + 1
y.backward()  # Türevleri hesapla
print(x.grad)  # dy/dx = 2x + 3 = 7.0
```

#### Açıklama
`requires_grad=True`, PyTorch'a bu tensörün türevinin alınacağını söyler. `.backward()` çağrısı tüm gradyanları hesaplar.

## Alıştırmalar

1. `Value` sınıfını kullanarak y = x^3 + 2x^2 + x fonksiyonunun türevini hesaplayın
2. XOR problemini çok katmanlı bir algılayıcıyla çözün
3. Gradyan kontrolü ile otomatik türevin doğruluğunu doğrulayın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Zincir kuralı | "Türev çarpımı" | Bileşik fonksiyonların türevini hesaplama kuralı |
| Otomatik türev | "Otomatik gradyan" | Türevleri otomatik olarak hesaplayan sistem |
| İleri besleme | "İleriye doğru hesaplama" | Girdiden çıktıya doğru hesaplama |
| Geri yayılım | "Geriye doğru türev" | Kayıttan ağırlıklara doğru gradyan hesaplama |
| Hesaplama grafiği | "İşlem diyagramı" | İşlemleri düğüm olarak gösteren yönlü graf |
| Topolojik sıralama | "İşlem sırası" | Graf düğümlerinin doğru sırada işlenmesini sağlayan sıralama |
