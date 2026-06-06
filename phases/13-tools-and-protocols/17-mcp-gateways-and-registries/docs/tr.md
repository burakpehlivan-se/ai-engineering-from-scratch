# MCP Ağ Geçitleri ve Kayıtları — Kurumsal Kontrol Düzlemleri

> Kurumsal şirketler her geliştiricinin rastgele MCP sunucuları yüklemesine izin veremez. Bir ağ geçidi (gateway), yetkilendirmeyi, RBAC'yi, denetimi, hız sınırlamasını, önbelleğe almayı ve araç zehirleme algılamasını merkezileştirir, ardından birleştirilmiş araç yüzeyini tek bir MCP uç noktası olarak sunar. Resmi MCP Kaydı (Anthropic + GitHub + PulseMCP + Microsoft, ad前三refix doğrulanmış) kanonik yukarı akıştır. Bu ders bir ağ geçidinin nereye oturduğunu isimlendirir, minimal bir uygulamayı yürüyerek gösterir ve 2026 satıcı manzarasını inceler.

**Tür:** Öğren
**Diller:** Python (stdlib, minimal ağ geçidi)
**Ön koşullar:** Faz 13 · 15 (araç zehirleme), Faz 13 · 16 (OAuth 2.1)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Bir MCP ağ geçidinin nerede oturduğunu açıkla (MCP istemcileri ile birden fazla arka plan MCP sunucusu arasında).
- Beş ağ geçidi sorumluluğunu uygula: auth, RBAC, denetim, hız sınırlaması, politika.
- Ağ geçidi katmanında sabitlenmiş araç hash'i manifestosunu zorla.
- Resmi MCP Kaydı ile meta kayıtları (Glama, MCPMarket, MCP.so, Smithery, LobeHub) ayırt et.

## Sorun

Fortune 500 şirketinin 30 onaylanmış MCP sunucusu, 5000 geliştiricisi, uyumluluk ve denetim gereksinimleri ve merkezi politika isteyen bir güvenlik ekibi var. Her geliştiricinin IDE'lerinde rastgele sunucu yüklemesine izin vermek başlangıçtan itibaren imkansız.

Ağ geçidi paterni:

1. Ağ geçidi, geliştiricilerin bağlandığı tek bir Streamable HTTP uç noktası olarak çalışır.
2. Ağ geçidi her arka plan MCP sunucusu için kimlik bilgilerini tutar.
3. Her geliştirici isteği, ağ geçidinin kendi OAuth'u ile kimlik doğrulanır ve kapsamlandırılır.
4. Ağ geçidi çağrıyı politikayı uygulayarak arka plan sunucusuna yönlendirir.
5. Tüm çağrılar denetim için günlüğe kaydedilir.

Cloudflare MCP Portals, Kong AI Gateway, IBM ContextForge, MintMCP, TrueFoundry, Envoy AI Gateway — hepsi 2025-2026'da ağ geçitleri veya ağ geçidi özellikleri yayınladı.

Bu arada, Resmi MCP Kaydı kanonik yukarı akış olarak yayınlandı: seçilmiş, ad前三refix doğrulanmış, ters-DNS adlı sunucular. Meta kayıtlar (Glama, MCPMarket, MCP.so, Smithery, LobeHub) birden fazla kaynaktan sunucuları toplar.

## Kavram

### Beş ağ geçidi sorumluluğu

1. **Auth.** Geliştiriciyi tanımlamak için OAuth 2.1; kullanıcı rollerine eşleme.
2. **RBAC.** Kullanıcı başına politika: hangi sunucular, hangi araçlar, hangi kapsamlar.
3. **Denetim.** Her çağrı kimin, ne zaman, ne yaptığını ve sonucuyla günlüğe kaydedilir.
4. **Hız sınırlaması.** Kullanıcı başına / araç başına / sunucu başına suiistimali önleyen üst sınırlar.
5. **Politika.** Zehirlenmiş açıklamaları reddet, İki Kuralı'nı uygula, Kişisel Bilgi'yi sansürle.

### Ağ geçidi tek uç nokta olarak

Geliştiricilere ağ geçidi tek bir MCP sunucusu gibi görünür. Dahili olarak N arka plana yönlendirir. Oturum id'leri (Faz 13 · 09) sınırla yeniden yazılır.

