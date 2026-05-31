# Konumsal Kodlama (Positional Encoding) — Sinüzoidal, RoPE, ALiBi

> Dikkat permutasyona karşı değişmezdir (permutation-invariant). "Kedi halıya oturdu" ve "halıya oturdu kedi" sinyal olmadan aynı çıktıyı üretir. Üç algoritma bunu düzeltir — her biri "konum"un ne anlama geldiği konusunda farklı bir bahse girer.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 02 (Self-Attention), Faz 7 · 03 (Çoklu-Baş Dikkati)
**Süre:** ~45 dakika

## Sorun

Ölçekli nokta çarpımı dikkatı sıradanlığın (order) farkında değildir. `softmax(Q K^T / √d) V` dikkat matrisi çiftleşik benzerliklerden hesaplanır. `X`'in satırlarını karıştırın, çıktının satırları da aynı şekilde karıştırılır. Dikkat içinde konum umrunda değildir.

Bu bir çanta-kelimeler (bag-of-words) modelinde hata değildir. Dil, kod, ses, video — konumun anlam taşıdığı her şey için — bu ölümcüldür.

Düzeltme, konumu bir şekilde gömelilere enjekte etmektir. Üç çağdan yanıtlar:

1. **Mutlak sinüzoidal** (Vaswani 2017). Gömüme konumun `sin/cos` değerini ekleyin. Basit, öğrenmez, eğitimin ötesinde zayıf dışa aktarım.
2. **RoPE — Dönel Konum Gömüsü** (Su 2021). Q ve K vektörlerini konumla orantılı bir açıyla döndürün. *Bağıl* konumu doğrudan nokta çarpımında kodlar. 2026'da baskın.
3. **ALiBi — Doğrusal Eğilimli Dikkat** (Press 2022). Gömileri tamamen atlayın; mesafeye dayalı baş-başına doğrusal cezayı dikkat puanlarına ekleyin. Mükemmel uzunluk dışa aktarımı.

2026 itibarıyla, neredeyse tüm sınırlı açık model RoPE kullanır: Llama 2/3/4, Qwen 2/3, Mistral, Mixtral, DeepSeek-V3, Kimi. Bir avuç uzun-bağlam modeli ALiBi veya modern varyantlarını kullanır. Mutlak sinüzoidal tarihseldir.

## Kavram

![Sinüzoidal mutlak vs RoPE döndürmeleri vs ALiBi mesafe eğilimi](../assets/positional-encoding.svg)

### Mutlak sinüzoidal

Önceden `(max_len, d_model)` şeklinde sabit bir `PE` matrisi hesaplayın:

```
PE[pos, 2i]   = sin(pos / 10000^(2i / d_model))
PE[pos, 2i+1] = cos(pos / 10000^(2i / d_model))
```

#### Açıklama
Her boyut, farklı bir frekansta sinüzoidal bir sinyal alır. Model, konumu faz deseninden okumayı öğrenir.

Sonra dikkatten önce `X' = X + PE[:N]`. Her boyut farklı frekansta bir sinüzdür. Model konumu faz deseninden okumayı öğrenir. `max_len`'in ötesinde başarısız olur: model sadece 0-2047 konumlarını看到ken 2048. konumda ne olduğunu hiçbir şey söylemedi.

### RoPE

Q ve K vektörlerini (gömüleri değil) döndürün. `(2i, 2i+1)` boyut çifti için:

```
[q'_2i    ]   [ cos(pos·θ_i)  -sin(pos·θ_i) ] [q_2i   ]
[q'_2i+1  ] = [ sin(pos·θ_i)   cos(pos·θ_i) ] [q_2i+1 ]

θ_i = base^(-2i / d_head),  varsayılan = 10000
```

#### Açıklama
RoPE, sorgu ve anahtar vektörlerini konum-bağımlı açıyla döndürür. Nokta çarpımı sadece bağıl mesafeye bağlı hale gelir.

`pos_k` konumundaki anahtarlara aynı döndürmeyi uygulayın. `q'_m · k'_n` nokta çarpımı `(m - n)`'in tek bir işlevi olur. Yani: **dikkat puanı sadece bağıl mesafeye bağlıdır**, döndürme mutlak konumlardan yapılmış olsa bile. Güzel bir numara.

RoPE'yi genişletme: `base`, yeniden eğitmeden daha uzun bağlamalara dışa aktarmak için ölçeklenebilir (NTK-farkında, YaRN, LongRoPE). Llama 3'ü bu şekilde 8K'dan 128K bağlamına genişletti.

### ALiBi

Gömü numarasını atlayın. Dikkat puanlarını doğrudan eğilimlendirin:

