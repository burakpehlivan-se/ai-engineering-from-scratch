> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/06-probability-and-distributions/docs/en.md)

# Olasılık ve Dağılımlar

> Olasılık, belirsizliği ifade etmek için yapay zekanın kullandığı dildir.

**Tür:** Öğrenme
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 01-04
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Bernoulli, kategorik, Poisson, uniform ve normal dağılımlar için sıfırdan PMF ve PDF'leri uygulayın
- Beklenen değeri, varyansı hesaplayın ve Gauss'un neden hakim olduğunu açıklamak için Merkezi Teoremi kullanın
- Sayısal kararlılık hilesiyle (maks logit'i çıkararak) softmax ve log-softmax fonksiyonları oluşturun
- Logit'lerden çapraz entropi kaybını hesaplayın ve negatif log-olabilirlikle bağlayın

## Sorun

Bir sınıflandırıcı `[0.03, 0.91, 0.06]` çıktısı veriyor. Bir dil modeli 50.000 adaydan bir sonraki kelimeyi seçiyor. Bir difüzyon modeli öğrenilen dağılımlardan örnekleme yaparak görüntüler üretiyor. Bunların hepsi çalışan olasılıktır.

Bir modelin her tahmini bir olasılık dağılımıdır. Her kayıp fonksiyonu, tahmin edilen dağılımın gerçek olanından ne kadar uzak olduğunu ölçer. Her eğitim adımı, bir dağılımın diğerine daha çok benzemesi için parametreleri ayarlar. Olasılık olmadan, tek bir ML makalesini okuyamaz, tek bir modeli hata ayıklayamaz veya eğitim kaybınızın neden NaN olduğunu anlayamazsınız.

## Kavram

### Olaylar, Örneklem Alanları ve Olasılık

Örneklem alanı S, tüm olası sonuçların kümesidir. Bir olay, örneklem alanının bir alt kümesidir. Olasılık, olayları 0 ile 1 arasında sayılara eşler.

```
Para atışı:
  S = {YAZI, TURA}
  P(YAZI) = 0.5,  P(TURA) = 0.5

Tek zar atışı:
  S = {1, 2, 3, 4, 5, 6}
  P(çift) = P({2, 4, 6}) = 3/6 = 0.5
```

Üç aksiyom tüm olasılığı tanımlar:
1. Her olay A için P(A) >= 0
2. P(S) = 1 (bir şey her zaman olur)
3. A ve B aynı anda oluşamıyorsa P(A veya B) = P(A) + P(B)

Diğer her şey (Bayes teoremi, beklentiler, dağılımlar) bu üç kuraldan türetilir.

### Koşullu Olasılık ve Bağımsızlık

P(A|B), B olduktan sonra A'nın olasılığıdır.

```
P(A|B) = P(A ve B) / P(B)

Örnek: iskambil destesi
  P(Kral | Resimli Kart) = P(Kral ve Resimli Kart) / P(Resimli Kart)
                         = (4/52) / (12/52)
                         = 4/12 = 1/3
```

İki olay, birini bilmek diğerini etkilemediğinde bağımsızdır:

```
P(A ve B) = P(A) × P(B)    (bağımsız ise)
```

### Beklenen Değer ve Varyans

Beklenen değer (ortalama): tüm olası sonuçların olasılık ağırlıklı ortalaması.

```
E[X] = Σ x_i × P(x_i)

Zar örneği:
E[X] = 1×(1/6) + 2×(1/6) + 3×(1/6) + 4×(1/6) + 5×(1/6) + 6×(1/6) = 3.5
```

Varyans: dağılımın ne kadar geniş olduğunu ölçer.

```
Var(X) = E[(X - μ)²] = E[X²] - (E[X])²
```

#### Açıklama
Düşük varyans = sonuçlar ortalamaya yakın. Yüksek varyans = sonuçlar yaygın.

### Yaygın Dağılımlar

| Dağılım | Kullanım | Özellik |
|---------|----------|---------|
| Bernoulli | İkili sonuçlar (0/1) | Tek deneme |
| Kategorik | Çoklu sonuçlar | Tek deneme, k>2 sonuç |
| Poisson | Olay sayıları | Zaman aralığında |
| Uniform | Eşit olasılıklı | Tüm sonuçlar eşit |
| Normal (Gauss) | Sürekli değişkenler | Çan eğrisi, Merkezi Teorem |

### Softmax

Softmax, ham skorları olasılık dağılımına dönüştürür.

```
softmax(z_i) = exp(z_i) / Σ exp(z_j)
```

#### Açıklama
Tüm değerler pozitiftir ve toplamları 1'dir. Sınıflandırıcıların çıktısında kullanılır.

Sayısal kararlılık için:
```python
import numpy as np

def softmax(z):
    z = z - np.max(z)  # Sayısal kararlılık için maks çıkar
    exp_z = np.exp(z)
    return exp_z / exp_z.sum()
```

### Çapraz Entropi Kaybı

Tahmin edilen olasılık dağılımı ile gerçek dağılım arasındaki farkı ölçer.

```
L = -Σ y_true × log(y_pred)
```

#### Açıklama
Tahmin ne kadar doğruysa kayıp o kadar düşüktür. Doğru sınıfa %100 güvenen bir modelin kaybı 0'dır.

## Alıştırmalar

1. Normal dağılım için PDF'yi sıfırdan kodlayın
2. Softmax'ı numpy ile uygulayın ve çıktıların toplamının 1 olduğunu doğrulayın
3. Farklı tahminler için çapraz entropi kaybını hesaplayın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Olasılık | "Şans" | Bir olayın gerçekleşme olasılığı (0 ile 1 arasında) |
| Dağılım | "Yayılım" | Olası sonuçların ve olasılıklarının listesi |
| Beklenen değer | "Ortalama" | Olasılık ağırlıklı ortalama |
| Varyans | "Dağınıklık" | Dağılımın genişliğinin ölçüsü |
| Normal dağılım | "Çan eğrisi" | Doğanın ve istatistiğin en yaygın dağılımı |
| Softmax | "Olasiğila dönüştürücü" | Ham skorları olasılık dağılımına dönüştüren fonksiyon |
| Çapraz entropi | "Fark ölçümü" | İki olasılık dağılımı arasındaki farkın ölçüsü |
