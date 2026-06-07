# Multimodal RAG ve Çapraz-Modal Retrieval

> Görünme-yönelik belge RAG'ı tek bir kesittir. Üretim multimodal RAG'ı daha geniş bir yelpazeye açılır — gezi planlama ("bana doğal ışıkta sessiz bir vegan kahvaltı bul"), tıbbi triyaj ("bu fotoğraf + bu notlar hangi yaraya uygun"), e-ticaret ("bu özçekimime benzer kıyafetler, benim bedenimde") ve saha hizmeti ("bu motor sesini teşhis edin artı parçanın fotoğrafı") gibi iş akışlarında metin, görüntü, ses ve video genelinde retrieval. 2025'teki üç anket — Abootorabi ve ark., Mei ve ark., Zhao ve ark. — alt sorunları kodladı: çapraz-modal retrieval, retrieval birleştirme (fusion), üretim temelleme (grounding), multimodal değerlendirme. Bu ders anketleri okur ve üretim bir boru hattı tasarlar.

**Tür:** İnşa Et
**Diller:** Python (stdlib, birleştirme + temellenmiş üreteçli çapraz-modal retriever)
**Ön koşullar:** Faz 12 · 23 (ColPali), Faz 11 (RAG temelleri)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Çapraz-modal retrieval tasarlayın: metin → görüntü, görüntü → metin, ses → video vb.
- Üç birleştirme stratejisini karşılaştırın: puan birleştirmesi (score fusion), attention tabanlı birleştirme, MoE birleştirmesi.
- Üretim temelleme (grounding) açıklayın: kaynakların bir karışık modalite olduğu durumda "kaynaklarınızı gösterin" nasıl görünür.
- 2025'in üç kanonik multimodal RAG anketini ve alt soru sınıflandırmalarını adlandırın.

## Problem

Tek modallıklı RAG çözülmüş bir paterndir: sorguyu gömün, parçaları gömün, getirin, LLM'e doldurun. Multimodal RAG şunları gerektirir:

