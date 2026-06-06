---
name: llm-security-plan
description: Sırlar kasası, tutarlı tokenleştirmeyle PII temizleme, ağ çıkış izin-listesi, denetim günlüğü saklama ve sıfır-güven duruşunu kapsayan bir LLM güvenlik planı üret.
version: 1.0.0
phase: 17
lesson: 25
tags: [security, vault, hashicorp, aws-secrets-manager, pii, presidio, egress, audit-log, zero-trust, ci-cd-supply-chain]
---

Düzenleyici kapsam (SOC 2, HIPAA, GDPR), mevcut kimlik bilgisi durumu ve ağ/çıkış duruşu verildiğinde bir güvenlik planı üret.

Üretilecekler:

1. **Kasa geçişi.** Kasayı seç (HashiCorp, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager). Ağ geçidi kalıbı: uygulamalar → ağ geçidi → çalışma zamanında kasa. Sabit kodlanmış ortam değişkeni ve yapılandırma-dosyası kimlik bilgilerini kullanımdan kaldır.
2. **Gizli tarama.** Her commit'te TruffleHog / GitGuardian / Gitleaks etkinleştir. Algılamada PR'ı engelle.
3. **Rotasyon politikası.** ≤ 90 gün. Mümkün olduğunda otomatik. CI/CD kimlik bilgileri için özel rotasyon (önerilen: daha kısa — 30g).
4. **PII temizleme.** Varlık tanıma (Presidio + regex). Tutarlı tokenleştirme (aynı değer → aynı yer tutucu) anlamı korumak için.
5. **Çıkış izin-listesi.** LLM sağlayıcı alan adlarını, vektör veritabanını, kasa uç noktalarını beyaz listeye al. DNS izin-listesi çözümleyicisi.
6. **Denetim günlüğü.** Yalnızca-ekleme, değişmez. Zorunlu alanlar: kullanıcı, kiracı, istem/yanıt karması, token'lar, maliyet, guardrail tetiklemeleri. Saklama çerçeveye göre (SOC 2 1y / HIPAA 6y).
7. **CI/CD hijyeni.** OIDC kimlik federasyonu (statik bulut anahtarı yok). CI/CD kimlik bilgilerini dar kapsamla. Motivasyon olarak 2026 Vercel tedarik-zinciri olayına atıf.

**Hard rejects (zorunlu redler):**
- Yapılandırma dosyalarında statik anahtarlar. Reddet.
- Denetim günlüğünde ham istemleri depolamak. Reddet — düzenleyici çerçeve açıkça gerektirmediği sürece yalnızca karma.
- `*`'a veya "internete" çıkışa izin vermek. Reddet — beyaz liste.

**Reddetme kuralları:**
- Müşteri için kasa kabul edilemezse (hava-boşluklu gereksinim), normal planı reddet ve dosya-tabanlı-rotasyonlu yedek tasarla. Açıkça daha az güvenli olduğunu not et.
- PII temizleme "gecikme" nedenleriyle reddedilirse, reddet — gecikme genellikle <20 ms'dir ve düzenleyici risk bunu katlar.
- Vault root token'ı için >90 gün rotasyon istenirse, reddet — ihlal vektörüne dönüşür.

**Çıktı:** Kasa, tarama, rotasyon, temizleme, çıkış, denetim günlüğü, CI/CD duruşu içeren tek sayfalık bir plan. Tek bir metrikle bitir: ay başına gizli-tarama isabet sayısı; hedef sıfır.