### Kimlik bilgisi kasası

Geliştiriciler asla arka plan jetonlarını görmez. Ağ geçidi bunları tutar (veya yapan bir kimlik sağlayıcısına proxy yapar). Ağ geçidinde `notes:read`'e sahip bir geliştirici, arka plan kimlik bilgileriyle notlar MCP sunucusuna dolaylı olarak erişebilir — ancak yalnızca dolaylı erişimi bağlayan politika altında.

### Ağ geçidinde araç hash sabitleme

Ağ geçidi onaylanmış araç açıklamalarının (SHA256 hash'leri) bir manifestosunu tutar. Keşif sırasında her arka plan sunucusunun `tools/list`'ini çeker, hash'leri manifestoyla karşılaştırır ve açıklaması değişen her aracı kaldırır. Bu, Faz 13 · 15'teki halı çekme savunmasının merkezi olarak uygulanmasıdır.

### Politika-olarak-kod

İleri düzey ağ geçitleri politikaları OPA/Rego, Kyverno veya Styra'da ifade eder. "`alice` kullanıcısı yalnızca `acme` kuruluşundaki depolarda `github.open_pr` çağırabilsin" gibi kurallar beyanlı olarak kodlanır. Basit ağ geçitleri elle kodlanmış Python kullanır. Her iki şekil de geçerlidir.

### Oturum farkındalıklı yönlendirme

Bir kullanıcının oturumunda karışık sunucular olduğunda, ağ geçidi çoklu kullanıma (multiplex) sokar: geliştiricinin tek MCP oturumu N arka plan oturumu tutar, sunucu başına bir tane. Herhangi bir arka plan bildirimi ağ geçidi aracılığıyla geliştiricinin oturumuna yönlendirilir.

### Ad前三refix birleştirme

Ağ geçitleri tüm arka planlardan araç ad前三refixlerini birleştirir, genellikle çakışmada前三refix ekleyerek. `github.open_pr`, `notes.search`. Bu yönlendirmeyi belirsizsiz yapar.

### Kayıtlar

- **Resmi MCP Kaydı (`registry.modelcontextprotocol.io`).** Anthropic, GitHub, PulseMCP, Microsoft yönetimi altında yayınlandı. Ad前三refix doğrulanmış (ters-DNS: `io.github.user/server`). Temel kalite için önceden filtrelenmiş.
- **Glama.** Arama merkezli, birden fazla kaynağı toplayan meta kayıt.
- **MCPMarket.** Satıcı listeleriyle ticari eğilimli dizin.
- **MCP.so.** Topluluk dizini; açık başvurular.
- **Smithery.** Paket yöneticisi tarzı yükleme akışı.
- **LobeHub.** LobeChat uygulamasındaki UI-entegre kayıt.

Kurumsal ağ geçitleri varsayılan olarak Resmi Kayıt'tan çeker, meta kayıtlardan yönetmen tarafından seçilmiş eklemelere izin verir ve sabitlenmemiş her şeyi redder.

### Ters-DNS adlandırma

Resmi Kayıt, genel sunucular için ters-DNS adları gerektirir: `io.github.alice/notes`. Ad前三refixleri istila önler ve güven devretmeyi netleştirir.

### Satıcı anketi, Nisan 2026

| Satıcı | Güçlü yön |
|--------|----------|
| Cloudflare MCP Portals | Kenar-merkezli; OAuth entegre; ücretsiz katman |
| Kong AI Gateway | K8s-native; ince taneli politika; OpenTelemetry'ye günlük |
| IBM ContextForge | Kurumsal IAM; uyumluluk; denetim dışa aktarımı |
| TrueFoundry | DevOps-eğilimli; metrik-öncelikli |
| MintMCP | Geliştirici platformu odaklı |
| Envoy AI Gateway | Açık kaynak; özelleştirilebilir filtreler |

Faz 17 (üretim altyapısı), ağ geçidi işletme konusunda daha derine dalar.

## Kullan

`code/main.py`, yaklaşık 150 satırda minimal bir ağ geçidi sunar: sahte bir Bearer jetonuyla kullanıcıları doğrular, kullanıcı başına bir RBAC politikası tutar, istekleri iki arka plan MCP sunucusuna yönlendirir, her çağrıyı bir denetim günlüğüne yazar, hız sınırlamasını zorlar ve açıklama hash'i sabitlenmiş bir manifestoyla eşleşmeyen her arka plan aracını reddeder.

Neye bakılmalı:

- `user_id` ile anahtarlanmış ve izin verilen `server_tool` girişlerine sahip `RBAC` dict'i.
- `AUDIT_LOG` eklemeli (append-only) bir olay listesidir.
- Hız sınırlaması kullanıcı başına token kovası (token bucket) kullanır.
- Sabitlenmiş manifesto `server::tool -> hash` dict'idir.

## Sun

Bu ders `outputs/skill-gateway-bootstrap.md` dosyasını üretir. Kurumsal bir MCP planı (kullanıcılar, arka planlar, uyumluluk) verildiğinde, beci bir ağ geçidi yapılandırma teknik dokümanı üretir.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. İzin verilmiş bir kullanıcıyla bir çağrı yapın; ardından izin verilmemiş bir kullanıcıyla; ardından hız-sınırı-aşımı patlamasıyla. Üç akışın da doğrulanmasını sağlayın.

2. Sonuçları istemciye döndürmeden önce Kişisel Bilgi'yi sansürleyen bir politika ekleyin. SSN şeklindeki stringler için basit bir regex geçişi kullanın; eksikliği not edin (e-posta, telefon numaraları).

3. Denetim günlüğünü OpenTelemetry GenAI aralıklarını (span) üretecek şekilde genişletin. Faz 13 · 20 doğru nitelikleri kapsar.

4. Beş arka planlı (notlar, github, postgres, jira, slack) 50 geliştirici için bir RBAC politikası tasarlayın. Her birinde salt okunur olan kim? Kim yazar?

5. Cloudflare kurumsal MCP yazısını baştan sona okuyun. Bu stdlib ağ geçidinin sunmadığı, Cloudflare'nin sunduğu bir özelliği belirleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Gateway (Ağ geçidi) | "MCP proxy" | İstemciler ile arka planlar arasında merkezileştirici |
| Credential vaulting | "Arka plan jetonları sunucu tarafında kalır" | Geliştiriciler yukarı akış jetonlarını asla görmez |
| Session-aware routing | "Çoklu arka plan oturumu" | Ağ geçidi, geliştirici oturumu başına N arka plan oturumunu çoklu kullanıma sokar |
| Tool-hash pinning | "Onaylanmış manifesto" | Her onaylanmış araç açıklamasının SHA256'sı; halı çekmelerini merkezi olarak engeller |
| RBAC | "Kullanıcı başına politika" | Araçlar ve sunucular için rol tabanlı erişim kontrolü |
| Policy-as-code | "Beyanlı kurallar" | OPA/Rego, Kyverno, Styra politikaları ağ geçidinde zorlanır |
| Audit log | "Kim, ne, ne zaman" | Uyumluluk için eklemeli olay günlüğü |
| Rate limit | "Kullanıcı başına token kovası" | Suiistimali önleyen dakika başına üst sınırlar |
| Official MCP Registry | "Kanonik yukarı akış" | `registry.modelcontextprotocol.io`, ad前三refix doğrulanmış |
| Reverse-DNS naming | "Kayıt ad前三refixi" | `io.github.user/server` kuralı |

## İleri Okuma

- [Official MCP Registry](https://registry.modelcontextprotocol.io/) — kanonik yukarı akış, ad前三refix doğrulanmış
- [Cloudflare — Enterprise MCP](https://blog.cloudflare.com/enterprise-mcp/) — OAuth ve politikayla ağ geçidi paterni
- [agentic-community — MCP gateway registry](https://github.com/agentic-community/mcp-gateway-registry) — açık kaynak referans ağ geçidi
- [TrueFoundry — What is an MCP gateway?](https://www.truefoundry.com/blog/what-is-mcp-gateway) — özellik karşılaştırma yazısı
- [IBM — MCP context forge](https://github.com/IBM/mcp-context-forge) — IBM'den kurumsal ağ geçidi
