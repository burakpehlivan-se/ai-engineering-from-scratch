---
name: coding-scaffold-audit
description: Production kod değişiklikleri için benimsemeden önce, önerilen bir kodlama-agent scaffold'unu (erişim, doğrulayıcı döngü, sandbox, benchmark uyumu) dört eksende denetleyin.
version: 1.0.0
phase: 15
lesson: 9
tags: [coding-agent, scaffolding, swe-bench, codeact, openhands]
---

Önerilen bir kodlama-agent scaffold'u (SWE-agent, OpenHands, Aider, Cline, Devin, Claude Code veya kurum içi yapım) verildiğinde, dört eksen boyunca puanlayın ve benchmark sayılarının production kalitesini nerede abartacağını işaretleyin.

Üretin:

1. **Erişim (Retrieval).** Scaffold'un agent hareket etmeden önce hangi dosyaları okuduğunu nasıl seçtiğini tanımlayın. Repo haritası, embedding araması, açık dosya listesi veya agent-tarafından yönlendirilen `grep` çağrıları. Erişim kalitesi, sessiz baskın güvenilirlik faktörüdür.
2. **Doğrulayıcı döngüsü.** Scaffold testleri çalıştırıyor, stack trace'i okuyor ve başarısızlığı bir sonraki tura (turn) geri besliyor mu? Doğrulayıcı döngüsü yoksa, eksik olarak işaretleyin — bu genellikle SWE-bench benzeri görevlerde mutlak 10+ puan deltasıdır.
3. **Sandbox ve patlama yarıçapı.** Eylemler nerede yürütülüyor? Yerel dosya sistemi, kısa-ömürlü container, yönetilen VM. CodeAct tarzı scaffold'lar için, sandbox'ın sertleştirildiğini (egress yok, host bağlamı yok, zaman sınırı) doğrulayın. JSON araç-çağrısı scaffold'ları için, araç doğrulayıcılarının amaçlanmamış her yan etkiyi reddettiğini doğrulayın.
4. **Benchmark uyumu.** Raporlanan sayının (örn. "SWE-bench Verified'da %80.9") gerçekte hangi dağılımı kapsadığı. Benchmark'ın 1-2 satırlık görevlerden oluşan kesrini sayın; aynı model için raporlanan puanı SWE-bench Pro (10+ satırlık görevler) ile karşılaştırın. Başlık sayısı kolay kuyruk tarafından yönlendirilen bir scaffold, production sinyali değildir.

Keskin redler:

- Önemsiz karmaşıklığın üzerindeki görevler için doğrulayıcı döngüsü olmayan herhangi bir scaffold.
- Gerçek depoları gösteren, sandbox izolasyonu (Docker yok, rootless container yok, VM yok) olmayan CodeAct scaffold'ları.
- Dağılımı (kolay-kuyruk kesri, Pro-eşdeğer puanı) açıklamayan benchmark iddiaları.
- Tek bir aracın herhangi bir yola doğrulayıcısız dokunabildiği araç-çağrısı scaffold'ları (örn. modele açık ham bir `shell_exec` aracı).

Ret kuralları:

- Kullanıcı, temsili bir iç dağılımda scaffold'un test-süiti geçme oranını üretemiyorsa, reddedin ve önce küçük-örneklem bir ölçüm isteyin. Açık benchmark'lar sıralama düzenini tahmin eder, mutlak kaliteyi değil.
- Önerilen scaffold, staging kuru-çalıştırması (dry-run) olmadan production deposuna karşı çalışacaksa, reddedin ve önce staging isteyin. Kodlama agent'ları dosyaları yeniden yazar; kötü erişimli kodlama agent'ları yanlış dosyaları yeniden yazar.
- Kullanıcık go/no-go kararı vermek için yalnızca benchmark puanlarını (kendi eval'leri olmadan) kullanmayı planlıyorsa, reddedin ve iç eval verisi isteyin.

Çıktı formatı:

Şunları içeren puanlı bir memo döndürün:

- **Erişim puanı** (0-5, mekanizma açıklanmış)
- **Doğrulayıcı döngü puanı** (0-5, geri besleme formatıyla)
- **Sandbox puanı** (0-5, izolasyon mekanizmasıyla)
- **Benchmark uyum puanı** (0-5, iç dağılım deltasıyla)
- **Deployment önerisi** (production / staging / yalnızca-araştırma)
- **Tek-satır risk özeti** (en olası ilk production başarısızlığı)
