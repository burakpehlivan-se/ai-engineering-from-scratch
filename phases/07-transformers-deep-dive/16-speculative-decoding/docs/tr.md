# Spekülatif Çözümleme — Taslak, Doğrula, Tekrarla

> Otonom çözümleme seridir. Her token bir öncekini bekler. Spekülatif çözümlemeye zinciri kırar: ucuz bir model N token taslağı çizer, pahalı model tüm N'i tek bir ileriye doğru geçişte doğrular. Taslak doğruysa, N üretim için bir büyük ileriye doğru geçiş ödemiş olursunuz.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 07 (GPT Nedensel LM), Faz 7 · 12 (KV-Çerez ve Flash Attention)
**Süre:** ~60 dakika

## Sorun

70B LLM, H100'de bir token örnekleme için ~30 ms alır. 3B taslak model ~3 ms alır. 3B modelin 5 token ileri taslak çizmesine izin verip ardından tüm 5'i doğrulamak için 70B'yi *bir kez* çalıştırırsanız, toplam kabul edilen 5 token için `5×3 + 30 = 45 ms` olur — doğrudan üretime kıyasla `5×30 = 150 ms`. Bu spekülatif çözümlemenin tam satış konuşmasıdır: küçük bir ekstra VRAM (taslak model) için 2–4× daha düşük çözümleme gecikmesi takası.

Numara dağılımı korumalıdır. Leviathan ve diğerleri (2023) ve aynı anda Chen ve diğerleri tarafından tanıtılan spekülatif örnekleme (speculative sampling), çıktı dizisinin büyük modelin tek başına üreteceğiyle **aynı dağılımda** olduğunu garanti eder. Kalite takası yok. Sadece daha hızlı.

2026 çıkarımında dört taslak-doğrulayıcı çifti ailesi baskındır:

1. **Vanilya spekülatif (Leviathan 2023).** Ayrı taslak model (ör. Llama 3 1B) + doğrulayıcı (ör. Llama 3 70B).
2. **Medusa (Cai 2024).** Doğrulayıcı üzerindeki birden fazla çözümleme başı `t+1..t+k` konumlarını paralel olarak tahmin eder. Ayrı taslak model yok.
3. **EAGLE ailesi (Li 2024, 2025).** Doğrulayıcının gizli durumlarını yeniden kullanan hafif taslak; vanilya'dan daha yüksek kabul oranı; tipik 3–4×.
4. **İleriye bakışlı çözümleme (Lookahead decoding)** (Fu 2024). Jacobi yinelemesi; taslak model gerekmez. Kendi-kendine speküle etme. Niş ama bağımsız.

2026'da her üretim çıkarım yığını varsayılan olarak spekülatif çözümleme gönderir. vLLM, TensorRT-LLM, SGLang ve llama.cpp en azından vanilya + EAGLE-2'yi destekler.

## Kavram

### Çekirdek algoritma

Bir doğrulayıcı `M_q` ve daha ucuz bir taslak `M_p` verildiğinde:

1. `x_1..x_k` önceden çözümlenmiş önek olsun.
2. **Taslak:** `M_p`'yi kullanarak `d_{k+1}, d_{k+2}, ..., d_{k+N}` önerilerini taslak olasılıkları `p_1..p_N` ile otonom olarak çizin.
3. **Paralel olarak doğrula:** `M_q`'yi `x_1..x_k, d_{k+1}, ..., d_{k+N}` üzerinde bir kez çalıştırın, `k+1..k+N+1` konumları için doğrulayıcı olasılıkları `q_1..q_{k+N+1}`'i alın.
4. **Her taslak token'ını soldan sağa kabul/red et:** her `i` için, `min(1, q_i(d_i) / p_i(d_i))` olasılığıyla kabul edin.
5. `j` konumunda ilk reddedişte: "artık" dağılımından `(q_j - p_j)_+` normalize edilmiş `t_j` örnekle. `j`'den sonraki tüm taslaklar atılır.
6. Tüm `N` kabul edildiğinde: `q_{N+1}`'den (ücretsiz bonus token) bir token daha örnekle.

Artık dağılım numarası, çıktının `M_q` tek başına örneklemiş gibi tam olarak aynı dağılımda olmasını sağlayan matematiksel içgörüdür.

### Hızlanmayı belirleyen şey

`α` = taslak token başına beklenen kabul oranı olsun. `c` = taslak/doğrulayıcı maliyet oranı olsun. Adım başına:

