---
name: hierarchy-fitness
description: Bir çok-agent'lı görevin hiyerarşik, düz denetçi veya sıralı koordinasyona uyup uymadığına karar verin. Önemli olan başarısızlık modlarını yüzeye çıkarın.
version: 1.0.0
phase: 16
lesson: 06
tags: [multi-agent, hierarchy, crewai, langgraph, decomposition-drift]
---

Bir görev tanımı ve isteğe bağlı bir organizasyon yapısı verildiğinde, koordinasyon örüntüsünü (düz denetçi, hiyerarşik, sıralı) önerin ve korunması gereken spesifik başarısızlık modlarını listeleyin.

Üretin:

1. **Görev şekli analizi.** Görev tek bir doğrusal akış mı, bağımsız dallarla fan-out mu, yoksa kendi alt ekipleri olan yuvalanmış takımlar mı? Gerekçelendirin.
2. **Örüntü kararı.** Sıralı, düz denetçi veya hiyerarşik. Hiyerarşik ise, derinliği belirtin (2 seviye kuvvetle tercih edilir; 3 yalnızca güçlü denetim ihtiyacıyla).
3. **Ayrıştırma planı.** Üst yöneticinin yapması gereken tam bölünme. Her dal için, alt yöneticiyi ve sınırlı kapsamı adlandırın.
4. **Uzlaştırma bütçesi.** Üst yöneticinin taahhüt etmesi gereken tur sayısı. Varsayılan 2.
5. **Koruma rayları.** Üç minimum koruma rayı: her seviyede canary işçi, her sentezde kaynak (provenance) zinciri, ayrıştırma sürüklenmesinde uyarı.
6. **Başarısızlık modu kontrol listesi.** {görev-atama hatası, çıktı yanlış yorumlama, fikir birliği döngüsü} öğelerinden hangisi görev şekli göz önüne alındığında en olasıdır? Her mod için somut bir belirti ve bir azaltma tanımlayın.

Keskin redler:

- Somut bir denetim veya organizasyon gereksinimi adlandırmadan derinlik > 2 öneren herhangi bir öneri.
- Tek doğrusal akışlı görevler için hiyerarşik. Bunlar sıralı pipeline olmalıdır.
- Açık bir uzlaştırma bütçesi olmayan tasarımlar.

Ret kuralları:

- Görev tek bir agent'a sığacak kadar basitse (~10'un altında araç çağrısı), hiyerarşiyi reddedin ve tek-agent önerin.
- Görevin doğal takım sınırları yoksa (her alt adım diğerine bağlı), reddedin ve bunun yerine grup sohbeti örüntüsü önerin.
- Kullanıcı "gerçekçilik" için (insan organizasyonu derin olduğu için) hiyerarşik istiyorsa, insan hiyerarşisinin LLM hiyerarşisine eşlenmediğini işaretleyin ve daha düz olanı önerin.

Çıktı: Tek sayfalık özet. Örüntü kararıyla açın, en büyük üç risk ve koruma raylarıyla kapatın.
