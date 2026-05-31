# Deep Q-Networks (DQN)

> 2013: Mnih, ham piksellerle tek bir Q-learning ağını eğitti, yedi Atari oyununda her klasik RL ajanını yendi. 2015: 49 oyuna genişletildi, Nature'da yayınlandı, deep-RL çağını başlattı. DQN, fonksiyon yaklaşımını kararlı kılan üç hile ile güçlendirilmiş Q-learning'dir.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 3 · 03 (Geri Yayılım), Faz 9 · 04 (Q-learning, SARSA)
**Süre:** ~75 dakika

## Problem

Tablo Q-learning, her (durum, eylem) çifti için ayrı bir Q-değeri gerektirir. Bir satranç tahtasının ~10⁴³ durumu vardır. Bir Atari karesi 210×160×3 = 100.800 özelliktir. Tablo RL binlerce durumda ölür, milyonlardan bahsetmiyor bile.

Düzeltme geriye dönüp bakıldığında açıktır: Q-tablosunu bir sinir ağıyla değiştirin, `Q(s, a; θ)`. Ama geriye dönüp bakıldığında açıktır onlarca yıl sürdü. Q-learning ile saf fonksiyon yaklaşımı "ölümcül üçlü" (deadly triad) altında diverge olur — fonksiyon yaklaşımı + bindirme + off-policy öğrenme. Mnih ve ark. (2013, 2015) öğrenmeyi stabilize eden üç mühendislik hilesi belirledi:

1. **Tecrübe tekrarı (experience replay)** geçişleri korele eder.
2. **Hedef ağı (target network)** bindirme hedefini dondurur.
3. **Ödül kırpma (reward clipping)** gradyan büyüklüklerini normalleştirir.

Atari'deki DQN, tek bir mimari ve tek bir hiperparametre kümesiyle ham piksellerden düzinesi kontrol problemini çözen ilk zamandır. O zamandan beri inşa edilen her "deep-RL" — DDQN, Rainbow, Dueling, Distributional, R2D2, Agent57 — bu üç hileli temelin üzerine yığılmıştır.

## Kavram

![DQN eğitim döngüsü: ortam, replay buffer, çevrimiçi ağ, hedef ağ, Bellman TD kaybı](../assets/dqn.svg)

**Hedef.** DQN, sinir Q-fonksiyonu üzerinde tek adım TD kaybını en aza indirir:

`L(θ) = E_{(s,a,r,s')~D} [ (r + γ max_{a'} Q(s', a'; θ^-) - Q(s, a; θ))² ]`

`θ` = çevrimiçi ağ, her adımda gradyan inişiyle güncellenir. `θ^-` = hedef ağ, periyodik olarak `θ`'dan kopyalanır (her ~10.000 adımda). `D` = geçmiş geçişlerin replay buffer'ı.

**Üç hile, önem sırasıyla:**

**Tecrübe tekrarı.** `~10⁶` geçişlik bir halka tamponu (ring buffer). Her eğitim adımı rastgele olarak bir mini grup örnekler. Bu zaman bağımlılığını kırar (ardışık kareler neredeyse aynıdır), ağın nadir ödüllü geçişlerden birçok kez öğrenmesini sağlar ve ardışık gradyan güncellemelerini korele eder. Olmadığında, sinir ağıyla on-policy TD Atari'de diverge olur.

