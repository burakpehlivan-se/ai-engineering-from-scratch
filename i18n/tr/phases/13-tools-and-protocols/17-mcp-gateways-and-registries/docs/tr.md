# MCP Geçitleri ve Kayıtlar  İşletme Kontrol Uçakları

> Şirketler her geliştiricinin rastgele MCP sunucuları yüklemesine izin veremez. Bir geçit, auth, RBAC, denetim, hız sınırlaması, önbelleği ve araç zehirlenmesi tespitini merkezileştirir, sonra birleşik araç yüzeyini tek bir MCP son noktası olarak ortaya çıkarır. Resmi MCP Kayıt (Anthropic + GitHub + PulseMCP + Microsoft, isim alanı doğrulanmış) kanonik yukarı akımdır. Bu ders bir kapı nerede yer aldığını belirler, minimal bir uygulamayı yürütür ve 2026 satıcı manzarasını araştırır.

**Type:** Learn
**Languages:** Python (stdlib, minimal gateway)
**Prerequisites:** Phase 13 · 15 (tool poisoning), Phase 13 · 16 (OAuth 2.1)
**Time:** ~45 minutes

## Öğrenme Hedefleri

- MCP geçitinin nerede bulunduğunu açıklayın (MCP istemcileri ile birden fazla arka uç MCP sunucuları arasında).
- Beş geçit sorumluluğunu yerine getirmek: auth, RBAC, denetim, oran sınırı, politika.
- Kapı katmanında bir sabitli bir araç-hash manifesti uygulayın.
- Resmi MCP Kayıtını metaregistri (Glama, MCPMarket, MCP.so, Smithery, LobeHub) ile ayırt edin.

## Sorun

Fortune 500'in 30 onaylı MCP sunucusu, 5000 geliştiricisi, uyumluluk ve denetim gereksinimleri ve merkezi bir politika isteyen bir güvenlik ekibi var. Her geliştiricinin kendi IDEs'lerine keyfi sunucuları yüklemesine izin vermek başlangıç değil.

Kapı örneği:

1. Gateway, tek bir Streamable HTTP son nokta geliştiricileri tarafından bağlanır.
2. Gateway, her arka uç MCP sunucusu için kimlik bilgileri tutar.
3. Her geliştiricinin talebi geçitinin kendi OAuth üzerinden doğrulanır ve ölçülür.
4. Gateway, çağrıyı arka uç sunucuya yönlendirir.
5. Tüm aramalar denetim için kaydedildi.

Cloudflare MCP Portalları, Kong AI Gateway, IBM ContextForge, MintMCP, TrueFoundry, Envoy AI Gateway  tüm geçit veya geçit özellikleri 2025-2026 yıllarında gönderildi.

Bu arada, Resmi MCP Kayıtları, kanonik yukarı akım olarak başlatıldı: kurate edilmiş, isim alanı doğrulanmış, geriye dönük DNS adlı sunucular. Geçit çekilebilir. Metaregistri (Glama, MCPMarket, MCP.so, Smithery, LobeHub) birden fazla kaynakta sunucular topluyor.

## Anlaşım

### Beş kapı sorumluluğu

1. **Auth.**2.1 geliştiricini tanımlamak için; kullanıcı rollerini haritalamak için.
2. **RBAC.**Kullanıcı başına politika: hangi sunucular, hangi araçlar, hangi alanlar.
3. **Audit.**Her arama kim, ne, ne zaman sonuçları ile kaydedildi.
4. **Rate limit.**İstifadeden kaçınmak için kullanıcı başına / araç başına / sunucu başına kaplamalar.
5. **Policy.**Zehirli tanımları reddet, ikinci kuralın uygulanması, PII'yi düzenlemek.

### Tek bir son nokta olarak kapı

Geliştiriciler için, geçit bir MCP sunucusu gibi görünür. İçeriden N arka uçlara yönlendirilir. Oturum kimlikleri (Fase 13 · 09) sınırda yeniden yazılır.

### İtirafı kaplama

Geliştiriciler asla arka uç tokenleri görmezler. Giriş kapısı onları tutar (veya kimlik sağlayıcısına temsil eder).`notes:read`geçit kapısı, geçit kapısı'nın kendi arka uç yetenekleri ile not MCP sunucusuna geçici olarak erişebilir  ancak geçit erişimi bağlayan politikalar altında.

### Kapıda alet-hash sıkıştırılması

Giriş kapısı onaylanmış araç tanımlarının bir manifestini (SHA256 hash) içerir.`tools/list`Bu, merkezi olarak uygulanan 13 · 15 aşamasındaki halı çekme savunması.

### Politika kod olarak

Gelişmiş geçitler OPA/Rego, Kyverno veya Styra'da politikayı ifade eder.`alice`Arayabilir .`github.open_pr`Sadece org'da depolamalar için`acme`" açıklama şeklinde kodlanmıştır. Basit geçitler el kodlanmış Python kullanır.

### Oturum farkında yönlendirme

Bir kullanıcı oturumunun bir sunucu karışımı olduğunda, geçit multipleksleri: geliştiricinin tek MCP oturumunda, her sunucu başına bir N arka uç oturumları bulunur.

### Ad alanı birleşimi

Gateways, tüm arka uçlardan araç isim alanlarını birleştirir, genellikle çarpışma üzerine önbellek ile. `github.open_pr`- Evet .`notes.search`Bu yönlendirmeyi netleştirir.

