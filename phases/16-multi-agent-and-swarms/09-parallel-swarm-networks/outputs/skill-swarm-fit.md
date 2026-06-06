---
name: swarm-fit
description: Bir görevin swarm (merkezi-olmayan) mimariye mi yoksa denetçi (merkezi) mimariye mi uyduğuna karar verin.
version: 1.0.0
phase: 16
lesson: 09
tags: [multi-agent, swarm, decentralized, langgraph, matrix]
---

Bir görev ve onun throughput / determinizm gereksinimleri verildiğinde, swarm veya denetçi önerin ve spesifik kuyruk ve koruma rayı seçimlerini listeleyin.

Üretin:

1. **Görev bağımsızlık kontrolü.** Alt görevler bağımsız mı yoksa birbirine mi bağlı? Swarm yalnızca bağımsızlık yüksek olduğunda uyar.
2. **Süre dağılımı.** Tekdüze mi yoksa değişken mi? Swarm çoğunlukla değişken-süreli iş yüklerinde kazanır.
3. **Sıralama gereksinimi.** Sıkı, gevşek veya yok. Swarm sırayı korumaz; denetçi korur.
4. **Hata ayıklanabilirlik ihtiyacı.** Yüksek (finans, tıp) → denetçi. Orta → görev başına iz ID'leriyle swarm.
5. **Kuyruk seçimi.** Bellek içi (`queue.Queue`) demolar için; Kafka / Redis Streams / NATS / dayanıklı DB-destekli production için.
6. **İşçi tasarım gereksinimleri.** Idempotent (tekrar-tekrar-aynı-sonuç) olmalı; görev başına iz yayınlamalı; back-pressure (geri-basınç) ile başa çıkmalı.
7. **Anti-açlık planı.** Öncelik yaşlandırma, işçi uzmanlaşması, sınırlı kuyruk.
8. **Gözlemlenebilirlik planı.** Görev başına ID'ler, başlangıç/bitiş olayları, sonuç havuzu şeması.

Keskin redler:

- Sıkı sıralama gereksinimleri olan görevler için swarm önerisi.
- Idempotent işçileri olmayan swarm.
- Production'da dayanıklı kuyruğu olmayan swarm.

Ret kuralları:

- Görevin saniyede 10'un altında bağımsız birimi varsa, swarm'ı reddedin ve denetçi önerin. Düşük throughput'ta swarm yükü haklı çıkmaz.
- Gözlemlenebilirlik gereksinimleri tek bir tutarlı iz gerektiriyorsa (denetim, uyumluluk), swarm'ı reddedin ve bunun yerine LangGraph deterministik grafik önerin.

Çıktı: Tek sayfalık mimari özeti. Uyum kararıyla açın, hedef throughput için spesifik mesaj broker'ı önerisiyle kapatın.
