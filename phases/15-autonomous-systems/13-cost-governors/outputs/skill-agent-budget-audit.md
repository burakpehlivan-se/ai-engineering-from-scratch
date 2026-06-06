---
name: agent-budget-audit
description: Bir agent deployment'ının maliyet-yönetici (cost-governor) stack'ini denetleyin ve gözetimsiz çalıştırmaları etkinleştirmeden önce eksik katmanları işaretleyin.
version: 1.0.0
phase: 15
lesson: 13
tags: [cost-governors, denial-of-wallet, budgets, claude-code-sdk, agent-governance]
---

Önerilen bir agent deployment'ı verildiğinde, maliyet-yönetici (cost-governor) stack'ini on iki-katmanlı referansa karşı denetleyin ve hangi katmanların eksik, yetersiz-ayarlanmış veya fazla-ayarlanmış olduğunu işaretleyin.

Üretin:

1. **Katman envanteri.** On iki referans katmanının her biri (istek başına tavan, görev başına token bütçesi, görev başına dolar bütçesi, araç başına tavan, iterasyon tavanı, dakika/saat/gün/ay başına kayan tavanlar, hız sınırı, kademeli yönlendirme, prompt caching, bağlam pencereleme, HITL kontrol noktaları, kill switch) için, yapılandırılıp yapılandırılmadığını ve hangi değerde olduğunu belirtin.
2. **Başarısızlık modu eşlemesi.** Her zaman-ölçeği başarısızlığı (kontrolsüz döngü, yavaş sızıntı, kötü sürüm, meşru sürdürüm) için, onu yakalayan spesifik katmanı ve ne kadar hızlı olduğunu adlandırın.
3. **Araç-spesifik tavanlar.** Agent'ın çağırabileceği her aracı listeleyin. Her biri için, oturum başına bir tavan ve bir neden adlandırın. Açık tavanı olmayan herhangi bir araç açık bir döngüdür.
4. **Uyarı eşikleri.** Tavanlardan ayrı olarak: hangi harcama oranında bir insan sayfa alır? Gözlemlenen e-ticaret vakası ($1,200 → $4,800) haftalık-bir-büyüme sorunuydu, aylık tavan sorunu değil.
5. **Kill switch yolu.** Bir tavan tetiklendiğinde ne olur? Temiz iptal, geri alma (rollback), uyarı, yeniden etkinleştirme prosedürü. Kill switch'in harici olduğunu (agent kendi tavanını düzenleyemez) doğrulayın.

Keskin redler:

- Görev başına dolar bütçesi olmayan herhangi bir otonom deployment.
- Hız sınırı olmayan gözetimsiz uzun-horizon çalıştırmalar.
- Yeni (<30 gün) araç eklentisinde araç başına tavanı olmayan araç yüzeyleri.
- Agent'ın kendisinin değiştirebileceği kill switch'ler.
- Tek tavan olarak aylık tavan (diğer her zaman ölçeği korunmasız).

Ret kuralları:

- Kullanıcı bugünkü model fiyatlarıyla en-kötü-durum bir çalıştırmayı fiyatlandıramıyorsa, reddedin ve maliyetlendirilmiş bir tahmin isteyin.
- Önerilen bütçe, organizasyonun tek bir hatada kabul edilebilir kaybını aşıyorsa, reddedin ve daha düşük bir tavan isteyin.
- Kullanıcı Auto Mode sınıflandırıcısını (Ders 10) bütçelerin yerine geçen bir şey olarak ele alıyorsa, reddedin. Sınıflandırıcı maliyete dik değildir; her iki katman da gereklidir.

Çıktı formatı:

Şunları içeren bir maliyet-yönetici denetimi döndürün:

- **Katman tablosu** (katman adı, yapılandırıldı mı e/h, değer)
- **Başarısızlık modu kapsamı** (4 satır: döngü / sızıntı / sürüm / sürdürüm)
- **Araç başına tavanlar** (araç, tavan, neden)
- **Uyarı eşikleri** (oran, sahip, kanal)
- **Kill switch yolu** (tetik, eylem, yeniden etkinleştirme prosedürü)
- **Hazırlık** (production / staging / yalnızca-araştırma)
