# Güvenlik — Sırlar, API Anahtarı Döndürme, Denetim Günlükleri, Koruyucular

> Sır yayılmasını (secret sprawl) merkezi kasalar (vault) aracılığıyla ortadan kaldırın (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault). Kimlik bilgilerini asla yapılandırma dosyalarında, VCS'deki ortam dosyalarında, e-tablolarda saklamayın. Statik anahtarlar yerine IAM rolleri; CI/CD için OIDC (Açık Kimlik Doğrulama). AI-ağ geçidi kalıbı 2026 çözümüdür: uygulamalar → ağ geçidi → model sağlayıcısı, ağ geçidi kimlik bilgilerini çalışma zamanında kasadan çeker. Kasada döndürün ve tüm uygulamalar dakikalar içinde alır — yeniden dağıtım yok, "yeni anahtarı kimde var" Slack mesajları yok. Döndürme politikası ≤90 gün; her commit'te TruffleHog / GitGuardian / Gitleaks ile tarayın. Sıfır güven (zero-trust): MFA (Çok Faktörlü Kimlik Doğrulama), SSO (Tek Oturum Açma), RBAC/ABAC (Rol/Tabanlı Nitelik Erişim Kontrolü), kısa-ömürlü token'lar, cihaz duruşu. PII temizleme, iletmeden önce PHI (Korunan Sağlık Bilgisi) / PII'yi maskelemek için varlık tanıma kullanır; tutarlı tokenizasyon (Mesh yaklaşımı) hassas değerleri kod/ilişki semantiğini koruyan kararlı yer tutuculara eşler. Ağ çıkışı: LLM servisleri, yalnızca `api.openai.com`, `api.anthropic.com` vb. beyaz listeye alan özel VPC/VNet alt ağında; diğer tüm gidenleri engelleyin. 2026 olay sürücüsü: tehlikeye atılmış CI/CD kimlik bilgileri aracılığıyla Vercel tedarik zinciri saldırısı, binlerce müşteri dağıtımı boyunca ortam değişkenlerini sızdırdı.

