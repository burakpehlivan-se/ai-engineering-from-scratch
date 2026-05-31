# Dikkat Varyantları — Kayan Pencere, Seyreltik, Farklılaştırılmış

> Tam dikkat bir çemberdir. Her token her token'ı görür ve bellek bedelini öder. Dört varyant çemberin şeklini büker ve maliyetin yarısını kurtarır.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 02 (Self-Attention), Faz 7 · 03 (Çoklu-Baş), Faz 7 · 12 (KV-Çerez / Flash Attention)
**Süre:** ~60 dakika

## Sorun

Tam dikkat, dizi uzunluğunda `O(N²)` bellek ve `O(N²)` hesaplama maliyetine sahiptir. 128K bağlam uzunluklu Llama 3 70B için bu katman başına 16 milyar dikkat girişi, 80 katman ile çarpılır. Flash Attention (Ders 12) `O(N²)` aktivasyon belleğini gizler ancak aritmetik maliyeti değiştirmez — her token hala her otra token'a dikkat eder.

Varyantların üç sınıfı, dikkat matrisinin topolojisinin kendisini değiştirir:

1. **Kayan pencere dikkati (Sliding Window Attention / SWA).** Her token sabit bir komşu penceresine, tüm öneke değil dikkat eder. Bellek ve hesaplama `O(N · W)`'ye düşer, burada W penceredir. Gemma 2/3, Mistral 7B'nin ilk katmanları, Phi-3-Long.
2. **Seyreltik / blok dikkati.** Yalnızca seçilmiş `(i, j)` çiftleri puanlanır; geri kalanı sıfır ağırlığa zorlanır. Longformer, BigBird, OpenAI seyreltik transformer'ı.
3. **Farklılaştırılmış dikkat (Differential attention).** Ayrı Q/K projeksiyonlarıyla iki dikkat haritası hesaplayın, birini diğerinden çıkarın. İlk birkaç token'a ağırlık sızmış olan "dikkat çukurunu" (attention sink) öldürür. Microsoft'un DIFF Transformer'ı (2024).

Bunlar bir arada var olur. 2026 sınır modeli genellikle bunları karıştırır: çoğu katman SWA-1024, her beşinci küresel tam dikkat ve bir avuç farklılaştırılmış baş, getirmeyi temizler. Gemma 3'ün 5:1 SWA-küresel oranı, güncel ders kitabısı varsayılandır.

## Kavram

### Kayan Pencere Dikkati (SWA)

`i` konumundaki her sorgu, `[i - W, i]` (nedensel SWA) veya `[i - W/2, i + W/2]` (çift yönlü) konumlarındaki pencerelere dikkat eder. Pencere dışındaki token'lara puan matrisinde `-inf` verilir.

```
full causal:           sliding window (W=4):
positions 0-7          positions 0-7, W=4
    0 1 2 3 4 5 6 7        0 1 2 3 4 5 6 7
0 | x                0 |  x
1 | x x              1 |  x x
2 | x x x            2 |  x x x
3 | x x x x          3 |  x x x x
4 | x x x x x        4 |    x x x x
5 | x x x x x x      5 |      x x x x
6 | x x x x x x x    6 |        x x x x
7 | x x x x x x x x  7 |          x x x x
```

#### Açıklama
`N = 8192` ve `W = 1024` için, puan matrisinin beklenti olarak 1024 × 8192 sıfır-dışı satırı vardır — 8× azalma.

`N = 8192` ve `W = 1024` için, puan matrisinin beklenti olarak 1024 × 8192 sıfır-dışı satırı vardır — 8× azalma.

**KV-çerez SWA ile küçülür.** Katman başına yalnızca son `W` token'ın K ve V'si tutulması gerekir. Gemma-3 benzeri bir yapılandırma için (1024 pencere, 128K bağlam), KV-çerez 128× düşer.

**Kalite bedeli.** Yalnızca SWA transformer'ları uzun menzilli getirme konusunda zorlanır. Düzeltme: SWA katmanlarını tam dikkat katmanlarıyla harmanlayın. Gemma 3, 5:1 SWA:küresel kullanır. Mistral 7B, bilginin örtüşmeli pencerelerden "ileriye doğru aktığı" bir nedensel-SWA yığını kullandı — her katman etkin reseptif alanı `W` kadar uzatır ve `L` katmandan sonra model `L × W` token geriye dikkat edebilir.

