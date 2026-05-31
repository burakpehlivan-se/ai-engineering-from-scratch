# Sim-to-Real Aktarımı

> Bir simülatörde eğitilmiş politikanın donanımda başarısız olması, politikanın simülatörü ezberlediği anlamına gelir. Domain randomization, domain adaptation ve system identification, öğrenilmiş kontrolörlerin reality gap'i aşmasını sağlayan üç araçtır.

**Tür:** Learn
**Diller:** Python
**Önkoşullar:** Phase 9 · 08 (PPO), Phase 2 · 10 (Bias/Variance)
**Süre:** ~45 dakika

## Problem

Gerçek bir robotu eğitmek yavaş, tehlikeli ve pahalıdır. İki ayaklı bir robot yürüme öğrenmek için milyonlarca eğitim bölümü gerektirir; bir kez bile düşen gerçek bir robot donanımı kırar. Simülasyon sınırsız sıfırlama, belirli tekrarlanabilirlik, paralel ortamlar ve fiziksel hasar vermez.

Ama simülatörler yanlıştır. Rulmanlar MuJoCo'nun modellerinden daha sürtünmelidir. Kameraların mercek bozulması simülatörde yoktur. Motorların gecikmeleri, ölü bölgesi (backlash) ve doygunluğu vardır; sim modellerinin %90'ı bunu atlar. Rüzgar, toz ve değişken aydınlatma, steril işleme üzerinde eğitilmiş politikayı sabote eder. **Reality gap** — sim dağılımı ile gerçek dağılım arasındaki sistematik fark — robotik için konuşlandırılmış RL'nin merkezi sorunudur.

*Sim-to-real dağılım kaymasına karşı dayanıklı* bir politikaya ihtiyacın vardır. Üç tarihsel yaklaşım: simülatörü rastgeleleştir (domain randomization), az miktarda gerçek veriyle politikayı uyarla (domain adaptation / fine-tuning) veya gerçek sistemin parametrelerini tanımla ve eşleştir (system identification). 2026'da baskın tarif, üçünü de büyük paralel simülasyonla (Isaac Sim, Isaac Lab, Mujoco MJX GPU üzerinde) birleştirir.

## Kavram

![Üç sim-to-real rejimi: domain randomization, adaptation, system identification](../assets/sim-to-real.svg)

**Domain Randomization (DR).** Tobin ve diğerleri 2017, Peng ve diğerleri 2018. Eğitim sırasında, gerçek robotta farklı olabilecek her sim parametresini rastgeleleştir: kütleler, sürtünme katsayıları, motor PD kazançları, sensör gürültüsü, kamera konumu, aydınlatma, dokular, temas modelleri. Politika, "bugün hangi simülasyonda" üzerine koşullu bir dağılım öğrenir ve tüm aralık boyunca genelleştirir. Gerçek robot eğitim zarfının içindeyse politika çalışır.

- **Artı:** gerçek veri gerekmez. Bir tarif, birçok robot.
- **Eksi:** aşırı rastgeleştirilmiş eğitim, "evrensel" ama aşırı temkinli bir politika üretir. Çok fazla gürültü ≈ çok fazla düzenleyici.

**System Identification (SI).** Eğitimden önce simülatörün parametrelerini gerçek dünya verilerine uydur. Gerçek robotta kol ekleme sürtünmesini ölçebiliyorsan, bunu simülatöre ekle. Sonra bu değerleri bekleyen bir politika eğit. Gerçek sisteme erişim gerektirir ama reality gap'i doğrudan azaltır.

- **Artı:** hassas, düşük gürültülü eğitim hedefi.
- **Eksi:** kalan model hatası politika için görünmezdir; tanımlanmamış küçük etkiler (örn., motor ölü bölgesi) hala konuşlandırmayı bozar.

**Domain Adaptation.** Simülatörde eğit, az miktarda gerçek veriyle ince ayar yap. İki çeşidi:

