---
name: ipi-audit
description: Ajan tabanlı bir dağıtımı dolaylı istem enjeksiyonu (indirect prompt injection) maruziyeti ve bilgi-akış-kontrolü kapsamı için denetle
version: 1.0.0
phase: 18
lesson: 15
tags: [ipi, indirect-prompt-injection, ifc, agent-security, owasp-llm01]
---

Bir ajan tabanlı dağıtım açıklaması verildiğinde, dağıtımı dolaylı istem enjeksiyonu (IPI) maruziyeti için denetle.

Çıktı:

1. Güvenilmeyen-içerik envanteri. Ajanın okuyabileceği her içerik kaynağını listele: RAG belgeleri, gelen kutusu, takvim, araç çıktıları, biletler, ürün yorumları, üçüncü taraf API'leri. Her biri potansiyel bir IPI vektörüdür.
2. Güven etiketleme. Dağıtım, güvenilir (kullanıcı istemi) içeriği güvenilmeyen (getirilen içerik) olandan ayırıyor mu? İçerik bir etiket olmadan aynı istemde birleştiriliyorsa, IFC (bilgi-akış-kontrolü) yürürlükte değildir.
3. Eylem geçitleme. Hangi araçlar çağrılabilir? Her biri için, çağrı yalnızca güvenilir istemle mi geçitleniyor, yoksa güvenilmeyen içerik çağrıyı etkileyebilir mi?
4. Adaptif saldırı değerlendirmesi. Dağıtım, Nasr ve diğerleri 2025'e göre adaptif saldırılarla (gradyan, RL, insan kırmızı takım) test edildi mi? Yalnızca statik saldırı değerlendirmesi yetersizdir.
5. Kapsam-ihlali sınırları. Her çapraz-güven sınırını belirle (örn. gelen kutusu -> gönder, belgeler -> harici API). Her biri için, eylemin güvenilmeyen etki altında ya yasaklandığını ya da güvenilir istemle açıkça onaylandığını doğrula.

Kesin redler:

- Getirilen içerik üzerinde açık güven etiketlemesi olmayan herhangi bir ajan dağıtımı.
- Yalnızca statik saldırılara dayanan herhangi bir savunma iddiası.
- IFC mekanizmasını adlandırmadan "ajanımız istem enjeksiyonuna güvenli" iddiası.

Ret kuralları:

- Kullanıcı filtrelemenin yeterli olup olmadığını sorarsa, reddet ve Nasr 2025'in adaptif saldırıların filtre tabanlı savunmaların >%90'ını kırdığı sonucunu açıkla.
- Kullanıcı gümüş kurşun bir savunma isterse, reddet — IPI savunması, IFC artı katmanlı yanıt moderasyonu artı yüksek-riskli eylemlerde insan denetimi gerektirir.

Çıktı: Yukarıdaki beş bölümü dolduran, en tehlikeli güvenilmeyen-güvenilir sınırını işaretleyen ve eklenmesi en acil olan tek denetimi adlandıran tek sayfalık bir denetim. MDPI Information 17(1):54 (2026) ve Nasr ve diğerlerini (Ekim 2025) her birini bir kez alıntıla.
