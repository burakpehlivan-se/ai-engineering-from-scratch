# KV-Çerez, Flash Attention ve Çıkarım Optimizasyonu

> Eğitim paraleldir ve FLOP-sınırlıdır. Çıkarım seridir ve bellek-sınırlıdır. Farklı darboğaz, farklı numaralar.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 02 (Self-Attention), Faz 7 · 05 (Tam Transformer), Faz 7 · 07 (GPT)
**Süre:** ~75 dakika

## Sorun

Naif bir otonom decoder, N token üretmek için `O(N²)` iş yapar: her adımda tüm önek (prefix) üzerinde dikkati yeniden hesaplar. 4K token'lık bir yanıt için bu 16M dikkat işlemidir, bunların çoğu gereksizdir. Bir önek token'ının her gizli durumu (hidden state) bir kez hesaplandığında belirlidir — yalnızca yeni token'ın sorgusunu önbellekteki anahtarların ve değerlerin her şeyine karşı çalıştırmanız gerekir.

Bunun üzerine, dikkat kendisi çok fazla veri taşır. Standart dikkat N×N puan matrisi, N×d softmax çıktısı, N×d son çıktıyı somutlaştırır — HBM'e çok fazla okuma ve yazma. N≥2K için dikkat, FLOP-sınırlı olmadan önce bellek-sınırlı hale gelir. Klasik dikkat çekirdekleri modern GPU'ları 4–10× yetersiz kullanır.

Dao ve diğerlerinden iki optimizasyon, sınır çıkarımını "yavaş"dan "hızlı"ya itti:

1. **KV-çerez (KV cache).** Her önek token'ının K ve V vektörlerini saklayın. Her yeni token'ın dikkati, önbellekteki anahtarlara karşı tek bir sorgudur. Çıkarım üretim adımında `O(N²)`'den `O(N)`'e düşer.
2. **Flash Attention.** Dikkat hesaplamasını kiremit (tile) boyutunda bölün ki tam N×N matris HBM'e hiç düşmesin. Tüm softmax + matmul SRAM'de gerçekleşir. A100'de 2–4× gerçek zaman hızlanması; FP8 ile H100'de 5–10×.

2026'ya kadar her ikisi de evrenseldir. Her üretim çıkarım yığını (vLLM, TensorRT-LLM, SGLang, llama.cpp) bunları varsayar. Her sınır modeli Flash Attention etkin olarak gönderilir.

## Kavram

![KV-çerez büyümesi ve Flash Attention kiremitleri](../assets/kv-cache-flash-attn.svg)

### KV-çerez matematiği

Decoder katmanı başına, token başına, baş başına:

```
bytes_per_token_per_layer = 2 * d_head * dtype_size
                          ^
                          K and V
```

32 katmanlı, 32 başlı, d_head=128, fp16 olan 7B model için:

```
per token per layer = 2 * 128 * 2 = 512 bytes
per token (32 layers) = 16 KB
per 32K context = 512 MB
```

Llama 3 70B için (80 katman, d_head=128, 8 KV başı ile GQA):

```
per token per layer = 2 * 8 * 128 * 2 = 4096 bytes (4 KB)
per 32K context = 10.4 GB
```

#### Açıklama
Bu 10 GB, Llama 3 70B'nin 128K bağlamda toplu boyutu 1'de KV-çerez için 40 GB A100'ün çoğunu kullanmasının nedenidir.

**GQA, KV-çerez kazancıdır.** 64 başlı MHA 32 GB olurdu. MLA daha da sıkıştırır.

### Flash Attention — kiremit numarası

Standart dikkat:

```
S = Q @ K^T          (HBM okuma, N×N, HBM yazma)
P = softmax(S)       (HBM okuma, HBM yazma)
O = P @ V            (HBM okuma, HBM yazma)
```

Üç HBM turu. H100'de HBM bant genişliği 3 TB/s'dir; SRAM 30 TB/s'dir. Her HBM yolculuğu, her şeyi çipte tutmaya kıyasla 10 kat yavaşlamadır.

Flash Attention:

```
for each block of Q (tile size ~128 × 128):
    load Q_tile into SRAM
    for each block of K, V:
        load K_tile, V_tile into SRAM
        compute S_tile = Q_tile @ K_tile^T     (SRAM)
        running softmax aggregation             (SRAM)
        accumulate into O_tile                  (SRAM)
    write O_tile to HBM
```

#### Açıklama
Her kiremit için bir HBM turu. Toplam bellek ayak izi `O(N²)`'den `O(N)`'e düşer. Geriye doğru geçiş, bazı değerleri saklamak yerine ileriye doğru geçişten yeniden hesaplar — bir bellek daha kazancı.

**Sayısal numara.** Çalışan softmax, kiremitler boyunca `(max, sum)` koruyarak son normalleştirmeyi tam yapar. Yaklaşım değil — Flash Attention, standart dikkatle (fp16-assosiatifliği modülü) bit-birebir aynı çıktıyı hesaplar.

