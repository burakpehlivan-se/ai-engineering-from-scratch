# Dynamic Programming — Politika İterasyonu ve Değer İterasyonu

> Dynamic programming, hile yapan RL'dir. Zaten geçiş ve ödül fonksiyonlarını bilirsiniz; sadece `V` veya `π` durana kadar Bellman denklemini yineler茨. Her örnekleme tabanlı yöntemin ulaşmaya çalıştığı kriter budur.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 9 · 01 (MDP'ler)
**Süre:** ~75 dakika

## Problem

Bilinen bir modele sahip bir MDP'niz var: her durum-eylem çifti için `P(s' | s, a)` ve `R(s, a, s')` sorgulayabilirsiniz. Bir envanter yöneticisi talep dağılımını bilir. Bir masa oyunu deterministik geçişlere sahiptir. Bir gridworld dört satır Python'dur. Bir *modeliniz* var.

Model-free RL (Q-learning, PPO, REINFORCE) modeliniz olmadığında icat edilmiştir — ortamdan yalnızca örnekleme yapabilirsiniz. Ama bir modeliniz varsa, daha hızlı ve daha iyi yöntemler vardır: dynamic programming. Bellman bunları 1957'de tasarladı. Hala doğruluğu tanımlar: insanlar "bu MDP için en iyi politika" dediğinde, DP'nin döndüreceği politikayı kastediyorlar.

2026'da bunlara üç nedenle ihtiyacınız var. Birincisi, RL araştırmasındaki tablolar arası her ortam (GridWorld, FrozenLake, CliffWalking) altın standart politikayı üretmek için DP ile çözülür. İkincisi, kesin değerler örnekleme yöntemlerinizi *hata ayıklamanızı* sağlar: Q-learning'in `V*(s_0)` için DP cevabıyla %30 uyuşmazsa, Q-learning'inizde bir hata var demektir. Üçüncüsü, modern offline RL ve planlama yöntemleri (MCTS, AlphaZero'nun araması, Faz 9 · 10'da model-tabanlı RL) hepsi bir öğrenilmiş veya verilen model üzerinde Bellman yedeği yineler.

## Kavram

![Politika iterasyonu ve değer iterasyonu, yan yana](../assets/dp.svg)

**İki algoritma, ikisi de Bellman üzerinde sabit nokta iterasyonu.**

**Politika iterasyonu (Policy iteration).** Politika değişmeyene kadar iki adımı değiştirerek sürdürür.

1. *Değerlendirme:* Verilen politika `π`, `V(s) ← Σ_a π(a|s) Σ_{s',r} P(s',r|s,a) [r + γ V(s')]` ifadesini yakınsayana kadar tekrarlayarak `V^π` hesaplanır.
2. *İyileştirme:* Verilen `V^π`, `π`'yi `V^π`'ye göre açgözlü (greedy) yapılır: `π(s) ← argmax_a Σ_{s',r} P(s',r|s,a) [r + γ V(s')]`.

Yakınsama garantilidir çünkü (a) her iyileştirme adımı `π`'yi aynı tutar veya bazı durumlar için `V^π`'yi kesinlikle artırır, (b) deterministik politikaların uzayı sonludur. Genellikle büyük durum uzaylarında bile ~5–20 dış iterasyonda yakınsar.

**Değer iterasyonu (Value iteration).** Değerlendirmeyi ve iyileştirmeyi tek bir taramada birleştirir. Bellman *eniyilik* denklemini uygulayın:

`V(s) ← max_a Σ_{s',r} P(s',r|s,a) [r + γ V(s')]`

`max_s |V_{new}(s) - V(s)| < ε` olana kadar tekrarlayın. Sonda açgözlü eylemi alarak politikayı çıkarın. İterasyon başına kesinlikle daha hızlıdır — iç değerlendirme döngüsü yoktur — ama genellikle yakınsamak için daha fazla iterasyon gerektirir.

**Genelleştirilmiş politika iterasyonu (GPI).** Birleştirici çerçevedir. Değer fonksiyonu ve politika çift yönlü bir iyileştirme döngüsünde kilitlenmiştir; her iki tarafı da karşılıklı tutarlılığa götüren herhangi bir yöntem (asenkron değer iterasyonu, değiştirilmiş politika iterasyonu, Q-learning, actor-critic, PPO) GPI'nin bir örneğidir.

**Neden `γ < 1` önemlidir.** Bellman operatörü sup-norm'da bir `γ`-sözleşmesidir: `||T V - T V'||_∞ ≤ γ ||V - V'||_∞`. Sözleşme benzersiz sabit nokta ve geometrik yakınsama anlamına gelir. `γ < 1`'i bırakırsanız garantiden mahrum kalırsınız — sonlu bir ufuk veya emici bir sonlanma durumuna ihtiyacınız vardır.

## İnşa Et

### Adım 1: GridWorld MDP modelini oluştur

Ders 01'deki aynı 4×4 GridWorld'ü kullanın. Stokastik bir varyant ekliyoruz: `0.1` olasılıkla rastgele dik bir yöne kayar.

```python
SLIP = 0.1

def transitions(state, action):
    if state == TERMINAL:
        return [(state, 0.0, 1.0)]
    outcomes = []
    for direction, prob in action_probs(action):
        outcomes.append((apply_move(state, direction), -1.0, prob))
    return outcomes
```

#### Açıklama
`transitions(s, a)` `(s', r, p)` listesi döndürür. Bu tüm modeldir.

### Adım 2: politika değerlendirmesi

Verilen bir politika `π(s) = {action: prob}` için, `V` değişmeyene kadar Bellman denklemini yineleyin:

```python
def policy_evaluation(policy, gamma=0.99, tol=1e-6):
    V = {s: 0.0 for s in states()}
    while True:
        delta = 0.0
        for s in states():
            v = sum(pi_a * sum(p * (r + gamma * V[s_prime])
                              for s_prime, r, p in transitions(s, a))
                   for a, pi_a in policy(s).items())
            delta = max(delta, abs(v - V[s]))
            V[s] = v
        if delta < tol:
            return V
```

#### Açıklama
Politikanın her durumdaki beklenen diskontlu getirisini hesaplar.

### Adım 3: politika iyileştirmesi

`π`'yi `V`'ye göre açgözlü politikayla değiştirin. `π` değişmediyse, döndürün — en optimumdasınız.

```python
def policy_improvement(V, gamma=0.99):
    new_policy = {}
    for s in states():
        best_a = max(
            ACTIONS,
            key=lambda a: sum(p * (r + gamma * V[s_prime])
                              for s_prime, r, p in transitions(s, a)),
        )
        new_policy[s] = best_a
    return new_policy
```

#### Açıklama
Her durum için en yüksek beklenen getiriyi veren eylemi seçer.

### Adım 4: birleştirin

```python
def policy_iteration(gamma=0.99):
    policy = {s: "up" for s in states()}   # rastgele başlangıç
    for _ in range(100):
        V = policy_evaluation(lambda s: {policy[s]: 1.0}, gamma)
        new_policy = policy_improvement(V, gamma)
        if new_policy == policy:
            return V, policy
        policy = new_policy
```

#### Açıklama
Politika değerlendirme ve iyileştirmeyi alternatif olarak çalıştırır.

### Adım 5: değer iterasyonu (tek döngülü versiyon)

```python
def value_iteration(gamma=0.99, tol=1e-6):
    V = {s: 0.0 for s in states()}
    while True:
        delta = 0.0
        for s in states():
            v = max(sum(p * (r + gamma * V[s_prime])
                       for s_prime, r, p in transitions(s, a))
                   for a in ACTIONS)
            delta = max(delta, abs(v - V[s]))
            V[s] = v
        if delta < tol:
            break
    policy = policy_improvement(V, gamma)
    return V, policy
```

#### Açıklama
Aynı sabit nokta, daha az kod satırı.

## Tuzaklar

- **Sonlanma durumlarını unutmak.** Bellman'ı emici bir duruma uygularsanız, hiçbir şeyi değiştirmeyen "en iyi eylemi" yine de seçer. `if s == terminal: V[s] = 0` ile koruyun.
- **Sup-norm vs L2 yakınsaması.** `max |V_new - V|` kullanın, ortalama değil. Teorik garanti sup-norm üzerindedir.
- **Yerinde vs senkron güncellemeler.** `V[s]`'yi yerinde güncellemek (Gauss-Seidel) ayrı bir `V_new` sözlüğünden (Jacobi) daha hızlı yakınsar. Üretim kodu yerinde güncellemeyi kullanır.
- **Politika bağları.** İki eylemin eşit Q-değeri varsa, `argmax` her iterasyonda bağları farklı kırabilir, "politika sabit" kontrolünün salınmasına neden olur. Kararlı bir bağ kırıcı kullanın (sabit sıradaki ilk eylem).
- **Durum uzayı patlaması.** DP tarama başına `O(|S| · |A|)`'dir. ~10⁷ duruma kadar çalışır. Onun ötesinde fonksiyon yaklaşımına (Faz 9 · 05 ve sonrası) ihtiyacınız vardır.

## Kullan

2026'da DP, doğruluk tabanı ve planlayıcıların iç döngüsüdür:

| Kullanım durumu | Yöntem |
|----------|--------|
| Küçük bir tablo MDP'sini tam olarak çöz | Değer iterasyonu (daha basit) veya politika iterasyonu (daha az dış iterasyon) |
| Bir Q-learning / PPO uygulamasını doğrula | Oyuncak bir ortamda DP-optimal V* ile karşılaştır |
| Model-tabanlı RL (Faz 9 · 10) | Öğrenilmiş geçiş modeli üzerinde Bellman yedeği |
| AlphaZero / MuZero'da planlama | Monte Carlo Tree Search = asenkron Bellman yedeği |
| Offline RL (CQL, IQL) | Muhafazakâr Q-iterasyonu — OOD eylemlere ceza ile DP |

Birisi "en iyi değer fonksiyonu" dediğinde, "DP sabit noktasını" kastediyor. Bir makalede `V*` veya `Q*` gördüğünüzde bu döngüyü hayal edin.

## Gemileştir

`outputs/skill-dp-solver.md` olarak kaydedin:

```markdown
---
name: dp-solver
description: Solve a small tabular MDP exactly via policy iteration or value iteration. Report convergence behavior.
version: 1.0.0
phase: 9
lesson: 2
tags: [rl, dynamic-programming, bellman]
---

Given an MDP with a known model, output:

1. Choice. Policy iteration vs value iteration. Reason tied to |S|, |A|, γ.
2. Initialization. V_0, starting policy. Convergence sensitivity.
3. Stopping. Sup-norm tolerance ε. Expected number of sweeps.
4. Verification. V*(s_0) computed exactly. Greedy policy extracted.
5. Use. How this baseline will be used to debug/evaluate sampling-based methods.

Refuse to run DP on state spaces > 10⁷. Refuse to claim convergence without a sup-norm check. Flag any γ ≥ 1 on an infinite-horizon task as a guarantee violation.
```

## Alıştırmalar

1. **Kolay.** 4×4 GridWorld'de `γ ∈ {0.9, 0.99}` ile değer iterasyonu çalıştırın. `max |ΔV| < 1e-6` olana kadar kaç tarama gerekir? `V*`'yi 4×4 ızgara olarak yazdırın.
2. **Orta.** *Stokastik* GridWorld'de (kayma olasılığı `0.1`) politika iterasyonu vs değer iterasyonunu karşılaştırın. Sayın: taramalar, duvar saati zamanı, son `V*(0,0)`. Hangisi iterasyonlarda daha hızlı yakınsar? Duvar saatinde?
3. **Zor.** Değiştirilmiş politika iterasyonu oluşturun: değerlendirme adımında yakınsamaya kadar değil, sadece `k` tarama çalıştırın. `k ∈ {1, 2, 5, 10, 50}` için `V*(0,0)` hatasını `k`'ya göre çizin. Eğri, değerlendirme/iyileştirme uzlaşması hakkında ne söylüyor?

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Politika iterasyonu | "DP algoritması" | Değerlendirme (`V^π`) ve iyileştirme (`V^π`'ye göre açgözlü `π`) alternatif sürdürülür — politika değişene kadar. |
| Değer iterasyonu | "Daha hızlı DP" | Tek taramada uygulanan Bellman eniyilik yedeği; geometrik olarak `V*`'ye yakınsar. |
| Bellman operatörü | "Rekürans" | `(T V)(s) = max_a Σ P (r + γ V(s'))`; sup-norm'da bir `γ`-sözleşmesi. |
| Sözleşme | "Neden DP yakınsar" | `γ \|\|x - y\|\|` sınırını sağlayan herhangi bir `T` operatörü benzersiz sabit noktaya sahiptir. |
| GPI | "Her şey DP'dir" | Genelleştirilmiş Politika İterasyonu: `V` ve `π`'yi karşılıklı tutarlılığa götüren her yöntem. |
| Senkron güncelleme | "Jacobi tarzı" | Bir tarama boyunca eski `V` kullanılır; temiz analiz edilebilir ama daha yavaş. |
| Yerinde güncelleme | "Gauss-Seidel tarzı" | `V` güncellenirken kullanılır; pratikte daha hızlı yakınsar. |

## İleri Okuma

- [Sutton & Barto (2018). Bölüm 4 — Dynamic Programming](http://incompleteideas.net/book/RLbook2020.pdf) — politika iterasyonu ve değer iterasyonunun kanonik sunumu.
- [Bertsekas (2019). Reinforcement Learning and Optimal Control](http://www.athenasc.com/rlbook.html) — sözleşme-mapping argümanlarının titiz ele alımı.
- [Puterman (2005). Markov Decision Processes](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470316887) — değiştirilmiş politika iterasyonu ve yakınsama analizi.
- [Howard (1960). Dynamic Programming and Markov Processes](https://mitpress.mit.edu/9780262582300/dynamic-programming-and-markov-processes/) — orijinal politika iterasyonu makalesi.
- [Bertsekas & Tsitsiklis (1996). Neuro-Dynamic Programming](http://www.athenasc.com/ndpbook.html) — DP'den yaklaşık-DP / deep RL'ye her sonraki dersin kullandığı köprü.
