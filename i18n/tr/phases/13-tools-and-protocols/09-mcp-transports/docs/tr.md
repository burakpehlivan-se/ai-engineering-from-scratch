# MCP Transport  stdio vs. Streamable HTTP vs. SSE Migration

> stdio yerel olarak ve başka hiçbir yerde çalışır. Akışlı HTTP (2025-03-26) uzaktan standarttır. Eski HTTP + SSE taşımacılığı eskiye döner ve 2026 yılının ortalarında kaldırılır. Yanlış taşımacılığı seçmek bir göç gerektirir; doğru olanı seçmek, oturma sürekliliği ve DNS yeniden bağlama koruması ile uzaktan barındırılabilir bir MCP sunucusu satın alır.

**Type:** Learn
**Languages:** Python (stdlib, Streamable HTTP endpoint skeleton)
**Prerequisites:** Phase 13 · 07, 08 (MCP server and client)
**Time:** ~45 minutes

## Öğrenme Hedefleri

- Stdio ve Streamable HTTP arasında yerleşim şekli (yerel vs uzak, tek süreç vs. filos) üzerine kurulmuş seçim yapın.
- Akışlanabilir HTTP tek uç noktası örneğini uygulayın: istekler için POST, oturum akışı için GET.
- Yaparım`Origin`DNS-i yeniden incelemek için doğrulama ve seans kimliği semantikleri.
- Eski bir HTTP + SSE sunucusu, 2026'un ortalarında kaldırma süresi gelmeden önce Streamable HTTP'ye göç et.

## Sorun

İlk MCP uzaktan taşıma (2024-11) HTTP+SSE'ydi: iki uç noktası, birisi istemcinin POST'ları için ve birisi sunucu-klient akışı için Server-Sent-Events kanalı. Çalıştı. Aynı zamanda çilekçiydi: her oturumda iki uç noktası, bazı CDN'lerin önünde kırılmış önbelleği ve bazı WAF'lerin saldırgan bir şekilde sona erdirdiği uzun ömürlü SSE bağlantılarına olan güçlü bir bağımlılık.

2025-03-26 spesifikasyonu, Streamable HTTP ile değiştirildi: bir son nokta, müşteri istekleri için POST, oturum akışı oluşturmak için GET, her ikisi de bir `Mcp-Session-Id`Header. O zamandan beri inşa edilen veya göç edilen her sunucu Streamable HTTP kullanıyor. Eski SSE modunun kullanımı sona erdi. Atlassian Rovo 30 Haziran 2026'da kaldırdı; Keboola 1 Nisan 2026'da; kalan çoğu işletme sunucusu 2026'ın sonuna kadar.

Stdio hala yerel sunucular için önemlidir. Claude Desktop, VS Code ve her IDE şeklinde müşteri stdio üzerinden sunucuları doğurur. Doğru zihinsel model: stdio "bu makine" için, Streamable HTTP "ağ üzerinde".

## Anlaşım

### studio

- Çocuk işlemi taşımacılığı. Müşteri sunucuyu doğurur, stdin/stdout üzerinden iletişim kurar.
- Bir satır başına bir JSON nesnesi.
- Oturum kimliği yok; süreç kimliği oturumdur.
- İhtiyacın yok (öğlenme sınırını çocuğun miras alması gerekir).
- Uzak sunucular için asla kullanmayın  tünel için SSH veya socat gerekir, bu noktada Streamable HTTP kullanın.

### Akışlanabilir HTTP

Tek bir son nokta`/mcp`Üç HTTP yöntemi destekler:

- **POST /mcp.**Müşteri bir JSON-RPC mesajı gönderir. Sunucu, ya tek bir JSON cevabı ile veya bir veya daha fazla cevabın SSE akışı ile yanıt verir (bu talebe bağlı toplu yanıtlar ve bildirimler için yararlıdır).
- **GET /mcp.**Client uzun ömürlü bir SSE kanalı açar.Server onu sunucu-klient istekleri (sampling, bildirimler, çağrışmalar) için kullanır.
- **DELETE /mcp.**Müşteri açıkça oturumu sona erdirir.

Oturumlar `Mcp-Session-Id`başlık sunucu ilk yanıt üzerine ayarlar ve istemci sonraki her talebe yankı verir. Oturum kimlikleri kripto olarak rastgele olmalıdır (128+ bit); istemci tarafından seçilen kimlikler güvenlik için reddedilmektedir.

### Tek son nokta vs. iki

