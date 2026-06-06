# Açık Ağırlıklı VLM Tarifleri: Aslında Neler Önemli

> 2024-2026 açık ağırlıklı VLM literatürü, kıyaslama deney tablolarının ormanıdır. Apple'ın MM1'i görüntü kodlayıcısı, bağlayıcı (connector) ve veri karışımının 13 kombinasyonunu test etti. Allen AI'ın Molmosu, yoğun insan açıklamalarının GPT-4V damıtmasını (distillation) yendiğini kanıtladı. Cambrian-1, 20+ kodlayıcı karşılaştırması yaptı. Idefics2 beş eksenli tasarım alanını formalize etti. Prismatic VLMs kontrollü bir kıyaslama testi üzerinde 27 eğitim tarifini karşılaştırdı. Bu gürültünün hepsinden küçük bir sonuç kümesi makaleler boyunca tutarlıdır: görüntü kodlayıcısı bağlayıcı mimarisinden daha önemlidir, veri karışımı ikisinden de daha önemlidir ve yoğun insan açıklamaları damıtılmış sentetik veriyi yener. Bu ders bu tabloları okuyor ki sizin okumanıza gerek kalmasın.

**Tür:** Öğren + laboratuvar
**Diller:** Python (stdlib, kıyaslama deney tablosu ayrıştırıcısı + tarif seçici)
**Önkoşullar:** Faz 12 · 05 (LLaVA temeli)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Beş eksenli VLM tasarım alanını adlandırma: görüntü kodlayıcısı, bağlayıcı, LLM, veri karışımı, çözünürlük takvimi.
- Bir MM1 / Idefics2 / Cambrian-1 kıyaslama deney tablosunu okuma ve belirli bir ayarın (knob) hangi kıyaslama testini hareket ettireceğini tahmin etme.
- Bütçe ve görev karışımı verildiğinde yeni bir VLM için bir tarif (kodlayıcı, bağlayıcı, veri, çözünürlük) seçme.
- Neden yoğun insan açıklamalarının aynı token sayısında GPT-4V damıtmasını yendiğini açıklama.

## Sorun

Yüzlerce açık ağırlıklı VLM vardır. "İyi" ile "durumun en iyisi" arasındaki farkın çoğu mimari değildir. Veri, çözünürlük takvimi ve kodlayıcı seçimidir. Modeliniz yetersiz performans gösterdiğinde önce hangi ayarı döndüğünüzü bilmek 5 milyon GPU-saatlik bir hatayı önler.

2023 dalgası (LLaVA-1.5, InstructBLIP, MiniGPT-4) açıklama çifti ön-eğitimi + LLaVA-Instruct-150k ile çalıştı. İyi temel. MMMU'da yaklaşık %35'te tavan yaptı.

2024 dalgası (MM1, Idefics2, Molmo, Cambrian-1, Prismatic VLMs) kapsamlı kıyaslama deneyleri yaptı. Sonuçlar şaşırtıcı ve pragmatikti.

## Kavram

### Beş eksenli tasarım alanı

Idefics2 (Laurençon ve diğerleri, 2024) eksenleri adlandırdı:

1. Görüntü kodlayıcısı. CLIP ViT-L/14, SigLIP SO400m/14, DINOv2 ViT-g/14, InternViT-6B. Kodlayıcılar yama boyutu, çözünürlük ve ön-eğitim hedefinde farklılık gösterir.
2. Bağlayıcı. MLP (2-4 katman), Q-Former (32 sorgu + çapraz-dikkat), Perceiver Resampler (64 sorgu), C-Abstractor (evrişimsel + çift doğrusal havuzlama).
3. Dil modeli. Llama-3 8B / 70B, Mistral 7B, Phi-3, Gemma-2, Qwen2.5. LLM boyutu baskın parametre maliyetidir.
4. Eğitim verileri. Açıklama çiftleri (CC3M, LAION), aralıklı (OBELICS, MMC4), talimat (LLaVA-Instruct, ShareGPT4V, PixMo, Cauldron).
5. Çözünürlük takvimi. Sabit 224/336/448, AnyRes, yerel dinamik. Eğitim sırasında kademeli veya sabit.