### Seyreltik / Blok Dikkati

Önceden bir `N × N` seyreltiklik (sparsity) paterni seçin. Üç kanonik şekil:

- **Yerel + adım-adımlı (OpenAI seyreltik transformer).** Son `W` token'a artı her `stride`. token'a dikkat edin. Yerel ve uzun menzilli aynı anda yakalar, `O(N · sqrt(N))` hesaplamayla.
- **Longformer / BigBird.** Yerel pencere + herkesin dikkat ettiği ve herkesin dikkat ettiği bir avuç global token (ör. `[CLS]`) + rastgele-seyreltik bağlantılar. Eşleşen kalitede empirik 2× bağlam.
- **Yerli Seyreltik Dikkat (Native Sparse Attention)** (DeepSeek, 2025). Hangi `(Q, K)` bloklarının önemli olduğunu öğrenin; sıfır blokları çekirdek düzeyinde atlayın. FlashAttention-uyumlu.

Seyreltik dikkat bir çekirdek-mühendisliği hikayesidir. Matematik basittir (puan matrisini maskeleyin); kazanç, sıfır girişlerini asla SRAM'e yüklemekten gelir. FlashAttention-3 ve 2026 FlexAttention API'si, özel seyreltik paternleri PyTorch'ta birinci sınıf yapar.

### Farklılaştırılmış Dikkat (DIFF Transformer, 2024)

Düzenli dikkatin bir "dikkat çukuru" sorunu vardır: softmax her satırı 1'e toplamaya zorlar, bu nedenle özellikle bir şeye dikkat etmek istemeyen token'lar ağırlığı ilk token'a (veya birkaçına) boşaltır. Bu, gerçek içeriğe gitmesi gereken kapasiteyi çalar.

Farklılaştırılmış dikkat, **iki** dikkat haritası hesaplayarak ve çıkararak bunu düzeltir:

```
A1 = softmax(Q1 K1^T / √d)
A2 = softmax(Q2 K2^T / √d)
DiffAttn = (A1 - λ · A2) V
```

#### Açıklama
Burada `λ` öğrenilmiş bir skalerdir (genellikle 0,5–0,8). A1 gerçek içerik ağırlıklarını yakalar; A2 çukuru yakalar. Çıkarma, çukuru iptal eder, ağırlığı ilgili token'lara yeniden dağıtır.

Bildirilen sonuçlar (Microsoft 2024): %5–10 daha düşük perplexity, aynı eğitim uzunluğunda 1,5–2× daha uzun etkin bağlam, daha keskin iğne-ot-balyazu (needle-in-haystack) getirmesi.

### Varyant Karşılaştırması

| Varyant | Hesaplama | KV-çerez | Kalite vs tam | Üretim kullanımı |
|---------|---------|----------|-----------------|----------------|
| Tam dikkat | O(N²) | katman başına O(N) | temel çizgi | her modelin varsayılan katmanı |
| SWA (pencere 1024) | O(N·W) | katman başına O(W) | -0,1 ppl, global katmanlarla iyi | Gemma 2/3, Phi-3-Long |
| Yerel + adım-adımlı seyreltik | O(N·√N) | karışık | SWA'ya benzer | OpenAI seyreltik transformer, Longformer |
| BigBird (yerel + küresel + rastgele) | O(N) yaklaşık | karışık | 2× bağlamda tam ile eşleşir | erken uzun-bağlam BERT |
| Yerli Seyreltik (DeepSeek-V3.2) | O(N · etkin oran) | O(N) | 0,05 ppl içinde | DeepSeek-V3.2, 2025 |
| Farklılaştırılmış | O(2·N²) | O(2N) | %5-10 ppl | DIFF Transformer, 2026'nın başları |

## İnşa Et

`code/main.py`'ye bakın. Küçük bir dizi üzerinde tam, SWA, yerel+adım-adımlı ve farklılaştırılmış dikkati yan yana gösteren bir nedensel maske karşılaştırıcısı uyguluyoruz.

### Adım 1: tam nedensel maske (temel çizgi)