Eski özellikten iki uç noktası modunun 2026 yılında hala çağrılabilir olması  özellik "miras uyumlu" olduğunu ilan eder. Ancak tüm yeni sunucular tek uç noktası olmalıdır. Resmi SDK'lar tek uç noktası yayar; sadece göç edilmemiş bir uzaktan bir iletişim kurarken miras modunu kullanın.

### `Origin`Valide ve DNS-i yeniden inceleme

Tarayıcılar MCP müşterileri değil (bugün), ama bir saldırgan bir tarayıcıyı POST'a ikna eden bir web sayfasını oluşturabilir `localhost:1234/mcp` Kullanıcının yerel MCP sunucusunun dinlediği yer.`Origin`, tarayıcı'nın aynı köken politikası onu kaydetmez çünkü `Origin: http://evil.com`geçerli çapraz kökenli.

2025-11-25 spesifikasyonu sunucuların , `Origin`Bu liste genellikle MCP istemci barındırıcısını içerir (`https://claude.ai`- Evet .`vscode-webview://*`) ve yerel kullanıcı arabirimleri için localhost varianları.

### Oturum ID yaşam döngüsü

1. Müşteri ilk talebi olmadan gönderir .`Mcp-Session-Id`- Evet .
2. Sunucu rastgele bir kimlik belirler, setler `Mcp-Session-Id`Cevap başlığı.
3. Müşteri , tüm sonraki talepleri ve `GET /mcp`Akıntı için.
4. Oturum sunucu tarafından iptal edilebilir; müşteri sonraki isteklerde 404'i görür ve yeniden başlatmalıdır.
5. Müşteri açıkça oturumu temiz kapatmak için silmek olabilir.

### Kalıcı ve yeniden bağlan

SSE bağlantıları düşüyor. müşteri aynı ile yeniden GET'e geçerek yeniden kurar `Mcp-Session-Id`. Server , kesinti sırasında kayıp olan olayları sıraya koyacak (makul bir pencerede) ve `last-event-id`Başlık, müşteri yankı veriyor.

13 · 13 aşaması, uzun süreli çalışmaların tam bir oturum yeniden bağlantı kurmasına izin veren Görevleri kapsar.

### Geriye doğru uyumlulık sondası

Eski ve yeni sunucuları desteklemek isteyen bir müşteri:

1. - Evet .`/mcp`- Evet .
2. Eğer cevap `200 OK`JSON veya SSE ile, bu Streamable HTTP.
3. Eğer cevap `200 OK`- Evet .`Content-Type: text/event-stream`Ve bir `Location`başlık ikinci bir son noktaya işaret eder, bu eski HTTP+SSE; `Location`- Evet .

### Cloudflare, ngrok ve hosting

