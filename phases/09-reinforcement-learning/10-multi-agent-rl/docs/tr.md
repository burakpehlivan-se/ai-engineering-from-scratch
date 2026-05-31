# Çoklu Ajan RL (Multi-Agent RL)

> Tek ajan RL, ortamın durağan (stationary) olduğunu varsayar. İki öğrenen ajanı aynı dünyaya koy ve bu varsayım bozulur: her ajan diğerinin ortamının bir parçasıdır ve ikisi de değişiyor. Çoklu ajan RL, Markov varsayımı artık geçerli olmadığında öğrenmeyi yakınsamak için gereken hileler kümesidir.

**Tür:** Build
**Diller:** Python
**Önkoşullar:** Phase 9 · 04 (Q-learning), Phase 9 · 06 (REINFORCE), Phase 9 · 07 (Actor-Critic)
**Süre:** ~45 dakika

## Problem

Bir robotun odayı öğrenerek dolaşması tek ajan RL sorunudur. Bir futbol takımı öyle değildir. AlphaStar'a karşı StarCraft rakipleri öyle değildir. Açık artırmacı ajanlar pazarı öyle değildir. Dört yollu durakta birbirleriyle anlaşan iki araç öyle değildir. Çoklu çoklu gerçek dünya sorunları öyle değildir.

Her çoklu ajan ortamında, herhangi bir ajanın perspektifinden, diğer ajanlar *ortamın bir parçasıdır*. Öğrenip davranışlarını değiştirdikçe ortam durulmayan (non-stationary) hale gelir. Markov özelliği — "sonraki durum sadece mevcut duruma ve benim aksiyonuma bağlıdır" — ihlal edilir çünkü sonraki durum ayrıca *diğer* ajanların ne seçtiğine bağlıdır ve politikaları hareketli hedeflerdir.

