# Reward Modeling ve RLHF

> İnsanlar "iyi asistan yanıtı" için bir ödül fonksiyonu yazamazlar, ama iki yanıtı karşılaştırıp daha iyisini seçebilirler. Bu karşılaştırmalara bir reward model uydur, sonra dil modelini ona göre RL ile eğit. Christiano 2017. InstructGPT 2022. GPT-3'ü ChatGPT'ye dönüştüren tarif. 2026'da çoğunlukla DPO ile değiştiriliyor — ama zihinsel model kalıyor.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 5 · 05 (Sentiment), Faz 9 · 08 (PPO)
**Süre:** ~45 dakika

## Problem

Bir dil modelini next-token-prediction amacı ile eğittin. Gramer doğru İngilizce yazıyor. Ayrıca yalan söylüyor, dolaşıyor ve reddetmeyi reddediyor. Bunu daha fazla ön-eğitimle düzeltemezsin — web metni sorunun kendisidir, çaresi değil.

"X talimatı için A yanıtı B'nden daha iyidir" diyen bir *skaler ödül* istiyorsun. Bu ödül fonksiyonunu el yazısıyla yazmak imkansızdır. "Yardımcılık" token'lar üzerinde kapalı formda bir ifade değildir. Ama insanlar iki çıktıyı karşılaştırıp bir tercih belirtebilir. Bu, büyük ölçekte toplamak için ucuzdur.

RLHF (Christiano ve diğerleri 2017; Ouyang ve diğerleri 2022) tercihleri bir reward model'e dönüştürür, sonra dili modelini PPO ile bu ödüle karşı optimize eder. Üç adımda: SFT → RM → PPO. Bu, 2023–2025'te ChatGPT, Claude, Gemini ve her hizalanmış LLM'yi sunan tariftir.

2026'da PPO adımı çoğunlukla DPO (Faz 10 · 08) ile değiştirilmiştir çünkü daha ucuzdur ve hizalama ayarı için neredeyse aynı kalitededir. Ama *reward model* parçası hala her Best-of-N örneklemecisini, her doğrulanabilir ödül-tabanlı RL hattını ve her süreç reward modeli (Process Reward Model) kullanan muhakeme modelini temellendirir. RLHF'yi anlarsan tüm hizalama yığınını anlarsın.

## Kavram

![Üç aşamalı RLHF: SFT, çiftli tercihler üzerinde RM eğitimi, KL cezalı PPO](../assets/rlhf.svg)

**Aşama 1: Denetimli İnce Ayar (SFT).** Önceden eğitilmiş bir temel modelden başla. Hedef davranışın (talimat-takip yanıtları, yardımcı cevaplar vb.) insan yazımlı gösterimleri üzerinde ince ayar yap. Sonuç: *iyi davranışa yönelik önyargılı* ama hala sınırsız bir eylem alanına sahip bir `π_SFT` modeli.

**Aşama 2: Reward Model eğitimi.**

- İstemler `x`'e verilen yanıt çiftleri `(y_+, y_-)` topla; insanlar tarafından "y_+ tercih edilir y_-'den" olarak etiketlenir.
- `y_+'ya` daha yüksek skorlar atamak için bir reward model `R_φ(x, y)` eğit.
- Kayıp: **Bradley-Terry çiftli lojistik** kaybı:

  `L(φ) = -E[ log σ(R_φ(x, y_+) - R_φ(x, y_-)) ]`

  σ sigmoiddir. Ödül farkı tercihin log-olasılık oranını ima eder. BT, 1952'den beri standarttır (Bradley-Terry) ve modern RLHF'de baskın seçimdir.

- `R_φ` genellikle SFT modelinin üzerine bir skaler başlık eklenerek başlatılır. Aynı transformer gövdesi; tek bir doğrusal katman ödüldü output eder.

**Aşama 3: KL cezalı RM'ye karşı PPO.**

