---
name: llm-pipeline-reviewer
description: Çok milyon dolarlık bir çalıştırmadan önce uçtan uca bir LLM eğitim pipeline'ı manifestosunu gözden geçirin.
version: 1.0.0
phase: 10
lesson: 13
tags: [pipeline, training, manifest, eval-gate, cost, rollback]
---

Önerilen bir eğitim pipeline'ı manifestosu (tokenizer, veri, ön-eğitim, SFT, hizalama, değerlendirme, nicemleme ve sunma aşamalarını tanımlayan YAML veya JSON) verildiğinde, şunları kapsayan bir inceleme üretin:

1. Aşama grafiği. Her aşamanın tiplendirilmiş girdi ve çıktılara sahip olduğunu doğrulayın. Eksik bağımlılıkları, örtük durumu veya adlandırılmış bir artifact hash (yapı hash'i) yerine çıplak bir dizin tüketen herhangi bir aşamayı işaretleyin.
2. Hash zinciri. Aşama N'nin output_hash değerinin, her downstream (aşağı akış) aşamasının input_hash değerlerinden birine eşit olduğunu doğrulayın. Herhangi bir uyumsuzluk, manifestonun tutarsız olduğu ve pipeline'ın başlamaması gerektiği anlamına gelir.
3. Değerlendirme kapısı. Kapı listesindeki her metrik sayısal olmalı, bir operatörü, eşiği ve ölçüm kaynağı olmalıdır. Öznel ("iyi görünüyor"), sınırsız (eşik yok) veya eğitim verisi üzerinde ölçülen herhangi bir kapıyı reddedin.
4. Regresyon koruması. Yeni modelin temel kıyaslamaları (MMLU, MATH, HumanEval+, GPQA veya alana özgü eşdeğeri) temel (baseline) sayılar içermelidir. Temeli olmayan bir çalıştırma, regresyon tespiti olmayan bir çalıştırmadır.
5. KL bütçesi. Hizalama aşamaları (RLHF, DPO, CAI, GRPO) referansa karşı kümülatif bir KL üst sınırı belirlemelidir. Sınırsız KL, sınırsız sapmadır.
6. Kontaminasyon kontrolü. Eğitim veri parçaları ve değerlendirme setleri, belgelenmiş bir örtüşme kontrolüne (tam eşleşme veya 13-gram) sahip olmalıdır. Gerekli geçme eşiği: <%0.1.
7. Maliyet tahmini. Her aşama için çalıştırma öncesi tahmin artı bir toplam, bütçe kapısıyla karşılaştırıldı. Tahmin > bütçe ise, pipeline başlamayı reddeder.
8. Geri alma (rollback) planı. Her aşama için, başarısızlık durumunda adlandırılmış eylemler: yeniden çalıştırma, önceki artefakta geri dönme, girdileri gözden geçirme ve downstream'i yeniden çalıştırma. Pahalı aşamalar (ön-eğitim) sıcak bir kontrol noktası stratejisine sahip olmalıdır.
9. Artefakt deposu. Kontrol noktaları, veri setleri, tokenizer'lar, değerlendirme raporları içerik adresli (SHA-256) olmalıdır. Dosya adı adresli artefaktlar ("latest.pt") sert bir reddir.
10. Gözlemlenebilirlik. Her aşama, bir izleme kimliği (trace ID), aşama adı, girdi hash'leri, çıktı hash'i, duvar saati ve maliyet ile yapılandırılmış günlükler yayınlamalıdır. Eksik izleme kimlikleri, çalıştırmanın sonradan hata ayıklanamayacağı anlamına gelir.

İncelemeyi durduran kırmızı bayraklar:
- ölçüm kaynağı eksik olan bir kapı (hiçbir aşamanın hesaplamadığı bir metrik üzerinde kapı)
- bir kontrol noktasını downstream aşamayla paylaşan bir aşama (endişelerin ayrımı yok)
- referans modeli olmayan bir hizalama aşaması (KL için çapa yok)
- hakemin politika ile aynı model ailesi olduğu bir LLM-as-judge değerlendirmesi (kontaminasyon)
- bütçeyi %20'den fazla aşan bir maliyet tahmini
- yalnızca "sıfırdan yeniden çalıştır"dan oluşan bir geri alma planı

Çıktı: Her kapı için PASS/HOLD, her kararı üreten tam manifesto alanı veya eksik alan ve bir HOLD'ı PASS'e çevirmek için gereken minimum değişiklik ile birlikte iki sayfalık bir inceleme.
