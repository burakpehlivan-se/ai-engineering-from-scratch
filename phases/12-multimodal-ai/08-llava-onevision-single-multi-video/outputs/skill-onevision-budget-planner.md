---
name: onevision-budget-planner
description: Hedef ürün karışımı için tek-görüntü, çoklu-görüntü ve video senaryoları arasında LLaVA-OneVision tarzı birleşik görsel-token bütçeleri ayırın.
version: 1.0.0
phase: 12
lesson: 08
tags: [llava-onevision, token-budget, curriculum, multi-image, video]
---

Bir ürünün beklenen görev dağılımı -- tek-görüntü, çoklu-görüntü ve video isteklerinin yüzdeleri -- ve örnek başına görsel-token bütçesi verildiğinde, senaryo başına bir tahsis planı ve bir eğitim müfredatı yayınlayın.

Üretin:

1. Senaryo başına yapılandırma. Tek-görüntü: AnyRes döşeme sayısı + küçük resim + havuzlama faktörü; çoklu-görüntü: örnek başına görüntü + görüntü başına havuzlama; video: kare sayısı + kare başına havuzlama.
2. Token bütçesi dengesi. Her senaryonun toplam token'ları hedef bütçenin ±%30'u içinde olmalıdır; hedefin %70'inin altına düşen (yetersiz tokenlanmış) veya %130'unun üzerine çıkan (bağlam riski) herhangi bir senaryoyu işaretleyin.
3. Müfredat planı. Üç aşama (SI -> OV -> TT) veri ağırlıklarıyla. TT aşaması için, kullanıcının ürün karışımını kullanın.
4. Beklenen ortaya çıkan beceriler. Kullanıcının ürün karışımı verildiğinde, hangi LLaVA-OneVision tarzı ortaya çıkan yeteneklerin muhtemelen görüneceğini tahmin edin (çoklu-kamera, işaret kümesi, ekran görüntüsü-ajanı veya ürüne özgü varyantlar).
5. Eğitim verisi tahmini. 7B tabanlı LLM verilen aşama başına yaklaşık token / görüntü / kare sayıları, OneVision-1.5 veri ölçeğine atıfta bulunarak.

Sert reddetmeler:
- Videoyu veya çoklu-görüntüyü tek-görüntüden önce koyan aşama sıraları önermek. OneVision bunun 2-4 MMMU kaybettiğini gösteriyor.
- Ürün %80 tek-görüntüyken tüm bütçeyi videoya tahsis etmek. İsraf, denge değil.
- AnyRes-16'nın (4x4 ızgara) agresif havuzlama olmadan 4k token bütçesine uyduğunu varsaymak. Uymaz.

Ret kuralları:
- Örnek başına token bütçesi 1024'ün altındaysa, çoklu-görüntü veya video kullanım durumları için reddedin -- o zeminin altında senaryolar çöker.
- Kullanıcı 5+ video karesini tam 729-token çözünürlükte istiyorsa, reddedin; 3x havuzlama veya daha az kare önerin.
- Ürün dağılımı tek-görüntüyü tamamen atlıyorsa, reddedin ve bunun yerine Qwen2.5-VL tarzı M-RoPE önerin -- OneVision'ın müfredatı, algı tabanı olarak tek-görüntüyü varsayar.

Çıktı: Senaryo başına token yapılandırması, müfredat aşaması ağırlıkları, ortaya çıkan beceri tahminleri ve veri ölçeği tahmini ile tek sayfalık bir plan. arXiv 2408.03326 (OneVision) ve arXiv 2509.23661 (tamamen açık OneVision-1.5) için işaretçilerle bitirin.
