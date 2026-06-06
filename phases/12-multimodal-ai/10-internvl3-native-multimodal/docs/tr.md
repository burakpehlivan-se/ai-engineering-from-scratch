# InternVL3: Yerel Multimodal Ön-Eğitim

> InternVL3 öncesindeki her açık VLM aynı üç adımlı tarifi izliyordu: trilyonlarca metin token'ı üzerinde eğitilmiş bir metin LLM'i alın, üzerine bir görüntü kodlayıcısı takın, sonra dikişleri ince ayarlayın. Bu çalışır ama hizalama borcu (alignment debt) biriktirir — metin LLM'i tüm ön-eğitim bütçesini saf metin üzerinde harcamıştır ve görsel token'ları doğal olarak anlamaz. Görüntüyü sonradan eklediğinizde LLM, görsel girdiyi kendi metin akıl yürütmesiyle nasıl ilişkilendireceğini unutmadan öğrenmek zorunda kalır. InternVL3 (Zhu ve diğerleri, Nisan 2025) sonradan ekleme yaklaşımını reddeder: bir ön-eğitim çalışması, baştan itibaren metin ve multimodal aralıklı. Sonuç, 78B açık parametreyle MMMU-Pro'da Gemini 2.5 Pro ile eşleşir. Bu ders yerel ön-eğitim davasını ve bunu yaptığınızda neler değiştiğini inceler.

**Tür:** Öğren
**Diller:** Python (stdlib, eğitim korpusu karıştırıcı)
**Önkoşullar:** Faz 12 · 05, Faz 12 · 07 (tarifler)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Sonradan VLM eğitiminin neden hizalama borcu biriktirdiğini, üç ölçülebilir belirtiyi (felaket unutma, cevap kayması, görsel-metin tutarsızlığı) atıfta bulunarak açıklama.
- InternVL3'ün yerel ön-eğitim korpusu karışımını ve metin : aralıklı : açıklama oranının neden önemli olduğunu tasvir etme.
- V2PE'yi (değişken görsel konum kodlaması) Qwen2-VL'nin M-RoPE'siyle karşılaştırma.
- Görsel Çözünürlük Yönlendiricisini (ViR) ve Ayrılmış Görüntü-Dil (DvD) dağıtım optimizasyonlarını adlandırma.

## Sorun

Sonradan VLM eğitimi varsayılandır. LLaVA, BLIP-2, Qwen-VL, Idefics — hepsi önceden eğitilmiş bir LLM (Llama, Vicuna, Qwen, Mistral) alır ve üzerine görüntü ekler. Eğitim aşamaları genellikle şöyle görünür:

1. Donmuş LLM + donmuş görüntü kodlayıcısı + eğitilebilir projeksiyoncu, gömmeleri hizalamak için açıklama çiftleri üzerinde eğitilir.
2. LLM serbest bırakılır, talimat verileri (LLaVA-Instruct, ShareGPT4V) üzerinde eğitilir.
3. İsteğe bağlı görev özel ince ayar.

Hizalama borcunun üç belirtisi ortaya çıkar:

- Felaket unutma. Sonradan VLM saf metin becerilerini unutur. GSM8K puanları 5-10 puan düşer. Hellaswag puanları düşer. Saf metin ajanları geriler.
- Cevap kayması. Aynı görsel sorunun küçük farklı ifadeleri farklı cevaplar alır. Görüntü kodlayıcısı LLM'e kendi token'larından daha zayıf bağlarla bağlanır.
- Görsel-metin tutarsızlığı. VLM bir görüntüyü doğru tarif edebilir ama kendi açıklamasıyla çelişen bir soruyu cevaplayabilir. Görsel token'lar LLM'in kendi iç tutarlılık kontrollerine metin gibi katılmaz.

Bu belirtiler iyi belgelenmiştir. MM1.5 Bölüm 4 bunları nicelleştirir. LLaVA-OneVision'ın kıyaslama deneyleri bunlara ipucu verir. Yerel ön-eğitim cevabıdır.

## Kavram

### Yerel multimodal ön-eğitim

InternVL3, baştan itibaren yerel multimodal olan bir korpus üzerinde sıfırdan eğitilir. Karışım:

- %40 yalnızca metin verisi (FineWeb, Proof-Pile-2 vb.)
- %35 aralıklı görüntü-metin verisi (OBELICS, MMC4 tarzı)
- %20 eşlenmiş görüntü-açıklama verisi
- %5 video-metin verisi

Görüntü token'ları, metin token'ları ve çapraz-modal etkileşimlerin hepsi ilk gradyan adımından aynı kayba katılır. Hizalama ön-eğitimi, projeksiyoncu dondurma aşaması, kurtululacak felaket unutma yok.

