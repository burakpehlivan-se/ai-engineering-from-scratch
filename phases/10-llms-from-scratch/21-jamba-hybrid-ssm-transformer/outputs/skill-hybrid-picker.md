---
name: hybrid-picker
description: Belirli bir iş yükü için saf Transformer, Jamba tarzı hibrit ve saf SSM arasında seçim yapın.
version: 1.0.0
phase: 10
lesson: 21
tags: [jamba, mamba, ssm, hybrid, long-context, memory-budget, architecture]
---

Bir iş yükü belirtimi (bağlam uzunluğu profili p50/p99, görev karışımı, GPU başına bellek bütçesi, hedef verim, kalite-vs-hız önceliği) verildiğinde, saf Transformer (+MoE +MLA), Jamba tarzı hibrit ve saf Mamba modeli arasında öneride bulunun.

Şunu üretin:

1. Bağlam uzunluğu kovası. Kısa (16k'nin altı), orta (16k-64k), uzun (64k-256k) veya ultra-uzun (256k-plus). İlk geçiş kararını yönlendirir.
2. Mimari önerisi. Saf Transformer, 1:7 hibrit, 1:3 hibrit, 1:15 hibrit veya saf Mamba arasından birini seçin. Bağlam kovası ve görevin bağlam-içi-getirme (in-context-recall) taleplerini kullanarak gerekçelendirin.
3. Bellek bütçesi kontrolü. Hedef bağlamda KV cache + SSM durumunu hesaplayın. Ağırlıklar ve aktivasyon belleği (tipik olarak ağırlıklar ve KV cache'in üzerinde 10-20 GB) hesaba katıldıktan sonra hedef hızlandırıcıya sığdığını doğrulayın.
4. Kalite ödünleşim açıklaması. Seçilen seyreklik düzeyinin kalite maliyetini belgelendirin. 1:7 oranının altındaki hibritler, bağlam-içi getirmede ölçülebilir miktarlarda bozulur; saf Mamba bazı durum takibi (state-tracking) görevlerinde başarısız olur.
5. Çıkarım yığını uyumluluğu. Seçilen mimarinin hedef yığın (vLLM, TensorRT-LLM, SGLang, llama.cpp) tarafından desteklendiğini doğrulayın. Hibritlerin araç desteği, saf Transformer'lardan daha dardır.

Sert redler:
- 16k'nin altındaki bağlam için Jamba tarzı hibrit. Mimari ek yük gerekçelendirilmez.
- Akıl yürütme ağırlıklı veya çoklu belge çapraz referans görevleri için saf Mamba. Durum takibi sınırları ısırır.
- 1:15'in altındaki hibrit oranları. Bunun altında, bağlam-içi getirme güvenilmezdir.
- Hesaplanan bellek bütçesinin belirtilen hızlandırıcıya sığmayan herhangi bir önerisi.

Reddetme kuralları:
- İş yükü gerçekten karışık kısa ve uzun bağlamlıysa, hibrit önerisini reddedin ve saf Transformer'ı (mümkünse MLA ile) önerin — hibritler özellikle uzun bağlam iş yüklerinde parlıyor.
- Hızlandırıcı tüketici sınıfıysa (24GB veya daha az), hibrit boyutlu modelleri reddedin ve damıtılmış küçük bir hibrit veya nicemlenmiş saf Transformer önerin.
- İş yükü gecikmeye duyarlı parti-1 üretimiyse ve model yeni ise (mevcut bir dağıtım yolu yok), reddedin ve daha basit yol olarak spekülatif kod çözme (Faz 10 · 15) ile iyi desteklenen saf Transformer önerin.

Çıktı: Bağlam kovasını, mimari seçimini, hedef bağlamda KV cache'i, kalite ödünleşim açıklamasını ve çıkarım yığını uyumluluğunu listeleyen tek sayfalık bir öneri. İlk 10k üretim isteğinde öneriyi doğrulayacak belirli uzun bağlam değerlendirmesini (RULER, LongBench, needle-in-haystack) adlandıran bir "ne izlenmeli" paragrafıyla bitirin.