2026 yılında uzaktan MCP sunucuları Cloudflare Workers (MCP Agents SDK'leri ile), Vercel Fonksiyonları veya konteynerleştirilmiş Node / Python üzerinde çalışmaktadır. Anahtar: barındırma işleminiz SSE GET için uzun ömürlü HTTP bağlantıları desteklemesi gerekir. Vercel'in ücretsiz seviyesi 10 saniyelik bir sınırlama yapar ve uygun değildir. Cloudflare Workers belirsiz akışları destekler.

### Kapı bileşimi

Bir kapı (Fase 13 · 17) ile birden fazla MCP sunucusu karşısında, kapı, sesyon kimliklerini ve multipleksleri akıntıya geri yazarak tek bir akış HTTP son noktasıdır. Araçlar kapı katmanında birleştirilir; istemci tek bir mantıklı sunucu görür.

### Nakliye başarısızlık modları

- **stdio SIGPIPE.**Çocuk işlem ölümü yazma ortasında SIGPIPE yükseltir; sunucular temiz çıkmalı. Müşteriler EOF'i tespit etmeli ve seansın ölü olduğunu işaretlemeli.
- **HTTP 502 / 504.**Cloudflare, nginx ve diğer vekiller bunları akıntılı bir başarısızlıkta yayar. Akışlanabilir HTTP istemcileri kısa bir yedeklemeden sonra bir kez tekrar denmelidir.
- **SSE connection drop.**TCP RST, proxy timeout veya istemci ağ değişikliği akışı kapatır.`Mcp-Session-Id`ve seçmeli `last-event-id`Tekrar devam etmek için.
- **Session revocation.**Sunucu bir seans kimliğini geçersiz kılar; müşteri bir sonraki istekle 404 görür. Müşteri tekrar el sıkışmalıdır.
- **Clock skew.**Client'deki kaynak-TTL hesaplamaları sunucudan farklıdır.

### Akışlı HTTP'yi ne zaman atlatmak

Bazı işletmeler, gRPC veya mesaj sırası taşımacılıklarının arkasında MCP sunucularını kendi ağları içinde dağıtır. Bu standart olmayan  MCP'nin spesifikasyonu bunları resmi olarak tanımlamıyor. Gateways, gRPC'yi içsel olarak kullanırken bir Streamable HTTP yüzeyini MCP istemcilerine açığa vurabilir. Dış yüzey spesifikasyonlarına uygun tutun; geçit çevirinin sahibi.

```figure
tp-transport-handshake
```

## Kullan

`code/main.py``http.server`Post, GET ve DELETE'yi işliyor.`/mcp`, setler`Mcp-Session-Id`İlk tepki üzerine onaylar.`Origin`Bu işlemci, ders 07 notları sunucunun gönderme mantığını tekrar kullanır.

Neye bakılır:

- POST işlevi, JSON-RPC vücudu okuyor, gönderir ve JSON cevabını yazar (tek cevap varianti; SSE varianti yapısal olarak benzerdir).
- - Evet .`Origin`kontrol öntanımlıyı reddediyor `http://evil.example`- Sonde ama kabul ediyor .`http://localhost`- Evet .
- Oturum kimlikleri rastgele 128 bit altıbuçlı iplerdir; sunucu, hafızada oturum başına durumunu tutar.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-mcp-transport-migrator.md`HTTP+SSE (meşru) MCP sunucusu verildiğinde, becerin sesyon kimliği sürekliliği, Kaynak kontrolleri ve geriye doğru uyumlu araştırma desteği ile Streamable HTTP'ye göç planı üretilmesi.

## Egzersizler

1. Çık .`code/main.py`- Bir mesaj gönder .`initialize`-`curl`ve `Mcp-Session-Id`Cevap başlığı. Başlığı yankı veren ikinci bir istek gönderin ve oturum devamlılığını doğrulayın.

2. SSE akışını açan bir GET yöneticisi ekle.`notifications/progress`Aynı oturum kimliği ile tekrar bağlantı kurarak ve sunucu tarafından kabul edildiğini onaylayın.

3. `last-event-id`Yeniden bağlantı kurduğunda, bu kimlikten sonra oluşan her olayı tekrar oynat.

4. Uzaklaştırma`Origin`Wildcard modelini desteklemek için onaylama (`https://*.example.com`) ve kabul ettiğini onaylar.`https://app.example.com`Ama reddediyor.`https://evil.example.com.attacker.net`- Evet .

5. Resmi kayıttan eski bir HTTP+SSE sunucusu alın (bir kaç tane var) ve göçü çizin: son nokta işlemesinde, oturum kimliği üretiminde ve başlık semantiğinde neler değişiklikler yapılır.

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| stdio transport | "Local child process" | JSON-RPC over stdin/stdout, newline-delimited |
| Streamable HTTP | "The remote transport" | Single-endpoint POST + GET + optional SSE, 2025-03-26 spec |
| HTTP+SSE | "Legacy" | Two-endpoint model being removed in mid-2026 |
| `Mcp-Session-Id` | "Session header" | Server-assigned random id echoed on every subsequent request |
| `Origin` allowlist | "DNS-rebinding defense" | Reject requests whose Origin is not approved |
| Single endpoint | "One URL" | `/mcp` handles POST / GET / DELETE for all session operations |
| `last-event-id` | "SSE replay" | Header used to resume a dropped stream without missing events |
| Backwards-compat probe | "Old vs new detection" | Client response-shape check that auto-selects transport |
| Long-lived HTTP | "SSE streaming" | Server pushes events for minutes or hours on one TCP connection |
| Session revocation | "Force re-init" | Server invalidates a session id; client must handshake again |

## Daha Fazla Okumak

- [MCP — Basic transports spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) stdio ve Streamable HTTP için kanonik referans
- [MCP — Basic transports spec 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) Streamable HTTP'yi tanıtan düzeltme
- [Cloudflare — MCP transport](https://developers.cloudflare.com/agents/model-context-protocol/transport/) İşçiler tarafından barındırılan Akışlanabilir HTTP kalıpları
- [AWS — MCP transport mechanisms](https://builder.aws.com/content/35A0IphCeLvYzly9Sw40G1dVNzc/mcp-transport-mechanisms-stdio-vs-streamable-http) Deployment şekilleri arasındaki karşılaştırma
- [Atlassian — HTTP+SSE deprecation notice](https://community.atlassian.com/forums/Atlassian-Remote-MCP-Server/HTTP-SSE-Deprecation-Notice/ba-p/3205484) Konkret göç tarihini örnek
