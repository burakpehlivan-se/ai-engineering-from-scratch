# Monte Carlo Yöntemleri — Tam Bölümlerden Öğrenme

> Dynamic programming bir modele ihtiyaç duyar. Monte Carlo'dan başka bir şeye ihtiyaç duymaz: bölümlere. Politikayı çalıştırın, getirileri izleyin, ortalamalarını alın. RL'deki en basit fikir — ve her şeyin kilidini açan.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 9 · 01 (MDP'ler), Faz 9 · 02 (Dynamic Programming)
**Süre:** ~75 dakika

## Problem

Dynamic programming zariftir, ama her durum ve eylem için `P(s' | s, a)` sorgulayabileceğinizi varsayar. Gerçek dünyada neredeyse hiçbir şey böyle çalışmaz. Bir robot eklem torkundan sonra kamera pikselleri üzerindeki dağılımı analitik olarak hesaplayamaz. Bir fiyatlandırma algoritması her olası müşteri tepkisi üzerinde integre edemez. Bir LLM bir token'dan sonra tüm olası devamları numaralandıramaz.

Yalnızca ortamdan *örnekleme* yapabilmenize ihtiyaç duyan bir yönteme ihtiyacınız var. Politikayı çalıştırın. Bir yörünge `s_0, a_0, r_1, s_1, a_1, r_2, …, s_T` elde edin. Değerleri tahmin etmek için kullanın. Bu Monte Carlo'dur.

DP'den MC'ye geçiş felsefi olarak önemlidir: *bilinen model + kesin yedekten* *örneklenmiş rollout'lar + ortalamalanmış getiriye* geçiş yapıyoruz. Varyans atlar, ama uygulanabilirlik patlar. Bu dersten sonraki her RL algoritması — TD, Q-learning, REINFORCE, PPO, GRPO — özünde bir Monte Carlo tahminleyicisidir, bazen üzerine bindirilmiş (bootstrap) katmanlarıyla.

## Kavram

![Monte Carlo: rollout, getirileri hesapla, ortalamala; ilk-ziyaret vs her-ziyaret](../assets/monte-carlo.svg)

**Temel fikir, tek satırda:** `V^π(s) = E_π[G_t | s_t = s] ≈ (1/N) Σ_i G^{(i)}(s)` burada `G^{(i)}(s)` politika `π` altında `s`'ye yapılan ziyaretlerden gözlenen getirilerdir.

**İlk-ziyaret vs her-ziyaret MC.** `s` durumunu birden fazla kez ziyaret eden bir bölüm verildiğinde, ilk-ziyaret MC sadece ilk ziyaretin getirisini sayar; her-ziyaret MC tüm ziyaretleri sayar. Her ikisi de limite kadar unbiased'dır. İlk-ziyaret analiz etmesi daha basittir (iid örnekler). Her-ziyaret bölüm başına daha fazla veri kullanır ve pratikte genellikle daha hızlı yakınsar.

**Artımlı ortalama.** Tüm getirileri saklamak yerine, çalışan ortalamayı güncelleyin:

`V_n(s) = V_{n-1}(s) + (1/n) [G_n - V_{n-1}(s)]`

Yeniden düzenleyin: `V_new = V_old + α · (target - V_old)` burada `α = 1/n`. `1/n`'yi sabit adım aralığı `α ∈ (0, 1)` ile değiştirin ve `π`'deki değişiklikleri takip eden istasyonel olmayan bir MC tahminleyicisi elde edersiniz. Bu hamle, MC'den TD'ye ve her modern RL algoritmasına tüm sıçramadır.

**Keşif artık bir sorundur.** DP her durumu numaralandırarak dokunurdu. MC sadece politikanın ziyaret ettiği durumları görür. `π` deterministik ise, durum uzayının bütünlüklü bölgeleri hiç örneklenmez ve değer tahminleri sonsuza kadar sıfırda kalır. Tarihsel sırayla üç düzeltme:

1. **Keşfeden başlangıçlar (Exploring starts).** Her bölüme rastgele bir (s, a) çiftinden başlayın. Kapsamı garanti eder; pratikte gerçekçi değildir (bir robotu keyfi bir duruma "sıfırlayamazsınız").
2. **ε-greedy.** Mevcut Q'ya göre açgözlü davranın, ama `ε` olasılıkla rastgele bir eylem seçin. Asimptotik olarak tüm durum-eylem çiftleri örneklenir.
3. **Off-policy MC.** Davranış politikası `μ` altında veri toplayın, önem örnekleme (importance sampling) yoluyla hedef politika `π` hakkında öğrenin. Yüksek varyans, ama DQN gibi replay buffer yöntemlerine köprüdür.

**Monte Carlo Kontrolü.** Değerlendir → geliştir → değerlendir, tıpkı politika iterasyonu gibi, ama değerlendirme örnekleme tabanlıdır:

1. `π`'yi çalıştırın, bir bölüm elde edin.
2. Gözlenen getirilerden `Q(s, a)`'yi güncelleyin.
3. `π`'yi `Q`'ya göre ε-greedy yapın.
4. Tekrarlayın.

Koşullar altında (her çift sonsuz kez ziyaret edilir, `α` Robbins-Monro sağlar) olasılık 1 ile `Q*` ve `π*`'ye yakınsar.

## İnşa Et

### Adım 1: rollout → (s, a, r) listesi

```python
def rollout(env, policy, max_steps=200):
    trajectory = []
    s = env.reset()
    for _ in range(max_steps):
        a = policy(s)
        s_next, r, done = env.step(s, a)
        trajectory.append((s, a, r))
        s = s_next
        if done:
            break
    return trajectory
```

#### Açıklama
Model yok, sadece `env.reset()` ve `env.step(s, a)`. Gym ortamıyla aynı arayüz ama sadeleştirilmiş.

### Adım 2: getirileri hesapla (tertersweep)

```python
def returns_from(trajectory, gamma):
    returns = []
    G = 0.0
    for _, _, r in reversed(trajectory):
        G = r + gamma * G
        returns.append(G)
    return list(reversed(returns))
```

#### Açıklama
Tek geçiş, `O(T)`. Ters rekürans `G_t = r_{t+1} + γ G_{t+1}` yeniden toplamayı önler.

### Adım 3: ilk-ziyaret MC değerlendirmesi

```python
def mc_policy_evaluation(env, policy, episodes, gamma=0.99):
    V = defaultdict(float)
    counts = defaultdict(int)
    for _ in range(episodes):
        trajectory = rollout(env, policy)
        returns = returns_from(trajectory, gamma)
        seen = set()
        for t, ((s, _, _), G) in enumerate(zip(trajectory, returns)):
            if s in seen:
                continue
            seen.add(s)
            counts[s] += 1
            V[s] += (G - V[s]) / counts[s]
    return V
```

#### Açıklama
Üç satır işi yapar: ilk ziyarette durumu görüldü olarak işaretle, sayacı artır, çalışan ortalamayı güncelle.

### Adım 4: ε-greedy MC kontrolü (on-policy)

```python
def mc_control(env, episodes, gamma=0.99, epsilon=0.1):
    Q = defaultdict(lambda: {a: 0.0 for a in ACTIONS})
    counts = defaultdict(lambda: {a: 0 for a in ACTIONS})

    def policy(s):
        if random() < epsilon:
            return choice(ACTIONS)
        return max(Q[s], key=Q[s].get)

    for _ in range(episodes):
        trajectory = rollout(env, policy)
        returns = returns_from(trajectory, gamma)
        seen = set()
        for (s, a, _), G in zip(trajectory, returns):
            if (s, a) in seen:
                continue
            seen.add((s, a))
            counts[s][a] += 1
            Q[s][a] += (G - Q[s][a]) / counts[s][a]
    return Q, policy
```

#### Açıklama
Eylem-değerlerini gözlenen getirilerden günceller.

### Adım 5: DP altın standardıyla karşılaştır

`V^π` MC tahmininiz bölümler → ∞ olduğunda Ders 02'deki DP sonucuyla uyuşmalıdır. Pratikte: 4×4 GridWorld'de 50.000 bölüm DP cevabına `~0.1` yakın getirir.

## Tuzaklar

- **Sonsuz bölümler.** MC bölümlerin *sonlanmasını* gerektirir. Politikanız sonsuza kadar döngü yapabiliyorsa, `max_steps`'i sınırlayın ve sınırlamayı örtük başarısızlık olarak kabul edin. Rastgele politikayla GridWorld düzenli olarak zaman aşımına uğrar — bu normal, sadece doğru saydığınızdan emin olun.
- **Varyans.** MC tam getirileri kullanır. Uzun bölümlerde varyans çok büyüktür — sonda bir şanssız ödül `V(s_0)`'yi aynı miktarda kaydırır. TD yöntemleri (Ders 04) bootstrap ile bunu keser.
- **Durum kapsamı.** Taze Q üzerinde bağlarla açgözlü MC sadece bir eylemi deneyecektir. *Keşfetmeniz* gerekir (ε-greedy, keşfeden başlangıçlar, UCB).
- **İstasyonel olmayan politikalar.** `π` değişirse (MC kontrolünde olduğu gibi), eski getiriler farklı bir politikadandır. Sabit-α MC bunu ele alır; örnek-ortalama MC ele almaz.
- **Off-policy önem örnekleme.** Ağırlıklar `π(a|s)/μ(a|s)` bir yörünge boyunca çarpılır. Varyans ufukla patlar. Karar-ağırlıklı IS ile sınırlayın veya TD'ye geçin.

## Kullan

2026'da Monte Carlo yöntemlerinin rolü:

| Kullanım durumu | Neden MC |
|----------|--------|
| Kısa ufuklu oyunlar (21, poker) | Bölümler doğal olarak sonlanır; getiriler temizdir. |
| Kaydedilmiş bir politikanın offline değerlendirmesi | Saklanan yörüngelegenler üzerinde ortalama diskontlu getiri. |
| Monte Carlo Tree Search (AlphaZero) | Ağaç yapraklarından MC rollout'ları seçimi yönlendirir. |
| LLM RL değerlendirmesi | Verilen politika için örneklene tamamlamalar üzerinde ortalama ödül hesapla. |
| PPO'da taban tahmini | Avantaj hedefi `A_t = G_t - V(s_t)` bir MC `G_t` kullanır. |
| RL öğretimi | Gerçekte çalışan en basit algoritma — çekirdeği görmek için bootstrap'ı çıkarın. |

Modern deep-RL algoritmaları (PPO, SAC) `n`-adım getirileri veya GAE aracılığıyla saf MC (tam getiriler) ve saf TD (tek adım bootstrap) arasında enterpolasyon yapar. Her iki uç da aynı tahminleyicinin örnekleridir.

## Gemileştir

`outputs/skill-mc-evaluator.md` olarak kaydedin:

```markdown
---
name: mc-evaluator
description: Evaluate a policy via Monte Carlo rollouts and produce a convergence report with DP-comparison if available.
version: 1.0.0
phase: 9
lesson: 3
tags: [rl, monte-carlo, evaluation]
---

Given an environment (episodic, with reset+step API) and a policy, output:

1. Method. First-visit vs every-visit MC. Reason.
2. Episode budget. Target number, variance diagnostic, expected standard error.
3. Exploration plan. ε schedule (if needed) or exploring starts.
4. Gold-standard comparison. DP-optimal V* if tabular; otherwise a bound from a Q-learning / PPO baseline.
5. Termination check. Max-step cap, timeouts, handling of non-terminating trajectories.

Refuse to run MC on non-episodic tasks without a finite horizon cap. Refuse to report V^π estimates from fewer than 100 episodes per state for tabular tasks. Flag any policy with zero-variance actions as an exploration risk.
```

## Alıştırmalar

1. **Kolay.** 4×4 GridWorld'de düzgün rastgele politikanın ilk-ziyaret MC değerlendirmesini uygulayın. 10.000 bölüm çalıştırın. `V(0,0)`'yi bölüm sayısının fonksiyonu olarak DP cevabına karşı çizin.
2. **Orta.** `ε ∈ {0.01, 0.1, 0.3}` ile ε-greedy MC kontrolünü uygulayın. 20.000 bölümden sonra ortalama getiriyi karşılaştırın. Eğri nasıl görünüyor? Önyargı- varyans uzlaşması nerede?
3. **Zor.** Önem örnekleme ile *off-policy* MC uygulayın: düzgün rastgele politika `μ` altında veri toplayın, deterministik en iyi politika `π` için `V^π`'yi tahmin edin. Düz IS vs karar-ağırlıklı IS vs ağırlıklı IS'i karşılaştırın. Hangisi en düşük varyansa sahip?

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Monte Carlo | "Rastgele örnekleme" | Dağılımdan iid örneklerin ortalamasını alarak beklentileri tahmin etme. |
| Getiri `G_t` | "Gelecek ödül" | `t` adımından bölüm sonuna kadar diskontlu ödüllerin toplamı: `Σ_{k≥0} γ^k r_{t+k+1}`. |
| İlk-ziyaret MC | "Her durumu bir kez say" | Bir bölümdeki ilk ziyaret yalnızca değer tahminine katkıda bulunur. |
| Her-ziyaret MC | "Tüm ziyaretleri kullan" | Her ziyaret katkıda bulunur; biraz biased ama daha örnek-verimli. |
| ε-greedy | "Keşif gürültüsü" | `1-ε` olasılıkla açgözlü eylem seç; `ε` olasılıkla rastgele eylem. |
| Önem örnekleme | "Yanlış dağılımdan örnekleme için düzeltme" | `π(a\|s)/μ(a\|s)` çarpımlarıyla getirileri yeniden ağırlıklandırarak `μ` verisinden `V^π`'yi tahmin etme. |
| On-policy | "Kendi verimden öğren" | Hedef politika = davranış politika. Vanilla MC, PPO, SARSA. |
| Off-policy | "Başkasının verisinden öğren" | Hedef politika ≠ davranış politika. Importance-sampled MC, Q-learning, DQN. |

## İleri Okuma

- [Sutton & Barto (2018). Bölüm 5 — Monte Carlo Yöntemleri](http://incompleteideas.net/book/RLbook2020.pdf) — kanonik ele alınış.
- [Singh & Sutton (1996). Reinforcement Learning with Replacing Eligibility Traces](https://link.springer.com/article/10.1007/BF00114726) — ilk-ziyaret vs her-ziyaret analizi.
- [Precup, Sutton, Singh (2000). Eligibility Traces for Off-Policy Policy Evaluation](http://incompleteideas.net/papers/PSS-00.pdf) — off-policy MC ve varyans kontrolü.
- [Mahmood et al. (2014). Weighted Importance Sampling for Off-Policy Learning](https://arxiv.org/abs/1404.6362) — modern düşük-varyanslı IS tahminleyicileri.
- [Tesauro (1995). TD-Gammon, A Self-Teaching Backgammon Program](https://dl.acm.org/doi/10.1145/203330.203343) — MC/TD kendi kendine oynamanın (self-play) süperinsan düzeyine yakınsamasının ilk büyük ölçekli ampirik gösterimi; bu fazın ikinci yarısındaki her dersin kavramsal öncüsü.
