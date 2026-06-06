# ColPali ve Görünme-Yönelik Belge RAG'ı

> Geleneksel RAG, PDF'leri metne ayrıştırır, parçalara böler (chunks), parçaları gömer (embeds), vektörleri saklar. Her adım sinyal kaybeder: OCR grafik verisini düşürür, parçalama tablo satırlarını böler, metin embedding'leri şekilleri görmezden gelir. ColPali (Faysse ve ark., Temmuz 2024) daha basit bir sordu: neden hiç metin çıkarmıyorsunuz? Sayfa görüntüsünü doğrudan PaliGemma aracılığıyla gömün, retrieval için ColBERT tarzı geç etkileşim (late interaction) kullanın ve belgenin taşıdığı tüm düzen, şekil, font ve biçimlendirme sinyalini koruyun. Yayınlanmış benchmark'lar: görsel olarak zengin belgelerde metin-RAG'a kıyasla %20-40 daha iyi uçtan uca doğruluk. ColQwen2, ColSmol ve VisRAG paterni genişletti. Bu ders görünme-yönelik RAG tezini okur ve minik bir ColPali benzeri indeksleyici (indexer) oluşturur.

**Tür:** İnşa Et
**Diller:** Python (stdlib, çoklu vektör indeksleyici + MaxSim puanlayıcısı)
**Ön koşullar:** Faz 11 (LLM Mühendisliği — RAG temelleri), Faz 12 · 05 (LLaVA)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Bi-encoder retrieval'ın (belge başına tek vektör) ve geç etkileşimli retrieval'ın (belge başına çok vektör) farkını açıklayın.
- ColBERT'in MaxSim işlemini ve ColPali'nin bunu metin token'larından görüntü yamalarına nasıl genelleştirdiğini tanımlayın.
- Minik bir ColPali benzeri indeksleyici oluşturun: sayfa → patch embedding'leri → sorgu terimi embedding'leri üzerinde MaxSim → en iyi k sayfa.
- Fatura / finansal rapor kullanım durumunda ColPali + Qwen2.5-VL üretecini metin-RAG + GPT-4 ile karşılaştırın.

## Problem

PDF'ler üzerinde metin-RAG belgenin çoğunu atar. Bir finansal raporun 3. çeyrek gelir büyümesi genellikle bir grafiktedir; bir tıbbi raporun bulguları notlanmış görüntülerdedir; bir yasal sözleşmenin imza bloğu bir düzgerçek (layout fact), bir metin gerçeği değil.

Metin-RAG boru hattı:

1. PDF → OCR / pdftotext aracılığıyla metin.
2. Metin → 300-500 tokenlık parçalar.
3. Parça → bi-encoder embedding'i (tek vektör).
4. Kullanıcı sorgusu → embedding → kosinüs benzerliği → en iyi k parça.
5. Parçalar + sorgu → LLM.

Beş kayıplı adım. Grafikler yakalanamıyor. Tablolar parçalar arasında bölünüyor. Çok sütunlu düzgerçek düzleşiyor. Şekil notları kayboluyor.

ColPali'nin çözümü: OCR'ı atlayın, sayfa görüntüsünü doğrudan gömün. Retrieval için ColBERT tarzı geç etkileşim kullanın, böylece model sorgu zamanında ince taneli yamalara dikkat edebilsin.

## Kavram

### ColBERT (2020)

ColBERT (Khattab & Zaharia, arXiv:2004.12832) bir metin retrieval yöntemidir. Belge başına tek vektör yerine, token başına bir vektör üretir. Sorgu zamanında:

- Sorgu token'ları kendi embedding'lerini alır (N_q vektör).
- Belge token'ları embedding'leri alır (N_d vektörü, tipik olarak önbelleklenmiş).
- Puan = sorgu token'ları üzerindeki max'ların toplamı: Σ_i max_j cos(q_i, d_j).

Bu MaxSim işlemidir. Her sorgu token'ı en iyi eşleşen belge token'ını "seçer". Son puan toplamıdır.

