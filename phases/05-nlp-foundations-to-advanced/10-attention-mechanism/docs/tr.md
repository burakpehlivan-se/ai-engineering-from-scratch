# Attention Mekanizması — Atılım

> Kod çözücü sıkıştırılmış bir özele bakmayı bırakır ve tüm kaynağa bakmaya başlar. Bundan sonraki her şey, artı mühendisliktir.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 09 (Diziden Diziye Modeller)
**Süre:** ~45 dakika

## Problem

Ders 09, ölçülü bir başarısızlıkla bitti. Oyuncak kopyalama görevi üzerinde eğitilmiş bir GRU kodlayıcı-kod çözücü, 5 uzunluğunda %89 doğruluktan 80 uzunluğunda tesadüfe yakın bir doğruluğa düşüyor. Neden yapısal, bir eğitim hatası değil: kodlayıcının topladığı her bilgi parçası tek sabit boyutlu gizli duruma sığmalıdır ve kod çözücü hiçbir şeyi görmez.

Bahdanau, Cho ve Bengio 2014'te üç satırlık bir düzeltme yayımladı. Kod çözücüye sadece son kodlayıcı durumunu vermek yerine, her kodlayıcı durumunu tutun. Her kod çözme adımında, "kod çözücünün o anda kodlayıcı pozisyonuna `i` ne kadar bakması gerekir?" sorusunu soran ağırlıklarla kodlayıcı durumlarının ağırlıklı ortalamasını hesaplayın. Bu ağırlıklı ortalama bağlamdır ve her kod çözücü adımında değişir.

İşte tüm fikir buydu. Transformer'lar bunu genişletti. Öz-dikkat (self-attention) bunu tek bir diziye uyguladı. Çok başlı dikkat (multi-head attention) bunu paralel olarak çalıştırdı. Ama 2014 versiyonu zaten darboğazı kırdı ve bir kez elinize geçtiğinde, transformer'lara geçiş kavramsal değil, mühendisliktir.

## Kavram

![Bahdanau attention: kod çözücü tüm kodlayıcı durumlarını sorgular](../assets/attention.svg)

Her kod çözücü adımında `t`:

1. Önceki kod çözücü gizli durumu `s_{t-1}`'i bir **sorgu (query)** olarak kullanın.
2. Her kodlayıcı gizli durumu `h_1, ..., h_T` ile puanlayın. Kodlayıcı pozisyonu başına bir skaler.
3. Skorları softmax ile attention ağırlıklarını `α_{t,1}, ..., α_{t,T}` elde edin; toplamları 1'dir.
4. Bağlam vektörü `c_t = Σ α_{t,i} * h_i`. Kodlayıcı durumlarının ağırlıklı ortalaması.
5. Kod çözücü `c_t` artı önceki çıkış token'ını alır, bir sonraki token'ı üretir.

Ağırlıklı ortalama buranın anahtarıdır. Kod çözücünün "Je" kelimesini "I" olarak çevirmesi gerektiğinde, "Je" üzerindeki kodlayıcı durumuna yüksek ağırlık verir ve diğerlerine düşük. "not" gerektiğinde "pas"'a yüksek ağırlık verir. Bağlam vektörü her adımı yeniden şekillendirir.

## Şekiller (herkesin takıldığı yer)

Bu, her attention uygulamasının ilk seferde yanlış yaptığı yerdir. Yavaş okuyun.

| Şey | Şekil | Notlar |
|-----|-------|--------|
| Kodlayıcı gizli durumları `H` | `(T_enc, d_h)` | BiLSTM ise `d_h = 2 * d_hidden` |
| Kod çözücü gizli durumu `s_{t-1}` | `(d_s,)` | Tek vektör |
| Attention skoru `e_{t,i}` | skaler | Kodlayıcı pozisyonu başına bir tane |
| Attention ağırlığı `α_{t,i}` | skaler | Tüm `i`'ler üzerinde softmax sonrası |
| Bağlam vektörü `c_t` | `(d_h,)` | Bir kodlayıcı durumuyla aynı şekil |

