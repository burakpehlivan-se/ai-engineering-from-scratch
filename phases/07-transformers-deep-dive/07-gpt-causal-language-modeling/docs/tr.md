# GPT — Nedensel Dil Modelleme (Causal Language Modeling)

> BERT her iki tarafı görür. GPT sadece geçmişi görür. Üçgen maske, modern yapay zekanın en sonuçlu tek satır kodudur.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 02 (Self-Attention), Faz 7 · 05 (Tam Transformer), Faz 7 · 06 (BERT)
**Süre:** ~75 dakika

## Sorun

Bir dil modeli (language model) tek bir soruya cevap verir: ilk `t-1` token verildiğinde, `t` token'ı üzerindeki olasılık dağılımı nedir? O sinyal üzerinde — bir sonraki token tahmini (next-token prediction) — eğitin ve istediğiniz metni token token üretebilen bir model elde edersiniz.

Tüm diziyi paralel olarak uçtan uca eğitmek için, her konumdaki tahminin yalnızca önceki konumlara bağlı olmasını sağlamanız gerekir. Aksi takdirde model cevaba bakarak bariz şekilde hile yapar.

Nedensel maske (causal mask) bunu yapar. Softmax'tan önce dikkat puanlarına eklenen `-inf` değerlerinden oluşan tek bir üst-üçgen matrisdir. Softmax'tan sonra bu konumlar 0 olur. Her konum yalnızca kendisine ve önceki konumlara dikkat edebilir. Ve bunu bir kez tüm diziye uyguladığınızda, tek bir ileriye doğru geçişte N paralel bir sonraki token tahmini elde edersiniz.

GPT-1 (2018), GPT-2 (2019), GPT-3 (2020), GPT-4 (2023), GPT-5 (2024), Claude, Llama, Qwen, Mistral, DeepSeek, Kimi — hepsi aynı çekirdek döngüye sahip sadece-decoder nedensel transformer'lardır. Sadece daha büyük, daha iyi veri ve daha iyi RLHF.

## Kavram

![Nedensel maske üçgen dikkat matrisi oluşturur](../assets/causal-attention.svg)

### Maske

Uzunluğu `N` olan bir dizi verildiğinde, `N × N` bir matris oluşturun:

```
M[i, j] = 0       eğer j <= i
M[i, j] = -inf    eğer j > i
```

#### Açıklama
Bu maske,softmax'tan önce dikkat puanlarına eklenir. `exp(-inf) = 0` olduğundan, maskeli konumlar sıfır ağırlık ekler. Dikkat matrisinin her satırı yalnızca önceki konumlar üzerinde bir olasılık dağılımıdır.

Uygulama maliyeti: tek bir `torch.tril()` çağrısı. Hesaplama süresi: nanosaniye. Alana etkisi: her şey.

### Paralel eğitim, seri çıkarım

Eğitim: tüm `(N, d_model)` dizisini bir kez ileriye doğru geçirin, N çapraz-entropi kaybı hesaplayın (konum başına bir), toplayın, geri yayılım (backprop) yapın. Dizi boyunca paralel. GPT eğitiminin neden ölçeklendiği budur — 1M token'ı tek bir GPU geçişinde işlersiniz.

Çıkarım: token token üretirsiniz. `[t1, t2, t3]` besleyin, `t4` alın. `[t1, t2, t3, t4]` besleyin, `t5` alın. `[t1, t2, t3, t4, t5]` besleyin, `t6` alın. KV-çerez (KV cache) (Ders 12) `t1…tn`'in gizli durumlarını (hidden states) saklar, böylece her adımda yeniden hesaplamazsınız. Ancak çıkarımdaki seri derinlik = çıktı uzunluğu. Bu otonom vergidir (autoregressive tax) ve neden çözümleme (decoding) her LLM'de gecikme darboğazı (latency bottleneck) olduğudur.

### Kayıp — bir kaydırma (shift-by-one)

`[t1, t2, t3, t4]` token'ları verildiğinde:

- Girdi: `[t1, t2, t3]`
- Hedefler: `[t2, t3, t4]`

Her `i` konumu için, `-log P(target_i | inputs[:i+1])` hesaplayın. Toplayın. Bu tüm dizi için çapraz-entropidir.