Artıları: güçlü hatırlama (recall), terim düzeyinde semantikleri işler. Eksileri: belge başına N_v vektörü, depolama pahalı.

### ColPali

ColPali (Faysse ve ark., arXiv:2407.01449) ColBERT paternini görüntülere uygular.

- Her sayfa PaliGemma (ViT + dil) tarafından patch embedding'lerine kodlanır: sayfa başına N_p vektör.
- Her kullanıcı sorgusu (metin) sorgu-token embedding'lerine kodlanır: N_q vektörü.
- Puan = Σ_i max_j cos(q_i, p_j), yani sorgu-metin-token'ları ve sayfa-görüntü-yamaları üzerinde MaxSim.
- Toplam puana göre en iyi k sayfayı getirin.

Belge-alma zamanında: her sayfayı PaliGemma ile gömün, tüm patch embedding'lerini saklayın. Sorgu zamanında: sorgu token'larını gömün, tüm saklanmış sayfa embedding'lerine karşı MaxSim hesaplayın, en iyi k sayfayı döndürün.

Artıları: uçtan uca görsel olarak zengin belgelerde metin-RAG'ı %20-40 yener. Her patch-vektörü yerel düzen ve içeriği yakalar.

Eksileri: N_p yama × 4 byte float × D-boyutlu vektör / sayfa = depolama hızla büyür. PQ / OPQ quantization ile hafifletilir.

### ColQwen2 ve ColSmol

ColQwen2 (illuin-tech, 2024-2025) PaliGemma yerine Qwen2-VL kullanır. Daha iyi temel encoder, daha iyi retrieval.

ColSmol yerel / kenar (edge) kullanımı için daha küçük ölçekli varyanttır. ~1B parametreli bir ColSmol retriever tüketici GPU'sunda çalışır.

### VisRAG

VisRAG (Yu ve ark., arXiv:2410.10594) farklı bir varyanttır: yamalar üzerinde MaxSim yerine, her sayfayı bir VLM ile tek bir vektöre havuzlayıp (pool) bi-encoder retrieval yapar. Daha hızlı indeksleme + daha küçük depolama, daha zayıf hatırlama.

Kalite-maliyet tavizi: kalite için ColPali, ölçek için VisRAG.

### M3DocRAG

M3DocRAG (Cho ve ark., arXiv:2411.04952) çoklu belge çıkarmalı retrieval'ı çoklu sayfa çıkarmalı çıkarıma genişletir. Belgeler arası sayfaları getirir, VLM için çok sayfalık bir bağlam birleştirir.

### ViDoRe — benchmark

ColPali'nin tamamlayıcı benchmark'ı. Görsel Belge Retrieval Değerlendirmesi (Visual Document Retrieval Evaluation). Görevler finansal raporları, bilimsel makaleleri, idari belgeleri, tıbbi kayıtları, kılavuzları kapsar. Metrik: nDCG@5.

ColPali-v1 ViDoRe'de ~%80 nDCG@5 puanı alır; aynı belgelerde metin-RAG ~%50-60 puan alır.

### Uçtan uca RAG boru hattı

Görünme-yönelik RAG için:

1. Alma: PDF → sayfa görüntüleri → PaliGemma kodlama → tüm patch embedding'lerini saklayın.
2. Sorgulama: kullanıcı metni → sorgu-token embedding'leri → tüm indeksli sayfalara karşı MaxSim → en iyi k sayfa.
3. Üretme: en iyi k sayfa görüntüsü + sorgu → VLM (Qwen2.5-VL veya Claude) → cevap.

Hiçbir yerde OCR yok. Şekiller, grafikler, fontlar, düzen tümü cevaba akar.

### Depolama matematiği

Sayfa başına 729 patch ve 128 boyutlu embedding ile 50 sayfalık bir finansal rapor:

- ColPali: 50 * 729 * 128 * 4 byte = ~18 MB ham, PQ sonrası ~4 MB.
- Metin-RAG: 50 parça * 768 boyut * 4 byte = ~150 kB.

ColPali belge başına ~30x daha fazla depolama. Ölçekli OPQ / PQ bunu ~5-10x'e düşürür, genellikle katlanılabilir.

