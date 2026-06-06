---
name: oauth-scope-planner
description: Bir remote MCP server için OAuth 2.1 scope kümesini, pinning kurallarını ve step-up policy'sini tasarla.
version: 1.0.0
phase: 13
lesson: 16
tags: [oauth, pkce, resource-indicators, step-up, sep-835]
---

Bir tool listesine sahip remote MCP server verildiğinde, authorization modelini tasarla.

Şunları üret:

1. Scope hiyerarşisi. Kademeli scope kümesi (örn. `read` -> `write` -> `delete` -> `admin`). Operation sınıfı başına bir scope; scope kümesini patlatma.
2. Scope-to-tool eşlemesi. Her tool, gereken scope'u ile birlikte annote edilmiş. Birden fazla scope'a ihtiyaç duyan herhangi bir tool'u işaretle.
3. Step-up policy. Hangi operation'ların başlangıç onayı yerine step-up gerektireceği. Tipik olarak: yıkıcı operation'lar step-up gerektirir.
4. Resource indicator değeri. `resource` parametresinde kullanılan kanonik URL. URL'in `.well-known/oauth-protected-resource` resource alanıyla eşleştiğinden emin ol.
5. Protected-resource metadata. `authorization_servers`, `scopes_supported` ve `resource` içeren `.well-known/oauth-protected-resource` JSON taslağı.

Sert reject sebepleri:
- Admin scope gerektiren ama açık bir confirmation dialog olmadan çağrılan herhangi bir tool. Step-up gerektirir.
- Birden fazla operation sınıfını kapsayan herhangi bir scope. Privilege creep.
- Audience doğrulamasını atlayan herhangi bir server. Confused-deputy güvenlik açığı.

Refusal kuralları:
- Server yerel ise (stdio), OAuth'u reddet ve stdio'nun parent trust'ı miras aldığını belirt.
- Server, legacy OAuth 2.0 implicit flow'a bağımlıysa, reddet ve 2.1 + PKCE'ye geçişi zorunlu kıl.
- Kullanıcı parolasız "sadece API key" auth isterse, remote server'lar için reddet; kullanıcı yetkili erişim için resource indicator'larla birlikte OAuth 2.1 authorization code + PKCE'yi gerekli kıl. Client credentials yalnızca kullanıcı delegasyonu olmayan makineden-makineye senaryolarda uygundur.

Çıktı: scope hiyerarşisi, scope-to-tool eşlemesi, step-up policy, resource indicator ve protected-resource metadata JSON'u içeren tek sayfalık bir authorization planı. İlk karşılaşmada kullanıcıları en çok şaşırtması muhtemel step-up operation ile bitir.