Her üretim VLM'i her eksende bir seçim yapar. MMMU puanlarındaki varyansın çoğu 1, 4 ve 5 numaralı eksenler tarafından açıklanır — hangi bağlayıcıyı seçtiğiniz tarafından değil.

### Eksen 1: kodlayıcı > bağlayıcı

MM1 Bölüm 3.2 şunu gösterdi: CLIP ViT-L/14'ten SigLIP SO400m/14'e geçiş MMMU'ya 3+ puan ekledi. Bağlayıcıyı MLP'den Perceiver Resampler'a geçiş 1 puandan az ekledi. Idefics2 bunu tekrarladı: SigLIP > CLIP, aynı token sayısında Q-Former ≈ MLP ≈ Perceiver.

Cambrian-1'in "Cambrian Görüntü Kodlayıcıları Maç-Savaşı" (Tong ve diğerleri, 2024) görüntü-odaklı bir kıyaslama testi (CV-Bench) üzerinde 20+ kodlayıcı çalıştırdı. Liderlik tablosunun üstü DINOv2 ve SigLIP karışımıdır; CLIP orta sıradadır; ImageBind ve ViT-MAE alt sıradadır. CLIP ViT-L'den DINOv2 ViT-g/14'e fark CV-Bench'te ~5-7 puandır.

2026 açık VLM'lerinin varsayılan kodlayıcısı anlamsal + yoğun özellikler için SigLIP 2 SO400m/14'tür, bazen DINOv2 ViT-g/14 özellikleriyle birleştirilir (Cambrian'ın "Uzamsal Görüntü Toplayıcısı" bunu yapar).

### Eksen 2: bağlayıcı tasarımı bir yıkamadır

MM1, Idefics2, Prismatic ve MM-Interleaved aynı sonuca ulaştı: sabit görsel-token sayısında bağlayıcı mimarısı neredeyse hiç önemli değildir. Ortalama havuzlanmış yamalar üzerinde 2 katmanlı MLP, aynı token bütçesinde 32 sorgulu Q-Former ile 1 puan içinde çalışır.

Önemli olan token sayısıdır. Daha fazla görsel token = daha fazla LLM hesaplaması = bir noktaya kadar daha iyi performans, sonra azalan getiriler. Görüntü başına 64 token OCR için çok azdır. 576-1024 token çoğu açık VLM için ideal noktadır. 2048+ yalnızca belgeler ve grafikler için yardımcı olur.

Q-Former vs MLP bir maliyet sorusudur, kalite sorusu değil: Q-Former, görüntü çözünürlüğünden bağımsız olarak token'ları 32-64'te sınırlar; MLP tüm yama token'larını üretir. Yüksek çözünürlüklü girdiler için Q-Former LLM bağlamını korur; düşük çözünürlükte fark gürültüdür.

### Eksen 3: LLM boyutu tavanı belirler

LLM'i 7B'den 13B'ye iki katına çıkarmak her VLM makalesinde MMMU'da güvenilir şekilde 2-4 puan ekler. 70B'de çoğu kıyaslama doyar. VLM'in çoklu akıl yürütme (multimodal reasoning) tavanı, LLM'in metin akıl yürütme tavanıdır — görüntü kodlayıcısı yalnızca besleyebilir, onun için akıl yürütemez.

Bu yüzden Qwen2.5-VL-72B ve Claude Opus 4.7 MMMU-Pro ve ScreenSpot-Pro'da ezici üstünlük kurar: dil beyni devasadır. 7B VLM, zekice bağlayıcı tasarımıyla 70B VLM'in yerini tutamaz.

### Eksen 4: veri — yoğun insan açıklamaları damıtmayı yener

Molmo + PixMo (Deitke ve diğerleri, 2024) herkesin okuması gereken 2024 sonucudur. Allen AI, insan etiketleyicilere görüntüleri 1-3 dakikalık yoğun konuşma-metin pasajlarında tarif ettirdi, 712K yoğun açıklanmış görüntü elde edildi. Eğitim verisinde hiçbir yerde GPT-4V damıtması yoktu.

Molmo-72B 11/11 kıyaslama testinde Llama-3.2-90B-Vision'ı yendi. Fark mimari değil — açıklama kalitesidir. Yoğun insan açıklamaları görüntü başına kısa web açıklamalarından 5-10x daha fazla bilgi taşır ve GPT-4V damıtmasının hayal ettiği yerlerde olgusal temelli kalır.

ShareGPT4V (Chen ve diğerleri, 2023) ve Cauldron (Idefics2) aynı senaryoyu insan + GPT-4V açıklamaları karışımıyla takip etti. Eğilim açıktır: 2026 çığır açanları için açıklama yoğunluğu > açıklama miktarı > damıtma kolaylığı.

### Eksen 5: çözünürlük ve takvimi

Idefics2'nin kıyaslama deneyleri: 384 -> 448 1-2 puan ekler. 448 -> 980 görüntü bölme (AnyRes) ile OCR kıyaslama testlerinde ek 3-5 puan ekler. Düz çözünürlük eğitimi orta doğrulukta platoya ulaşır; çözünürlük kademelendirmesi (224'te başla, 484 veya yerel çözünürlükte bitir) daha hızlı eğitir ve daha yüksek biter.