- Eğitilebilir politikayı `π_SFT`'den başlat: `π_θ`. Dondurulmuş bir *referans* `π_ref = π_SFT` tut.
- Yanıt `y`'nin sonundaki ödül:

  `r_total(x, y) = R_φ(x, y) - β · KL(π_θ(·|x) || π_ref(·|x))`

  KL cezası, `π_θ`'nın `π_SFT`'den keyfi olarak sapmasını önler — bu bir *düzenleyicidir*, sıkı bir güven bölgesi değil. `β` tipik olarak `0.01`-`0.05`.
- Bu ödül ile PPO (Ders 08) çalıştır. Advantage'ler token seviyesindeki yörünge üzerinde hesaplanır ama RM sadece tam yanıtı puanlar.

**Neden KL?** Olmadığında PPO, reward-hacking stratejilerini mutlulukla bulur — RM sadece dağılım içindeki tamamlamalar üzerinde eğitilmişti. Dağılım dışı bir yanıt, herhangi bir insan yazımından daha yüksek puan alabilir. KL, `π_θ`'yı RM'nin eğitildiği manifolda yakın tutar. RLHF'deki en önemli ayar düğmesidir.

**2026 durumu:**

- **DPO** (Rafailov 2023): kapalı form cebir, 2+3. aşamaları tercih verileri üzerinde tek bir denetimli kayba sıkıştırır. RM yok, PPO yok. Hizalama benchmark'larında aynı kalite, çok daha az hesaplama maliyetiyle. Faz 10 · 08'de ele alınır.
- **GRPO** (DeepSeek 2024–2025): Critic yerine group-relative baseline kullanan PPO; insan tarafından eğitilmiş RM yerine *doğrulayıcıdan* (kod çalışır / matematik cevabı eşleşir) ödül. Muhakeme modellerinde baskındır. Faz 9 · 12'de ele alınır.
- **Süreç reward modeli (PRM):** Kısmi çözümleri (her muhakeme adımını) puanlar; hem RLHF hem de muhakeme varyantlarında GRPO kullanılır.
- **Constitutional AI / RLAIF:** Tercihleri insanlar yerine hizalanmış bir LLM ile üret. Tercih bütçesini ölçeklendirir.

## İnşa Et

Bu ders, dizeler olarak temsil edilen küçük sentetik "istemleri" ve "yanıtları" kullanır. RM, token torbası (bag-of-tokens) temsili üzerinde doğrusal bir puanlayıcıdır. Gerçek LLM yok — hattın *şekli* önemlidir, ölçek değil. `code/main.py`'ye bakın.

### Adım 1: sentetik tercih verileri

```python
PROMPTS = ["help me", "answer me", "explain this"]
GOOD_WORDS = {"clear", "specific", "kind", "thorough"}
BAD_WORDS = {"vague", "rude", "wrong", "short"}

def make_pair(rng):
    x = rng.choice(PROMPTS)
    y_good = rng.choice(list(GOOD_WORDS)) + " " + rng.choice(list(GOOD_WORDS))
    y_bad = rng.choice(list(BAD_WORDS)) + " " + rng.choice(list(BAD_WORDS))
    return (x, y_good, y_bad)
```

#### Açıklama

Gerçek RLHF'de bunu insan etiketçiler yapar. Şekil — `(prompt, preferred_response, rejected_response)` — özdeştir.

### Adım 2: Bradley-Terry reward modeli

Doğrusal skor: `R(x, y) = w · bag(y)`. BT çiftli log-kayıbını minimize etmek için eğit:

```python
def rm_train_step(w, x, y_pos, y_neg, lr):
    r_pos = dot(w, bag(y_pos))
    r_neg = dot(w, bag(y_neg))
    p = sigmoid(r_pos - r_neg)
    for tok, cnt in bag(y_pos).items():
        w[tok] += lr * (1 - p) * cnt
    for tok, cnt in bag(y_neg).items():
        w[tok] -= lr * (1 - p) * cnt
```

#### Açıklama

Birkaç yüz güncelleme sonra `w`, iyi kelime token'larına pozitif, kötülere negatif ağırlıklar atar.

### Adım 3: RM üzerine PPO benzeri politika

