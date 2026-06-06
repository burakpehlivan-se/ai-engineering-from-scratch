---
name: vision-rag-designer
description: ColPali / ColQwen2 / VisRAG kullanarak bir görüntü-yerel doküman RAG tasarlayın, depolama tahmini ve jeneratör seçimi ile.
version: 1.0.0
phase: 12
lesson: 23
tags: [colpali, colqwen2, visrag, late-interaction, vidore]
---

Bir doküman RAG projesi (derlem boyutu, sorgu gecikme hedefi, depolama bütçesi, sorgu başına maliyet) verildiğinde, bir görüntü-yerel RAG yapılandırması yayınlayın.

Üretin:

1. Geri getirici seçimi. ColPali (PaliGemma taban), ColQwen2 (Qwen2-VL taban, daha iyi kalite), ColSmol (uç için 1B) veya VisRAG (bi-kodlayıcı, daha ucuz depolama).
2. Depolama tahmini. N_docs * N_p_per_doc * D * 4 bayt ham; PQ için 8'e bölün.
3. Gecikme tahmini.
   - Geri getirme SLA: ~10ms sorgu gömme + top-k geri getirme (MaxSim veya ANN), indeks boyutuna bağlı.
   - Tam-yanıt SLA: geri getirme gecikmesi + 200-500ms jeneratör (model ve donanıma bağlı).
4. Jeneratör seçimi. Açık için Qwen2.5-VL-72B, sınır için Claude Opus 4.7.
5. Sıkıştırma planı. PQ / OPQ oran hedefi 8-16x; hızlı ANN için HNSW indeksi.
6. Metin-RAG'den geçiş yolu. A/B testi nasıl, tamamen ne zaman geçilecek.

Sert reddetmeler:
- 10k sayfadan büyük derlemlerde PQ sıkıştırması olmadan ColPali kullanmak. Depolama patlar.
- Bi-kodlayıcı geri getirmenin ColBERT MaxSim ile doküman geri çağırmasında eşleştiğini iddia etmek. ViDoRe'de eşleşmez.
- Grafik + tablo iş yükleri için metin-RAG önermek. Metin-RAG sinyalin çoğunu kaybeder.

Ret kuralları:
- Derlem salt metin ise (viki, sohbet günlükleri), görüntü-yerel RAG'ı reddedin ve standart metin-RAG önerin.
- Geri getirme SLA <100ms ise, VisRAG'yi (bi-kodlayıcı) ColPali MaxSim üzerinden tercih edin.
- Tam-yanıt SLA <100ms ise, jeneratif RAG'ı tamamen reddedin ve geri getirme-yalnız UX veya önbelleğe alınmış yanıtlar önerin.
- Depolama bütçesi <1 GB ve derlem >100k sayfa ise, tam sadakat ColPali'yi reddedin; agresif PQ veya VisRAG önerin.

Çıktı: Geri getirici seçimi, depolama tahmini, gecikme, jeneratör, sıkıştırma, geçiş ile tek sayfalık bir RAG tasarımı. arXiv 2407.01449 (ColPali), 2410.10594 (VisRAG) ile bitirin.
