> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/02-vectors-matrices-operations/docs/en.md)

# Vektörler, Matrisler ve İşlemler

> Her sinir ağı, ekstra adımlarla yapılmış matris çarpımıdır.

**Tür:** Uygulama
**Diller:** Python, Julia
**Ön Koşullar:** Faz 1, Ders 01 (Doğrusal Cebir Sezgisi)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Eleman bazlı işlemler, matris çarpımı, transpoz, determinant ve ters ile bir Matris sınıfı oluşturun
- Eleman bazlı çarpımı matris çarpımından ayırt edin ve her birinin ne zaman uygulanacağını açıklayın
- Sadece sıfırdan yazılmış Matris sınıfı kullanarak tek bir yoğun sinir ağı katmanı (`relu(W @ x + b)`) uygulayın
- Yayma kurallarını ve sinir ağı çerçevelerinde sapma eklemenin nasıl çalıştığını açıklayın

## Sorun

Bir sinir ağı oluşturmak istiyorsunuz. Kodu okuyorsunuz ve şunu görüyorsunuz:

```
cikisi = aktivasyon(agirliklar @ girdi + sapma)
```

O `@` matris çarpımıdır. `agirliklar` bir matristir. `girdi` bir vektördür. Bu işlemlerin ne yaptığını bilmiyorsanız, bu satır sihire dönüştürür. Biliyorsanız, bir katmanın tüm ileri beslemesini üç işlemde anlatır.

Modelinizin işlediği her görüntü piksel değerlerinden oluşan bir matristir. Her kelime gömmesi bir vektördür. Her sinir ağının her katmanı bir matris dönüşümüdür. Matris işlemlerinde akıcı olmadan yapay zeka sistemleri oluşturamazsınız, tıpkı değişkenleri anlamadan kod yazamayacağınız gibi.

Bu ders o akıcılığı sıfırdan oluşturur.

## Kavram

### Vektörler: Sayıların düzenli listeleri

Bir vektör, yönü ve büyüklüğü olan bir sayı listesidir. Yapay zekada vektörler veri noktalarını, özellikleri veya parametreleri temsil eder.

```
v = [3, 4]        -- 2B vektör
w = [1, 0, -2]    -- 3B vektör
```

2B vektör `[3, 4]` düzlemde (3, 4) koordinatlarına yönlenir. Uzunluğu (büyüklüğü) 5'tir (3-4-5 üçgeni).

### Matrisler: Sayı ızgaraları

Bir matris 2B bir ızgaradır. Satırlar ve sütunlar. m x n matrisi m satır ve n sütun içerir.

```
A = | 1  2  3 |     -- 2x3 matris (2 satır, 3 sütun)
    | 4  5  6 |
```

Sinir ağlarında ağırlık matrisleri, girdi vektörlerini çıktı vektörlerine dönüştürür. 784 girdili ve 128 çıkışlı bir katman 128x784 ağırlık matrisi kullanır.

### Neden şekiller önemli

Matris çarpımının katı bir kuralı vardır: `(m x n) @ (n x p) = (m x p)`. İç boyutlar eşleşmelidir.

```
(128 x 784) @ (784 x 1) = (128 x 1)
  ağırlıklar       girdi       çıktı

İç boyutlar: 784 = 784  -- geçerli
```

PyTorch'ta şekil uyumsuzluğu hatası alırsanız, nedeni budur.

### İşlem haritası

| İşlem | Ne yapar | Sinir ağı kullanımı |
|-------|----------|---------------------|
| Toplama | Eleman bazlı birleştirme | Çıktıya sapma ekleme |
| Skaler çarpma | Her elemanı ölçekle | Öğrenme hızı * gradyanlar |
| Matris çarpımı | Vektörleri dönüştürme | Katman ileri beslemesi |
| Transpoz | Satırları ve sütunları ters çevirme | Geri yayılım |
| Determinant | Tek sayı özeti | Tersinirliği kontrol etme |
| Ters | Dönüşümü geri alma | Doğrusal sistemleri çözme |
| Birim matris | İşlem yapmayan matris | Başlatma, artık bağlantılar |

### Eleman bazlı vs matris çarpımı

```python
# Eleman bazlı çarpım (Hadamard)
A * B   # Her eleman çarpılır: (i,j) * (i,j)

# Matris çarpımı
A @ B   # Satır-sütun çarpımı: satır · sütun
```

#### Açıklama
Eleman bazlı çarpım her elemanı çarpar, matris çarpımı satır-sütun iç çarpımlarını yapar. Farklı işlemlerdir!

## Alıştırmalar

1. Python ile 2x2 matris çarpımını sıfırdan uygulayın
2. Bir 3B vektörün büyüklüğünü hesaplayın
3. iki 2x2 matrisin transpozunu hesaplayın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Matris çarpımı | "Satır-sütun çarpımı" | İki matrisi birleştiren temel işlem |
| Transpoz | "Ters çevirme" | Satırları sütun, sütunları satır yapan işlem |
| Determinant | "Tek sayı özeti" | Matrisin ölçekleme faktörünü gösteren skaler |
| Ters matris | "Geri alma" | Matris çarpımının tersini yapan matris |
| Yayma (Broadcasting) | "Otomatik genişletme" | Farklı boyutlardaki tensörleri otomatik eşitleme |
