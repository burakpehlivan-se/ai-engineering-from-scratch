# Oyunlar İçin RL — AlphaZero, MuZero ve LLM-Muhakeme Çağı

> 1992: TD-Gammon saf TD ile insan şampiyonları yendi. 2016: AlphaGo Lee Sedol'u yendi. 2017: AlphaZero sıfırdan satranç, shogi ve go'ya hükmetti. 2024: DeepSeek-R1 aynı tarifin — GRPO PPO'yu değiştirerek — muhakeme üzerinde çalıştığını kanıtladı. Oyunlar, bu fazdaki her atılımı yönlendiren benchmark'tır.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 9 · 05 (DQN), Faz 9 · 08 (PPO), Faz 9 · 09 (RLHF), Faz 9 · 10 (MARL)
**Süre:** ~120 dakika

## Problem

Oyunlar, RL'nin istediği her şeye sahiptir. Temiz ödül (kazanma/kaybetme). Sonsuz bölüm (self-play sıfırlamaları). Mükemmel simülasyon (oyun *kendisi* simülatördür). Ayrık veya küçük sürekli eylem alanları. Düşmanca dayanıklılığı zorunlu kılan çoklu ajan yapısı.

Ve oyunlar her büyük RL atılımının test edildiği yerdi. TD-Gammon (tavla, 1992). Atari-DQN (2013). AlphaGo (2016). AlphaZero (2017). OpenAI Five (Dota 2, 2019). AlphaStar (StarCraft II, 2019). MuZero (öğrenilmiş model, 2019). AlphaTensor (matris çarpımı, 2022). AlphaDev (sıralama algoritmaları, 2023). DeepSeek-R1 (matematik muhakemesi, 2025) — oyun-RL tekniklerinin metin üzerinde çalıştığını gösteren en son gösteri.

Bu kapanış dersi, üç dönüm noktası mimarisini — AlphaZero, MuZero ve GRPO'yu — tek bir birleştirici mercekten inceler: **self-play + arama + politika iyileştirme**. Her biri bir öncekini genelleştirir; GRPO özellikle AlphaZero'nun LLM muhakemesine uygulanmış tarifidir; token'lar aksiyonlar, matematik doğrulama ise kazanma sinyalidir.

## Kavram

![AlphaZero ↔ MuZero ↔ GRPO: aynı döngü, farklı ortamlar](../assets/rl-games.svg)

**Birleştirici döngü.**

```
while True:
    trajectory = self_play(current_policy, search)     # play game against self
    policy_target = search.improved_policy(trajectory) # search improves raw policy
    policy_net.update(policy_target, value_target)     # supervised on search output
```

**AlphaZero (2017).** Silver ve diğerleri. Bilinen kuralları olan bir oyun (satranç, shogi, go) verildiğinde:

- Policy-value ağı: tek bir kafatı `f_θ(s) → (p, v)`. `p`, yasal hamleler üzerinde bir önceki olasılıktır (prior). `v`, beklenen oyun sonucudur.
- Monte Carlo Tree Search (MCTS): her hamlede, olası devamların bir ağacını genişlet. `(p, v)`'yi önceki + bootstrap olarak kullan. Düğümeleri UCB (PUCT) ile seç: `a* = argmax Q(s, a) + c · p(a|s) · √N(s) / (1 + N(s, a))`.
- Self-play: ajan-vs-ajan oyunları oyna. Hamle `t`'de MCTS ziyaret dağılımı `π_t`, politika eğitim hedefi haline gelir.
- Kayıp: `L = (v - z)² - π · log p + c · ||θ||²`. `z`, oyun sonucudur (+1 / 0 / -1).

Sıfır insan bilgisi. Sıfır el yapımı sezgisel. Her biri birkaç on milyon self-play oyunundan sonra satranç, shogi ve go'ya hükmeden tek bir tarif.

**MuZero (2019).** Schrittwieser ve diğerleri. Kuralların bilinmesi gerekliliğini kaldırır.

- Sabit bir ortam yerine bir *gizli dinamik modeli* `(h, g, f)` öğren:
  - `h(s)`: gözlemi gizli duruma kodla.
  - `g(s_latent, a)`: sonraki gizli durumu + ödülü tahmin et.
  - `f(s_latent)`: politika önceki + değeri tahmin et.
- MCTS *öğrenilmiş gizli alanda* çalıştır. Aynı arama, aynı eğitim döngüsü.
- Go, satranç, shogi *ve* Atari üzerinde çalışır — tek algoritma, kural bilgisi yok.

