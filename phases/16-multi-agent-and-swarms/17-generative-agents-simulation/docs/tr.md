# Üretken Ajanlar ve Ortaya Çıkan Simülasyon

> Park ve diğerleri 2023 (UIST '23, arXiv:2304.03442) **Smallville**'ı (25 ajanlı bir sandbox) üç parçalı bir mimariyle doldurdu: **bellek akışı** (memory stream, doğal-dil günlüğü), **yansıma** (reflection, ajanın kendi akışı hakkında ürettiği üst-düzey sentezler) ve **plan** (gün-düzeyinde davranış, sonra alt-planlar). Dönüm noktası sonucu Sevgililer Günü partisinin ortaya çıkışıydı: "Sevgililer Günü partisi vermek istiyor" diye tohumlanan bir ajan, başka komut dosyası olmadan, nüfusa yayılan davetler, koordine edilen tarihler üretti ve parti gerçekleşti — başlangıçta bu konuda hiçbir bilgisi olmayan 24 ajandan. Ablasyon çalışmaları inandırıcılık için üç bileşenin de gerekli olduğunu gösterir. Belgelenen başarısızlıklar uzamsal-norm hatalarıdır (kapalı mağazalara girmek, tek-kişilik banyoları paylaşmak). Bu, 2026'da ajan simülasyonları ve çok-ajanlı sosyal değerlendirme için referans mimaridir.

**Tip:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Önkoşullar:** Faz 16 · 04 (Primitif Model), Faz 16 · 13 (Paylaşımlı Bellek)
**Süre:** ~75 dakika

## Problem

Çoğu multi-agent sistemi sıkı-komut-dosyalı takımlardır: planlayıcı planlar, kodlayıcı kodlar, gözden geçiren gözden geçirir. Bu, iyi tanımlanmış görevler için çalışır. Ajanların belleği, öncelikleri ve açık bir dünyası olduğunda ortaya çıkan, komut-dosyasız davranışı yakalamaz. Araştırma, toplum simülasyonu ve giderek oyun AI'sı bu ikinci türü gerektirir.

Smallville mimarisi bunun için kıyaslama noktasıdır. Park 2023 öncesinde, en iyi ajan simülasyonları sığ komut-izleyicilerdi; sonrasında, örüntü açık dünyalardaki üretken ajanlar için varsayılan oldu. 2026'da bir ajan simülasyonu inşa ediyorsanız, ya Smallville'ın üç bileşenini kullanıyorsunuz ya da neden kullanmadığınızı açıkça gerekçelendiriyorsunuz.

## Kavram

### Üç bileşen

**Bellek akışı (memory stream).** Gözlemlerin, eylemlerin, yansımaların ve planların yalnızca-eklemeli (append-only) bir günlüğü. Her girdinin bir zaman damgası, bir türü, bir açıklaması (doğal dil) ve türetilmiş meta verileri vardır: **yenilik** (recency), **önem** (importance, ajan tarafından 1-10 kendi kendine puanlanır) ve **ilgililik** (relevance, mevcut sorguya kosinüs benzerliği).

```
[2026-02-14 09:12:03] gözlem: Isabella Rodriguez bana caz sevip sevmediğimi sordu
[2026-02-14 09:14:22] yansıma: Müzik hakkında uzun sohbetlerden keyif alıyorum
[2026-02-14 10:05:00] plan: Bu akşam Isabella'nın Sevgililer Günü partisine katıl
```

#### Açıklama
Bellek geri çağırma üç puanı birleştirir: `puan = w_yenilik * e^(-bozunma * yaş) + w_önem * önem + w_ilgililik * kosinüs_benzerliği`. İlk k girdileri mevcut isteme girer.

**Yansıma (reflection).** Periyodik olarak (her N bellekte veya önemli olaylarda), ajan son belleklerden üst-düzey sentezler üretir. Yansıma girdileri akışa geri döner ve herhangi bir bellek gibi geri çağrılabilir. Bu, ajanların "anlayışlar" oluşturma biçimidir — mimarinin uzun-vadeli inançlar eşdeğeri.

**Plan.** Yukarıdan aşağıya ayrıştırma. Önce, geniş çizgilerle gün-düzeyinde bir plan ("işe git, Klaus'la akşam yemeği ye"). Sonra saat-düzeyinde planlar. Sonra eylem-düzeyinde planlar. Planlar gözden geçirilebilir: bir gözlem bir planla çeliştiğinde, ajan etkilenen bölümü yeniden planlar.

### Neden üçü de önemli (ablasyon)

Park ve diğerleri gözlem, yansıma ve planın her birini düşüren ablasyonlar yürüttü. Her ablasyon inandırıcılığa zarar verir:

- **Gözlem** olmadan ajan bağlamı kaçırır ve eski inançlara göre hareket eder.
- **Yansıma** olmadan ajan üst-düzey inançlar oluşturamaz; etkileşimler sığ kalır.
- **Plan** olmadan davranış reaktif gürültüye dönüşür; hedefler dağılır.

İnsan değerlendiricilerden gelen inandırıcılık puanları üçü birden olduğunda en yüksektir; herhangi birini düşürmek ölçülebilir bir gerileme üretir.

### Sevgililer Günü ortaya çıkışı

Bir ajan olan Isabella Rodriguez, "14 Şubat saat 17:00'te Hobbs Cafe'de Sevgililer Günü partisi vermek istiyor" hedefiyle tohumlanır. Diğer 24 ajan böyle bir tohum almaz. Simüle edilen günler boyunca:

1. Isabella'nın planı insanları davet etmeyi içerir.
2. Her davet, bir komşunun bellek akışında bir gözlem haline gelir.
3. Komşunun yansıması inançlar üretir: "Isabella parti veriyor."
4. Komşunun planı "14 Şubat'ta partiye katıl"ı dahil eder.
5. Komşular diğer komşulara söyler. Davet merkezi koordinasyon olmadan yayılır.
6. 14 Şubat saat 17:00'de, birkaç ajan Hobbs Cafe'de buluşur.

Bu, teknik anlamda ortaya çıkıştır (emergence): sistem-düzeyinde davranış (bir parti) yerel etkileşimlerden (ikili davetler + bireysel planlama) merkezi bir orkestratör olmadan doğar.

### Belgelenen başarısızlık kipleri

Park ve diğerleri şunları açıkça belgeler:

- **Uzamsal norm hataları.** Ajanlar kapalı mağazalara yürür. Ajanlar aynı tek-kişilik banyoyu kullanmaya çalışır. Ajanlar yemek yemek için tasarlanmamış odalarda yer. Model, sosyal-fiziksel normları ortamdan tek başına çıkaramaz.
- **Bellek taşması.** Derin simülasyon çalıştırmaları bellek geri çağırma maliyetinin büyümesine neden olur. Pratik çare: periyodik bellek sıkıştırması (özetle-ve-buda) ve düşük-önem girdilerinde bozunma.
- **Yansıma halüsinasyonu.** Yansımalar bellek akışında var olmayan ilişkiler uydurabilir. Hafifletme: yansıma istemlerine kaynak bellek kimliklerini dahil edin ve geri çağırma zamanında doğrulayın.

Bunlar üretimle ilgili başarısızlık kipleridir: herhangi bir 2026 ajan simülasyonu bunları miras alır.

### Üç-bileşen uygulama kuralları

1. **Bellek yalnızca-eklemeli (append-only).** Bir bellek girdisini asla değiştirmeyin. Düzeltmeler yeni girdilerdir.
2. **Önem puanları ucuz.** Yazma zamanında LLM'yi önemi 1-10 puanlaması için çağırın. Puanı önbelleğe alın.
3. **Geri çağırma sıralanır, süzülmez.** Birleşik puana göre ilk k; sabit süzgeçler kullanmayın (bağlamı kaybeder).
4. **Yansıma periyodik çalışır.** İşlenmemiş belleklerin önem toplamı bir eşiği aştığında tetikleyin (örn. 150).
5. **Planlar gözden geçirilebilir.** Yeni bir gözlem bir planla çeliştiğinde, yalnızca etkilenen bölümü yeniden oluşturun, tüm planı değil.

### Smallville'ın ötesinde üretken ajanlar

2024-2026 takip literatürü mimariyi genişletir:

- **Politika / pazar araştırması için çok-ajanlı sosyal simülasyon.** Smallville benzeri popülasyonlar, özelliklere yanıt olarak kullanıcı davranışını simüle eder. A/B testlerinden daha hızlı; doğruluk tartışmalıdır.
- **Oyunlar için NPC AI'sı.** Smallville ajanlarına sahip RPG'ler, komut-dosyalı görevler yerine emergent hikaye örgüleri üretir.
- **Üretken-ajan değerlendirme kıyaslamaları.** Görev doğruluğu yerine, metrik uzun koşular üzerinde davranışın inandırıcılığı + tutarlılığı olur.

Mimari referanstır. Uzantılar bileşenleri değiştirir (bellek için vektör deposu, retrieval-augmented yansıma, neurosembolik plan) ama üç parçalı yapıyı korur.

### Bu neden multi-agent mühendisliği için önemlidir

Smallville, bileşenler doğru olduğunda çok-ajanlı ortaya çıkışın ucuz olduğunun kanıtıdır. Mimari artık açık kaynak modellerde kopyalanmıştır (daha küçük LLM'ler inandırıcılığı zarif biçimde, keskin biçimde değil kaybeder). **Emergent sosyal davranış** gerektiren herhangi bir üretim sistemi bu şekli kullanır. **Sıkı görev yürütme** gerektiren herhangi bir sistem bu fazın önceki bölümlerindeki supervisor / roller / primitives kalıplarını kullanır.

## İnşa Et

`code/main.py` üç bileşeni stdlib Python'da komut-dosyalı ajan politikalarıyla uygular (gerçek LLM yok). Demo, Sevgililer Günü partisinin ortaya çıkışını küçük ölçekte yeniden üretir:

- `MemoryStream` — yenilik/önem/ilgililik geri çağırmasıyla yalnızca-eklemeli günlük.
- `reflect(stream)` — son yüksek-önemli bellekler üzerine komut-dosyalı yansıma.
- `plan(agent_state)` — mevcut inançlara dayalı gün-düzeyinde ve saat-düzeyinde planlar.
- Senaryo: 5 ajan. Ajan 1 "5'te parti ver" ile başlar. Simüle edilen tikler boyunca davet yayılır ve ajanlar buluşur.

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı: tik-tik-tik iz. Son tike kadar, 5 ajandan en az 3'ü planında partiyi gösterir ve parti konumunda buluşurlar. Tek tohum, herhangi bir orkestratör olmadan koordineli varışı üretti.

## Kullan

`outputs/skill-simulation-designer.md` bir üretken-ajan simülasyonu tasarlar: ajan sayısı, bellek şeması, yansıma kadansı, plan ufkı ve değerlendirme metriği.

## Yayınla

Üretim simülasyonları için kurallar:

- **Bellek veritabanıdır.** Ölçekte gerçek bir depolama seçin (vektör DB, Postgres). Bellek içi stdlib prototipler içindir.
- **Geri çağırma izini kaydedin.** Her eylem için, onu yönlendiren ilk k belleği kaydedin. Bu, hata ayıklama yeteneğinizdir.
- **Ajan başına token bütçesi.** Her ajanın tik başına retrieve + reflect + plan'ı O(k) LLM çağrısıdır. N ajan × T tik × tik-başına-çağrı, bütçenizi gölgede bırakabilir.
- **Belleği periyodik olarak sıkıştırın.** Düşük-önem girdilerini özetle-ve-buda. Saklama politikası bir tasarım kararıdır, ayrıntı değil.
- **Uzamsal / sosyal norm ihlallerini açıkça tespit edin.** Mimari bunları öğrenmez.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. 3+ ajanın partide buluştuğunu doğrulayın. Ajanları 10'a çıkarın — ortaya çıkış hâlâ gerçekleşiyor mu?
2. Yansıma adımını kaldırın. Davranış nasıl görünür? Park 2023'teki ablasyon bulgusuyla eşleştirin.
3. Rekabet eden tohumlanmış bir hedef ekleyin ("Klaus saat 5'te araştırma sunumu vermek istiyor"). Ajanlar bölünüyor mu, yoksa bir hedef baskın mı? Bunu ne belirler?
4. Uzamsal kısıtlamalar ekleyin: Hobbs Cafe en fazla 4 ajan alır. Simülasyon taşmayı zarif biçimde ele alıyor mu, yoksa "tek-kişilik banyo" başarısızlık örüntüsüne mi takılıyor?
5. Park ve diğerleri (arXiv:2304.03442) Bölüm 6'yı (emergent davranış deneyleri) okuyun. Minyatürünüzde yeniden üretilemeyen bir davranış belirleyin. Mimarinin hangi bileşenini geliştirmeniz gerekirdi?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| Bellek akışı | "Ajanın günlüğü" | Gözlemlerin, eylemlerin, yansımaların, planların yalnızca-eklemeli günlüğü. |
| Yenilik | "Bellek ne kadar yeni" | Yaşa göre üstel bozunma puanı. |
| Önem | "Ajan ne kadar önemsiyor" | Yazma zamanında 1-10 kendi kendine puanlanır. Önbelleğe alınır. |
| İlgililik | "Mevcut sorguyla ne kadar ilgili" | Kosinüs benzerliği (gömme-tabanlı). |
| Yansıma | "Üst-düzey inanç" | Son belleklerden üretilen, yeni bir bellek olarak yeniden alınan sentez. |
| Plan | "Gün/saat/eylem ayrıştırması" | Yukarıdan aşağıya plan ağacı. Gözlemler çeliştiğinde gözden geçirilebilir. |
| Smallville | "Park 2023'ün sandbox'ı" | 25-ajanlı simülasyon; Sevgililer Günü ortaya çıkışını üretti. |
| İnandırıcılık | "Kalite metriği" | Davranışın olası bir ajan gibi görünüp görünmediğine dair insan-değerlendirici puanı. |

## İleri Okuma

- [Park et al. — Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) — referans mimari
- [UIST '23 paper page](https://dl.acm.org/doi/10.1145/3586183.3606763) — yayın yeri
- [Smallville kod sürümü](https://github.com/joonspk-research/generative_agents) — referans Python uygulaması
- [Hayes-Roth 1985 — A Blackboard Architecture for Control](https://www.sciencedirect.com/science/article/abs/pii/0004370285900639) — yapılandırılmış-bellekli ajanlar için önceki sanat
