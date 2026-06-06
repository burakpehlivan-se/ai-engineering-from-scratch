---
name: ner-picker
description: Belirli bir çıkarma görevi için doğru NER (Adlandırılmış Varlık Tanıma) yaklaşımını seçer.
version: 1.0.0
phase: 5
lesson: 06
tags: [nlp, ner, extraction]
---

Bir görev açıklaması (alan, etiket kümesi, dil, gecikme, veri hacmi) verildiğinde şunu üretirsiniz:

1. Yaklaşım. Kural tabanlı + gazeteer, CRF, BiLSTM-CRF veya transformer ince ayar.
2. Başlangıç modeli. Adını belirtin (spaCy model kimliği: `en_core_web_sm` / `en_core_web_trf`, Hugging Face kontrol noktası kimliği: `dslim/bert-base-NER` veya "sıfırdan eğitilmiş özel model").
3. Etiketleme stratejisi. BIO, BILOU veya span-tabanlı. Tek cümlede gerekçelendirin.
4. Değerlendirme. `seqeval` kullanın. Her zaman varlık düzeyinde F1 raporlayın, asla token düzeyinde değil.

Kullanıcının zaten alana özgü önceden eğitilmiş bir modeli (örn. tıp için BioBERT) yoksa 500'ün altında etiketli örnek için transformer ince ayarı önermeyi reddedin. İç içe geçmiş varlıkları span-tabanlı veya çok geçişli modeller gerektiriyor olarak işaretleyin. Kullanıcı "üretim ölçeği"nden bahsederken ve hazır CoNLL-2003 etiketlerini kullanıyorsa bir gazeteer denetimi zorunlu kılın.