```python
def causal_mask(n):
    return [[0.0 if j <= i else float("-inf") for j in range(n)] for i in range(n)]
```

#### Açıklama
Ders 07'den temel çizgi. Alt-üçgen; diyagonalin üzerinde sıfır ağırlık.

### Adım 2: kayan pencere nedensel maskesi

```python
def swa_mask(n, window):
    M = [[float("-inf")] * n for _ in range(n)]
    for i in range(n):
        lo = max(0, i - window + 1)
        for j in range(lo, i + 1):
            M[i][j] = 0.0
    return M
```

#### Açıklama
Tek parametre — `pencere`. `pencere >= n` için tam nedensel dikkat elde edersiniz. `pencere = 1` için her token yalnızca kendisine dikkat eder.

### Adım 3: yerel + adım-adımlı seyreltik maske

```python
def strided_mask(n, window, stride):
    M = [[float("-inf")] * n for _ in range(n)]
    for i in range(n):
        lo = max(0, i - window + 1)
        for j in range(lo, i + 1):
            M[i][j] = 0.0
        for j in range(0, i + 1, stride):
            M[i][j] = 0.0
    return M
```

#### Açıklama
Yoğun yerel pencere artı dizinin başından itibaren her `stride`. token. Ek katmanlarla reseptif alan logaritmik adımlarla büyür.

### Adım 4: farklılaştırılmış dikkat

```python
def diff_attention(Q1, K1, Q2, K2, V, lam):
    A1 = softmax_causal(Q1 @ K1.T / sqrt_d)
    A2 = softmax_causal(Q2 @ K2.T / sqrt_d)
    return (A1 - lam * A2) @ V
```

#### Açıklama
İki dikkat geçişi, öğrenilmiş bir karıştırma katsayısıyla çıkarılır. Kodda tekli vs farklılaştırılmış dikkat-çukuru ısı haritasını karşılaştırır ve çukurun çöktüğünü görürüz.

### Adım 5: KV-çerez boyutları

Her varyant için `N = 131072`'de katman başına çerez boyutunu yazdırın. SWA ve seyreltik varyantlar 10–100× düşer. Farklılaştırılmış olan ise ikiye katlanır. Bellek faturanızı bilinçli ödeyin.

## Kullan

2026 üretim kalıpları:

```python
from transformers import AutoModelForCausalLM
# Gemma 3, SWA (pencere=1024) ve global katmanları 5:1 oranında karıştırır.
model = AutoModelForCausalLM.from_pretrained("google/gemma-3-27b-it")
# print(model.config.sliding_window, model.config.layer_types)
```

PyTorch 2.5+ FlexAttention bir maske fonksiyonu kabul eder:

```python
from torch.nn.attention.flex_attention import flex_attention, create_block_mask

def swa_pattern(b, h, q_idx, kv_idx):
    return (q_idx - kv_idx < 1024) & (q_idx >= kv_idx)

mask = create_block_mask(swa_pattern, B=batch, H=heads, Q_LEN=n, KV_LEN=n)
out = flex_attention(q, k, v, block_mask=mask)
```

#### Açıklama
Bu, özel bir Triton çekirdeğine derlenir. Yaygın paternler için FlashAttention-3 hızının %10'u içinde ve maske fonksiyonu bir Python çağrılabiliridir.

**Her biri ne zaman seçilir:**

- **Saf tam dikkat** — ~16K bağlamaya kadar her katman, veya getirme kalitesinin önemli olduğu yerde.
- **SWA + küresel karışım** — uzun bağlam (>32K), eğitim ve çıkarım bellek-sınırlı. 32K üstünde 2026 varsayılanı.
- **Seyreltik blok dikkati** — özel çekirdek, özel patern. Özel iş yükleri için ayrılmış (getirme, ses).
- **Farklılaştırılmış dikkat** — dikkat-çukuru kirliliğinin zarar verdiği her iş yükü (uzun-bağlam RAG, iğne-ot-balya).

## Teslim Et

