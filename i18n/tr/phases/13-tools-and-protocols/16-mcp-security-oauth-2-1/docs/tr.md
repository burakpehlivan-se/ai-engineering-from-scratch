# MCP Güvenliği II  OAuth 2.1, Kaynak göstergeler, Gelişmiş kapsamlar

> Uzaktan MCP sunucuları sadece doğrulama değil yetkilidir. 2025-11-25 spesifikasyonu OAuth 2.1 + PKCE + kaynak göstergelerine (RFC 8707) + korunan kaynak metadatalarına (RFC 9728) uyum sağlar. SEP-835 403 WWW-Authenticate'de step-up yetki ile artımsal kapsamlılık onayını ekler. Bu ders step-up akışını bir durum makinesi olarak uyguluyor, böylece her atışını görebilirsiniz.

**Type:** Build
**Languages:** Python (stdlib, OAuth state machine simulator)
**Prerequisites:** Phase 13 · 09 (transports), Phase 13 · 15 (security I)
**Time:** ~75 minutes

## Öğrenme Hedefleri

- Kaynak sunucusu ile yetki sunucu sorumluluklarını ayırt edin.
- PKCE korumalı OAuth 2.1 yetki kod akışını izleyin.
- Kullanım`resource`(RFC 8707) ve korunan kaynak metadataları (RFC 9728) karışıklıklı yardım saldırılarının önlenmesi için.
- Gelişme yetkisi uygulanır: sunucu 403'e WWW-Authenticate ile daha büyük bir kapsam talep eder; istemci kullanıcı onayını tekrar talep eder ve tekrar dener.

## Sorun

Erken MCP (2025) ad-hoc API anahtarları veya hiç bir auth ile uzaktan sunucuları gönderdi. 2025-11-25 spesifikasyonu, bu boşluğu tam bir OAuth 2.1 profiliyle kapatıyor.

Gerçek dünyadaki üç ihtiyaç:

- **Ordinary remote servers.**Kullanıcı, Notion / GitHub / Gmail'ine erişebilen uzaktan bir MCP sunucusu yükler. PKCE ile OAuth 2.1 doğru şekildir.
- **Scope escalation.**Not sunucu veriliyor .`notes:read`Daha sonra ihtiyacın olabilir .`notes:write`Tüm akışı yeniden yapmak yerine, step-up (SEP-835) ek kapsamı talep eder.
- **Confused deputy prevention.**Müşteri, Server A için kitle odaklı bir token tutmaktadır. Server A kötü niyetli ve token'ı Server B'ye sunmaya çalışır. Kaynak göstericileri (RFC 8707) token'i amaçlı kitleye bağlar.

OAuth 2.1 yeni bir şey değil. Yeni olan MCP'nin profili: belirli gerekli akışlar (sadece yetki kodu + PKCE; hiçbir içerikli, varsayılan olarak müşteri kimlikleri yoktur), her token talebi için zorunlu kaynak göstergeler ve müşterilerin nereye gideceğini bilmeleri için yayınlanan korunan kaynak metadataları.

## Anlaşım

### Roller

- **Client.**MCP istemcisi (Claude Desktop, Cursor vb.).
- **Resource server.**MCP sunucusu (notlar, GitHub, Postgres, her neyse).
- **Authorization server.**Kaynak sunucu ile aynı hizmet veya ayrı bir IDP (Auth0, Keycloak, Cognito) olabilir.

MCP'nin profilli, kaynak ve yetki sunucuları aynı barındırma olabilir ancak URL'ler ile ayırt edilmelidir.

### Yetki kodu + PKCE

Akış:

1. Müşteri üretir `code_verifier`(hassasi) ve `code_challenge`(SHA256)
2. Müşteri kullanıcıyı  adresine yönlendirir`/authorize?response_type=code&client_id=...&redirect_uri=...&scope=notes:read&code_challenge=...&resource=https://notes.example.com`- Evet .
3. Kullanıcı onay verdi. yetki sunucusu yönlendiriyor `redirect_uri?code=...`- Evet .
4. Müşteri gönderdi `/token?grant_type=authorization_code&code=...&code_verifier=...&resource=...`- Evet .
5. Yetki sunucu, verifikatörün hashini depolanan zorlukla doğruluyor ve bir erişim jetonu yayınlıyor.
6. Müşteri simgesini kullanıyor: `Authorization: Bearer ...`Kaynak sunucusuna yapılan her talepte.

PKCE yetki kodları kapsamlı saldırıları önler. Kaynak göstergelerleri token'ın başka yerlerde geçerli olmamasını engeller.

### Korunan kaynak metadataları (RFC 9728)

Kaynak sunucusu bir `.well-known/oauth-protected-resource`Belge:

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "scopes_supported": ["notes:read", "notes:write", "notes:delete"]
}
```

Client yetki sunucusunu kaynak sunucusundan keşfeder. Yapılandırmayı azaltır  istemci yalnızca kaynak URL'ine ihtiyaç duyar.

### Kaynak göstericileri (RFC 8707)

`resource`Token istekinde belirtilen parametre, token'ın amaçlı kitlesini işaretler.`aud: "https://notes.example.com"`Bu token çeklerini alan başka bir MCP sunucusu .`aud`Ve onu reddeder.

### Kapsam modeli

Görevi alanlar uzayla ayrılan iplerdir.

- `notes:read`- Evet .`notes:write`- Evet .`notes:delete`
- `admin:*`Admin yetenekleri için (sürekli kullanmak)
- `profile:read`Kimlik için

Sınıf seçimi en az ayrıcalık olmalıdır: ihtiyacınız olanı şimdi isteyin, daha fazlasına ihtiyacınız olduğunda adım atın.

### Gelişme izni (SEP-835)

Kullanıcı yardımları `notes:read`Sonra ajanı bir not silmesini isterler.

```
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
    scope="notes:delete", resource="https://notes.example.com"
