# Proximal Policy Optimization (PPO)

> A2C her rollout'u bir güncellemeden sonra atar. PPO, policy gradient'i kırpılmış bir importance ratio'ya sarar; böylece aynı veri üzerinde 10+ epoch çalışabilirsin ve politika patlamaz. Schulman ve diğerleri (2017). 2026'da hala varsayılan policy gradient algoritmasıdır.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 9 · 06 (REINFORCE), Faz 9 · 07 (Actor-Critic)
**Süre:** ~75 dakika

## Problem

A2C (Ders 07) on-policy'dir: gradyan `E_{π_θ}[A · ∇ log π_θ]`, *mevcut* `π_θ`'dan örneklenebilen veri gerektirir. Bir güncelleme yaparsın ve `π_θ` değişir; kullandığın veri artık off-policy'dir. Yeniden kullanırsan gradyanın yönlüdür (biased).

Rollout'lar pahalıdır. Atari'de 8 ortam × 128 adım üzerinde bir rollout, 1024 geçiş ve bir düzine saniye ortam zamanı demektir. Bunu bir gradyan adımından sonra atmak israftır.

Trust Region Policy Optimization (TRPO, Schulman 2015) ilk düzeltmeydi: her güncellemeyi, eski ve yeni politika arasındaki KL ıraklığının `δ` altında kalacak şekilde sınırla. Teorik olarak temiz, ama güncelleme başına eşlikli-gradient çözümü gerektirir. 2026'da kimse TRPO çalıştırmaz.

PPO (Schulman ve diğerleri 2017), sıkı güven bölgesi kısıtını basit bir kırpılmış amaçla değiştirir. Ekstra bir kod satırı. Rollout başına on epoch. Eşlikli gradient yok. Yeterli teorik garantiler. Dokuz yıl sonra hala MuJoCo'dan RLHF'ye kadar her şey için varsayılan policy gradient algoritmasıdır.

## Kavram

![PPO kırpılmış surrogate amacı: ratio kırpma 1 ± ε](../assets/ppo.svg)

**Importance oranı.**

`r_t(θ) = π_θ(a_t | s_t) / π_{θ_old}(a_t | s_t)`

Bu, veriyi toplayan politikaya kıyasla yeni politikanın olasılık oranıdır. `r_t = 1` değişim yok demektir. `r_t = 2` ise yeni politikanın `a_t`'yi alma olasılığının eskinin iki katı demektir.

**Kırpılmış surrogate.**

`L^{CLIP}(θ) = E_t [ min( r_t(θ) A_t, clip(r_t(θ), 1-ε, 1+ε) A_t ) ]`

İki terim:

- Advantage `A_t > 0` ise ve oran `1 + ε`'nin üzerine büyümeye çalışırsa, kırpma gradyanı düzleştirir — iyi bir aksiyonu eski olasılığın `+ε` üzerine itme.
- Advantage `A_t < 0` ise ve oran `1 - ε`'nin üzerine büyümeye çalışırsa (kötü bir aksiyonu kırpılmış düşüşüne göre daha olası hale getireceğiz demektir), kırpma gradyanı sınırlar — kötü bir aksiyonu `-ε`'nin altına itme.

`min`, diğer yönü de ele alır: oran *yararlı* yönde hareket ettiyse, gradyanı yine de alırsın (sana zarar verecek tarafta kırpma yoktur).

Tipik `ε = 0.2`. Amacı `r_t`'nin fonksiyonu olarak çizin: "iyi tarafta" düz bir çatılı ve "kötü tarafta" düz bir tabanlı parçalı-lineer bir fonksiyondur.

**Tam PPO kaybı.**

`L(θ, φ) = L^{CLIP}(θ) - c_v · (V_φ(s_t) - V_t^{target})² + c_e · H(π_θ(·|s_t))`

A2C ile aynı actor-critic yapısı. Üç katsayı, genellikle `c_v = 0.5`, `c_e = 0.01`, `ε = 0.2`.

**Eğitim döngüsü.**

1. `N` paralel ortamda `T`'şer adım boyunca `N × T` geçiş topla.
2. Advantage'leri hesapla (GAE), bunları sabit olarak dondur.
3. `π_{θ_old}`'u mevcut `π_θ`'nın anlık görüntüsü olarak dondur.
4. `K` epoch için, `(s, a, A, V_target, log π_old(a|s))`'nin her minibatch'i için:
   - `r_t(θ) = exp(log π_θ(a|s) - log π_old(a|s))` hesapla.
   - `L^{CLIP}` + değer kaybı + entropi uygula.
   - Gradyan adımı at.
5. Rollout'u at. 1. adıma dön.

`K = 10` ve 64 boyutunda minibatch'ler standart bir hiperparametre kümesidir. PPO dayanıklıdır: kesin sayılar nadiren ±%50 içinde önemli değişir.

**KL-ceza varyantı.** Orijinal makale, adaptif KL cezası kullanan bir alternatif önerdi: `L = L^{PG} - β · KL(π_θ || π_old)`; `β`, gözlenen KL'ye göre ayarlanır. Kırpılmış versiyon baskın hale geldi; KL varyantı RLHF'de hayatta kalır (referans politikaya KL, her zaman istediğiniz ayrı bir kısıttır).

