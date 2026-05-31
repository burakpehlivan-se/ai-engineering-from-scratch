# Tam Transformer — Encoder + Decoder

> Dikkat (attention) yıldızdır. Geri kalan her şey — artık bağlar (residuals), normalizasyon, besleme-öncü (feed-forward), çapraz-dikkat (cross-attention) — onu derin yığınlayabilmeniz için gerekli iskeleti oluşturur.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 02 (Self-Attention), Faz 7 · 03 (Multi-Head Attention), Faz 7 · 04 (Konumsal Kodlama / Positional Encoding)
**Süre:** ~75 dakika

## Sorun

Tek bir dikkat katmanı bir özellik çıkarıcıdır (feature extractor), bir model değildir. Katman başına tek bir matmul, dil için yeterli kapasiteye sahip değildir. Derinliğe ihtiyacınız vardır — ve derinlik doğru tesisat (plumbing) olmadan çöker.

2017 Vaswani makalesi, tek bir dikkat katmanını yığılabilir bir bloğa dönüştüren altı tasarım kararını paketledi. O zamandan beri her transformer — sadece encoder (BERT), sadece decoder (GPT), encoder-decoder (T5) — aynı iskeleti miras alır. 2026'da bloklar iyileştirilmiştir (RMSNorm, SwiGLU, ön-normalizasyon / pre-norm, RoPE) ancak iskelet aynıdır.

Bu ders iskelettir. Sonraki dersler onu özelleştirir — 06 encoder'lar için, 07 decoder'lar için, 08 encoder-decoder için.

## Kavram

![Encoder ve decoder bloğu iç yapıları, bağlantılar](../assets/full-transformer.svg)

### Altı parça

1. **Gömme + konumsal sinyal.** Token'lar → vektörler. Konum RoPE (modern) veya sinüzoidal (klasik) yoluyla eklenir.
2. **Self-attention.** Her konum diğer her konuma dikkat eder. Decoder'larda maskelidir.
3. **Besleme-öncü ağı (FFN).** Konum bazlı iki katmanlı MLP: `W_2 · activation(W_1 · x)`. Varsayılan genişleme oranı 4×.
4. **Artık bağ (Residual connection).** `x + sublayer(x)`. Bunun olmadan, gradyanlar ~6 katmandan sonra kaybolur (vanish).
5. **Katman normalizasyonu (Layer normalization).** `LayerNorm` veya `RMSNorm` (modern). Artık akışını stabilize eder.
6. **Çapraz-dikkat (Cross-attention) (sadece decoder).** Sorgular decoder'dan gelir, anahtarlar ve değerler encoder çıktısından gelir.

### Encoder bloğu (BERT, T5 encoder tarafından kullanılır)

```
x → LN → MHA(self) → + → LN → FFN → + → out
                     ^              ^
                     |              |
                     └── residual ──┘
```

#### Açıklama
Encoder çift yönlüdür (bidirectional). Maske yoktur. Tüm konumlar tüm konumları görür.

### Decoder bloğu (GPT, T5 decoder tarafından kullanılır)

```
x → LN → MHA(masked self) → + → LN → MHA(cross to encoder) → + → LN → FFN → + → out
```

#### Açıklama
Decoder blok başına üç alt katman taşır. Ortadaki — çapraz-dikkat — bilginin encoder'dan decoder'a aktarıldığı tek yerdir. Saf bir sadece-decoder mimarisinde (GPT), çapraz-dikkat atlanır ve sadece maskelenmiş self-attention + FFN kalır.

### Ön-normalizasyon vs son-normalizasyon