- **Real2Sim2Real:** gerçek rollout'lardan arta kalan bir simülatör `f(s, a, z) - f_sim(s, a)` öğren, düzeltilmiş simülatörde eğit. Çok fazla gerçek veri olmadan gap'i kapatır.
- **Gözlem adaptasyonu:** gerçek gözlemleri → simülatöre benzer gözlemlere eşleyen bir politika eğit (örn., GAN piksel-to-piksel). Kontrolör simülatörde kalır.

**Ayrıcalıklı öğrenme / öğretmen-öğrenci.** Miki ve diğerleri 2022 (ANYmal dört ayaklı). Simülasyonda ayrıcalıklı bilgiye (gerçek sürtünme, zemin yüksekliği, IMU sapması) erişimi olan bir *öğretmen* eğit. Sadece gerçek-sensör gözlemlerini gören bir *öğrenci*yi damıtır. Öğrenci, fiziksel parametreler boyunca dayanıklı olan tarihçe üzerinden ayrıcalıklı özelliklerin nasıl çıkarılacağını öğrenir.

**Büyük paralel simülasyon.** 2024–2026. Isaac Lab, Mujoco MJX, Brax hepsi tek GPU üzerinde binlerce paralel robot çalıştırır. 4.096 paralel insan robotu ile PPO, saatlerce yıllık deneyim toplar. "Reality gap", eğitim dağılımı genişledikçe daralır; o 4.096 ortamın her birinin farklı rastgeleştirilmiş parametreleri olduğunda DR neredeyse bedavaya gelir.

**Gerçek dünya 2026 tarifi (dört ayaklı yürüme örneği):**

1. Rastgeleştirilmiş kütle, sürtünme, motor kazancı, yük ile büyük paralel sim.
2. Ayrıcalıklı bilgiyle eğitilmiş öğretmen politikası (zemin haritası, gövde hızı gerçek değeri).
3. Sadece propriosepsiyon (bacak eklem kodlayıcıları) kullanan öğretmenden damıtılmış öğrenci politikası.
4. İsteğe bağlı gerçek IMU üzerinde autoencoder ile gözlem adaptasyonu.
5. Konuşlandırma. 10+ ortamda sıfır-atışlı (zero-shot). Başarısız olursa, güvenlik kısıtlı PPO ile birkaç dakika gerçek dünya fine-tuning'i yap.

## Kodu Yaz

Bu dersin kodu, *gürültülü* geçişlere sahip bir GridWorld üzerinde domain randomization'ın küçük bir demosudur. "Simülasyonda" rastgeleleştirilmiş kayma olasılıkları deneyen ve "gerçek" ortamda eğitimin hiç görmediği bir kayma seviyesinde değerlendiren bir politika eğitiriz. Şekil doğrudan MuJoCo'dan donanıma aktarım ile eşleşir.

### Adım 1: parametrize edilmiş simülasyon

```python
def step(state, action, slip):
    if rng.random() < slip:
        action = random_perpendicular(action)
    ...
```

#### Açıklama

`slip`, simülatörün sergilediği bir parametredir. Gerçek robotikte sürtünme, kütle, motor kazancı olabilir — sim ile gerçek arasında değişen her şey.

### Adım 2: DR ile eğit

Her bölümün başında `slip ~ Uniform[0.0, 0.4]` örnekle. PPO / Q-learning / herhangi bir şey eğit. Bunu birçok bölüm için yap.

### Adım 3: "gerçek" kaymalarda sıfır-atışlı değerlendir

`slip ∈ {0.0, 0.1, 0.2, 0.3, 0.5, 0.7}` üzerinde değerlendir. İlk dört eğitim desteği içindedir; `0.5` ve `0.7` dışındadır. DR ile eğitilmiş politika destek içinde en iyiye yakın, dışında zarif bozunma göstermelidir. Sabit kayma ile eğitilmiş politika eğitim dışı kaymada kırılgan olacaktır.

### Adım 4: dar eğitimle karşılaştır

İkinci bir politikayı sadece `slip = 0.0` ile eğit. Aynı `slip` taraması üzerinde değerlendir. Gerçek kayma > 0 olduğunda felaket bir düşüş görmelisin.

## Tuzaklar

