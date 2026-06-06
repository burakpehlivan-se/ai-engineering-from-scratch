---
name: structured-output-picker
description: Yapılandırılmış çıktı yaklaşımı, şema tasarımı ve doğrulama planı seçer.
version: 1.0.0
phase: 5
lesson: 20
tags: [nlp, llm, structured-output]
---

Bir kullanım senaryosu (sağlayıcı, gecikme bütçesi, şema karmaşıklığı, başarısızlık toleransı) verildiğinde şunu üretirsiniz:

1. Mekanizma. Yerel satıcı yapılandırılmış çıktısı, Instructor yeniden denemeleri, Outlines FSM veya XGrammar CFG. Tek cümlelik neden.
2. Şema tasarımı. Alan sırası (önce akıl yürütme, sonra yanıt), "bilinmiyor" için null yapılabilir alanlar, enum veya regex, zorunlu alanlar.
3. Başarısızlık stratejisi. Maks yeniden deneme, yedek model, zarif `null` işleme, dağılım-dışı reddetme.
4. Doğrulama planı. Şema uyum oranı (hedef %100), anlamsal geçerlilik (LLM-hakem), alan kapsama oranı, gecikme p50/p99.

`answer` veya `decision` alanını akıl yürütme alanlarından önce koyan her tasarımı reddedin. Şema olmadan çıplak JSON modunu kullanmayı reddedin. Özyinelemeli şemaları FSM-only kütüphanesinin arkasına almayı işaretleyin.
