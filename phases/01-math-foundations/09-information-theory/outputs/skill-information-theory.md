---
name: skill-information-theory
description: Bilgi teorisi kavramlarını ML kayıp fonksiyonlarına, model değerlendirmesine ve özellik seçimine uygula
version: 1.0.0
phase: 1
lesson: 9
tags: [information-theory, entropy, loss-functions]
---

# ML için Bilgi Teorisi

Makine öğrenmesi sistemlerinde entropi, çapraz entropi, KL diverjansı ve karşılıklı bilgi (mutual information) ne zaman kullanılır.

## Karar Kontrol Listesi

1. Tek bir dağılımdaki belirsizliği ölçüyor musun? **Entropi** kullan.
2. Bir modelin gerçek etiketleri ne kadar iyi yaklaştırdığını mı ölçüyorsun? **Çapraz entropi** kullan (sınıflandırma kaybın budur).
3. İki dağılım arasındaki mesafeyi mi ölçüyorsun? **KL diverjansı** kullan.
4. İki değişkenin ilişkili olup olmadığını mı kontrol ediyorsun? **Karşılıklı bilgi** (mutual information) kullan.
5. Dil modeli kalitesini mi raporluyorsun? **Perplexity** (çapraz entropinin üsteli) kullan.
6. Bir modeli diğerine mi damıtıyorsun (distillation)? Öğretmenden öğrenciye **KL diverjansı**nı en aza indir.

## Her ölçütün ne zaman kullanılacağı

| Ölçüt | Formül | Kullanım durumu | ML uygulaması |
|---|---|---|---|
| Entropi H(P) | -sum(p log p) | Bu dağılım ne kadar belirsiz? | Veri karmaşıklığı, maksimum entropi modelleri |
| Çapraz entropi H(P,Q) | -sum(p log q) | Q modeli gerçek P'yi ne kadar iyi tahmin ediyor? | Sınıflandırma kaybı, dil modeli kaybı |
| KL diverjansı D(P\|\|Q) | sum(p log(p/q)) | P ve Q ne kadar farklı? | VAE kaybı (ELBO), bilgi damıtma, RLHF |
| Karşılıklı bilgi I(X;Y) | H(X) - H(X\|Y) | Y, X hakkında ne kadar bilgi veriyor? | Özellik seçimi, temsil öğrenme |
| Perplexity | exp(H(P,Q)) veya 2^H | Model ne kadar kafası karışık? | Dil modeli değerlendirmesi |
| Koşullu entropi H(X\|Y) | -sum(p(x,y) log p(x\|y)) | Y'yi bildikten sonra X'te kalan belirsizlik | Özelliğin bilgilendiriciliği |

## Temel ilişkiler

```
Çapraz entropi  = Entropi + KL diverjansı
H(P, Q)         = H(P)   + D_KL(P || Q)

Eğitim sırasında H(P) sabit olduğundan:
  Çapraz entropiyi enküçültmek = KL diverjansını enküçültmek

Karşılıklı bilgi = Entropi - Koşullu entropi
I(X; Y) = H(X) - H(X|Y) = H(Y) - H(Y|X)

Perplexity = exp(çapraz entropi, nat cinsinden)
           = 2^(çapraz entropi, bit cinsinden)
```

## Hızlı başvuru: formüller ve birimler

| Formül | Bitler (log tabanı 2) | Natlar (log tabanı e) |
|---|---|---|
| Bilgi: -log(p) | -log2(p) | -ln(p) |
| Entropi: -sum(p log p) | bit | nat |
| 1 nat = | 1.4427 bit | 1 nat |
| PyTorch varsayılanı | -- | nat |
| Bilgi teorisi makaleleri | bit | -- |

## Değerlerin yorumlanması

| Entropi değeri | Anlamı |
|---|---|
| 0 | Deterministik. Bir sonucun olasılığı 1. |
| log(n) | Maksimum belirsizlik. n sonuç üzerinde düzgün dağılım. |
| Düşük | Dağılım sivri. Model kendinden emin. |
| Yüksek | Dağılım düz. Model belirsiz. |

| Perplexity değeri | Dil modeli kalitesi |
|---|---|
| 1 | Mükemmel tahmin (pratikte asla olmaz) |
| 10 | Ortalama olarak ~10 eşit olasılıklı token arasından seçim |
| 50 | Standart kıyaslama (benchmark) üzerinde GPT-2 seviyesi |
| < 10 | İyi temsil edilen alanlar için son teknoloji |

## Yaygın hatalar

- KL diverjansını simetrik gibi ele almak. D_KL(P||Q) != D_KL(Q||P). Simetrik bir ölçüt için Jensen-Shannon diverjansını kullan: JS = 0.5 * KL(P||M) + 0.5 * KL(Q||M), burada M = 0.5*(P+Q).
- Bir-etiketli (one-hot) etiketlerle çapraz entropinin -log(p_true_class) olarak sadeleştiğini unutmak. Gerçek dağılım bir-etiketli olduğunda tüm sınıflar üzerinde toplam alman gerekmez.
- Kodda log tabanı 2 kullanıp nat cinsinden raporlamak (ya da tam tersi). PyTorch varsayılan olarak doğal log kullanır. Natları bitlere çevirmek için log2(e) = 1.4427 ile çarp.
- Boş veya sıfır olasılıklı bir olayın entropisini hesaplamak. Kural: 0 * log(0) = 0, çünkü lim(p->0) p*log(p) = 0.
- Perplexity'yi farklı sözlük boyutları arasında karşılaştırmak. Sözlük boyutu 50k ve perplexity 30 olan bir model, sözlük boyutu 10k ve perplexity 30 olan bir modelle doğrudan karşılaştırılamaz.

## Her kavramın üretim ML'sinde nerede göründüğü

| Kavram | Nerede karşına çıkar |
|---|---|
| Çapraz entropi kaybı | Her sınıflandırma modeli (nn.CrossEntropyLoss) |
| KL diverjansı | VAE ELBO, PPO kırpma, bilgi damıtma |
| Entropi düzenlileştirmesi | RL'de keşif bonusu (daha yüksek entropi = daha fazla keşif) |
| Karşılıklı bilgi | Özellik seçimi, InfoNCE kaybı (karşılaştırmalı öğrenme) |
| Perplexity | Dil modeli kıyaslamaları (düşük = daha iyi) |
| Etiket yumuşatma (label smoothing) | Bir-etiketli (one-hot) etiketi yumuşak hedeflerle değiştirir, çapraz entropinin aşırı güvenini azaltır |
| Sıcaklık ölçekleme | Softmax'tan önce logits'leri T'ye böler, çıktı entropisini kontrol eder |