- **Çok fazla rastgeleştirme.** `slip ∈ [0, 0.9]` üzerinde eğit ve politikan o kadar risk-korkak olur ki asla en iyi yolu deneme. Beklenen gerçek dünya dağılımını eşleştir, "her şey olabilir" değil.
- **Çok az rastgeleştirme.** İnce bir dilimde eğit ve politika hiç genelleştiremez. Politika geliştikçe dağılımı genişletir.
- **Yanlış tanımlanmış parametre alanı** (gerçek gap motor gecikmesi iken kamera rengini rastgeleleştirirsen) DR yardım etmez. Önce gerçek robotu profille.
- **Ayrıcalıklı bilgi sızması.** Sadece gözlemler değil, küresel durumu aksiyonlar için kullanan bir öğretmen, yetişemeyen bir öğrenci üretebilir. Öğretmen politikasının öğrenci gözlem tarihçesi verildiğinde uygulanabilir olmasını sağla.
- **Sim-to-sim aktarım hatası.** Politikan daha zorlu bir simülatör çeşidine karşı dayanıklı değilse, gerçek dünyaya karşı da dayanıklı olmayacaktır. Konuşlandırmadan önce her zaman tutulmuş bir simülatör çeşidi üzerinde test et.
- **Gerçek dünya güvenlik zarfı yok.** Simülatörde çalışan ve düşük seviye güvenlik kalkanı olmadan "gerçek dünyada da çalışan" bir politika hala donanımı kırabilir. Öğrenilmemiş bir kontrolörde hız sınırları, tork sınırları, eklem sınırları ekle.

## Kullanım

2026 sim-to-real yığını:

| Alan | Yığın |
|--------|-------|
| Ayaklı yürüme (ANYmal, Spot, insan robotu) | Isaac Lab + DR + ayrıcalıklı öğretmen / öğrenci |
| Manipülasyon (el becerikliliği, kapma-yerleştirme) | Isaac Lab + DR + görüntü için DR-GAN |
| Otonom sürüş | CARLA / NVIDIA DRIVE Sim + DR + gerçek fine-tune |
| Drone yarışı | RotorS / Flightmare + DR + çevrimiçi adaptasyon |
| Parmak/iç el manipülasyonu | OpenAI Dactyl (benzersiz ölçekte DR) |
| Endüstriyel kollar | MuJoCo-Warp + SI + küçük gerçek fine-tune |

Tüm ölçeklerde kontrol için iş tutarlıdır: simülatörü mümkün olduğunca iyi uydur, uyduramadığını rastgeleleştir, devasa politikalar eğit, damıt, güvenlik kalkanıyla konuşlandır.

## Ürün Haline Getir

`outputs/skill-sim2real-planner.md` olarak kaydet:

```markdown
---
name: sim2real-planner
description: Belirli bir robot + görev için sim-to-real aktarım hattı planla; DR, SI ve güvenliği kapsar.
version: 1.0.0
phase: 9
lesson: 11
tags: [rl, sim2real, robotics, domain-randomization]
---

Bir robot platformu, bir görev ve gerçek donanım zamanı erişimi verildiğinde, output et:

1. Reality gap envanteri. Beklenen etkiye göre sıralanmış şüpheli kaynaklar (temas, algılama, eylem gecikmesi, görüntü).
2. DR parametreleri. Kesin liste, aralıklar, dağılım. Her aralığı gerçek ölçümlerle gerekçelendir.
3. SI adımları. Hangi parametreler ölçülecek; ölçüm yöntemi.
4. Öğrenci/öğretmen ayrımı. Öğretmenin kullandığı ayrıcalıklı bilgi; öğrencinin kullandığı gözlemler.
5. Güvenlik zarfı. Düşük seviye sınırları, acil durdurma, yedek kontrolör.

(a) sıfır-atışlı sim-çeşidi testi, (b) güvenlik kalkanı, (c) geri alma planı olmadan konuşlandırmayı reddet. Ölçülmüş gerçek değişkenliğin 3×'inden geniş herhangi bir DR aralığını muhtemelen aşırı rastgeleştirilmiş olarak işaretle.
```

## Alıştırmalar

