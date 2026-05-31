# MDP'ler, Durumlar, Eylemler ve Ödüller

> Bir Markov Decision Process beş şeyden oluşur: durumlar (state), eylemler (action), geçişler, ödüller (reward) ve bir diskont faktörü (discount). RL'deki her şey — Q-learning, PPO, DPO, GRPO — bu yapı üzerinde optimize eder. Bir kez öğrenin, geri kalan reinforcement learning'ı bedavaya okuyun.

**Tür:** Öğrenme
**Diller:** Python
**Ön Koşullar:** Faz 1 · 06 (Olasılık ve Dağılımlar), Faz 2 · 01 (ML Sınıflandırması)
**Süre:** ~45 dakika

## Problem

Bir satranç botu yazıyorsunuz. Ya da bir envanter planlayıcı. Ya da bir işlem (trading) ajanı. Ya da bir akıl yürütme modelini eğiten PPO döngüsü. Dört farklı alan, şaşırtıcı bir gerçek: dördü de aynı materyal nesneye indirgenir.

Denetimli öğrenme (supervised learning) size `(x, y)` çiftleri verir ve bir fonksiyon uydurmanızı ister. Reinforcement learning size etiket vermez — sadece bir durum akışı, aldığınız eylemler ve skaler bir ödül. Hamle oyunu kazandırdı mı? Yeniden stoklama kararı para tasarrufu sağladı mı? İşlem kâr getirdi mi? LLM'nin ürettiği token hakemden daha yüksek bir ödül mü aldı?

Bu akıştan öğrenemezsiniz; önce onu formalize etmeniz gerekir. "Ne gördüm", "ne yaptım", "sonra ne oldu", "ne kadar iyiydi" — her biri üzerinde akıl yürüyebileceğiniz bir nesneye dönüşmeli. Bu formalizasyon bir Markov Decision Process'tir. Bu fazdaki her RL algoritması, sonda yer alan RLHF ve GRPO döngüleri dahil, bu yapı üzerinde optimize eder.

## Kavram

![Markov decision process: states, actions, transitions, rewards, discount](../assets/mdp.svg)

**Beş nesne.**

- **Durumlar (State)** `S`. Ajanın karar vermesi için gereken her şey. GridWorld'de hücre. Satrançta tahta. Bir LLM'de bağlam penceresi (context window) artı hafıza.
- **Eylemler (Action)** `A`. Seçenekler. Yukarı/aşağı/sola/sağa hareket. Bir hamle yap. Bir token üret.
- **Geçişler** `P(s' | s, a)`. Verilen durum `s` ve eylem `a` için bir sonraki durum üzerindeki dağılım. Satrançta deterministik, envanterde stokastik, LLM çözümlemesinde neredeyse deterministik.
- **Ödüller (Reward)** `R(s, a, s')`. Skaler sinyal. Kazanç = +1, kayıp = -1. Gelir eksi maliyet. GRPO'daki log-olabilirlik oranı (log-likelihood ratio) terimi.
- **Diskont** `γ ∈ [0, 1)`. Gelecek ödülün şimdikiye kıyasla ne kadar önemli olduğu. `γ = 0.99` yaklaşık 100 adım ufuk sağlar; `γ = 0.9` yaklaşık 10 adım.

**Markov özelliği** `P(s_{t+1} | s_t, a_t) = P(s_{t+1} | s_0, a_0, …, s_t, a_t)`. Gelecek sadece mevcut duruma bağlıdır. Eğer öyle değilse, durum temsili eksiktir — bu yöntemin başarısızlığı değil, durumun başarısızlığıdır.

**Politikalar (policy) ve getiriler (return).** Bir politika `π(a | s)` durumları eylem dağılımlarına eşler. Getiri `G_t = r_t + γ r_{t+1} + γ² r_{t+2} + …` gelecek ödüllerin diskontlu toplamıdır. Değer `V^π(s) = E[G_t | s_t = s]` politika `π` altında `s`'den başlayan beklenen getiridir. Q-değeri `Q^π(s, a) = E[G_t | s_t = s, a_t = a]` belirli bir eylemle başlayan beklenen getiridir. Her RL algoritması bu ikisinden birini tahmin eder ve ardından `π`'yi buna göre geliştirir.

**Bellman denklemleri.** Bu fazdaki her şeyin kullandığı sabit nokta denklemleri:

`V^π(s) = Σ_a π(a|s) Σ_{s', r} P(s', r | s, a) [r + γ V^π(s')]`
`Q^π(s, a) = Σ_{s', r} P(s', r | s, a) [r + γ Σ_{a'} π(a'|s') Q^π(s', a')]`

Bunlar beklenen getiriyi "bu adımın ödülüsü" artı "varılacak yerin diskontlu değeri" olarak böler. Rekürsif. Faz 9'daki her algoritma bu denklemi ya yakınsamaya kadar yineleden (dynamic programming), ya örneklemden (Monte Carlo) ya da bir adım ileri bootstrap eden (temporal difference, TD learning) bir yoldur.

## İnşa Et

### Adım 1: küçük bir deterministik MDP

