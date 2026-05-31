# Policy Gradient — Sıfırdan REINFORCE

> Değer tahminini bırak. Politikayı doğrudan parametrize et, beklenen getirinin gradyanını hesapla, yokuş yukarı adım at. Williams (1992) bunu tek bir teoremde yazdı. PPO, GRPO ve her LLM RL döngüsünün var olmasının nedeni budur.

**Tür:** Build
**Diller:** Python
**Önkoşullar:** Phase 3 · 03 (Backpropagation), Phase 9 · 03 (Monte Carlo), Phase 9 · 04 (TD Learning)
**Süre:** ~75 dakika

## Problem

Q-learning ve DQN *değer* fonksiyonunu parametrize eder. Aksiyonları `argmax Q` ile seçersin. Bu ayrık aksiyonlar ve ayrık durumlar için yeterlidir. Sürekli aksiyonlarda bozulur (10 boyutlu tork üzerinde hangisiyle `argmax` yapacaksın?) veya stokastik (olasılıksal) politika istediğinde (`argmax` yapısı gereği deterministiktir).

Policy gradient ise *politikayı* parametrize eder. `π_θ(a | s)`, aksiyonlar üzerinde bir dağılım output eden sinir ağıdır. Buradan örnek alarak hareket et. Beklenen getirinin `θ`'ya göre gradyanını hesapla. Yokuş yukarı adım at. `argmax` yok. Bellman递归 yok. Sadece `J(θ) = E_{π_θ}[G]` üzerinde gradient ascent.

REINFORCE teoremi (Williams 1992) bu gradyanın hesaplanabilir olduğunu söyler: `∇J(θ) = E_π[ G · ∇_θ log π_θ(a | s) ]`. Bir bölüm (episode) çalıştır. Getiriyi hesapla. Her adımda `∇ log π_θ(a | s)` ile çarp. Ortalamasını al. Gradient ascent. Bitti.

2026'daki her LLM-RL algoritması — PPO, DPO, GRPO — REINFORCE'ın bir iyileştirmesidir. Bunu avucunun içi gibi bilmen, bu fazın ve Phase 10 · 07 (RLHF uygulaması) ile Phase 10 · 08 (DPO) için önkoşuldur.

## Kavram

![Policy gradient: softmax politikası, log-π gradyanı, getiri ağırlıklı güncelleme](../assets/policy-gradient.svg)

**Policy gradient teoremi.** `θ` ile parametrize edilmiş herhangi bir politika `π_θ` için:

`∇J(θ) = E_{τ ~ π_θ}[ Σ_{t=0}^{T} G_t · ∇_θ log π_θ(a_t | s_t) ]`

burada `G_t = Σ_{k=t}^{T} γ^{k-t} r_{k+1}`, `t`'den itibaren indirimli getiridir. Beklenti, `π_θ`'dan örneklenebilen tüm yörüngeler `τ` üzerindendir.

**İspatlama kısadır.** `J(θ) = Σ_τ P(τ; θ) G(τ)` ifadesinin beklenti altında türevini al. `∇P(τ; θ) = P(τ; θ) ∇ log P(τ; θ)` (log-türev hilesi) kullan. `log P(τ; θ) = Σ log π_θ(a_t | s_t) + θ'a bağlı olmayan ortam terimleri` olarak ayrıştır. Ortam terimleri yok olur. İki satır cebirle teoremi elde edersin.

**Varyans azaltma hileleri.** Saf REINFORCE'ın yıkıcı varyansı vardır — getiriler gürültülüdür, `∇ log π` gürültülüdür, çarpımları çok gürültülüdür. İki standart düzeltme:

