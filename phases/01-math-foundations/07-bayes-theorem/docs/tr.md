> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/07-bayes-theorem/docs/en.md)

# Bayes Teoremi

> Olasılık ne beklediğinizle ilgilidir. Bayes teoremi ne öğrendiğinizle ilgilidir.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 06 (Olasılık Temelleri)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Öncüller, olabilirlikler ve kanıtlarla sonraki olasılıkları hesaplamak için Bayes teoremini uygulayın
- Laplace düzeltmesi ve log uzayı hesaplamasıyla sıfırdan bir Saf Bayes metin sınıflandırıcısı oluşturun
- MLE ve MAP tahminlerini karşılaştırın ve MAP'ın L2 düzenlemesiyle nasıl eşleştiğini açıklayın
- A/B testi için Beta-Binomyal eşlenik öncülleri kullanarak sıralı Bayes güncellemesi uygulayın

## Sorun

Tıbbi bir testin doğruluk oranı %99. Pozitif çıkıyorsunuz. Gerçekten hasta olma olasılığınız nedir?

Çoğu insan %99 der. Gerçek cevap hastalığın ne kadar nadir olduğuna bağlıdır. 10.000 kişide birinde varsa, pozitif sonuç size sadece yaklaşık %1 olasılık verir. Diğer %99 pozitif sonuç, sağlıklı insanlardan gelen yanlış alarmdır.

Bu bir tuzak soru değil. Bu Bayes teoremidir. Her spam filtresi, her tıbbi teşhis, belirsizliği nicelleştiren her makine öğrenmesi modeli bu tam mantığı kullanır. Bir inançla başlarsınız. Kanıt görürsünüz. Güncellersiniz.

Bunu anlamadan ML sistemleri oluşturursanız, model çıktılarını yanlış yorumlarsınız, kötü eşikler belirlersiniz ve aşırı kendine güvenen tahminler sunarsınız.

## Kavram

### Ortak olasılıktan Bayes'e

Ders 06'dan biliyorsunuz, koşullu olasılık:

```
P(A|B) = P(A ve B) / P(B)
```

Ve simetrik olarak:

```
P(B|A) = P(A ve B) / P(A)
```

Her iki ifade de aynı payı paylaşır: P(A ve B). Bunları eşitleyin ve yeniden düzenleyin:

```
P(A ve B) = P(A|B) * P(B) = P(B|A) * P(A)

Bu nedenle:

P(A|B) = P(B|A) * P(A) / P(B)
```

Bu Bayes teoremidir. Tüm olasılık hesaplamalarının temelidir.

### Terminoloji

```
P(durum|kanıt) = P(kanıt|durum) × P(durum) / P(kanıt)
  sonraki       olabilirlik     öncül       kanıt
```

- **Öncül (P(durum))**: Kanıttan ÖNCE duruma inanma dereceniz
- **Olasilik (P(kanıt|durum))**: Durum doğruysa kanıtı görme olasılığı
- **Sonraki (P(durum|kanıt))**: Kanıttan SONRA duruma inanma dereceniz

### Örnek: Tıbbi Test

```
Hastalık oranı: 1/1000 = 0.001 (öncül)
Testin doğru pozitif oranı: %99 = 0.99 (olasılık)
Testin yanlış pozitif oranı: %1 = 0.01

P(hasta|pozitif) = 0.99 × 0.001 / (0.99 × 0.001 + 0.01 × 0.999)
                 = 0.00099 / (0.00099 + 0.00999)
                 = 0.09 = %9
```

#### Açıklama
Hastalık çok nadir olduğu için (1/1000), pozitif test sonucu bile sadece %9 olasılık verir. Bu, Bayes teoreminin gücünü gösterir.

### Saf Bayes Sınıflandırıcısı

Metin sınıflandırmada kelime olasılıklarını çarparak sınıflandırma yapar:

```
P(sınıf|kelimeler) ∝ P(kelimeler|sınıf) × P(sınıf)
```

Laplace düzeltmesi: Hiç görülmemiş kelimeler için olasılığı sıfır yapmak yerine küçük bir değer ekler.

### MLE vs MAP

- **MLE (Maksimum Olabilirlik Tahmini)**: Veride en iyi uyan parametreleri bulur
- **MAP (Maksimum Sonraki Tahmini)**: Öncül bilgiyi de hesaba katar

MAP, L2 düzenlemesiyle eşdeğerdir: Büyük ağırlıklara ceza vererek basit modelleri tercih eder.

## Alıştırmalar

1. Bayes teoremini kullanarak, verilen bir test sonucunda hastalık olasılığını hesaplayın
2. Sıfırdan bir Saf Bayes sınıflandırıcısı kodlayın
3. Farklı öncül değerleriyle sonraki olasılıkların nasıl değiştiğini grafikle gösterin

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Bayes teoremi | "Olasiği güncelleme" | Kanıt geldikçe inancı güncelleme formülü |
| Öncül | "Başlangıç inancı" | Kanıttan önceki inanç derecesi |
| Sonraki | "Güncellenmiş inanç" | Kanıttan sonraki inanç derecesi |
| Olasılık | "Şans" | Bir durumun gözlemlenme olasılığı |
| MLE | "En iyi uyan" | Veride en yüksek olasılığı veren parametreler |
| MAP | "Öncüllü en iyi uyan" | Öncül bilgiyle birlikte en iyi parametreler |
