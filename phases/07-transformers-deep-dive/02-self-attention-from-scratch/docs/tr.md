# Self-Attention'dan Sıfıra

> Dikkat, her kelimenin "benim için kim önemli?" diye sorduğu ve cevabı öğrendiği bir lookup tablosudur.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 3 (Derin Öğrenme Çekirdeği), Faz 5 Ders 10 (Diziden Diziye)
**Süre:** ~90 dakika

## Öğrenme Amaçları

- Sadece NumPy kullanarak, sorgu/anahtar/değer (query/key/value) projeksiyonlarını ve softmax ağırlıklı toplamı içeren ölçekli nokta çarpımı self-attention'ı sıfırdan uygulayın
- Başları bölen, paralel dikkat hesaplayan ve sonuçları birleştiren çoklu dikkat (multi-head attention) katmanı oluşturun
- Dikkat matrisinin token ilişkilerini nasıl yakaladığını izleyin ve `sqrt(d_k)` ile ölçeklemenin softmax doygunluğunu neden önlediğini açıklayın
- Çift yönlü dikkati otoregresif (çözücü tarzı) dikkate dönüştürmek için nedensel maske (causal masking) uygulayın

## Sorun

RNN'ler dizileri tek token işler. 50. token'a ulaştığınızda, 1. token'dan bilgi 50 sıkıştırma adımından geçirilmişti. Uzun menzilli bağımlılıklar sabit boyutlu bir gizli duruma sıkıştırılıyor — LSTM kapısı hiçbir zaman tam olarak çözemeyen bir darboğaz.

2014 Bahdanau dikkat makalesi düzeltmeyi gösterdi: çözücünün her kodlayıcı konumuna geri bakmasına ve hangilerinin mevcut adım için önemli olduğuna karar vermesine izin verin. Ama hala bir RNN'e eklenmişti. 2017 "Attention Is All You Need" makalesi daha keskin bir sordu: ya dikkat *tek* mekanizma olursa? Yineleme yok. Evrişim yok. Sadece dikkat.

Self-attention, bir dizideki her konumun diğer her konuya tek bir paralel adımda dikkat etmesine izin verir. Bu, transformer'ları hızlı, ölçeklenebilir ve baskın kılan şeydir.

## Kavram

### Veritabanı Sorgulama Benzetmesi

Dikkati yumuşak bir veritabanı sorgulaması olarak düşünün:

```
Geleneksel veritabanı:
  Sorgu: "Fransa'nın başkenti"  -->  tam eşleşme  -->  "Paris"

Dikkat:
  Sorgu: "Fransa'nın başkenti"  -->  TÜM anahtarlara benzerlik  -->  TÜM değerlerin ağırlıklı karışımı
```

#### Açıklama
Bu karşılaştırma, geleneksel veritabanlarının tam eşleşme (lookup) yaparken, dikkat mekanizmasının tüm anahtarlarla benzerlik hesaplayarak yumuşak (soft) bir eşleşme yaptığını gösterir.

Her token üç vektör üretir:
- **Sorgu (Query):** "Ne arıyorum?"
- **Anahtar (Key):** "Ne içeriyorum?"
- **Değer (Value):** "Seçilirsem hangi bilgiyi sağlarım?"

Bir sorgu ile tüm anahtarların nokta çarpımı dikkat puanlarını üretir. Yüksek puan "bu anahtar sorgumla eşleşiyor" demektir. Bu puanlar değerleri ağırlıklandırır. Çıktı, değerlerin ağırlıklı toplamıdır.

### Q, K, Hesaplaması

Her token gömüsü (embedding), öğrenilen üç ağırlık matrisi boyunca projekte edilir:

```
Girdi gömüler dizisi (n token, her biri d-boyutlu):

  X = [x1, x2, x3, ..., xn]       şekil: (n, d)

Üç ağırlık matrisi:

  Wq  şekil: (d, dk)
  Wk  şekil: (d, dk)
  Wv  şekil: (d, dv)

Projeksiyonlar:

  Q = X @ Wq    şekil: (n, dk)      her token'ın sorgusu
  K = X @ Wk    şekil: (n, dk)      her token'ın anahtarı
   V = X @ Wv    şekil: (n, dv)      her token'ın değeri
```