1. **Baseline çıkarma.** `G_t` yerine `G_t - b(s_t)` kullan; herhangi bir `b(s_t)` fonksiyonu `a_t`'ye bağlı olmasın. Tarafsızdır çünkü `E[b(s_t) · ∇ log π(a_t | s_t)] = 0`. Tipik seçim: `b(s_t) = V̂(s_t)` bir critic tarafından öğrenilir → actor-critic (Ders 07).
2. **Reward-to-go (gitmeyecek ödül).** `Σ_t G_t · ∇ log π_θ(a_t | s_t)` yerine `Σ_t G_t^{from t} · ∇ log π_θ(a_t | s_t)` kullan. Belirli bir aksiyon için sadece gelecek getiriler önemlidir — geçmiş ödüller ortalama sıfır gürültüsü katkıda bulunur.

Birleştirildiğinde:

`∇J ≈ (1/N) Σ_{i=1}^{N} Σ_{t=0}^{T_i} [ G_t^{(i)} - V̂(s_t^{(i)}) ] · ∇_θ log π_θ(a_t^{(i)} | s_t^{(i)})`

bu, baseline'lı REINFORCE'tur — A2C (Ders 07) ve PPO (Ders 08)'nin doğrudan atasıdır.

**Softmax politika parametrizasyonu.** Ayrık aksiyonlar için standart seçim:

`π_θ(a | s) = exp(f_θ(s, a)) / Σ_{a'} exp(f_θ(s, a'))`

burada `f_θ`, her aksiyon için bir skor output eden herhangi bir sinir ağıdır. Gradyanın temiz bir formu vardır:

`∇_θ log π_θ(a | s) = ∇_θ f_θ(s, a) - Σ_{a'} π_θ(a' | s) ∇_θ f_θ(s, a')`

yani alınan aksiyonun skoru eksi politika altındaki beklenen değeri.

**Sürekli aksiyonlar için Gaussian politikası.** `π_θ(a | s) = N(μ_θ(s), σ_θ(s))`. `∇ log N(a; μ, σ)` kapalı formdadır. Phase 9 · 07'deki SAC'ın ihtiyac olan tek şey budur.

## Kodu Yaz

### Adım 1: softmax politika ağı

```python
def policy_logits(theta, state_features):
    return [dot(theta[a], state_features) for a in range(N_ACTIONS)]

def softmax(logits):
    m = max(logits)
    expts = [exp(l - m) for l in logits]
    Z = sum(expts)
    return [e / Z for e in expts]
```

#### Açıklama

Tablo bazlı bir ortam için doğrusal politika (her aksiyon için bir ağırlık vektörü) kullanılır. Atari için CNN ile değiştirip softmax başlığını koruyun.

### Adım 2: örnekleme ve log-olasılık

```python
def sample_action(probs, rng):
    x = rng.random()
    cum = 0
    for a, p in enumerate(probs):
        cum += p
        if x <= cum:
            return a
    return len(probs) - 1

def log_prob(probs, a):
    return log(probs[a] + 1e-12)
```

#### Açıklama

Softmax'tan elde edilen olasılıklardan aksiyon örnekleme ve ilgili log-olasılığı hesaplama.

### Adım 3: log-prob'lar yakalanan rollout

```python
def rollout(theta, env, rng, gamma):
    trajectory = []
    s = env.reset()
    while not done:
        logits = policy_logits(theta, s)
        probs = softmax(logits)
        a = sample_action(probs, rng)
        s_next, r, done = env.step(s, a)
        trajectory.append((s, a, r, probs))
        s = s_next
    return trajectory
```

#### Açıklama

Politika ağı ile tam bir bölüm rollout'u; her adımda durum, aksiyon, ödül ve olasılıklar kaydedilir.

### Adım 4: REINFORCE güncelleme

```python
def reinforce_step(theta, trajectory, gamma, lr, baseline=0.0):
    returns = compute_returns(trajectory, gamma)
    for (s, a, _, probs), G in zip(trajectory, returns):
        advantage = G - baseline
        grad_log_pi_a = [-p for p in probs]
        grad_log_pi_a[a] += 1.0
        for i in range(N_ACTIONS):
            for j in range(len(s)):
                theta[i][j] += lr * advantage * grad_log_pi_a[i] * s[j]
```