1. **Kolay.** Sabit kaymalı GridWorld'de (slip=0.0) bir Q-learning ajanı eğit. slip ∈ {0.0, 0.1, 0.3, 0.5} üzerinde değerlendir. Getiriyi kaymaya göre çiz.
2. **Orta.** `slip ~ Uniform[0, 0.3]` örnekleme yapan bir DR Q-learning ajanı eğit. Aynı taramayı değerlendir. slip=0.5'te (dağılım dışında) DR ne kadar kazandırır?
3. **Zor.** Müfredat uygula: slip=0.0 ile başla, politika %90 optimal'e her ulaştığında DR aralığını genişlet. Sıfır-atışlı slip=0.3'e ulaşmak için toplam ortam adımını sabit DR baseline'ı ile karşılaştır.

## Anahtar Terimler

| Terim | İnsanlar ne der | Gerçekte ne anlama gelir |
|------|-----------------|-----------------------|
| Reality gap | "Sim-to-real farkı" | Eğitim ve konuşlandırma fiziği/algılaması arasındaki dağılım kayması. |
| Domain randomization (DR) | "Rastgele simülasyonlarda eğit" | Eğitim sırasında sim parametrelerini rastgeleleştirerek politikanın genelleştirmesini sağla. |
| System identification (SI) | "Gerçeği ölç ve simülatörü uydur" | Gerçek fiziksel parametreleri tahmin et; simülatörü eşleştir. |
| Domain adaptation | "Gerçek veriyle ince ayar" | Sim eğitimi sonrası küçük bir gerçek dünya ince ayarlaması; gözlemleri veya dinamikleri uyarlayabilir. |
| Ayrıcalıklı bilgi | "Öğretmen için gerçek değer" | Sadece simülatörün sahip olduğu bilgi; öğrenci bunu gözlem tarihçesinden çıkarmalıdır. |
| Öğretmen/öğrenci | "Ayrıcalıklı → gözlemlenebilir olarak damıt" | Öğretmen kısayollarla eğitilir; öğrenci bunlar olmadan taklit etmeyi öğrenir. |
| ADR | "Otomatik Domain Randomization" | Politika geliştikçe DR aralıklarını genişleten müfredat. |
| Real2Sim | "Gerçek veriyle gap'i kapat" | Simülatörün gerçek rollout'ları taklit etmesini sağlamak için arta kalan öğren. |

## İleri Okuma

- [Tobin ve diğerleri (2017). Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World](https://arxiv.org/abs/1703.06907) — orijinal DR makalesi (robotik için görüntü).
- [Peng ve diğerleri (2018). Sim-to-Real Transfer of Robotic Control with Dynamics Randomization](https://arxiv.org/abs/1710.06537) — Dinamikler için DR, dört ayaklı yürüme.
- [OpenAI ve diğerleri (2019). Solving Rubik's Cube with a Robot Hand](https://arxiv.org/abs/1910.07113) — Dactyl, büyük ölçekte ADR.
- [Miki ve diğerleri (2022). Learning robust perceptive locomotion for quadrupedal robots in the wild](https://www.science.org/doi/10.1126/scirobotics.abk2822) — ANYmal için öğretmen-öğrenci.
- [Makoviychuk ve diğerleri (2021). Isaac Gym: High Performance GPU Based Physics Simulation for Robot Learning](https://arxiv.org/abs/2108.10470) — 2025–2026 konuşlandırmalarını yönlendiren büyük paralel simülasyon.
- [Akkaya ve diğerleri (2019). Automatic Domain Randomization](https://arxiv.org/abs/1910.07113) — ADR müfredat yöntemi.
- [Sutton & Barto (2018). Böl. 8 — Tablolarla Planlama ve Öğrenme](http://incompleteideas.net/book/RLbook2020.pdf) — modern sim-to-real hatlarını destekleyen Dyna çerçevesi (planlama + rollout için bir model kullanma).
- [Zhao, Queralta & Westerlund (2020). Sim-to-Real Transfer in Deep Reinforcement Learning for Robotics: a Survey](https://arxiv.org/abs/2009.13303) — benchmark sonuçlarıyla sim-to-real yöntemlerinin sınıflandırması.