Cambrian-1 çözünürlük vs token takası yaptı: sabit hesaplama gücünde daha düşük çözünürlükte daha fazla token veya daha yüksek çözünürlükte daha az token alabilirsiniz. OCR için daha yüksek çözünürlük kazanır; genel sahne anlama için daha düşük çözünürlük-daha fazla token kazanır.

2026 üretim tarifi: 1. aşamayı sabit 384'te, 2. aşamayı OCR-ağır görevler için 1280'e kadar dinamik çözünürlükle eğitin.

### Prismatic kontrollü karşılaştırma

Prismatic VLMs (Karamcheti ve diğerleri, 2024) tüm eksenleri kontrol eden makaledir. Aynı 13B LLM, aynı talimat verisi, aynı değerlendirme — yalnızca bir eksende değişim. Sonuçlar:

- Görüntü başına görsel-token sayısı varyansın ~%60'ını açıklar.
- Kodlayıcı seçimi ~%20'yi açıklar.
- Bağlayıcı mimarisi ~%5'i açıklar.
- Diğer her şey (veri karışımı, zamanlayıcı, öğrenme hızı) kalan ~%15'i.

Bu kabaca bir ayrıştırmadır ama literatürde "ilk olarak hangi deneyi yapmalıyım" sorusunun en temiz cevabıdır.

### 2026 için bir seçici

Kanıtlar ışığında, 2026'da yeni bir proje için varsayılan açık-VLM tarifi:

- Kodlayıcı: NaFlex ile yerel çözünürlükte SigLIP 2 SO400m/14, segmentasyon/sapma (grounding) gerekirse yoğun özellikler için DINOv2 ViT-g/14 ile birleştirilmiş.
- Bağlayıcı: Yama token'ları üzerinde 2 katmanlı MLP. Token kısıtlı değilseniz Q-Former'ı atlayın.
- LLM: Qwen2.5 / Llama-3.1 / Gemma 2, maliyet için 7B, kalite için 70B, hedef gecikmeye göre seçim.
- Veri: PixMo + ShareGPT4V + Cauldron, görev özel talimat verileriyle tamamlanmış.
- Çözünürlük: dinamik (uzun kenar başına min 256, max 1280 piksel).
- Takvim: 1. aşama hizalama (yalnızca projeksiyoncu), 2. aşama tam ince ayar, 3. aşama görev özel ince ayar.

Bu varsayımların her biri bu dersin sonunda atıfta bulunulan makalelerdeki ölçülmüş kıyaslama deneyine kadar izlenebilir.

## Kullan

`code/main.py` bir kıyaslama deney tablosu ayrıştırıcısı ve tarif seçicisidir. MM1 ve Idefics2 kıyaslama deney tablolarını (sıkıştırılmış) kodlar ve sorgulamanıza olanak tanır:

- "Verilen bütçe X ve görev Y, hangi tarif kazanır?"
- "7B Llama'da SigLIP'i CLIP ile değiştirirsem beklenen MMMU farkı nedir?"
- "%80 güvenle cevap almak için ilk olarak hangi ekseni deneyeyim?"

Çıktı, beklenen kıyaslama farklarıyla sıralanmış bir tarif listesi ve "ilk olarak dene" önerisidir.

## Teslimat

