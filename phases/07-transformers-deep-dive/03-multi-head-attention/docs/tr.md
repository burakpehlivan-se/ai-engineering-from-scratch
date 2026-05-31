# Çoklu Dikkat (Multi-Head Attention)

> Tek bir dikkat başı (head) bir seferde bir ilişki öğrenir. Sekiz baş sekiz ilişki öğrenir. Başlar ücretsizdir. Daha fazla alın.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 02 (Self-Attention'dan Sıfıra)
**Süre:** ~75 dakika

## Sorun

Tek bir self-attention başı tek bir dikkat matrisi hesaplar. Bu matris bir tür ilişkiyi yakalar — genellikle eğitim sinyalinin ne olduğuna bağlı olarak kaybı en aza indireni. Verilerinizde özne-fiil uyumu, eş-anlam referansı (co-reference), uzun menzilli söylem ve sözdizimsel bloklar (syntactic chunking) birbirine karışmışsa, tek bir baş bunları tek bir softmax dağılımı olarak bulandırır ve sinyalin yarısını kaybeder.

2017 Vaswani makalesinden düzeltme: her biri kendi Q, K, V projeksiyonlarına sahip birden fazla dikkat işlevini paralel çalıştırın ve çıktıları birleştirin. Her baş, `d_model / n_heads` boyutunda daha küçük bir alt uzayda çalışır. Toplam parametre sayısı aynı kalır. İfade gücü (expressive power) artar.

Çoklu dikkat, 2026'daki her transformer'ın varsayılan donanımıdır. Tek tartışma *kaç* baş olduğu ve anahtarların ile değerlerin projeksiyonları paylaşıp paylaşmadığıdır (Gruplanmış-Sorgu Dikkati / Grouped-Query Attention, Çoklu-Sorgu Dikkati / Multi-Query Attention, Çoklu-Baş Gizli Dikkati / Multi-head Latent Attention).

## Kavram

![Çoklu dikkat böler, dikkat eder, birleştirir](../assets/multi-head-attention.svg)

**Böl.** `(N, d_model)` şeklindeki `X`'i alın. Her biri `(N, d_model)` şeklindeki Q, K, V'ye projekte edin. `(N, n_heads, d_head)` şeklinde yeniden şekillendirin, burada `d_head = d_model / n_heads`. `(n_heads, N, d_head)` olarak转置 edin.

#### Açıklama
Girdi matrisi, birden fazla dikkat başı tarafından işlenebilecek şekilde bölünür. Her baş kendi alt uzayında çalışır.

**Paralel olarak dikkat et.** Her başın içinde ölçekli nokta çarpımı dikkatı çalıştırın. Her baş `(N, d_head)` üretir. Başlar gömülmenin farklı alt uzaylarında çalışır ve dikkat hesaplaması sırasında birbirleriyle konuşmazlar.

**Birleştir ve projekte et.** Başları `(N, d_model)` olarak geri yığınlayın ve `(d_model, d_model)` şeklinde öğrenilen bir çıktı matrisi `W_o` ile çarpın. `W_o` başların karıştığı yerdir.

**Neden çalışıyor.** Her baş, diğerleriyle temsil bütçesi için rekabet etmeden uzmanlaşabilir. 2019-2024'ten sondaj çalışmaları (probing studies), farklı baş rolleri göstermiştir: konumsal başlar, önceki token'a dikkat eden başlar, kopyalama başları, adlandırılmış varlık başları, indüksiyon başları (bağlam-içinde öğrenmeyi destekleyen).

**2026 varyasyon soyağacı:**

| Varyant | Q başları | K/V başları | Kullananlar |
|---------|---------|-----------|---------|
| Çoklu-baş (MHA) | N | N | GPT-2, BERT, T5 |
| Çoklu-sorgu (MQA) | N | 1 | PaLM, Falcon |
| Gruplanmış-sorgu (GQA) | N | G (ör. N/8) | Llama 2 70B, Llama 3+, Qwen 2+, Mistral |
| Çoklu-baş gizli (MLA) | N | düşük dereceli gizli uzaya sıkıştırılmış | DeepSeek-V2, V3 |

GQA modern varsayılanıdır çünkü neredeyse tam kaliteyi korurken KV-çerez belleğini `N/G` kat azaltır. MLA daha ileri giderek K/V'yi gizli uzaya sıkıştırır, ardından hesaplama zamanında geri projekte eder — FLOP harcar, çok daha fazla bellek kazandırır.

## İnşa Et

### Adım 1: tek başlı dikkatten başları böl

Ders 02'deki `SelfAttention`'ı alın ve bir böl/birleştir çiftiyle sarın. Bir numpy uygulaması için `code/main.py`'e bakın; mantık şudur:

```python
def split_heads(X, n_heads):
    n, d = X.shape
    d_head = d // n_heads
    return X.reshape(n, n_heads, d_head).transpose(1, 0, 2)  # (heads, n, d_head)

def combine_heads(H):
    h, n, d_head = H.shape
    return H.transpose(1, 0, 2).reshape(n, h * d_head)
```

#### Açıklama
Bu işlevler, çoklu dikkat için gerekli olan baş bölme ve birleştirme işlemlerini yapar. Bir reshape ve bir transpose — döngü yok.

Bir reshape ve bir transpose. Döngü yok. Bu tam olarak PyTorch'un `nn.MultiheadAttention` altında yaptığı şeydir.

### Adım 2: her baş için ölçekli nokta çarpımı dikkatı çalıştır

Her baş kendi Q, K, V dilimini alır. Dikkat toplu bir matris çarpımına dönüşür:

```python
def mha_forward(X, W_q, W_k, W_v, W_o, n_heads):
    Q = X @ W_q
    K = X @ W_k
    V = X @ W_v
    Qh = split_heads(Q, n_heads)         # (heads, n, d_head)
    Kh = split_heads(K, n_heads)
    Vh = split_heads(V, n_heads)
    scores = Qh @ Kh.transpose(0, 2, 1) / np.sqrt(Qh.shape[-1])
    weights = softmax(scores, axis=-1)
    out = weights @ Vh                    # (heads, n, d_head)
    concat = combine_heads(out)
    return concat @ W_o, weights
```

#### Açıklama
Her dikkat başı kendi projeksiyonlarıyla çalışır ve sonuçlar birleştirilerek tek bir çıktı elde edilir.

Gerçek donanımda `Qh @ Kh.transpose(...)` tek bir `bmm`'dir. GPU, `(heads, N, d_head) × (heads, d_head, N) -> (heads, N, N)` şeklinde tek bir toplu matris çarpımı görür. Baş eklemek ücretsizdir.

### Adım 3: Gruplanmış-Sorgu Dikkati varyantı

Sadece anahtar ve değer projeksiyonları değişir. Q `n_heads` grup alır; K ve V `n_kv_heads < n_heads` grup alır ve eşleşmek için tekrar edilir:

```python
def gqa_project(X, W, n_kv_heads, n_heads):
    kv = split_heads(X @ W, n_kv_heads)       # (kv_heads, n, d_head)
    repeat = n_heads // n_kv_heads
    return np.repeat(kv, repeat, axis=0)      # (n_heads, n, d_head)
```

#### Açıklama
GQA'da sadece K ve V projeksiyonları paylaşılır. Bu, KV-çerez belleğini önemli ölçüde azaltır.

Çıkarım sırasında bellek tasarrufu sağlar çünkü KV-çerezinde sadece `n_kv_heads` kopya yaşar, `n_heads` değil. Llama 3 70B, 64 sorgu başı ile 8 KV başı kullanır — 8× çerez küçültmesi.

### Adım 4: her başın ne öğrendiğini sondajla

Kısa bir cümlede 4 baş ile MHA çalıştırın. Her baş için `(N, N)` dikkat matrisini yazdırın. Rastgele başlangıçla bile farklı başların farklı yapıları seçtiğini göreceksiniz — bu kısmen sinyal, kısmen de alt uzaylardaki dönel simetri (rotational symmetry) kaynaklıdır.

## Kullan

PyTorch'ta tek satırlık versiyon:

```python
import torch.nn as nn

mha = nn.MultiheadAttention(embed_dim=512, num_heads=8, batch_first=True)
```

PyTorch 2.5+ ile GQA:

```python
from torch.nn.functional import scaled_dot_product_attention

# scaled_dot_product_attention CUDA'da Flash Attention'ı otomatik olarak seçer.
# GQA için, Q'yu (B, n_heads, N, d_head) ve K,V'yi
# (B, n_kv_heads, N, d_head) şeklinde geçirin. PyTorch tekrarı halleder.
out = scaled_dot_product_attention(q, k, v, is_causal=True, enable_gqa=True)
```

**Kaç baş?** 2026'daki üretim modellerinden uygulama kuralları:

| Model boyutu | d_model | n_heads | d_head |
|------------|---------|---------|--------|
| Küçük (~125M) | 768 | 12 | 64 |
| Temel (~350M) | 1024 | 16 | 64 |
| Büyük (~1B) | 2048 | 16 | 128 |
| Sınır (~70B) | 8192 | 64 | 128 |

`d_head` neredeyse her zaman 64 veya 128'e düşer. Bir başın "görebileceği" şeyin birimdir. 32'nin altına düşerseniz başlar `sqrt(d_head)` ölçekleme faktörüyle savaşmaya başlar; 256'nın üzerine çıkarsanız "birçok küçük uzman" avantajını kaybedersiniz.

## Teslim Et

`outputs/skill-mha-configurator.md`'ye bakın. Bu beceri, parametre bütçesi, dizi uzunluğu ve dağıtım hedefi verildiğinde yeni bir transformer için baş sayısını, kv-head sayısını ve projeksiyon stratejisini önerir.

## Alıştırmalar

1. **Kolay.** `code/main.py`'deki MHA'yı alın ve `n_heads`'i 1'den 16'ya, `d_model=64` sabit değiştirin. Sentetik bir kopyalama görevi üzerinde tek katmanlı bir modelin kaybını çizin. Daha fazla baş yardımcı oluyor mu, plato mu yapıyor, yoksa zarar mı veriyor?
2. **Orta.** MQA (tüm sorgu başları arasında paylaşılan tek KV başı) uygulayın. Tam MHA'ya kıyasla parametre sayısının ne kadar düştüğünü ölçün. N=2048'de çıkarım sırasında KV-çerez boyutunun ne kadar küçüldüğünü hesaplayın.
3. **Zor.** Çoklu-Baş Gizli Dikkatin (MLA) küçük bir versiyonunu uygulayın: K,V'yi derece-`r` gizli uzaya sıkıştırın, gizliyi KV-çerezinde saklayın, dikkat zamanında sıkıştırın. Çerez belleğinin tam MHA'nın 1/8'inin altına düştüğü ve kalitenin doğrulama ppl'sinden 1 bit içinde kaldığı `r` değeri nedir?

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Baş (Head) | "Tek bir dikkat devresi" | `d_head = d_model / n_heads` boyutunda tek bir Q/K/V projeksiyonu, kendi dikkat matrisine sahip. |
| d_head | "Baş boyutu" | Baş başına gizli genişlik; üretimde neredeyse her zaman 64 veya 128. |
| Böl / birleştir (Split / combine) | "Yeniden şekillendirme numaraları" | Dikkat etrafında `(N, d_model) ↔ (n_heads, N, d_head)` reshape+transpose. |
| W_o | "Çıktı projeksiyonu" | Başları birleştikten sonra uygulanan `(d_model, d_model)` matrisi; başların karıştığı yer. |
| MQA | "Tek KV başı" | Çoklu-Sorgu Dikkati: tek paylaşılan K/V projeksiyonu. En küçük KV çerezi, bazı kalite kayıpları. |
| GQA | "Llama 2'den beri varsayılan" | `n_kv_heads < n_heads` ile Gruplanmış-Sorgu Dikkati; Q'ya eşleşmek için tekrar eder. |
| MLA | "DeepSeek'in numarası" | Çoklu-Baş Gizli Dikkat: K,V düşük dereceli gizliye sıkıştırılır, dikkat anında sıkıştırılır. |
| İndüksiyon başı (Induction head) | "Bağlam-içinde öğrenmenin arkasındaki devre" | Daha önceki oluşumları tespit edip ardından gelenleri kopyalayan bir baş çifti. |

## İleri Okuma

- [Vaswani ve diğerleri (2017). Attention Is All You Need §3.2.2](https://arxiv.org/abs/1706.03762) — orijinal çoklu-baş specification'ı.
- [Shazeer (2019). Fast Transformer Decoding: One Write-Head is All You Need](https://arxiv.org/abs/1911.02150) — MQA makalesi.
- [Ainslie ve diğerleri (2023). GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints](https://arxiv.org/abs/2305.13245) — eğitimin ardından MHA'yı GQA'ya dönüştürme.
- [DeepSeek-AI (2024). DeepSeek-V2 Technical Report](https://arxiv.org/abs/2405.04434) — MLA ve neden çerez belleğinde MHA/GQA'yı yener.
- [Olsson ve diğerleri (2022). In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html) — başların aslında ne yaptığına mekanistik bir bakış.
