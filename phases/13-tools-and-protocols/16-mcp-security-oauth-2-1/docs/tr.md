# MCP Güvenliği II — OAuth 2.1, Kaynak Göstergeleri, Kademeli Kapsamlar

> Uzak MCP sunucuları yalnızca kimlik doğrulama değil, yetkilendirme de ister. 2025-11-25 teknik dokümanı OAuth 2.1 + PKCE + kaynak göstergeleri (RFC 8707) + korumalı-kaynak meta verisi (RFC 9728) ile uyumludur. SEP-835, 403 WWW-Authenticate ile kademeli kapsam onayı ekler. Bu ders, her atlamayı görebilmeniz için adım-artırma akışını bir durum makinesi olarak uygular.

**Tür:** İnşa Et
**Diller:** Python (stdlib, OAuth durum makinesi simülatörü)
**Ön koşullar:** Faz 13 · 09 (taşıyıcılar), Faz 13 · 15 (güvenlik I)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Kaynak sunucusu ile yetkilendirme sunucusu sorumluluklarını ayırt et.
- PKCE-korumalı OAuth 2.1 yetkilendirme kodu akışını yürü.
- Kafa karışıklığı memuru saldırılarını önlemek için `resource` (RFC 8707) ve korumalı-kaynak meta verisini (RFC 9728) kullan.
- Adım-artırma yetkilendirmesini uygula: sunucu daha yüksek bir kapsam isteyen 403 ile yanıt verir; istemci kullanıcının onayını yeniden ister ve yeniden dener.

## Sorun

Erken MCP (2025 öncesi), uzak sunucuları rastgele API anahtarlarıyla veya hiç auth olmadan yayınladı. 2025-11-25 teknik dokümanı, eksiksiz bir OAuth 2.1 profiliyle bu boşluğu kapatır.

Üç gerçek dünya ihtiyacı:

- **Sıradan uzak sunucular.** Kullanıcı, Notion / GitHub / Gmail'ine erişen uzak bir MCP sunucusu yükler. OAuth 2.1 PKCE ile doğru şekildir.
- **Kapsam yükseltmesi.** `notes:read` verilmiş bir notlar sunucusunun belirli bir eylem için `notes:write`'a ihtiyacı olabilir. Tüm akışı yeniden yapmak yerine, adım-artırma (SEP-835) ek kapsamı ister.
- **Kafa karışıklığı memuru önleme.** İstemci, Sunucu A için amaçlanmış bir token tutuyor. Sunucu A kötü niyetli ve token'ı Sunucu B'ye sunmaya çalışıyor. Kaynak göstergeleri (RFC 8707) token'ı hedef kitlesine sabitler.

OAuth 2.1 yeni değil. Yeni olan MCP'nin profili: zorunlu akışlar (yalnızca yetkilendirme kodu + PKCE; örtük yok, varsayılan istemci kimlik bilgileri yok), her token isteğinde zorunlu kaynak göstergeleri ve istemcilerin nereye gideceğini bilmesi için yayımlanan korumalı-kaynak meta verisi.

## Kavram

### Roller

- **İstemci.** MCP istemcisi (Claude Desktop, Cursor vb.).
- **Kaynak sunucusu.** MCP sunucusu (notlar, GitHub, Postgres, her neyse).
- **Yetkilendirme sunucusu.** Token verir. Kaynak sunucuyla aynı hizmet olabilir veya ayrı bir IdP (Auth0, Keycloak, Cognito) olabilir.

MCP'nin profilinde, kaynak ve yetkilendirme sunucuları AYNI ana bilgisayar OLABİLİR ancak URL'lerle AYRILMALIDIR.

### Yetkilendirme kodu + PKCE

Akış:

1. İstemci rastgele bir `code_verifier` ve (SHA256 ile) `code_challenge` üretir.
2. İstemci kullanıcıyı `/authorize?response_type=code&client_id=...&redirect_uri=...&scope=notes:read&code_challenge=...&resource=https://notes.example.com` adresine yönlendirir.
3. Kullanıcı onaylar. Yetkilendirme sunucusu `redirect_uri?code=...` adresine yönlendirir.
4. İstemci `/token?grant_type=authorization_code&code=...&code_verifier=...&resource=...` adresine POST yapar.
5. Yetkilendirme sunucusu, doğrulayıcının hash'ini depolanan challenge ile doğrular ve bir erişim jetonu (access token) verir.
6. İstemci jetonu kullanır: kaynak sunucusuna her istekte `Authorization: Bearer ...`.