Oyuncak politikamız bir sözlükten tek bir token üretir. Token'ı RM altında puanlayıp `log π_θ(token | prompt)` hesaplar, referansa KL cezası ekler ve kırpılmış PPO surrogate'ini uygularız.

```python
def rlhf_step(theta, ref, w, prompt, rng, eps=0.2, beta=0.1, lr=0.05):
    logits_theta = policy_logits(theta, prompt)
    probs = softmax(logits_theta)
    token = sample(probs, rng)
    logits_ref = policy_logits(ref, prompt)
    probs_ref = softmax(logits_ref)
    reward = dot(w, bag([token])) - beta * kl(probs, probs_ref)
    # ppo-style update on theta, treating reward as the return
    ...
```

#### Açıklama

Ödülü getiri olarak ele alarak theta üzerinde PPO tarzı güncelleme.

### Adım 4: KL'yi izle

Her güncellemede ortalama `KL(π_θ || π_ref)`'yi izle. `~5-10`'un üzerine çıkarsa politika `π_SFT`'den çok uzaklaşmıştır — `β` düşüyor veya reward hacking başlıyor. Bu gerçek RLHF'deki en önemli tanı aracıdır.

### Adım 5: TRL ile üretim tarifi

Oyuncak hattı anladığında, aynı döngüyü gerçek bir kütüphane kullanıcısının nasıl yazdığını görebilirsin. Hugging Face'in [TRL](https://huggingface.co/docs/trl) kütüphanesi referans uygulamasıdır — Aşama 2 için `RewardTrainer` ve Aşama 3 için ( dahili referansa KL ile) `PPOTrainer`.

```python
# Aşama 2: çiftli tercihlerden reward model
from trl import RewardTrainer, RewardConfig
from transformers import AutoModelForSequenceClassification, AutoTokenizer

tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
rm = AutoModelForSequenceClassification.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct", num_labels=1
)

# veri seti satırları: {"prompt", "chosen", "rejected"} — Bradley-Terry formatı
trainer = RewardTrainer(
    model=rm,
    tokenizer=tok,
    train_dataset=preference_data,
    args=RewardConfig(output_dir="./rm", num_train_epochs=1, learning_rate=1e-5),
)
trainer.train()
```

```python
# Aşama 3: SFT referansına KL cezalı RM'ye karşı PPO
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead

policy = AutoModelForCausalLMWithValueHead.from_pretrained("./sft-checkpoint")
ref    = AutoModelForCausalLMWithValueHead.from_pretrained("./sft-checkpoint")  # dondurulmuş

ppo = PPOTrainer(
    config=PPOConfig(learning_rate=1.41e-5, batch_size=64, init_kl_coef=0.05,
                     target_kl=6.0, adap_kl_ctrl=True),
    model=policy, ref_model=ref, tokenizer=tok,
)

for batch in dataloader:
    responses = ppo.generate(batch["query_ids"], max_new_tokens=128)
    rewards   = rm(torch.cat([batch["query_ids"], responses], dim=-1)).logits[:, 0]
    stats     = ppo.step(batch["query_ids"], responses, rewards)
    # stats içerir: mean_kl, clip_frac, value_loss — üç PPO tanı aracı
```

#### Açıklama

Kütüphane sizin için üç şey yapar. `adap_kl_ctrl=True` adaptif β programını uygular: gözlenen KL `target_kl`'yi aşarsa β ikiye katlanır; yarısının altına düşerse β yarıya iner. Referans modeli sözleşme gereği dondurulmuştur — `policy` ile yanlışlıkla parametre paylaşımı yapmamalısınız. Değer başlığı politika ile aynı gövde üzerindedir (`AutoModelForCausalLMWithValueHead` skaler bir MLP başlığı ekler), bu yüzden TRL `policy/kl` ve `value/loss`'u ayrı raporlar.

## Tuzaklar

