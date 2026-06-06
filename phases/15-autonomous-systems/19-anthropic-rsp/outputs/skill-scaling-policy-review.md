---
name: scaling-policy-review
description: Bir frontier-lab ölçeklendirme politikasını (Anthropic RSP, OpenAI Preparedness, DeepMind FSF, dahili) RSP v3.0 referans şekline karşı inceleyin.
version: 1.0.0
phase: 15
lesson: 19
tags: [rsp, scaling-policy, ai-rd-4, pause-commitment, saferai, governance]
---

Yayınlanmış veya önerilen bir ölçeklendirme politikası verildiğinde, RSP v3.0 referans şekline (AI R&D-4, olumlu durum, iki-kademeli azaltma, Frontier Safety Roadmap, Risk Report, bağımsız inceleme) karşı yapılandırılmış bir inceleme üretin.

Üretin:

1. **İki-kademe envanteri.** Taahhütleri "laboratuvar-tek-taraflı" ve "sektör-geneli öneri" olarak ayırın. Öneri kademesindeki taahhütler savunuculuktur, söz değil. Oranı sayın; çoğu taahhüdün öneri kademesinde yaşadığı bir politika zayıf bir politikadır.
2. **Eşikler.** Her yetenek eşiğini ve tetiklediği azaltmayı adlandırın. v2'de nicel olduğu yerde nitel olan eşikleri işaretleyin. Politikanın kapsıyor gibi göründüğü yetenekler için eksik eşikleri işaretleyin.
3. **Duraklama taahhüdü.** Politikanın belirli eşiklerde bir duraklama maddesini (eğitimi durdurma, deployment'ı durdurma veya benzeri) adlandırdığını doğrulayın. v3.0 bunu kaldırdı; peşinden giden politikalar gerilemeyi miras alır.
4. **Duran artefaktlar.** Politikanın, beyan edilmiş kadansla duran Frontier Safety Roadmap ve Risk Report belgelerini zorunlu kıldığını doğrulayın. Sonradan yayınlanan tek-seferlik artefaktlar uygun değildir.
5. **Bağımsız inceleme.** Harici inceleme mekanizmasını adlandırın. Yalnızca dahili inceleme (laboratuvar çalışanlarından oluşan bir "Güvenlik Danışma Grubu") bağımsız denetim olarak uygun değildir.

Keskin redler:

- Adlandırılmış yetenek eşiği olmayan politikalar.
- Azaltmalarının tümü sektör-öneri kademesinde yaşayan politikalar.
- Duran Roadmap / Risk Report artefaktı olmayan politikalar.
- Bağımsız inceleme mekanizması olmayan politikalar.
- Politika metninin nasıl güncellendiğini ve hangi kadansla güncellendiğini belirtmeden "gerçek-dünya deneyimlerinden öğrenmeyi" iddia eden politikalar.

Ret kuralları:

- Politika belgesi yönetişim yerine pazarlama ise (spesifik taahhüt yok, eşik yok, kadans yok), bir ölçeklendirme politikası olarak puanlamayı reddedin.
- Kullanıcı bir politikanın varlığını uyumlulukla eşdeğer olarak ele alıyorsa, reddedin. Politika bir taahhüt cihazıdır; uyumluluk kanıt gerektirir.
- Kullanıcı mevcut olarak eski bir politika versiyonunu (örn. 2023 Anthropic RSP) gösteriyorsa, reddedin ve mevcut versiyonu isteyin.

Çıktı formatı:

Şunları içeren bir politika incelemesi döndürün:

- **İki-kademe oranı** (tek-taraflı / öneri / toplam sayı)
- **Eşik tablosu** (ad, tür: nicel / nitel, tetik, azaltma)
- **Duraklama taahhüdü** (mevcut e/h, spesifik madde)
- **Duran artefaktlar** (Roadmap kadansı, Risk Report kadansı)
- **Bağımsız inceleme** (mekanizma, incelemci kimliği, sıklık)
- **Özet puan** (güçlü / orta / zayıf, gerekçeli)