- Naif üretim, token başına 1 büyük model çağrısı yapar.
- Spekülatif, `α` yüksek olduğunda `(1 - α^{N+1}) / (1 - α) ≈ 1/(1-α)` token için 1 büyük model çağrısı yapar.

Tipik kural `α = 0,75` ve `N = 5`'de: 3× daha az büyük model çağrısı. Taslak maliyeti 5× ucuz. Toplam gerçek zaman ~2,5× düşer.

**α şunlara bağlıdır:**

- Taslağın doğrulayıcıyı ne kadar iyi yaklaştığı. Aynı aile / aynı eğitim verisi α'yı önemli ölçüde artırır.
- Çözümleme stratejisi. Naif taslak vs naif doğrulayıcı: yüksek α. Sıcaklık örnelemesi: eşleştirmek daha zor; kabul düşer.
- Görev türü. Kod ve yapılandırılmış çıktı daha fazla kabul eder (tahmin edilebilir); serbest yaratıcı yazma daha az kabul eder.

### Medusa — taslak modelsiz taslaklar

Medusa, taslak modelini doğrulayıcı üzerindeki ekstra çıktı başlarıyla değiştirir. `t` konumunda:

```
shared trunk → hidden h_t
    ├── head_0: predict token at t+1  (standard LM head)
    ├── head_1: predict token at t+2
    ├── head_2: predict token at t+3
    ├── head_3: predict token at t+4
```

#### Açıklama
Her baş kendi logit'lerini üretir. Çıkarımda her baştan örnekleme yaparak bir aday dizi elde edersiniz, sonra bir ağaç-dikkat şeması kullanarak tüm aday devamları aynı anda göz önüne alarak tek bir ileriye doğru geçişle doğrulama yaparsınız.

Artıları: ikinci model yok. Eksileri: eğitilebilir parametre ekler; denetimli bir inceltme aşaması gerektirir (~1B token); iyi bir taslakla vanilya spekülatiften biraz daha düşük kabul oranı.

### EAGLE — gizli durumları yeniden kullanarak daha iyi taslak

EAGLE-1/2/3 (Li ve diğerleri, 2024–2025), taslak modelini doğrulayıcının son katman gizli durumlarını alan küçük bir transformer (tipik 1 katman) yapar. Taslak, doğrulayıcının özellik temsilini gördüğünden, tahminleri doğrulayıcı dağılımıyla güçlü bir şekilde korele olur. Kabul oranları ~0,6'dan (vanilya) 0,85+'e tırmanır.

EAGLE-3 (2025) aday devamlar üzerinde ağaç araması ekledi. vLLM ve SGLang, Llama 3/4 ve Qwen 3 için varsayılan spekülatif yol olarak EAGLE-2/3'ü gönderir.

### KV-çerez dansı

Doğrulama, `N` taslak token'ı tek bir ileriye doğru geçişte doğrulayıcıya besler. Bu, doğrulayıcının KV-çerezini `N` giriş uzatır. Bazı taslaklar reddedilirse, çerezi kabul edilmiş önek uzunluğuna geri sarmanız gerekir.

Üretim uygulamaları (vLLM'in `--speculative-model`, TensorRT-LLM'in LookaheadDecoder) bunu scratch (kılavuz) KV arabellekleriyle işler. Önce yaz, kabulde işaretle. Kavramsal olarak zor değil, ancak detaycılıklıdır.

## İnşa Et

`code/main.py`'ye bakın. Çekirdek spekülatif-örnekleme algoritmasını (ret adımı + artık dağılım) şunlarla uyguluyoruz:

- Üzerinde el-kodlanmış bir dağılım üzerinde deterministik-softmax olan bir "büyük model" (kabul matematiğini analitik olarak doğrulayabilmemiz için).
- Büyük modelin bir bozulması olan bir "taslak model".
- Doğrudan örneklemeyle aynı marjinal dağılımı üreten bir kabul/red döngüsü.

### Adım 1: ret adımı

```python
def accept_or_reject(q_prob, p_prob, draft_token, u):
    ratio = q_prob / p_prob if p_prob > 0 else float("inf")
    return u < min(1.0, ratio)
```

#### Açıklama
`u` düzgün dağılımlı bir rastgele sayıdır. `q_prob`, taslak token için doğrulayıcının olasılığıdır. `p_prob`, taslak modelin olasılığıdır. Leviathan teoremi, bu Bernoulli kararının ve ret durumunda artık dağılımdan örnekleme işleminin doğrulayıcı dağılımını tam olarak koruduğudur.

