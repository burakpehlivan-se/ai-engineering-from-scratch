# Üretimde MCP Auth — DCR, JWKS Döndürme, iii Primitifleri Üzerinde Hedef Sabitlenmiş Tokenlar

> Ders 16 OAuth 2.1 durum makinesini bellekte kurmuştu. 2026 itibarıyla gerçek bir kuruluşa sunduğunuz her MCP sunucusu üretim auth'unun arkasında oturur: dinamik istemci kaydı (RFC 7591), yetkilendirme-sunucusu meta verisi keşfi (RFC 8414), 3'te bir token doğrulamasını bozmayan JWKS döndürmesi ve kafa karışıklığı memuru suistimalini reddeden hedef sabitlenmiş tokenlar. Bu ders, her şeyi iii primitifleri aracılığıyla — HTTP ve cron için `iii.registerTrigger`, auth mantığı için `iii.registerFunction`, önbelleklenmiş anahtarlar için `state::set/get` — bağlar, böylece auth yüzeyi, motorun diğer her iş yükü gibi gözlemlenebilir, yeniden başlatılabilir ve tekrar oynatılabilir olur.

**Tür:** İnşa Et
**Diller:** Python (stdlib, ders ortamı için mocklanmış iii primitifleri)
**Ön koşullar:** Faz 13 · 16 (OAuth 2.1 durum makinesi), Faz 13 · 17 (ağ geçitleri)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- RFC 8414 meta verisi aracılığıyla bir yetkilendirme sunucusu keşfet ve sözleşmeyi doğrula.
- MCP istemcilerinin yönetici müdahalesi olmadan kaydolmasını sağlayan RFC 7591 dinamik istemci kaydını uygula.
- Bir cron tetikleyicisi kullanarak JWKS anahtarlarını önbelleğe al ve döndür, böylece imza doğrulaması anahtar yuvarlanmasında hayatta kalır.
- RFC 8707 kaynak göstergeleriyle tokenları tek bir MCP kaynağına sabitle ve kafa karışıklığı memuru suistimalini reddet.
- Her uç noktayı ve arka plan görevini iii primitifleri olarak bağla — HTTP tetikleyicileri, cron tetikleyicileri, adlı fonksiyonlar ve `state::*` okumaları — böylece tek bir yeniden başlatma auth yüzeyini yeniden inşa eder.
- Bir IdP yetenek matrisini oku ve IdP, MCP'nin auth profilini karşılayamıyorsa dağıtıma reddet.

## Sorun

Ders 16 simülatörü OAuth 2.1'i bellekte çalıştırır. Üretimin, yalnızca bellek tabanlı bir simülatörün görmediği üç operasyonel boşluğu vardır.

İlk boşluk kayıttır. Gerçek bir kuruluş yüzlerce MCP sunucusu ve binlerce MCP istemcisi çalıştırır. Operatörler her Cursor kullanıcısını elle bir OAuth istemcisi olarak kaydetmez. RFC 7591 dinamik istemci kaydı, bir istemcinin yetkilendirme sunucusuna `POST /register` yaparak yerinde bir `client_id` (ve isteğe bağlı `client_secret`) almasını sağlar. Sunucu, RFC 8414 meta verisinde `registration_endpoint`'i yayımlar; istemci bunu bant dışı yapılandırma olmadan keşfeder.

İkinci boşluk anahtar döndürmesidir. JWT doğrulaması, yetkilendirme sunucusunun imza anahtarlarına bağlıdır, bunlar bir JSON Web Key Set (JWKS) olarak yayımlanır. Yetkilendirme sunucusu bunları programlı olarak döndürür (genellikle saatlik, bazen olay müdahalesi altında daha hızlı). Bir MCP sunucusu JWKS'yi bir kez yükleme zamanında çekerse, döndürme penceresine kadar iyi doğrulayır — ardından yeniden başlatılana kadar her istek başarısız olur. Üretim, JWKS'yi bir refresh göreviyle önbelleklenmiş bir değer olarak bağlar, önceki anahtarlar süresi dolmadan önbelleği üzerine yazar ve önbellek eksikliğinde imzası önbellekten daha yeni bir anahtarla imzalanmış bir token geldiğinde bir düşüş yolu (fall-back) olarak senkron çeker.

