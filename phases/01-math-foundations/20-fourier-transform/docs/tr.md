> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/20-fourier-transform/docs/en.md)

# Fourier Dönüşümü

> Her sinyal sinüs dalgalarının toplamıdır. Fourier dönüşümü hangileri olduğunu söyler.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 01-04, 19 (karmaşık sayılar)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Sıfırdan DFT uygulayın ve O(N log N) Cooley-Tukey FFT ile karşılaştırın
- Frekans katsayılarını yorumlayın: sinyalden genlik, faz ve güç spektrumunu çıkarın
- Konvolüsyon teoremini uygulayarak FFT çarpımıyla konvolüsyon yapın
- Fourier frekans ayrıştırmasını transformer konumsal kodlamaları ve CNN konvolüsyon katmanlarıyla bağlayın

## Sorun

Bir ses kaydı zaman boyunca basınç ölçümlerinin bir dizisidir. Bir hisse fiyatı günler boyunca değerlerin bir dizisidir. Bir görüntü uzay boyunca piksel yoğunluklarının bir ızgarasıdır. Bunların tümü zaman alanındaki (veya uzay alanındaki) veridir. Bazı indeks boyunca değişen değerler görürsünüz.

Ama birçok desen zaman alanında görünmezdir. Bu ses sinyali saf bir ton mu yoksa bir akor mu? Bu hisse fiyatı haftalık bir döngüye sahip mi? Bu görüntü tekrarlayan bir doku mu içeriyor? Bu sorular frekans içeriğiyle ilgilidir ve zaman alanı bunu gizler.

Fourier dönüşümü, veriyi zaman alanından frekans alanına dönüştürür. Bir sinyali alır ve farklı frekanslardaki sinüs dalgalarına ayrıştırır. Her sinüs dalgasının bir genliği (ne kadar güçlü) ve bir fazı (nerede başladığı) vardır. Fourier dönüşümü her ikisini de söyler.

## Kavram

### DFT tanımı

N örnek x[0], x[1], ..., x[N-1] verildiğinde, Ayrık Fourier Dönüşümü N frekans katsayısı üretir:

```
X[k] = Σ_{n=0}^{N-1} x[n] × e^(-2πi×k×n/N)

k = 0, 1, ..., N-1 için
```

Her X[k] bir karmaşık sayıdır. Büyüklüğü |X[k]| frekans k'nın genliğini söyler. Faz açısı angle(X[k]) o frekansın faz_ofsetini söyler.

### FFT (Hızlı Fourier Dönüşümü)

DFT'nin O(N²) yerine O(N log N) çalışan versiyonu.

```python
import numpy as np

# NumPy ile FFT
sinyal = np.random.randn(1024)
fft_sonuc = np.fft.fft(sinyal)
frekanslar = np.fft.fftfreq(len(sinyal))

# Genlik spektrumu
genlik = np.abs(fft_sonuc)

# Faz spektrumu
faz = np.angle(fft_sonuc)
```

### Konvolüsyon Teoremi

Zaman alanındaki konvolüsyon, frekans alanındaki çarpımdır.

```
f * g = F⁻¹(F(f) × F(g))
```

#### Açıklama
Bu, CNN'lerin neden bu kadar hızlı olduğunun temelidir. Konvolüsyonu FFT ile yapmak çok daha hızlıdır.

### ML'de Fourier Kullanımı

- **CNN'ler:** Konvolüsyon katmanları frekans alanında çarpım yapar
- **Transformerlar:** Konumsal kodlamalar frekans ayrıştırması kullanır
- **Ses modelleri:** Spektrogramlar frekans temsilleridir
- **Zaman serisi:** Periyodik desenleri bulmak için

## Alıştırmalar

1. Basit bir sinüs dalgasının DFT'sini hesaplayın ve frekansını bulun
2. NumPy FFT ile kendi DFT'nizi karşılaştırın
3. Bir ses sinyalinin frekans spektrumunu görselleştirin

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Fourier dönüşümü | "Frekans analizi" | Sinyali frekans bileşenlerine ayıran dönüşüm |
| FFT | "Hızlı frekans analizi" | DFT'nin O(N log N) çalışan hızlı algoritması |
| Genlik | "Güç" | Frekans bileşeninin büyüklüğü |
| Faz | "Başlangıç zamanı" | Sinüs dalgasının döngüdeki konumu |
| Konvolüsyon | "Filtreleme" | Sinyal üzerinde kaydırarak filtre uygulama |
| Spektrogram | "Frekans zaman grafiği" | Zamana göre frekans dağılımını gösteren görüntü |
