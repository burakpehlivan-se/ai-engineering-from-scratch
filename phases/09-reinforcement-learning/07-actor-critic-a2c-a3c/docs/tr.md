# Actor-Critic — A2C ve A3C

> REINFORCE gürültüldür. `V̂(s)` öğrenen bir critic ekle, getiriden çıkar ve aynı beklentiye sahip ama çok daha düşük varyanslı bir advantage elde edersin. Bu actor-critic'tir. A2C bunu senkron çalıştırır; A3C bunu iş parçacıkları arasında çalıştırır. İkisi de her modern deep-RL yönteminin zihinsel modelidir.

**Tür:** Build
**Diller:** Python
**Önkoşullar:** Phase 9 · 04 (TD Learning), Phase 9 · 06 (REINFORCE)
**Süre:** ~75 dakika

## Problem

Saf REINFORCE çalışır ama varyansı berbattır. Monte Carlo getirileri `G_t` bölümler arasında 10 kata kadar değişebilir. Bu gürültüyü `∇ log π` ile çarpmak ve ortalamasını almak, politikayı aynı mesafeye taşımak için binlerce bölüm gerektiren bir gradyan tahmincisi üretir; oysa DQN güncellemeleriyle çok daha az bölümde hareket ettirebilirsin.

Varyans ham getirilerin kullanılmasından gelir. Bir baseline `b(s_t)` — durumun herhangi bir fonksiyonu, öğrenilmiş değer dahil — çıkarırsan beklenti değişmez ve varyans düşer. En iyi uygulanabilir baseline `V̂(s_t)`'dir. Şimdi `∇ log π` ile çarpılan miktar *advantage*'dir:

`A(s, a) = G - V̂(s)`

Bir aksiyon, ortalamanın üstünde getiri ürettiyse iyidir; altındaysa kötüdür. Öğrenilmiş critic'li REINFORCE, *actor-critic*'tir. Critic, actor'a düşük varyanslı bir öğretmen verir. Bu, 2015'ten sonraki her deep-policy yönteminin temelidir (A2C, A3C, PPO, SAC, IMPALA).

## Kavram

![Actor-critic: politika ağı artı değer ağı, TD residual advantage olarak](../assets/actor-critic.svg)

**İki ağ, tek kayıp:**

- **Actor** `π_θ(a | s)`: politika. Örneklemeyle aksiyon alınır. Policy gradient ile eğitilir.
- **Critic** `V_φ(s)`: durumdan beklenen getiriyi tahmin eder. `(V_φ(s) - target)²`'i minimize etmek için eğitilir.

**Advantage.** İki standart form:

- *MC advantage:* `A_t = G_t - V_φ(s_t)`. Tarafsız, daha yüksek varyans.
- *TD advantage:* `A_t = r_{t+1} + γ V_φ(s_{t+1}) - V_φ(s_t)`. Yönlü (biased) (`V_φ` kullanır), çok daha düşük varyans. Ayrıca *TD residual* `δ_t` olarak adlandırılır.

**n-step advantage.** İkisi arasında interpolasyon:

`A_t^{(n)} = r_{t+1} + γ r_{t+2} + … + γ^{n-1} r_{t+n} + γ^n V_φ(s_{t+n}) - V_φ(s_t)`

`n = 1` saf TD'dir. `n = ∞` MC'dir. Çoğu uygulama Atari için `n = 5`, MuJoCo üzerindeki PPO için `n = 2048` kullanır.

**Generalized Advantage Estimation (GAE).** Schulman ve diğerleri (2016) tüm n-step advantage'lerin üstel ağırlıklı ortalamasını önerdi:

`A_t^{GAE} = Σ_{l=0}^{∞} (γλ)^l δ_{t+l}`

`λ ∈ [0, 1]` ile. `λ = 0` TD'dir (düşük varyans, yüksek bias). `λ = 1` MC'dir (yüksek varyans, tarafsız). `λ = 0.95`, 2026 varsayılanıdır — bias/varias ayarını istediğin noktaya gelene kadar ayarla.

**A2C: senkron advantage actor-critic.** `N` paralel ortamda `T` adım topla. Her adım için advantage hesapla. Birleştirilmiş batch'te actor ve critic'i güncelle. Tekrarla. A3C'nin daha basit, daha ölçeklenebilir kardeşidir.

**A3C: asenkron advantage actor-critic.** Mnih ve diğerleri (2016). `N` worker iş parçacığı oluştur, her biri bir ortam çalıştır. Her worker kendi rollout'unda yerel olarak gradyan hesaplar ve bunları asenkron olarak paylaşımlı bir parametre sunucusuna uygular. Replay buffer'a gerek yok — worker'lar farklı yörüngeler çalışarak birbirlerinin korelasyonunu bozar. A3C, CPU'larda büyük ölçekte eğitimin mümkün olduğunu kanıtladı. 2026'da GPU tabanlı A2C (batchlenmiş paralel ortamlar) baskındır çünkü GPU'lar büyük batch'ler ister.

