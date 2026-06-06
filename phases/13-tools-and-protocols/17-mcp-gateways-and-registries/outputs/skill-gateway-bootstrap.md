---
name: gateway-bootstrap
description: Kullanıcılar, backend'ler ve uyumluluk kısıtları verildiğinde bir gateway konfigürasyon spec'i üret.
version: 1.0.0
phase: 13
lesson: 17
tags: [mcp, gateway, rbac, audit, policy]
---

Bir enterprise MCP planı verildiğinde (kullanıcılar, backend'ler, uyumluluk kısıtları), gateway konfigürasyon spec'ini üret.

Şunları üret:

1. Backend listesi. Her biri registry'si (Official / Glama / custom), kanonik ismi (reverse-DNS) ve pinli description hash'leri ile.
2. Kullanıcı listesi. Her biri bir rol ve izin verilen tool kümesiyle.
3. RBAC matrisi. Kullanıcı x backend-tool başına bir satır, allow/deny ile.
4. Rate limit'leri. Kullanıcı başına burst ve sustained limit'ler; pahalı tool'lar için tool başına limit'ler.
5. Audit planı. Log destination (file, OpenTelemetry, SIEM), retention, yakalanan alanlar.

Sert reject sebepleri:
- Açık admin onayı olmadan Official Registry'de olmayan herhangi bir backend.
- Tüm kullanıcılara tüm tool'lara izin veren herhangi bir RBAC kuralı. Privilege patlaması.
- Immutable storage olmayan herhangi bir audit planı. Compliance başarısızlığı.

Refusal kuralları:
- Bir developer popülasyonu hiçbir rol tanımlanmadan 100'ü aşıyorsa, bootstrap etmeyi reddet ve en az üç rol gerektir.
- Plan bir OAuth 2.1 identity provider'ı tanımlamıyorsa, reddet ve önce Keycloak veya Auth0 benimsemeyi öner.
- Herhangi bir backend stdio kullanıyorsa, onu HTTP gateway üzerinden proxy etmeyi reddet; stdio server'lar developer başına yerel çalışır.

Çıktı: backend listesi, kullanıcı listesi, RBAC matrisi, rate limit'leri ve audit planı içeren tek sayfalık bir config dokümanı. Ekibin önce uygulaması gereken tek policy kuralıyla bitir.
