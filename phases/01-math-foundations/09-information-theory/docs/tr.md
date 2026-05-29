> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/09-information-theory/docs/en.md)

# Bilgi Teorisi

> Bilgi teorisi şaşkınlığı ölçer. Kayıp fonksiyonları bunun üzerine kuruludur.

**Tür:** Öğrenme
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 06 (Olasılık)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Entropi, çapraz entropi ve KL diverjansını sıfırdan hesaplayın ve aralarındaki ilişkiyi açıklayın
- Çapraz entropi kaybını asgari yapmanın log-olabilirliği maksimum yapmaya eşdeğer olduğunu türetin
- Özellikler ile hedef arasındaki karşılıklı bilgiyi hesaplayarak özellik önemini sıralayın
- Perplexity'yi bir dil modelinin seçtiği etkili sözlük boyutu olarak açıklayın

## Sorun

Her sınıflandırma modelinde `CrossEntropyLoss()` çağırıyorsunuz. Her dil modeli makalesinde "perplexity" görüyorsunuz. VAE'lerde, damıtma ve RLHF'de KL diverjansı hakkında okuyorsunuz. Bunlar bağlantısız kavramlar değildir. Hepsi farklı şapkalar takmış aynı fikirdir.

Bilgi teorisi, belirsizlik, sıkıştırma ve tahmin hakkında akıl yürütmeniz için dili verir. Claude Shannon, 1948'de iletişim sorunlarını çözmek için bunu icat etti. Meğersin, bir sinir ağı eğitmek bir iletişim sorunuymuş: model, öğrenilmiş ağırlıkların gürültülü kanalı aracılığıyla doğru etiketi iletmeye çalışıyor.

Bu ders her formülü sıfırdan oluşturur, böylece nereden geldiklerini ve neden çalıştıklarını görürsünüz.

## Kavram

### Bilgi İçeriği (Şaşkınlık)

Olası olmayan bir şey olduğunda, daha fazla bilgi taşır. Yazi gelen bir para? Şaşırtıcı değil. Piyango kazanmak? Çok şaşırtıcı.

Olasılığı p olan bir olayın bilgi içeriği:

```
I(x) = -log(p(x))
```

Log tabanı 2 kullanırsanız bit, doğal log kullanırsanız nat alırsınız.

```
Olay                Olasılık      Şaşkınlık (bit)
Adaş para            0.5            1.0
6 gelmesi            0.167          2.58
1000'de 1 olay       0.001          9.97
Kesin olay           1.0            0.0
```

Kesin olaylar sıfıraf bilgi taşır. Zaten olacaklarını biliyordunuz.

### Entropi (Ortalama Şaşkınlık)

Bir dağılımın ortalama şaşkınlığıdır. Ne kadar belirsiz olduğunu ölçer.

```
H(X) = -Σ p(x_i) × log(p(x_i))
```

Düşük entropi = belirsizlik az, yüksek entropi = belirsizlik çok.

```
Adil para: H = -0.5×log(0.5) - 0.5×log(0.5) = 1 bit
Sahte para (hepsi tura): H = -1×log(1) = 0 bit
```

### Çapraz Entropi

İki dağılım arasındaki farkın ölçüsüdür. Bir dağılımın diğerini ne kadar iyi modellediğini söyler.

```
H(p, q) = -Σ p(x_i) × log(q(x_i))
```

Yapay zekada:
- p = gerçek dağılım (etiketler)
- q = modelin tahmin ettiği dağılım
- Çapraz entropi ne kadar düşükse, model o kadar iyi

### KL Diverjansı (Kullback-Leibler)

Bir dağılımın diğerinden ne kadar farklı olduğunu ölçer. Asimetriktir.

```
KL(p || q) = Σ p(x_i) × log(p(x_i) / q(x_i))
```

#### Açıklama
KL = 0 ise dağılımlar aynıdır. KL > 0 ise q, p'den farklıdır. VAE'lerde ve damıtmada kullanılır.

### Perplexity

Dil modellerinde kullanılır. Modelin her adımda kaç seçeneği ciddiye aldığını söyler.

```
Perplexity = exp(çapraz entropi)
```

Düşük perplexity = model daha kararlı, yüksek perplexity = model daha belirsiz.

### Karşılıklı Bilgi

İki değişken arasındaki bağımlılığın ölçüsüdür. Özellik seçimi için kullanılır.

```
I(X; Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)
```

## Alıştırmalar

1. Bir zar için entropiyi sıfırdan hesaplayın
2. Farklı tahminler için çapraz entropiyi hesaplayın
3. Bir metin dosyasının entropisini hesaplayarak ne kadar "tahmin edilemez" olduğunu ölçün

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Entropi | "Belirsizlik ölçüsü" | Bir dağılımın ortalama şaşkınlığı |
| Çapraz entropi | "Tahmin hatası" | İki dağılım arasındaki farkın ölçüsü |
| KL diverjansı | "Dağılım farkı" | Bir dağılımın diğerinden ne kadar farklı olduğunu ölçen asimetrik metrik |
| Perplexity | "Karışıklık" | Dil modelinin her adımda seçtiği ortalama seçenek sayısı |
| Karşılıklı bilgi | "Bağımlılık ölçüsü" | İki değişken arasındaki bilgi paylaşımı |
| Bit | "Bilgi birimi" | İkili seçimdeki şaşkınlık miktarı |
