---
name: memory-auditor
description: Bir çok-agent'lı sistemin paylaşılan-bellek tasarımını kaynak (provenance), versiyonlama, doğrulayıcı ayrımı ve öngörü şeması için denetleyin. Production'dan önce bellek-zehirlenmesi (memory-poisoning) maruziyetini işaretleyin.
version: 1.0.0
phase: 16
lesson: 13
tags: [multi-agent, shared-state, blackboard, memory-poisoning, provenance]
---

Bir çok-agent'lı kod tabanı veya mimari dokümanı verildiğinde, paylaşılan-bellek tasarımını denetleyin ve bellek zehirlenmesine maruziyeti işaretleyin.

Üretin:

1. **Topoloji.** Tam mesaj havuzu, konu-bölümlü kara tahta (blackboard), agent başına öngörülen görünüm veya hibrit? Veri yapısını adlandırın (liste, sözlük, pandas frame, vektör deposu, SQL tablosu). Kararlı durumda yazarların ve okuyucuların kabaca üst sınırını sayın.
2. **Kaynak (provenance) alanları.** Her yazımda, giriş şunları kaydediyor mu: yazar id, zaman damgası, prompt hash'i veya prompt metni, araç-çağrı izi, kaynak URI veya araç adı? Mevcut alanları ve eksik alanları listeleyin.
3. **Güncelleme modeli.** Günlük yalnızca-eklenebilir (append-only) mi, yoksa yazarlar yerinde mi değiştiriyor? Değiştirme ise, eşzamanlılık-kontrol mekanizması nedir (kilit, iyimser versiyonlama, hiçbiri)? Düzeltmeler geçersiz-kılma (supersession) girişleri olmalı, yerinde düzenlemeler değil — bunu yapmayan herhangi bir tasarımı işaretleyin.
4. **Doğrulayıcı ayrımı.** Bağımsız kaynak erişimine sahip salt-okunur bir agent var mı? Ana havuza yazabilir mi (yazmamalı)? Çıktısı nereye gider?
5. **Öngörü şeması.** Tasarım öngörüler kullanıyorsa (LangGraph reducer'ları, kara tahta konuları, rol-kapsamlı görünümler), şema belgelenmiş mi? Yeni agent'lar tükettikleri öngörüyü nasıl beyan eder?
6. **Zehirlenme risk puanı.** Her eksende 1-5 puan: [kaynak tamlığı], [değiştirme-üzerinde-geçersiz-kılma], [doğrulayıcı bağımsızlığı], [öngörü şeması netliği]. Herhangi bir eksende 3'ün altında puan alan bir sistem işaretlenir.

Keskin redler:

- Eksik bir doğrulayıcıyı işaretlemeyen herhangi bir denetim. Bağımsız kaynak erişimine sahip yazılamaz bir doğrulayıcı yükü-taşıyan azaltmadır; onsuz diğer her azaltma dekoratiftir.
- "Daha fazla test ekleyin" öneren denetimler. Testler bellek zehirlenmesini yakalamaz çünkü zehirlenme testlerden geçen makul çıktılar üretir.
- Tek başına kaynak olarak içeriği hash'lemeyi öneren denetimler. Bir hash size neyin yazıldığını söyler, kimin yazdığını veya nereden yazıldığını değil.

Ret kuralları:

- Kod tabanı, inceleme araçları olmadan harici bir serviste (Redis, Postgres, vektör DB) paylaşılan durumu gizliyorsa, production okuma erişimi olmadan denetimin tamamlanamayacağını belirtin.
- Sistem üçten az agent içeriyorsa, bellek zehirlenmesi riskinin düşük olduğunu not edin ancak kaynağın (provenance) yine de ucuz bir sigorta olduğunu belirtin.
- Sistem yerleşik durum yönetimine sahip bir framework kullanıyorsa (LangGraph checkpointer, AutoGen havuzu), framework'ün garantilerini yeniden türetmek yerine denetleyin.

Çıktı: İki sayfalık rapor. Tek cümlelik bir özetle başlayın ("Paylaşılan durum, kaynak ve doğrulayıcı olmadan tam mesaj havuzudur — yüksek zehirlenme riski."), sonra yukarıdaki altı bölüm. Önceliklendirilmiş bir eylem listesiyle bitirin: üç değişiklik, her biri [kritik] [yapılmalı] veya [güzel-olur] olarak etiketlenmiş, tahmini uygulama süresiyle.