Duyduğunuz her transformer dil modeli bu kayıp üzerinde eğitilir. Ön-eğitim, inceltme, SFT — aynı kayıp, farklı veri.

### Çözümleme stratejileri

Eğitimden sonra, örnekleme (sampling) seçimleri insanların düşündüğünden daha önemlidir.

| Yöntem | Ne yapar | Ne zaman kullanılır |
|--------|--------------|-------------|
| Açgözlü (Greedy) | Her adımda argmax | Belirli görevler, kod tamamlama |
| Sıcaklık (Temperature) | Logit'leri T'ye böl, örnekle | Yaratıcı görevler, yüksek T = daha fazla çeşitlilik |
| Top-k | Yalnızca en iyi k token'dan örnekle | Düşük olasılık kuyruklarını öldürür |
| Top-p (nükleus) | Kümülatif olasılık ≥ p olan en küçük kümeden örnekle | 2020+ varsayılanı; dağılım şekline uyar |
| Min-p | `p > min_p * max_p` olan token'ları koru | 2024+; top-p'den daha iyi uzun kuyrukları reddeder |
| Spekülatif çözümleme (Speculative decoding) | Taslak model N token önerir, büyük model doğrular | Aynı kalitede 2-3× gecikme azalması |

2026'da, min-p + sıcaklık 0.7, ağırlıkları serbest bırakılan (open-weights) modeller için makul bir varsayılandır. Spekülatif çözümleme, herhangi bir üretim çıkarım yığını için standart bir gerekliliktir.

### "GPT tarifinin" neden işe yaradığı

1. **Sadece-decoder.** Encoder overhead'i yok. Katman başına bir geçişte dikkat + FFN.
2. **Ölçekleme.** 124M → 1.5B → 175B → trilyonlarca. Chinchilla ölçekleme yasaları (Ders 13) hesaplamayı nasıl harcayacağınızı söyler.
3. **Bağlam-içinde öğrenme (In-context learning).** ~6B–13B civarında ortaya çıktı. Model, inceltme olmadan birkaç örnekle (few-shot) uyum sağlayabilir.
4. **RLHF.** İnsan tercihleri üzerinde sonraki eğitim, ham ön-eğitimli metini sohbet asistanlarına dönüştürdü.
5. **Ön-normalizasyon + RoPE + SwiGLU.** Ölçekte kararlı eğitim.

Çekirdek mimari GPT-2'den beri çok değişmedi. İlginç her şey veri, ölçek ve sonraki eğitimde oldu.

## İnşa Et

### Adım 1: nedensel maske

`code/main.py`'ye bakın. Tek satırlık:

```python
def causal_mask(n):
    return [[0.0 if j <= i else float("-inf") for j in range(n)] for i in range(n)]
```

#### Açıklama
Bu maske, dikkat puanlarına softmax'tan önce eklenir. Üst üçgen `-inf` matrisi, her konumun yalnızca kendisine ve önceki konumlara dikkat etmesini sağlar. Tüm mekanizma budur.

### Adım 2: 2 katmanlı GPT benzeri bir model