### Kayıtlar

- **Official MCP Registry (`registry.modelcontextprotocol.io`).**Anthropic, GitHub, PulseMCP, Microsoft yönetimi altında başlatıldı.`io.github.user/server`) Temel kalitede önceden filtreli.
- **Glama.**Arama odaklı metaregistri, birçok kaynağı topluyor.
- **MCPMarket.**Satıcı listeleri olan ticari e-postalar.
- **MCP.so.**Topluluk Dizini; açık gönderiler.
- **Smithery.**Paket yöneticisi tarzı kurulum akışı.
- **LobeHub.**LobeChat uygulamasında UI-ye entegre bir kayıt.

Girişim kapıları varsayılan olarak Resmi Kayıttan çekilir, metaregistri'den yöneticiler tarafından kuralı eklemeleri sağlar ve desteklenmeyen herhangi bir şeyi reddeder.

### Ters DNS isimlendirme

Resmi Kayıt , kamu sunucuları için ters DNS isimlerini zorluyor: `io.github.alice/notes`Ad boşlukları, koltukları kapatmayı önler ve güven delegasyonunu daha netleştirir.

### Satıcılar Anketleri, Nisan 2026

| Vendor | Strength |
|--------|----------|
| Cloudflare MCP Portals | Edge-hosted; OAuth integrated; free tier |
| Kong AI Gateway | K8s-native; fine-grained policy; logs to OpenTelemetry |
| IBM ContextForge | Enterprise IAM; compliance; audit export |
| TrueFoundry | DevOps-leaning; metrics-first |
| MintMCP | Developer-platform oriented |
| Envoy AI Gateway | Open-source; customizable filters |

17 (önemli üretim altyapısı) aşama, geçit operasyonlarını daha da derinlemesine araştırıyor.

```figure
t3-gateway-funnel
```

## Kullan

`code/main.py`~ 150 satırda minimum bir geçit gönderir: kullanıcıları sahte bir Bearer token ile kimliklendirir, kullanıcı başına bir RBAC politikası tutar, iki arka uç MCP sunucusuna istekleri yönlendirir, her çağrıyı bir denetim günlüğüne yazar, bir oran sınırı uyguluyor ve açıklaması hash'i sabitlenmiş bir manifest ile eşleşmeyen herhangi bir arka uç aracı reddeder.

Neye bakılır:

- `RBAC`Klavye:`user_id`İzin verilir`server_tool`Girişler.
- `AUDIT_LOG`Sadece eklem olarak yapılan bir olay listesidir.
- Sınır sınırı, kullanıcı başına bir token kova kullanıyor.
- - Bu bir açıklama .`server::tool -> hash`- Evet .

## Gönder

Bu ders bize çok yararlı .`outputs/skill-gateway-bootstrap.md`. Bir kurumsal MCP planı (kullanıcılar, arka planlar, uyumluluk) verildiğinde, beceriler bir geçit yapılandırması spesifikasyonu üretir.

## Egzersizler

1. Çık .`code/main.py`. İzinli kullanıcı olarak, sonra izinsiz kullanıcı olarak, sonra oran sınırının ötesinde bir patlama yapın.

2. Müşteriye dönmeden önce sonuçlardan PII'yi düzenleyen bir politika ekleyin. SSN şeklinde dizilen dizileri için basit bir regex geçit kullanın; boşluğu (e-postalar, telefon numaraları) not edin.

3. OpenTelemetry GenAI alanlarını yaymak için denetim günlüğünü genişlet.

4. 50 geliştiriciden oluşan bir ekip için RBAC politikası tasarlayın ve beş arka plan (not, github, postgres, jira, slack) oluşturun.

5. Cloudflare kurumsal MCP yazısını yukarıdan aşağıya okuyun.

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Gateway | "MCP proxy" | Centralizing server between clients and backends |
| Credential vaulting | "Backend tokens stay server-side" | Developers never see upstream tokens |
| Session-aware routing | "Multi-backend session" | Gateway multiplexes N backend sessions per developer session |
| Tool-hash pinning | "Approved manifest" | SHA256 of every approved tool description; blocks rug-pulls centrally |
| RBAC | "Per-user policy" | Role-based access control for tools and servers |
| Policy-as-code | "Declarative rules" | OPA/Rego, Kyverno, Styra policies enforced at gateway |
| Audit log | "Who, what, when" | Append-only event log for compliance |
| Rate limit | "Per-user token bucket" | Per-minute caps to prevent abuse |
| Official MCP Registry | "Canonical upstream" | `registry.modelcontextprotocol.io`, namespace-verified |
| Reverse-DNS naming | "Registry namespace" | `io.github.user/server` convention |

## Daha Fazla Okumak

- [Official MCP Registry](https://registry.modelcontextprotocol.io/) Kanonik akıntı, isim alanı doğrulanmış
- [Cloudflare — Enterprise MCP](https://blog.cloudflare.com/enterprise-mcp/) OAuth ve politika ile geçit modeli
- [agentic-community — MCP gateway registry](https://github.com/agentic-community/mcp-gateway-registry) Açık kaynaklı referans geçidi
- [TrueFoundry — What is an MCP gateway?](https://www.truefoundry.com/blog/what-is-mcp-gateway) Özellik karşılaştırma makalesi
- [IBM — MCP context forge](https://github.com/IBM/mcp-context-forge)IBM'den kurumsal geçit