- **Aşırı optimizasyon / reward hacking.** RM kusurludur; `π_θ`, yüksek puan alan ama kötü olan düşmanca tamamlamalar bulur. Belirtiler: ödül sonsuz yükselirken insan değerlendirme puanı durağanlaşır veya düşer. Düzeltme: erken durdur, `β`'yi artır, RM eğitim verisini genişlet.
- **Uzunluk hilesi.** Yardımcı yanıtlar üzerinde eğitilmiş RM'ler genellikle dolaylı olarak uzunluğu ödüllendirir. Politika yanıtları doldurmayı öğrenir. Çare: uzunluk-normalleştirilmiş ödül veya uzunluk-bilinçli RM ile RLAIF.
- **Çok küçük RM.** RM en az politika kadar büyük olmalıdır. Çok küçük bir RM politikanın çıktılarını sadık bir şekilde puanlayamaz.
- **KL ayarı.** Çok düşük β → sapma ve reward hacking. Çok yüksek β → politika neredeyse değişmez. Standart hile, adım başına sabit bir KL'yi hedefleyen *adaptif* β'dır.
- **Tercih verisi gürültüsü.** İnsan etiketlerinin ~%30'u gürültülü veya belirsizdir. RM'yi anlaşmaya filtrelenmiş veriler üzerinde eğiterek kalibre et veya BT'de sıcaklık (temperature) kullan.
- **Off-policy sorunları.** PPO verisi ilk epoch'tan sonra biraz off-policy olur. Kırpma oranını Ders 08'deki gibi izle.

## Kullanım

2026'da RLHF katmanlıdır:

| Katman | Hedef | Yöntem |
|-------|--------|--------|
| Talimat takibi, yardımcılık, zararsızlık | Hizalama | RLHF-PPO yerine DPO (Faz 10 · 08) tercih edilir. |
| Muhakeme doğruluğu (matematik, kod) | Yetenek | Doğrulayıcı ödüllü GRPO (Faz 9 · 12). |
| Uzun ufuklu çoklu adım görevleri | Ajan tabanlı | Adımlar üzerinde süreç reward modelli PPO / GRPO. |
| Güvenlik / davranış reddi | Güvenlik | Ayrı güvenlik RM'si ile RLHF-PPO veya Constitutional AI. |
| Çıkarımda Best-of-N | Hızlı hizalama | Çıkarma zamanında RM kullan; politika eğitimi gerekmez. |
| Ödül damıtma | Çıkarım hesaplama | Dondurulmuş LM üzerine küçük bir "ödül başlığı" eğit. |

RLHF 2022–2024'te *en önemli* yöntemdi. 2026'da üretim hizalama hatları DPO-önceliklidir; PPO sadece RM-yoğun veya güvenlik-kritik adımlarda kullanılır.

## Gemileştir

`outputs/skill-rlhf-architect.md` olarak kaydet:

```markdown
---
name: rlhf-architect
description: Bir dil modeli için RLHF / DPO / GRPO hizalama hattı tasarla; RM, KL ve veri stratejisini dahil et.
version: 1.0.0
phase: 9
lesson: 9
tags: [rl, rlhf, alignment, llm]
---

Bir temel LM, bir hedef davranış (hizalama / muhakeme / reddi / ajan) ve bir tercih veya doğrulayıcı bütçesi verildiğinde, output et:

1. Aşama. SFT? RM? DPO? GRPO? Gerekçesiyle.
2. Tercih veya doğrulayıcı kaynağı. İnsanlar, AI geri bildirimi, kural tabanlı, birim-test-geçme veya ödül damıtması.
3. KL stratejisi. Sabit β, adaptif β veya DPO (dolaylı KL).
4. Tanılama. Ortalama KL, ödül kararlılığı, aşırı optimizasyon koruması (tutulmuş insan değerlendirmesi).
5. Güvenlik kapısı. Red-takım kümesi, reddetme oranı, yardımcılık RM'sinden ayrı güvenlik RM'si.

KL izleyicisi olmadan RLHF-PPO gönderimini reddet. Hedef politikadan daha küçük RM kullanılmasını reddet. Sadece-uzunluk ödüllerini reddet. Tutulmuş bir insan-değerlendirme kümesi tutmayan her hattı aşırı optimizasyon koruması eksik olarak işaretle.
```

## Alıştırmalar