4×4 GridWorld. Ajan sol üstten başlar, sağ altta sonlanır, adım başına -1 ödül, eylemler `{yukarı, aşağı, sol, sağ}`. `code/main.py`'ye bakın.

```python
GRID = 4
TERMINAL = (3, 3)
ACTIONS = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}

def step(state, action):
    if state == TERMINAL:
        return state, 0.0, True
    dr, dc = ACTIONS[action]
    r, c = state
    nr = min(max(r + dr, 0), GRID - 1)
    nc = min(max(c + dc, 0), GRID - 1)
    return (nr, nc), -1.0, (nr, nc) == TERMINAL
```

#### Açıklama
Beş satır. Bu tüm ortamdır. Deterministik geçişler, sabit adım cezası, emici sonlanma durumu (absorbing terminal state).

### Adım 2: bir politikayı rollout et

Politika, durumdan eylem dağılımına bir fonksiyondur. En basiti: düzgün rastgele.

```python
def uniform_policy(state):
    return {a: 0.25 for a in ACTIONS}

def rollout(policy, max_steps=200):
    s, total, steps = (0, 0), 0.0, 0
    for _ in range(max_steps):
        a = sample(policy(s))
        s, r, done = step(s, a)
        total += r
        steps += 1
        if done:
            break
    return total, steps
```

#### Açıklama
Rastgele politikayı 1000 kez çalıştırın. Ortalama getiri bu 4×4 tahta için -60 ile -80 arasında olur. En iyi getiri -6'dır (doğrudan sağ-aşağı yolu). Bu kapatmak Faz 9'daki her şeydir.

### Adım 3: Bellman denklemiyle `V^π`'yi tam olarak hesapla

Küçük MDP'ler için Bellman denklemi bir lineer sistemdir. Durumları numaralandırın, beklentiyi uygulayın, değerler değişmeyene kadar yineleyin.

```python
def policy_evaluation(policy, gamma=0.99, tol=1e-6):
    V = {s: 0.0 for s in all_states()}
    while True:
        delta = 0.0
        for s in all_states():
            if s == TERMINAL:
                continue
            v = 0.0
            for a, pi_a in policy(s).items():
                s_next, r, _ = step(s, a)
                v += pi_a * (r + gamma * V[s_next])
            delta = max(delta, abs(v - V[s]))
            V[s] = v
        if delta < tol:
            return V
```

#### Açıklama
Bu yinelemeli politika değerlendirmesidir (iterative policy evaluation). Sutton & Barto'daki ilk algoritmadır ve ardından gelen her RL yönteminin teorik temelidir.

### Adım 4: `γ` fiziksel anlamı olan bir hiperparametredir

Etkili ufuk yaklaşık `1 / (1 - γ)`'dir. `γ = 0.9` → 10 adım. `γ = 0.99` → 100 adım. `γ = 0.999` → 1.000 adım.

Çok düşük olursa ajan dar görüşlü (myopic) davranır. Çok yüksek olursa kredi atama (credit assignment) gürültülü hale gelir çünkü birçok erken adım uzak gelecek ödülle ortak sorumluluk paylaşır. LLM RLHF genellikle `γ = 1` kullanır çünkü bölümler kısa ve sınırlıdır. Kontrol görevleri `0.95–0.99` kullanır. Uzun ufuklu strateji oyunları `0.999` kullanır.

## Tuzaklar