**Birleşik kayıp.**

`L(θ, φ) = -E[ A_t · log π_θ(a_t | s_t) ]  +  c_v · E[(V_φ(s_t) - G_t)²]  -  c_e · E[H(π_θ(·|s_t))]`

Üç terim: policy-gradient kaybı, değer regresyonu, entropi bonusu. `c_v ~ 0.5`, `c_e ~ 0.01` kanonik başlangıç noktalarıdır.

## Kodu Yaz

### Adım 1: bir critic

Doğrusal critic `V_φ(s) = w · features(s)`, MSE ile güncellenir:

```python
def critic_update(w, x, target, lr):
    v_hat = dot(w, x)
    err = target - v_hat
    for j in range(len(w)):
        w[j] += lr * err * x[j]
    return v_hat
```

#### Açıklama

Tablo bazlı bir ortamda critic birkaç yüz bölümde yakınsar. Atari'de doğrusal critic'i paylaşımlı CNN gövdesi + değer başlığı ile değiştirin.

### Adım 2: n-step advantage

Uzunluğu `T` olan bir rollout ve bootstrap edilmiş son `V(s_T)` verildiğinde:

```python
def compute_advantages(rewards, values, gamma=0.99, lam=0.95, last_value=0.0):
    advantages = [0.0] * len(rewards)
    gae = 0.0
    for t in reversed(range(len(rewards))):
        next_v = values[t + 1] if t + 1 < len(values) else last_value
        delta = rewards[t] + gamma * next_v - values[t]
        gae = delta + gamma * lam * gae
        advantages[t] = gae
    returns = [a + v for a, v in zip(advantages, values)]
    return advantages, returns
```

#### Açıklama

`returns` critic hedefidir. `advantages`, `∇ log π` ile çarpılandır.

### Adım 3: birleşik güncelleme

```python
for step_i, (x, a, _r, probs) in enumerate(traj):
    adv = advantages[step_i]
    target_v = returns[step_i]

    # critic
    critic_update(w, x, target_v, lr_v)

    # actor
    for i in range(N_ACTIONS):
        grad_logpi = (1.0 if i == a else 0.0) - probs[i]
        for j in range(N_FEAT):
            theta[i][j] += lr_a * adv * grad_logpi * x[j]
```

#### Açıklama

On-policy, güncelleme başına bir rollout, actor ve critic için ayrı öğrenme hızları.

### Adım 4: paralelleştirme (A3C vs A2C)

- **A3C:** `N` iş parçacığı başlat. Her biri kendi ortamını ve kendi ileri yayılımını çalıştırır. Periyodik olarak gradyen güncellemelerini paylaşımlı bir master'a iter. Master'da kilit yok — yarışma sorun değil, sadece gürültü ekler.
- **A2C:** tek bir süreçte `N` ortam örneği çalıştır, gözlemleri `[N, obs_dim]` batch'ine istifle, toplu ileri yayılım, toplu geri yayılım. Daha yüksek GPU kullanımı, deterministik, daha kolay anlaşılır. 2026'da varsayılan budur.

Oyuncak kodumuz netlik için tek iş parçacıklıdır; batchlenmiş A2C'ye yeniden yazmak üç satır numpy'tır.

## Tuzaklar

