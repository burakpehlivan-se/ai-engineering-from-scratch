---
name: mha-configurator
description: Yeni bir transformer için kafa sayısı, KV-kafa sayısı ve izdüşüm stratejisi (MHA / MQA / GQA / MLA) öner
version: 1.0.0
phase: 7
lesson: 3
tags: [transformers, dikkat, mha, gqa]
---

Bir transformer spesifikasyonu (parametre bütçesi, gizli boyut `d_model`, hedef bağlam uzunluğu, çıkarım cihazı belleği, eğitim ve çıkarım önceliği) verildiğinde, aşağıdakileri üret:

1. İzdüşüm varyantı. Şunlardan biri: MHA, GQA, MQA, MLA. KV önbelleği kısıtlamalarına bağlı tek cümlelik gerekçe.
2. Kafa geometrisi. `n_heads`, `n_kv_heads`, `d_head`. Değerler `d_model = n_heads * d_head` ve `n_heads % n_kv_heads == 0` koşullarını sağlamalıdır.
3. KV önbellek tahmini. Hedef bağlam uzunluğunda seçilen varyant için katman başına token başına bayt (fp16). Tek bir partinin hedef cihaz belleğini aşıp aşmadığını işaretle.
4. Başlatma. Q, K, V, O matrisleri için Xavier / Kaiming ölçeği. Yanlılık (bias) terimlerinin dahil edilip edilmediğini belirt (çoğu 2026 modeli bunları kaldırır).
5. Test edilebilirlik kancası. Eğitilmiş iki katmanlı bu yapılandırmanın ≥%95 çözmesi gereken tek bir sentetik görev (örneğin indüksiyon-kafa kalıbı `A B A ? → B`).

`d_head < 32` önerme — dikkat dinamikleri bozulur. 32K üzeri bağlam uzunlukları için `n_heads > 16` ile MHA önerme; KV önbelleğini açıkça fiyatlandır ve bunun yerine GQA veya MLA öner. Açıkça kıyaslama yapılmadıkça 1B parametrenin altındaki modeller için MLA önerme.