İki decoder bloğu (maskelenmiş self-attention + FFN, çapraz-dikkat yok) yığın. Bir token gömmesi, bir konumsal kodlama (positional encoding) ve bir çıkarma (unembedding) ekleyin (token gömme matrisine bağlı — GPT-2'den beri standart bir numara).

### Adım 3: bir sonraki token tahmini, uçtan uca

20 token'lık küçük bir sözlükte, her konumda logit üretin. Bir kaydırma hedefine karşı çapraz-entropi kaybı hesaplayın. Gradyan yok — bu bir ileriye doğru geçiş doğrulamasıdır.

### Adım 4: örnekleme

Açgözlü, sıcaklık, top-k, top-p, min-p uygulayın. Her birini sabit bir istem (prompt) üzerinde çalıştırın ve çıktıları karşılaştırın. Bir örnekleme fonksiyonu 10 satırdır.

## Kullan

PyTorch, 2026 dili:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")

prompt = "Attention is all you need because"
inputs = tok(prompt, return_tensors="pt")
out = model.generate(
    **inputs,
    max_new_tokens=64,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
)
print(tok.decode(out[0]))
```

#### Açıklama
`generate()` fonksiyonu, ileriye doğru geçişi çalıştırır, son konum logit'lerini çeker, bir sonraki token'ı örnekler, ekler ve tekrar eder. Her üretim LLM çıkarım yığını (vLLM, TensorRT-LLM, llama.cpp, Ollama, MLX) aynı döngüyü yoğun optimizasyonlarla uygular — toplu doldurma (batched prefill), sürekli toplu işleme (continuous batching), KV-çerez sayfalama (paging), spekülatif çözümleme.

**GPT vs BERT, satır başına birer cümle:** GPT `P(x_t | x_{<t})` tahmin eder. BERT `P(x_masked | x_unmasked)` tahmin eder. Kayıp, modelin üretebilip üretemeyeceğini belirler.

## Teslim Et

`outputs/skill-sampling-tuner.md`'ye bakın. Bu beceri, yeni bir üretim görevi için örnekleme parametrelerini seçer ve belirli çözümlemenin gerekli olduğu durumları bayraklar.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın ve nedensel dikkat matrisinin softmax'tan sonra alt-üçgen olduğunu doğrulayın. Denetim: 3. satır yalnızca 0–3 sütunlarında ağırlıklara sahip olmalıdır.
2. **Orta.** Genişlik 4 için ışın araması (beam search) uygulayın. 10 kısa istemde ışın-4 ile açgözlünün perplexity karşılaştırması. Işın her zaman kazanır mı? (İpucu: genellikle çeviri için, açık uçlu sohbet için değil.)
3. **Zor.** Spekülatif çözümlemeyi uygulayın: bir taslak olarak küçük 2 katmanlı bir model ve bir doğrulayıcı olarak 6 katmanlı bir model kullanın. 64 uzunluğunda 100 tamamlamada gerçek zaman hızlanmasını ölçün. Çıktıların doğrulayıcının açgözlüsüyle eşleştiğini doğrulayın.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Nedensel maske (Causal mask) | "Üçgen" | Dikkat puanlarına eklenen üst-üçgen `-inf` matrisi, böylece `i` konumu yalnızca `≤ i` konumlarını görür. |
| Bir sonraki token tahmini | "Kayıp" | Modelin dağılımının her konumda gerçek bir sonraki token'a karşı çapraz-entropisi. |
| Otonom (Autoregressive) | "Birer birer üret" | Çıktıyı girdi olarak geri besle; paralellik yalnızca eğitim sırasında, üretim sırasında değil. |
| Logit'ler | "Öncesi-softmax puanları" | Softmax'tan önce LM kafasının ham çıktısı; örnekleme bunların üzerinde yapılır. |
| Sıcaklık (Temperature) | "Yaratıcılık düğmesi" | Logit'leri T'ye böl; T→0 = açgözlü, T→∞ = düzgün (uniform). |
| Top-p | "Nükleus örnekleme" | Dağılımı kümülatif olasılık ≥p olan en küçük kümeye kırp; kalanından örnekle. |
| Min-p | "Top-p'den iyi" | `p ≥ min_p × max_p` olan token'ları koru; kıyıcıyı dağılımın keskinliğine uyar. |
| Spekülatif çözümleme (Speculative decoding) | "Taslak + doğrulama" | Ucuz model N token önerir; büyük model paralel olarak doğrular. |
| Öğretmen zorlaması (Teacher forcing) | "Eğitim hilesi" | Eğitim sırasında gerçek bir önceki token'ı besleyin, modelin tahminini değil. Her seq2seq dil modeli için standarttır. |

## İleri Okuma

- [Radford ve diğerleri (2018). Improving Language Understanding by Generative Pre-Training](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) — GPT-1.
- [Radford ve diğerleri (2019). Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) — GPT-2.
- [Brown ve diğerleri (2020). Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) — GPT-3 ve bağlam-içinde öğrenme.
- [Leviathan, Kalman, Matias (2023). Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192) — spekülatif çözümleme makalesi.
- [HuggingFace `modeling_llama.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py) — kanonik nedensel-LM referans kodu.
