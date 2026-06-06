---
name: browser-agent-trust-boundary
description: Agent gerçek bir siteye dokunmadan önce, önerilen bir browser-agent deployment'ını kapsamlandırın — güven bölgeleri, yetkili yazımlar, gerekli savunmalar.
version: 1.0.0
phase: 15
lesson: 11
tags: [browser-agents, prompt-injection, trust-boundary, osworld, webarena]
---

Önerilen bir browser-agent iş akışı verildiğinde, her okumayı, her yazımı ve ilk çalıştırma için gereken minimum savunma stack'ini numaralandıran bir güven sınırı kapsam belgesi üretin.

Üretin:

1. **Okuma yüzeyi.** Agent'ın getireceği her origin'i listeleyin. Her birini güven-içinde (kullanıcının organizasyonu tarafından işletilen birinci-taraf siteler) veya güven-dışı (herhangi bir üçüncü-taraf, herhangi bir kullanıcı-tarafından-üretilmiş içerik, herhangi bir arama sonucu) olarak sınıflandırın. Tüm güven-dışı okumalar potansiyel prompt-injection (komut enjeksiyonu) kanalları olarak ele alınmalıdır.
2. **Yazma yüzeyi.** Agent'ın yetkilendirildiği her sonuç doğurucu eylemi listeleyin (form göndermek, içerik yayınlamak, bir backend aracı çağırmak, belleğe yazmak). Her biri için, patlama yarıçapını ve eylemin geri-dönülebilir olup olmadığını belirtin.
3. **Gerekli savunmalar.** Minimum stack: içerik temizleyici (sanitizer), okuma/yazma sınırı (content_origin güven-dışı olduğunda yazımlar taze onay gerektirir), görev başına araç allowlist'i, kapsamlı kimlik bilgileriyle oturum izolasyonu, kalıcı bellekte canary token'ları, geri dönülemez eylemlerde HITL.
4. **Benchmark-dağılım uyumu.** Agent bir BrowseComp, OSWorld veya WebArena-Verified puanı raporluyorsa, benchmark'ın gerçek görevle dağılım örtüşmesini adlandırın. Yüksek bir BrowseComp puanı, rezervasyon akışı güvenilirliğini tahmin etmez.
5. **Bilinen-saldırı kontrol listesi.** Deployment'ın şunlara karşı sertleştirildiğini doğrulayın: (a) görünür-metin enjeksiyonu, (b) URL parçası/sorgu enjeksiyonu, (c) bellek-bağlama saldırıları (Tainted Memories sınıfı), (d) kimlik doğrulamalı oturumlarda CSRF-şeklinde saldırılar, (e) tek-tıklama kaçırmaları. Her biri için, spesifik savunmayı ve nerede tetiklendiğini adlandırın.

Keskin redler:

- Production kimlik bilgilerine erişimi olan ve oturum izolasyonu olmayan browser agent'ları.
- Güven-dışı içerikten başlatılan bir yazımın taze HITL onayı gerektirmediği herhangi bir deployment.
- Yalnızca içerik temizleyicisine güvenen herhangi bir deployment (temizleyiciler kolay saldırıları yakalar; sofistike payload'lar geçer).
- Canary girişleri olmayan kalıcı bellek.
- Yazımlarda HITL olmadan finansal işlemlere veya müşteri verisine dokunan iş akışları.

Ret kuralları:

- Kullanıcı, enjeksiyon-tahrikli yanlış bir yazımın patlama yarıçapını adlandıramıyorsa, reddedin ve açık bir cümle isteyin.
- Kullanıcı, kapsamlı kimlik bilgilerinin mevcut olmadığı bir stack'te browser agent öneriyorsa, reddedin ve önce ayrı bir kimlik isteyin.
- Kullanıcı, agent'ın bir production görevini "yapabildiğine" dair kanıt olarak bir benchmark puanını (BrowseComp, OSWorld, WebArena) gösteriyorsa, reddedin ve gerçek dağılım üzerinde iç eval'ler isteyin.

Çıktı formatı:

Şunları içeren bir güven sınırı memo'su döndürün:

- **Okuma yüzeyi tablosu** (origin, güven-içinde / güven-dışı)
- **Yazma yüzeyi tablosu** (eylem, patlama yarıçapı, geri-dönülebilir mi e/h)
- **Savunma stack'i** (yapılandırılmış katmanların maddeli listesi)
- **Benchmark-uyum notu** (varsa)
- **Bilinen-saldırı kontrol listesi** (beş satır, satır başına adlandırılmış savunma)
- **Deployment kararı** (production / staging / yalnızca-araştırma)
