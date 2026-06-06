# LLM'ler İçin Sürü Optimizasyonu (PSO, ACO)

> Biyolojiden esinlenen optimizasyon, LLM'lerde geri dönüş yapıyor. **LMPSO** (arXiv:2504.09247), her parçacığın hızının bir istem (prompt) olduğu ve LLM'nin bir sonraki adayı ürettiği PSO'yu kullanır; yapılandırılmış-dizi çıktılarında (matematiksel ifadeler, programlar) iyi çalışır. **Model Swarms** (arXiv:2410.11163) her LLM uzmanını model-ağırlık manifoldundaki bir PSO parçacığı olarak ele alır ve 9 veri kümesinde 12 temel çizgiye karşı yalnızca 200 örneklemle **%13,3 ortalama kazanç** bildirir. **SwarmPrompt** (ICAART 2025) prompt optimizasyonu için PSO + Grey Wolf'ü melezler. **AMRO-S** (arXiv:2603.12933), çok-ajanlı LLM yönlendirmesi (routing) için feromon uzmanlarından esinlenen ACO-tabanlı bir yönlendiricidir — **4,7x hızlanma**, yorumlanabilir yönlendirme kanıtı, çıkarımı öğrenmeden ayıran kalite-kapılı asenkron güncelleme. Bu ders istem parametre uzayında PSO'yu ve ajan yönlendirmesinde ACO'yu uygular, bu klasik algoritmaların neden LLM çağına uyduğunu ve nerede uymadığını ölçer.

**Tip:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Önkoşullar:** Faz 16 · 09 (Paralel Sürü Ağları), Faz 16 · 14 (Konsensüs ve BFT)
**Süre:** ~75 dakika

## Problem

Görev değerlendirmenizde %62 puan alan bir isteminiz (prompt) var. Onu iyileştirmek istiyorsunuz. Saf yaklaşım manuel ince ayardır ve kötü ölçeklenir. Pekiştirmeli öğrenme (RL) ödül sinyalleri ve eğitim için yeterli koşuma ihtiyaç duyar. İstemlerden geri yayılım (backprop) gerçekten mümkün değildir — istem ayrık bir dizedir, türetilebilir bir parametre değil.

Klasik biyolojiden-esinlenen optimizasyon — sürekli arama uzayları için PSO, yol seçimi için ACO — tam olarak bu rejim için tasarlandı: gradsız, popülasyon-tabanlı, değerlendirme başına ucuz. Gradsız arama adımı için LLM'lerle eşleştirin ve şaşırtıcı derecede pratik bir optimize edici elde edin.

Aynı kalıplar multi-agent sistemlerde ajan *yönlendirmesine* (routing) uygulanır. ACO tarzı bir feromon izi, hangi ajanın hangi görev türünde en iyi çalıştığını kaydeder, yönlendiricinin izi sömürmesine izin verir ve yolların yeniden keşfedilebilmesi için feromonları bozundurur.

## Kavram

### PSO hatırlatıcısı (Kennedy & Eberhart 1995)

Parçacık Sürüsü Optimizasyonu (Particle Swarm Optimization): sürekli arama uzayında bir parçacık popülasyonu. Her parçacığın konumu `x_i` ve hızı `v_i` vardır. Her iterasyon:

```
v_i <- w * v_i + c1 * r1 * (p_en_iyi_i - x_i) + c2 * r2 * (g_en_iyi - x_i)
x_i <- x_i + v_i
uygunluk(x_i) değerlendir
iyileştiyse p_en_iyi_i güncelle
iyileştiyse g_en_iyi güncelle
```

#### Açıklama
Burada `p_en_iyi` parçacığın kendi en iyisi, `g_en_iyi` sürünün en iyisi, `w, c1, c2` atalet + bilişsel + sosyal ağırlıklar, `r1, r2` rastgele faktörlerdir.

### LLM çıktıları üzerinde PSO — LMPSO

arXiv:2504.09247, PSO'yu LLM tarafından üretilen yapılandırılmış çıktılar (matematiksel ifadeler, programlar) için uyarlar. Her parçacık bir aday çıktıdır. Hız, mevcut çıktıyı kişisel/küresel en iyiye doğru nasıl değiştireceğini tanımlayan bir *istemdir*. LLM, hız isteminden yeni çıktıyı üretir. Hızın "ataleti" "küçük artımlı değişiklikler yap" gibi bir istemdir.

Bu şu durumlarda iyi çalışır:
- Çıktı yapılandırılmıştır (ayrıştırılabilir, değerlendirilebilir).
- Uygunluk otomatiktir (test koşumları, aritmetik değerlendirme).
- Popülasyon küçüktür (~10-30 parçacık) böylece toplam LLM çağrıları yönetilebilir kalır.

Uygunluk insan incelemesi gerektirdiğinde iyi çalışmaz — iterasyon başına maliyet yasaklayıcı olur.

### Model Swarms

arXiv:2410.11163, PSO'yu çıktı katmanından *model* katmanına taşır. Her "parçacık" bir uzman LLM'dir (parametreler). Sürü, gradsız bir güncelleme ile parametreleri kolektif en iyiye doğru hareket ettirir. Bildirilen: 9 veri kümesinde 12 temel çizgiye karşı ortalama %13,3 kazanç, iterasyon başına yalnızca 200 örneklemle.