### Adım 2: artık dağılım

```python
def residual_dist(q, p):
    raw = [max(0.0, qi - pi) for qi, pi in zip(q, p)]
    s = sum(raw)
    return [r / s for r in raw]
```

#### Açıklama
`p`'yi `q`'dan eleman bazında çıkarın, negatif değerleri sıfıra bağlayın ve yeniden normalleştirin. Herhangi bir ret durumundan bunun örneklemesi, doğrulayıcı dağılımını korur.

### Adım 3: bir spekülatif adım

```python
def spec_step(prefix, q_model, p_model, N, rng):
    drafts = []
    p_probs = []
    ctx = list(prefix)
    for _ in range(N):
        p_dist = p_model(ctx)
        d = sample(p_dist, rng)
        drafts.append(d)
        p_probs.append(p_dist[d])
        ctx.append(d)

    q_dists = [q_model(prefix + drafts[:i]) for i in range(N + 1)]

    for i, d in enumerate(drafts):
        u = rng.random()
        q_prob = q_dists[i][d]
        p_prob = p_probs[i]
        if u < min(1.0, q_prob / p_prob if p_prob > 0 else float("inf")):
            prefix = prefix + [d]
        else:
            res = residual_dist(q_dists[i], p_model(prefix))
            prefix = prefix + [sample(res, rng)]
            return prefix
    prefix = prefix + [sample(q_dists[N], rng)]
    return prefix
```

#### Açıklama
Beş kabul → bir bonus → bir doğrulayıcı geçişinde altı token üretildi.

### Adım 4: kabul oranını ölçün

Farklı taslak-kalite seviyelerinde 10.000 spekülatif adım çalıştırın. Kabul oranını taslak ve doğrulayıcı dağılımları arasındaki KL sapmasına (KL divergence) göre çizin. Temiz bir monoton ilişki görmelisiniz.

### Adım 5: dağılım eşdeğerliğini doğrulayın

Deneysel olarak: spekülatif döngü tarafından üretilen token histogramı, doğrulayıcıdan doğrudan örneklemeyle üretilen histogramla eşleşmelidir. Bu pratikteki Leviathan teoremidir. Ki-kare testi, örnekleme hatası içinde doğrular.

## Kullan

Üretim:

```bash
# vLLM with EAGLE
vllm serve meta-llama/Llama-3.1-70B-Instruct \
    --speculative-model /models/llama-3.1-eagle-70b \
    --speculative-draft-tensor-parallel-size 1 \
    --num-speculative-tokens 5

# vLLM with vanilla draft model
vllm serve meta-llama/Llama-3.1-70B-Instruct \
    --speculative-model meta-llama/Llama-3.2-1B-Instruct \
    --num-speculative-tokens 5
```

#### Açıklama
TensorRT-LLM, 2026 ortası itibarıyla en hızlı Medusa yoluna sahiptir. `faster-whisper`, Whisper-large için küçük bir taslakla spekülatif çözümlemeyi sarar.

**Taslak seçimi:**

| Strateji | Ne zaman seçilir | Hızlanma |
|----------|--------------|---------|
| Vanilya taslak (1B/3B Llama ailesi) | Hızlı prototip, eğitim yok | 1,8–2,3× |
| Medusa başları | Doğrulayıcıyı inceltebilirsiniz | 2–3× |
| EAGLE-2 / 3 | Üretim, maks hız | 3–4× |
| İleriye bakışlı | Taslak yok, eğitim yok, ekstra parametre yok | 1,3–1,6× |

**Spekülatif çözümleme NE ZAMAN kullanılmaz:**

- 1–5 token dizisi üretimi. Overhead domine eder.
- Çılgınca yaratıcı / yüksek sıcaklık örnelemesi (α düşer).
- Bellek-kısıtlı dağıtımlar (taslak model VRAM ekler).

## Teslim Et