```
dikkat_puanı[i, j] = (q_i · k_j) / √d  -  m_h · |i - j|
```

Burada `m_h` başa özgü bir eğimdir (ör. `1 / 2^(8·h/H)`). Daha yakın token'lar desteklenir; uzak token'lar cezalandırılır. Eğitim-sırası maliyeti yoktur. Makale, sinüzoidal ile RoPE'nin orijinal eğitim uzunluğunda eşleştiğini gösterir.

### 2026'da ne seçmeli

| Varyant | Dışa aktarım | Eğitim maliyeti | Kullananlar |
|---------|---------------|---------------|---------|
| Mutlak sinüzoidal | zayıf | ücretsiz | orijinal transformer, erken BERT |
| Öğrenilen mutlak | yok | çok az | GPT-2, GPT-3 |
| RoPE | ölçekleme ile iyi | ücretsiz | Llama 2/3/4, Qwen 2/3, Mistral, DeepSeek-V3, Kimi |
| RoPE + YaRN | mükemmel | ince-ayar aşaması | Qwen2-1M, Llama 3.1 128K |
| ALiBi | mükemmel | ücretsiz | BLOOM, MPT, Baichuan |

RoPE mimariyi değiştirmeden dikkatin içine girdiği, bağıl konumu kodladığı ve `base` hiper-parametresinin uzun-bağlam ince-ayarı için temiz bir kol verdiği için kazandı.

## İnşa Et

### Adım 1: sinüzoidal kodlama

`code/main.py`'ye bakın. 4 satırlık bir hesaplama:

```python
def sinusoidal(N, d):
    pe = [[0.0] * d for _ in range(N)]
    for pos in range(N):
        for i in range(d // 2):
            theta = pos / (10000 ** (2 * i / d))
            pe[pos][2 * i]     = math.sin(theta)
            pe[pos][2 * i + 1] = math.cos(theta)
    return pe
```

#### Açıklama
Bu işlev, sinüzoidal konumsal kodlama matrisini hesaplar. Her konum ve boyut çifti için sin ve cos değerleri üretilir.

Bunu ilk dikkat katmanından önce gömme matrisine ekleyin.

### Adım 2: Q, K'ya uygulanan RoPE

RoPE, Q ve K üzerinde yerinde çalışır. Her boyut çifti için:

```python
def apply_rope(x, pos, base=10000):
    d = len(x)
    out = list(x)
    for i in range(d // 2):
        theta = pos / (base ** (2 * i / d))
        c, s = math.cos(theta), math.sin(theta)
        a, b = x[2 * i], x[2 * i + 1]
        out[2 * i]     = a * c - b * s
        out[2 * i + 1] = a * s + b * c
    return out
```

#### Açıklama
RoPE, her boyut çiftine konum-bağılı bir açıyla döndürme uygular. Bu, nokta çarpımının sadece bağıl mesafeye bağlı olmasını sağlar.

Kritik: `m` konumundaki Q ve `n` konumundaki K'ya aynı işlevi uygulayın. Nokta çarpımları her koordinat çiftinde `cos((m-n)·θ_i)` çarpanını alır. Dikkat bağıl konumu ücretsiz olarak öğrenir.

### Adım 3: ALiBi eğimleri ve eğilimi

```python
def alibi_bias(n_heads, seq_len):
    # slope_h = 2 ** (-8 * h / n_heads) for h = 1..n_heads
    slopes = [2 ** (-8 * (h + 1) / n_heads) for h in range(n_heads)]
    bias = []
    for m in slopes:
        row = [[-m * abs(i - j) for j in range(seq_len)] for i in range(seq_len)]
        bias.append(row)
    return bias  # softmazdan önce dikkat puanlarına ekleyin
```

#### Açıklama
ALiBi, her baş için mesafeye orantılı bir ceza ekler. Daha yakın token'lar daha yüksek ağırlık alır.

Baş `h`'nin `(seq_len, seq_len)` dikkat puanı matrisine `bias[h]` ekleyin, sonra softmaks uygulayın.

### Adım 4: RoPE'nin bağıl-mesafe özelliğini doğrula

Rastgele iki vektör `a, b` seçin. `(pos_a, pos_b)` ile döndürün. Sonra `(pos_a + k, pos_b + k)` ile. Her iki nokta çarpımı da kayan nokta hatası içinde eşleşmelidir. Bu özellik RoPE'nin tamamıdır — mutlak ofsete değişmezdir, sadece bağıl boşluk önemlidir.

## Kullan

PyTorch 2.5+ `torch.nn.functional` içinde RoPE yardımcı programları sunar. Üretim kodunun çoğu `flash_attn` veya `xformers` kullanır, burada RoPE dikkat çekirdeğinin içinde uygulanır.