**Sürüm evrimi:**

| Sürüm | Yıl | Ana değişiklik | Referans donanımda hızlanma |
|---------|------|-----------|-------------------------------|
| Flash 1 | 2022 | Kiremitli SRAM çekirdeği | A100'de 2× |
| Flash 2 | 2023 | Daha iyi paralellik, nedensel-öncelikli sıralama | A100'de 3× |
| Flash 3 | 2024 | Hopper asenkronluğu, FP8 | H100'de 1,5–2× (~740 TFLOPs FP16) |
| Flash 4 | 2026 | Blackwell 5 aşamalı boru hattı, yazılımsal exp2 | Çıkarım-öncelikli (başlangıçta sadece ileriye doğru) |

Flash 4, başlatıldığında yalnızca ileriye doğru geçiştir. Eğitim hala Flash 3 kullanır. Flash 4 için GQA ve varlen desteği beklemededir (2026 ortası).

### Spekülatif çözümleme — diğer gecikme kazancı

Ucuz model N token önerir. Büyük model tüm N'i paralel olarak doğrular. Doğrulama k token kabul ederse, k üretim için 1 büyük model ileriye doğru geçişi ödemiş olursunuz. Kod ve düz metinde tipik k=3–5.

2026 varsayımları:
- **EAGLE 2 / Medusa.** Doğrulayıcının gizli durumlarını paylaşan entegre taslak başları. Kalite kaybı olmadan 2–3× hızlanma.
- **Taslak model ile spekülatif çözümleme.** Tüketici donanımında 2–4× hızlanma.
- **İleriye bakışlı çözümleme (Lookahead decoding).** Jacobi yinelemesi; taslak model gerekmez. Niş ama ücretsiz.

### Sürekli toplu işleme (Continuous batching)

Klasik toplu çıkarım: en yavaş dizinin bitmesini bekleyin, sonra yeni bir toplu başlatın. Kısa yanıtlar erken bittiğinde GPU israf eder.

Sürekli toplu işleme (ilk olarak Orca'da, şimdi vLLM, TensorRT-LLM, SGLang'da): eskileri biter bitmez yeni istekleri topluya sokun. Tipik sohbet iş yükleri için 5–10× verimlilik artışı.

### PagedAttention — KV-çerez sanal bellek olarak

vLLM'in başlık özelliği. KV-çerez 16 token'lık bloklar halinde ayrılmıştır; bir sayfa tablosu (page table) mantıksal konumları fiziksel bloklara eşler. Paralel örnekler (ışın araması, paralel örnekleme) arasında KV paylaşımına, istem önbellekleme için sıcak-değişim öneklerine ve bellek parçalanmasını gidermeye olanak tanır. Naif bitişik ayırma (contiguous allocation) üzerinde 4× verimlilik artışı.

## İnşa Et

`code/main.py`'ye bakın. Şunları uyguluyoruz:

1. Naif `O(N²)` artımlı decoder.
2. `O(N)` KV-çerezli decoder.
3. Flash Attention'ın çalışan-maksimum algoritmasını taklit eden kiremitli softmax.

### Adım 1: KV-çerez

```python
class KVCache:
    def __init__(self, n_layers, n_heads, d_head):
        self.K = [[[] for _ in range(n_heads)] for _ in range(n_layers)]
        self.V = [[[] for _ in range(n_heads)] for _ in range(n_layers)]

    def append(self, layer, head, k, v):
        self.K[layer][head].append(k)
        self.V[layer][head].append(v)

    def read(self, layer, head):
        return self.K[layer][head], self.V[layer][head]
```

#### Açıklama
Basit: katman-başına, baş-başına listelerde token-başına K, V vektörlerini büyütün.

### Adım 2: kiremitli softmax

```python
def tiled_softmax_dot(q, K, V, tile=4):
    """Flash-attention-style softmax(qK^T)V with running max/sum."""
    m = float("-inf")
    s = 0.0
    out = [0.0] * len(V[0])
    for start in range(0, len(K), tile):
        k_block = K[start:start + tile]
        v_block = V[start:start + tile]
        scores = [sum(qi * ki for qi, ki in zip(q, k)) for k in k_block]
        new_m = max(m, *scores)
        exp_old = math.exp(m - new_m) if m != float("-inf") else 0.0
        exp_new = [math.exp(sc - new_m) for sc in scores]
        s = s * exp_old + sum(exp_new)
        for j in range(len(out)):
            out[j] = out[j] * exp_old + sum(e * v[j] for e, v in zip(exp_new, v_block))
        m = new_m
    return [o / s for o in out]
```

#### Açıklama
Tek geçişte `softmax(qK) V` ile bit-birebir aynı çıktı, ancak herhangi bir anda çalışma seti tam `N × d_head` yerine `tile × d_head` bloğudur.

### Adım 3: naif vs çerezli çözümlemeyi 100 token üretiminde karşılaştırın

