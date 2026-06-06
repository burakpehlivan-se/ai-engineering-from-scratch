# Bedensel VLA'lar: RT-2, OpenVLA, π0, GR00T

> Bir modelin bir web sitesinden bir tarif okuyup bir mutfak robotunda çalıştırdığı ilk sefer RT-2'ydi (Google DeepMind, Temmuz 2023). RT-2 eylemleri metin token'ları olarak ayrıştırdı, bir VLM'i web verisi artı robot eylem verisi üzerinde birlikte ince ayarladı (co-fine-tuned) ve web ölçeğindeki görüntü-dil bilgisinin robotik kontrole aktarıldığını kanıtladı. OpenVLA (Haziran 2024) açık 7B referansını piyasaya sürdü. Physical Intelligence'ın π0 serisi (2024-2025) flow-matching eylem uzmanlarını ekledi. NVIDIA'nın GR00T N1'i (Mart 2025) insansı robotlar için çift sistem (System 1 / System 2) kontrolünü ölçekli olarak sundu. VLA ilkesi — görüntü-dil-eylem (vision-language-action), gören, okuyan ve hareket eden tek model — bu fazın anlama modelleri ile Faz 15'teki otonom sistemler arasındaki köprüdür.

**Tür:** Öğren
**Diller:** Python (stdlib, eylem tokenizer'ı + VLA çıkarım iskeleti)
**Ön koşullar:** Faz 12 · 05 (LLaVA), Faz 15 (Otonom Sistemler, referans)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Eylem tokenize etmeyi (action tokenization) tanımlayın: ayrık kutu kodlaması (RT-2), FAST verimli eylem token'ları, sürekli flow-matching eylemleri (π0).
- Web + robot verisi üzerinde birlikte ince ayarın neden yeni görevlere genel bilgi aktarımını koruduğunu açıklayın.
- Aynı robot görevi üzerinde OpenVLA (açık 7B Llama+VLM), π0 (flow-matching) ve GR00T N1'i (çift sistem) karşılaştırın.
- Open X-Embodiment veri setini ve RT-X eğitim derlemi (corpus) olarak rolünü adlandırın.

## Problem

Doğal dil talimatlarından ev işleri yapan bir robot, 1970'lerden beri bir araştırma hedefi olmuştur. 2020'lerin cevabı: bir görüntü-dil-eylem (VLA) modeli. VQA için kullanılan aynı VLM mimarisi, ancak çıktı metin yerine ekleme torkları (joint torques), uç etkinlik pozları (end-effector poses) veya ayrık komutlardan oluşan eylemlerdir.

VLA'lara özgü zorluklar:

1. Eylem uzayları sürekli (ekleme açıları, kuvvetler) ve yüksek boyutludur (7-DOF kol + 3-DOF kavrama = 30 Hz'de 10 boyut).
2. Robot-spesifik eğitim verisi nadirdir. Open X-Embodiment ~1M yörüngeye sahiptir; web metin-görüntüsü 5B+'dır.
3. Kontrol frekansı önemlidir. 30 Hz kontrol döngüsü, eylem başına 33ms bütçe demektir.
4. Güvenlik. Yanlış bir eylem donanımı, insanları veya mülkü Hasara uğratır.

## Kavram

### Eylem tokenize etme (RT-2)

RT-2'nin hilesi: her ekleme hedefini quantize edilmiş bir metin token'ı olarak temsil etmek. Normalleştirilmiş [-1, 1] aralığını 256 kutuya ayrıştırın (discretize), her kutuyu bir sözcük dağarcığı (vocabulary) ID'sine eşleyin. 10 boyutlu bir eylem, her kontrol adımında 10 token olur.

Bir PaLM-X VLM'i şu karışım üzerinde birlikte ince ayarlayın:

- Web görüntü-metin çiftleri (captioning, VQA).
- Robot demonstrasyonları, eylem token olarak.

Model "kırmızı küpü al" (dil) → görüntü (görüntü) → 10 token'lık eylem dizisi (ayrıştırılmış ekleme hedefleri)看到r. Web ön eğitimi genel bilgi aktarımını korur: RT-2 "hızlı hareket eden nesneye doğru hareket et" talimatını izleyebilir, "hızlı hareket eden" eğitim verisinde olmasa bile.

RT-2 makalesinde VLM otoregressive çözümlemesiyle sınırlı olarak 3-5 Hz'de çıkarım.

### OpenVLA — açık 7B referansı

OpenVLA (Kim ve ark., Haziran 2024) açık ağırlıklı RT-2 eşdeğeridir. 7B Llama omurgası, DINOv2 + SigLIP çift görüntü encoder'ı, 256 kutu üzerinde eylem tokenize etme.

Open X-Embodiment (22 robot genelinde 970k yörünge) üzerinde eğitilmiştir. Yeni robotlara uyum sağlamak için LoRA ince ayar desteğiyle birlikte gelir.

Çıkarım: kuantizasyonla A100'de 4-5 Hz. Yavaş manipülasyon için yeterince hızlı, yüksek frekanslı kontrol için değil.

### FAST tokenizer — daha hızlı eylem çözümlemesi

Pertsch ve ark. (2024), ayrık-kutu tokenize etmenin verimsiz olduğunu gösterdi — çoğu eylem kutu-uzayının küçük bir bölgesinde kümelidir. FAST (Frequency-domain Action Sequence Tokenizer), eylem dizilerini DCT aracılığıyla sıkıştırır ve katsayıları quantize eder.

30 adımlık bir eylem yörüngesi, 300 ayrık-kutu token'ı yerine ~10 FAST token'ına dönüşür. Kalite kaybı olmadan çıkarım hızı 3-5x artar.

### π0 ve flow-matching eylemleri

Physical Intelligence'ın π0'ı (Black ve ark., Ekim 2024) ayrık eylem token'larını bir flow-matching eylem uzmanıyla değiştirir:

- Küçük bir eylem transformer'ı VLM'in gizli durumlarını (hidden states) okur ve rectified flow aracılığıyla sürekli 50 adımlık eylem dizisi üretir.
- Eylem başlığı (head) flow-matching kaybıyla eğitilir; VLM ön eğitimi değişmez.
- Çıkarım: tam eylem dizisi ~5 deneme (denoising) adımında üretilir, etkin olarak 50 Hz kontrol.

π0'nun iddiası: geniş bir manipülasyon görevleri setinde OpenVVA ve Octo'yu yener. Sürekli-eylem formülizasyonu, ayrıştırmanın yok ettiği pürüzsüzlüğü korur.

π0.5 ve π0-FAST kademeli güncellemelerdir. π0-FAST FAST tokenize etmeyi flow matching ile birleştirir.

### GR00T N1 — insansılar için çift sistem

NVIDIA'nın GR00T N1'i (Mart 2025) insansı robotlar (>30 DOF, tüm vücut) için tasarlanmıştır:

- System 2: sahneyi + talimatı okuyan, ~1 Hz'de üst düzey alt hedefler üreten büyük bir VLM.
- System 1: alt koşullara bağlı düşük düzey 50-100 Hz ekleme komutları üreten küçük eylem başlığı transformer'ı.

Bölünme Kahneman'ın hızlı ve yavaş düşünmesine karşılık gelir: System 2 planlar, System 1 hareket eder. Yararları: yavaş VLM boyutlu planlama hızlı kontrolü engellemez; System 1 gecikme için küçük kalır.

GR00T N1.7 (2025 sonu) veri ölçeklemesini geliştirir. GR00T, Omniverse'den sim-to-real verileriyle ince ayar yapar.

### Open X-Embodiment

Eğitim verisi. RT-X (Ekim 2023), 22 robot genelinde 1M yörüngeyi kapsayan 22 veri setini bir araya getirdi. Open X-Embodiment herkesin kullandığı derlemdir:

- ALOHA / Bridge V2 / Droid / RT-2 Kitchen / Language Table.
- Her örnek: (robot durumu, kamera açıları, talimat, eylem dizisi).
- Eğitim hijyeni: ekleme uzayını birleştirin, ekleme aralıklarını normalleştirin, kamera boyutlarını değiştirin.

OpenVLA ve π0 Open X-Embodiment üzerinde eğitilir. Herhangi bir belirli robota alan farkı (domain gap), 100-1000 görev-spesifik demonstrasyonla LoRA ince ayarıyla kapatılır.

### Birlikte ince ayar vs sadece robot

Birlikte ince ayar, web VQA verisini robot yörüngeleriyle harmanlar. Oran önemlidir: çok fazla VQA ve model eylemleri unutur; çok fazla robot verisi ve model genel bilgiyi kaybeder.

RT-2'nin oranı: ~1:1. OpenVLA: ~0.5:1 web-to-robot. π0: benzer. Kesin oran, veri seti boyutuna göre ayarlanması gereken bir hiperparametre.

Sadece robot eğitimi, dağılım dışı talimatlarda başarısız olan görev-spesifik modeller üretir. Birlikte ince ayar, "kırmızı küpü al (demonstrasyonda)" ile "soldan üçüncü en büyük nesneyi al (yeni ifade)" arasındaki farktır.

### Güvenlik ve eylem sınırları

Her üretim VLA'sı şunlarla birlikte gelir:

- Sert ekleme sınırları (spesifikasyon ötesinde tork uygulanamaz).
- Hız sınırları (yumuşak kırpma / soft clipping).
- Çalışma alanı sınırları (uç etkinlik masanın dışına çıkamaz).
- Yeni görevler için insan-onay döngüsü.

Bunlar VLA'nın dışında kontrol katmanı kontrolleri olarak oturur. VLA'nın çıktısı bir öneridir, komut değil.

## Kullan

`code/main.py`:

- 256 kutulu eylem tokenize etme ve tokenize geri alma uygular.
- DCT + quantization tabanlı bir FAST tokenizer taslağı çizer.
- (ayrık-kutu, FAST, sürekli-flow) arasında eylem adımına göre token sayısını karşılaştırır.
- RT-2 → OpenVLA → π0 → GR00T soy ağacını yazdırır.

## Teslim Et

Bu ders `outputs/skill-vla-action-format-picker.md` dosyasını üretir. Bir robot görevi (manipülasyon, navigasyon, insansı tüm vücut) verildiğinde ayrık-kutu + RT-2, FAST + OpenVLA, flow-matching + π0 veya çift sistem + GR00T arasında seçim yapar.

## Alıştırmalar

1. 30 Hz kontrol hızında 10 DOF kol. 256 kutuda ayrık-kutu tokenize etme saniyede kaç token üretir? 7B bir VLM ayak uydurabilir mi?

2. FAST tokenize etme 30 adımlık yörüngeleri ~10 token'a sıkıştırır. Yörünge yüksek frekanslı hareket (örneğin davul çalma) içeriyorsa kullanıcı ne kaybeder?

3. π0'nun flow-matching başlığı ~5 adımda gürültü temizler (denoise). OpenVLA'nın 4-5 Hz'de otoregressive çözümlemesiyle throughput'u karşılaştırın.

4. GR00T'nun System 1 / System 2 bölünmesi Kahneman'a karşılık gelir. Çift ayaklı yürüyüşe yardımcı olabilecek farklı bir bölünme (System 3?) önerin.

5. Open X-Embodiment Bölüm 4'ü veri seti derleme üzerine okuyun. Alan sızıntısını (domain leakage) önleyen üç derleme kuralını adlandırın.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| VLA | "Görüntü-dil-eylem" | Görüntü + talimat alan ve eylem komutları üreten model |
| Eylem tokenize etme | "Ayrık kutular" | Sürekli ekleme hedeflerini boyut başına 256 kutuya quantize etme, her biri bir sözcük dağarcığı ID'si |
| FAST tokenizer | "Frekans eylem token'ları" | 30 adımlık yörüngeleri ~10 token'a sıkıştırmak için DCT + quantize |
| Birlikte ince ayar | "Web + robot karışımı" | Web VQA verisini robot demonstrasyonlarıyla birlikte eğiterek genel bilgiyi koruma |
| Flow-matching eylem başlığı | "π0 sürekli çıktı" | Rectified flow aracılığıyla 50 adımlık eylem dizisi üreten küçük transformer |
| System 1 / System 2 | "Çift sistem kontrolü" | Büyük VLM yavaşça planlar, küçük eylem başlığı hızlıca hareket eder; GR00T paterni |
| Open X-Embodiment | "RT-X veri seti" | 1M yörüngelik çapraz-robot veri seti; eğitim derlemi |

## Daha Fazla Kaynak

- [Brohan ve ark. — RT-2 (arXiv:2307.15818)](https://arxiv.org/abs/2307.15818)
- [Kim ve ark. — OpenVLA (arXiv:2406.09246)](https://arxiv.org/abs/2406.09246)
- [Black ve ark. — π0 (arXiv:2410.24164)](https://arxiv.org/abs/2410.24164)
- [NVIDIA — GR00T N1 (arXiv:2503.14734)](https://arxiv.org/abs/2503.14734)
- [Open X-Embodiment İşbirliği — RT-X (arXiv:2310.08864)](https://arxiv.org/abs/2310.08864)