#### Açıklama

`∇ log π(a|s) = e_a - π(·|s)` (a'nın one-hot'ı eksi olasılıklar) softmax policy gradient'lerin kalbidir. Bunu kas hafızana yaz.

### Adım 5: baseline'lar

Son bölümlerden `G`'nin hareketli ortalaması, 4×4 GridWorld'ün çalışması için yeterli varyans azaltma sağlar; yakınsama için ~500 bölüm gerekir. Baseline'ı öğrenilmiş `V̂(s)`'e yükselttiğinizde actor-critic elde edersiniz.

## Tuzaklar

- **Patlayan gradyanlar.** Getiriler çok büyük olabilir. `G`'yi `∇ log π` ile çarpmadan önce batch boyunca `~N(0, 1)` olarak normalleştirmeyi unutma.
- **Entropi çöküşü.** Politika çok erken neredeyse deterministik bir aksiyona yakınsar, keşfi durdurur, takılır. Düzeltme: amaca entropi bonusu `β · H(π(·|s))` ekle.
- **Yüksek varyans.** Saf REINFORCE binlerce bölüm gerektirir. Critic baseline'ı (Ders 07) veya TRPO/PPO'nun güven bölgesi (Ders 08) standart çözümdür.
- **Örnek verimliliği.** On-policy, her güncelleme sonra her geçişi attığın anlamına gelir. Importance sampling ile off-policy düzeltmeleri veriyi geri kazandırır ama varyans bedeliyle (PPO'nun oranı kırpılmış bir IS ağırlığıdır).
- **Durulmayan gradyanlar.** 100 bölüm önceki aynı gradyan eski `π` kullanır. On-policy yöntemler bu yüzden her birkaç rollout'ta güncelleme yapar.
- **Kredi dağıtımı.** Reward-to-go olmadan geçmiş ödüller gürültü贡献 eder. Her zaman reward-to-go kullan.

## Kullanım

2026'da REINFORCE nadiren doğrudan çalıştırılır ama gradyan formülü her yerdedir:

| Kullanım alanı | Türetilen yöntem |
|----------|---------------|
| Sürekli kontrol | Gaussian politikalı PPO / SAC |
| LLM RLHF | Token-seviyesinde politika üzerinde çalışan KL cezalı PPO |
| LLM muhakeme (DeepSeek) | GRPO — group-relative baseline'lı REINFORCE, critic yok |
| Çoklu ajan | Merkezi critic'li REINFORCE (MADDPG, COMA) |
| Ayrık aksiyonlu robotik | A2C, A3C, PPO |
| Sadece tercih verileri | DPO — tercih-olasılık kaybına yeniden yazılmış REINFORCE, örnekleme yok |

2026'daki bir eğitim betiğinde `loss = -advantage * log_prob` gördüğünüzde, bu baseline'lı REINFORCE'tur. Tam makaleler (DPO, GRPO, RLOO) bu tek satırın üzerine kurulmuş varyans azaltma hileleridir.

## Ürün Haline Getir

`outputs/skill-policy-gradient-trainer.md` olarak kaydet:

```markdown
---
name: policy-gradient-trainer
description: Belirli bir görev için REINFORCE / actor-critic / PPO eğitim yapılandırması üret ve varyans sorunlarını teşhis et.
version: 1.0.0
phase: 9
lesson: 6
tags: [rl, policy-gradient, reinforce]
---

Bir ortam verildiğinde (ayrık / sürekli aksiyonlar, ufuk, ödül istatistikleri), output et:

1. Politika başlığı. Softmax (ayrık) veya Gaussian (sürekli) parametre sayılarıyla birlikte.
2. Baseline. Yok (saf), hareketli ortalama, öğrenilmiş `V̂(s)` veya A2C critic.
3. Varyans kontrolleri. Varsayılan açık reward-to-go, getiri normalizasyonu, gradyan kırpma değeri.
4. Entropi bonusu. Katsayı β ve azalma programı.
5. Batch boyutu. Güncelleme başına bölüm sayısı; on-policy veri tazeliği sözleşmesi.

Ufuk > 500 adım olan durumlarda baseline'sız REINFORCE'ı reddet. Softmax başlığıyla sürekli aksiyon kontrolünü reddet. `β = 0` ve gözlemlenen politika entropisi < 0.1 olan her çalışmayı entropi çökmüş olarak işaretle.
```

## Alıştırmalar

1. **Kolay.** 4×4 GridWorld'de doğrusal softmax politikası ile REINFORCE uygula. Baseline olmadan 1.000 bölüm eğit. Öğrenme eğrisini çiz; varyansı ölç (getirilerin std'si).
2. **Orta.** Hareketli ortalama baseline ekle. Tekrar eğit. Örnek verimliliği ve varyansı saf çalışmayla karşılaştır. Baseline, yakınsama adımlarını ne kadar azaltır?
3. **Zor.** Entropi bonusu `β · H(π)` ekle. `β ∈ {0, 0.01, 0.1, 1.0}` değerlerini tara. Son getiriyi ve politika entropisini çiz. Bu görevde en iyi nokta nerededir?