**Bahdanau (toplamsal / additive) skoru.** `e_{t,i} = v_α^T * tanh(W_a * s_{t-1} + U_a * h_i)`.

- `s_{t-1}` `(d_s,)` şeklindedir, `h_i` `(d_h,)` şeklindedir.
- `W_a` `(d_attn, d_s)` şeklindedir. `U_a` `(d_attn, d_h)` şeklindedir.
- tanh içindeki toplamları `(d_attn,)` şeklindedir.
- `v_α` `(d_attn,)` şeklindedir. `v_α` ile iç çarpım skalera çöker. **İşte `v_α`'nın yaptığı budur.** Büyü değildir. Bir attention-boyutlu vektörü skaler bir skora dönüştüren projeksiyondur.

**Luong (çarpımsal / multiplicative) skoru.** Üç varyant:

- `dot`: `e_{t,i} = s_t^T * h_i`. `d_s == d_h` gerektirir. Sıkı kısıtlama. Kodlayıcınız iki yönlüyse atlayın.
- `general`: `e_{t,i} = s_t^T * W * h_i` ve `W` şekli `(d_s, d_h)`. Eşit boyut kısıtlamasını kaldırır.
- `concat`: özünde Bahdanau formudur. İlk ikisi daha ucuz olduğu için nadiren kullanılır.

**Bir Bahdanau / Luong tuzağı değer.** Bahdanau `s_{t-1}`'i (mevcut kelimeyi üretmeden *önceki* kod çözücü durumu) kullanır. Luong `s_t`'yi (sonraki durum) kullanır. İkisini karıştırmak son derece zor ayıklanan ince gradyan hatalarına yol açar. Bir makale seçin ve onun kuralına sadık kalın.

## İnşa Et

### Adım 1: toplamsal (Bahdanau) attention

```python
import numpy as np


def additive_attention(decoder_state, encoder_states, W_a, U_a, v_a):
    projected_dec = W_a @ decoder_state
    projected_enc = encoder_states @ U_a.T
    combined = np.tanh(projected_enc + projected_dec)
    scores = combined @ v_a
    weights = softmax(scores)
    context = weights @ encoder_states
    return context, weights


def softmax(x):
    x = x - np.max(x)
    e = np.exp(x)
    return e / e.sum()
```

Şekillerinizi yukarıdaki tabloyla kontrol edin. `encoder_states` `(T_enc, d_h)` şeklindedir. `projected_enc` `(T_enc, d_attn)` şeklindedir. `projected_dec` `(d_attn,)` şeklindedir ve broadcast yapar. `combined` `(T_enc, d_attn)` şeklindedir. `scores` `(T_enc,)` şeklindedir. `weights` `(T_enc,)` şeklindedir. `context` `(d_h,)` şeklindedir. Hazır.

### Adım 2: Luong dot ve general

```python
def dot_attention(decoder_state, encoder_states):
    scores = encoder_states @ decoder_state
    weights = softmax(scores)
    return weights @ encoder_states, weights


def general_attention(decoder_state, encoder_states, W):
    projected = W.T @ decoder_state
    scores = encoder_states @ projected
    weights = softmax(scores)
    return weights @ encoder_states, weights
```

Her biri üç satır. İşte Luong'un makalesinin neden ses getirdiği. Çoğu görevde aynı doğruluk, çok daha az kod.

### Adım 3: işlenmiş sayısal bir örnek

Üç kodlayıcı durumu ("cat", "sat", "mat" civarı) ve ilkiyle en çok hizalanan bir kod çözücü durumu verildiğinde, attention dağılımı 0. pozisyona yoğunlaşır. Kod çözücü durumu sonuncuyla hizalanacak şekilde kayarsa, attention 2. pozisyona kayar. Bağlam vektörü takip eder.