## İnşa Et

### Adım 1: rollout zamanında `log π_old(a | s)` yakala

```python
for step in range(T):
    probs = softmax(logits(theta, state_features(s)))
    a = sample(probs, rng)
    s_next, r, done = env.step(s, a)
    buffer.append({
        "s": s, "a": a, "r": r, "done": done,
        "v_old": value(w, state_features(s)),
        "log_pi_old": log(probs[a] + 1e-12),
    })
    s = s_next
```

#### Açıklama

Anlık görüntü rollout zamanında bir kez alınır. Güncelleme epoch'ları sırasında değişmez.

### Adım 2: GAE advantage'lerini hesapla (Ders 07)

A2C ile aynı. Batch boyunca normalleştir.

### Adım 3: kırpılmış surrogate güncelleme

```python
for _ in range(K_EPOCHS):
    for mb in minibatches(buffer, size=64):
        for rec in mb:
            x = state_features(rec["s"])
            probs = softmax(logits(theta, x))
            logp = log(probs[rec["a"]] + 1e-12)
            ratio = exp(logp - rec["log_pi_old"])
            adv = rec["advantage"]
            surrogate = min(
                ratio * adv,
                clamp(ratio, 1 - EPS, 1 + EPS) * adv,
            )
            # backprop -surrogate, add value loss, subtract entropy
            grad_logpi = onehot(rec["a"]) - probs
            if (adv > 0 and ratio >= 1 + EPS) or (adv < 0 and ratio <= 1 - EPS):
                pg_grad = 0.0  # clipped
            else:
                pg_grad = ratio * adv
            for i in range(N_ACTIONS):
                for j in range(N_FEAT):
                    theta[i][j] += LR * pg_grad * grad_logpi[i] * x[j]
```

#### Açıklama

"Kırpılmış → sıfır gradyan" kalıbı PPO'nun kalbidir. Yeni politika yararlı yönde çoktan fazla kaydıysa, güncelleme durur.

### Adım 4: değer ve entropi

Critic hedefine standart MSE, actor'a entropi bonusu ekle; A2C ile aynı.

### Adım 5: tanılamalar

Her güncellemede izlenmesi gereken üç şey:

- **Ortalama KL** `E[log π_old - log π_θ]`. `[0, 0.02]` arasında kalmalıdır. `0.1`'in üzerine çıkarsa, `K_EPOCHS` veya `LR`'yi azalt.
- **Kırpma oranı** — oranının `[1-ε, 1+ε]` dışında kaldığı örneklerin oranı. `~0.1-0.3` olmalıdır. `~0` ise kırpma hiç tetiklenmiyor demektir → `LR` veya `K_EPOCHS` artır. `~0.5+` ise rollout'u aşırı uyduruyorsun demektir → düşür.
- **Açıklanan varyans** `1 - Var(V_target - V_pred) / Var(V_target)`. Critic kalite metriğidir. Critic öğrenirken 1'e doğru tırmanmalıdır.

## Tuzaklar

- **Kırpma katsayısı yanlış ayarlı.** `ε = 0.2` fiili standarttır. `0.1`'e gitmek güncellemeleri çok çekingen yapar; `0.3+` istikrarsızlık davet eder.
- **Çok fazla epoch.** `K > 20` genellikle politikanın `π_old`'dan çok uzaklaşması nedeniyle istikrarsızlaştırır. Özellikle büyük ağlar için epoch'ları sınırla.
- **Ödül normalizasyonu yok.** Büyük ödül ölçekleri kırpma aralığını yerler. Avantaj hesaplamadan önce ödülleri normalleştir (hareketli std).
- **Advantage normalizasyonunu unutma.** Batch başına sıfır ortalama/birim std normalizasyonu standarttır. Atlamak çoğu benchmark'ta PPO'yu bozar.
- **Öğrenme hızı azaltılmamış.** PPO, lineer LR azalmasından faydalanır. Sabit LR genellikle daha kötüdür.
- **Importance oranı matematik hataları.** Sayısal kararlılık için her zaman `exp(log_new - log_old)` kullan, `new / old` değil.
- **Yanlış gradyan işareti.** Surrogate'u *maksimize* et = `-L^{CLIP}`'i *minimize* et. Çevrilmiş işareti en yaygın PPO hatasıdır.

## Kullanım

PPO, 2026'da şaşırtıcı sayıda alanda varsayılan RL algoritmasıdır:

| Kullanım alanı | PPO varyantı |
|----------|-------------|
| MuJoCo / robotik kontrol | Gaussian politikalı PPO, GAE(0.95) |
| Atari / ayrık oyunlar | Kategorik politikalı PPO, 128 adımlık dönen rollout'lar |
| LLM'ler için RLHF | Referans modele KL cezalı PPO, yanıt sonunda RM'den ödül |
| Büyük ölçekli oyun ajanları | IMPALA + PPO (AlphaStar, OpenAI Five) |
| Muhakeme LLM'leri | GRPO (Ders 12) — criticsiz PPO varyantı |
| Sadece tercih verileri | DPO — PPO+KL'nin kapalı formda sıkıştırılması, çevrimiçi örnekleme yok |