## Anahtar Terimler

| Terim | İnsanlar ne der | Gerçekte ne anlama gelir |
|------|-----------------|-----------------------|
| Policy gradient | "Politikayı doğrudan eğit" | `∇J(θ) = E[G · ∇ log π_θ(a\|s)]`; log-türev hilesinden türetilmiştir. |
| REINFORCE | "Orijinal PG algoritması" | Williams (1992); Monte Carlo getirileri ile log-politika gradyanının çarpımı. |
| Log-türev hilesi | "Score function estimator" | `∇P(τ;θ) = P(τ;θ) · ∇ log P(τ;θ)`; beklentilerin gradyanlarını hesaplanabilir hale getirir. |
| Baseline | "Varyans azaltma" | Herhangi bir `b(s)`, `G`'den çıkarılır; `E[b · ∇ log π] = 0` olduğu için tarafsızdır. |
| Reward-to-go | "Sadece gelecek getiriler sayar" | Tam `G_0` yerine `G_t^{from t}`; daha doğru ve daha düşük varyanslıdır. |
| Entropi bonusu | "Keşfi teşvik et" | `+β · H(π(·\|s))` terimi politikanın çökmesini önler. |
| On-policy | "Yeni gördüğün şeyin üzerinde eğit" | Gradyan beklentisi mevcut politika üzerindedir — eski veriyi doğrudan yeniden kullanamazsın. |
| Advantage | "Ortalama ne kadar iyi" | `A(s, a) = G(s, a) - V(s)`; baseline'lı REINFORCE'ın çarptığı işaretli niceliktir. |

## İleri Okuma

- [Williams (1992). Simple Statistical Gradient-Following Algorithms for Connectionist Reinforcement Learning](https://link.springer.com/article/10.1007/BF00992696) — orijinal REINFORCE makalesi.
- [Sutton et al. (2000). Policy Gradient Methods for Reinforcement Learning with Function Approximation](https://papers.nips.cc/paper_files/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html) — fonksiyon approximationsı ile modern policy gradient teoremi.
- [Sutton & Barto (2018). Böl. 13 — Policy Gradient Methods](http://incompleteideas.net/book/RLbook2020.pdf) — ders kitabı sunumu.
- [OpenAI Spinning Up — VPG / REINFORCE](https://spinningup.openai.com/en/latest/algorithms/vpg.html) — PyTorch kodlu pedagojik açıklama.
- [Peters & Schaal (2008). Reinforcement Learning of Motor Skills with Policy Gradients](https://homes.cs.washington.edu/~todorov/courses/amath579/reading/PolicyGradient.pdf) — varyans azaltma ve REINFORCE'u güven bölgesi ailesine (TRPO, PPO) bağlayan doğal gradyan görüşü.