1. Çoklu retrieval başlığı (her modallık uyumlu bir uzayda embedding'lere ihtiyaç duyar).
2. Modallıklar arası retrieval sonuçlarının birleştirilmesi (fusion).
3. Modallıklar arası kaynakları gösteren üretim temelleme.
4. Çapraz-modal sinyali kapsayan değerlendirme metrikleri.

2025 anketleri aynı sınıflandırmaya varır.

## Kavram

### Çapraz-modal retrieval

B modallığında belgeleri, A modallığında bir sorgu verildiğinde getirin. Üç patern:

1. Ortak embedding uzayı. CLIP ve CLAP, metin + görüntü / metin + ses embedding'lerini ortak bir uzayda üretir. Modallıklar arası kosinüs benzerliği doğrudan çalışır. CLIP-eğitilmiş çiftlerle sınırlıdır.

2. Modallık-başına encoder + çevirme. Metin encoder'ı + görüntü encoder'ı + uzaylar arasında eşleyen küçük bir çevirmen modülü. Gupta ve ark.'dan Sen2Sen ve diğer 2024 tasarımları. Esnek ancak karmaşıklık ekler.

3. VLM olarak encoder. Bir VLM'in gizli durumlarını (hidden states) temsil olarak kullanma. VLM'in desteklediği her modallık çalışır. Daha yüksek kalite, daha pahalı.

Seçim: metin+görüntü için CLIP / SigLIP 2; metin+ses için CLAP; sınır kalitesinde çapraz-modal için VLM-gizli-durumları.

### Birleştirme stratejileri

10 sonuç getirdiniz: 5 görüntü, 3 metin parçası, 2 ses klibi. Nasıl birleştirirsiniz?

Puan birleştirmesi (en ucuz). Her modallığın kendi retriever'ı var, her biri puanlar döndürür. Puanları modallık-içinde normalleştirin sonra toplayın. Basit, genellikle çalışır.

Attention tabanlı birleştirme. Tüm getirilen öğeleri birleştirin, küçük bir attention ağı bunları ağırlıklandırır. Eğitim gerektirir.

MoE birleştirmesi. Kapı (gating) ağı modallık-başına uzmanlara yönlendirir. Farklı sorgu türleri farklı yönlendirilir — görsel bir soru görüntüleri daha yüksek ağırlıklandırır.

Üretim varsayılanı: sorgunun baskın modallığına hafif bir önyargıyla puan birleştirmesi. A/B testinde alanınıza açık kazanımlar gösteriyorsa MoE'ye yükseltin.

### Üretim temelleme (grounding)

LLM her iddianın hangi getirilen öğeyi yönlendirdiğini göstermelidir. Multimodal için:

- Metin kaynağı: standart atıf `[1]`.
- Görüntü kaynağı: kısa açıklamayla `[img 3]`.
- Ses: `[audio 2 at 0:34]`.

Üreteci temelleme-farkındalıklı veriyle eğitin: eğitim hedefindeki her iddia kaynak indeksiyle etiketlenir. Çıkarımda model doğal olarak atıflar üretir.

### 2025 anketleri

Abootorabi ve ark. (arXiv:2502.08826, "Herhangi Bir Modalla Sor"): multimodal RAG için sınıflandırma. Retrieval, birleştirme, üretimi kapsar. En geniş kapsama alanı.

Mei ve ark. (arXiv:2504.08748, "Multimodal RAG Üzerine Bir Anket"): alt görev benchmark'larına ve hata modlarına odaklanır. Değerlendirme tasarımı için yararlı.

Zhao ve ark. (arXiv:2503.18016): görsele odaklı anket. ColPali ailesi çalışmalarında güçlü.

Üçünü de okumak, 2025 baharına kadar durumun sunar. Alt soruların çoğu hâlâ açıktır.

### MuRAG — temel makale

MuRAG (Chen ve ark., 2022) ilk multimodal RAG'tı. Multimodal KB'den görüntü + metin getirdi, cevaplar üretti. VLM dalgasından önce uygulanabilirliği gösterdi. Modern sistemler (REACT, VisRAG, M3DocRAG) bunun üzerine inşa edilir.

### Üretim gezi planlayıcı örneği

Sorgu: "bana doğal ışıkta sessiz bir vegan kahvaltı bul."

Boru hattı:

1. Sorguyu ayrıştırın. "sessiz" → ses/inceleme anahtar kelimesi; "vegan kahvaltı" → menü öğesi; "doğal ışık" → görüntü özelliği.
2. Modallık başına retrieval:
 - İncelemelerde metin retrieval'ı: "vegan kahvaltı, sessiz ortam."
 - Restoran fotoğraflarında görüntü retrieval'ı: "doğal ışık, ferah."
 - Ortam sesi kliplerinde ses retrieval'ı: "düşük desibel, müzik yok."
3. Puanları birleştirin. Her restoranın bileşik bir puanı vardır.
4. En iyi k restoran → tüm kanıtlarla VLM üreteci → atıflı cevap.

Bu metin-RAG'ın çok ötesindedir. Her modallık tek metnin kaçırdığı sinyali ekler.

### Ajanlı multimodal RAG

Çoklu atlamalı (multi-hop): ilk retrieval yüksek güvenli cevaplar döndürmüyorsa, LLM yeniden formüle eder ve tekrar getirir. Faz 14'teki ajanlı RAG paternleri burada geçerlidir. Örnekler:

- İlk en iyi 10'u getir → LLM "çok gürültülü, <40 dB filtrele" der → tekrar getir.
- Görüntüleri getir → LLM birinde menü görür → menü metnini getir → cevap verir.

Karmaşıklık ekler ancak tek atışlı retrieval'ın başaramadığı sorguları işler.

### Değerlendirme

Çapraz-modal değerlendirme hâlâ olgun değil. Yaygın vekiller:

- Modallık-başına Recall@k.
- Birleştirilmiş en iyi k doğruluğu.
- İnsan yargılı uçtan uca memnuniyet.
- Göreve özel (tamamlanan rezervasyonlar, yapılan satın almalar).

Tüm modallıkları kapsayan standart benchmark yoktur. Makalelerin çoğu görev-spesifik değerlendirir.

## Kullan

`code/main.py`:

- Restoranlar üzerinde ortak bir derlemde çalışan üç sahte retriever (metin, görüntü, ses).
- Modallık puanlarını yapılandırılabilir ağırlıklarla birleştiren puan birleştirmesi.
- Atıflı son cevabı üreten bir üreteç taslağı.
- Güven düşükse sorguyu yeniden formüle eden basit bir ajanlı döngü.

## Teslim Et

Bu ders `outputs/skill-multimodal-rag-designer.md` dosyasını üretir. Multimodal sorgu akışına sahip bir ürün özelgesi verildiğinde, retriever'ları, birleştirmeyi, üreteci ve değerlendirmeyi tasarlar.

## Alıştırmalar

1. Tıbbi triyaj multimodal RAG'ı önerin: sorgu = yar fotoğrafı + metin semptomları. Hangi modallıklar hangi KB'den retrieval yapar?

2. Puan birleştirmesi basit bir ağırlıklı toplamdır. MoE birleştirmesinin kaçırdığı hata modu nedir?

3. Abootorabi ve ark.'nın sınıflandırmasını okuyun (Bölüm 3). Üç kanonik alt soru nedir ve seçtiğiniz ürüne nasıl karşılık gelir?

4. Bir gezi planlayıcı multimodal RAG için değerlendirme özelgesi tasarlayın. Görüntü hatırlaması, ses hatırlaması ve bileşik doğru hangi metrikleri kapsar?

5. Ajanlı çoklu atlamalı RAG round-trip başına bir gecikme vergisi taşır. Hangi sorgu karmaşıklığında doğruluk kazancı gecikmeyi doğrular?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Çapraz-modal retrieval | "Bir modalla sorgula, başka birini getir" | Metin sorgusu görüntüleri getirir; görüntü sorgusu metni getirir; ortak uzay veya çevirmen gerektirir |
| Puan birleştirmesi | "Puanları birleştir" | Modallık-başına retrieval puanlarının ağırlıklı toplamı; en basit birleştirme |
| MoE birleştirmesi | "Modallık-yönlendirmeli uzmanlar" | Kapı ağı hangi modallığın puanlarına güveneceğini sorgu başına seçer |
| Temellenmiş üretim | "Kaynaklarınızı gösterin" | Cevaptaki her iddia kaynak indeksiyle etiketlenir |
| MuRAG | "İlk multimodal RAG" | Multimodal RAG paternini kuran 2022 makalesi |
| Ajanlı çoklu atlama | "Yeniden formüle et ve tekrar dene" | İlk tur güven düşüklüğünde LLM retriever'ları tekrar sorgular |

## Daha Fazla Kaynak

- [Abootorabi ve ark. — Herhangi Bir Modalla Sor (arXiv:2502.08826)](https://arxiv.org/abs/2502.08826)
- [Mei ve ark. — Multimodal RAG Üzerine Bir Anket (arXiv:2504.08748)](https://arxiv.org/abs/2504.08748)
- [Zhao ve ark. — Görüntü RAG Anketi (arXiv:2503.18016)](https://arxiv.org/abs/2503.18016)
- [Chen ve ark. — MuRAG (arXiv:2210.02928)](https://arxiv.org/abs/2210.02928)
- [Liu ve ark. — REACT (arXiv:2301.10382)](https://arxiv.org/abs/2301.10382)