Temel içgörü: LLM uzman modelleri zaten paylaşılan bir parametre manifoldunda (adaptör ağırlıkları, LoRA deltaları) birbirine yakındır. Bu düşük-boyutlu alt uzayda PSO ucuz ve etkilidir.

### ACO hatırlatıcısı (Dorigo 1992)

Karınca Kolonisi Optimizasyonu (Ant Colony Optimization): karıncalar bir grafiği geçer; her yolun bir feromon izi vardır. Karınca hareket olasılıkları feromon gücüyle ağırlıklandırılır. Görevi tamamlayan karıncalar çözüm kalitesiyle orantılı feromon bırakır. Feromon zamanla bozunur.

### AMRO-S — ajan yönlendirmesi için ACO

arXiv:2603.12933, çok-ajanlı yönlendirme için ACO kullanır. Her görev türü bir "hedef"tir; her ajan olası bir yoldur. Feromonlar iyi çıktılar üreten yolları güçlendirir. Temel katkılar:

- **Yorumlanabilir yönlendirme kanıtı.** Feromon gücü insan-okunabilir bir sinyaldir.
- **Kalite-kapılı asenkron güncelleme.** Feromonlar yalnızca kalite kontrolleri geçtikten sonra güncellenir, çıkarımı öğrenmeden ayırır.
- **Çok-ajanlı yönlendirme kıyaslamasında **4,7x hızlanma**.

Kalite kapısı önemlidir: onsuz, hızlı-ama-yanlış ajanlar feromon biriktirir ve sistem kötü yollara kilitlenir.

### LLM'ler için PSO / ACO ne zaman kullanılır

**Şu durumda PSO kullanın:**
- Arama uzayı süreklidir veya sürekli parametrelere eşlenir (istem gömmeleri, LoRA ağırlıkları, sayısal üretim parametreleri).
- Uygunluk ucuz ve otomatiktir.
- Popülasyon küçük olabilir (10-30).

**Şu durumda ACO kullanın:**
- Bir yönlendirme veya yol-seçimi probleminiz var.
- Kararlar zaman içinde güçlenir (aynı görev türleri tekrarlanır).
- Yönlendirme kararları için yorumlanabilir kanıta ihtiyacınız var.

**Şu durumlarda hiçbirini kullanmayın:**
- Uygunluk insan incelemesi gerektirir (iterasyon başına çok pahalı).
- Arama uzayı PSO'nün kapsamadığı biçimde ayrık ve kombinatoryaldir (bunun yerine genetik algoritmalar).
- Gerçek-zamanlı kararlar sıkı gecikme gerektirir (PSO/ACO tek-geçişli sezgisellere göre yavaş yakınsar).

### Biyolojiden esinlenen neden hâlâ kazanıyor

Gradyan-tabanlı yöntemler türetilebilir sinyallere ihtiyaç duyar. LLM çıktıları ve yönlendirme kararları trivial biçimde türetilebilir değildir. Sözde-gradyan yöntemler (RL-öğrenilmiş yönlendiriciler, DPO tarzı istem ayarlayıcılar) çalışır ama pahalı eğitim gerektirir.

PSO ve ACO yalnızca bir *değerlendirici* fonksiyon gerektirir. Bir aday çıktıyı veya yönlendirme kararını puanlayabiliyorsanız, uzay üzerinde optimize edebilirsiniz. Bu, uygulanabilirlik çıtasını çok düşürür.

### Pratik sınırlar

- **Popülasyon bütçesi.** N parçacık × T iterasyon × değerlendirme-başına maliyet. ~0,02$/çağrı LLM değerlendirmelerinde, 20 parçacıklı ve 50 iterasyonlu PSO ~20$ maliyetle çalışır. Buna göre planlayın.
- **Keşif vs sömürü.** Feromon bozunma oranı ve PSO ataleti bir değiş-tokuştur; çok hızlı bozunma → çözümleri unutma; çok yavaş → erken yerel en iyi noktalara takılma.
- **Yıkıcı kayma (catastrophic drift).** Her iki algoritma de yakınsayıp sonra uygunluk arazisi değişirse (yeni veri dağılımı) sapabilir. En iyi-uygunluk kararlılığını izleyin.

## İnşa Et

`code/main.py` şunları uygular:

- `LMPSO` — sayısal istem parametreleri (sıcaklık, top_k ağırlıkları) üzerinde PSO. Her parçacığın "LLM üretimi" komut-dosyalı bir uygunluk fonksiyonu olarak simüle edilir. Algoritmayı 30 iterasyon çalıştırır ve g_en_iyi yakınsamasını gösterir.
- `AMRO_S` — ACO tarzı yönlendirme. 3 ajan, 4 görev türü, feromon matrisi, 100 yönlendirilmiş görev. İz oluşumunu göstermek için zaman içinde (görev_türü → ajan seçimleri) dağılımını yazdırır.
- Karşılaştırma: aynı görev akışı üzerinde rastgele yönlendirme vs ACO yönlendirme. Kalite ve gecikmeyi ölçer.

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı:
- LMPSO: g_en_iyi uygunluğu 30 iterasyonda rastgeleden optimale yakın iyileşir.
- AMRO-S: feromon tablosu görev türü başına doğru ajan üzerinde dengelenir; ACO yönlendirme kalitede rastgeleyi ~%30-40 yener ve ayrıca gecikmeyi azaltır (daha az yeniden deneme).

