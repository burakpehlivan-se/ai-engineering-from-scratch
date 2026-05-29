> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/13-numerical-stability/docs/en.md)

# Sayısal Kararlılık

> Kayan nokta sızdıran bir soyutlama boyutudur. Eğitim sırasında sizi ısırır ve gelmediğini görmezsiniz.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 01-04
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Maksimum çıkarma hilesiyle sayısal kararlı softmax ve log-sum-exp uygulayın
- Kayan nokta hesaplamalarında taşma, taşma altı ve felaket iptalini tanıyın
- Merkezli sonlu farklarla analitik gradyanları sayısal gradyanlara karşı doğrulayın
- Eğitimde neden bfloat16'nın float16'dan tercih edildiğini ve kayıp ölçeklemenin gradyan taşmasını nasıl önlediğini açıklayın

## Sorun

Modeliniz üç saat çalışıyor, sonra kayıp NaN oluyor. Bir yazdırma ifadesi ekliyorsunuz. 9.000. adımda logit'ler iyi. 9.001. adımda `inf` oluyorlar. 9.002. adımda tüm gradyanlar `nan' oluyor ve eğitim ölüyor.

Ya da: Modeliniz eğitimi tamamlıyor ama doğruluk, makalenin iddia ettiğinden %2 daha düşük. Her şeyi kontrol ediyorsunuz. Mimari eşleşiyor. Hiperparametreler eşleşiyor. Veri eşleşiyor. Sorun, makalenin float32 kullandığı sizin ise float16'ı doğru ölçekleme olmadan kullandığınız. Otuz iki bit birikmiş yuvarlama hatası sessizce doğruluğunuzu yedi.

Ya da: Çapraz entropi kaybını sıfırdan uyguluyorsunuz. Küçük logit'lerde çalışıyor. Logit'ler 100'ü aştığında `inf` döndürüyor. Softmax taştı çünkü `exp(100)` float32'nin temsil edebileceğinden büyük. Her ML çerçevesi bunu iki satırlık bir hileyle ele alır. Hilenin varlığından haberiniz yoktu.

Sayısal kararlılık teorik bir endişe değildir. Başarılı bir eğitim çalıştırması ile sessizce başarısız olan arasındaki farktır. Hata ayıklayacağınız her ciddi ML hatası sonunda kayan noktaya gelir.

## Kavram

### IEEE 754: Bilgisayarlar Gerçek Sayıları Nasıl Saklar

Bilgisayarlar gerçek sayıları IEEE 754 standardını izleyerek kayan nokta değerleri olarak saklar. Float üç bölümden oluşur: işaret biti, üs ve anlamlı (mantissa).

```
Float32 düzeni (toplam 32 bit):
[1 işaret] [8 üs] [23 anlamlı]

Değer = (-1)^işaret * 2^(üs - 127) * 1.anlamlı
```

Anlamlı, hassasiyeti belirler (kaç anlamlı basamak). Üs, aralığı belirler (bir sayı ne kadar büyük veya küçük olabilir).

### Yaygın Kararsızlık Kaynakları

**1. Taşma (Overflow):** Sayı aralık dışına çıkar
```python
import numpy as np
x = np.float32(1e38) * 2  # inf olur
```

**2. Taşma Altı (Underflow):** Sayı çok küçük olur ve sıfır olur
```python
x = np.float32(1e-45) / 2  # 0 olur
```

**3. Felaket İptali:** Büyük sayılar arasındaki küçük farkları kaybetme
```python
a = np.float32(1.0000001)
b = np.float32(1.0000000)
print(a - b)  # 0 olabilir
```

### Sayısal Kararlı Softmax

Softmax, `exp()` kullanır. Büyük değerler taşar. Çözüm: maksimumu çıkarın.

```python
def kararli_softmax(z):
    z = z - np.max(z)  # Maksimumu çıkar
    exp_z = np.exp(z)
    return exp_z / exp_z.sum()
```

#### Açıklama
Maksimumu çıkarmak, değerleri negatif yaparak taşmayı önler. Sonuç aynıdır, sayısal olarak kararlıdır.

### Sayısal Kararlı Çapraz Entropi

```python
def kararli_ce(tahmin, hedef):
    tahmin = tahmin - np.max(tahmin)  # Kararlı softmax
    log_tahmin = np.log(tahmin + 1e-12)  # Log(0) önlemek için küçük epsilon
    return -np.sum(hedef * log_tahmin)
```

### bfloat16 vs float16

- **float16:** Daha küçük üs aralığı (±65504), daha fazla hassasiyet
- **bfloat16:** float32 ile aynı üs aralığı, daha az hassasiyet

Eğitimde bfloat16 tercih edilir çünkü gradyanların taşması daha az olur.

## Alıştırmalar

1. Standart softmax'u ve sayısal kararlı softmax'u karşılaştırın (büyük logit'lerle test edin)
2. Bir gradyanın NaN olmasına neden olan bir durum yaratın ve düzeltin
3. float16 ve bfloat16 ile aynı işlemi çalıştırın ve farkları gözlemleyin

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Sayısal kararlılık | "Hata önleme" | Kayan nokta işlemlerinde hataları önleme |
| Taşma | "Sayı çok büyük" | Sayının temsil aralığını aşması |
| Taşma altı | "Sayı çok küçük" | Sayının en küçük pozitif değerin altına düşmesi |
| Felaket iptal | "Bilgi kaybı" | Büyük sayılar arasındaki küçük farkların kaybolması |
| bfloat16 | "Eğitim formatı" | GPU eğitiminde tercih edilen 16 bit kayan nokta formatı |
| Epsilon | "Güvenlik marjı" | Sıfıra bölmeyi ve log(0)'ı önlemek için eklenen çok küçük sayı |
