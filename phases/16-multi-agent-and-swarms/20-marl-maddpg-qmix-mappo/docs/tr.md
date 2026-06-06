# MARL — MADDPG, QMIX, MAPPO

> Çok-ajanlı koordinasyonun takviyeli-öğrenme (RL) mirası, 2026'da hâlâ LLM-ajan sistemlerini bilgilendiriyor. **MADDPG** (Lowe ve diğerleri, NeurIPS 2017, arXiv:1706.02275) Merkezileştirilmiş Eğitim, Merkezsiz Yürütme (CTDE, Centralized Training, Decentralized Execution) kavramını tanıttı: eğitim sırasında her eleştirmen (critic) tüm ajanların durum ve eylemlerini görür; test zamanında yalnızca yerel aktörler çalışır. İşbirlikçi, rekabetçi ve karışık ayarlar için çalışır. **QMIX** (Rashid ve diğerleri, ICML 2018, arXiv:1803.11485), monoton bir karıştırma ağı (mixing network) ile değer ayrıştırmasıdır (value decomposition); ajan başına Q'lar ortak Q'ya birleşir, böylece `argmax` temiz biçimde dağıtılır — StarCraft Multi-Agent Challenge (SMAC) üzerinde baskındır. **MAPPO** (Yu ve diğerleri, NeurIPS 2022, arXiv:2103.01955), merkezileştirilmiş bir değer fonksiyonuyla PPO'dur; minimum ayarla "şaşırtıcı derecede etkili" — particle-world, SMAC, Google Research Football, Hanabi'de. Bunlar, merkezsiz hareket etmesi gereken ajan takımları için politikaları eğitmenin temelini oluşturur. MAPPO **2026 varsayılan işbirlikçi-MARL temel çizgisidir**. Bu ders her birini küçük bir grid-world oyuncağından inşa eder ve bir LLM-ajan eğitimine dokunmadan önce üç fikri kas hafızasına yerleştirir.