#### Açıklama
Her token gömüsü, öğrenilen üç farklı ağırlık matrisi ile çarpılarak Sorgu (Q), Anahtar (K) ve Değer (V) matrislerine dönüştürülür. Bu projeksiyonlar eğitilir.

Görsel olarak, bir token için:

```
             Wq
  x_i ------[*]------> q_i    "Ne arıyorum?"
       |
       |     Wk
       +----[*]------> k_i    "Ne içeriyorum?"
       |
       |     Wv
       +----[*]------> v_i    "Ne sunuyorum?"
```

### Dikkat Matrisi

Tüm token'lar için Q, K, V'yi aldığınızda, dikkat puanları bir matris oluşturur:

```
Puanlar = Q @ K^T    şekil: (n, n)

              k1    k2    k3    k4    k5
        +-----+-----+-----+-----+-----+
   q1   | 2.1 | 0.3 | 0.1 | 0.8 | 0.2 |   <- q1 her anahtara ne kadar dikkat ediyor
        +-----+-----+-----+-----+-----+
   q2   | 0.4 | 1.9 | 0.7 | 0.1 | 0.3 |
        +-----+-----+-----+-----+-----+
   q3   | 0.2 | 0.6 | 2.3 | 0.5 | 0.1 |
        +-----+-----+-----+-----+-----+
   q4   | 0.9 | 0.1 | 0.4 | 1.7 | 0.6 |
        +-----+-----+-----+-----+-----+
   q5   | 0.1 | 0.3 | 0.2 | 0.5 | 2.0 |
        +-----+-----+-----+-----+-----+

Her satır: bir token'ın tüm dizi boyunca dikkati
```

#### Açıklama
Dikkat matrisinin her satırı, bir token'ın dizideki diğer tüm token'lara olan dikkat ağırlıklarını gösterir.

### Neden Ölçekliyoruz?

Nokta çarpımları dk boyutuyla büyür. Eğer dk = 64 ise, nokta çarpımları onlar aralığında olabilir, softmaksı gradyanların kaybolduğu bölgelere itebilir. Düzeltme: sqrt(dk)'ya bölün.

```
Ölçekli puanlar = (Q @ K^T) / sqrt(dk)
```

Bu, değerleri softmaksın faydalı gradyanlar ürettiği aralıkta tutar.

#### Açıklama
Nokta çarpımlarının boyutla birlikte büyümesi, softmaks fonksiyonunun doymasına (saturation) neden olur. Ölçekleme, gradyanların kaybolmasını önler.

### Softmax Puanları Ağırlıklara Dönüştürür

Softmax ham puanları her satır üzerinde bir olasılık dağılımına dönüştürür:

```
q1 için ham puanlar:   [2.1, 0.3, 0.1, 0.8, 0.2]
                            |
                         softmax
                            |
Dikkat ağırlıkları:   [0.52, 0.09, 0.07, 0.14, 0.08]   (~1.0 toplar)
```

#### Açıklama
Softmax, ham puanları toplamı 1 olan bir olasılık dağılımına dönüştürür. Böylece her token diğer token'lara ne kadar dikkat edeceği konusunda bir ağırlık setine sahip olur.

Şimdi her token, diğer her token'a ne kadar dikkat edeceğini söyleyen bir dizi ağırlığa sahiptir.

### Değerlerin Ağırlıklı Toplamı

Her token için nihai çıktı, tüm değer vektörlerinin ağırlıklı toplamıdır:

```
output_i = sum( dikkat_agirlik[i][j] * v_j  için tüm j )

Token 1 için:
  output_1 = 0.52 * v1 + 0.09 * v2 + 0.07 * v3 + 0.14 * v4 + 0.08 * v5
```

### Tam Hat

```
                    +-------+
  X (girdi)  ----->|  @ Wq  |-----> Q
                    +-------+
                    +-------+
  X (girdi)  ----->|  @ Wk  |-----> K
                    +-------+                     +----------+
                    +-------+                     |          |
  X (girdi)  ----->|  @ Wv  |-----> V ---------->| ağırlıklı|----> çıktı
                    +-------+          ^          |  toplam   |
                                       |          +----------+
                              +--------+--------+
                              |    softmax      |
                              +---------+-------+
                                        ^
                              +---------+-------+
                              | Q @ K^T / sqrt  |
                              +-----------------+
```

