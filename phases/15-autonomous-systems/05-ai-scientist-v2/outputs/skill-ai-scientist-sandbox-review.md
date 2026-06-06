---
name: ai-scientist-sandbox-review
description: Sandbox'tan herhangi bir şey çıkmadan önce araştırma-döngüsü agent çıktıları için iki aşamalı inceleme kontrol listesi.
version: 1.0.0
phase: 15
lesson: 5
tags: [ai-scientist, research-agent, sandbox, peer-review, disclosure]
---

Bir AI-Scientist-v2 tarzı döngü tarafından üretilen otonom bir araştırma çıktısı (hipotez, kod, deneyler, şekiller, makale taslağı) verildiğinde, iki aşamalı bir inceleme üretin: sandbox denetimi (bir şey çıkıyor mu?) artı araştırma denetimi (çalışma sağlam mı?).

İki aşama doğrudan aşağıdaki denetimlere eşlenir: **Sandbox aşaması = madde 1**; **Araştırma aşaması = maddeler 2 (Deney denetimi) + 3 (Cilalama denetimi)**. Maddeler 4–5, her iki aşama geçtikten sonra ne olacağını yönetir.

Üretin:

1. **Sandbox aşaması.** Herhangi bir artefakt sandbox'tan çıkmadan önce:
   - Döngünün yaptığı her ağ çağrısını ve hedefini listeleyin. Önceden onaylanmamış olanları işaretleyin.
   - Döngünün çalışma dizininin dışına yazdığı her dosyayı envanterleyin.
   - Docker / seccomp / gVisor (sandbox container çekirdek izolasyonu) kapsamının tüm çalıştırma boyunca tutulduğunu doğrulayın.
   - Hiçbir alt sürecin (subprocess) sandbox denetiminden kaçmadığını doğrulayın.
   Herhangi bir kontrol başarısız olursa, dışa aktarmayı engelleyin; bir insana iletin.
2. **Deney denetimi.** Makaleyi değil, deney kodunu okuyun:
   - İddia edilen her deneyin gerçekten çalıştığını ve raporlanan sayıların tekrarlanabilir olduğunu doğrulayın.
   - Başarısız deneylerin başarısızlık olarak raporlandığını, sonradan negatif sonuçlar olarak yeniden çerçevelenmediğini kontrol edin.
   - Fikir üzerindeki "novelty" (yenilik) etiketinin, bir insan domain uzmanı tarafından yapılan literatür taramasına karşı dayandığını kontrol edin.
3. **Cilalama denetimi.** Şekilleri okuyun:
   - Her şeklin verisinin loglanmış bir deney çalıştırmasından geldiğinden emin olun, cilalama aşamasında yeniden yazılmadığından emin olun.
   - Eksenlerin, ölçeklerin ve açıklamaların altta yatan veriyle eşleştiğini doğrulayın.
   - Altyazısı, verinin desteklediğinden fazlasını iddia eden her şekli işaretleyin.
4. **Açıklama planı.** Artefakt harici dağıtım için tasarlandıysa:
   - Artefaktın agent tarafından yazıldığını açıklayın.
   - Kullanılan araçları açıklayın (model ailesi, döngü versiyonu).
   - Kontrol eden insan incelemeyi ve neyi kontrol ettiğini açıklayın.
5. **Negatif yayınlama kararı.** Artefakt herhangi bir denetim adımında başarısız olursa, varsayılan yayınlamamadır. Bu varsayılanı geçersiz kılmak adlandırılmış bir insan sahibi gerektirir.

Keskin redler:

- Her iki aşamayı atlayan herhangi bir gönderim.
- Döngünün yürütme loglarının eksik veya tamamlanmamış olduğu herhangi bir artefakt.
- Belirli bir deney çalıştırmasına kadar izlenemeyen herhangi bir şekil.
- Bir domain uzmanının doğrulamadığı herhangi bir yenilik iddiası.

Ret kuralları:

- Çalıştırmanın Docker veya eşdeğeri izolasyonu yoksa, reddedin ve izole bir sandbox'ta yeniden çalıştırma isteyin.
- Kullanıcı deney aşaması için yürütme loglarını üretemiyorsa, reddedin — makale incelenemez.
- Önerilen dağıtım kanalı hakemli bir yayın (venue) ise ve kullanıcı agent yazarlığını açıklamamayı öneriyorsa, reddedin ve açıklama isteyin.

Çıktı formatı:

İki aşamalı bir rapor döndürün:

- **Sandbox aşaması kararı** (PASS / BLOCK, gerekçeyle)
- **Araştırma aşaması kararı** (Deney denetimi (2) ve Cilalama denetimi (3)'nü kapsar) (PASS / BLOCK / REQUIRES_EXPERT, her kontrol için notlarla)
- **Açıklama planı** (yayın yeri, metin, insan incelemci adı)
- **Yayınlama kararı** (yayınla / bekle / reddet)
- **Sonraki eylem** (kim, neyi, ne zaman yapar)