**Stochastic MuZero (2022).** Rastgele dinamikler ve şans düğümleri ekler; tavla sınıfı oyunlara genişletir.

**Muesli, Gumbel MuZero (2022-2024).** Örnek verimliliği ve deterministik arama üzerinde geliştirmeler.

**GRPO (2024-2025).** DeepSeek-R1 tarifi. Aynı AlphaZero-şekilli döngü, dil modeli muhakemesine uygulanır:

- "Oyun": bir matematik / kodlama / muhakeme sorusunu yanıtlamak. "Kazanma" = doğrulayıcı (test durumu geçer, sayısal cevap eşleşir) 1 döndürür.
- Politika: LLM. Aksiyonlar: token'lar. Durum: istem + şimdiye kadar verilen yanıt.
- Critic yok (PPO tarzı V_φ). Bunun yerine, her istem için politikadan `G` tamamlama örnekle. Her biri için ödül hesapla. REINFORCE tarzı güncelleme sinyali olarak **group-relative advantage** `A_i = (r_i - mean_r) / std_r` kullan.
- Saptamayı önlemek için referans politikaya KL cezası (RLHF gibi).
- Tam kayıp:

  `L_GRPO(θ) = -E_{q, {o_i}} [ (1/G) Σ_i A_i · log π_θ(o_i | q) ] + β · KL(π_θ || π_ref)`

Reward model yok, critic yok, MCTS yok. Group-relative baseline üçünün de yerini alır. Muhakeme benchmark'larında PPO-RLHF kalitesini eşler veya aşar, çok daha az hesaplama maliyetiyle.

**Tam R1 tarifi.** DeepSeek-R1 (DeepSeek 2025) tek bir makalede iki modeldir:

- **R1-Zero.** DeepSeek-V3 temel modelinden başla. SFT yok. GRPO'yu doğrudan iki bileşenli ödülle uygula: *doğruluk ödülü* (kural tabanlı — son cevap doğru sayıya dönüştürülebildi mi / kod birim testlerini geçti mi) ve *biçim ödülü* (düşünce zinciri `<think>…</think>` etiketlerine sarıldı mı). Binlerce adımda ortalama yanıt uzunluğu ~100'den ~10.000 token'a büyür ve matematik benchmark puanları neredeyse o1-preview seviyelerine tırmanır. Model sıfırdan muhakeme etmeyi öğrenir. Dezavantajı: düşünme zincirleri genellikle okunaksızdır, dilleri karıştırır ve üslupsal parlaklıktan yoksundur.
- **R1.** R1-Zero'nun okunabilirlik sorunlarını dört aşamalı bir hatla çöz:
  1. **Soğuk başlangıç SFT.** Temiz biçimlendirmeyle birkaç bin uzun-CoT gösterimi topla. Temel modeli bunlar üzerinde denetimli ince ayar yap. Bu okunabilir bir başlangıç noktası sağlar.
  2. **Muhakeme odaklı GRPO.** Doğruluk+biçim ödüllerine ek olarak kod değiştirmemayı önleyen bir *dil-tutarlılığı* ödülü ile GRPO uygula.
  3. **Reddetme örnekleme + SFT 2. tur.** RL kontrol noktasından ~600K muhakeme yörüngesi örnekle, sadece doğru son cevaplara ve okunabilir CoT'ye sahip olanları tut ve ~200K mantık-dışı SFT örneğiyle (yazma, soru-cevap, öz-bilinç) birleştir. Temel modeli tekrar ince ayar yap.
  4. **Tam spektrum GRPO.** Hem muhakeme (kural tabanlı ödüller) hem de genel hizalama (yardımcılık/zararsızlık tercih tabanlı ödüller) kapsayan bir RL turu daha.

Sonuç, ağırlıkları açık olan o1'i AIME ve MATH-500'de eşler ve damıtmak için yeterince küçüktür. Aynı makale ayrıca R1'in muhakeme izleri üzerinde SFT yaparak altı damıtılmış yoğun model (Qwen-1.5B'den Llama-70B'ye) yayınlar — öğrencide RL yok. Güçlü bir RL öğretmeninin damıtması, öğrenci ölçeğinde sıfırdan RL'den tutarlı olarak daha iyi sonuç verir.

