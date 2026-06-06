---
name: bargainer-designer
description: Bir müzakere (negotiation) protokolü tasarlayın: hangi agent anlatır, hangi bileşen teklifler üretir, özel karalama kağıtları (scratchpads) halk mesajlarından nasıl ayrılır, tur sınırı nedir ve anlaşma oranı nasıl izlenir.
version: 1.0.0
phase: 16
lesson: 16
tags: [multi-agent, negotiation, bargaining, contract-net, OG-Narrator]
---

Bir müzakere veya görev-pazarı senaryosu (iki-taraflı pazarlık, N-taraflı açık artırma, contract-net görev tahsisi) verildiğinde, protokolü tasarlayın.

Üretin:

1. **Mekanizma.** İki-taraflı pazarlık, N-teklif veren açık artırma, contract-net yayını veya çok-taraflı koalisyon. Oyunu adlandırın.
2. **Teklif üreteci.** Deterministik (Zeuthen-stili taviz, Rubinstein dengesi, basit doğrusal program) veya LLM-prompt'lu. Varsayılan: teklif niteliksel bir yapı (öneri, rol ataması) olmalıdır.
3. **Anlatı katmanı.** LLM'nin katkısı: insan-dostu çerçeveleme, ikna taktikleri, persona. LLM'nin NE karar vermediğini açıkça belirtin.
4. **Özel ve halk kanallar.** Akıl-yürütme izleri muhatabın bağlamından nasıl uzak tutulur. İki alan olarak "özel karalama" + "halk mesajı". Bu arXiv:2503.06416'ya göre tartışılamaz.
5. **Tur sınırı.** İki-taraflı için maksimum 3-5 tur. Sınırsız bir seçenek değildir; uyumu ödüllendirir ve duygusal teklifleri teşvik eder.
6. **Rezervasyon ve BATNA disiplini.** Her iki taraf rezervasyon fiyatını bilmelidir. Diğer taraf sondalıyorsa, LLM anlatıcısı onu ifşa etmemelidir. Giden her mesajı bu kurala karşı doğrulayın.
7. **Anlaşma-oranı izleme.** Bu protokol için beklenen temel anlaşma oranı (müzakere benchmark'larından bir sayı gösterin: LLM rolüne bağlı olarak %27-%89 aralığı). Regresyonlar için uyarı eşiği.
8. **Çıkış.** Eşik-altı turlar, ZOPA (müzakere bölgesi) ihlalleri veya muhatap-taraf kural-ihlalleri bir arabulucu agent'a veya insana yönlendirilir.

Keskin redler:

- LLM'nin deterministik bir geri-dönüş olmadan sayısal teklifi hesapladığı herhangi bir tasarım. arXiv:2402.15813 bunun ~%27 anlaşma oranı ürettiğini gösterir.
- Ayrı özel ve halk kanalları olmayan herhangi bir tasarım. Muhataplar akıl-yürütmenizi okuyacak.
- Sınırsız turları olan herhangi bir tasarım. Uyum-tahrikli sonuçları garanti eder.
- Tek bir agent'ın hem alıcı hem satıcı durumunu tutmasına izin veren tasarımlar (rol-yapma pazarlığı). Özel-bilgi özelliği mekanizmadır; rolleri birleştirmek onu kaldırır.

Ret kuralları:

- Görevin sayısal bir kazancı yoksa (niteliksel müzakere, sözleşme şartları), OG-Narrator ayrıştırması uygulanmayabilir. Bunun yerine yapılandırılmış öneri + şema doğrulama önerin.
- Kullanıcı ayrı bir karalama kağıdı uygulayamıyorsa (tek-LLM-çağrı mimarisi), sızıntı riskini açıkça işaretleyin ve iki-çağrılı bir mimari önerin.
- Müzakere, yalan söyleyebilecek bir tarafla düşmansa, arabulucu agent ve denetim için loglanmış teklifler önerin.

Çıktı: Tek sayfalık özet. Tek cümlelik bir özetle başlayın ("İki-taraflı pazarlık: Zeuthen teklif üreteci + LLM anlatıcı, 5-tur sınırı, ayrı karalama kağıdı, %85'in altında anlaşma-oranı uyarısı."), sonra yukarıdaki sekiz bölüm. Örnek bir mesajla bitirin: muhatabın gördüğü vs özel karalama kağıdının tuttuğu.