```python
from transformers import AutoModel
model = AutoModel.from_pretrained("meta-llama/Llama-3.2-3B")
# model.config.rope_scaling → {"type": "yarn", "factor": 32.0, "original_max_position_embeddings": 8192}
```

**2026'da uzun-bağlam numaraları:**

- **NTK-farkında interpolasyon.** 4K'dan 16K+'ya genişletirken `base`'i `base * (scale_factor)^(d/(d-2))` olarak yeniden ölçekleyin.
- **YaRN.** Uzun bağlamlarda dikkat entropisini koruyan daha akıllı interpolasyon. Llama 3.1 128K bunu kullanır.
- **LongRoPE.** Microsoft'un 2024 yöntemi, boyut-başına ölçek faktörlerini seçmek için evrimsel arama kullanır. Phi-3-Long bunu kullanır.
- **Konum interpolasyonu + ince-ayar.** Konumları genişletme çarpanıyla küçültün ve 1-5B token için ince-ayar yapın. Şaşırtıcı derecede etkilidir.

## Teslim Et

`outputs/skill-positional-encoding-picker.md`'ye bakın. Bu beceri, hedef bağlam uzunluğu, dışa aktarım ihtiyaçları ve eğitim bütçesi verildiğinde yeni bir model için bir kodlama stratejisi seçer.

## Alıştırmalar

1. **Kolay.** Sinüzoidal `PE` matrisini `max_len=512, d=128` için ısı haritası olarak çizin. "Şeritler boyut indeksiyle birlikte genişler" desenini doğrulayın.
2. **Orta.** NTK-farkında RoPE ölçeklemesi uygulayın. 256 uzunluğunda dizeler üzerinde küçük bir LM eğitin, sonra 1024 uzunluğunda ölçekleme ile ve olmadan test edin. Perplexity'yi ölçün.
3. **Zor.** Aynı dikkat modülünde ALiBi ve RoPE uygulayın. 512 uzunluğunda dizelerle bir kopyalama görevinde 4 katmanlı bir transformer eğitin. Test sırasında 2028'e dışa aktarın. Bozulmayı karşılaştırın.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Konumsal kodlama | "Dikkata sırayı söyler" | Gömelilere veya dikkate eklenen, konumu kodlayan herhangi bir sinyal. |
| Sinüzoidal | "Orijinal olan" | Gömelilere geometrik frekanslarda eklenen `sin/cos`; dışa aktarmaz. |
| RoPE | "Dönel gömüler" | Q, K'yı konum-bağılı açıyla döndür; nokta çarpımı bağıl mesafeyi kodlar. |
| ALiBi | "Doğrusal eğilim numarası" | Dikkat puanlarına `-m·\|i-j\|` ekle; gömü gerekmez, mükemmel dışa aktarım. |
| base | "RoPE'nin kolu" | RoPE'deki frekans ölçekleyicisi; bağlamları genişletmek için artırın. |
| NTK-farkında | "Bir RoPE ölçekleme numarası" | Bağlam genişlediğinde yüksek frekanslı boyutların sıkışmaması için `base`'i yeniden ölçekleyin. |
| YaRN | "Gösterişli olan" | Dikkat entropisini koruyan boyut-başına interpolasyon+dışa aktarım. |
| Dışa aktarım | "Eğitim uzunluğunun ötesinde çalışır" | Konum şeması, eğitimde görülen `max_len`'in ötesinde doğru çıktı üretebilir mi? |

## İleri Okuma

- [Vaswani ve diğerleri (2017). Attention Is All You Need §3.5](https://arxiv.org/abs/1706.03762) — orijinal sinüzoidal.
- [Su ve diğerleri (2021). RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864) — RoPE makalesi.
- [Press, Smith, Lewis (2021). Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation](https://arxiv.org/abs/2108.12409) — ALiBi.
- [Peng ve diğerleri (2023). YaRN: Efficient Context Window Extension of Large Language Models](https://arxiv.org/abs/2309.00071) — en son RoPE ölçeklemesi.
- [Chen ve diğerleri (2023). Extending Context Window of Large Language Models via Positional Interpolation](https://arxiv.org/abs/2306.15595) — Meta'nın Llama 2 uzun-bağlam makalesi.
- [Ding ve diğerleri (2024). LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens](https://arxiv.org/abs/2402.13753) — Phi-3-Long ve Kullan bölümünde atıfta bulunulan Microsoft yöntemi.
- [HuggingFace Transformers — `modeling_rope_utils.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/modeling_rope_utils.py) — her RoPE ölçekleme şemasının üretim-sınıfı uygulamaları (varsayılan, doğrusal, dinamik, YaRN, LongRoPE, Llama-3).