### Metin-RAG'ın hâlâ kazandığı durumlar

- Düzen sinyali olmayan saf metin belgeleri (wiki makaleleri, sohbet kayıtları). Metin-RAG daha basit ve depolama-maliyeti ucuzdur.
- Depolamanın maliyeti belirlediği milyonlarca sayfalık arşivler.
- Yanı sıra çıkarılabilir OCR metni gerektiren sıkı düzenleyici gereksinimleri.

2026'da geri kalan her şey için — finansal raporlar, bilimsel makaleler, yasal sözleşmeler, tıbbi kayıtlar, UX dokümantasyonu — görünme-yönelik RAG kazanır.

## Kullan

`code/main.py`:

- Bir "sayfayı" (özellik vektörlerinin küçük ızgarası) patch embedding'leri dizisine eşleyen oyuncak patch encoder.
- Sorgu token' embedding'i kümesi ile sayfa patch kümesi arasında ColBERT tarzı puan hesaplayan MaxSim puanlayıcısı.
- 5 oyuncak sayfayı indeksler, 3 sorgu çalıştırır, puanlarla en iyi k döndürür.

## Teslim Et

Bu ders `outputs/skill-vision-rag-designer.md` dosyasını üretir. Bir belge-RAG projesi verildiğinde ColPali / ColQwen2 / VisRAG / metin-RAG'i seçer ve depolamayı boyutlandırır.

## Alıştırmalar

1. Sayfa başına 729 patch, 128 boyutlu embedding, 4 byte float ile 200 sayfalık yıllık rapor. Ham depolama ve sıkıştırılmış (8x) depolamayı hesaplayın.

2. MaxSim Σ_i max_j cos(q_i, p_j)'dir. Bu toplam, basit ortalama benzerliğin yakalayamadığı şeyi yakalar mı?

3. ColPali sayfaları patch kümeleri olarak indeksler. Kelime düzeyinde indekslersek (ColBERT'in yaptığı gibi) ne değişir? Tavizler?

4. Sorgu başına 500ms gecikme bütçesiyle 1M sayfalık bir derlem için uçtan uca boru hattını tasarlayın. ColQwen2 / VisRAG seçin ve gerekçelendirin.

5. M3DocRAG'ı okuyun (arXiv:2411.04952). Tek sayfalı ColPali retrieval'dan farklı olan çok sayfalık attention desenini tanımlayın.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Geç etkileşim | "ColBERT tarzı" | Token başına veya yama başına embedding'ler + MaxSim kullanan retrieval; tek belge vektörü değil |
| MaxSim | "Yamalar üzerinde max" | Her sorgu token'ı için en yüksek benzerlikli belge token'ını seç; sorgu genelinde topla |
| Bi-encoder | "Tek vektör" | Belge başına tek vektör; daha hızlı ancak taneliliği kaybeder |
| Çoklu vektör | "Belge başına çok vektör" | Belge / sayfa başına N_p vektör sakla; depolama maliyeti artar ancak hatırlama iyileşir |
| Patch embedding | "Sayfa özelliği" | VLM encoder'ından görüntü yaması başına bir vektör, sayfa başına önbelleklenmiş |
| ViDoRe | "Görsel belge benchmark'ı" | ColPali'nin görsel belge retrieval benchmark'ı |
| PQ quantization | "Ürün quantization" | Depolamayı ~8x küçültürken vektör benzerliğini koruyan sıkıştırma |

## Daha Fazla Kaynak

- [Faysse ve ark. — ColPali (arXiv:2407.01449)](https://arxiv.org/abs/2407.01449)
- [Khattab & Zaharia — ColBERT (arXiv:2004.12832)](https://arxiv.org/abs/2004.12832)
- [Yu ve ark. — VisRAG (arXiv:2410.10594)](https://arxiv.org/abs/2410.10594)
- [Cho ve ark. — M3DocRAG (arXiv:2411.04952)](https://arxiv.org/abs/2411.04952)
- [illuin-tech/colpali GitHub](https://github.com/illuin-tech/colpali)