1. **Kolay.** `code/main.py`'deki Bradley-Terry reward modelini 500 sentetik tercih çifti üzerinde eğit. Tutulmuş 100 çift üzerinde çiftli doğruluğu ölç. %90'ı geçmelidir.
2. **Orta.** Oyuncak PPO-RLHF döngüsünü `β ∈ {0.0, 0.1, 1.0}` ile çalıştır. Her biri için güncelleme boyunca RM skorunu referansa KL'ye göre çiz. Hangileri reward-hack yapıyor?
3. **Zor.** Aynı tercih verileri üzerinde DPO (kapalı form tercih-olasılık kaybı) uygula ve kullandığı hesaplama ile elde edilen son RM skoru açısından RLHF-PPO hattıyla karşılaştır.

## Anahtar Terimler

| Terim | İnsanlar ne der | Gerçekte ne anlama gelir |
|------|-----------------|-----------------------|
| RLHF | "Hizalama RL" | Üç aşamalı SFT + RM + PPO hattı (Christiano 2017, Ouyang 2022). |
| Reward Model (RM) | "Puanlama ağı" | Çiftli tercihlere Bradley-Terry ile uydurulmuş öğrenilmiş skaler fonksiyon. |
| Bradley-Terry | "Çiftli lojistik kayıp" | `P(y_+ ≻ y_-) = σ(R(y_+) - R(y_-))`; standart RM amacı. |
| KL cezası | "Referansa yakın kal" | Ödüldedeki `β · KL(π_θ \|\| π_ref)`; anti-reward-hacking düzenleyicisi. |
| Reward hacking | "Goodhart yasası" | Politika RM kusurlarını istismar eder; belirtiler: ödül artar, insan değerlendirme durağanlaşır. |
| RLAIF | "AI etiketli tercihler" | Etiketleri insanlar yerine başka bir LM'den gelen RLHF. |
| PRM | "Süreç Reward Modeli" | Kısmi muhakeme adımlarını puanlar; muhakeme hatlarında kullanılır. |
| Constitutional AI | "Anthropic yöntemi" | Açık kurallarla yönlendirilmiş AI tarafından üretilmiş tercihler. |

## İleri Okuma

- [Christiano ve diğerleri (2017). Deep Reinforcement Learning from Human Preferences](https://arxiv.org/abs/1706.03741) — RLHF'yi başlatan makale.
- [Ouyang ve diğerleri (2022). InstructGPT — Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) — ChatGPT'nin arkasındaki tarif.
- [Stiennon ve diğerleri (2020). Learning to summarize with human feedback](https://arxiv.org/abs/2009.01325) — özetleme için erken RLHF.
- [Rafailov ve diğerleri (2023). Direct Preference Optimization](https://arxiv.org/abs/2305.18290) — DPO; 2026'da RLHF sonrası varsayılan.
- [Bai ve diğerleri (2022). Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) — RLAIF ve öz-eleştiri döngüsü.
- [Anthropic RLHF makalesi (Bai ve diğerleri 2022). Training a Helpful and Harmless Assistant](https://arxiv.org/abs/2204.05862) — HH makalesi.
- [Hugging Face TRL kütüphanesi](https://huggingface.co/docs/trl) — üretim `RewardTrainer` ve `PPOTrainer`. Adaptif-KL ve değer başlığı detayları için eğitici kaynağını okuyun.
- [Hugging Face — Illustrating Reinforcement Learning from Human Feedback](https://huggingface.co/blog/rlhf) Lambert, Castricato, von Werra, Havrilla tarafından — diyagramlarla üç aşamalı hattın kanonik yürüyüşü.
- [von Werra ve diğerleri (2020). TRL: Transformer Reinforcement Learning](https://github.com/huggingface/trl) — kütüphane; `examples/` Llama, Mistral ve Qwen için uçtan uca RLHF betikleri içerir.
- [Sutton & Barto (2018). Böl. 17.4 — Designing Reward Signals](http://incompleteideas.net/book/RLbook2020.pdf) — ödül hipotezi görüşü; reward hacking hakkında düşünmek için temel önkoşul.