## Kullan

`outputs/skill-swarm-optimizer.md`, LLM / ajan optimizasyon problemleri için PSO, ACO, genetik algoritmalar ve gradyan-tabanlı optimize ediciler arasında seçim yapmaya yardımcı olur.

## Yayınla

- **Küçük başlayın.** 10-20 parçacık, 20-50 iterasyon. Yakınsama eğrisi net kazanç gösteriyorsa ölçeklendirin.
- **İterasyon başına feromonları veya g_en_iyi değerini kaydedin.** İz olmadan sürü optimize edicilerinde hata ayıklamak acı vericidir.
- **Kalite-kapılı güncellemeler.** Özellikle ACO yönlendirmesi için: hızlı-ve-yanlış ajanlar feromon biriktirmemelidir.
- **Dağılım kaymasında bozunmayı sıfırlayın.** Değerlendirme dağılımınız değiştiğinde, eski feromonlar bayat olur; geçici olarak sıfırlayın veya bozunma oranını ikiye katlayın.
- **İterasyon başına maliyeti sınırlayın.** İterasyon başına maliyet metriği yayınlayın. İterasyon başına 500$ maliyetleyen ve %0,5 kazanan PSO gönderilebilir değildir.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. LMPSO yakınsamasını gözlemleyin. Popülasyon boyutunu 5, 10, 20, 50 olarak değiştirin. Yakınsama süresi hangi boyutta doygunlaşır?
2. Bir "yıkıcı kayma" deneyi uygulayın: iterasyon 30'dan sonra uygunluk fonksiyonunu değiştirin. PSO ne kadar hızlı uyum sağlar? `p_en_iyi`'yi sıfırlamak yardımcı olur mu?
3. AMRO-S'e bir kalite kapısı ekleyin: yalnızca değerlendirme puanı > 0,7 olan koşularda feromon bırakın. Bu, kapısız sürüme karşı yakınsamayı nasıl değiştirir?
4. LMPSO'yu (arXiv:2504.09247) okuyun. Makalenin "hız olarak istem" kavramını kendi sayısal hızınıza geri eşleyin. Simülasyonda ne kaybolur, ne korunur?
5. AMRO-S'i (arXiv:2603.12933) okuyun. Asenkron feromon güncellemesiyle ayrıştırılmış "çıkarım hızlı yolu"nu uygulayın. Bu, sürekli yük altında sistem gecikmesini nasıl değiştirir?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| PSO | "Parçacık Sürüsü Optimizasyonu" | Kennedy-Eberhart 1995. Popülasyon-tabanlı gradsız optimize edici. |
| ACO | "Karınca Kolonisi Optimizasyonu" | Dorigo 1992. Feromon izleriyle yol/yönlendirme optimizasyonu. |
| LMPSO | "LLM üretimiyle PSO" | arXiv:2504.09247. Hız bir istemdir; LLM adayları üretir. |
| Model Swarms | "Uzman ağırlıklarında PSO" | arXiv:2410.11163. Model parametre alt uzayında gradsız güncelleme. |
| AMRO-S | "Ajan yönlendirmesi için ACO" | arXiv:2603.12933. Görev türü × ajan üzerinde feromon matrisi. |
| p_en_iyi / g_en_iyi | "Kişisel / küresel en iyi" | Parçacık başına ve sürü çapında şimdiye kadar bulunan en iyi çözümler. |
| Feromon | "Yönlendirme belleği" | Bir kenardaki güç; zamanla bozunur; kalite üzerine bırakılır. |
| Kalite-kapılı güncelleme | "Yalnızca iyi koşulardan öğren" | Kalite kontrolüne bağlı feromon bırakma. |
| Yıkıcı kayma | "Dağılım kayması" | Uygunluk arazisi değişir; eski p_en_iyi ve feromonlar bayat olur. |

## İleri Okuma

- [Kennedy & Eberhart — Particle Swarm Optimization](https://ieeexplore.ieee.org/document/488968) — 1995 PSO makalesi
- [Dorigo — Ant Colony Optimization](https://www.aco-metaheuristic.org/about.html) — 1992 ACO temelleri
- [LMPSO — Language Model Particle Swarm Optimization](https://arxiv.org/abs/2504.09247) — yapılandırılmış LLM çıktıları için PSO
- [Model Swarms — gradsız LLM uzman optimizasyonu](https://arxiv.org/abs/2410.11163) — model ağırlık alt uzayında PSO
- [AMRO-S — karınca-kolonisi çok-ajanlı yönlendirme](https://arxiv.org/abs/2603.12933) — kalite kapılı feromon-tahrikli yönlendirme