**Tip:** Öğren
**Diller:** Python (stdlib, küçük NumPy'siz uygulamalar)
**Önkoşullar:** Faz 09 (Pekiştirmeli Öğrenme), Faz 16 · 09 (Paralel Sürü Ağları)
**Süre:** ~90 dakika

## Problem

LLM-ajan sistemleri, ajanlar arası koordinasyon için giderek daha fazla politika eğitir: ne zaman ertelenecek, ne zaman hareket edilecek, hangi akran çağrılacak. Bu tür politikaları nasıl eğiteceğinizi söyleyen literatür, LLM dalgasından önce gelen ve baskın algoritmaların küçük bir kümesine sahip olan Çok-Ajanlı Pekiştirmeli Öğrenmedir (MARL, Multi-Agent Reinforcement Learning).

MARL makalelerini örüntü kelime hazinesi olmadan okumak acı vericidir. Merkezileştirilmiş eğitim ve merkezsiz yürütme (CTDE), değer ayrıştırması ve merkezileştirilmiş eleştirmenler (critics) boş kelimeler değildir — belirli sorunlara belirli yanıtlardır:

- Bağımsız RL (her ajan tek başına öğrenir) her ajanın perspektifinden durağan değildir. Kötü.
- Merkezileştirilmiş RL (tek bir ajan tümünü kontrol eder) ölçeklenmez ve yürütme kısıtlarını ihlal eder.
- CTDE, ikisinin en iyisini alır: küresel bilgiyle eğit, yerel politikalarla dağıt.

## Kavram

### Makalelerin kullandığı üç ortam

- **Particle World (çok-ajanlı parçacık ortamı).** İşbirlikçi/rekabetçi görevlerle basit 2B fizik. MADDPG'nin özgün test yatağı.
- **StarCraft Multi-Agent Challenge (SMAC).** İşbirlikçi mikro-yönetim, kısmi gözlem. QMIX'in test yatağı. Ayrık eylemler, sürekli durumlar.
- **Google Research Football, Hanabi, MPE.** MAPPO temel çizgileri.

Farklı ortamların farklı eylem/gözlem türleri vardır. Algoritmalar buna göre seçim yapar.

### MADDPG (2017) — CTDE kalıbı

Her ajan `i`'nin kendi gözlemini eyleme eşleyen bir aktörü `mu_i(o_i)` vardır. Her ajanın ayrıca eğitim sırasında tüm gözlemleri ve tüm eylemleri gören bir eleştirmeni `Q_i(x, a_1, ..., a_n)` vardır. Aktör, eleştirmenin değerlendirmesine karşı politika gradyanı ile güncellenir.

```
aktör güncelleme:   grad_theta_i J = E[grad_theta mu_i(o_i) * grad_a_i Q_i(x, a_1..n) at a_i=mu_i(o_i)]
eleştirmen güncelleme: TD on Q_i(x, a_1..n) bir sonraki-durum ortak tahmini verildiğinde
```

#### Açıklama
Neden CTDE: eğitim zamanında herkesin eylemlerini biliriz; her eleştirmendeki varyansı azaltmak için bunu kullanırız. Dağıtım zamanında her ajan yalnızca `o_i` görür ve `mu_i(o_i)` çağırır.

Başarısızlık kipi: eleştirmenler N ajanla büyür (girdi tüm eylemleri içerir). Yaklaşıklıklar olmadan ~10 ajanın ötesinde ölçeklenmez.

### QMIX (2018) — değer ayrıştırması

Yalnızca işbirlikçi. Küresel ödül, ajan başına Q-değerlerinin monoton bir fonksiyonunun toplamıdır:

```
Q_top(tau, a) = f(Q_1(tau_1, a_1), ..., Q_n(tau_n, a_n)),   df/dQ_i >= 0
```

#### Açıklama
Monotonluk, `argmax_a Q_top`'un her ajanın bağımsız olarak `argmax_{a_i} Q_i` seçmesiyle hesaplanabileceğini garanti eder. Bu, tam olarak ihtiyacınız olan **merkezsiz yürütme özelliğidir**. Eğitim zamanında, bir karıştırma ağı (mixing network) ajan başına Q'lardan `Q_top` üretir.

QMIX'in SMAC'ta neden kazandığı: işbirlikçi StarCraft mikro-yönetimi homojen ajanlara, yerel gözlemlere, küresel ödüle sahiptir — değer ayrıştırması için mükemmel uyum.

Başarısızlık kipi: monotonluk kısıtı kısıtlayıcıdır; bazı görevlerde ödül yapıları monoton olarak ayrıştırılamaz (bir ajan takım için kendini feda eder). Uzantılar (QTRAN, QPLEX) bunu gevşetir.

### MAPPO (2022) — gözden kaçan varsayılan

Çok-Ajanlı PPO: merkezileştirilmiş bir değer fonksiyonuyla PPO. Her ajanın kendi politikası vardır; tüm ajanlar tam durumu gören değer fonksiyonlarını paylaşır (veya ajan başınadır). Yu ve diğerleri 2022, MAPPO'yu beş kıyaslamada MADDPG, QMIX ve uzantılarına karşı kıyasladı ve şunu buldu:

- MAPPO, particle-world, SMAC, Google Research Football, Hanabi, MPE'de politika-dışı (off-policy) MARL yöntemlerine eşit veya üstündür.
- Minimum hiperparametre ayarı gerekir.
- Kararlı eğitim; tohumlar arasında tekrarlanabilir.

Topluluk, politika-içi (on-policy) MARL'yi bu makaleye kadar küçümsedi. 2026'da MAPPO, işbirlikçi MARL için varsayılan temel çizgidir; herhangi bir yeni yöntem onu yenmelidir.

### LLM-ajan mühendislerinin neden önemsemesi gerektiği

Üç doğrudan kullanım:

1. **Yönlendirici (router) eğitimi.** Bir meta-ajan, bir görevi hangi alt-ajanın ele alacağını seçer. Bu, N merkezsiz alt-ajanlı ve bir merkezileştirilmiş yönlendiricili bir MARL problemidir. MAPPO uyar.
2. **Rol ortaya çıkışı.** Üretken-ajan simülasyonlarında, ajanları zamanla tamamlayıcı roller benimsemeye eğitmek gizlenmiş bir MARL problemidir. QMIX tarzı değer ayrıştırması tamamlayıcılığı yapısal olarak zorlar.
3. **Çok-ajanlı araç kullanımı.** Ajanlar araçları paylaştığında ve bütçe için rekabet ettiğinde, CTDE ile eğitim kaynak kısıtlarına saygı gösteren dağıtılabilir yerel politikalar üretir.

Pratik uyarı: 2026'da, çoğu üretim LLM-ajan sistemi politikalarını eğitmek yerine istem yazar. MARL şu durumlarda devreye girer: (a) çok etkileşim verisi, (b) net bir ödül sinyali ve (c) eğitim altyapısına yatırım isteği.

### CTDE, RL ötesinde bir tasarım kalıbı olarak

Eğitim olmadan bile, CTDE yararlı bir mimari kalıptır:

- *Tasarım* sırasında, tam takım görünürlüğü varsayın.
- *Çalışma zamanında*, merkezsiz yürütme uygulayın: her ajan yalnızca `o_i` görür.

Kalıp, ajan başına durumu açık tutmaya ve kısmi gözlenebilirliği önceden düşünmeye zorlar. Birçok üretim multi-agent sistemi her yerde paylaşılan durum varsayar — CTDE disiplini bunu önler.

### Durağan-olmama (non-stationarity) problemi

Birden fazla ajan aynı anda öğrendiğinde, her ajanın ortamı (diğerlerinin politikalarını içerir) durağan değildir. Klasik tek-ajanlı RL ispatları bozulur. Bu dersteki MARL algoritmalarının tümü bunu ele alır:

- MADDPG: küresel eleştirmen tüm eylemleri görür, böylece değer tahmini durağandır.
- QMIX: değer ayrıştırması öğrenmeyi, en iyi noktanın iyi tanımlandığı ortak-Q uzayına taşır.
- MAPPO: merkezileştirilmiş değer fonksiyonu, diğerlerinin politika değişikliklerinden gelen varyansı söndürür.

LLM-ajan sistemlerinde, durağan-olmama "ajanım geçen ay çalıştı, şimdi yukarı akıştaki başka bir ajan değişti, benimki bozuldu" olarak ortaya çıkar. CTDE ile MARL eğitimi ilkeli çözümdür; istem-düzeyinde çözümler daha hızlıdır ama daha az dayanıklıdır.

### Bu dersin KAPSAMADIĞI konular

Gerçek ağları eğitmek bir Faz 09 konusudur. Bu ders, gradyan güncellemeleri olmadan CTDE, değer ayrıştırması ve merkezileştirilmiş-değer kalıplarını gösteren komut-dosyalı politika sürümlerini inşa eder. Amaç, tam bir MARL kitaplığı (PyMARL, MARLlib, RLlib multi-agent) almadan önce kalıpları içselleştirmektir.

## İnşa Et

`code/main.py` üç kalıp gösterimi uygular, tümü küçük bir 2-ajanlı işbirlikçi grid-world üzerinde:

- Ortam: 4x4 grid üzerinde 2 ajan, bir ödül pellet'i. Bir ajan pellet'e ulaşırsa ödül = 1; görev biter.
- `IndependentAgents` — her ajan diğerlerini ortam olarak ele alır. Temel çizgi.
- `MADDPGStyle` — merkezileştirilmiş eleştirmen ortak bir değer hesaplar; aktör politikaları ondan güncellenir. Komut-dosyalı politika iyileştirmesi.
- `QMIXStyle` — monoton karıştırıcıyla değer ayrıştırması.
- `MAPPOStyle` — merkezileştirilmiş değer fonksiyonu; politikalar paylaşılan temel çizgiye karşı güncellenir.

Dördü de aynı bölümleri çalıştırır ve ortalama adım-hedef sayısını raporlar. CTDE varyantları, bağımsız temel çizgiden daha kısa yollara yakınsar.

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı: bağımsız ajanlar ortalama ~6 adım; CTDE varyantları ~3,5 adıma yakınsar (4x4 grid için en iyi 3). Kalıp farkı, komut-dosyalı politikalara rağmen ortaya çıkar.

## Kullan

`outputs/skill-marl-picker.md`, belirli bir çok-ajanlı görev için (işbirlikçi vs rekabetçi, homojen vs heterojen, eylem-uzayı türü, ölçek, ödül sinyali) bir MARL algoritması seçen bir beceridir.

## Yayınla

Üretimde MARL nadirdir. Kullandığınızda:

- **MAPPO ile başlayın.** 2022 makalesi bunu temel çizgi olarak belirledi; önce yeniden üretmek haftalarca daha süslü yöntemleri kovalamaktan kurtarır.
- **Her ajanın gözlem ve eylem akışını kaydedin.** Ajan başına izler olmadan MARL'da hata ayıklamak umutsuzdur.
- **Eğitim kodunu yürütme kodundan ayırın.** CTDE bir disiplindir; yürütme yolunun gerçekten yalnızca `o_i` gördüğüne izin verin.
- **Ödül şekillendirme uyarısı.** MARL, ödül tasarımına aşırı duyarlıdır. Şekillendirmede bir koordinasyon hatası ve ajanlar onu sömürmeyi öğrenir. Düşmanca testler çalıştırın.
- **LLM ajanları için**, önce istem-düzeyinde politikaları düşünün. Etkileşim verisi + ödül sinyali + altyapının tümü mevcut olduğunda yalnızca MARL eğitimine yatırım yapın.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Bağımsız ve MAPPO tarzı ajanlar arasındaki adım-hedef farkını ölçün. 6x6 grid'de fark büyüyor mu, küçülüyor mu?
2. Rekabetçi bir varyant uygulayın: iki ajan, bir pellet, yalnızca ilk ulaşan ödül alır. Hangi kalıp rekabeti temiz biçimde ele alır? Tarihsel olarak MADDPG.
3. MADDPG'yi (arXiv:1706.02275) Bölüm 3'ü okuyun. Tam eleştirmen güncelleme kuralını kendi kelimelerinizle sembolik olarak sözde-kodda uygulayın.
4. MAPPO'yu (arXiv:2103.01955) okuyun. Yazarlar neden merkezileştirilmiş değer + PPO'nun kıyaslamalarında politika-dışı MARL'yi yendiğini savunuyor? En güçlü üç iddiayı listeleyin.
5. CTDE'yi varsayımsal bir LLM-ajan sistemine (örn. araştırma ajanı + özetleyici + kodlayıcı) tasarım kalıbı olarak uygulayın. Çalışma zamanında mevcut olmayan, tasarım zamanında mevcut olan ortak bilgi nedir?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| MARL | "Çok-Ajanlı RL" | Çok-ajanlı sistemler için pekiştirmeli öğrenme. |
| CTDE | "Merkezileştirilmiş Eğitim, Merkezsiz Yürütme" | Küresel bilgiyle eğit, yerel politikalarla dağıt. |
| MADDPG | "Çok-Ajanlı DDPG" | Tüm gözlem + eylemleri gören ajan başına eleştirmenle CTDE. |
| QMIX | "Değer ayrıştırması" | Ajan başına Q'ların monoton karışımı. İşbirlikçi. |
| MAPPO | "Çok-Ajanlı PPO" | Merkezileştirilmiş değer fonksiyonuyla PPO. 2026 varsayılan temel çizgisi. |
| Değer ayrıştırması | "Bireysel Q'ların toplamı" | Ortak Q, ajan başına Q'ların monoton fonksiyonu olarak temsil edilir. |
| Durağan-olmama | "Hareketli hedefler" | Diğerleri öğrendikçe her ajanın ortamı değişir. Temel MARL problemi. |
| Politika-içi / politika-dışı | "Mevcut / yeniden oynatmadan öğren" | PPO politika-içidir (MAPPO); DDPG ve Q-öğrenme politika-dışıdır. |
| SMAC | "StarCraft Çok-Ajanlı Meydan Okuması" | İşbirlikçi mikro-yönetim kıyaslaması; QMIX'in yetiştiği yer. |

## İleri Okuma

- [Lowe et al. — Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments](https://arxiv.org/abs/1706.02275) — MADDPG; NeurIPS 2017
- [Rashid et al. — QMIX: Monotonic Value Function Factorisation for Deep Multi-Agent Reinforcement Learning](https://arxiv.org/abs/1803.11485) — QMIX; ICML 2018
- [Yu et al. — The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games](https://arxiv.org/abs/2103.01955) — MAPPO; NeurIPS 2022
- [BAIR blog yazısı MAPPO üzerine](https://bair.berkeley.edu/blog/2021/07/14/mappo/) — MAPPO sonucunun okunabilir çerçevesi
- [SMAC deposu](https://github.com/oxwhirl/smac) — StarCraft Çok-Ajanlı Meydan Okuması
