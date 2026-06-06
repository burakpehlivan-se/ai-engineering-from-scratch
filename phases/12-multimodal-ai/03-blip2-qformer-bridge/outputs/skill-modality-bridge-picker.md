---
name: modality-bridge-picker
description: Token bütçesi, kalite hedefi ve eğitim hesaplaması verildiğinde bir VLM yapılandırması için Q-Former, MLP projektör veya Perceiver resampler arasında öneride bulunun.
version: 1.0.0
phase: 12
lesson: 03
tags: [blip2, qformer, vlm, modality-bridge, architecture]
---

Bir görüntü kodlayıcının görüntü başına token sayısı, LLM'in bağlam bütçesi, prompt başına hedef görüntü sayısı ve eğitim hesaplama bütçesi verildiğinde, hangi modalite köprüsünün kullanılacağını önerin ve parametre sayıları ve token ekonomisi ile gerekçelendirin.

Üretin:

1. Token bütçe denetimi. Görüntü kodlayıcısından görüntü başına ham token'ları, her köprü seçeneğinden sonra görüntü başına token'ları ve beyan edilen görüntü-başına-prompt sayılarında tüketilen LLM bağlamının kesrini bildirin.
2. Köprü karşılaştırması. Q-Former (32 token, ~188M parametre), MLP projektör (tüm yamalar, ~20M parametre) ve Perceiver resampler (N-katmanlı çapraz dikkat yoluyla K öğrenilebilir sorgu, değişken) için parametreler, kalite vekilleri ve eğitim maliyeti tahmini verin.
3. Öneri. Belirtilen kısıtlamalar için tek en iyi seçim, tek satırlık gerekçeyle. Kısıtlamalar çeliştiğinde işaretleyin (yüksek kalite + sıkı token bütçesi + düşük eğitim hesaplaması).
4. İki aşamalı eğitim izi. Q-Former seçilirse, aşama 1 için ITC + ITM + ITG kayıplarını ve aşama 2 için LM kaybını ana hatlarıyla belirtin. Her biri için temsili bir veri kümesi adlandırın (COCO, LAION, Visual Genome).
5. Ablasyon kontrol listesi. Köprüyü kilitlemeden önce arayanın çalıştırması gereken beş deney (sorgu sayısı, iki aşamalı ve tek aşamalı, projektör derinliği, dondurma programı, ince ayar alt kümesi).

Sert reddetmeler:
- Token bütçesini yok sayan herhangi bir öneri. Görüntü başına 576 token ile "MLP kullan" 4k bağlamda 10 görüntüde başarısız olur.
- Q-Former'ın MLP'ye kesinlikle hakim olduğunu iddia etmek. Sınırsız bağlamla tek-görüntü yüksek kaliteli görevlerde, MLP kazanır.
- Perceiver resampler'ı Q-Former'a eşdeğer olarak ele almak. Flamingo onu her LLM katmanında uygular; BLIP-2 bir kez uygular.

Ret kuralları:
- Arayan, kaç kare ve hangi kare hızında olduğunu belirtmeden video işleyebilen bir köprü istiyorsa, reddedin -- video köprüleri tek-görüntü köprülerinden spesifikasyona göre farklılık gösterir, sadece ölçek olarak değil.
- Kapsamdaki LLM, görüntü kulesi ile sıfırdan eğitilmişse (erken füzyon, Chameleon tarzı), reddedin -- Ders 12.11 bu vakayı ayrıca kapsar.
- Eğitim hesaplaması belirtilmemişse, reddedin ve arayanın BLIP-2'nin 2. aşamasını karşılayıp karşılayamayacağını (birkaç yüz A100-saati) veya yalnızca projektör-only eğitimi mi karşılayacağını sorun.

Çıktı: Token matematiği, parametre sayıları, önerilen mimari, eğitim ana hattı ve ablasyon kontrol listesi ile tek sayfalık bir köprü önerisi. Çapraz dikkat-her-yerde için Ders 12.04'e (Flamingo), yalnızca MLP için Ders 12.05'e (LLaVA) veya veri-vs-mimari ödünleşimi için Ders 12.07'ye (ablasyonlar) işaret eden bir "sırada ne okunmalı" paragrafı ile bitirin.
