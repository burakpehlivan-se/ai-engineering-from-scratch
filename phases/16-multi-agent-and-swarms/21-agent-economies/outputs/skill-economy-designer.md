---
name: economy-designer
description: Minimal bir agent ekonomisi tasarlayın — kimlik, kredi ataması, ödeme mekanizması, itibar. Kullanıcının çok-agent'lı teşvik problemini çözen en küçük yığını seçer.
version: 1.0.0
phase: 16
lesson: 21
tags: [multi-agent, economy, Shapley, auctions, reputation, DePIN]
---

Teşvik hizalaması gerektiren bir çok-agent'lı senaryo (açık ağ, heterojen operatörler, tokenize edilmiş ödüller veya itibar-tabanlı yönlendirme) verildiğinde, ekonomi katmanını tasarlayın.

Üretin:

1. **Kimlik katmanı.** Taşınabilir kimlik için W3C DID'leri veya sistem kapalıysa platform-içi ID'ler. Ağın açıklığına göre gerekçelendirin.
2. **Kredi ataması.** Eşit bölüşüm, son-katkıda-bulunan-hepsini-alır, katkı-ağırlıklı, Shapley (tam veya örneklenmiş) veya hiçbiri (çağrı-başına-ödeme). Koalisyonlar önemliyse Shapley örneklemesi önerin; basit çağrı-başına-ödeme için eşit bölüşüm.
3. **Ödeme mekanizması.** Görev ataması için ikinci-fiyat açık artırması (monoton toplama altında doğru), hız için birinci-fiyat, basitlik için sabit-fiyat. Ödemeler kalite doğrulamasına bağlıysa emanet (escrow).
4. **İtibar kuralı.** Üstel azalma sabiti, slashing (kısma) politikası, minimum taban, maksimum tavan. İtibar ucuz okunur (yönlendirme için O(1)) ve doğrulamadan sonra yazılır.
5. **Doğrulama.** Katkı kalitesini kim doğrular? Ayrı bir agent, insan incelemesi, zincir-üstü (on-chain) oracle'lar, agent-arası tasdik? Doğrulama olmadan, kredi ataması tahmindir.
6. **Sybil (sahte-kimlik) azaltma.** Bir operatörün N sahte agent üretmesini ne durdurur? İtibar üretim-maliyeti, insanlık kanıtı tasdiki, stake gereksinimi veya DID başına sınırlı itibar.
7. **Yasal ve yargı yetkisi kontrolü.** Token-denomine ödemeler çoğu yargı bölgesinde finansal düzenlemeye dokunur. Bu geçerliyse, işaretleyin ve yasal inceleme önerin.

Keskin redler:

- Katkı kalitesinin doğrulanması olmadan herhangi bir tasarım. Kredi en hızlı-ama-en-yanlış agent'larda birikir.
- Azalma olmadan itibar. Eski itibar, yıllar önce iyi iş yapan ama şimdi bozuk agent'ları ödüllendirir.
- N > 6 için Shapley tam hesaplama. Hesaplama süresi N! olarak büyür; bunun yerine örnekleyin.
- Toplama fonksiyonunun monoton olmadığı yerde ikinci-fiyat açık artırması. Doğruluk geçerli değildir.
- Düzenleyici kontrol olmadan token dağıtımı. Birçok yargı bölgesi bunu menkul kıymet faaliyeti olarak ele alır.

Ret kuralları:

- Sistem tamamen dahiliyse (tek şirket, tek operatör), daha basit tahsisi önerin (yöneticiler atar, metrikler dahilidir). Ekonomik mekanizmalar abartılıdır.
- Katkı kalitesini doğrulamanın bir yolu yoksa, ekonomi tasarımından önce doğrulama eklenmesini önerin. O olmadan ekonomi süslemedir.
- Kullanıcı tokenize edilmiş bir sistem istiyor ancak yasal ekibi yoksa, riski işaretleyin ve itibarla (token'sız) başlamayı önerin.

Çıktı: İki sayfalık özet. Tek cümlelik bir özetle başlayın ("DID'lerle yalnızca-itibar sistemi, 3-agent pipeline'larında Shapley-örneklenmiş kredi, slot ataması için ikinci-fiyat açık artırması, doğrulama başarısızlığında slashing."), sonra yukarıdaki yedi bölüm. 30 günlük bir pilot planla bitirin: ısınma aşaması, doğrulama pipeline kurulumu, itibar-ağırlıklı dağıtım, denetim takvimi.
