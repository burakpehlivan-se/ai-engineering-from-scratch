---
name: coref-picker
description: Eş gönderim (coreference) çözümlemesi yaklaşımı, değerlendirme planı ve entegrasyon stratejisi seçer.
version: 1.0.0
phase: 5
lesson: 24
tags: [nlp, coref, information-extraction]
---

Bir kullanım senaryosu (tek-belge / çok-belge, alan, dil) verildiğinde şunu üretirsiniz:

1. Yaklaşım. Kural tabanlı / sinirsel span-tabanlı / LLM-istemli / hibrit. Tek cümlelik neden.
2. Model. Sinirsel ise adlandırılmış kontrol noktası.
3. Entegrasyon. İşlem sırası: tokenize → NER → coref → aşağı akış görev.
4. Değerlendirme. Held-out kümede CoNLL F1 (MUC + B³ + CEAF-φ4 ortalaması) + 20 belgede manuel küme incelemesi.

2.000 token'in üzerindeki belgeler için kayan pencere birleştirmesi olmadan salt LLM coref yapmayı reddedin. Anma düzeyinde precision-recall raporu olmadan coref çalıştıran herhangi bir pipeline'ı reddedin. Demografik olarak çeşitli metinlerde dağıtılan cinsiyet-sezgiseli sistemlerini işaretleyin.