Bu, tablo bazlı yakınsama ispatlarını bozar (Q-learning'in garantisi durağan bir ortam varsayar). Basit deep RL'yi de bozar: ajanlar birbirlerinin peşinde döngülere girer, asla kararlı bir politikaya yakınsamazlar. Çoklu ajan-a özgü tekniklere ihtiyacın vardır: merkezi eğitim / merkezsiz yürütme, counterfactual baseline'lar, lig oynaması, self-play.

2026 uygulamaları: robot sürüleri, trafik yönlendirme, otonom araç filoları, pazar simülasyonları, çoklu ajan LLM sistemleri (Phase 16) ve birden fazla zeki oyuncusu olan her oyun.

## Kavram

![Dört MARL rejimi: bağımsız, merkezi critic, self-play, lig](../assets/marl.svg)

**Formalizm: Markov Oyunu.** MDP'nin bir genelleştirmesi: durumlar `S`, ortak aksiyon `a = (a_1, …, a_n)`, geçiş `P(s' | s, a)` ve ajan-başına ödüller `R_i(s, a, s')`. Her ajan `i`, kendi politikası `π_i` altında kendi getirisini maksimize eder. Ödüller aynıysa **tam işbirlikçidir**. Sıfır toplamlıysa **düşmansaldır**. Karışık ise **genel toplamlıdır**.

**Temel zorluklar:**

- **Durulmazlık (Non-stationarity).** Ajan `i`'nin bakış açısından `P(s' | s, a_i)`, değişen `π_{-i}`'ye bağlıdır.
- **Kredi dağıtımı.** Ortak ödülle, hangi ajan buna neden olmuştur?
- **Keşif koordinasyonu.** Ajanlar tamamlayıcı stratejileri keşfetmeli, aynı durumu gereksizce keşfetmemeli.
- **Ölçeklenebilirlik.** Ortak eylem alanı `n`'de üssel olarak büyür.
- **Kısmi gözlemlilik.** Her ajan sadece kendi gözlemini görür; küresel durum gizlidir.

**Dört baskın rejim:**

**1. Bağımsız Q-learning / bağımsız PPO (IQL, IPPO).** Her ajan kendi Q'sunu veya politikasını öğrenir, diğerlerini ortamın bir parçası olarak ele alır. Basit, bazen işe yarar (özellikle deneyim tekrarı (experience replay) bir yumuşatma ajan-modelleme hilesi olarak işlev gördüğünde). Teorik yakınsama: yok. Pratikte: gevşek bağlantılı görevler için iyi, sıkı bağlantılı olanlar için kötü.

**2. Merkezi eğitim, merkezsiz yürütme (CTDE).** En yaygın modern paradigma. Her ajan kendi *politikasına* `π_i` sahiptir ve yerel gözlem `o_i`'ye koşulludur — dağıtımda standart merkezsiz yürütme. *Eğitim* sırasında merkezi bir critic `Q(s, a_1, …, a_n)` tam küresel duruma ve ortak aksiyona koşulludur. Örnekler:
- **MADDPG** (Lowe ve diğerleri 2017): Her ajan için merkezi critic'li DDPG.
- **COMA** (Foerster ve diğerleri 2017): Counterfactual baseline — "farklı bir aksiyon alsaydım ödülüm ne olurdu?" diye sorar — benim katkımı izole eder.
- **MAPPO** / **IPPO** paylaşımlı critic ile (Yu ve diğerleri 2022): Merkezi değer fonksiyonlu PPO. 2026'da işbirlikçi MARL'da baskındır.
- **QMIX** (Rashid ve diğerleri 2018): Değer ayrıştırması — `Q_tot(s, a) = f(Q_1(s, a_1), …, Q_n(s, a_n))` monotonik karıştırma ile.

**3. Self-play.** Aynı ajanın iki kopyası birbirlerine karşı oynar. Rakibin politikası, *benim geçmiş anlık görüntümdeki politikamdır*. AlphaGo / AlphaZero / MuZero. OpenAI Five. Sıfır toplamlı oyunlar için en iyi çalışır; eğitim sinyali simetrikтир.

**4. Lig oynaması.** Self-play'in genel toplamlı / düşmansal ortamlara genişletilmesi: geçmiş ve mevcut politikaların bir nüfusunu tut, ligden bir rakip örnekle, onlara karşı eğit. Exploiters (mevcut en iyiyi yenmeye yönelik uzmanlaşmış) ve main exploiters (exploiters'ları yenmeye yönelik uzmanlaşmış) ekler. AlphaStar (StarCraft II). Oyun "taş-kagit-makas" strateji döngülerine izin verdiğinde gerekli.

**İletişim.** Ajanların birbirlerine öğrenilmiş mesajlar `m_i` göndermesine izin ver. İşbirlikçi ortamlarda çalışır. Foerster ve diğerleri (2016), farklılaştırılabilir ajanlararası iletişimin uçtan uca eğitilebileceğini gösterdi. Günümüz LLM tabanlı çoklu ajan sistemleri (Phase 16) özünde doğal dil ile iletişim kurar.

## Kodu Yaz

Bu ders, iki işbirlikçi ajanlı 6×6 GridWorld kullanır. Farklı köşelerden başlarlar ve ortak bir hedefe ulaşmaları gerekir. Ortak ödül: her iki ajan da hala hareket halindeyken adım başına `-1`, ikisi de ulaştığında `+10`. `code/main.py`'ye bakın.

### Adım 1: çoklu ajan ortamı

```python
class CoopGridWorld:
    def __init__(self):
        self.size = 6
        self.goal = (5, 5)

    def reset(self):
        return ((0, 0), (5, 0))  # two agents

    def step(self, state, actions):
        a1, a2 = state
        new1 = move(a1, actions[0])
        new2 = move(a2, actions[1])
        done = (new1 == self.goal) and (new2 == self.goal)
        reward = 10.0 if done else -1.0
        return (new1, new2), reward, done
```

#### Açıklama

*Ortak* eylem alanı `|A|² = 16`'dır. Küresel durum iki konumdur.

### Adım 2: bağımsız Q-learning

Her ajan, ortak duruma anahtarlanmış kendi Q-tablosunu çalıştırır. Her adımda: her ikisi de ε-greedy aksiyonlar seçer, ortak geçişi toplar, her biri ortak ödülle kendi Q'sunu günceller.

```python
def independent_q(env, episodes, alpha, gamma, epsilon):
    Q1, Q2 = defaultdict(default_q), defaultdict(default_q)
    for _ in range(episodes):
        s = env.reset()
        while not done:
            a1 = epsilon_greedy(Q1, s, epsilon)
            a2 = epsilon_greedy(Q2, s, epsilon)
            s_next, r, done = env.step(s, (a1, a2))
            target1 = r + gamma * max(Q1[s_next].values())
            target2 = r + gamma * max(Q2[s_next].values())
            Q1[s][a1] += alpha * (target1 - Q1[s][a1])
            Q2[s][a2] += alpha * (target2 - Q2[s][a2])
            s = s_next