Tek satır formül:

```
Attention(Q, K, V) = softmax( Q @ K^T / sqrt(dk) ) @ V
```

## İnşa Et

### Adım 1: Softmax sıfırdan

Softmax ham logitleri olasılıklara dönüştürür. Sayısal kararlılık için maksimumu çıkarın.

```python
import numpy as np

def softmax(x):
    shifted = x - np.max(x, axis=-1, keepdims=True)
    exp_x = np.exp(shifted)
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

logits = np.array([2.0, 1.0, 0.1])
print(f"logits:  {logits}")
print(f"softmax: {softmax(logits)}")
print(f"sum:     {softmax(logits).sum():.4f}")
```

#### Açıklama
Bu kod, logitleri olasılıklara dönüştüren softmax fonksiyonunu sıfırdan uygular. Sayısal kararlılık için, hesaplamadan önce her ögeden maksimum değer çıkarılır.

### Adım 2: Ölçekli nokta çarpımı dikkatı

Temel işlev. Q, K, V matrislerini alır ve dikkat çıktısı ile ağırlık matrisini döndürür.

```python
def scaled_dot_product_attention(Q, K, V):
    dk = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(dk)
    weights = softmax(scores)
    output = weights @ V
    return output, weights
```

#### Açıklama
Bu işlev, ölçekli nokta çarpımı dikkat formülünü uygular: softmax(Q @ K^T / sqrt(dk)) @ V.

### Adım 3: Öğrenilen projeksiyonlu self-attention sınıfı

Wq, Wk, Wv ağırlık matrisleri Xavier benzeri ölçekleme ile başlatılmış tam bir self-attention modülü.

```python
class SelfAttention:
    def __init__(self, d_model, dk, dv, seed=42):
        rng = np.random.default_rng(seed)
        scale = np.sqrt(2.0 / (d_model + dk))
        self.Wq = rng.normal(0, scale, (d_model, dk))
        self.Wk = rng.normal(0, scale, (d_model, dk))
        scale_v = np.sqrt(2.0 / (d_model + dv))
        self.Wv = rng.normal(0, scale_v, (d_model, dv))
        self.dk = dk

    def forward(self, X):
        Q = X @ self.Wq
        K = X @ self.Wk
        V = X @ self.Wv
        output, weights = scaled_dot_product_attention(Q, K, V)
        return output, weights
```

#### Açıklama
Bu sınıf, öğrenilen projeksiyon ağırlıklarıyla tam bir self-attention modülü tanımlar. Xavier başlangıcı, ağırlıkların uygun aralıkta başlamasını sağlar.

### Adım 4: Bir cümle üzerinde çalıştır

Bir cümle için sahte gömüler oluşturun ve dikkat ağırlıklarını izleyin.

```python
sentence = ["The", "cat", "sat", "on", "the", "mat"]
n_tokens = len(sentence)
d_model = 8
dk = 4
dv = 4

rng = np.random.default_rng(42)
X = rng.normal(0, 1, (n_tokens, d_model))

attn = SelfAttention(d_model, dk, dv, seed=42)
output, weights = attn.forward(X)

print("Dikkat ağırlıkları (her satır: o token'ın nereye baktığı):\n")
print(f"{'':>6}", end="")
for token in sentence:
    print(f"{token:>6}", end="")
print()

for i, token in enumerate(sentence):
    print(f"{token:>6}", end="")
    for j in range(n_tokens):
        w = weights[i][j]
        print(f"{w:6.3f}", end="")
    print()
```

### Adım 5: Dikkati ASCII ısı haritasıyla görselleştirin

Dikkat ağırlıklarını hızlı bir görsel için karakterlere eşleyin.

```python
def ascii_heatmap(weights, tokens, chars=" ░▒▓█"):
    n = len(tokens)
    print(f"\n{'':>6}", end="")
    for t in tokens:
        print(f"{t:>6}", end="")
    print()

    for i in range(n):
        print(f"{tokens[i]:>6}", end="")
        for j in range(n):
            level = int(weights[i][j] * (len(chars) - 1) / weights.max())
            level = min(level, len(chars) - 1)
            print(f"{'  ' + chars[level] + '   '}", end="")
        print()

ascii_heatmap(weights, sentence)
```

