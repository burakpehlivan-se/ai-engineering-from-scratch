---
name: ai-sre-plan
description: Bir ekip için AI SRE yayılımı tasarla — çok-agent'lı triyaj mimarisi, yapılandırılmış runbook'lar, hasmane değerlendirme, dar otomatik düzeltme ve tahmine-dayalı-algılama duruşu.
version: 1.0.0
phase: 17
lesson: 23
tags: [ai-sre, multi-agent, runbooks, auto-remediation, adversarial-eval, datadog-bits-ai, neubird, predictive]
---

Ekip büyüklüğü, olay hacmi, gözlemlenebilirlik olgunluğu ve risk toleransı verildiğinde bir AI SRE planı üret.

Üretilecekler:

1. **Mimari.** Çok-agent'lı: denetçi + log agent + metrik agent + runbook agent + insan kapısı. Uzmanlaşmış agent'ları mevcut veri kaynaklarıyla (Datadog, Grafana, Loki, Confluence) eşle.
2. **Runbook dönüşümü.** Yapılandırılmamış Confluence'dan, semptom / hipotez / doğrula / hareket bölümleri olan yapılandırılmış markdown'a geç. Git'te sürümle.
3. **Ürün seçimi.** Datadog Bits AI, Azure SRE Agent, NeuBird Hawkeye, Incident.io Autopilot veya kendin yap.
4. **Otomatik düzeltme kapsamı.** Dar güvenli küme (pod'u yeniden başlat, dağıtımı geri al, sınırlar içinde ölçeklendir). Açık red listesi (topoloji, kod, IAM, veritabanı). Kod olarak politika.
5. **Hasmane değerlendirme.** Otomatik düzeltme için iki-model uzlaşı kapısı belirle. Uyuşmazlık yükseltir.
6. **Tahmine-dayalı-algılama duruşu.** Düşünülüyorsa (MIT %89 sonucu), tahrik politikasını adlandır — pager, ön-drain, otomatik-ölçek — aksi durumda yalnızca bir panodur.

**Hard rejects (zorunlu redler):**
- Geniş değişikliklerde insan kapısı olmadan otomatik düzeltme. Reddet — güvenli kümeyi açıkça adlandır.
- Bilgi tabanı olarak yapılandırılmamış runbook'lar. Reddet — yapılandırılmış, sürümlenmiş markdown zorunlu.
- "Kur ve unut" çerçevelemesi. Reddet — otonom olan ve olmayan şeyleri açıkça kapsamla.

**Reddetme kuralları:**
- Olay hacmi <10/ay ise, tam AI SRE yayılımını reddet — maliyet faydayı aşar. Yalnızca yapılandırılmış runbook'lar öner.
- Ekip gözlemlenebilirliği olgun değilse (loglar aranamaz, metrikler seyrek), reddet — AI SRE kötü veriyi büyütür.
- Ekip ilk özellik olarak "tahmine dayalı algılama → otomatik düzeltme" öneriyorsa, reddet — önce tahrik-politika sorusunu yürü.

**Çıktı:** Mimari, runbook planı, ürün seçimi, otomatik düzeltme kapsamı, hasmane kapı, tahmine-dayalı duruş içeren tek sayfalık bir plan. 12 haftalık bir yayılım takvimiyle bitir: 1-4. haftalar yapılandırılmış runbook'lar, 5-8. triyaj agent'ı, 9-12. dar otomatik düzeltme.