Üçüncü boşluk hedef kitlesi bağlamasıdır. Ders 16 RFC 8707 kaynak göstergelerini tanıttı. Üretimde bu gösterge, her istekte bir sert kimlik kontrolü haline gelir. MCP sunucusu `token.aud`'u kendi kanonik kaynak URL'siyle karşılaştırır ve eşleşmeyenleri HTTP 401 ile reddeder. Bu, yukarı akıştaki bir MCP sunucusunun (veya bir sunucu için tasarlanmış bir token tutan kötü niyetli bir istemcinin) aynı güven ağ içindeki başka bir sunucuya o token'ı yeniden oynatmasına karşı tek savunmadır.

Bu ders, bu boşlukların her birini bir iii primitifi olarak ele alır. Meta veri belgesi, bir fonksiyonun çıktısını döndüren bir HTTP tetikleyicisidir. JWKS döndürmesi, `state::set("auth/jwks/<issuer>", ...)` yazan `auth::rotate-jwks` çağıran bir cron tetikleyicisidir. JWT doğrulaması, başkalarının `iii.trigger("auth::validate-jwt", token)` ile çağırdığı bir fonksiyondur. MCP sunucusu kendi başına yalnızca bir HTTP tetikleyicisidir ve dağıtımdan önce doğrulamaya girer. Motoru yeniden başlatın: tetikleyici kaydı yeniden inşa edilir; durum hayatta kalır; auth yüzeyi manuel uzlaşma olmadan çalışır haldedir.

## Kavram

### RFC 8414 — OAuth Yetkilendirme Sunucusu Meta Verisi

`/.well-known/oauth-authorization-server`'daki bir belge, istemcinin ihtiyaç duyduğu her şeyi tanımlar:

```json
{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
  "registration_endpoint": "https://auth.example.com/register",
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "scopes_supported": ["mcp:tools.read", "mcp:tools.invoke"],
  "token_endpoint_auth_methods_supported": ["none", "private_key_jwt"]
}
```

Bir MCP kaynağı URL'si verilen istemci keşif zincirini takip eder: RFC 9728'den `oauth-protected-resource` (kaynak sunucusunun belgesi) yayımcıyı isimlendirir, ardından `oauth-authorization-server` (bu RFC) her uç noktayı isimlendirir. İstemci asla bir yetkilendirme URL'sini kodlamaz.

MCP için bir IdP'ye güvenden önce doğruladığınız sözleşme:

- `code_challenge_methods_supported` `S256` içerir (RFC 7636'e göre PKCE).
- `grant_types_supported` `authorization_code` içerir ve `password` ve `implicit`'i reddeder.
- `registration_endpoint` mevcuttur (RFC 7591 desteği).
- `response_types_supported` OAuth 2.1 için tam olarak `["code"]`'dir.

Bunlardan herhangi biri eksikse, MCP sunucusu bu IdP'ye karşı dağıtıma reddeder. Dağıtım manifestosu yanlıştır, kod değil.

### RFC 9728 (özet) — Korumalı Kaynak Meta Verisi

Ders 16 RFC 9728'i kapsadı. Üretimdeki fark: bu belge, istemcinin *bu* MCP sunucusunun güvendiği yetkilendirme sunucularını bulmak için baktığı tek yerdir. Tek bir MCP sunucusu birden fazla IdP'den token kabul edebilir (biri çalışanlar, biri ortaklar). RFC 9728 bu kümesi beyan eder; RFC 8414 her IdP'nin ne desteklediğini belgeler.

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com", "https://partners.example.com"],
  "scopes_supported": ["mcp:tools.invoke"],
  "bearer_methods_supported": ["header"],
  "resource_documentation": "https://notes.example.com/docs"
}
```

### RFC 7591 — Dinamik İstemci Kaydı

DCR olmadan, her MCP istemcisi (Cursor, Claude Desktop, özel bir ajan) IdP yöneticisiyle bant dışı bir değişim gerektirir. DCR ile istemci POST yapar:

```json
POST /register
Content-Type: application/json

