---
name: rollback-rehearsal
description: Önerilen otonom iş akışı için bir rollback-prova testi tasarlayın ve checkpoint backend'ini denetim-izi kalıcılığı için denetleyin.
version: 1.0.0
phase: 15
lesson: 16
tags: [checkpointing, rollback, idempotency, eu-ai-act-article-14, durable-execution]
---

Önerilen uzun-horizon otonom bir iş akışı verildiğinde, idempotency + önkoşul + doğrulama + rollback stack'inin uçtan uca gerçekten çalıştığını kanıtlayan bir rollback-prova testi tasarlayın ve checkpoint backend'ini düzenleyici-hazırlığı için denetleyin.

Üretin:

1. **Prova senaryosu.** (a) iş akışını başlatan, (b) taahhüt ortasında çökerten, (c) devam ettiren, (d) eylemin tam olarak bir kez tetiklendiğini doğrulayan, (e) bir doğrulama başarısızlığı enjekte eden, (f) rollback'in tetiklendiğini ve durumun geri yüklendiğini doğrulayan somut test. Hiçbir production iş akışı, bu test en az bir kez geçmeden çalışmamalıdır.
2. **Idempotency denetimi.** Idempotency key'in öneri içeriğinden türetildiğini (Ders 15) ve taahhüt mantığının açık yürütme durumları (`pending` -> `executing` -> `committed`/`failed`) kullandığını doğrulayın. Yan etkiden önce idempotency key ile rezerve/kilitleyin ve ancak yan etki doğrulandıktan sonra `committed` olarak işaretleyin.
3. **Önkoşul envanteri.** İş akışının taahhüt anında yeniden kontrol etmesi gereken her önkoşulu listeleyin. Kontrol-zamanı vs kullanım-zamanı boşlukları en yaygın production hatasıdır; önkoşul öneri anında değil taahhüt anında değerlendirilmelidir.
4. **Doğrulama envanteri.** Her sonuç doğurucu eylem için, yan etkinin gerçekleştiğini doğrulayan spesifik okumayı adlandırın. "200 döndü" kabul edilemez.
5. **Rollback envanteri.** Her sonuç doğurucu eylem için, rollback'i bant-içi, telafi edici işlem veya bant-dışı uyarı olarak sınıflandırın. No-op rollback'ler ("bunu geri alamayız") öneride açıkça adlandırılmalıdır (Ders 15 meta verileri).

Keskin redler:

- Provası yapılmamış rollback'i olan iş akışları.
- Deploy'da veri kaybeden checkpoint backend'leri.
- Durumun yürütmeden sonra değil önce yazıldığı taahhüt yolları.
- Yalnızca araç çağrısının dönüş kodunu kontrol eden "doğrulanmış" durumlar.
- Yalnızca öneri anında, taahhüt anında değil çalışan önkoşul kontrolleri.

Ret kuralları:

- Kullanıcı prova senaryosunu staging'de en az bir kez çalıştırmadıysa, production rollout'unu reddedin.
- Kullanıcı checkpoint store şemasını üretemiyorsa, reddedin ve önce şema dokümantasyonunu isteyin. Düzenleyiciler sorgulanabilir durum ister.
- İş akışı bellek içi bir checkpoint'e bağlıysa (kalıcılık yok), reddedin.

Çıktı formatı:

Şunları içeren bir prova planı döndürün:

- **Test senaryosu taslağı** (doğrulamalarla adımlar)
- **Idempotency tablosu** (anahtar bileşimi, durum-yazma sırası)
- **Önkoşul tablosu** (kontrol, ne zaman değerlendirildi, sonuç)
- **Doğrulama tablosu** (eylem, doğrulayan okuma)
- **Rollback tablosu** (eylem, tür, hedef durum)
- **Backend tasdiki** (store, deploy-hayatta-tutuyor mu e/h, sorgulamaya-hazır mı e/h)
- **Hazırlık** (production / staging / yalnızca-araştırma)