Eğitim temel model için tek bir aşamadır. Talimat ince ayarı takip eder ama temel model zaten görsel token'ları birinci sınıf vatandaş olarak anlar.

### V2PE (değişken görsel konum kodlaması)

Qwen2-VL sabit eksen dağılımıyla M-RoPE kullanır. InternVL3 V2PE'yi tanıtır: konum kodlaması, öğrenilebilir ölçeklemeyle (learnable scaling) modalite türüne (metin, görüntü, video) göre değişir. pratikte:

- Metin token'ları 1B konum alır (metin indeksi).
- Görüntü yamaları 2B konum alır (satır, sütun).
- Video kareleri 3B konum alır (zaman, satır, sütun).

Üçü aynı RoPE frekans tabanını paylaşır ama şerit başına gizli boyut dağılımı sabit bir bölmek yerine öğrenilen bir parametremdir. Ön-eğitim sırasında zamansal ile uzamsal frekans çözünürlüğü arasında takas yapma özgürlüğü.

V2PE'nin kıyaslama iddiası: aynı hesaplama gücünde video kıyaslama testlerinde M-RoPE'ye göre 1-2 puan. Devrim değil ama daha temiz.

### Görsel Çözünürlük Yönlendiricisi (ViR)

Dağıtım optimizasyonu. Tüm görüntülerin tam çözünürlüklü kodlanmasına gerek yoktur. Düşük ayrıntıda tek nesne içeren bir fotoğraf 1280px yerel çözünürlükte kodlandığında token'ları boşa harcar. ViR, kodlamadan önce soruyu yanıtlamak için gereken minimum çözünürlüğü tahmin eden küçük bir sınıflandırıcıdır.

Yönlendirme üç katmanlıdır: düşük çözünürlük (256 token), orta (576), yüksek (2048+). Üretim trafiğindeki sorguların %60'ı için düşük veya orta yeterlidir. Net etki: aynı kalitede 2-3x verimlilik.

### Ayrılmış Görüntü-Dil Dağıtımı (DvD)

Bir büyük VLM sunduğunuzda görüntü kodlayıcısı görüntü başına bir kez çalışır ama LLM her çıktı token'ı için otoregresif çalışır. İki bileşenin farklı darboğazları vardır (görüntü = konvolüsyon + dikkat için GPU bellek bant genişliği; LLM = KV önbellek). DvD bunları akış (streaming) ile ayrı GPU'lara böler.

8B + 400M kodlayıcı modeli için DvD, yerleşik modele göre düğüm başına verimliliği yaklaşık ikiye katlar.

### Tek aşamalı vs çok aşamalı kalite

InternVL3'ün birincil kıyaslama iddiası: 78B parametrede Gemini 2.5 Pro'nun MMMU-Pro'suyla eşleşme. 38B'de GPT-4o ile eşleşme. 8B'de açık-8B liderlik tablosunda öncülük. Hepsi tek aşamalı ön-eğitim + talimat ince ayarı tarifiyle.

Hizalama borcu hipotezi ölçülebilirdir: InternVL3-8B, görsel kıyaslama kazancı başına Qwen2.5-VL-7B'den daha az metin kıyaslama puanı (MMLU, GSM8K) kaybeder. Model daha fazla bir genelcidir çünkü eğitim bir parça değil, tek bir parçaydı.

### InternVL3.5 ve InternVL-U

InternVL3.5 (Ağustos 2025) tarifi ölçeklendirir. Aynı yerel ön-eğitim yaklaşımı, daha fazla veri, daha fazla parametre. MMMU geliştirmeleri kademelidir.

InternVL-U (2026) birleşik üretim ekler — aynı omurga üzerine MMDiT kafalarıyla görüntü çıkışı. "U" "Anlama + Üretim" demektir, Transfusion tarzı birleşik modellere (Ders 12.13) yöneldi. Aynı yerel ön-eğitim omurgası hem anlama hem de üretim kafalarını destekler.

### Yerel ön-eğitim uzlaşmaları

Yerel ön-eğitim ücretsiz değildir:

- Hesaplama. Yeni bir VLM'i sıfırdan eğitmek, bir metin LLM'i eğitmek kadar tutar — milyonlarca GPU-saat. Sonradan uyarlama mevcut LLM ağırlıklarını yeniden kullanır, maliyetin çoğunu tasarruf eder.
- Veri. Ölçekte aralıklı görüntü-metin korpusları nadirdir. OBELICS 141M belgedir; MMC4 571M'dir. Yalnızca metin 15T token gelir. Multimodal ön-eğitim verisi kıtlığı sıkı bir kısıttır.
- Temel-LLM yeniden kullanımı. Yerel ön-eğitim, ileride yeni bir LLM ekleme seçeneğini bırakır. Sonradan ekleme, yalnızca adaptörü yeniden eğiterek Llama-3.1'i Llama-4 ile değiştirmenize izin verir.