`outputs/skill-attention-variant-picker.md`'ye bakın. Bu beceri, hedef bağlam uzunluğu, getirme talepleri ve eğitim/çıkarma hesaplama profili verildiğinde yeni bir model için dikkat topolojisini seçer.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. `pencere=4`'de SWA'nın her satırda son 4 token dışındaki her şeyi sıfırladığını doğrulayın. `pencere=n`'in tam nedensel dikkati bit-birebir yeniden ürettiğini doğrulayın.
2. **Orta.** Ders 07 bitirme projesi üzerine `pencere=1024` ile nedensel SWA uygulayın. tinyshakespeare üzerinde 1.000 adım eğitin. Doğrulama kaybı tam dikkate kıyasla ne kadar regres olur? Tepe bellek ne kadar düşer?
3. **Zor.** Gemma-3 tarzı 5:1 katman karışımını (5 SWA, 1 global) bitirme projesi modeline uygulayın. Kaybı, belleği ve üretim kalitesini saf-SWA ve saf-küresel temel çizgileriyle karşılaştırın.
4. **Zor.** Baş başına öğrenilmiş `λ` ile farklılaştırılmış dikkat uygulayın. Sentetik bir getirme görevi üzerinde eğitin (bir iğne, 2.000 dikkat dağıtıcı). Eşleşen parametrelerde tek-dikkat temel çizgisine kıyasla getirme doğruluğunu ölçün.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Kayan pencere dikkati (SWA) | "Yerel dikkat" | Her sorgu son `W` token'ına dikkat eder; KV-çerez `O(W)`'ye düşer. |
| Ekin reseptif alan | "Model ne kadar geriye görüyor" | Pencere `W` olan `L` katmanlı SWA yığınında, `L × W` token'a kadar. |
| Longformer / BigBird | "Yerel + küresel + rastgele" | Her zaman dikkat eden birkaç global token'la seyreltik paternler; erken uzun-bağlam yaklaşımı. |
| Yerli Seyreltik Dikkat | "DeepSeek'in çekirdek numarası" | Blok-düzeyi seyreltiklik öğrenme; kaliteyi koruyarak çekirdek düzeyinde sıfır blokları atlama. |
| Farklılaştırılmış dikkat | "İki harita, biri çıkarıyor" | DIFF Transformer: dikkat çukurlarını iptal etmek için birinci dikkat haritasından öğrenilmiş `λ` katlı ikinci haritayı çıkarın. |
| Dikkat çukuru (Attention sink) | "Ağırlık 0. token'a sızıyor" | Softmask normalleştirmesi satırları 1'e toplamaya zorlar; bilgilendirici olmayan sorgular ağırlığı 0. konuma boşaltır. |
| FlexAttention | "Maske-olarak-Python" | PyTorch 2.5+ API'si, rastgele maske fonksiyonlarını FlashAttention-şekilli çekirdeklere derler. |
| Katman türü karışımı | "5:1 SWA-küresel" | Daha düşük bellekte kaliteyi korumak için yığında seyreltik ve tam dikkat katmanlarını harmanlayın. |

## İleri Okuma

- [Beltagy, Peters, Cohan (2020). Longformer: The Long-Document Transformer](https://arxiv.org/abs/2004.05150) — kanonik kayan-pencere + global-token makalesi.
- [Zaheer ve diğerleri (2020). Big Bird: Transformers for Longer Sequences](https://arxiv.org/abs/2007.14062) — yerel + küresel + rastgele.
- [Child ve diğerleri (2019). Generating Long Sequences with Sparse Transformers](https://arxiv.org/abs/1904.10509) — OpenAI'nin yerel+adım-adımlı paterni.
- [Gemma Team (2024). Gemma 2: Improving Open Language Models at a Practical Size](https://arxiv.org/abs/2408.00118) — 1:1 SWA:küresel karışımı.
- [Gemma Team (2025). Gemma 3 technical report](https://arxiv.org/abs/2503.19786) — pencere=1024 ile 5:1 karışımı, artık ders kitabısı varsayılan.
- [Ye ve diğerleri (2024). Differential Transformer](https://arxiv.org/abs/2410.05258) — DIFF Transformer makalesi.
- [Yuan ve diğerleri (2025). Native Sparse Attention](https://arxiv.org/abs/2502.11089) — DeepSeek-V3.2'nin öğrenilmiş-seyreltik dikkati.
- [PyTorch — FlexAttention blog ve dokümanları](https://pytorch.org/blog/flexattention/) — Kullan'da maske-çağrılabilir paterni için API referansı.
