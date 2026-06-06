---
name: transformer-review
description: Sıfırdan transformer uygulamasını 13 Faz 7 dersine karşı incele
version: 1.0.0
phase: 7
lesson: 14
tags: [transformers, inceleme, capstone]
---

Sıfırdan transformer kod tabanı (PyTorch / JAX) verildiğinde, 2026 varsayılanlarına göre incele ve eksik veya hatalı parçaları işaretle:

1. Dikkat. Nedensel maske mevcut. `sqrt(d_head)` ile ölçekle. Çoklu kafa bölünmesi çalışıyor. Varsa Flash Attention kullanılıyor. d_model ≥ 1024 ise GQA'dan bahsedilmiş.
2. Konumsal kodlama. RoPE (2026'da tercih edilen) veya öğrenilmiş mutlak (küçük modeller için kabul edilebilir). Sinüzoidali tarihsel olarak işaretle.
3. Blok bağlantısı. Ön-norm (son-norm değil). RMSNorm (LayerNorm değil). SwiGLU FFN (ReLU/GELU değil). Her alt katmanın etrafında artık bağlantılar. Doğrusal katmanlarda yanlılıklar kaldırılmış (modern varsayılan).
4. Eğitim. AdamW (veya 2026+ için Muon), doğrusal ısınma ile kosinüs LR zamanlaması, 1.0'da gradyan kırpma, bf16 autocast. Token gömme ile lm_head arasında ağırlık bağlama.
5. Kayıp. Her konumda bir-kaydırmalı çapraz entropi. Varsa dolguyu maskele. Sabit aralıkla eğitim ve doğrulama kaybını günlüğe kaydet.

Aşağıdakilerden herhangi birine sahip kod tabanını onaylama: açık neden olmadan son-norm, gerekçe olmadan 2026 üretim kodunda LayerNorm, kodçözücü öz-dikkatinde eksik nedensel maske, küçük bir LM'de bağlanmamış gömmeler. İşaretle: doğrulama bölütü yok, gradyan kırpma yok, ısınma olmadan LR > 1e-3 veya geri dönüş olmadan konumsal gömme aralığını aşan block_size. `python code/main.py` dosyasını uçtan uca çalıştırmayı ve nano yapılandırmada tinyshakespeare üzerinde son doğrulama kaybının 2.5'in altına indiğini kontrol etmeyi öner.