**Neden muhakeme için PPO yerine GRPO?** DeepSeekMath makalesinde (Şubat 2024) üç nedir: (1) eğitilecek değer ağı yok, belleği yarıya indirir; (2) group baseline, muhakeme görevlerinin ürettiği seyrek bölüm-sonu ödülünü doğal şekilde ele alır; (3) istem-başına normalizasyon, farklı zorluktaki sorunlar arasında advantage'leri karşılaştırılabilir kılar; PPO'nun tek critici bunu yapamaz.

**Aramasız vs arama-tabanlı.** Oyunlar iki kola ayrılmıştır:

- *Uzun ufuklu tam bilgi oyunları* (go, satranç): hala arama-tabanlı. AlphaZero / MuZero baskındır.
- *LLM muhakemesi*: üretimde henüz MCTS yok; tam rollout'lar üzerinde GRPO, çıkarım hesaplaması için best-of-N. Süreç reward modelleri (PRM), seviye-aramanın geri ekleneceğine dair ipuçları verir.

## İnşa Et

`code/main.py`'deki kod, **minyatür GRPO** uygular — örnekleme grupları olan bir bandit. Algoritma LLM'dekiyle aynıdır; sadece politika ve ortam daha basittir. *Kaybı* ve *group-relative advantage*'yi öğretir; bu 2024 DeepSeek hilesidir.

### Adım 1: küçük bir doğrulayıcı ortam

```python
QUESTIONS = [
    {"prompt": "q1", "correct": 3},
    {"prompt": "q2", "correct": 1},
]

def verify(prompt_idx, answer_token):
    return 1.0 if answer_token == QUESTIONS[prompt_idx]["correct"] else 0.0
```

#### Açıklama

Gerçek GRPO'da doğrulayıcı birim testleri çalıştırır veya matematik eşitliğini kontrol eder.

### Adım 2: politika: her istem için K cevap token'ı üzerinde softmax

```python
def policy_probs(theta, p_idx):
    return softmax(theta[p_idx])
```

#### Açıklama

Bir isteme koşullu bir LLM'nin son katman çıktısına eşdeğerdir.

### Adım 3: grup örnekleme ve group-relative advantage

```python
def grpo_step(theta, p_idx, G=8, beta=0.01, lr=0.1, rng=None):
    probs = policy_probs(theta, p_idx)
    samples = [sample(probs, rng) for _ in range(G)]
    rewards = [verify(p_idx, s) for s in samples]
    mean_r = sum(rewards) / G
    std_r = stddev(rewards) + 1e-8
    advs = [(r - mean_r) / std_r for r in rewards]

    for a, A in zip(samples, advs):
        grad = onehot(a) - probs
        for i in range(len(probs)):
            theta[p_idx][i] += lr * A * grad[i]
    # KL penalty: pull theta toward reference
    for i in range(len(probs)):
        theta[p_idx][i] -= beta * (theta[p_idx][i] - reference[p_idx][i])
```

#### Açıklama

Group-relative advantage 2024 DeepSeek hilesidir. Critic gerekmez. "Baseline" grup ortalamasıdır ve normalizasyon grup std'sini kullanır.

### Adım 4: REINFORCE baseline'ı ile karşılaştır (değersiz)

Aynı kurulum, aynı hesaplama, saf REINFORCE. GRPO daha hızlı ve daha kararlı yakınsar.

### Adım 5: entropi ve KL'yi gözlemle

RLHF ile aynı tanılar: referansa ortalama KL, politika entropisi, zaman içinde ödül. Bunlar durağanlaştığında eğitim biter.

## Tuzaklar

- **Doğrulayıcı istismarı aracılığıyla reward hacking.** GRPO, RLHF'nin riskini miras alır: doğrulayıcı yanlışsa veya istismar edilebilirse, LLM istismarı bulur. Sağlam doğrulayıcılar (çoklu test durumları, resmi ispatlar) önemlidir.
- **Çok küçük grup boyutu.** Group baseline varyansı `1/√G` gibi azalır. `G = 4`'ün altında advantage sinyali gürültülüdür; standart seçim `G = 8` ile `64` arasındadır.
- **Uzunluk önyargısı.** Farklı uzunluklardaki LLM tamamlamalarının farklı log-olasılıkları vardır. Token sayısına göre normalleştir veya dize-seviyesinde log-prob kullan veya maksimum uzunluğa kes.
- **Saf self-play döngüleri.** AlphaZero tarzı eğitim genel toplamlı oyunlarda hakimiyet döngülerine takılabilir. Çeşitli rakip havuzlarıyla (lig oynaması, Ders 10) hafifletilir.
- **Arama-politika uyumsuzluğu.** AlphaZero, politikayı arama çıktısını taklit etmesi için eğitir. Politika ağı aramanın dağılımını temsil edecek kadar küçükse, eğitim durur.
- **Hesaplama zemini.** MuZero / AlphaZero devasa hesaplama gerektirir. Tek bir ablasyon genellikle yüzlerce GPU-saatidir. Öğrenme için minyatür demolar mevcuttur (örn., Connect Four üzerinde AlphaZero).
- **Doğrulayıcı kapsamı.** Hatalı bir çözümü geçen birim testleri hatayı güçlendirir. Kenar vakalarını yakalayan doğrulayıcılar tasarla.

