# CLIP'ten BLIP-2'ye — Q-Former Modalite Köprüsü

> CLIP görüntü ve metni hizalar ama açıklama üretemez, sorulara cevap veremez veya sohbet edemez. BLIP-2 (Salesforce, 2023) bunu küçük bir eğitilebilir köprüyle çözdü: 32 öğrenilebilir sorgu vektörü (learnable query) donmuş bir ViT'nin özelliklerine çapraz-dikkat (cross-attention) ile bakar, ardından doğrudan donmuş bir LLM'in girdi akışına girer. 188M parametrelik köprü, 11B'lik bir LLM'i ViT-g/14'e bağladı. 2026'ya kadar tüm adaptörlü VLM — MiniGPT-4, InstructBLIP, LLaVA'nın kuzenleri — bir soyundandır. Bu ders Q-Former'ın mimarisini inceler, iki aşamalı eğitimini açıklar ve görsel token'ları donmuş bir metin çözümleyiciye (decoder) besleyen oyuncu bir versiyonu uygular.

**Tür:** İnşa Et
**Diller:** Python (stdlib, çapraz-dikkat + öğrenilebilir sorgu demosu)
**Önkoşullar:** Faz 12 · 02 (CLIP), Faz 7 (Transformer'lar)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Neden donmuş bir görüntü kodlayıcısı ve donmuş LLM arasındaki eğitilebilir bir darboğazın (bottleneck), uçtan uca ince ayara kıyasla maliyet ve kararlılık açısından daha iyi olduğunu açıklama.
- Sabit bir öğrenilebilir sorgu kümesinin harici görüntü özelliklerine çapraz-dikkat uyguladığı bir çapraz-dikkat bloğunu uygulama.
- BLIP-2'nin iki aşamalı ön-eğitimini inceleme: temsil (ITC + ITM + ITG) ardından üreteçsel (donmuş çözümleyici ile dil modeli kaybı).
- Q-Former'ı LLaVA'da kullanılan daha basit MLP projeksiyoncusuyla karşılaştırma ve her seçeneğin ne zaman kazandığını savunma.

## Sorun

Her görüntü için 1408 boyutunda 256 yama token'ı üreten donmuş bir ViT'niz var. 4096 boyutunda token gömmesi bekleyen donmuş 7B'lik bir LLM'niz var. Açık köprü — 1408'den 4096'ya doğrusal katman — işe yarar ama 256 yama token'ının tamamını LLM'in bağlamına beslemek görüntü başına 256 ekstra token'a mal olur. 32 görüntüden oluşan bir toplu işte görsel modalite tek başına 8192 token tüketir.

BLIP-2 sorusu: 256 tokenlık görüntü temsilini çok daha az token'a (ör. 32) sıkıştırabilir misiniz, hem de LLM'in açıklama yapması, sorulara cevap vermesi ve görüntü hakkında akıl yürütebilmesi için yeterli bilgiyi koruyarak? Ve bu köprüyü donmuş omurgalara dokunmadan, eğitim maliyetini yalnızca köprü parametreleriyle sınırlı tutarak eğitebilir misiniz?

Cevap: Q-Former. ViT'nin yama token'larına çapraz-dikkat uygulayan 32 öğrenilebilir "sorgu" vektörü, LLM'in tükettiği 32 tokenlık bir görsel özet üretir. Toplam 188M parametre. LLM'e dokunmadan önce karşıtlıklı, eşleştirmeli ve üreteçsel hedeflerle eğitilir.

## Kavram

### Öğrenilebilir sorgular

Q-Former'ın temel hilesi: LLM'in metin token'larının görüntü yamalarına dikkat etmesine izin vermek yerine, 32 yeni öğrenilebilir sorgu vektörü `Q` tanıtıp *onların* görüntü yamalarına dikkat etmesini sağlamak. Sorgular modelin parametreleridir — eğitim sırasında öğrenilir ve aynı 32 sorgu her görüntü için kullanılır.

Çapraz-dikkatten sonra her sorgu görüntünün sıkıştırılmış bir özetini taşır — "ana nesneyi tanımla", "arka planı tanımla", "nesneleri say" vb. Sorgular kelimenin tam anlamıyla anlamsal etiketlerde uzmanlaşmaz; alt görev kayıplarını düşüren herhangi bir kodlamayı öğrenirler.

### Mimari

Q-Former, iki yola sahip küçük bir transformerdır (12 katman, ~100M parametre):

1. Sorgu yolu: 32 sorgu vektörü kendi aralarında öz-dikkatten (self-attention) geçer, ardından donmuş ViT'nin yama token'ları üzerinde çapraz-dikkat, ardından FFN.
2. Metin yolu: BERT benzeri bir metin kodlayıcısı sorgu yoluyla öz-dikkat ve FFN ağırlıklarını paylaşır. Çapraz-dikkat metin yolu için devre dışıdır.

Eğitim sırasında her iki yol da çalışır. Sorgular ve metin paylaşımlı öz-dikkat aracılığıyla etkileşime girer; bu da sorguların gerektiği görevlerde (ITM, ITG) metne koşullandırılmasını sağlar. VLM devretme için çıkarım sırasında yalnızca sorgular geçer ve 32 görsel token üretir.

### İki aşamalı eğitim

BLIP-2 iki aşamada ön-eğitir:

1. Aşama: temsel öğrenme (LLM yok). Üç kayıp:
 - ITC (görüntü-metin karşıtlıklı): havuzlanmış sorgu token'ları ile metin CLS token'ı arasında CLIP tarzı karşıtlık.
 - ITM (görüntü-metin eşleme): ikili sınıflandırıcı — bu görüntü-metin çifti eşleşme mi? Sert negatif çıkarmalı.
 - ITG (görüntüye dayalı metin üretimi): sorgular koşullu olarak metin üzerinde nedensel (causal) dil modeli kafası. Sorguların metin üretilebilir içerik kodlamasını zorlar.

Yalnızca Q-Former eğitilir. ViT donmuştur. LLM yoktur.

2. Aşama: üreteçsel öğrenme. Donmuş bir LLM (OPT-2.7B veya Flan-T5-XL vb.) eklenir. 32 sorgu çıktısı küçük bir doğrusal katmanla LLM'in gömme boyutuna projekte edilir. Metin isteminin başına eklenir. Yalnızca doğrusal projeksiyon ve Q-Former, birleştirilmiş istem + görüntü + açıklama dizisi üzerinde dil modeli kaybıyla eğitilir.

2. aşamadan sonra Q-Former + projeksiyon tam görsel adaptördür. Çıkarım sırasında: görüntü → ViT → Q-Former → doğrusal projeksiyon → metnin başına eklendi → donmuş LLM çıktıyı üretir.

### Parametre ekonomisi

ViT-g/14 (1.1B, donmuş) + OPT-6.7B (6.7B, donmuş) + Q-Former (188M, eğitilmiş) = toplam 8B, 188M eğitilmiş. Q-Former tek başına toplam yığının parametrelerinin ~%2.4'üdür. Eğitim maliyeti bunu yansıtır: birkaç A100 üzerinde birkaç gün vs uçtan uca haftalarca.

Kalite: BLIP-2, Flamingo-80B ile zero-shot VQA'da eşleşir veya yener, 50x daha küçükken. Köprü işe yarıyor.

### InstructBLIP ve talimat-farkında Q-Former

InstructBLIP (2023), Q-Former'ı ek bir girişle genişletir: talimat metninin kendisi. Çapraz-dikkat sırasında sorgular artık hem görüntü yamalarına hem de talimata erişebilir. Sorgular sabit bir özet yerine talimat başına uzmanlaşabilir ("arabaları say", "ruh halini tanımla"). Çıkarılmış görevlerde kıyaslama kazanımları.

### MiniGPT-4 ve yalnızca projeksiyoncu yaklaşımı

MiniGPT-4 Q-Former'ı korudu ama yalnızca çıktı doğrusal projeksiyonunu eğitirken diğer her şeyi dondurdu. Ucuz ama kalite maliyetli — sorgular BLIP-2'nin sizin değildi. Hızlı iterasyon için iyi, en iyi mimari değil.

### Neden LLaVA daha basite gitti

LLaVA (2023, Ders 12.05) Q-Former'ı her ViT yama token'ını LLM uzayına projekte eden düz 2 katmanlı MLP ile değiştirdi — 24x24 ızgara için görüntü başına 576 token, hepsi LLM'e beslendi. Daha kötü sıkıştırma ama LLM'in ham yamalar üzerinde dikkat etmesine izin verdi. O zamanlar tartışmalıydı; 2023 sonuna kadar baskın hale geldi çünkü görsel talimat verileri (LLaVA-Instruct-150k) MLP'nin yeterli sinyali koruyacak şekilde eğitilebileceğini kanıtladı. Uzlaşma: LLaVA'nın bağlamı daha hızlı dolar, ama doğal olarak çoklu görüntü ve videoya ölçeklenir.

2026'ya kadar alan ikiye bölündü: Q-Former token bütçesinin önemli olduğu yerlerde (uzun video, çok görüntü); MLP projeksiyoncusu token başına ham kalitenin öncelik olduğu yerlerde baskındır.

### Kapılı çapraz-dikkat: Flamingo, ataları

Flamingo (Ders 12.04) BLIP-2'den önce geldi ve aynı çapraz-dikkat fikrini ama tek bir köprü yerine her donmuş LLM katmanında kullandı. BLIP-2, yalnızca girdi katmanına sıkıştırmanın hâlâ çalıştığını gösterdi. Gemini ve Idefics her ikisini birleştirir: aralıklı girdi token'ları artı bağlam-içi few-shot için isteğe bağlı kapılı çapraz-dikkat.

### 2026 soyundanları

- Q-Former: BLIP-2, InstructBLIP, MiniGPT-4 ve token bütçesi nedeniyle çoğu video-dil modeli.
- Perceiver yeniden örnekleme (resampler): Flamingo'nun çeşidi (Ders 12.04); Idefics ailesi, Eagle, OmniMAE.
- MLP projeksiyoncusu: LLaVA, LLaVA-NeXT, LLaVA-OneVision, Cambrian-1.
- Dikkat havuzlaması (attention pool): VILA, PaliGemma.

Dördü de geçerlidir. Belirleyici soru, token bütçesinde mi yoksa token başına kalitede mi kısıtlı olduğunuzdur.

## Kullan

`code/main.py` stdlib Q-Former tarzı çapraz-dikkat inşa eder:

1. 256 görüntü yama token'ını simüle eder (boyut 128).
2. 32 öğrenilebilir sorgu başlatır (boyut 128).
3. Ölçeklendirilmiş nokta çarpımı çapraz-dikkati çalıştırır (Q sorgulardan, K/V yamalardan).
4. Doğrusal katmanla LLM boyutuna (512) projekte eder.
5. 32 LLM-hazır görsel token'ı çıktı verir.

Tüm matematik saf Python'da (vektörler üzerinde iç içe döngüler). Oyuncu ama doğru şekildedir. Dikkat ağırlık matrisi yazdırılır, böylece her sorgunun hangi yamalardan çektiğini görebilirsiniz.

## Teslimat

Bu ders `outputs/skill-modality-bridge-picker.md` dosyasını üretir. Hedef bir VLM yapılandırması (görüntü kodlayıcısı token sayısı, LLM bağlam bütçesi, dağıtım kısıtlamaları, kalite hedefi) verildiğinde, kısa bir gerekçeyle Q-Former vs MLP vs Perceiver yeniden örnekleme önerir ve her köprü için parametre sayısı tahmini verir.

## Alıştırmalar

1. Çapraz-dikkat bloğunu PyTorch'ta uygulayın. 32 sorgu ve 256 anahtar/değer ile dikkat ağırlık matrisinin 32 x 256 olduğunu ve softmax'tan sonra her satırın 1'e toplandığını doğrulayın.

2. BLIP-2 1. aşamada Q-Former üç kaybı aynı anda çalıştırır: ITC, ITM, ITG. Her biri için pseudo-kodda ileri geçiş (forward) imzası yazın. Hangisi metin kodlayıcı yolunun aktif olmasını gerektirir?

3. Parametre sayılarını karşılaştırın: Q-Former (12 katman, 768 gizli) vs 2 katmanlı MLP projeksiyoncusu (1408 → 4096, iki katman). Hangi LLM ölçeğinde 188M Q-Former maliyeti eğitim verimliliğiyle kendini amorti eder?

4. BLIP-2 makalesinin Bölüm 3.2'sini okuyun (arXiv:2301.12597) — Q-Former nasıl başlatılır. Neden BERT-tabanından (rastgele değil) başlatma yakınsamayı hızlandırır?

5. 1 FPS ile örnekleme yapılan 10 dakikalık video için kare başına token maliyetini hesaplayın: (Q-Former → 32 token/kare) vs (MLP projeksiyoncusu → 576 token/kare). Hangisi 128k tokenlık LLM bağlam penceresine sığar?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Q-Former | "Sorgulayan transformer" | 32 öğrenilebilir sorgu vektörüyle donmuş ViT özelliklerine çapraz-dikkat uygulayan küçük transformer |
| Öğrenilebilir sorgular | "Görüntü için yumuşak istem" | Çapraz-dikkatin sorgu tarafını oluşturan sabit parametre kümesi; model başına öğrenilir, tüm girdiler paylaşılır |
| Çapraz-dikkat (Cross-attention) | "Buradan Q, ordan K/V" | Sorgu, anahtar ve değerin farklı kaynaklardan geldiği dikkat mekanizması; sorguların ViT yamalarından nasıl çektiğidir |
| ITC | "Görüntü-metin karşıtlıklı" | Q-Former havuzlanmış sorguları vs metin CLS'i üzerine uygulanan CLIP tarzı kayıp |
| ITM | "Görüntü-metin eşleme" | Sert negatif çıkarmalı çiftler üzerinde ikili sınıflandırıcı; sorguların ince ayrım yapmasını zorlar |
| ITG | "Görüntüye dayalı metin üretimi" | Sorgular koşullu olarak metin üretildiğinde nedensel dil modeli kaybı; sorguların metin-cozunur içerik kodlamasını zorlar |
| İki aşamalı ön-eğitim | "Önce temsil, sonra üreteçsel" | 1. aşama yalnızca Q-Former'ı eğitir (ITC/ITM/ITG); 2. aşama donmuş LLM ekler ve yalnızca projeksiyon + Q-Former'ı eğitir |
| Donmuş omurga | "İnce ayar yapma" | Görüntü kodlayıcısı ve LLM ağırlıkları sabittir; yalnızca köprü eğitilir |
| Projeksiyon kafası | "LLM boyutuna doğrusal" | Q-Former çıktısını LLM'in gömme boyutuna haritalayan son doğrusal katman |
| Perceiver yeniden örnekleme | "Flamingo'nun sürümü" | Benzer öğrenilebilir sorgu çapraz-dikkati; Flamingo bunu tek köprü yerine her katmanda kullanır |

## İleri Okuma

- [Li ve diğerleri — BLIP-2 (arXiv:2301.12597)](https://arxiv.org/abs/2301.12597) — temel makale.
- [Li ve diğerleri — BLIP (arXiv:2201.12086)](https://arxiv.org/abs/2201.12086) — ITC/ITM/ITG üçlüsüyle selefi.
- [Li ve diğerleri — ALBEF (arXiv:2107.07651)](https://arxiv.org/abs/2107.07651) — "birleştirmeden önce hizala" — 1. aşama eğitiminin kavramsal atası.
- [Dai ve diğerleri — InstructBLIP (arXiv:2305.06500)](https://arxiv.org/abs/2305.06500) — talimat-farkında Q-Former.
- [Zhu ve diğerleri — MiniGPT-4 (arXiv:2304.10592)](https://arxiv.org/abs/2304.10592) — yalnızca projeksiyoncu yaklaşımı.
- [Jaegle ve diğerleri — Perceiver IO (arXiv:2107.14795)](https://arxiv.org/abs/2107.14795) — öğrenilebilir sorgu çapraz-dikkati için genel mimari.
