---
name: compliance-matrix
description: Müşteri coğrafyası, segmenti ve sözleşme kapsamına göre bir LLM SaaS için gerekli-çerçeve matrisini üret. SOC 2, HIPAA, GDPR, PCI-DSS, EU AI Act, Colorado AI Act, ISO 42001 boyunca kontrolleri eşle.
version: 1.0.0
phase: 17
lesson: 26
tags: [compliance, soc2, hipaa, gdpr, pci-dss, eu-ai-act, colorado-ai-act, iso-42001, iso-27001]
---

Müşteri coğrafyası (ABD / AB / Küresel, veya belirli ABD eyaletleri), segmenti (SaaS / sağlık / fintek), sözleşme kapsamı (kurumsal veya KOBİ) ve mevcut uyumluluk durumu verildiğinde, gerekli-çerçeve matrisini üret.

Üretilecekler:

1. **Gerekli çerçeveler.** Coğrafya, segment, müşteri profili gerekçesiyle ulaşılması gereken her çerçeveyi listele.
2. **Zaman çizelgesi.** Her çerçeve için mevcut durumu (yok / Type I / denetimde / Type II) belirt. Boşluğu adlandır.
3. **Çerçeveler-arası kontrol eşlemesi.** Her gerekli çerçeve için birden fazlasını karşılayan kontrolleri belirle (erişim günlüğü, şifreleme, denetim günlüğü, değişiklik yönetimi).
4. **AB AI Act duruşu.** Ürünün risk seviyesini sınıflandır (kabul edilemez / yüksek / sınırlı / minimal). Yüksek-riskli ise, 2 Ağustos 2026 yürürlük tarihinden önce uygunluk-değerlendirme (conformity assessment) yolu zorunlu kıl.
5. **PII / PHI işleme.** Gerçek-zamanlı çıkarım-katmanı sansürlemeyi (Phase 17 · 25) doğrula — sonradan-işleme GDPR-açısından savunulabilir değildir. PHI'ye dokunan tüm AI satıcıları için BAA'ları doğrula.
6. **Denetim araçları.** Çerçeveler-arası otomasyon için Drata / Vanta / Secureframe. Çok-çerçeve kapsamda maliyetine değer.

**Hard rejects (zorunlu redler):**
- SOC 2 Type I'i kurumsal tedarik için "SOC 2 uyumlu" olarak iddia etmek. Reddet — Type II geçittir.
- BAA olmadan bir sağlayıcıya PHI göndermek. Reddet — HIPAA ihlali.
- GDPR duruşu olarak sonradan-işleme PII temizlemeyi kullanmak. Reddet — gerçek-zamanlı zorunlu.

**Reddetme kuralları:**
- Ürün, GDPR Madde 30 kayıtları olmadan AB kullanıcılarına hizmet veriyorsa, kayıtlar oluşturulana kadar AB müşterilerine gönderimi reddet.
- Ürün, kredi/istihdam/konut/eğitim/temel hizmetler alanlarında Colorado sakinlerine hizmet veriyorsa, SB24-205'in SB25B-004 ile değiştirilmiş haliyle Colorado AI Act kapsamında 30 Haziran 2026 yürürlük tarihinden önce tamamlanmış bir etki değerlendirmesinin kanıtını lansman öncesinde zorunlu kıl.
- Ürün AB AI Act kapsamında yüksek-riskli ise ve ekibin uygunluk-değerlendirme planı yoksa, adlandırılmış bir uygulama ortağı olmadan Ağustos 2026 hazırlığı vaat etmeyi reddet.

**Çıktı:** Gerekli çerçeveler, mevcut durum, boşluklar, zaman çizelgesi, çerçeveler-arası kontroller, AB AI Act seviyesi, PII duruşu, araçlar içeren tek sayfalık bir matris. 12 aylık yol haritasıyla bitir: çerçeve-çerçeve üç aylık kilometre taşları.