```

#### Açıklama

Ödüller yoğun ve hizalı olduğu için bu görevde çalışır. Sıkı bağlantılı görevlerde (örn., bir ajanın diğerini *beklemesi* gereken durumlarda) başarısız olur.

### Adım 3: ayrıştırılmış değer güncellemeli merkezi Q

Ortak aksiyonlar üzerinde tek bir Q kullan: `Q(s, a_1, a_2)`. Ortak ödülden güncelle. Marjinalleştirerek yürütmeyi merkezsizleştir: `π_i(s) = argmax_{a_i} max_{a_{-i}} Q(s, a_1, a_2)`. Üstel ortak eylem alanını *doğru* bir küresel görünüş için takas eder.

### Adım 4: basit self-play (düşmansal 2-ajan)

Aynı ajan, iki rol. Ajanı A'ya karşı ajanı B'yi eğit; `K` bölüm sonra A'nın ağırlıklarını B'ye kopyala. Simetrik eğitim, tutarlı ilerleme. AlphaZero tarifinin minyatürü.

## Tuzaklar

- **Durulmayan tekrar.** Bağımsız ajanlarla deneyim tekrarı, tek ajanlıdan daha kötüdür çünkü eski geçişler artık geçersiz rakipler tarafından üretilmiştir. Düzeltme: yeniden etiketle veya güncelliğe göre ağırlıklandır.
- **Kredi dağıtımı belirsizliği.** Uzun bir bölümden sonra ortak ödül; hangi ajanın katkıda bulunduğunu söylemenin açık bir yolu yok. Düzeltme: counterfactual baseline'lar (COMA) veya ajan başına ödül şekillendirme.
- **Politika kayması / kovalama.** Her ajanın en iyi yanıtı, diğerinin güncellemesiyle değişir. Düzeltme: merkezi critic, yavaş öğrenme hızları veya birini dondurarak sırayla güncelleme.
- **Koordinasyon aracılığıyla reward hacking.** Ajanlar tasarımcının öngörmediği koordineli istismarlar bulur. Açık artırmacı ajanlar sıfır teklife yakınsar. Düzeltme: dikkatli ödül tasarımı, davranış kısıtlamaları.
- **Keşif yinelemesi.** Her iki ajan da aynı durum-aksiyon çiftlerini keşfeder. Düzeltme: ajan başına entropi bonusları veya rol-koşullandırma.
- **Lig döngüleri.** Saf self-play hakimiyet döngüsüne takılabilir. Düzeltme: çeşitli rakiplerle lig oynaması.
- **Örnek patlaması.** `n` ajan × durum alanı × ortak aksiyonlar. Fonksiyon approximationsı ile yaklaşık hesaplama; ayrıştırılmış eylem alanları (her ajan için bir politika çıkış başlığı).

## Kullanım

2026 MARL uygulama haritası:

| Alan | Yöntem | Notlar |
|--------|--------|-------|
| İşbirlikçi gezinme / manipülasyon | MAPPO / QMIX | CTDE; paylaşımlı critic + merkezsiz actor'lar. |
| İki oyunculu oyunlar (satranç, go, poker) | MCTS ile self-play (AlphaZero) | Sıfır toplamlı; simetrik eğitim. |
| Karmaşık çoklu oyuncu (Dota, StarCraft) | Lig oynaması + taklit ön-eğitimi | OpenAI Five, AlphaStar. |
| Otonom araç filoları | Dikkatli CTDE MAPPO / PPO | Kısmi gözlem; değişken takım boyutları. |
| Açık artırma pazarları | Oyun teorisi dengesi + RL | `n` → ∞ olduğunda ortalama alan RL (mean-field RL). |
| LLM çoklu ajan sistemleri (Phase 16) | Doğal dil iletişimi + rol koşullandırması | Ajan planlama katmanında RL döngüsü. |

2026'da MARL'nin en büyük büyüme alanı LLM tabanlıdır: dil modeli ajanlarının sürüleri pazarlık ediyor, tartışıyor, yazılım üretiyor. RL, token seviyesinde değil *yörünge seviyesinde* çıktılar üzerinde tercih optimizasyonu olarak ortaya çıkar (Phase 16 · 03).

## Ürün Haline Getir

`outputs/skill-marl-architect.md` olarak kaydet:

```markdown
---
name: marl-architect
description: Belirli bir görev için doğru çoklu ajan RL rejimini seç (IPPO, CTDE, self-play, lig).
version: 1.0.0
phase: 9
lesson: 10
tags: [rl, multi-agent, marl, self-play]
---

`n` ajanlı bir görev verildiğinde, output et:

1. Rejim sınıflandırması. İşbirlikçi / düşmansal / genel toplamlı. Gerekçesiyle.
2. Algoritma. IPPO / MAPPO / QMIX / self-play / lig. Bağlantı sıkılığı ve ödül yapısına bağlı gerekçe.
3. Bilgi erişimi. Merkezi eğitim (hangi küresel bilgi critic'e gider)? Merkezsiz yürütme?
4. Kredi dağıtımı. Counterfactual baseline, değer ayrıştırması veya ödül şekillendirme.
5. Keşif planı. Ajan başına entropi, nüfus tabanlı eğitim veya lig.

Sıkı bağlantılı işbirlikçi görevlerde bağımsız Q-learning'i reddet. Döngü riskleri olan genel toplamlıda self-play önermeyi reddet. Sabit-rakip değerlendirmesi olmayan her MARL hattını işaretle (kiraz-kertilmiş self-play sayıları yaygındır).
```

## Alıştırmalar

1. **Kolay.** 2-ajanlı işbirlikçi GridWorld'de bağımsız Q-learning eğit. Ortalama getiri > 0 olana kadar kaç bölüm gerekir? Ortak öğrenme eğrisini çiz.
2. **Orta.** Bir "koordinasyon" görevi ekle: hedef sadece her iki ajan da aynı adımda üzerine bastığında ulaşılır. Bağımsız Q hala yakınsar mı? Ne bozulur?
3. **Zor.** MAPPO tarzı eğitim için merkezi bir critic uygula ve koordinasyon görevinde bağımsız PPO ile yakınsama hızını karşılaştır.

## Anahtar Terimler

| Terim | İnsanlar ne der | Gerçekte ne anlama gelir |
|------|-----------------|-----------------------|
| Markov oyunu | "Çoklu ajan MDP" | `(S, A_1, …, A_n, P, R_1, …, R_n)`; her ajanın kendi ödülü vardır. |
| CTDE | "Merkezi eğitim, merkezsiz yürütme" | Eğitim zamanında ortak critic; her ajanın politikası sadece yerel gözlemini kullanır. |
| IPPO | "Bağımsız PPO" | Her ajan PPO'yu ayrı çalıştırır. Basit baseline; genellikle hafife alınır. |
| MAPPO | "Çoklu ajan PPO" | Küresel duruma koşullu merkezi değer fonksiyonlu PPO. |
| QMIX | "Monotonik değer ayrıştırması" | `Q_tot = f_monotone(Q_1, …, Q_n)` merkezsiz argmax'a izin verir. |
| COMA | "Counterfactual çoklu ajan" | Advantage = benim Q'm eksi aksiyonumu marjinalleştirerek beklenen Q. |
| Self-play | "Ajan vs geçmiş ben" | Tek ajan, iki rol; sıfır toplamlı oyunlarda standarttır. |
| Lig oynaması | "Nüfus eğitimi" | Geçmiş politikaları önbelleğe al, havuzdan rakip örnekle; strateji döngülerini ele alır. |

## İleri Okuma

- [Lowe ve diğerleri (2017). Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments (MADDPG)](https://arxiv.org/abs/1706.02275) — Merkezi critic'li CTDE.
- [Foerster ve diğerleri (2017). Counterfactual Multi-Agent Policy Gradients (COMA)](https://arxiv.org/abs/1705.08926) — Kredi dağıtımı için counterfactual baseline'lar.
- [Rashid ve diğerleri (2018). QMIX: Monotonic Value Function Factorisation](https://arxiv.org/abs/1803.11485) — Monotoniklik ile değer ayrıştırması.
- [Yu ve diğerleri (2022). The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games (MAPPO)](https://arxiv.org/abs/2103.01955) — PPO, MARL için şaşırtıcı derecede güçlüdür.
- [Vinyals ve diğerleri (2019). Grandmaster level in StarCraft II using multi-agent reinforcement learning (AlphaStar)](https://www.nature.com/articles/s41586-019-1724-z) — Büyük ölçekte lig oynaması.
- [Silver ve diğerleri (2017). Mastering the game of Go without human knowledge (AlphaGo Zero)](https://www.nature.com/articles/nature24270) — Sıfır toplamlı oyunlarda saf self-play.
- [Sutton & Barto (2018). Böl. 15 — Nörobilim & Böl. 17 — Önler](http://incompleteideas.net/book/RLbook2020.pdf) — çoklu ajan ortamlarına ve CTDE'nin çözmeye yönelik olduğu durulmazlık sorununa dair ders kitabı kısa değerlendirmesini içerir.
- [Zhang, Yang & Başar (2021). Multi-Agent Reinforcement Learning: A Selective Overview](https://arxiv.org/abs/1911.10635) — işbirlikçi, rekabetçi ve karışık MARL'yi yakınsama sonuçlarıyla kapsayan anket.