**Tür:** Öğren
**Diller:** Python (stdlib, basit PII-temizleyici + denetim-günlüğü yazıcı)
**Önkoşullar:** Phase 17 · 19 (AI Ağ Geçitleri), Phase 17 · 13 (Gözlemlenebilirlik)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Dört sır-yönetimi anti-kalıbını (VCS'de yapılandırma dosyaları, sabit kodlanmış ortam, e-tablolar, statik anahtarlar) sıralayın ve yerlerine yenilerini sayın.
- AI-ağ geçidi-kasadan-çeker kalıbını 2026 üretim standardı olarak açıklayın.
- Semantiğin hayatta kalması için tutarlı tokenizasyonla (aynı değer → aynı yer tutucu) bir PII temizleyici uygulayın.
- 2026 Vercel tedarik zinciri olayını ve CI/CD kimlik bilgisi hijyeni hakkında öğrettiğini sayın.

## Problem

Bir stajyer API anahtarlarıyla `.env`'yi commit ediyor. Hızla siliyor. Anahtarlar zaten git geçmişinde — GitGuardian taraması yakalıyor, döndürme süreciniz "ekibe Slack gönder, 40 yapılandırma dosyasını güncelle, tüm servisleri yeniden dağıt." 8 saat sonra, servislerinizin yarısı canlı, yarısı dağıtım pencerelerini bekliyor.

Ayrı olarak, kullanıcı prompt'ları "SSN'im 123-45-6789" içeriyor. Prompt OpenAI'a gidiyor. BAA'nız (İş Ortağı Anlaşması — HIPAA uyumlu veri işleme sözleşmesi) var ama iç politikanız iletmeden önce PII'yi maskelemek. Yapmadınız.

Ayrı olarak, EKS kümenizin LLM pod'u herhangi bir internet ana bilgisayarına ulaşabiliyor. Biri saldırgan-kontrollü bir alan adına DNS araması yoluyla veri sızdırıyor. Hiçbir şey engellemedi.

LLM servisleri için güvenlik, üç vektörün tümünü ele almalıdır. Kasa destekli kimlik bilgileri. PII temizleme. Ağ çıkış filtreleme. Denetim günlükleri.

## Kavram

### Merkezi kasa + IAM-rol çekme

**Kasa**: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager. Tek doğruluk kaynağı.

**IAM rolü**: uygulama/ağ geçidi statik anahtar yerine IAM kimliği aracılığıyla kimlik doğrular. Kasa, token ömrü boyunca sırrı döndürür.

**AI-ağ geçidi kalıbı**: ağ geçidi `OPENAI_API_KEY`'i istek zamanında kasadan çeker. Kasada döndürün; sonraki istek yeni anahtarı alır. Yeniden dağıtım yok.

### Döndürme politikası ≤ 90 gün

Tüm API anahtarları, kasa kök token'ları, CI/CD kimlik bilgileri. Mümkün olduğunda otomatik döndürme. Manuel döndürme günlüğe kaydedilir ve izlenir.

### Sır tarama

- **TruffleHog** — commit'lerde regex + entropi.
- **GitGuardian** — ticari, yüksek doğruluk.
- **Gitleaks** — OSS, CI'da çalışır.

Her commit'te çalıştırın. Yeni sır tespit edilirse PR'ı engelleyin.

### Sıfır güven duruşu

- Tüm hesaplarda MFA gerekli.
- SAML/OIDC üzerinden SSO.
- İnce taneli erişim için RBAC (rol tabanlı) veya ABAC (nitelik tabanlı).
- Kısa-ömürlü token'lar (günler değil saatler).
- Cihaz duruşu — yalnızca disk şifrelemesi olan kurumsal cihazlar.

### PII / PHI temizleme

Prompt altyapınızdan ayrılmadan önce:

1. Varlık tanıma (spaCy NER — Adlandırılmış Varlık Tanıma, Presidio, ticari).
2. Eşleşen varlıkları maskele: `"SSN'im 123-45-6789"` → `"SSN'im [SSN_TOKEN_A3F]"`.
3. Tutarlı tokenizasyon (Mesh yaklaşımı): aynı değer, ilişkileri koruyan aynı yer tutucuya eşlenir.
4. LLM yanıtı için isteğe bağlı ters eşleme.

Statik regex filtreleri temel kalıpları yakalar; NER daha fazlasını yakalar. İkisini de kullanın.

### Girdi + çıktı koruyucuları

Girdi: bilinen jailbreak'leri engelle, yasak konular; kullanıcı başına hız sınırı.

Çıktı: sızan sırlar için regex temizleme (API anahtarı kalıpları, red bağlamlarında e-posta kalıpları), politika ihlalleri için sınıflandırıcı.

### Ağ çıkış beyaz listesi

Özel alt ağdaki LLM servisleri:
- Beyaz liste: `api.openai.com`, `api.anthropic.com`, vektör veritabanı uç noktaları, kasa uç noktaları.
- Geri kalan her şey: bırak.
- Yalnızca izin veren çözümleyici (resolver) üzerinden DNS (DNS tünelleme sızdırmasından kaçının).

### Denetim günlüğü

Her LLM çağrısının değişmez günlüğü:

- Zaman damgası.
- Kullanıcı / kiracı.
- Prompt özeti (hash — gizlilik için ham prompt değil).
- Model + versiyon.
- Token sayıları.
- Maliyet.
- Yanıt özeti.
- Koruyucu tetiklemeleri.

Düzenleyici gereksinime göre sakla (SOC 2 1 yıl, HIPAA 6 yıl).

### 2026 Vercel olayı

Tedarik zinciri saldırısı: tehlikeye atılmış CI/CD kimlik bilgileri, binlerce müşteri dağıtımı boyunca ortam değişkenlerini sızdırdı. Ders: CI/CD kimlik bilgileri üretim-eşdeğeridir. Kasada saklayın. Dar kapsamlı. Agresif şekilde döndürün.

### Hatırlamanız gereken sayılar

- Döndürme politikası: ≤ 90 gün.
- Her commit'te tara: TruffleHog / GitGuardian / Gitleaks.
- Vercel 2026: CI/CD kimlik bilgileri tehlikeye atıldı → binlerce müşterinin ortam değişkeni sızdı.
- Denetim günlüğü saklama: SOC 2 = 1 yıl, HIPAA = 6 yıl.

## Kullanım

`code/main.py`, tutarlı tokenizasyonla basit bir PII temizleyici ve yalnızca-ekleme (append-only) bir denetim günlüğü uygular.

## Yaygınlaştırma

Bu ders `outputs/skill-llm-security-plan.md` üretir. Düzenleyici kapsam ve mevcut durum verildiğinde, kasa geçişini, temizleyiciyi, çıkışı, denetim günlüğünü planlar.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Aynı SSN'ye atıfta bulunan iki prompt gönderin. İkisinin de aynı yer tutucu aldığını doğrulayın.
2. OpenAI + Anthropic + Weaviate çağıran bir vLLM-on-EKS dağıtımı için ağ çıkış politikasını tasarlayın.
3. Git geçmişinde 2 yıllık bir anahtar keşfediyorsunuz. Doğru yanıt nedir — anahtarı döndür, geçmişi temizle veya ikisi de? Gerekçelendirin.
4. Denetim günlüğünüz günde 10 GB büyüyor. Saklama katmanlarını tasarlayın (sıcak 30g, ılık 12ay, soğuk 6yıl).
5. Ters-tokenizasyonun (LLM yanıtına gerçek değerleri koyma) yer tutucuları görünür tutmaya kıyasla karmaşıklığa değip değmediğini tartışın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| Kasa | "sır deposu" | Merkezi kimlik bilgisi yönetim servisi |
| IAM rolü | "kimlik tabanlı yetkilendirme" | Uygulamanın üstlendiği rol; kısa-ömürlü kimlik bilgileri döndürür |
| CI/CD için OIDC | "bulut tarafından verilen token'lar" | CI'da statik anahtar yok — OIDC üzerinden kimlik |
| TruffleHog / GitGuardian / Gitleaks | "sır tarayıcıları" | Commit-zamanı sır tespiti |
| RBAC / ABAC | "erişim kontrolü" | Rol tabanlı veya nitelik tabanlı |
| PII temizleme | "veri maskeleme" | Hassas varlıkları kaldır veya tokenleştir |
| Tutarlı tokenizasyon | "kararlı yer tutucular" | Aynı değer → her seferinde aynı token |
| Mesh yaklaşımı | "Mesh tokenizasyonu" | Semantik koruyan tokenizasyon kalıbı |
| Çıkış beyaz listesi | "giden izin listesi" | Yalnızca izin verilen alan adlarına ulaşılabilir |
| Denetim günlüğü | "değişmez tarihçe" | Uyumluluk için yalnızca-ekleme kayıt |

## Ek Okuma

- [Doppler — Gelişmiş LLM Güvenliği](https://www.doppler.com/blog/advanced-llm-security)
- [Portkey — Gizli referanslarla LLM API anahtarlarını yönetme](https://portkey.ai/blog/secret-references-ai-api-key-management/)
- [Datadog — LLM Koruyucu En İyi Uygulamaları](https://www.datadoghq.com/blog/llm-guardrails-best-practices/)
- [JumpServer — Sır Yönetimi En İyi Uygulamaları 2026](https://www.jumpserver.com/blog/secret-management-best-practices-2026)
- [Microsoft Presidio](https://github.com/microsoft/presidio) — PII tespiti ve anonimleştirme.
- [HashiCorp Vault docs](https://developer.hashicorp.com/vault/docs)