PKCE, yetkilendirme kodu yakalama saldırılarını önler. Kaynak göstergeleri, token'ın başka bir yerde geçerli olmasını önler.

### Korumalı-kaynak meta verisi (RFC 9728)

Kaynak sunucusu bir `.well-known/oauth-protected-resource` belgesi yayımlar:

```json
{
  "resource": "https://notes.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "scopes_supported": ["notes:read", "notes:write", "notes:delete"]
}
```

İstemci, yetkilendirme sunucusunu kaynak sunucusundan keşfeder. Yapılandırma azalır — istemcinin yalnızca kaynak URL'sine ihtiyacı vardır.

### Kaynak göstergeleri (RFC 8707)

Token isteğindeki `resource` parametresi, token'ın hedef kitlesini sabitler. Verilen token `aud: "https://notes.example.com"` içerir. Bu token'ı alan başka bir MCP sunucusu `aud`'u kontrol eder ve reddeder.

### Kapsam modeli

Kapsamlar boşlukla ayrılmış stringlerdir. Yaygın MCP kuralları:

- `notes:read`, `notes:write`, `notes:delete`
- `admin:*` yetenek kapasitesi için (dikkatli kullanın)
- `profile:read` kimlik için

Kapsam seçimi en-az-ayrıcalık olmalıdır: şu an gerekli olanı isteyin, daha fazlasına ihtiyacınız olduğunda adım artırın.

### Adım-artırma yetkilendirmesi (SEP-835)

Kullanıcı `notes:read` veriyor. Sonra ajanın bir notu silmesini istiyor. Sunucu şöyle yanıt verir:

```
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope",
    scope="notes:delete", resource="https://notes.example.com"
```

İstemci insufficient_scope hatasını görür, kullanıcıya ek kapsam için bir onay dialogu gösterir, bunun için mini bir OAuth akışı çalıştırır, yeni token ile isteği yeniden dener.

### Token hedef kitlesi doğrulaması

Her istekte: sunucu `token.aud == self.resource_url` kontrol eder. Eşleşmezse = 401. Bu, çapraz sunucu token suistimalini önler.

### Kısa ömürlü tokenlar ve döndürme

Erişim jetonları kısa ömürlü OLMALIDIR (varsayılan 1 saat). Yenileme jetonları (refresh token) her yenilemede döndürülür. İstemci sessiz yenilemeyi arka planda ele alır.

### Token geçirme yok

Örneleme sunucuları (Faz 13 · 11) istemcinin token'ını diğer hizmetlere GEÇİRMEK ZORUNDA DEĞİLDİR. Örnekleme isteği sınırdır.

### Kafa karışıklığı memuru önleme

Token `aud`'a bağlanır. İstemci `client_id`'ye bağlanır. Her istek her ikisine göre doğrulanır. Teknik doküman, MCP öncesi uzak araç ekosistemlerinde yaygın olan eski "token geçirmesi" paternini açıkça yasaklar.

### İstemci ID keşfi

Her MCP istemcisi meta verilerini sabit bir URL'de yayımlar. Yetkilendirme sunucuları, yönlendirme URI'lerini ve iletişim bilgilerini keşfetmek için istemcinin meta veri belgesini okuyabilir. Bu, manuel istemci kaydını ortadan kaldırır.

### Ağ geçitleri ve OAuth

Faz 13 · 17, bir kurumsal ağ geçidinin OAuth'u nasıl ele aldığını gösterir: ağ geçidi yukarı akış sunucuları için kimlik bilgilerini tutar, istemcilere verilen tokenlar ağ geçidi tarafından verilir ve yukarı akış tokenları ağ geçidinden asla çıkmaz. Bu güven modelini tersine çevirir — kullanıcılar ağ geçidine bir kez kimlik doğrulama yapar; ağ geçidi N sunucu yetkilendirmesini ele alır.

## Kullan

`code/main.py`, eksiksiz OAuth 2.1 adım-artırma akışını bir durum makinesi olarak simüle eder. Şunları uygular:

