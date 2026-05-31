# Uzmanların Karışımı (Mixture of Experts / MoE)

> Yoğun (dense) 70B transformer her token için her parametreyi etkinleştirir. 671B MoE, token başına yalnızca 37B'yi etkinleştirir ve her kıyaslama testinde onu geçer. seyreltiklik (sparsity), on yılın en önemli ölçekleme fikridir.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 05 (Tam Transformer), Faz 7 · 07 (GPT)
**Süre:** ~45 dakika

## Sorun

Yoğun bir transformer'ın çıkarım sırasındaki FLOP'ları parametre sayısına eşittir (ileriye doğru geçiş için 2 ile çarpılır). Yoğun bir modeli ölçeklendirirseniz her token tam faturayı öder. 2024'e kadar sınır (frontier) bir hesaplama duvarına çarpıyordu: anlamlı şekilde daha akıllı olmak için token başına katlanarak daha fazla FLOP gerekiyordu.

Uzmanların karışımı bu bağı kırar. Her FFN'i bağımsız `E` uzman + token başına `k` uzman seçen bir yönlendirici (router) ile değiştirin. Toplam parametre = `E × FFN_boyutu`. Token başına etkin parametre = `k × FFN_boyutu`. Tipik 2026 yapılandırması: `E=256`, `k=8`. Depolama `E` ile, hesaplama `k` ile ölçeklenir.

2026 sınırı neredeyse tamamen MoE'dir: DeepSeek-V3 (671B toplam / 37B etkin), Mixtral 8×22B, Qwen2.5-MoE, Llama 4, Kimi K2, gpt-oss. Artificial Analysis'ın bağımsız sıralama tablosunda, en iyi 10 açık kaynak modelin hepsi MoE'dir.

## Kavram