- **Actor gradyanından önce critic bias'ı.** Critic rastgele ise, baseline bilgilendirici değildir ve saf gürültü üzerinde eğitiyorsun. Policy gradient'i açmadan önce critic'i birkaç yüz adım ısıt veya yavaş bir actor öğrenme hızı kullan.
- **Advantage normalizasyonu.** Advantage'leri batch başına sıfır ortalama/birim std'ye normalle. Eğitimi neredeyse sıfır maliyetle büyük ölçüde stabilize eder.
- **Paylaşımlı gövde.** Görüntü girdilerinde actor ve critic için paylaşımlı bir özellik çıkarıcı kullan. Ayrı başlıklar. Paylaşımlı özellikler her iki kayıptan da bedavaya yararlanır.
- **On-policy sözleşmesi.** A2C veriyi tam olarak bir güncelleme için yeniden kullanır. Daha fazlası gradyanınızı yönlü yapar (importance-sampling düzeltmesi PPO'nun eklediği şeydir).
- **Entropi çöküşü.** `c_e > 0` olmadan politika birkaç yüz güncellemede neredeyse deterministik hale gelir ve keşfi durdurur.
- **Ödül ölçeği.** Advantage büyüklükleri ödül ölçeğine bağlıdır. Tutarlı gradyan büyüklükleri için ödülleri normalleştir (örn., hareketli std ile bölme).

## Kullanım

A2C/A3C, 2026'da nadiren nihai seçimdir ama her şeyin üzerine inşa edildiği mimari budur:

| Yöntem | A2C ile ilişkisi |
|--------|----------------|
| PPO | Çoklu-epoch güncellemeleri için kırpılmış importance ratio'lu A2C |
| IMPALA | V-trace off-policy düzeltmeli A3C |
| SAC (Phase 9 · 07) | Soft-value critic'li off-policy A2C (bir sonraki ders) |
| GRPO (Phase 9 · 12) | Critic'siz A2C — group-relative advantage |
| DPO | Tercih sıralama kaybına sıkıştırılmış A2C, örnekleme yok |
| AlphaStar / OpenAI Five | Lig eğitimi + taklit ön-eğitimli A2C |

2026'da bir makalede "advantage" görürsen, actor-critic düşün.

## Ürün Haline Getir

`outputs/skill-actor-critic-trainer.md` olarak kaydet:

```markdown
---
name: actor-critic-trainer
description: Belirli bir ortam için A2C / A3C / GAE yapılandırması üret; advantage tahmini ve kayıp ağırlıklarını belirt.
version: 1.0.0
phase: 9
lesson: 7
tags: [rl, actor-critic, gae]
---

Bir ortam ve hesaplama bütçesi verildiğinde, output et:

1. Paralelleştirme. A2C (GPU batch'li) vs A3C (CPU asenkron) ve worker sayısı.
2. Rollout uzunluğu T. Güncelleme başına ortam başına adım sayısı.
3. Advantage tahmincisi. n-step veya GAE(λ); λ'yı belirtle.
4. Kayıp ağırlıkları. `c_v` (değer), `c_e` (entropi), gradyan kırpma.
5. Öğrenme hızları. Actor ve critic (ayrıysa).

Ufuk > 1000 olan ortamlarda tek-worker A2C'yi reddet (çok on-policy, çok yavaş). Advantage normalizasyonu olmadan gönderimi reddet. `c_e = 0` ve gözlemlenen entropi < 0.1 olan her çalışmayı entropi çökmüş olarak işaretle.
```

## Alıştırmalar

1. **Kolay.** 4×4 GridWorld'de MC advantage (`G_t - V(s_t)`) ile actor-critic eğit. Örnek verimliliğini Ders 06'daki hareketli ortalama baseline'lı REINFORCE ile karşılaştır.
2. **Orta.** TD-residual advantage'ye (`r + γ V(s') - V(s)`) geç. Advantage batch'lerinin varyansını ölç. Ne kadar düşer?
3. **Zor.** GAE(λ) uygula. `λ ∈ {0, 0.5, 0.9, 0.95, 1.0}` değerlerini tara. Son getiriyi örnek verimliliğine göre çiz. Bu görevde bias/variance en iyi noktası nerededir?

## Anahtar Terimler

| Terim | İnsanlar ne der | Gerçekte ne anlama gelir |
|------|-----------------|-----------------------|
| Actor | "Politika ağı" | `π_θ(a\|s)`, policy gradient ile güncellenir. |
| Critic | "Değer ağı" | `V_φ(s)`, getiriler / TD hedefleri üzerinde MSE regresyonuyla güncellenir. |
| Advantage | "Ortalama ne kadar iyi" | `A(s, a) = Q(s, a) - V(s)` veya tahmincileri. `∇ log π` için çarpan. |
| TD residual | "δ" | `δ_t = r + γ V(s') - V(s)`; tek adım advantage tahmini. |
| GAE | "İnterpolasyon düğmesi" | n-step advantage'lerin üstel ağırlıklı toplamı, `λ` ile parametrize edilir. |
| A2C | "Senkron actor-critic" | Ortamlar arasında batch'lenir; rollout başına bir gradyan adımı. |
| A3C | "Asenkron actor-critic" | Worker iş parçacıkları gradyanları paylaşımlı param sunucusuna iter. Orijinal makale; 2026'da daha az yaygın. |
| Bootstrap | "Ufukta V kullan" | Rollout'u kes, toplamı kapatmak için `γ^n V(s_{t+n})` ekle. |

## İleri Okuma

- [Mnih ve diğerleri (2016). Asynchronous Methods for Deep Reinforcement Learning](https://arxiv.org/abs/1602.01783) — A3C, orijinal asenkron actor-critic makalesi.
- [Schulman ve diğerleri (2016). High-Dimensional Continuous Control Using Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438) — GAE.
- [Sutton & Barto (2018). Böl. 13 — Actor-Critic Methods](http://incompleteideas.net/book/RLbook2020.pdf) — temeller; critic sinir ağı olduğunda Böl. 9 (fonksiyon approximation) ile eşleştir.
- [Espeholt ve diğerleri (2018). IMPALA](https://arxiv.org/abs/1802.01561) — V-trace off-policy düzeltmeli ölçeklenebilir dağıtık actor-critic.
- [OpenAI Baselines / Stable-Baselines3](https://stable-baselines3.readthedocs.io/) — okumaya değer üretim A2C/PPO uygulamaları.
- [Konda & Tsitsiklis (2000). Actor-Critic Algorithms](https://papers.nips.cc/paper/1786-actor-critic-algorithms) — iki-zamanlı actor-critic ayrıştırmasının temel yakınsama sonucu.
