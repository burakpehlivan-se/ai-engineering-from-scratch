---
name: simulation-designer
description: Belirli bir senaryo için üretken-agent (Smallville-stili) bir simülasyon tasarlayın. Bellek şemasını, yansıtma (reflection) sıklığını, plan ufkunu, mekansal/sosyal kısıtlamaları ve değerlendirme metriklerini belirler.
version: 1.0.0
phase: 16
lesson: 17
tags: [multi-agent, simulation, generative-agents, emergence, memory]
---

Bir agent popülasyonundan (sosyal simülasyon, oyun NPC'leri, politika provası, piyasa dinamikleri) acıkan (emergent) davranış gerektiren bir senaryo verildiğinde, simülasyonu tasarlayın.

Üretin:

1. **Popülasyon büyüklüğü ve heterojenliği.** N agent; hangileri bir temel modeli paylaşıyor vs hangileri farklı; prompt aileleri; rol dağılımı. Smallville 25 homojen agent kullandı bireyselleştirilmiş personalarla; daha büyük popülasyonlar heterojenlikten fayda görür.
2. **Bellek şeması.** Giriş başına alanlar: `(ts, kind, content, importance, embedding_ref, source_ids)`. Yenilik-azalma sabiti; önem puanlama prosedürü; ilgililik metriği (embedding modeli X ile kosinüs). Sıkıştırma için tutma politikası.
3. **Yansıtma (reflection) sıklığı.** Tetikleyici: işlenmemiş önem toplamı > eşik, veya her N gözlemde, veya periyodik tick. Tetikleyici başına yansıtma sayısı. Yansıtma prompt şablonu.
4. **Plan ufuğu.** Gün / saat / eylem seviyeleri. Hangileri zorunlu; hangileri isteğe bağlı. Revizyon tetikleyicisi: aktif planla çelişen, önemi > eşik olan yeni bir gözlem.
5. **Dünya modeli.** Mekansal ızgara, sosyal grafik, kaynak kısıtlamaları. Bir gözlemi ne oluşturur (görüş çizgisi, konuşma, bildirim). Mimarinin öğrenmediği ve açıkça kodlanması gereken normatif kısıtlamalar (kapasite sınırları, kapalı saatler, özel alanlar).
6. **Tohum hedefler.** Hangi agent'lar hangi önceliklerle tohumlanır. Rekabet edebilecek örtüşen hedefler; bir arada var olması gereken rekabet-etmeyen hedefler.
7. **Bütçe.** Tick başına agent başına LLM çağrıları (gözlemle + getir + yansıt + planla + hareket et). Agent başına tick başına beklenen token. T tick için toplam simülasyon maliyeti.
8. **Değerlendirme metriği.** İnandırıcılık (insan puanlayıcı), hedef-başarı oranı, sayılan koordinasyon olayları, başarısızlık sinyali olarak mekansal-norm ihlalleri.

Keskin redler:

- Açık mekansal / sosyal norm kodlaması olmayan tasarımlar. Mimari onları ihlal edecek (Park 2023'ten kapalı-mağaza, tek-banyo başarısızlıkları).
- Değiştirilebilir bellekli tasarımlar. Bellek yalnızca-eklenebilir olmalı; düzeltmeler yeni girişlerdir.
- Her tick'te yansıtma çalıştıran tasarımlar. Bu bütçe-verimsizdir; yansıtma pahalıdır ve tetikleyiciler eşik-tabanlı olmalıdır.
- Bellek-sıkıştırma stratejisi olmadan büyük N'de (> 50) simülasyonlar. Getirme maliyeti akış uzunluğuyla büyür.

Ret kuralları:

- Senaryo acıkan görev yürütme yerine acıkan sosyal davranış gerektiriyorsa, bunun yerine denetçi / roller / ilkeller örüntülerini önerin (Faz 16 · 05-08). Smallville sosyal simülasyon içindir.
- Bütçe tick başına toplam 100'ün altında LLM çağrısına izin veriyorsa, daha büyük popülasyonlar yerine yoğun etkileşimli N = 3-5 önerin.
- Senaryo acıkıştan fayda görmüyorsa (sıkı-senaryolu görev), tek-agent + araçlar önerin.

Çıktı: Tek sayfalık tasarım özeti. Tek cümlelik bir özetle başlayın ("Smallville-stili simülasyon: 15 heterojen agent, önem toplamı > 120'de yansıtma, 3-seviyeli plan ufuğu, kapasite kısıtlamalı mekansal ızgara, inandırıcılık + koordinasyon olaylarıyla ölçülen."), sonra yukarıdaki sekiz bölüm. Beklenen acıkan davranışlar ve izlenecek ilk üç başarısızlık modu ile bitirin.