- PKCE code-verifier / challenge üretimi.
- Kaynak göstergesiyle yetkilendirme kodu akışı.
- Korumalı-kaynak meta verisi uç noktası.
- Hedef kitlesi kontrolüyle token doğrulaması.
- `insufficient_scope`'ta adım-artırma.

Bu derste HTTP sunucusu yok; durum makinesi bellekte çalışır, böylece her atlama izlenebilir. Faz 13 · 17'nin ağ geçidi dersi bunu gerçek bir taşıyıcıya bağlar.

## Sun

Bu ders `outputs/skill-oauth-scope-planner.md` dosyasını üretir. Araçlara sahip uzak bir MCP sunucusu verildiğinde, beceri kapsam kümesini, sabitleme kurallarını ve adım-artırma politikasını tasarlar.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. İki kapsamlı adım-artırma akışını izleyin. Adım-artırmada hangi atlamaların tekrarlandığını not edin.

2. Yenileme jetonu döndürmesi ekleyin: her yenileme yeni bir yenileme jetonu verir ve eskisini geçersizleştirir. Çalınmış bir yenileme jetonunun döndürmeden sonra kullanıldığını simüle edin ve başarısız olduğunu doğrulayın.

3. Korumalı-kaynak meta verisi uç noktasını stdlib http.server kullanarak gerçek bir HTTP yanıtı olarak uygulayın. Ders 09'daki /mcp uç noktasını ayna olarak kullanın.

4. Bir GitHub MCP sunucusu için bir kapsam hiyerarşisi tasarlayın: depo oku, PR yaz, PR'ı onayla, PR'ı birleştir, yönetici. Her düzey arasında adım-artırma kullanın.

5. RFC 8707 ve RFC 9728'i okuyun. 9728'deki MCP'nin RFC'nin örneğinden farklı kullandığı alanı belirleyin. (İpucu: `scopes_supported` ile ilgili.)

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| OAuth 2.1 | "Modern OAuth" | PKCE'yi zorunlu kılan ve örtük akışı yasaklayan birleşik RFC |
| PKCE | "Sahiplik kanıtı" | Yetkilendirme kodu yakalama saldırılarını yenen kod doğrulayıcısı + challenge |
| Resource indicator (Kaynak göstergesi) | "Token hedef kitlesi" | Token'ı bir sunucuya sabitleyen RFC 8707 `resource` parametresi |
| Protected-resource metadata | "Keşif belgesi" | RFC 9728 `.well-known/oauth-protected-resource` |
| Step-up authorization | "Kademeli rıza" | İstenen kapsamlar için SEP-835 akışı |
| `insufficient_scope` | "WWW-Authenticate ile 403" | Daha büyük bir kapsam için yeniden onay isteyen sunucu sinyali |
| Confused deputy (Kafa karışıklığı memuru) | "Hizmetler arası token suistimali" | Güvenilir bir taşıyıcının token'ı uygunsuz yönlendirdiği saldırı |
| Short-lived token | "Erişim jetonu TTL" | Hızla sona eren taşıyıcı jetonu; yenileme jetonu yeniler |
| Scope hierarchy | "En-az-ayrıcalık yığını" | Adım-artımalı kademeli kapsam kümesi |
| Client ID metadata | "İstemci keşif belgesi" | İstemcinin kendi OAuth meta verilerini yayımladığı URL |

## İleri Okuma

- [MCP — Authorization spec](https://modelcontextprotocol.io/specification/draft/basic/authorization) — kanonik MCP OAuth profili
- [den.dev — MCP November authorization spec](https://den.dev/blog/mcp-november-authorization-spec/) — 2025-11-25 değişikliklerinin yürüyüşü
- [RFC 8707 — Resource indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707) — hedef kitlesi sabitleme RFC'si
- [RFC 9728 — OAuth 2.0 protected resource metadata](https://datatracker.ietf.org/doc/html/rfc9728) — keşif belgesi RFC'si
- [Aembit — MCP OAuth 2.1, PKCE and the future of AI authorization](https://aembit.io/blog/mcp-oauth-2-1-pkce-and-the-future-of-ai-authorization/) — pratik adım-artırma akışı yürüyüşü