```python
H = np.array([
    [1.0, 0.0, 0.2],
    [0.5, 0.5, 0.1],
    [0.1, 0.9, 0.3],
])

s_close_to_cat = np.array([0.9, 0.1, 0.2])
ctx, w = dot_attention(s_close_to_cat, H)
print("weights:", w.round(3))
```

```
weights: [0.464 0.305 0.231]
```

İlk satır kazanır. Sonra kod çözücü durumunu üçüncü kodlayıcı durumuna yaklaştırın ve ağırlıkların kaydığını izleyin. Hepsi bu. Attention açık hizalama (explicit alignment) demektir.

### Adım 4: neden bu transformera giden köprüdür

Yukarıdaki dili Q/K/V'ye dönüştürün:

- **Sorgu (Query)** = kod çözücü durumu `s_{t-1}`
- **Anahtar (Key)** = kodlayıcı durumları (puanladığımız şey)
- **Değer (Value)** = kodlayıcı durumları (ağırlıklandırıp topladığımız şey)

Klasik attention'da anahtarlar ve değerler aynı şeydir. Öz-dikkat (self-attention) onları ayırır: bir diziyi kendisine karşı sorgulayabilirsiniz, K ve V için farklı öğrenilmiş projeksiyonlarla. Çok başlı dikkat (multi-head attention) bunu farklı öğrenilmiş projeksiyonlarla paralel olarak çalıştırır. Transformer'lar bu sahneyi birçok kez üst üste koyar ve RNN'leri bırakır.

Matematik aynıdır. Şekiller aynıdır. Bahdanau attention'dan ölçekli iç çarpımlı attention'a (scaled dot-product attention) pedagojik sıçrama çoğunlukla gösterim (notation) farkıdır.

## Kullan

PyTorch ve TensorFlow attention'ı doğrudan sunar.

```python
import torch
import torch.nn as nn

mha = nn.MultiheadAttention(embed_dim=128, num_heads=8, batch_first=True)
query = torch.randn(2, 5, 128)
key = torch.randn(2, 10, 128)
value = torch.randn(2, 10, 128)

output, weights = mha(query, key, value)
print(output.shape, weights.shape)
```

```
torch.Size([2, 5, 128]) torch.Size([2, 5, 10])
```

İşte bu bir transformer attention katmanıdır. 5 pozisyonluk sorgu batch'i, 10 pozisyonluk anahtar/değer batch'i, herbiri 128 boyutlu, 8 baş (head). `output` bağlam zenginleştirilmiş yeni sorgulardır. `weights` görselleştirebileceğiniz 5x10 hizalama matrisidir.

### Klasik attention hâlâ neden önemli

- Pedagoji. Tek başlı, tek katmanlı, RNN tabanlı versiyon her kavramı görünür kılar.
- Transformer'ların sığmadığı cihaz üzerinde dizi görevleri.
- 2014-2017 arası herhangi bir makale. Bahdanau kuralını bilmeden yanlış okursunuz.
- Çeviri ince hizalama analizi. Ham attention ağırlıkları transformer modellerinde bile yorumlanabilirlik aracıdır ve bunları okumak ne olduklarını bilmeyi gerektirir.

### Attention ağırlığı-yorumlama tuzağı

Attention ağırlıkları yorumlanabilir görünür. Bunlar pozisyonlar boyunca toplamı bir olan ağırlıklardır; bunları çizgi grafiğine (plot) dökebilirsiniz; yüksek olması "buraya baktı" demektir. Hakemler bunları sever.

Sandıkları kadar yorumlanabilir değiller. Jain ve Wallace (2019), bazı görevlerde attention dağılımlarının tahminleri değiştirmeden rastgele alternatiflerle permüte edilebileceğini ve değiştirilebileceğini gösterdi. Attention ağırlıklarını asla bir ablasyon veya karşıt-fakt kontrolü olmadan muhakeme kanıtı olarak raporlamayın.