## Kullanım

2026 oyun-RL manzarası, alana göre:

| Alan | Baskın yöntem |
|--------|-----------------|
| İki oyunculu sıfır toplamlı tahta oyunları (go, satranç, shogi) | AlphaZero / MuZero / KataGo |
| Eksik bilgi kart oyunları (poker) | CFR + deep learning (DeepStack, Libratus, Pluribus) |
| Atari / piksel oyunları | Muesli / MuZero / IMPALA-PPO |
| Büyük çoklu oyuncu strateji (Dota, StarCraft) | PPO + self-play + lig (OpenAI Five, AlphaStar) |
| LLM matematik/kod muhakemesi | GRPO (DeepSeek-R1, Qwen-RL, açık çoğaltımlar) |
| LLM hizalama | DPO / RLHF-PPO (GRPO değil; doğrulayıcı tercih tabanlıdır, doğrulanabilir değil) |
| Robotik | PPO + DR (oyun-RL değil ama aynı policy gradient araçlarını kullanır) |
| Kombinatoryal sorunlar | AlphaZero varyantları (AlphaTensor, AlphaDev) |

*Tarif* — self-play, arama-geliştirmeli iyileştirme, politika damıtma — metin, piksel ve fiziksel kontrolü kapsar. GRPO en genç örnektir; daha fazlası geliyor.

## Gemileştir

`outputs/skill-game-rl-designer.md` olarak kaydet:

```markdown
---
name: game-rl-designer
description: Belirli bir alan için bir oyun-RL veya muhakeme-RL eğitim hattı tasarla (AlphaZero / MuZero / GRPO).
version: 1.0.0
phase: 9
lesson: 12
tags: [rl, alphazero, muzero, grpo, self-play]
---

Bir hedef (tam-bilgi oyunu / eksik-bilgi / Atari / LLM muhakemesi / kombinatoryal) verildiğinde, output et:

1. Ortam uyumu. Bilinen kurallar mı? Markov mu? Rastgele mi? Çoklu ajan mı? AlphaZero vs MuZero vs GRPO'yu yönlendirir.
2. Arama stratejisi. MCTS (öğrenilmiş prior ile PUCT), Gumbel-örneklemeli, best-of-N veya yok.
3. Self-play planı. Simetrik self-play / lig / çevrimdışı veri / doğrulayıcı-üretilmiş.
4. Hedef sinyali. Oyun sonucu / doğrulayıcı ödül / tercih / öğrenilmiş model. Dayanıklılık planını dahil et.
5. Tanılama. Baseline'a karşı kazanma oranı, ELO eğrisi, doğrulayıcı geçme oranı, referansa KL.

Eksik bilgi oyunlarında AlphaZero'yı reddet (yönlendirme CFR'ye). Güvenilir doğrulayıcı olmadan GRPO'yu reddet. Sabit baseline rakip seti olmayan her oyun-RL hattını reddet (self-play ELO'su aksi takdirde kalibre edilmemiştir).
```

## Alıştırmalar

1. **Kolay.** `code/main.py`'deki GRPO banditini uygula. 2 istem × 4 cevap token'ı ile eğit. `G=8` ile < 1.000 güncellemede yakınsa.
2. **Orta.** PPO (kırpılmış) ve saf REINFORCE ekle. Aynı bandit üzerinde GRPO ile örnek verimliliğini ve ödül varyansını karşılaştır.
3. **Zor.** Uzunluğu 2 olan bir "muhakeme zincirine" genişlet: ajan iki token üretir ve doğrulayıcı çifti ödüllendirir. GRPO'nun iki adımlık diziler boyunca kredi dağıtımını nasıl ele aldığını ölç. (İpucu: *tam dizi* başına group advantage hesapla, her iki token konumuna da yay.)