Orijinal makale: `x + sublayer(LN(x))` vs `LN(x + sublayer(x))`. Son-normalizasyon (post-norm) 2019 civarında popülerliğini kaybetti — dikkatli bir ısınma (warmup) olmadan derin eğitilmesi zordur. Ön-normalizasyon (`LN` *sublayer'dan önce*) 2026'nın varsayılanıdır: Llama, Qwen, GPT-3+, Mistral hepsi bunu kullanır.

### 2026 modernize edilmiş blok

Vaswani 2017'de LayerNorm + ReLU ile çıktı. Modern yığınlar ikisini de değiştirdi. Üretim bloklarının gerçekte görünümü:

| Bileşen | 2017 | 2026 |
|-----------|------|------|
| Normalizasyon | LayerNorm | RMSNorm |
| FFN aktivasyonu | ReLU | SwiGLU |
| FFN genişlemesi | 4× | 2.6× (SwiGLU üç matris kullanır, toplam parametre sayısı eşleşir) |
| Konum | Sinüzoidal mutlak | RoPE |
| Dikkat | Tam MHA | GQA (veya MLA) |
| Önyargı terimleri (Bias) | Evet | Hayır |

#### Açıklama
RMSNorm, LayerNorm'un ortalama merkezleme işlemini bırakır (bir çıkarma işlemi daha az), bu hesaplama süresinden tasarruf sağlar ve deneysel olarak en az aynı kararlılığı gösterir. SwiGLU (`Swish(W1 x) ⊙ W3 x`) Llama, PaLM ve Qwen makalelerinde ppl'de ~0.5 puan tutarlı olarak ReLU/GELU FFN'yi geçer.

### Parametre sayısı

`d_model = d` ve FFN genişlemesi `r` olan bir blok için:

- MHA: `4 · d²` (Q, K, V, O projeksiyonları)
- FFN (SwiGLU): `3 · d · (r · d)` ≈ `3rd²`
- Normlar: ihmal edilebilir

`d = 4096, r = 2.6, katman = 32`'de (kabaca Llama 3 8B), toplam: `32 · (4·4096² + 3·2.6·4096²) ≈ 32 · (16 + 32) M = ~1.5B parametre katman başına × 32 ≈ 7B` (artı gömmeler ve kafa). Yayınlanan sayımlarla eşleşir.

## İnşa Et

### Adım 1: yapı taşları

Ders 03'teki küçük `Matrix` sınıfını kullanarak (bağımsızlık için bu dosyaya kopyalandı):

- `layer_norm(x, eps=1e-5)` — ortalamayı çıkar, std'ye böl.
- `rms_norm(x, eps=1e-6)` — RMS'ye böl. Ortalama çıkarma yok.
- `gelu(x)` ve `silu(x) * W3 x` (SwiGLU).
- `ffn_swiglu(x, W1, W2, W3)`.
- `encoder_block(x, params)` ve `decoder_block(x, enc_out, params)`.

Tam bağlantılar için `code/main.py`'e bakın.

### Adım 2: 2 katmanlı encoder ve 2 katmanlı decoder bağlayın

Onları yığın. Encoder çıktısını her decoder çapraz-dikkatine geçirin. Çıktı projeksiyonundan önce son bir LN ekleyin.

```python
def encode(tokens, params):
    x = embed(tokens, params.emb) + sinusoidal(len(tokens), params.d)
    for block in params.encoder_blocks:
        x = encoder_block(x, block)
    return x

def decode(target_tokens, encoder_out, params):
    x = embed(target_tokens, params.emb) + sinusoidal(len(target_tokens), params.d)
    for block in params.decoder_blocks:
        x = decoder_block(x, encoder_out, block)
    return x
```

#### Açıklama
Encode fonksiyonu girdi token'larını alır ve encoder bloklarından geçirerek anlamsal temsili üretir. Decode fonksiyonu hedef token'ları ve encoder çıktısını alarak çapraz-dikkat ile her adımda bir sonraki token'ı üretir.

### Adım 3: küçük bir örnek üzerinde ileriye doğru çalıştırma

6 token'lı bir kaynak ve 5 token'lı bir hedef besleyin. Çıktı şeklinin `(5, vocab)` olduğunu doğrulayın. Eğitim yok — bu ders mimariyle ilgili, kayıpla değil.

### Adım 4: RMSNorm + SwiGLU ile değiştirme

LayerNorm ve ReLU-FFN'i RMSNorm ve SwiGLU ile değiştirin. Şekillerin hala eşleştiğini doğrulayın. Bu tek bir işlev ikamesiyle 2026 modernizasyonudur.

## Kullan

PyTorch/TF referans uygulamaları: `nn.TransformerEncoderLayer`, `nn.TransformerDecoderLayer`. Ancak 2026 üretimi kodun çoğu kendi bloğunu yazar çünkü:

- Flash Attention dikkat içinde çağrılır, `nn.MultiheadAttention` üzerinden değil.
- GQA / MLA standart kütüphane referansında yoktur.
- RoPE, RMSNorm, SwiGLU PyTorch varsayılanları değildir.

HF `transformers`'ta okumanız gereken temiz referans blokları vardır: `modeling_llama.py` 2026'nın kanonik sadece-decoder bloğudur. ~500 satırdır ve bir kez yürütmeye değerdir.

**Encoder vs decoder vs encoder-decoder — ne zaman seçilir:**

| İhtiyaç | Seçin | Örnek |
|------|------|---------|
| Sınıflandırma, gömmeler, metin üzerinde QA | Sadece encoder | BERT, DeBERTa, ModernBERT |
| Metin üretimi, sohbet, kod, muhakeme | Sadece decoder | GPT, Llama, Claude, Qwen |
| Yapılandırılmış girdi → yapılandırılmış çıktı (çeviri, özetleme) | Encoder-decoder | T5, BART, Whisper |

Sadece-decoder dili fethetti çünkü en temiz şekilde ölçeklenir ve hem anlama hem üretimi işler. Encoder-decoder, girdinin net bir "kaynak dizisi" kimliği taşıdığı yerde (çeviri, konuşma tanıma, yapılandırılmış görevler) hala en iyisidir.

## Teslim Et

`outputs/skill-transformer-block-reviewer.md`'ye bakın. Bu beceri, yeni bir transformer blok uygulamasını 2026 varsayımlarına göre inceler ve eksik parçaları (ön-normalizasyon, RoPE, RMSNorm, GQA, FFN genişleme oranı) bayraklar.

## Alıştırmalar

1. **Kolay.** `d_model=512, n_heads=8, ffn_expansion=4, swiglu=True` ile encoder_block'ınızdaki parametreleri sayın. Bloğu uygulayarak ve `sum(p.numel() for p in block.parameters())` kullanarak doğrulayın.
2. **Orta.** Son-normalizasyondan ön-normalizasyona geçin. Her ikisini de başlatın ve rastgele girdi üzerinde 12 yığılmış katmandan sonra aktivasyon normunu ölçün. Son-normalizasyonun aktivasyonları patlamalı; ön-normalizasyonunki sınırlı kalmalıdır.
3. **Zor.** Küçük bir kopyalama görevinde 4 katmanlı encoder-decoder uygulayın (`x`'i ters çevrilmiş olarak kopyalayın). 100 adım eğitin. Kaybı raporlayın. RMSNorm + SwiGLU + RoPE ekleyin — kayıp düşer mi?

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Blok (Block) | "Tek bir transformer katmanı" | Norm + dikkat + norm + FFN yığını, artık bağlantılarla sarılmış. |
| Artık (Residual) | "Atlama bağlantısı" | `x + f(x)` çıkışı; derin yığınlardan gradyan akışını sağlar. |
| Ön-normalizasyon (Pre-norm) | "Önce normalleştir, sonra değil" | Modern: `x + sublayer(LN(x))`. Isınma jimnastiği olmadan daha derin eğitilir. |
| RMSNorm | "Ortalama olmadan LayerNorm" | RMS'ye böl; bir işlem daha az, aynı deneysel kararlılık. |
| SwiGLU | "Herkesin geçtiği FFN" | `Swish(W1 x) ⊙ W3 x → W2`. LM ppl'de ReLU/GELU'yu geçer. |
| Çapraz-dikkat (Cross-attention) | "Decoder'ın encoder'ı nasıl gördüğü" | Decoder'dan Q, encoder çıkışlarından K/V ile MHA. |
| FFN genişlemesi | "Orta MLP'nin ne kadar geniş olduğu" | Gizli boyut / d_model oranı, genellikle 4 (LayerNorm) veya 2.6 (SwiGLU). |
| Önyargısız (Bias-free) | "+b terimlerini bırakın" | Modern yığınlar lineer katmanlarda önyargıları atlar; hafif ppl iyileştirmesi, daha küçük model. |

## İleri Okuma

- [Vaswani ve diğerleri (2017). Attention Is All You Need](https://arxiv.org/abs/1706.03762) — orijinal blok specification'ı.
- [Xiong ve diğerleri (2020). On Layer Normalization in the Transformer Architecture](https://arxiv.org/abs/2002.04745) — neden ön-normalizasyon derinlikte son-normalizasyonu geçer.
- [Zhang, Sennrich (2019). Root Mean Square Layer Normalization](https://arxiv.org/abs/1910.07467) — RMSNorm.
- [Shazeer (2020). GLU Variants Improve Transformer](https://arxiv.org/abs/2002.05202) — SwiGLU makalesi.
- [HuggingFace `modeling_llama.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py) — kanonik 2026 sadece-decoder bloğu.
