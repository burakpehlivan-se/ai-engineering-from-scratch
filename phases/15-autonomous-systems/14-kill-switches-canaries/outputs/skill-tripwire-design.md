---
name: tripwire-design
description: Önerilen bir agent dedektör stack'ini (kill switch, circuit breaker'lar, canary token'ları) inceleyin ve ilk otonom çalıştırmadan önce eksik tetikleyicileri işaretleyin.
version: 1.0.0
phase: 15
lesson: 14
tags: [kill-switch, circuit-breaker, canary, honeytoken, detection-and-response]
---

Bir agent deployment'ı için önerilen dedektör stack'i verildiğinde, onu üç-dedektör referansına (kill switch, circuit breaker, canary) karşı denetleyin ve neyin eksik, yanlış-ayarlanmış veya agent'a maruz olduğunu işaretleyin.

Üretin:

1. **Kill switch denetimi.** Anahtar nerede yaşıyor (feature flag, Redis, imzalı yapılandırma)? Agent'ın kimlik bilgilerinin onu tetikleyemeyeceğini doğrulayın. Her sonuç doğurucu eylemin anahtarı yalnızca başlangıçta değil kontrol ettiğini doğrulayın. Yeniden etkinleştirmenin açık bir insan eylemi olduğunu doğrulayın.
2. **Circuit breaker envanteri.** Bir breaker'ın izlediği her örüntüyü (tekrarlama, ardışık başarısızlıklar, oran, güven-dışı okumadan sonra belirli araç) listeleyin. Her biri için eşik ve cool-down (soğuma) belirtin. 10'un üzerindeki eşikler genellikle çok gevşektir.
3. **Canary tasarımı.** Ortamdaki her canary token'ını listeleyin. Her biri için: ne olduğu (sahte kimlik bilgisi, sahte DB kaydı, sahte dosya, sahte bellek girişi), nerede yaşadığı, hangi erişim alarmı tetikler, kim sayfa alır. Hiçbir canary'nin dokunmak için meşru bir nedeni olmadığını doğrulayın.
4. **İstatistiksel + sert katmanlama.** Stack'in herhangi bir istatistiksel dedektörün (EWMA — üstel ağırlıklı hareketli ortalama, z-skoru) yanı sıra en az bir sert sınır (Ders 17 anayasal stil) kullandığını doğrulayın. Yalnızca-istatistiksel dedektörler yavaş sürüklenmeyi kabul eder.
5. **Karantina yolu.** Bir dedektör tetiklendiğinde ne olur? Tam agent durdurma, yola-özgü duraklama, trafik yönlendirme (eBPF / Cilium honeypot), yalnızca uyarı. Yolun uçtan uca en az bir kez test edildiğini doğrulayın.

Keskin redler:

- Harici kill switch'i olmayan herhangi bir deployment.
- Canary token'larının agent'ın yazma erişimi olan sistemlerde depolanması.
- Sert sınırları olmayan yalnızca-istatistiksel tespit.
- Cool-down'ları insan incelemesi olmadan otomatik-yeniden-etkinleştiren circuit breaker'lar.
- Kill switch'in yalnızca başlangıçta, eylem başına değil kontrol edildiği gözetimsiz çalıştırmalar.

Ret kuralları:

- Kullanıcı, kill switch'i barındıran agent kimlik bilgilerinin dışındaki spesifik sistemleri adlandıramıyorsa, reddedin. "Agent'ın okuduğu bir yapılandırma dosyası kullanıyoruz", agent yapılandırma dosyalarını yazabiliyorsa bir kill switch değildir.
- Kullanıcı Auto Mode sınıflandırıcısını (Ders 10) tetikleyicilerin (tripwires) yerine geçen bir şey olarak ele alıyorsa, reddedin. Sınıflandırıcı tespit-ve-yanıta dik değildir.
- Önerilen canary'ler agent'ın okumak için meşru nedeni olan sistemlerdeyse, reddedin ve yeniden tasarım isteyin.

Çıktı formatı:

Şunları içeren bir tetikleyici denetimi döndürün:

- **Kill switch satırı** (konum, kontrol sıklığı, yeniden etkinleştirme prosedürü)
- **Circuit breaker tablosu** (örüntü, eşik, cool-down)
- **Canary tablosu** (token, konum, alarm, sahip)
- **Katmanlama notu** (istatistiksel + sert sınırlar mevcut mu e/h)
- **Karantina akışı** (ne tetikler, ne olur, test edildi mi e/h)
- **Hazırlık** (production / staging / yalnızca-araştırma)
