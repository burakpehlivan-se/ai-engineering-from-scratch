# Temporal Difference — Q-Learning ve SARSA

> Monte Carlo bölümün bitmesini bekler. TD her adımdan sonra bir sonraki değer tahminini bindirerek (bootstrap) güncellenir. Q-learning off-policy ve iyimserdir; SARSA on-policy ve temkinlidir. Her ikisi de bir satır kod. Her ikisi de bu fazdaki her deep-RL yönteminin temelini oluşturur.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 9 · 01 (MDP'ler), Faz 9 · 02 (Dynamic Programming), Faz 9 · 03 (Monte Carlo)
**Süre:** ~75 dakika

## Problem

Monte Carlo çalışır ama iki pahalı talebi vardır. Sonlanan bölümlere ihtiyaç duyar ve yalnızca son getiri geldikten sonra güncellenir. Bölümünüz 1.000 adımsa, MC herhangi bir şeyi güncellemek için 1.000 adım bekler. Yüksek varyanslı, düşük önyargılı ve pratikte yavaştır.

Dynamic programming'in tam tersi profili vardır — sıfır varyanslı bindirilmiş yedekler — ama bilinen bir model gerektirir.

Temporal difference (TD) öğrenmesi farkı böler. Tek bir geçişten `(s, a, r, s')`, bir adım hedef `r + γ V(s')` oluşturun ve `V(s)`'yi ona doğru kaydırın. Model yok. Tam bölümler yok. Sağdaki tarafta yaklaşık bir `V` kullanmaktan kaynaklanan önyargı, ama MC'den çok daha düşük varyans ve ilk adımdan çevrimiçi güncellemeler.

Bu, tüm modern RL'nin — DQN, A2C, PPO, SAC — döndüğü eksendir. Faz 9'un geri kalanı, bu derste yazacağınız tek adım TD güncellemesinin üzerine inşa edilmiş fonksiyon yaklaşımı ve hileler katmanlarıdır.

## Kavram

![Q-learning vs SARSA: off-policy max vs on-policy Q(s', a')](../assets/td.svg)

**V için TD(0) güncellemesi:**

`V(s) ← V(s) + α [r + γ V(s') - V(s)]`

Parantez içindeki miktar TD hatasıdır: `δ = r + γ V(s') - V(s)`. MC'deki `G_t - V(s_t)`'nin çevrimiçi analogudur. Yakınsama için `α`'nın Robbins-Monro'yu sağlaması (`Σ α = ∞`, `Σ α² < ∞`) ve tüm durumların sonsuz kez ziyaret edilmesi gerekir.

**Q-learning.** Kontrol için bir off-policy TD yöntemi:

`Q(s, a) ← Q(s, a) + α [r + γ max_{a'} Q(s', a') - Q(s, a)]`

`max`, `s'`'den itibaren *açgözlü* politikanın izleneceğini varsayar, ajanın aslında hangi eylemi aldığına bakmaksızın. Bu kopukluk, Q-learning'in `Q*`'yu öğrenirken ajanın ε-greedy ile keşfetmesini sağlar. Mnih ve ark. (2015) bunu Atari'deki deep Q-learning'e dönüştürdü (Ders 05).

**SARSA.** Bir on-policy TD yöntemi:

`Q(s, a) ← Q(s, a) + α [r + γ Q(s', a') - Q(s, a)]`

İsim `(s, a, r, s', a')` demetidir. SARSA, ajanın aslında bir sonraki aldığı eylemi `a'` kullanır, açgözlü `argmax`'ı değil. Çalışan herhangi bir ε-greedy `π` için `Q^π`'ye yakınsar ki `ε → 0` limitinde `Q*` olur.

**Uçurum-yürüme farkı.** Klasik uçurum-yürüme görevinde (düşme = ödül -100), Q-learning uçurum kenarındaki en iyi yolu öğrenir ama keşif sırasında cezayı zaman zaman alır. SARSA, uçurumdan bir adım uzakta daha güvenli bir yol öğrenir çünkü keşif gürültüsünü Q-değerine dahil eder. Eğitimle, her ikisi de `ε → 0`'da en iyi hale gelir. Pratikte bu önemlidir: keşif dağıtım sırasında gerçekten gerçekleşiyorsa, SARSA'nın davranışı daha muhafazakârdır.

**Beklenen SARSA.** `Q(s', a')`'yi `π` altında beklenen değeriyle değiştirin:

`Q(s, a) ← Q(s, a) + α [r + γ Σ_{a'} π(a'|s') Q(s', a') - Q(s, a)]`

SARSA'dan daha düşük varyans (örnek `a'` yok), aynı on-policy hedef. Genellikle modern ders kitaplarında varsayılan olarak kullanılır.

**n-adım TD ve TD(λ).** Bindirmeden önce `n` adım bekleyerek TD(0) ile MC arasında enterpolasyon yapar. `n=1` TD, `n=∞` MC'dir. TD(λ), geometrik ağırlıklarla `(1-λ)λ^{n-1}` tüm `n`'lerin ortalamasıdır. Çoğu deep-RL `n`'yi 3 ile 20 arasında kullanır.

## İnşa Et

### Adım 1: ε-greedy politikada SARSA

```python
def sarsa(env, episodes, alpha=0.1, gamma=0.99, epsilon=0.1):
    Q = defaultdict(lambda: {a: 0.0 for a in ACTIONS})

    def choose(s):
        if random() < epsilon:
            return choice(ACTIONS)
        return max(Q[s], key=Q[s].get)

    for _ in range(episodes):
        s = env.reset()
        a = choose(s)
        while True:
            s_next, r, done = env.step(s, a)
            a_next = choose(s_next) if not done else None
            target = r + (gamma * Q[s_next][a_next] if not done else 0.0)
            Q[s][a] += alpha * (target - Q[s][a])
            if done:
                break
            s, a = s_next, a_next
    return Q
```

#### Açıklama
Sekiz satır. Q-learning'den tek fark hedef satırıdır.

### Adım 2: Q-learning

```python
def q_learning(env, episodes, alpha=0.1, gamma=0.99, epsilon=0.1):
    Q = defaultdict(lambda: {a: 0.0 for a in ACTIONS})
    for _ in range(episodes):
        s = env.reset()
        while True:
            a = choose(s, Q, epsilon)
            s_next, r, done = env.step(s, a)
            target = r + (gamma * max(Q[s_next].values()) if not done else 0.0)
            Q[s][a] += alpha * (target - Q[s][a])
            if done:
                break
            s = s_next
    return Q
```

#### Açıklama
`max` hedefi davranıştan koparır. Bu, sembolik olarak on-policy ile off-policy arasındaki farktır.

### Adım 3: öğrenme eğrileri

Her 100 bölümdeki ortalama getiriyi izleyin. Q-learning basit deterministik GridWorld'de daha hızlı yakınsar; SARSA uçurum-yürümede daha muhafazakârdır. `code/main.py`'deki 4×4 GridWorld'de, her ikisi de `α=0.1, ε=0.1` ile ~2.000 bölümden sonra en yakın optime ulaşır.

### Adım 4: DP gerçeğiyle karşılaştır

`Q*`'yi almak için değer iterasyonu (Ders 02) çalıştırın. `max_{s,a} |Q_learned(s,a) - Q*(s,a)|` kontrol edin. Sağlıklı bir tablo TD ajanı 4×4 GridWorld'de 10.000 bölümden sonra `~0.5` içinde olur.

## Tuzaklar

- **Başlangıç Q değerleri önemlidir.** İyimser başlatma (negatif ödüllü bir görevde `Q = 0`) keşfi teşvik eder. Kötümser başlatma açgözlü bir politikayı sonsuza kadar hapsedebilir.
- **α çizelgesi.** Sabit `α` istasyonel olmayan sorunlar için iyidir. `α_n = 1/n` ile azaltmak teoride yakınsama sağlar ama pratikte çok yavaştır — `α`'yı `[0.05, 0.3]` aralığında sabitleyin ve öğrenme eğrisini izleyin.
- **ε çizelgesi.** Yüksek başlatın (`ε=1.0`), `ε=0.05`'e düşürün. "GLIE" (sonsuz keşifle limitte açgözlü) yakınsama koşuludur.
- **Q-learning'de maksimum önyargı.** `max` operatörü `Q` gürültülü olduğunda yukarı yönlü yanlıdır. Aşırı tahminlere yol açar — Hasselt'in Çift Q-learning'i (Ders 05'te DDQN tarafından kullanılır) bunu iki Q tablosuyla düzeltir.
- **Sonlanmayan bölümler.** TD sonlanmalar olmadan öğrenebilir, ama adımları sınırlamanız veya sınırlamada bindirmeyi doğru şekilde ele almanız gerekir. Standart: sınırlamayı sonlanmamış olarak kabul et, bindirmeyi sürdür.
- **Durum hash'leme.** Durumlar tuple/tensor ise, hash'lenebilir bir anahtar kullanın (liste değil tuple; ham yuvarlanmamış yerine yuvarlanmış float tuple'ı).

## Kullan

2026 TD manzarası:

| Görev | Yöntem | Neden |
|------|--------|--------|
| Küçük tablo ortamları | Q-learning | En iyi politikayı doğrudan öğrenir. |
| On-policy güvenlik-kritik | SARSA / Beklenen SARSA | Keşif sırasında muhafazakâr. |
| Yüksek boyutlu durum | DQN (Faz 9 · 05) | Replay ve target net ile sinir ağı Q-fonksiyonu. |
| Sürekli eylemler | SAC / TD3 (Faz 9 · 07) | Q-ağı üzerinde TD güncellemesi; politika ağı eylemler üretir. |
| LLM RL (ödül-modeli tabanlı) | PPO / GRPO (Faz 9 · 08, 12) | GAE ile TD tarzı avantajlı actor-critic. |
| Offline RL | CQL / IQL (Faz 9 · 08) | Muhafazakâr regularizasyonlu Q-learning. |

2026 makalelerinde okuduğunuz "RL"'nin %90'ı Q-learning veya SARSA'nın bir elaborasyonudur. Daha derine okumadan önce tablo güncellemesini parmaklarınızla bilin.

## Gemileştir

`outputs/skill-td-agent.md` olarak kaydedin:

```markdown
---
name: td-agent
description: Pick between Q-learning, SARSA, Expected SARSA for a tabular or small-feature RL task.
version: 1.0.0
phase: 9
lesson: 4
tags: [rl, td-learning, q-learning, sarsa]
---

Given a tabular or small-feature environment, output:

1. Algorithm. Q-learning / SARSA / Expected SARSA / n-step variant. One-sentence reason tied to on-policy vs off-policy and variance.
2. Hyperparameters. α, γ, ε, decay schedule.
3. Initialization. Q_0 value (optimistic vs zero) and justification.
4. Convergence diagnostic. Target learning curve, `|Q - Q*|` check if DP is possible.
5. Deployment caveat. How will exploration behave at inference? Is SARSA's conservatism needed?

Refuse to apply tabular TD to state spaces > 10⁶. Refuse to ship a Q-learning agent without a max-bias caveat. Flag any agent trained with ε held at 1.0 throughout (no exploitation phase).
```

## Alıştırmalar

1. **Kolay.** 4×4 GridWorld'de Q-learning ve SARSA'yı uygulayın. 2.000 bölüm için öğrenme eğrilerini (her 100 bölümde ortalama getiri) çizin. Hangisi daha hızlı yakınsar?
2. **Orta.** Bir uçurum-yürüme ortamı oluşturun (4×12, son satır uçurumdur, ödül -100 ve başa dönüş). Q-learning ve SARSA son politikalarını karşılaştırın. Her birinin aldığı yolların ekran görüntüsünü alın. Hangisi uçuruma daha yakın?
3. **Zor.** Double Q-learning'i uygulayın. Gürültülü ödüllü bir GridWorld'de (Gaussian gürültü σ=5 adım başına ödüle eklenir), Q-learning'in `V*(0,0)`'yı anlamlı bir miktarda aşırı tahmin ettiğini, Double Q-learning'in etmediğini gösterin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| TD hatası | "Güncelleme sinyali" | `δ = r + γ V(s') - V(s)`, bindirilmiş artık. |
| TD(0) | "Tek adım TD" | Yalnızca sonraki durum tahminini kullanarak her geçişten sonra güncelleme. |
| Q-learning | "Off-policy RL 101" | Sonraki durum eylemleri üzerinde `max` ile TD güncellemesi; davranış politikasına bakmaksızın `Q*`'yu öğrenir. |
| SARSA | "On-policy Q-learning" | Asıl sonraki eylemi kullanan TD güncellemesi; mevcut ε-greedy π için `Q^π`'yi öğrenir. |
| Beklenen SARSA | "Düşük varyanslı SARSA" | Örneklenmiş `a'` yerine π altında beklenen değeriyle değiştirir. |
| GLIE | "Doğru keşif çizelgesi" | Sonsuz keşifle limitte açgözlü; Q-learning yakınsaması için gerekli. |
| Bindirme (Bootstrapping) | "Hedefteki mevcut tahminleri kullanma" | TD'yi MC'den ayıran. Önyargı kaynağı ama devasa varyans azaltması. |
| Maksimum önyargı | "Q-learning aşırı tahmin eder" | Gürültülü tahminler üzerinde `max` yukarı yönlü yanlıdır; Double Q-learning tarafından düzeltilir. |

## İleri Okuma

- [Watkins & Dayan (1992). Q-learning](https://link.springer.com/article/10.1007/BF00992698) — orijinal makale ve yakınsama kanıtı.
- [Sutton & Barto (2018). Bölüm 6 — Temporal-Difference Öğrenmesi](http://incompleteideas.net/book/RLbook2020.pdf) — TD(0), SARSA, Q-learning, Beklenen SARSA.
- [Hasselt (2010). Double Q-learning](https://papers.nips.cc/paper_files/paper/2010/hash/091d584fced301b442654dd8c23b3fc9-Abstract.html) — maksimum önyargı düzeltmesi.
- [Seijen, Hasselt, Whiteson, Wiering (2009). A Theoretical and Empirical Analysis of Expected SARSA](https://ieeexplore.ieee.org/document/4927542) — beklenen SARSA motivasyonu.
- [Rummery & Niranjan (1994). On-line Q-learning using connectionist systems](https://www.researchgate.net/publication/2500611_On-Line_Q-Learning_Using_Connectionist_Systems) — SARSA'yı icat eden makale (o zamanlar "değiştirilmiş connectionist Q-learning" olarak adlandırılmış).
- [Sutton & Barto (2018). Bölüm 7 — n-adım Bindirme](http://incompleteideas.net/book/RLbook2020.pdf) — TD(0)'ı TD(n)'ye genelleştirir, Q-learning'den uygunluk izlerine (eligibility traces) ve daha sonra PPO'daki GAE'ye giden yol.
