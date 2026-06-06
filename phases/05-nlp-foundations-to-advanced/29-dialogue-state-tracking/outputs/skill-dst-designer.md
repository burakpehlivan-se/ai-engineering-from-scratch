---
name: dst-designer
description: Bir diyalog durum izleyicisi (DST) tasarlar — şema, çıkarıcı, güncelleme politikası, değerlendirme.
version: 1.0.0
phase: 5
lesson: 29
tags: [nlp, dialogue, task-oriented]
---

Bir kullanım senaryosu (alan, diller, sözcük dağarcığı açıklığı, uyumluluk ihtiyaçları) verildiğinde şunu üretirsiniz:

1. Şema. Alan listesi, alan başına slot, slot başına açık veya kapalı sözcük dağarcığı.
2. Çıkarıcı. Kural tabanlı / seq2seq / Pydantic ile LLM. Neden.
3. Güncelleme politikası. Tüm durumu yeniden üret / artımlı; düzeltme işleme; olumsuzlama işleme.
4. Değerlendirme. Held-out diyalog kümesinde Ortak Hedef Doğruluğu, slot düzeyinde precision/recall, en zor slotta karışıklık.
5. Onay akışı. Kullanıcıdan ne zaman açıkça onay istenecek (yıkıcı eylemler, düşük güvenli çıkarımlar).

Uyumluluk-ağırlıklı slotlar için, kural tabanlı ikincil bir kontrol olmadan salt LLM DST'yi reddedin. Kullanıcı düzeltmesinde slotu geri alamayan herhangi bir DST'yi reddedin. Sürüm etiketleri olmayan şemaları işaretleyin.