```

Müşteri insufficient_scope hatasını görür, kullanıcıya ek kapsam için bir onay diyalogunu sunar, bunun için mini OAuth akışını yapar, talebi yeni jetonla tekrar dener.

### Token izleyicisi doğrulama

Her istek: sunucu kontrolü`token.aud == self.resource_url`Bu, sunucu çapındaki token yeniden kullanımı durdurur.

### Kısa ömürlü tokenler ve dönüşüm

Erişim tokenleri kısa ömürlü olmalıdır (1 saat varsayılan).

### - İşaretli geçit yok.

Örnekleme sunucuları (Fase 13 · 11) müşteri tokenini diğer hizmetlere aktarmamalıdır.

### Karışık Yardımcı Önleme

İşaret bağlanır `aud`Müşteri bağlanır .`client_id`Bu özellik açıkça eski "pass the token" modelini yasaklıyor.

### Müşteri kimliği tespit edilmesi

Her MCP istemcisi metadatalarını sabit bir URL'de yayınlar. Yetki sunucular, istemcinin metadata belgesini yeniden yönlendirme URI'lerini ve iletişim bilgilerini keşfetmek için alabilir. Bu da manuel istemci kayıtlarını kaldırır.

### Geçitler ve OAuth

13 · 17 aşaması bir kurumsal geçitinin OAuth'u nasıl ele aldığını gösterir: geçit yukarıdaki sunucular için kimlik bilgileri tutar, istemciye gelen tokenler geçit tarafından verilir ve yukarıdaki tokenler geçitten asla ayrılmaz. Bu, güven modelini tersine çevirir  kullanıcılar bir kez geçitle kimlik doğruluşu yaparlar; geçit N sunucu yetkileri ele alırlar.

```figure
t3-scope-stepup
```

## Kullan

`code/main.py`OAuth 2.1'in tam yükseltme akışını bir durum makinesi olarak simüle eder.

- PKCE kod doğrulayıcısı / meydan okuma üretimi.
- Yetki kodı kaynak göstergesi ile akış.
- Korunan kaynak metadata son noktası.
- Görev verifiyle onaylanmış.
- İlerleme .`insufficient_scope`- Evet .

Bu derste HTTP sunucusu yoktur; durum makinesi hafızada çalışır, böylece her hop'u izleyebilirsiniz. 13 · 17 aşamasındaki geçit dersi onu gerçek bir taşımacılığa kablolar.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-oauth-scope-planner.md`. Araçlarla birlikte uzaktan bir MCP sunucusu verildiğinde, yetenek alanı, kuralları ve gelişme politikasını tasarlar.

## Egzersizler

1. Çık .`code/main.py`İki boyutlu bir adım atış akışını takip edin.

2. Yenilenme simgesi dönüşümünü ekleyin: Her yenilenme yeni bir yenilenme simgesi çıkarır ve eski birini geçersiz kılar.

3. Korunan kaynak metadata son noktasını stdlib http.server kullanarak gerçek bir HTTP yanıt olarak uygulayın. /mcp son noktasını Ders 09'dan yansıttır.

4. GitHub MCP sunucu için bir kapsam hiyerarşisi tasarlayın: repo okuyun, PR yazın, PR onaylayın, PR birleştirin, admin. Her seviyede step-up kullanın.

5. RFC 8707 ve RFC 9728'i okuyun. 9728'de MCP'nin RFC örneğinden farklı olarak kullandığı bir alanı belirleyin.`scopes_supported`.)

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| OAuth 2.1 | "Modern OAuth" | Consolidated RFC that mandates PKCE and forbids implicit flow |
| PKCE | "Proof-of-possession" | Code verifier + challenge defeating authorization-code interception |
| Resource indicator | "Token audience" | RFC 8707 `resource` parameter pinning token to one server |
| Protected-resource metadata | "Discovery doc" | RFC 9728 `.well-known/oauth-protected-resource` |
| Step-up authorization | "Incremental consent" | SEP-835 flow for adding scopes on demand |
| `insufficient_scope` | "403 with WWW-Authenticate" | Server signal to re-consent for a larger scope |
| Confused deputy | "Token reuse across services" | Attack where a trusted holder forwards a token inappropriately |
| Short-lived token | "Access token TTL" | Bearer that expires quickly; refresh token renews |
| Scope hierarchy | "Least privilege stack" | Graduated scope set with step-up between levels |
| Client ID metadata | "Client discovery doc" | URL at which the client publishes its own OAuth metadata |

## Daha Fazla Okumak

- [MCP — Authorization spec](https://modelcontextprotocol.io/specification/draft/basic/authorization) Kanonik MCP OAuth profili
- [den.dev — MCP November authorization spec](https://den.dev/blog/mcp-november-authorization-spec/) 2025-11-25 değişikliklerinin yürürlükteki geçişi
- [RFC 8707 — Resource indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) Seyircilik RFC
- [RFC 9728 — OAuth 2.0 protected resource metadata](https://datatracker.ietf.org/doc/html/rfc9728) keşif belgesinin RFC
- [Aembit — MCP OAuth 2.1, PKCE and the future of AI authorization](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/) pratik adım atma akışı yürüyüş