InternVL3'ün yaptığı bahis: hizalama borcu yeniden kullanım kaybından daha kötüdür. Kıyaslama testleri iddiayı destekler. Üretim maliyeti gelecek laboratuvarların ucuza kopyalamasını engeller. Sonradan VLM'ler çoğu proje için hâlâ daha ucuz oldukları için var olmaya devam edecek.

## Kullan

`code/main.py` bir eğitim korpusu karıştırıcısı ve ViR yönlendirici simülatörüdür:

- Hedef korpus karışımını (%metin, %aralıklı, %açıklama, %video) alır ve modalite başına beklenen adımları hesaplar.
- Bir sorgu toplu işi üzerinde ViR yönlendirmesini simüle eder (dağılım: %50 düşük ayrıntı, %30 orta, %20 yüksek ayrıntı) ve ortalama token sayısını raporlar.
- Kodlayıcı vs LLM FLOPs'ları verildiğinde DvD verimlilik tahminleri raporlar.
- Sonradan vs yerel ön-eğitimi parametre, hesaplama, veri ve beklenen hizalama borcu belirtileri açısından yan yana yazdırır.

## Teslimat

Bu ders `outputs/skill-native-vs-posthoc-auditor.md` dosyasını üretir. Önerilen bir VLM eğitim planı verildiğinde, yerel mi sonradan mı gidileceğini denetler, hizalama borcu riskini işaretler ve bir korpus karışımı önerir. Yeni bir açık-VLM projesini boyutlandırırken ve eğitim stratejisini seçerken kullanın.

## Alıştırmalar

1. InternVL3-8B (yerel ön-eğitim) ile LLaVA-OneVision-7B (sonradan) arasındaki hesaplama farkını tahmin edin. GPU-saat oranı yaklaşık olarak nedir? Farkı ne açıklar?

2. InternVL3 %40 metin / %35 aralıklı / %20 açıklama / %5 video rapor ediyor. Hedef göreviniz ağırlıklı olarak videoysa yeni bir oran önerin ve temel modelin neden hâlâ önemli miktarda metin ve açıklama verisine ihtiyacı olduğunu savunun.

3. MM1.5 Bölüm 4'ü unutma hakkında okuyun. Sonradan eğitimin en büyük gerilemeyi gösterdiği tam kıyaslama testini adın. Gerileme ne kadara mal oldu?

4. ViR trafiğin %60'ını düşük çözünürlüklü kodlamaya yönlendiriyor. Hangi tür sorguları yanlış yönlendirir (yüksek çözünürlük gerekirken düşük çözünürlüğe gönderir)? Üç yönlendirici hata modu önerin.

5. DvD görüntü ve LLM'i ayrı GPU'lara böler. Hangi trafik kalıbında DvD yardımcı olmak yerine verimliliği düşürür?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Yerel multimodal ön-eğitim | "Sıfırdan birlikte" | Metin + görüntü + video token'ları 1. adımdan kayba katılır, sonradan eklenmez |
| Hizalama borcu | "Sonradan cezası" | Donmuş bir LLM üzerine görüntü takmanın yarattığı ölçülebilir metin becerisi ve cevap tutarsızlığı gerilemesi |
| V2PE | "Değişken görsel konum kodlaması" | Modalite başına öğrenilebilir konum kodlaması dağıtımı; InternVL3'ün M-RoPE halefi |
| ViR | "Çözünürlük yönlendiricisi" | Kodlamadan önce sorgu başına gereken minimum çözünürlüğü seçen küçük sınıflandırıcı, çıkarım token'larını tasarruf eder |
| DvD | "Ayrılmış dağıtım" | Görüntü kodlayıcısı bir GPU'da, LLM diğerinde, akış el değiştirme; büyük VLM'lerde verimliliği ikiye katlar |
| InternVL-U | "Birleşik anlama + üretim" | 2026 devamı, yerel ön-eğitim omurgasına görüntü üretim kafaları ekler |
| Aralıklı korpus | "OBELICS / MMC4" | Doğal okuma sırasında metin ve görüntü içeren belgeler; yerel ön-eğitim için ham madde |

## İleri Okuma

- [Chen ve diğerleri — InternVL 1 (arXiv:2312.14238)](https://arxiv.org/abs/2312.14238)
- [Zhu ve diğerleri — InternVL3 (arXiv:2504.10479)](https://arxiv.org/abs/2504.10479)
- [InternVL3.5 (arXiv:2508.18265)](https://arxiv.org/abs/2508.18265)
- [InternVL-U (arXiv:2603.09877)](https://arxiv.org/abs/2603.09877)
- [Zhang ve diğerleri — MM1.5 (arXiv:2409.20566)](https://arxiv.org/abs/2409.20566)