## Kullan

PyTorch'un `nn.MultiheadAttention`'ı tam olarak inşa ettiğimiz şeyi yapar, artı çoklu-baş bölme ve çıktı projeksiyonu:

```python
import torch
import torch.nn as nn

d_model = 8
n_heads = 2
seq_len = 6

mha = nn.MultiheadAttention(embed_dim=d_model, num_heads=n_heads, batch_first=True)

X_torch = torch.randn(1, seq_len, d_model)

output, attn_weights = mha(X_torch, X_torch, X_torch)

print(f"Girdi şekli:            {X_torch.shape}")
print(f"Çıktı şekli:           {output.shape}")
print(f"Dikkat ağırlık şekli: {attn_weights.shape}")
print(f"\nDikkat ağırlıkları (başlar ortalaması):")
print(attn_weights[0].detach().numpy().round(3))
```

Temel fark: çoklu dikkat (multi-head attention), birden fazla dikkat işlevini paralel olarak çalıştırır, her biri dk = d_model / n_heads boyutunda kendi Q, K, V projeksiyonuna sahiptir, ardından sonuçları birleştirir. Bu, modelin farklı ilişki türlerine aynı anda dikkat etmesini sağlar.

## Teslim Et

Bu ders şunları üretir:
- `outputs/prompt-attention-explainer.md` - dikkati veritabanı sorgulama benzetmesiyle açıklayan bir prompt

## Alıştırmalar

1. Softmax'tan önce belirli konumları negatif sonsuzluğa ayayan isteğe bağlı bir maske matrisi kabul edecek şekilde `scaled_dot_product_attention`'ı değiştirin (böylece nedensel/çözücü maskesi çalışır)
2. Sıfırdan çoklu dikkat uygulayın: Q, K, V'yi `n_heads` parçalara bölün, her biri üzerinde dikkat çalıştırın, birleştirin ve son ağırlık matrisi Wo ile projekte edin
3. Aynı uzunlukta iki farklı cümle alın, aynı SelfAttention örneği üzerinden besleyin ve dikkat kalıplarını karşılaştırın. Ne değişir? Ne aynı kalır?

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|----------------------|
| Sorgu (Query) | "Soru vektörü" | Bu token'ın ne tür bilgi aradığını temsil eden öğrenilmiş bir girdi projeksiyonu |
| Anahtar (Key) | "Etiket vektörü" | Bu token'ın ne tür bilgi içerdiğini temsil eden, sorgularla eşleştirilen öğrenilmiş bir projeksiyon |
| Değer (Value) | "İçerik vektörü" | Dikkat puanlarına göre toplanan gerçek bilgiyi taşıyan öğrenilmiş bir projeksiyon |
| Ölçekli nokta çarpımı dikkatı | "Dikkat formülü" | softmax(QK^T / sqrt(dk)) @ V - ölçekleme yüksek boyutlarda softmaks doygunluğunu önler |
| Self-attention | "Token kendine ve diğerlerine bakar" | Q, K, V'nin hepsinin aynı diziden geldiği, her konumun diğer her konuya dikkat etmesini sağlayan dikkat türü |
| Dikkat ağırlıkları | "Ne kadar odaklanma" | Ölçekli nokta çarpımları üzerine softmax tarafından üretilen konumlar üzerinde bir olasılık dağılımı |
| Çoklu dikkat (Multi-head attention) | "Paralel dikkat" | Farklı projeksiyonlarla birden fazla dikkat işlevi çalıştırma, zengin temsiller için sonuçları birleştirme |

## İleri Okuma

- [Attention Is All You Need (Vaswani ve diğerleri, 2017)](https://arxiv.org/abs/1706.03762) - orijinal transformer makalesi
- [The Illustrated Transformer (Jay Alammar)](https://jalammar.github.io/illustrated-transformer/) - tam mimarinin en iyi görsel anlatımı
- [The Annotated Transformer (Harvard NLP)](https://nlp.seas.harvard.edu/annotated-transformer/) - açıklamalı satır satır PyTorch uygulaması