- **Non-Markovian durum.** Karar vermek için son üç gözleme ihtiyacınız varsa, "durum" sadece mevcut gözlem değildir. Çözüm: kareleri istifleyin (Atari'de DQN 4 istifler) veya rekürsif durum kullanın (LSTM/GRU gözlemler üzerinde).
- **Seyrek ödüller.** Sadece kazanç ödülleri büyük durum uzaylarında öğrenmeyi neredeyse imkansız hale getirir. Ödülleri şekillendirin (ara sinyal) veya taklit ile bootstrap edin (Faz 9 · 09).
- **Ödül hacking.** Bir vekil ödülü optimize etmek genellikle patolojik davranış üretir. OpenAI'ın tekne yarışı ajanı bitiş çizgisine ulaşmak yerine güçlendirmeleri toplamak için sonsuza kadar dairesel döndü. Ödülü her zaman hedeften, vekilden değil, tanımlayın.
- **Diskont hatalı tanımlama.** Sonsuz ufuklu bir görevde `γ = 1` her değeri sonsuz yapar. Her zaman sonlu bir ufuk veya `γ < 1` ile sınırlayın.
- **Ödül ölçeği.** {+100, -100} ile {+1, -1} ödülleri aynı en iyi politikaları verir ama çok farklı gradyan büyüklükleri. PPO/DQN'a eklemeden önce `[-1, 1]` civarına normalleştirin.

## Kullan

2026 yığını her RL hattını koda dokunmadan bir MDP'ye indirger:

| Alan | Durum | Eylem | Ödül | γ |
|-----------|-------|--------|--------|---|
| Kontrol (lokomosyon, manipülasyon) | Eklem açıları + hızları | Sürekli torklar | Göreve özel şekillendirilmiş | 0.99 |
| Oyunlar (satranç, Go, poker) | Tahta + geçmiş | Yasal hamle | Kazanç=+1 / kayıp=-1 | 1.0 (sonlu) |
| Envanter / fiyatlandırma | Stok + talep | Sipariş miktarı | Gelir - maliyet | 0.95 |
| LLM'ler için RLHF | Bağlam token'ları | Bir sonraki token | Sonda ödül modeli puanı | 1.0 (bölüm ~200 token) |
| Akıl yürütme için GRPO | İstem + kısmi yanıt | Bir sonraki token | Sonda doğrulayıcı 0/1 | 1.0 |

Herhangi bir eğitim döngüsünü yazmadan önce beşli demeti (five tuple) yazın. Çoğu "RL çalışmıyor" hata raporu kağıt üzerinde kırık bir MDP formülasyonuna geri gider.

## Gemileştir

`outputs/skill-mdp-modeler.md` olarak kaydedin:

```markdown
---
name: mdp-modeler
description: Given a task description, produce a Markov Decision Process spec and flag formulation risks before training.
version: 1.0.0
phase: 9
lesson: 1
tags: [rl, mdp, modeling]
---

Given a task (control / game / recommendation / LLM fine-tuning), output:

1. State. Exact feature vector or tensor spec. Justify Markov property.
2. Action. Discrete set or continuous range. Dimensionality.
3. Transition. Deterministic, stochastic-with-known-model, or sample-only.
4. Reward. Function and source. Sparse vs shaped. Terminal vs per-step.
5. Discount. Value and horizon justification.

Refuse to ship any MDP where the state is non-Markovian without explicit mention of frame-stacking or recurrent state. Refuse any reward that was not defined in terms of the target outcome. Flag any `γ ≥ 1.0` on an infinite-horizon task. Flag any reward range >100x the typical step reward as a likely gradient-explosion source.
```

## Alıştırmalar

1. **Kolay.** `code/main.py`'de 4×4 GridWorld ve rastgele politika rollout'unu uygulayın. 10.000 bölüm çalıştırın. Getirinin ortalamasını ve standart sapmasını raporlayın. En iyi getiriyle (-6) karşılaştırın.
2. **Orta.** Düzgün rastgele politika için `γ ∈ {0.5, 0.9, 0.99}` ile `policy_evaluation` çalıştırın. Her biri için `V`'yi 4×4 ızgara olarak yazdırın. Neden sonlanmaya yakın durum değerleri daha büyük `γ` ile daha hızlı büyüdüğünü açıklayın.
3. **Zor.** GridWorld'ü stokastik yapın: her eylem `p = 0.1` olasılıkla komşu bir yöne kayar. Düzgün politikayı yeniden değerlendirin. `V[start]` daha iyi mi yoksa daha kötü mü olur? Neden?

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| MDP | "Reinforcement learning kurulumu" | Markov özelliğini sağlayan `(S, A, P, R, γ)` demeti. |
| Durum (State) | "Ajanın gördüğü" | Seçilen politika sınıfı altında gelecek dinamikleri için yeterli istatistik. |
| Politika (Policy) | "Ajanın davranışı" | Koşullu dağılım `π(a \| s)` veya deterministik eşleşme `s → a`. |
| Getiri (Return) | "Toplam ödül" | Mevcut adımdan itibaren diskontlu toplam `Σ γ^t r_t`. |
| Değer (Value) | "Bir durum ne kadar iyi" | `π` altında `s`'den başlayan beklenen getiri. |
| Q-değeri | "Bir eylem ne kadar iyi" | `π` altında `s`'den ve ilk eylem `a` ile başlayan beklenen getiri. |
| Bellman denklemi | "Dynamic programming reküransı" | Değer / Q'nun tek adım ödülü artı diskontlu halef değerine sabit nokta ayrıştırması. |
| Diskont `γ` | "Gelecek vs şimdiki" | Uzak gelecek ödül üzerinde geometrik ağırlık; etkili ufuk `~1/(1-γ)`. |

## İleri Okuma

- [Sutton & Barto (2018). Reinforcement Learning: An Introduction, 2nd ed.](http://incompleteideas.net/book/RLbook2020.pdf) — ders kitabı. Bölüm 3 MDP'leri ve Bellman denklemlerini kapsar; Bölüm 1, her sonraki dersin temelini oluşturan ödül hipotezini motive eder.
- [Bellman (1957). Dynamic Programming](https://press.princeton.edu/books/paperback/9780691146683/dynamic-programming) — Bellman denkleminin kökeni.
- [OpenAI Spinning Up — Part 1: Key Concepts](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html) — deep-RL açısından kısa bir MDP el kitabı.
- [Puterman (2005). Markov Decision Processes](https://onlinelibrary.wiley.com/doi/book/10.1002/9780470316887) — MDP'ler ve kesin çözüm yöntemleri üzerine operasyon araştırması referansı.
- [Littman (1996). Algorithms for Sequential Decision Making (PhD thesis)](https://www.cs.rutgers.edu/~mlittman/papers/thesis-main.pdf) — MDP'lerin dynamic programming uzmanlaşması olarak en temiz türetme.
