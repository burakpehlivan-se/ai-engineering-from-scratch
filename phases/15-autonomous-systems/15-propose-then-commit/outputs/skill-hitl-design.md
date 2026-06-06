---
name: hitl-design
description: Önerilen bir Human-in-the-Loop (HITL) iş akışını öneri-sonra-taahhüt (propose-then-commit) şekline karşı inceleyin ve eksik meta verileri, idempotency, doğrulama veya sorgulama-yanıt (challenge-and-response) katmanlarını işaretleyin.
version: 1.0.0
phase: 15
lesson: 15
tags: [hitl, propose-then-commit, idempotency, langgraph, cloudflare, agent-framework, eu-ai-act]
---

Önerilen bir HITL iş akışı verildiğinde, onu öneri-sonra-taahhüt referansına karşı denetleyin ve neyin eksik, yetersiz-belirtilmiş veya düzenleyici-uyumsuz olduğunu işaretleyin.

Üretin:

1. **Öneri meta verileri.** Her önerinin şunları yüzeye çıkardığını doğrulayın: niyet (neden), veri soy ağacı (kaynak içerik), dokunulan izinler, patlama yarıçapı (en kötü durum), geri alma planı. Eksik alanlar engelleyicidir; "agent X'i yapmak istiyor" bir öneri değildir.
2. **Idempotency.** Idempotency key bileşimini adlandırın. Retry'lar aynı kaydı döndürsün diye öneri içeriğinden türetilebilir olmalıdır. Duvar-saati zamanı içeren anahtarlar idempotency anahtarı değildir; loglama zaman damgalarıdır.
3. **Dayanıklılık (Durability).** Store'u adlandırın (PostgreSQL, Redis, Durable Object, bütünlük kontrolü olan nesne depolaması). Onayların agent yeniden başlatmasını, host yeniden başlatmasını ve deploy'u hayatta tuttuğunu doğrulayın. Bellek içi kuyruklar uygun değildir.
4. **Onay yüzeyi. Lastik-damga (rubber-stamp) onayı (tek Onayla düğmesi) bu denetimi geçemez. Gerekenler: niyet anlayışı, patlama yarıçapı doğrulaması ve geri alma hazırlığı üzerinde pozitif kabul ile sorgulama-yanıt kontrol listesi. Kontrol listesinin belirli eylem sınıfına göre uyarlandığını, jenerik olmadığını doğrulayın.**
5. **Taahhüt-sonrası doğrulama.** İş akışının yürütmeden sonra hedef kaynağı yeniden okuduğunu ve doğrulama başarısızlığında uyardığını doğrulayın. "Araç 200 döndü" doğrulama değildir.

Keskin redler:

- Önerileri dayanıklı olarak kalıcılaştırmayan HITL yüzeyleri.
- İncelemcinin agent'ın kendisi olduğu onay akışları.
- Sorgulama-yanıt olmadan herhangi bir geri dönülemez production eylemi.
- Duvar-saati bileşenleri olan idempotency anahtarları.
- Sonuç doğurucu eylemlerde taahhüt-sonrası doğrulamanın eksik olduğu iş akışları.

Ret kuralları:

- Kullanıcı onay UI'sini adlandırır ancak arkasındaki dayanıklı store'u adlandıramazsa, reddedin ve önce bir store isteyin.
- Kullanıcı "max_budget_usd ve bir onay diyaloğu"nu yeterli HITL olarak ele alıyorsa, reddedin. Bütçeler maliyeti sınırlar, doğruluğu değil.
- Deployment yüksek-riskli AB kapsamına dokunuyorsa ve lastik-damga örüntüleri kalıyorsa, Madde 14 gerekçesiyle reddedin.

Çıktı formatı:

Şunları içeren bir öneri-sonra-taahhüt denetimi döndürün:

- **Öneri alan tablosu** (niyet / soy ağacı / patlama / geri alma / izinler — beşi de zorunlu)
- **Idempotency notu** (anahtar bileşimi, retry test sonucu)
- **Dayanıklılık satırı** (store, yeniden-başlatmayı-hayatta-tutuyor mu e/h)
- **Onay yüzeyi** (lastik-damga / kontrol listesi; kontrol listesi ise, soruları listeleyin)
- **Taahhüt-sonrası doğrulama** (mevcut mu e/h, neyi yeniden okuyor)
- **Hazırlık** (production / staging / yalnızca-araştırma)
