---
name: seq2seq-design
description: Belirli bir görev için diziden diziye (sequence-to-sequence) bir pipeline tasarlar.
phase: 5
lesson: 09
---

Bir görev (çeviri, özetleme, yeniden ifade etme, soru yeniden yazımı) verildiğinde şunu üretirsiniz:

1. Mimari. Önceden eğitilmiş transformer kodlayıcı-çözümleyici (BART, T5, mBART, NLLB) varsayılandır. RNN tabanlı seq2seq yalnızca belirli kısıtlar (streaming, uç çıkarım, pedagoji) içindir.
2. Başlangıç kontrol noktası. Adını belirtin (`facebook/bart-base`, `google/flan-t5-base`, `facebook/nllb-200-distilled-600M`). Kontrol noktasını görev ve dil kapsamıyla eşleştirin.
3. Kod çözme stratejisi. Deterministik çıktı için açgözlü (greedy), kalite için ışın arama (beam search, genişlik 4-5), çeşitlilik için sıcaklıkla örnekleme. Tek cümlelik gerekçe.
4. Yayına almadan önce doğrulanacak bir başarısızlık modu. Pozlama yanlılığı (exposure bias) daha uzun çıktılarda üretim kayması (generation drift) olarak ortaya çıkar; 90. yüzdelik uzunlukta 20 çıktıyı örnekleyip gözle inceleyin.

~1M paralel örneğin altında sıfırdan bir seq2seq eğitmeyi önermeyi reddedin. Kullanıcıya dönük içerik için açgözlü kod çözme kullanan her pipeline'ı kırılgan olarak işaretleyin (açgözlü tekrar eder ve döngüye girer).