Bu ders `outputs/skill-vlm-recipe-picker.md` dosyasını üretir. Hedef görev karışımı, bütçe ve gecikme hedefi verildiğinde, her seçimi gerekçelendiren kıyaslama deneyine atıfla tam bir tarif (kodlayıcı, bağlayıcı, LLM, veri karışımı, çözünürlük takvimi) üretir. Her yeni VLM projesi başladığında Idefics2 kıyaslama deney tablosunu yeniden icat etmeyi mühendisler için durdurur.

## Alıştırmalar

1. MM1 Bölüm 3.2'yi okuyun. Sabit 2B LLM ve 50M görüntü bütçesinde hangi kodlayıcı kazanır? 13B LLM'de cevap tersine döner mi? Neden?

2. Cambrian-1, DINOv2 + SigLIP birleştirmenin görüntü odaklı kıyaslama testlerinde her ikisini tek başına yendiğini ama MMMU'da sinyal eklemediğini buluyor. Hangi kıyaslama testlerinin arttığını ve hangilerinin sabit kaldığını tahmin edin.

3. Hedefiniz 2B LLM üzerinde bir mobil arayüz ajanı. Kodlayıcı, bağlayıcı, çözünürlük ve veri karışımı seçin. Her seçimi belirli bir kıyaslama deney tablosuyla gerekçelendirin.

4. Molmo 4B ve 72B modelleri sunar. 4B, kapalı 7B VLM'lerle rekabet eder; 72B 11/11 kıyaslama testinde Llama-3.2-90B-Vision'ı yener. Bu LLM boyutu platoya ilişkin hipotez hakkında ne söylüyor?

5. 7B VLM'de veri karışımı kalitesini kodlayıcı kalitesinden izole etmek için bir kıyaslama deney tablosu tasarlayın. Minimum kaç eğitim çalışması gerekir? Dört ayar ayarını önerin.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Kıyaslama deneyi (Ablation) | "Tek bir ayarı çevirme" | Tam olarak bir tasarım alanı ekseninde farklılık gösteren birden fazla eğitim çalışması, diğer her şey sabit tutularak |
| Bağlayıcı (Connector) | "Köprü" / "projeksiyoncu" | Görüntü kodlayıcısı çıktısını LLM'in token uzayına haritalayan eğitilebilir modül (MLP, Q-Former, Perceiver) |
| Yoğun insan açıklaması | "Yoğun açıklama" | Kısa web alternatif metninden daha zengin, çok cümleli insan yazılı açıklama (genellikle 80-300 token) |
| Damıtma (Distillation) | "GPT-4V açıklamaları" | Daha güçlü tescilli bir VLM tarafından üretilen eğitim verisi; kullanışlı ama devralınmış hayal ürünü eğilimli |
| AnyRes / dinamik çözünürlük | "Yüksek çözünürlük yolu" | Döşeme veya M-RoPE aracılığıyla kodlayıcının yerel çözünürlüğünden daha büyük görüntüleri besleme stratejisi |
| Çözünürlük kademelendirmesi | "Müfredat" | Düşük çözünürlükte başlayıp artırarak hizalama öğrenmesini hızlandıran eğitim takvimi |
| Görüntü odaklı kıyaslama | "CV-Bench / BLINK" | Dil-yoğun akıl yürütmeyi değil, ince görsel algıyı sınayan değerlendirme |
| PixMo | "Molmo'nun verisi" | Allen AI'ın 712K yoğun açıklanmış görüntü veri seti; insan konuşması yoğun açıklamalara dönüştürülmüş |

## İleri Okuma

- [McKinzie ve diğerleri — MM1 (arXiv:2403.09611)](https://arxiv.org/abs/2403.09611)
- [Laurençon ve diğerleri — Idefics2 / VLM inşa ederken ne önemlidir (arXiv:2405.02246)](https://arxiv.org/abs/2405.02246)
- [Deitke ve diğerleri — Molmo ve PixMo (arXiv:2409.17146)](https://arxiv.org/abs/2409.17146)
- [Tong ve diğerleri — Cambrian-1 (arXiv:2406.16860)](https://arxiv.org/abs/2406.16860)
- [Karamcheti ve diğerleri — Prismatic VLMs (arXiv:2402.07865)](https://arxiv.org/abs/2402.07865)