**Hedef ağı.** Bellman denkleminin her iki tarafında aynı ağı `Q(·; θ)` kullanmak hedefin her güncellemede hareket etmesine neden olur — "kendi kuyruğunun peşinden koşma." Düzeltme: donmuş ağırlıklara sahip ikinci bir ağ `Q(·; θ^-)` tutun. Her `C` adımda `θ → θ^-` kopyalayın. Bu, binlerce gradyan adımı boyunca regresyon hedefini stabilize eder. yumuşak güncellemeler `θ^- ← τ θ + (1-τ) θ^-` (DDPG, SAC'da kullanılır) daha pürüzsüz bir varyanttır.

**Ödül kırpma.** Ödül büyüklükleri 1'den 1000+'ya kadar değişir. `{-1, 0, +1}`'e kırpma, herhangi bir oyunun gradyanı domine etmesini engeller. Ödül büyüklüğü önemli olduğunda yanlıştır; sadece işaretin önemli olduğu Atari'de ise sorunsuzdur.

**Double DQN.** Hasselt (2016) maksimum önyargıyı düzeltir: eylemi *seçmek* için çevrimiçi ağı, *değerlendirmek* için hedef ağı kullanın.

`target = r + γ Q(s', argmax_{a'} Q(s', a'; θ); θ^-)`

Doğrudan değiştirme, tutarlı olarak daha iyi. Varsayılan olarak kullanın.

**Diğer iyileştirmeler (Rainbow, 2017):** öncelikli replay (yüksek TD-hatası olan geçişleri daha fazla örnekle), düello mimarisi (ayrı `V(s)` ve avantaj başları), gürültülü ağlar (öğrenilmiş keşif), n-adım getirileri, dağılımsal Q (C51/QR-DQN), çoklu adım bindirmesi. Her biri birkaç yüzde ekler; kazanımlar kabaca toplanabilir.

## İnşa Et

Buradaki kod yalnızca stdlib — numpy'siz — küçük bir sürekli GridWorld üzerinde el yapımı tek-gizli katmanlı MLP kullanıyoruz, böylece her eğitim adımı mikrosaniyeler içinde çalışır. Algoritma, ölçekli Atari DQN ile özdeştir.

### Adım 1: replay buffer

```python
class ReplayBuffer:
    def __init__(self, capacity):
        self.buf = []
        self.capacity = capacity
    def push(self, s, a, r, s_next, done):
        if len(self.buf) == self.capacity:
            self.buf.pop(0)
        self.buf.append((s, a, r, s_next, done))
    def sample(self, batch, rng):
        return rng.sample(self.buf, batch)
```

#### Açıklama
Atari için ~50.000 kapasite; oyuncak ortamımız için 5.000 yeterlidir.

### Adım 2: küçük bir Q-ağı (el yapımı MLP)

```python
class QNet:
    def __init__(self, n_in, n_hidden, n_actions, rng):
        self.W1 = [[rng.gauss(0, 0.3) for _ in range(n_in)] for _ in range(n_hidden)]
        self.b1 = [0.0] * n_hidden
        self.W2 = [[rng.gauss(0, 0.3) for _ in range(n_hidden)] for _ in range(n_actions)]
        self.b2 = [0.0] * n_actions
    def forward(self, x):
        h = [max(0.0, sum(w * xi for w, xi in zip(row, x)) + b) for row, b in zip(self.W1, self.b1)]
        q = [sum(w * hi for w, hi in zip(row, h)) + b for row, b in zip(self.W2, self.b2)]
        return q, h
```

#### Açıklama
İleri yayılım: lineer → ReLU → lineer. Bu tüm ağdır.

### Adım 3: DQN güncellemesi

```python
def train_step(online, target, batch, gamma, lr):
    grads = zeros_like(online)
    for s, a, r, s_next, done in batch:
        q, h = online.forward(s)
        if done:
            y = r
        else:
            q_next, _ = target.forward(s_next)
            y = r + gamma * max(q_next)
        td_error = q[a] - y
        accumulate_grads(grads, online, s, h, a, td_error)
    apply_sgd(online, grads, lr / len(batch))
```

#### Açıklama
Biçim, Ders 04'teki Q-learning ile iki farkla: (a) bir tabloyu indekslemek yerine farklılaştırılabilir `Q(·; θ)` üzerinden geri yayılım, (b) hedef `Q(·; θ^-)` kullanır.

### Adım 4: dış döngü

Her bölüm için, `Q(·; θ)` üzerinde ε-greedy davranın, geçişleri buffer'a ekleyin, bir mini grup örnekleyin, bir gradyan adımı alın, periyodik olarak `θ^- ← θ` senkronize edin. Örüntü:

```python
for episode in range(N):
    s = env.reset()
    while not done:
        a = epsilon_greedy(online, s, epsilon)
        s_next, r, done = env.step(s, a)
        buffer.push(s, a, r, s_next, done)
        if len(buffer) >= batch:
            train_step(online, target, buffer.sample(batch), gamma, lr)
        if steps % sync_every == 0:
            target = copy(online)
        s = s_next
```

#### Açıklama
16 boyutlu tek-sıcak durumlu küçük GridWorld'ümüzde ajan ~500 bölümde neredeyse en iyi politikayı öğrenir. Atari'de bunu 200M kareye ölçekleyin ve bir CNN özellik çıkarıcı ekleyin.

## Tuzaklar

- **Ölümcül üçlü.** Fonksiyon yaklaşımı + off-policy + bindirme diverge olabilir. DQN bunu hedef ağı + replay ile azaltır; ikisini de çıkarmayın.
- **Keşif.** ε azalmalıdır, genellikle eğitimden ilk ~%10'da 1.0'dan 0.01'e. Yeterli erken keşif olmadıkça Q-ağı yerel bir havzaya yakınsar.
- **Aşırı tahmin.** Gürültülü Q üzerinde `max` yukarı yönlü yanlıdır. Üretimde her zaman Double DQN kullanın.
- **Ödül ölçeği.** Ödülleri kırpın veya normalleştirin; gradyan büyüklüğü ödül büyüklüğüyle orantılıdır.
- **Replay buffer soğuk başlangıç.** Buffer'da birkaç bin geçiş olana kadar eğitmeyin. ~20 örnek üzerindeki erken gradyanlar aşırı uyum sağlar.
- **Hedef senkronizasyon sıklığı.** Çok sık ≈ hedef ağı yok; çok seyrek ≈ eskimiş hedefler. Atari DQN 10.000 ortam adımı kullanır. Kural: eğitim ufğunun ~1/100'ünde senkronize edin.
- **Gözlem ön-işleme.** Atari DQN durumu Markov yapmak için 4 kareyi istifler. Hız bilgisi olan her ortam kare istiflemesi veya rekürsif durum gerektirir.

## Kullan

2026'da DQN nadiren en gelişmiş durumdadır ama referans off-policy algoritması olarak kalır:

| Görev | Tercih edilen yöntem | Neden DQN değil? |
|------|------------------|--------------|
| Atari benzeri ayrık eylem | Rainbow DQN veya Muesli | Aynı çerçeve, daha fazla hile. |
| Sürekli kontrol | SAC / TD3 (Faz 9 · 07) | DQN'de politika ağı yok. |
| On-policy / yüksekthroughput | PPO (Faz 9 · 08) | Replay buffer yok; ölçeklemesi daha kolay. |
| Offline RL | CQL / IQL / Decision Transformer | Muhafazakâr Q-hedefleri, bindirme patlamaları yok. |
| Büyük ayrık eylem uzayları (öneri) | Eylem gömme ile DQN veya IMPALA | Sorunsuz; dekorasyon önemlidir. |
| LLM RL | PPO / GRPO | Düzey-seviyesinde, adım-seviyesinde değil; farklı kayıp. |

Dersler hala geçerlidir. Replay ve hedef ağlar SAC, TD3, DDPG, SAC-X, AlphaZero'nun kendi-kendine-oynama buffer'ı ve her offline RL yönteminde görünür. Ödül kırpma PPO'da avantaj normalleştirmesi olarak yaşar. Mimari plan.

## Gemileştir

`outputs/skill-dqn-trainer.md` olarak kaydedin:

```markdown
---
name: dqn-trainer
description: Produce a DQN training config (buffer, target sync, ε schedule, reward clipping) for a discrete-action RL task.
version: 1.0.0
phase: 9
lesson: 5
tags: [rl, dqn, deep-rl]
---

Given a discrete-action environment (observation shape, action count, horizon, reward scale), output:

1. Network. Architecture (MLP / CNN / Transformer), feature dim, depth.
2. Replay buffer. Capacity, minibatch size, warmup size.
3. Target network. Sync strategy (hard every C steps or soft τ).
4. Exploration. ε start / end / schedule length.
5. Loss. Huber vs MSE, gradient clip value, reward clipping rule.
6. Double DQN. On by default unless explicit reason to disable.

Refuse to ship a DQN with no target network, no replay buffer, or ε held at 1. Refuse continuous-action tasks (route to SAC / TD3). Flag any reward range > 10× per-step mean as needing clipping or scale normalization.
```

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Bölüm başına getiri eğrisini çizin. Çalışan ortalama -10'u aşana kadar kaç bölüm gerekir?
2. **Orta.** Hedef ağı devre dışı bırakın (Bellman hedefinin her iki tarafı için çevrimiçi ağı kullanın). Eğitim kararsızlığını ölçün — getiri salınır mı yoksa diverge mı olur?
3. **Zor.** Double DQN ekleyin: `argmax a'`'yı seçmek için çevrimiçi ağı, değerlendirmek için hedef ağı kullanın. Gürültülü ödüllü bir GridWorld'de Double DQN'siz 1.000 bölümden sonra `Q(s_0, best_a)` önyargısını gerçek `V*(s_0)` ile karşılaştırın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| DQN | "Deep Q-learning" | Sinir Q-fonksiyonu, replay buffer ve hedef ağı ile Q-learning. |
| Tecrübe tekrarı | "Karıştırılmış geçişler" | Her gradyan adımında eşit olarak örneklenen halka tamponu; veriyi korele eder. |
| Hedef ağı | "Dondurulmuş bindirme" | Bellman hedefinde kullanılan periyodik Q kopyası; eğitimi stabilize eder. |
| Ölümcül üçlü | "Neden RL diverge olur" | Fonksiyon yaklaşımı + bindirme + off-policy = yakınsama garantisi yok. |
| Double DQN | "Maksimum önyargı düzeltmesi" | Çevrimiçi ağ eylemi seçer, hedef ağ değerlendirir. |
| Dueling DQN | "V ve A başları" | Q = V + A - mean(A) ayrıştırması; aynı çıkış, daha iyi gradyan akışı. |
| Rainbow | "Tüm hileler" | DDQN + PER + düello + n-adım + gürültülü + dağılımsal hepsi bir arada. |
| PER | "Öncelikli Replay" | TD-hatası büyüklüğüyle orantılı olarak geçiş örnekler. |

## İleri Okuma

- [Mnih et al. (2013). Playing Atari with Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602) — deep RL'yi başlatan 2013 NeurIPS workshop makalesi.
- [Mnih et al. (2015). Human-level control through deep reinforcement learning](https://www.nature.com/articles/nature14236) — Nature makalesi, 49 oyun DQN.
- [Hasselt, Guez, Silver (2016). Deep Reinforcement Learning with Double Q-learning](https://arxiv.org/abs/1509.06461) — DDQN.
- [Wang et al. (2016). Dueling Network Architectures](https://arxiv.org/abs/1511.06581) — düello DQN.
- [Hessel et al. (2018). Rainbow: Combining Improvements in Deep RL](https://arxiv.org/abs/1710.02298) — yığılmış hileler makalesi.
- [OpenAI Spinning Up — DQN](https://spinningup.openai.com/en/latest/algorithms/dqn.html) — net modern anlatım.
- [Sutton & Barto (2018). Bölüm 9 — Yaklaşımla On-Policy Tahmini](http://incompleteideas.net/book/RLbook2020.pdf) — DQN'nin hedef ağı ve replay buffer'ı evcilleştirmek için tasarlandığı "ölümcül üçlü" (fonksiyon yaklaşımı + bindirme + off-policy) ders kitabı ele alımı.
- [CleanRL DQN uygulaması](https://docs.cleanrl.dev/rl-algorithms/dqn/) — ablasyon çalışmalarında kullanılan referans tek-dosyalık DQN; bu dersin sıfırdan versiyonuyla birlikte okunması iyi bir fikir.