{
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none",
  "scope": "mcp:tools.invoke",
  "client_name": "Cursor",
  "software_id": "com.cursor.cursor",
  "software_version": "0.42.0"
}
```

Sunucu `client_id` ve sonraki güncellemeler için bir `registration_access_token` ile yanıt verir:

```json
{
  "client_id": "c_3e7f1a",
  "client_id_issued_at": 1769472000,
  "redirect_uris": ["http://127.0.0.1:7333/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "registration_access_token": "regt_b2...",
  "registration_client_uri": "https://auth.example.com/register/c_3e7f1a"
}
```

`token_endpoint_auth_method: none`, kullanıcının cihazında çalışan MCP istemcileri için doğru varsayılandır. Yalnızca `client_id` alırlar — sızdırılacak `client_secret` yoktur. PKCE, genel istemcinin ihtiyaç duyduğu sahiplik kanıtını sağlar.

Üç üretim tuzağı:

- Kayıt uç noktası kaynak IP'sine göre hız sınırlamalıdır. Bunun olmadan, düşmanca bir aktör milyonlarca sahte kayıt betiği yazarak `client_id` ad前三refixini tüketir. iii bunu basit hale getirir: kayıt HTTP tetikleyicisi, kayıt memuruna dağıtımdan önce `auth::rate-limit` fonksiyonunu çağırır.
- Bazı kurumsal IdP'ler `software_statement`'ı (istemci için kefil olan imzalanmış bir JWT) ister. Dersin mock'u bunu atlar; üretim, localhost dışı redirect URI'lerinden gelen imzasız kayıtları reddeden bir doğrulama adımı bağlar.
- `registration_access_token` düz metin yerine hash olarak saklanmalıdır. Bu jetonun çalınması, saldırganın istemcinin redirect URI'lerini yeniden yazabileceği anlamına gelir.

### RFC 8707 (özet) — Kaynak Göstergeleri

Ders 16 shape'i oluşturdu. Üretim kuralı: her token isteği `resource=<canonical-mcp-url>` içerir ve MCP sunucusu her çağrıda `token.aud`'un kendi kaynak URL'siyle eşleştiğini doğrular. MCP sunucusu `https://notes.example.com/mcp` üzerinden erişilebilirse, kanonik URL `https://notes.example.com`'dur — bileşen yolu, tek bir sunucunun birden fazla yolu tek bir hedef kitlesi altında barındırabilmesi için hariç tutulur.

### RFC 7636 (özet) — PKCE

PKCE, OAuth 2.1'de zorunludur. Dersin yetkilendirme kodu akışı her zaman `code_challenge` ve `code_verifier` taşır. Sunucu, doğrulayıcısı olmayan veya doğrulayıcısı depolanan challenge'a hash'lenmeyen her token isteğini reddeder.

### MCP Teknik Dokümanı 2025-11-25 Auth Profili

MCP teknik dokümanı (2025-11-25), bir MCP sunucusunun yetkilendirme katmanının ne yapması gerektiğinde hassastır:

- `/.well-known/oauth-protected-resource` (RFC 9728) yayımlayın.
- Tokenları yalnızca `Authorization: Bearer ...` aracılığıyla kabul edin.
- Her istekte `aud`, `iss`, `exp` ve gerekli kapsamları doğrulayın.
- Her 401 ve 403'te `Bearer error=...` taşıyan `WWW-Authenticate` ile yanıt verin; uygulanabilir yerlerde `scope=` ve `resource=` parametrelerini dahil edin.
- `aud`'u kanonik kaynakla eşleşmeyen tokenları reddedin.
- `iss`'i korumalı-kaynak meta verisinin `authorization_servers` listesinde olmayan tokenları reddedin.

OAuth 2.1 taslağı temeldir; RFC 8414/7591/8707/9728 + RFC 7636 yüzeydir; MCP teknik dokümanı profildir.

### IdP yetenek matrisi

Her IdP tam MCP profilini desteklemez. Aşağıdaki matris, 2025-11-25 teknik dokümanına göre fiiliyet yetenek beyanlarını belgeler. Bu bir *dağıtım kapısı*dır, bir tavsiye değildir.

| IdP kategorisi | RFC 8414 meta | RFC 7591 DCR | RFC 8707 kaynak | RFC 7636 S256 PKCE | Notlar |
|---|---|---|---|---|---|
| Kendi barındıran (Keycloak) | evet | evet | evet (24.x'ten beri) | evet | Bu derste MCP profili için referans IdP; her RFC'yi uçtan uca destekler. |
| Kurumsal SSO (Microsoft Entra ID) | evet | evet (premium katmanlar) | evet | evet | DCR kullanılabilirliği kiracı katmanına göre değişir; dağıtımdan önce hedef kiracıda doğrulayın. |
| Kurumsal SSO (Okta) | evet | evet (Okta CIC / Auth0) | evet | evet | DCR Auth0'da (şimdi Okta CIC) mevcut; klasik Okta kuruluşları yönetici ön-kaydı gerektirir. |
| Sosyal giriş IdP'leri (genel) | değişir | nadiren | nadiren | evet | Çoğu sosyal IdP istemcileri statik ortak olarak ele alır; DCR'ye güvenmeyin. Yalnızca kimlik kaynağı olarak kullanın, kendi MCP-farkındalıklı yetkilendirme sunucunuzu üzerine katmanlandırın. |
| Özel / ev yapımı | bağımlı | bağımlı | bağımlı | bağımlı | Kendi sunucunuzu yayınlıyorsanız, tam profili yayınlayın. Yukarıdaki dört RFC'den herhangi birini atlamak MCP auth sözleşmesini bozar. |

Dağıtım manifestosu için ret kuralı: seçilen IdP `registration_endpoint` döndürmüyorsa ve `code_challenge_methods_supported`'ta `S256` listelemiyorsa, MCP sunucusu başlatmayı reddeder. Düşürülmüş mod yoktur.

### iii ile JWKS döndürme paterni

Üretim hata modu bayat bir JWKS önbelleğidir. Bir cron tetikleyicisi ve bir `state::*` önbelleğiyle çözün:

```python
iii.registerTrigger(
    "cron",
    {"schedule": "0 */6 * * *", "name": "auth::jwks-refresh"},
    "auth::rotate-jwks",
)
```

Her altı saatte bir, cron tetikleyicisi `<issuer>/.well-known/jwks.json`'ı çeken ve `state::set("auth/jwks/<issuer>", {keys, fetched_at})` yazan `auth::rotate-jwks`'i çağırır. Doğrulayıcı `state::get`'ten okur. `kid`'i önbellekte eksik olan bir token, düşüş olarak senkron bir `auth::rotate-jwks` çağrısı tetikler. Bu iki durumu birden çözer: zamanlanmış döndürme (cron) ve anahtar-buluşma pencereleri (senkron düşüş).

### iii primitif bağlaması (bu dersin aslında ele aldığı kısım)

Beş primitif auth yüzeyini bir araya getirir:

```python
# 1. RFC 8414 meta veri belgesi
iii.registerTrigger("http", {"path": "/.well-known/oauth-authorization-server", "method": "GET"}, "auth::serve-asm")

# 2. RFC 7591 dinamik istemci kaydı
iii.registerTrigger("http", {"path": "/register", "method": "POST"}, "auth::register-client")

# 3. Çağrılabilir fonksiyon olarak JWT doğrulaması (kaynak sunucusu tetikler)
iii.registerFunction("auth::validate-jwt", validate_jwt_handler)

# 4. Kademeli kapsam için adım-artırma verme (Ders 16'dan SEP-835)
iii.registerFunction("auth::issue-step-up", issue_step_up_handler)

# 5. Cron-driven JWKS döndürmesi
iii.registerTrigger("cron", {"schedule": "0 */6 * * *"}, "auth::rotate-jwks")
iii.registerFunction("auth::rotate-jwks", rotate_jwks_handler)
```

MCP sunucusu kendi başına doğrulamayı doğrudan çağırmaz. Şunu yapar:

```python
result = iii.trigger("auth::validate-jwt", {"token": bearer_token, "resource": self.resource})
if not result["valid"]:
    return {"status": 401, "WWW-Authenticate": result["www_authenticate"]}
```

Bu dolaylılık iii bahsidir. Yarın doğrulayıcıyı paralel olarak iki IdP'ye danışan bir fanout ile değiştirirsiniz veya bir aralık (span) üretici eklersiniz veya olumlu doğrulamaları önbelleğe alırsınız. MCP sunucusu değişmez.

### Hedef kitlesi bağlamasıyla kafa karışıklığı memuru yürüyüşü

Sunucu A (`notes.example.com`) ve Sunucu B (`tasks.example.com`) her ikisi de aynı yetkilendirme sunucusuna kayıtlıdır. Sunucu A ele geçirilmiştir. Saldırgan bir kullanıcının notlar jetonunu alır ve Sunucu B'ye yeniden oynatır.

Sunucu B'nin doğrulayıcısı:

1. JWT'yi kod çöz, `kid` ile JWKS'yi çek, imzayı doğrula.
2. `iss`'i korumalı-kaynak meta verisinin `authorization_servers`'ine göre kontrol et. (Geçti — aynı IdP.)
3. `aud == "https://tasks.example.com"` kontrol et. (Başarısız — token'ın `aud`'u `https://notes.example.com`.)
4. `WWW-Authenticate: Bearer error="invalid_token", error_description="audience mismatch"` ile 401 döndür.

Hedef kitlesi iddiası, bu saldırıya karşı protokol katmanındaki tek savunmadır. Performans için bunu atlamak en yaygın üretim hatasıdır; doğrulayıcı yalnızca oturum başlangıcında değil, her istekte çalışmalıdır.

### Hata modları

- **Bayat JWKS.** Doğrulayıcı anahtar döndürmesinden sonra geçerli tokenları reddeder. Çözüm yukarıdaki cron+düşüş paternidir. JWKS'yi asla bir refresh görevi olmadan önbelleğe almayın.
- **Eksik `aud` iddiası.** Bazı IdP'ler token isteğinde `resource` mevcut olmadıkça `aud`'u atlamayı varsayır. Doğrulayıcı eksik `aud`'lu tokenları reddetmeli, yokluğu joker olarak işlememelidir.
- **Kapsam yükseltme yarışı.** Aynı kullanıcı için eşzamanlı iki adım-artırma akışı da başarılı olabilir ve farklı kapsamlara sahip iki erişim jetonu üretebilir. Doğrulayıcı istek üzerinde sunulan token'ı kullanmalıdır, "kullanıcının mevcut kapsamını" aramamalıdır — bu bir TOCTOU penceresi yaratır.
- **Kayıt jetonu hırsızlığı.** Sızdırılmış bir `registration_access_token`, saldırganın redirect URI'lerini yeniden yazmasına olanak tanır. Bunları depolamada hash'leyin; istemciden her güncellemede düz metni sunmasını isteyin; şüpheli durumda döndürün.
- **`iss` sabitlenmemiş.** Herhangi bir `iss`'i kabul eden bir doğrulayıcı, saldırganın kendi yetkilendirme sunucusunu kurmasına, hedef kitle için bir istemci kaydetmesine ve token vermesine olanak tanır. Korumalı-kaynak meta verisinin `authorization_servers` listesi izin listesidir; zorlayın.

## Kullan

`code/main.py`, stdlib Python ve `iii.registerFunction`, `iii.registerTrigger`, `iii.trigger`, `state::set/get`'i taklit eden küçük bir `iii_mock` kaydıyla tam üretim akışını yürüyerek gösterir. Akış:

1. Yetkilendirme sunucusu `/.well-known/oauth-authorization-server`'da RFC 8414 meta verisini yayımlar.
2. MCP istemcisi meta veri uç noktasını çağırır, kayıt uç noktasını keşfeder.
3. MCP istemcisi `/register`'e POST yapar (RFC 7591) ve bir `client_id` alır.
4. MCP istemcisi `resource` göstergesi (RFC 8707) ile PKCE-korumalı yetkilendirme kodu akışı çalıştırır (RFC 7636).
5. MCP istemcisi MCP sunucusunda `Authorization: Bearer ...` ile bir araç çağırır.
6. MCP sunucusu `auth::validate-jwt` tetikler, bu JWKS'yi `state::get`'ten okur.
7. Cron tetikleyicisi `auth::rotate-jwks`'i tetikler, state'deki JWKS'yi değiştirir.
8. Sonraki çağrı yeni anahtarlara göre yeniden başlatma olmadan doğrulanır.
9. Farklı bir MCP kaynağına yönelik bir kafa karışıklığı memuru denemesi, hedef kitlesi uyumsuzluğuyla 401 alır.

Buradaki mock JWT, yalnızca stdlib ile çalışması için ortak gizli anahtarla (shared secret) HS256 kullanır (ders yalnızca stdlib ile çalışsın). Üretim, yukarıdaki JWKS paterniyle RS256 veya EdDSA kullanır; doğrulama mantığı aksi halde aynıdır.

## Sun

Bu ders `outputs/skill-mcp-auth-iii.md` dosyasını üretir. Bir MCP sunucusu yapılandırması ve bir IdP yetenek kümesi verildiğinde, beci kaydedilecek iii primitiflerini, JWKS döndürme zamanlamasını, kapsam eşlemesini ve IdP tam RFC profilini desteklemediğinde uygulanacak ret kurallarını üretir.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. 9 adımlı akışı izleyin. `state::get`'in `auth::rotate-jwks` üzerine yazmadan hemen önce bayat veri döndürdüğü yeri ve sonraki isteğin artık yeni anahtara göre nasıl doğrulandığını not edin.

2. Korumalı-kaynak meta verisinin `authorization_servers` listesine yeni bir IdP ekleyin. Yeni IdP ile imzalanmış bir token verin ve doğrulayıcının bunu kabul ettiğini doğrulayın. Listelenmemiş bir IdP ile imzalanmış bir token verin ve doğrulayıcının `WWW-Authenticate: Bearer error="invalid_token", error_description="iss not allowed"` ile reddettiğini doğrulayın.

3. `auth::rate-limit`'i bir iii fonksiyonu olarak uygulayın ve kayıt HTTP tetikleyicisi içinde kayıt memurundan önce çağrılmasını sağlayın. Kaynak IP başına tutulan `state::set("auth/ratelimit/<ip>", ...)` ile bir token kovası kullanın.

4. RFC 7591'i okuyun ve dersin `/register` işleyicisinin doğrulamadığı iki alanı belirleyin. Doğrulamayı ekleyin. (İpucu: `software_statement` ve `redirect_uris` URI şeması.)

5. MCP teknik dokümanı 2025-11-25 yetkilendirme bölümünü okuyun. Dersin doğrulayıcısının şu anda üretmediği, `WWW-Authenticate` başlıklarıyla ilgili bir normatif gereklilik bulun. Ekleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| ASM | "OAuth meta veri belgesi" | RFC 8414 `/.well-known/oauth-authorization-server` JSON'u |
| DCR | "Kendi hizmetinde istemci kaydı" | RFC 7591 `POST /register` akışı |
| JWKS | "JWT doğrulaması için herkese açık anahtarlar" | `jwks_uri`'den çekilen, `kid` ile indekslenen JSON Web Key Set |
| Resource indicator | "Hedef kitlesi parametresi" | Token'ı bir sunucuya sabitleyen RFC 8707 `resource` parametresi |
| `aud` iddiası | "Hedef kitlesi" | Doğrulayıcının kanonik kaynak URL'sine göre karşılaştırdığı JWT iddiası |
| Confused deputy | "Token yeniden oynatma" | Sunucu A için verilen tokenın Sunucu B'ye sunulduğu saldırı |
| `iss` izin listesi | "Güvenilen yetkilendirme sunucuları" | Korumalı-kaynak meta verisinin `authorization_servers`'inde belirtilen küme |
| Key rotation | "JWKS döndürme" | Buluşma pencereleriyle imza anahtarlarının periyodik olarak değiştirilmesi |
| Public client | "Yerel veya tarayıcı istemcisi" | `client_secret`'i olmayan OAuth istemcisi; PKCE telafi eder |
| `WWW-Authenticate` | "401/403 yanıt başlığı" | İstemci kurtarmasını yönlendiren `Bearer error=...` direktiflerini taşır |

## İleri Okuma

- [MCP — Authorization spec (2025-11-25)](https://modelcontextprotocol.io/specification/draft/basic/authorization) — bu dersin uyguladığı MCP auth profili
- [RFC 8414 — OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414) — keşif sözleşmesi
- [RFC 7591 — OAuth 2.0 Dynamic Client Registration Protocol](https://datatracker.ietf.org/doc/html/rfc7591) — DCR
- [RFC 7636 — Proof Key for Code Exchange (PKCE)](https://datatracker.ietf.org/doc/html/rfc7636) — genel istemci sahiplik kanıtı
- [RFC 8707 — Resource Indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) — hedef kitlesi sabitleme
- [RFC 9728 — OAuth 2.0 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728) — kaynak sunucusu keşfi
- [OAuth 2.1 draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1) — birleşik OAuth temeli