Dikkat işlemlerini sayın. Naif: `O(N²)` = 5050. Çerezli: `O(N)` = 100. Kod her ikisini yazdırır.

## Kullan

```python
# HuggingFace transformers, decoder-only generate()'da KV-çerezi otomatik etkinleştirir.
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B",
    attn_implementation="flash_attention_2",  # use FA3 if Hopper
    torch_dtype="bfloat16",
)
# generate() KV-çerezi otomatik kullanır
```

vLLM üretimi:

```bash
pip install vllm
vllm serve meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 4 \
    --max-model-len 32768 \
    --enable-prefix-caching \
    --kv-cache-dtype fp8
```

#### Açıklama
İstekler arası ön ek önbellekleme, 2026'da büyük bir kazançtır — aynı sistem istemi, birkaç-atımlık örnekler veya uzun bağlam belgesi, çağrılar arasında KV'yi yeniden kullanır. Tekrarlanan araç istemleriyle ajan iş yükleri için ön ek önbellekleme, rutin olarak 5× verimlilik artışı sağlar.

## Teslim Et

`outputs/skill-inference-optimizer.md`'ye bakın. Bu beceri, yeni bir çıkarım dağıtımı için dikkat uygulaması, KV-çerez stratejisi, nicemleme ve spekülatif çözümleme seçer.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Naif ve çerezli decoder'ların aynı çıktıyı ürettiğini doğrulayın; işlem sayısındaki farkı not edin.
2. **Orta.** Ön ek önbellekleme uygulayın: bir istem P ve birkaç tamamlama verildiğinde, P üzerinde tek bir ileriye doğru geçiş çalıştırarak KV-çerezi doldurun, sonra tamamlama başına dallanın. Her biri için P'yi yeniden kodlamaya kıyasla hızlanmayı ölçün.
3. **Zor.** Küçük bir PagedAttention uygulayın: sabit 16 token'lık bloklarda KV-çerez, serbest-liste (free-list) ile. Bir dizi bittiğinde bloklarını havuza iade edin. Değişken uzunluklarda 1.000 sohbet tamamlamasını simüle edin. Bellek parçalanmasını bitişik ayırma ile karşılaştırın.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| KV-çerez | "Çözümlemeyi hızlı yapan numara" | Her önek token'ından saklanan K ve V; yeni sorgular onlara yeniden hesaplamak yerine dikkat eder. |
| HBM | "GPU ana belleği" | Yüksek Bant Genişliği Belleği; H100'de 80 GB, B200'de 192 GB. ~3 TB/s bant genişliği. |
| SRAM | "Çip-içi bellek" | SM başına hızlı bellek, H100'de SM başına ~256 KB. ~30 TB/s bant genişliği. |
| Flash Attention | "Kiremitli dikkat çekirdeği" | N×N'yi HBM'de somutlaştırmadan dikkat hesaplar. |
| Sürekli toplu işleme | "Bekleme yok toplu işleme" | Bitmiş dizileri dışarı, yeni dizileri içeri, topluyu boşaltmadan değiştirin. |
| PagedAttention | "vLLM'in başlığı" | KV-çerez sabit bloklarda sayfa tablosuyla ayrılmıştır; parçalanmayı ortadan kaldırır. |
| Ön ek önbellekleme | "Uzun istemleri yeniden kullan" | İstekler arasında paylaşılan bir ön ek için KV'yi önbelleğe al; ajanlar için büyük maliyet düşüşü. |
| Spekülatif çözümleme | "Taslak + doğrulama" | Ucuz taslak model token önerir; büyük model k'yi tek geçişte doğrular. |

## İleri Okuma

- [Dao ve diğerleri (2022). FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135) — Flash 1.
- [Dao (2023). FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning](https://arxiv.org/abs/2307.08691) — Flash 2.
- [Shah ve diğerleri (2024). FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision](https://arxiv.org/abs/2407.08608) — Flash 3.
- [FlashAttention-4 sürüm notları (Dao-AILab, 2026)](https://github.com/Dao-AILab/flash-attention) — Blackwell 5 aşamalı boru hattı ve yazılımsal-exp2 numarası; bu dersin bahsettiği yalnızca-ileriye-doğru başlatma uyarılarını görmek için depo README'sini okuyun.
- [Kwon ve diğerleri (2023). Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180) — vLLM makalesi.
- [Leviathan ve diğerleri (2023). Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192) — spekülatif çözümleme.
- [Li ve diğerleri (2024). EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty](https://arxiv.org/abs/2401.15077) — bu derin bahsettiği entegre-taslak yaklaşımı için EAGLE-1/2 makalesi.
- [Cai ve diğerleri (2024). Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads](https://arxiv.org/abs/2401.10774) — EAGLE ile birlikte atıfta bulunulan Medusa yaklaşımı.
- [vLLM docs — PagedAttention](https://docs.vllm.ai/en/latest/design/kernel/paged_attention.html) — 16 token'lık blok ve sayfa tablosu tasarımı hakkında kanonik derin dalış.