PPO *kayıp şekli* — kırpılmış surrogate + değer + entropi — DPO, GRPO ve neredeyse tüm RLHF hatlarının iskeletidir.

## Gemileştir

`outputs/skill-ppo-trainer.md` olarak kaydet:

```markdown
---
name: ppo-trainer
description: Belirli bir ortam için PPO eğitim yapılandırması ve tanı planı üret.
version: 1.0.0
phase: 9
lesson: 8
tags: [rl, ppo, policy-gradient]
---

Bir ortam ve eğitim bütçesi verildiğinde, output et:

1. Rollout boyutu. `N` ortam × `T` adım.
2. Güncelleme programı. `K` epoch, minibatch boyutu, LR programı.
3. Surrogate parametreleri. `ε` (kırpma), `c_v`, `c_e`, advantage normalizasyonu açık.
4. Advantage. Açıkça belirtilmiş `γ` ve `λ` ile GAE(`λ`).
5. Tanı planı. KL, kırpma oranı, uyarılarla birlikte açıklanan varyans eşikleri.

`K > 30` veya `ε > 0.3`'ü reddet (güvensiz güven bölgesi). Advantage normalizasyonu veya KL/kırpma izleme olmadan herhangi bir PPO çalışmasını reddet. Sürekli 0.4'ün üzerinde kırpma oranını sapma olarak işaretle.
```

## Alıştırmalar

1. **Kolay.** 4×4 GridWorld'de `ε=0.2, K=4` ile PPO çalıştır. Eşleştirilmiş ortam adımlarında A2C (rollout başına bir epoch) ile örnek verimliliğini karşılaştır.
2. **Orta.** `K ∈ {1, 4, 10, 30}` değerlerini tara. Getiriyi ortam adımlarına göre çiz ve güncelleme başına ortalama KL'yi izle. Bu görevde KL hangi `K`'da patlar?
3. **Zor.** Kırpılmış surrogate'u adaptif KL cezasıyla değiştir (`KL > 2·target` ise `β` ikiye katla, `KL < target/2` ise yarıya indir). Son getiri, stabilite ve kırpmasızlığı karşılaştır.

## Anahtar Terimler

| Terim | İnsanlar ne der | Gerçekte ne anlama gelir |
|------|-----------------|-----------------------|
| Importance oranı | "r_t(θ)" | `π_θ(a\|s) / π_old(a\|s)`; veriyi toplayan politikadan sapma. |
| Kırpılmış surrogate | "PPO'nun ana hilesi" | `min(r·A, clip(r, 1-ε, 1+ε)·A)`; yararlı tarafta kırpma sonrası düz gradyan. |
| Trust region | "TRPO / PPO niyeti" | Her güncellemenin KL'sini kısıtla, monoton iyileşmeyi garanti altına al. |
| KL cezası | "Yumuşak güven bölgesi" | Alternatif PPO: `L - β · KL(π_θ \|\| π_old)`. Adaptif `β`. |
| Kırpma oranı | "Ne sıklıkla kırpma tetikleniyor" | Tanısal — 0.1-0.3 olmalıdır; dışarıda olmak yanlış ayar demektir. |
| Çoklu-epoch eğitimi | "Veri yeniden kullanımı" | Her rollout'ta K epoch; varyans bedeli örnek verimliliğiyle takas edilir. |
| On-policy'e yakın | "Çoğunlukla on-policy" | PPO nominal olarak on-policy'dir ama K>1 epoch biraz off-policy veriyi güvenli kullanır. |
| PPO-KL | "Diğer PPO" | KL-ceza varyantı; KL-to-reference zaten bir kısıt olan RLHF'de kullanılır. |

## İleri Okuma

- [Schulman ve diğerleri (2017). Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347) — makale.
- [Schulman ve diğerleri (2015). Trust Region Policy Optimization](https://arxiv.org/abs/1502.05477) — TRPO, PPO'nun öncüsü.
- [Andrychowicz ve diğerleri (2021). What Matters In On-Policy RL? A Large-Scale Empirical Study](https://arxiv.org/abs/2006.05990) — her PPO hiperparametresi ablatılmış.
- [Ouyang ve diğerleri (2022). Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) — InstructGPT; RLHF'deki PPO tarifi.
- [OpenAI Spinning Up — PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html) — PyTorch ile temiz modern açıklama.
- [CleanRL PPO uygulaması](https://github.com/vwxyzjn/cleanrl) — birçok makale tarafından kullanılan referans tek dosyalı PPO.
- [Hugging Face TRL — PPOTrainer](https://huggingface.co/docs/trl/main/en/ppo_trainer) — dil modelleri üzerinde PPO'nun üretim tarifi; Ders 09 (RLHF) ile birlikte okunmalı.
- [Engstrom ve diğerleri (2020). Implementation Matters in Deep Policy Gradients](https://arxiv.org/abs/2005.12729) — "37 kod düzeyinde optimizasyon" makalesi; hangi PPO hileleri taşıyıcı ve hangileri söylence.
