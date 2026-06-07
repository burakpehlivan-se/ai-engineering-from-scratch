---
name: batch-triager
description: LLM iş yüklerini interaktif / yarı-interaktif / toplu iş şeritlerine triyajla, yığılmış indirimi (toplu iş + önbellek) hesapla ve yanlış-triyajlanan iş yüklerini işaretle.
version: 1.0.0
phase: 17
lesson: 15
tags: [batch-api, openai-batch, anthropic-batches, vertex-batch, triage, cost]
---

Bir iş yükü (ad, gecikme için kullanıcı beklentisi, trafik hacmi, paylaşılan istem yapısı) verildiğinde bir triyaj + maliyet planı üret.

Üretilecekler:

1. **Şerit.** İnteraktif (TTFT-bağlı, senkron), yarı-interaktif (dakikalar OK, asenkron kuyruk) veya toplu iş (sabah-olunca OK, toplu iş API'si). Belirli kullanıcı beklentisiyle gerekçelendir.
2. **Mevcut maliyet.** Mevcut yapılandırmada (senkron, önbellek yok vb.) aylık maliyeti hesapla.
3. **Hedef maliyet.** Önerilen yapılandırmadan (toplu iş + önbellek veya senkron + önbellek) sonraki maliyeti hesapla. Mevcut durumun %'si olarak ifade et.
4. **Geçiş planı.** Sağlayıcıya-özgü adımlar (iş yükünün modeliyle eşleşeni seç, ikisini birden değil):
 - OpenAI: `/v1/batches`'e geçir. İstem önbellekleme uygun istemler için (≥1024 token) otomatik olarak etkinleştirilir — ayarlanacak `cache_control` yok. İsteğe bağlı olarak daha sıkı atıf için `prompt_cache_key` geçir.
 - Anthropic: Message Batches'e geçir. Önbellek yeniden kullanımı, önbelleklenebilir istem aralıklarında açık `cache_control` blokları (ör. `{"type": "ephemeral"}`) gerektirir; toplu iş indirimi önbellekli-okuma fiyatlandırmasıyla yığılır.
 - İkisi: Bir başarı/başarısızlık webhook'u ve dönüş penceresini kaçıran toplu işler için senkrone taşma şeridi enstrüman et.
5. **Risk.** Toplu iş dönüşü P99'da 20 saat ise ne olur? Aşağı akış sistem davranışını adlandır (e-posta teslimi, senkrone kuyruk taşması).
6. **Gözlemlenebilir.** Yanlış-triyajı yakalayan metrik: toplu iş tamamlama gecikmesi P95; > 12 saat ise uyar.

**Hard rejects (zorunlu redler):**
- Kullanıcının yalnızca "sabah-olunca" gecikme gerektirdiği bir gece-boruhattını toplu iş kullanmadan senkron modda çalıştırmak. Reddet — sızan ~%90 harcamayı belirt.
- 15-dakika altı kullanıcı beklentisi olan herhangi bir şey için toplu iş vaat etmek. Reddet — toplu iş SLA'sı 24 saattir.
- Paylaşılan sistem istemli bir toplu iş yükünde istem önbelleklemeyi yok saymak. Reddet — yığılmış indirim asıl noktadır.

**Reddetme kuralları:**
- İş yükü "gerçek-zamanlı" olarak pazarlanıyor ancak gerçek kullanıcı beklentisi dakikalar ise, toplu iş önermeden önce açık onay zorunlu.
- İş yükü toplu işte istem önbelleği olmayan bir sağlayıcıyı hedefliyorsa (ör. KV-önek yeniden kullanımı olmayan herhangi bir özel veya self-hosted yığın), yalnızca toplu iş indiriminin geçerli olduğunu not et ve yığılmış tasarruf olmadan yeniden hesapla. OpenAI toplu iş önbellekleme otomatiktir; Anthropic toplu iş önbellekleme açık `cache_control` blokları gerektirir.
- İş yükü sıkı gecikme SLA'sına sahipse (ör. P99 < 60s), toplu işi açıkça reddet — farklı bir şeride aittir.

**Çıktı:** Şerit, mevcut maliyet, hedef maliyet, geçiş adımları, risk, gözlemlenebilir içeren tek sayfalık bir triyaj. Ürün yüzeyi değiştikçe tüm iş yüklerini üç aylık olarak yeniden triyajla kadansıyla bitir.