![MoE katmanı: yönlendirici token başına E uzmandan k'sını seçer](../assets/moe.svg)

### FFN değişimi

Yoğun transformer bloğu:

```
h = x + attn(norm(x))
h = h + FFN(norm(h))
```

MoE bloğu:

```
h = x + attn(norm(x))
scores = router(norm(h))              # (N_tokens, E)
top_k = argmax_k(scores)              # pick k of E per token
h = h + sum_{e in top_k}(
        gate(scores[e]) * Expert_e(norm(h))
    )
```

#### Açıklama
Her uzman bağımsız bir FFN'dir (genellikle SwiGLU). Yönlendirici tek bir doğrusal katmandır. Her token kendi `k` uzmanını seçer ve çıktılarının kapılı bir karışımını alır.

### Yük dengeleme sorunu

Yönlendirici token'ların %90'ını 3 numaralı uzmana yönlendirirse, diğer uzmanlar aç kalır. Üç düzeltme denendi:

1. **Yardımcı yük dengeleme kaybı (Auxiliary load-balancing loss)** (Switch Transformer, Mixtral). Uzman kullanımındaki varyansa orantlı bir ceza ekleyin. Çalışır, ancak bir hiperparametre ve ikinci bir gradyan sinyali ekler.
2. **Uzman kapasitesi + token bırakma (token dropping)** (erken Switch). Her uzman en fazla `C × N/E` token işler; taşan token katmanı atlar. Kaliteyi bozar.
3. **Yardımcı-kayıpsız dengeleme (Auxiliary-loss-free balancing)** (DeepSeek-V3). Yönlendiricinin üst-k seçimini kaydıran öğrenilmiş bir uzman-başına önyargı (bias) ekleyin. Önyargı, eğitim kaybının dışında güncellenir. Ana hedefe ceza yok. 2024'ün büyük kilidi.

DeepSeek-V3'ün yaklaşımı: her eğitim adımından sonra, her uzman için kullanımının hedefin üzerinde mi altında mı olduğunu kontrol edin. Önyargıyı `±γ` kadar kaydırın. Seçim `scores + bias` kullanır. Kapılandırma için kullanılan uzman olasılıkları, ham `scores` değişmez. Yönlendirmeyi ifadeden (expression) ayırır.

### Paylaşımlı uzmanlar

DeepSeek-V2/V3 uzmanları *paylaşımlı* ve *yönlendirilmiş* olarak böler. Her token tüm paylaşımlı uzmanlardan geçer. Yönlendirilmiş uzmanlar üst-k ile seçilir. Paylaşımlı uzmanlar ortak bilgiyi yakalar; yönlendirilmiş uzmanlar uzmanlaşır. V3, 256 yönlendirilmiş uzmandan 1 paylaşımlı uzman artı üst-8 çalıştırır.

### İnce taneli uzmanlar

Klasik MoE (GShard, Switch): her uzman tam bir FFN kadar geniştir. `E` küçüktür (8–64), `k` küçüktür (1–2).

Modern ince taneli MoE (DeepSeek-V3, Qwen-MoE): her uzman daha dardır (1/8 FFN boyutu). `E` büyüktür (256+), `k` daha büyüktür (8+). Toplam parametre aynı, ancak kombinasyonlar çok daha hızlı ölçeklenir. `C(256, 8) = 400 trilyon` olası "uzman" kombinasyonu. Kalite artar, gecikme düz kalır.

### Maliyet profili

Token başına, katman başına:

| Yapılandırma | Token başına etkin parametre | Toplam parametre |
|--------|-----------------------|--------------|
| Mixtral 8×22B | ~39B | 141B |
| Llama 3 70B (yoğun) | 70B | 70B |
| DeepSeek-V3 | 37B | 671B |
| Kimi K2 (MoE) | ~32B | 1T |

DeepSeek-V3, neredeyse her kıyaslama testinde Llama 3 70B'yi (yoğun) **token başına daha az etkin FLOP** yaparak geçer. Daha fazla parametre = daha fazla bilgi. Daha fazla etkin FLOP = token başına daha fazla hesaplama. MoE bunları birbirinden ayırır.

### Yakalama: bellek

Tüm uzmanlar hangilerinin ateşlendiğine bakılmaksızın GPU'da yaşar. 671B model için fp16 ağırlıklarda ~1.3 TB VRAM gerekir. Sınır MoE dağıtımı uzman-paralellik (expert parallelism) gerektirir — uzmanları GPU'lar arası paylaştırın, token'ları ağ üzerinden yönlendirin. Gecikme, all-to-all iletişim tarafından domine edilir, matmul tarafından değil.

## İnşa Et

`code/main.py`'ye bakın. Saf stdlib içinde_compact bir MoE katmanı:

- `n_experts=8` SwiGLU benzeri uzman (gösterim için herbirinde tek bir doğrusal)
- top-k=2 yönlendirme
- softmax-normalize edilmiş kapı ağırlıkları
- Uzman-başına önyargı ile yardımcı-kayıpsız dengeleme

### Adım 1: yönlendirici

```python
def route(hidden, W_router, top_k, bias):
    scores = [sum(h * w for h, w in zip(hidden, W_router[e])) for e in range(len(W_router))]
    biased = [s + b for s, b in zip(scores, bias)]
    top_idx = sorted(range(len(biased)), key=lambda i: -biased[i])[:top_k]
    # softmax over ORIGINAL scores of the chosen experts
    chosen = [scores[i] for i in top_idx]
    m = max(chosen)
    exps = [math.exp(c - m) for c in chosen]
    s = sum(exps)
    gates = [e / s for e in exps]
    return top_idx, gates
```

#### Açıklama
Önyargı seçimi etkiler, kapı ağırlığını değil. Bu DeepSeek-V3 numarasıdır — önyargı, yük dengesizliğini modelin tahminlerini yönlendirmeden düzeltir.

Bias seçimi etkiler, kapı ağırlığını değil. Bu DeepSeek-V3 numarasıdır — önyargı, yük dengesizliğini modelin tahminlerini yönlendirmeden düzeltir.

### Adım 2: yönlendiriciden 100 token çalıştırın

Hangi uzmanların ne sıklıkla ateşlendiğini izleyin. Önyargı olmadan kullanım eğridir. Bir güncelleme döngüsü ile (`-γ` aşırı kullanılan uzmanlar için, `+γ` az kullanılan için), kullanım birkaç yinelemede düzgün dağılıma yakınsar.

### Adım 3: parametre sayısı karşılaştırması

MoE yapılandırmasının "yoğun eşdeğerini" yazdırın. DeepSeek-V3 şeklinde: 256 yönlendirilmiş + 1 paylaşımlı, 8 etkin, d_model=7168. Toplam parametre sayısı göz yaşartıcı. Ekin sayısı yoğun Llama 3 70B'nin yedisi.

## Kullan

HuggingFace yükleme:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mixtral-8x22B-v0.1")
```

2026 üretim çıkarımı: vLLM MoE yönlendirmesini doğrudan destekler. SGLang en hızlı uzman-paralel yola sahiptir. Her ikisi de top-k seçimini ve uzman-paralelliğini otomatik olarak işler.

**MoE ne zaman seçilir:**
- Token başına daha düşük çıkarım maliyetiyle sınır kalitesi istiyorsunuz.
- VRAM / uzman-paralel altyapınız var.
- İş yükünüz token-ağır (sohbet, kod) bağlam-ağır değil (uzun belgeler).

**MoE NE ZAMAN SEÇİLMEZ:**
- Kenar dağıtımı — her etkin FLOP için tam depolama ödersiniz.
- Kritik gecikmeli tek kullanıcılı hizmet — uzman yönlendirmesi overhead ekler.
- Küçük modeller (<7B) — MoE kalite avantajı yalnızca bir hesaplama eşiğinin üzerinde görünür (~6B etkin parametre).

## Teslim Et

`outputs/skill-moe-configurator.md`'ye bakın. Bu beceri, parametre bütçesi, eğitim token'ları ve dağıtım hedefi verildiğinde yeni bir MoE için E, k ve paylaşımlı-uzman düzenini seçer.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Yardımcı-kayıpsız önyargı güncellemesinin 50 yinelemede uzman kullanımını nasıl düzleştirdiğini izleyin.
2. **Orta.** Öğrenilmiş yönlendiriciyi tabanlı (hash-based) bir yönlendiriciyle (belirli, öğrenme yok) değiştirin. Kalite ve dengeyi karşılaştırın. Öğrenilmiş yönlendirici neden daha iyidir?
3. **Zor.** DeepSeek-V3.2 numarası olan GRPO tarzı "yayınlama-eşleşmeli yönlendirmeyi" (rollout-matched routing) uygulayın: çıkarım sırasında hangi uzmanların ateşlendiğini kaydedin, gradyan hesaplaması sırasında aynı yönlendirmeyi zorlayın. Küçük bir politika-gradyan kurulumu üzerindeki etkiyi ölçün.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Uzman (Expert) | "Birçok FFN arasındaki biri" | Bağımsız bir besleme-öncü ağ; FFN hesaplamasının seyreltik bir dilimine adanmış parametreler. |
| Yönlendirici (Router) | "Kapı" | Her token'ı her uzmana puanlayan küçük bir doğrusal katman; üst-k seçimi. |
| Üst-k yönlendirmesi | "Token başına k etkin uzman" | Her token'ın FFN hesaplaması tam olarak k uzmandan geçer, kapı ile ağırlıklandırılır. |
| Yardımcı kayıp | "Yük dengeleme cezası" | Uzman kullanımındaki eğriliği cezalandıran ekstra kayıp terimi. |
| Yardımcı-kayıpsız | "DeepSeek-V3'ün numarası" | Yalnızca yönlendiricinin seçiminde uzman-başına önyargı ile dengeleme; ekstra gradyan yok. |
| Paylaşımlı uzman | "Her zaman açık" | Her token'ın geçtiği ekstra uzman; ortak bilgiyi yakalar. |
| Uzman-parallellik | "Uzmana göre paylaştır" | Farklı uzmanları farklı GPU'lara dağıt; token'ları ağ üzerinden yönlendir. |
| Seyreltiklik (Sparsity) | "Ekin parametre < toplam parametre" | `k × uzman_boyutu / (E × uzman_boyutu)` oranı; DeepSeek-V3 için 37/671 ≈ %5.5. |

## İleri Okuma

- [Shazeer ve diğerleri (2017). Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer](https://arxiv.org/abs/1701.06538) — fikir.
- [Fedus, Zoph, Shazeer (2022). Switch Transformer: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity](https://arxiv.org/abs/2101.03961) — Switch, klasik MoE.
- [Jiang ve diğerleri (2024). Mixtral of Experts](https://arxiv.org/abs/2401.04088) — Mixtral 8×7B.
- [DeepSeek-AI (2024). DeepSeek-V3 Technical Report](https://arxiv.org/abs/2412.19437) — MLA + yardımcı-kayıpsız MoE + MTP.
- [Wang ve diğerleri (2024). Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts](https://arxiv.org/abs/2408.15664) — önyargı-tabanlı dengeleme makalesi.
- [Dai ve diğerleri (2024). DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models](https://arxiv.org/abs/2401.06066) — bu dersin yönlendiricisinin kullandığı ince taneli + paylaşımlı-uzman bölünmesi.
- [Kim ve diğerleri (2022). DeepSpeed-MoE: Advancing Mixture-of-Experts Inference and Training](https://arxiv.org/abs/2201.05596) — orijinal paylaşımlı-uzman makalesi.