`outputs/skill-spec-decode-picker.md`'ye bakın. Bu beceri, yeni bir çıkarım iş yükü için bir spekülatif çözümleme stratejisi (vanilya / Medusa / EAGLE / ileriye bakışlı) ve ayarlama parametreleri (N, sıcaklık) seçer.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Spekülatif token dağılımının, 50.000 token üzerinde ki-kare p > 0,05 içinde doğrulayıcının doğrudan-örnekleme dağılımıyla eşleştiğini doğrulayın.
2. **Orta.** Hızlanmayı (büyük model ileriye doğru geçişi başına token) `α = 0,5, 0,7, 0,85` için `N`'nin fonksiyonu olarak çizin. Her α için optimum `N`'yi belirleyin. (İpucu: doğrulama çağrısı başına beklenen token = `(1 - α^{N+1}) / (1 - α)`.)
3. **Zor.** Küçük bir Medusa uygulayın: Ders 14'ten bitirme projesi GPT'sini alın, t+2, t+3, t+4 konumlarını tahmin eden 3 ekstra LM kafası ekleyin. Birleşik çoklu-baş kaybıyla tinyshakespeare üzerinde eğitin. Kabul oranlarını aynı modelin kesilmesiyle yapılan vanilya taslakla karşılaştırın.
4. **Zor.** Geri sarımı (rollback) uygulayın: 10 token'lık önek KV-çerezi ile başlayın, 5 taslak token besleyin, 3. konumda bir ret simüle edin. Çerezinizin bir sonraki yinelemede "önek + ilk 2 kabul edilmiş taslak" ile doğru eşleştiğini doğrulayın.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Taslak model | "Ucuz olan" | Öneri aday token'ları sunan daha küçük model; genellikle doğrulayıcıdan 10–50× ucuz. |
| Doğrulayıcı | "Büyük olan" | Dağılımını koruduğumuz hedef model; spekülatif adım başına bir kez çalışır. |
| Kabul oranı (α) | "Taslak ne sıklıkla doğru" | Token-başına doğrulayıcının taslağı kabul etme olasılığı. Tipik 0,7–0,9. |
| Artık dağılım (Residual distribution) | "Red fallback'i" | Normalize `(q - p)_+`; ret durumunda örnekleme, doğrulayıcı dağılımını korur. |
| Bonus token | "Ücretsiz olan" | Tüm N taslak kabul edildiğinde, doğrulayıcının bir sonraki adım dağılımından bir token daha örnekle. |
| Medusa | "Taslaksız spekülatif" | Doğrulayıcı üzerindeki birden fazla LM başı t+1..t+k konumlarını paralel tahmin eder. |
| EAGLE | "Gizli durumlu taslak" | Doğrulayıcının son katman gizli durumlarına koşullu küçük transformer taslağı. |
| İleriye bakışlı çözümleme | "Jacobi yinelemesi" | Sabit-nokta yinelemesiyle kendi-kendine speküle etme; taslak model yok. |
| Ağaç-dikkati | "Birçok adayı aynı anda doğrula" | Birkaç taslak devamını aynı anda göz önüne alan dallanmalı doğrulama. |
| KV geri sarımı | "Reddedilen taslakları geri al" | Scratch KV arabelleği; kabulde işaretle, reddette at. |

## İleri Okuma

- [Leviathan, Kalman, Matias (2023). Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192) — çekirdek algoritma ve eşdeğerlik teoremi.
- [Chen ve diğerleri (2023). Accelerating Large Language Model Decoding with Speculative Sampling](https://arxiv.org/abs/2302.01318) — eş zamanlı tanıtım; temiz Bernoulli-reddetme kanıtı.
- [Cai ve diğerleri (2024). Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads](https://arxiv.org/abs/2401.10774) — Medusa makalesi; ağaç-dikkat doğrulaması.
- [Li ve diğerleri (2024). EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty](https://arxiv.org/abs/2401.15077) — EAGLE-1; gizli-durum-koşullu taslak.
- [Li ve diğerleri (2024). EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees](https://arxiv.org/abs/2406.16858) — EAGLE-2; dinamik ağaç derinliği.
- [Li ve diğerleri (2025). EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test](https://arxiv.org/abs/2503.01840) — EAGLE-3.
- [Fu ve diğerleri (2024). Break the Sequential Dependency of LLM Inference Using Lookahead Decoding](https://arxiv.org/abs/2402.02057) — ileriye bakışlı, taslak-olmayan yaklaşım.
- [vLLM docs — Spekülatif Çözümleme](https://docs.vllm.ai/en/latest/features/spec_decode.html) — dört stratejinin de bağlandığı kanonik üretim referansı.
- [SafeAILab / EAGLE referans uygulaması](https://github.com/SafeAILab/EAGLE) — EAGLE-1/2/3 için referans kodu.