## Ürün Haline Getir

`outputs/prompt-attention-shapes.md` olarak kaydedin:

```markdown
---
name: attention-shapes
description: Debug shape bugs in attention implementations.
phase: 5
lesson: 10
---

Given a broken attention implementation, you identify the shape mismatch. Output:

1. Which matrix has the wrong shape. Name the tensor.
2. What its shape should be, derived from (d_s, d_h, d_attn, T_enc, T_dec, batch_size).
3. One-line fix. Transpose, reshape, or project.
4. A test to catch regressions. Typically: assert `output.shape == (batch, T_dec, d_h)` and `weights.shape == (batch, T_dec, T_enc)` and `weights.sum(dim=-1) close to 1`.

Refuse to recommend fixes that silently broadcast. Broadcast-hiding bugs surface later as silent accuracy degradation, the worst kind of attention bug.

For Bahdanau confusion, insist the decoder input is `s_{t-1}` (pre-step state). For Luong, `s_t` (post-step state). For dot-product, flag dimension mismatch between query and key as the most common first-time error.
```

## Alıştırmalar

1. **Kolay.** Kodlayıcıdaki padding token'larının attention ağırlığının sıfır olması için `softmax` maskesi uygulayın. Değişken uzunluklu dizilerle bir batch üzerinde test edin.
2. **Orta.** Luong `general` formuna çok başlı attention (multi-head attention) ekleyin. `d_h`'yi `n_heads` gruba bölün, baş başına attention çalıştırın, birleştirin. Tek baş durumunun önceki uygulamanızla eşleştiğini doğrulayın.
3. **Zor.** Ders 09'daki oyuncak kopyalama görevi üzerinde Bahdanau attention'a sahip bir GRU kodlayıcı-kod çözücü eğitin. Doğruluk vs dizi uzunluğu grafiğini çizin. Attention-sız temel çizgiyle karşılaştırın. Uzunluk arttıkça farkın açıldığını görmelisiniz, bu da darboğazın aşıldığını doğrular.

## Anahtar Terimler

| Terim | İnsanlar ne söyler | Aslında ne anlama gelir |
|-------|-------------------|------------------------|
| Attention (Dikkat) | Şeylere bakma | Bir değer (value) dizisinin, sorgu-anahtar benzerliğinden hesaplanan ağırlıklarla ağırlıklı ortalaması. |
| Sorgu, Anahtar, Değer (Query, Key, Value) | QKV | Üç projeksiyon: Q sorar, K eşleşecek şeydir, V döndürülecek şeydir. |
| Toplamsal attention (Additive attention) | Bahdanau | İleri beslemeli (feed-forward) skorlama: `v^T tanh(W q + U k)`. |
| Çarpımsal attention (Multiplicative attention) | Luong dot / general | Skor `q^T k` veya `q^T W k`'dir. Daha ucuz, çoğu görevde aynı doğruluk. |
| Hizalama matrisi (Alignment matrix) | Güzel görsel | Attention ağırlıklarının `(T_dec, T_enc)` ızgarası. Modelin neye odaklandığını görmek için okuyun. |

## İleri Okuma

- [Bahdanau, Cho, Bengio (2014). Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) — makalenin kendisi.
- [Luong, Pham, Manning (2015). Effective Approaches to Attention-based Neural Machine Translation](https://arxiv.org/abs/1508.04025) — üç skor varyantı ve karşılaştırmaları.
- [Jain ve Wallace (2019). Attention is not Explanation](https://arxiv.org/abs/1902.10186) — yorumlanabilirlik uyarısı.
- [Dive into Deep Learning — Bahdanau Attention](https://d2l.ai/chapter_attention-mechanisms-and-transformers/bahdanau-attention.html) — PyTorch ile çalıştırılabilir açıklama.
