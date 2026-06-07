---
name: mcp-auth-iii-wiring
description: Production MCP authorization'u (RFC 8414, 7591, 8707, 7636 PKCE, 9728) iii primitive'leri üzerine kur — HTTP/cron için registerTrigger, doğrulama için registerFunction, JWKS cache için state::*.
version: 1.0.0
phase: 13
lesson: 18
tags: [mcp, oauth, dcr, jwks, iii, rfc8414, rfc7591, rfc8707, rfc7636, rfc9728]
---

Bir MCP server config'i ve bir IdP capability kümesi verildiğinde, production auth yüzeyini oluşturan iii primitive'lerini ve refusal kurallarını yayınla.

Input'lar:

- `mcp_resource_url` — kanonik resource URL'i (path yok), `aud` olarak ve protected-resource metadata `resource` değeri olarak kullanılır.
- `idp_metadata_url` — IdP'nin `/.well-known/oauth-authorization-server` URL'i.
- `idp_capabilities` — `code_challenge_methods_supported`, `grant_types_supported`, `registration_endpoint`, `response_types_supported` için gözlemlenen değerler.
- `tools` — her birinin gerektirdiği scope ile birlikte MCP tool listesi.

Şunları üret:

1. **Refusal kapısı.** Dört koşuldan herhangi biri başarısız olursa, wiring'i reddet ve dur:
 - `code_challenge_methods_supported`'tan `S256` eksik.
 - `grant_types_supported`'tan `authorization_code` eksik.
 - `registration_endpoint` yok (RFC 7591 DCR yok).
 - `response_types_supported` tam olarak `["code"]` dışında bir şey.

2. **Protected-resource metadata dokümanı** (RFC 9728), MCP server'ın `/.well-known/oauth-protected-resource`'ta yayınlaması için. İçerir: `resource`, `authorization_servers` (issuer allow-list), `scopes_supported`, `bearer_methods_supported: ["header"]`.

3. **iii trigger kayıtları.** Her çağrıyı literal olarak yayınla:
 - `iii.registerTrigger("http", {"path": "/.well-known/oauth-protected-resource", "method": "GET"}, "auth::serve-protected-resource")`
 - `iii.registerTrigger("http", {"path": "/mcp", "method": "POST"}, "mcp::dispatch")` — dispatcher, herhangi bir tool çalışmadan önce `iii.trigger("auth::validate-jwt", ...)` çağırır.
 - `iii.registerTrigger("cron", {"schedule": "<rotation_schedule>"}, "auth::rotate-jwks")` — schedule varsayılan olarak `0 */6 * * *`; yüksek rotasyonlu IdP'ler için `*/15 * * * *`'a sıkılaştır.

4. **iii function kayıtları.** Her çağrıyı literal olarak yayınla:
 - `iii.registerFunction("auth::validate-jwt", handler)` — `iss` allow-list'ini, cached JWKS'e karşı imzayı, `aud == mcp_resource_url`'ı, `exp`'i, gereken scope'u kontrol eder.
 - `iii.registerFunction("auth::rotate-jwks", handler)` — `jwks_uri`'yi fetch eder, `state::set("auth/jwks/<iss>", {keys, fetched_at})` yazar.
 - `iii.registerFunction("auth::serve-protected-resource", handler)` — (2)'deki dokümanı döndürür.
 - `iii.registerFunction("auth::issue-step-up", handler)` — sadece tool listesi, kullanıcının başlangıçta vermediği bir scope arkasına alınmış operation'lar içeriyorsa.

5. **State key planı.** Kabul edilen issuer başına bir key: `{keys, fetched_at}` tutan `auth/jwks/<issuer>`. Read pattern'i belgele: validator `state::get`'ten okur, `kid` miss'inde senkron bir `iii.trigger("auth::rotate-jwks", ...)`'a fallback yapar.

6. **Scope eşlemesi.** Her tool'u gerektirdiği scope'a eşle. Bir tablo çıktıla:
 `| tool | required_scope | rationale |`. Yıkıcı tool'ları kendi scope'ları altında grupla; bir read scope'unu asla bir write tool için yeniden kullanma.

7. **Çalışma zamanı refusal kuralları** (validator bunları kodlamalıdır — handler gövdesinde yayınla):
 - `aud != mcp_resource_url` olduğunda reddet.
 - `iss not in authorization_servers` olduğunda reddet.
 - Tek bir rotation fall-back'ten sonra `kid` cached JWKS'te değilse reddet.
 - Gereken scope eksik olduğunda reddet → 403 `Bearer error="insufficient_scope", scope="<required>", resource="<mcp_resource_url>"`.
 - `code_verifier` veya `resource` parametresi olmayan herhangi bir token isteğini reddet.

Sert reject sebepleri (bunlardan hiçbirini wire etme — isteği reddet ve nedenini belgele):

- iii state store'da `client_secret`'ı plaintext olarak saklamak. Public client'lar `token_endpoint_auth_method: none` kullanır; confidential client'lar `private_key_jwt` kullanır. `state::*`'ta veya registration response log'larında plaintext shared secret yok.
- Validator'da `aud` kontrolünü atlamak. Confused-deputy, RFC 8707 + RFC 9728'in tüm var oluş nedenidir.
- PKCE'siz authorization code request'lerine izin vermek. OAuth 2.1 bunu yasaklar; validator, depolanan authorization-code kaydında `code_challenge` bulunmayan herhangi bir `/token` exchange'ini reddetmelidir.
- Refresh job olmadan JWKS'i cache'lemek. Ya cron trigger gönderilir ya da auth yüzeyi deploy edilmez.
- Allow-list olmadan `iss` claim'ine güvenmek. Herhangi bir `iss`'den token kabul eden herhangi bir validator, bir saldırganın kendi IdP'sini kurup token forge etmesine izin verir.
- `registration_access_token`'ı plaintext olarak saklamak. Hash-at-rest; her güncellemede cleartext talep et.

Çıktı: protected-resource dokümanı, üç `registerTrigger` çağrısı, dört `registerFunction` çağrısı, state key planı, scope eşleme tablosu ve encoded çalışma zamanı refusal kurallarını içeren tek sayfalık bir wiring planı. Seçilen IdP'ye karşı yüzeye çıkması en muhtemel deployment-blocking tek boşlukla bitir — tipik olarak enterprise SSO için DCR mevcudiyeti.
