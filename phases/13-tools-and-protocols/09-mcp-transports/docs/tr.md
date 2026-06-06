# MCP Taşıyıcıları — stdio vs Streamable HTTP vs SSE Geçişi

> stdio yerel olarak çalışır, başka bir yerde çalışmaz. Streamable HTTP (2025-03-26) uzak standarttır. Eski HTTP+SSE taşıması kullanımdan kaldırıldı ve 2026 ortasında kaldırılıyor. Yanlış taşımayı seçmek bir geçiş maliyeti demektir; doğru olanı oturum sürekliliği ve DNS yeniden bağlama korumasıyla uzakta barındırılabilir bir MCP sunucusu satın alır.

**Tür:** Öğren
**Diller:** Python (stdlib, Streamable HTTP uç noktası iskeleti)
**Ön koşullar:** Faz 13 · 07, 08 (MCP sunucusu ve istemcisi)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Dağıtım şekline (yerel vs uzak, tek süreç vs filo) göre stdio ile Streamable HTTP arasında seçim yap.
- Streamable HTTP tek uç noktası paternini uygula: istekler için POST, oturum akışı için GET.
- DNS yeniden bağlamayı yenmek için `Origin` doğrulaması ve oturum id anlambilimini zorla.
- Miras HTTP+SSE sunucusunu 2026 ortası kaldırma tarihlerinden önce Streamable HTTP'ye geçir.

## Sorun

İlk MCP uzak taşıması (2024-11) HTTP+SSE'ydi: iki uç noktası, biri istemcinin POST'ları için diğeri sunucudan istemciye akış için bir SSE kanalı. Çalışıyordu. Ayrıca sakarca: oturum başına iki uç noktası, bazı CDN'lerin önünde bozuk önbellekler ve bazı WAF'lerin agresif şekilde sonlandırdığı uzun ömürlü SSE bağlantılarına sert bağımlılık.

2025-03-25 teknik dokümanı bunu Streamable HTTP ile değiştirdi: tek uç noktası, istekler için POST, bir oturum akışı başlatmak için GET, her ikisi de `Mcp-Session-Id` başlığını paylaşır. O zamandan beri inşa edilen veya geçirilen her sunucu Streamable HTTP kullanır. Eski SSE modu kullanımdan kaldırılıyor — Atlassian Rovo 30 Haziran 2026'da kaldırdı; Keboola 1 Nisan 2026'da; kalan kurumsal sunucuların çoğu 2026 sonuna kadar.

Ve stdio hala yerel sunucular için önemlidir. Claude Desktop, VS Code ve her IDE şeklindeki istemci stdio aracılığıyla sunucular başlatır. Doğru zihinsel model: "bu makine için" stdio, "ağ üzerinden" Streamable HTTP. Çapraz geçiş yok.

## Kavram

### stdio

- Çocuk süreç taşıması. İstemci sunucuyu başlatır, stdin/stdout aracılığıyla iletişim kurar.
- Satır başına bir JSON nesnesi. Satır sonu ile sınırlı.
- Oturum id'si yok; süreç kimliği oturumdur.
- Auth gerekmez (çocuk, ebeveynin güven sınırını miras alır).
- Asla uzak sunucular için kullanmayın — tünellemek için SSH veya socat gerekir, o noktada Streamable HTTP kullanın.

### Streamable HTTP

Tek uç noktası `/mcp` (veya herhangi bir yol). Üç HTTP metodunu destekler:

- **POST /mcp.** İstemci bir JSON-RPC mesajı gönderir. Sunucu ya tek bir JSON yanıtı ya da bir veya daha fazla yanıttan oluşan bir SSE akışıyla yanıt verir (toplu yanıtlar ve o istekle ilgili bildirimler için kullanışlı).
- **GET /mcp.** İstemci uzun ömürlü bir SSE kanalı açar. Sunucu bunu sunucudan istemciye istekler (örnekleme, bildirimler, ricada bulunma) için kullanır.
- **DELETE /mcp.** İstemci oturumu açıkça sonlandırır.

Oturumlar, sunucunun ilk yanıtta ayarladığı ve istemcinin sonraki her istekte yinelediği `Mcp-Session-Id` başlığıyla tanımlanır. Oturum id'leri kriptografik olarak rastgele olmalıdır (128+ bit); güvenlik için istemcinin seçtiği id'ler reddedilir.

### Tek uç nokta vs iki

Eski teknik dokümandaki iki uç noktası modu 2026'da hala çağrılabilir — teknik doküman "eski uyumlu" (legacy compatible) olarak beyan eder. Ancak tüm yeni sunucular tek uç noktalı olmalıdır. Resmi SDK'lar tek uç noktalı üretir; yalnızca geçilmemiş bir uzakla konuşurken eski modu kullanın.

### `Origin` doğrulaması ve DNS yeniden bağlama

Tarayıcılar bugün MCP istemcisi değildir, ancak bir saldırgan, kullanıcının yerel MCP sunucusunun dinlediği `localhost:1234/mcp`'ye POST yapması için bir tarayıcıyı ikna eden bir web sayfası oluşturabilir. Sunucu `Origin`'i kontrol etmezse, tarayıcının aynı kaynak (same-origin) politikası onu kurtaramaz çünkü `Origin: http://evil.com` geçerli bir çapraz kaynaktır.

2025-11-25 teknik dokümanı, sunucuların `Origin`'i bir izin listesinde olmayan istekleri reddetmesini_buyurur. İzin listesi genellikle MCP istemci ana bilgisayarını (`https://claude.ai`, `vscode-webview://*`) ve yerel UI'lar için localhost çeşitlerini içerir.

### Oturum id yaşam döngüsü

1. İstemci `Mcp-Session-Id` olmadan ilk isteği gönderir.
2. Sunucu rastgele bir id atar, yanıt başlığında `Mcp-Session-Id` ayarlar.
3. İstemci akış için sonraki tüm isteklerde ve `GET /mcp`'de bu başlığı yineler.
4. Oturum sunucu tarafından iptal edilebilir; istemci sonraki isteklerde 404 görür ve yeniden başlatmalıdır.
5. İstemci temiz kapatma için oturumu açıkça DELETE edebilir.

### Canlı tutma ve yeniden bağlanma

SSE bağlantıları düşer. İstemci aynı `Mcp-Session-Id` ile yeniden GET yaparak yeniden kurar. Sunucu, kesinti sırasında kaçırılan olayları ( makul bir pencereye kadar) kuyruğa almalı ve istemcinin yinelediği `last-event-id` başlığı aracılığıyla tekrar oynatmalıdır.

Faz 13 · 13, uzun süren çalışmaların bile tam oturum yeniden bağlanmasında hayatta kalmasını sağlayan Görevleri (Tasks) kapsar.

### Geriye uyumluluk probu

Hem eski hem de yeni sunucuları desteklemek isteyen bir istemci:

1. `/mcp`'ye POST yapar.
2. Yanıt JSON veya SSE ile `200 OK` ise, bu Streamable HTTP'dir.
3. Yanıt `Content-Type: text/event-stream` ve ikincil bir uç noktaya işaret eden bir `Location` başlığı ile `200 OK` ise, bu eski HTTP+SSE'dir; `Location`'ı takip edin.

### Cloudflare, ngrok ve barındırma

2026'daki üretim uzak MCP sunucuları Cloudflare Workers (MCP Agents SDK ile), Vercel Functions veya konteynerlenmiş Node/Python üzerinde çalışır. Anahtar: barındırmanız SSE GET için uzun ömürlü HTTP bağlantılarını desteklemelidir. Vercel'in ücretsiz katmanı 10 saniyede sınırlıdır ve uygun değildir. Cloudflare Workers süresiz akışları destekler.

### Ağ geçidi birleştirme

Birden fazla MCP sunucusunu bir ağ geçidiyle (Faz 13 · 17) önünüze koyduğunuzda, ağ geçidi oturum id'lerini yeniden yazan ve yukarı akışı çoklu kullanan tek bir Streamable HTTP uç noktasıdır. Araçlar ağ geçidi katmanında birleştirilir; istemci tek bir mantıksal sunucu görür.

### Taşıma hata modları

- **stdio SIGPIPE.** Yazma ortasında çocuk süreç ölümü SIGPIPE fırlatır; sunucular temiz şekilde çıkmalıdır. İstemciler EOF'ı algılamalı ve oturumu ölü olarak işaretlemelidir.
- **HTTP 502 / 504.** Cloudflare, nginx ve diğer proxy'ler yukarı akış başarısızlığında bunları üretir. Streamable HTTP istemcileri kısa bir gecikmeden sonra bir kez yeniden denemelidir.
- **SSE bağlantı düşüşü.** TCP RST, proxy zaman aşımı veya istemci ağ değişikliği akışı kapatır. İstemci `Mcp-Session-Id` ve isteğe bağlı `last-event-id` ile yeniden bağlanarak devam eder.
- **Oturum iptali.** Sunucu bir oturum id'sini geçersizleştirir; istemci sonraki istekte 404 görür. İstemci yeniden el sıkışmalıdır.
- **Saat farkı.** İstemcideki Kaynak-TTL hesaplamaları sunucudan sapar. İstemci sunucu zaman damgalarını yetkili olarak işlemelidir.

### Ne zaman Streamable HTTP'den geçilir

Bazı kurumsal şirketler, kendi ağları içinde gRPC veya mesaj kuyruğu taşıyıcılarının arkasında MCP sunucuları dağıtır. Bu standart dışıdır — MCP'nin teknik dokümanı bunları resmi olarak tanımlamaz. Ağ geçitleri, MCP istemcilerine bir Streamable HTTP yüzeyi sunabilirken dahili olarak gRPC kullanabilir. Dış yüzeyi teknik doküman uyumlu tutun; ağ geçidi çeviriyi sahiplenir.

## Kullan

`code/main.py`, `http.server` (stdlib) kullanarak minimal bir Streamable HTTP uç noktası uygular. `/mcp` üzerinde POST, GET ve DELETE'i ele alır, ilk yanıtta `Mcp-Session-Id` ayarlar, `Origin`'i doğrular ve izin listesinde olmayan kaynaklardan gelen istekleri reddeder. İşleyici Ders 07 notlar sunucusunun dağıtım mantığını yeniden kullanır.

Neye bakılmalı:

- POST işleyicisi JSON-RPC gövdesini okur, dağıtır ve bir JSON yanıtı yazar (tek yanıt varyantı; SSE varyantı yapı olarak benzer).
- `Origin` kontrolü varsayılan `http://evil.example` probunu reddeder ancak `http://localhost`'u kabul eder.
- Oturum id'leri rastgele 128-bit hex stringlerdir; sunucu oturum başına durumu bellekte tutar.

## Sun

Bu ders `outputs/skill-mcp-transport-migrator.md` dosyasını üretir. Bir HTTP+SSE (eski) MCP sunucusu verildiğinde, beceri oturum id sürekliliği, Origin kontrolleri ve geriye uyumlu prob desteğiyle Streamable HTTP'ye geçiş planı üretir.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. `curl` ile bir `initialize` POST edin ve `Mcp-Session-Id` yanıt başlığını gözlemleyin. Header'ı yineleyen ikinci bir istek POST edin ve oturum sürekliliğini doğrulayın.

2. Bir SSE akışı açan bir GET işleyicisi ekleyin. Her beş saniyede bir `notifications/progress` olayı gönderin. Aynı oturum id ile yeniden GET yaparak yeniden bağlanın ve sunucunun bunu kabul ettiğini doğrulayın.

3. `last-event-id` tekrar oynatma mantığını uygulayın. Yeniden bağlandığında, o id'den beri üretilen olayları tekrar oynatın.

4. `Origin` doğrulamasını bir joker (wildcard) kalıbını (`https://*.example.com`) destekleyecek şekilde genişletin ve `https://app.example.com`'u kabul ettiğini ancak `https://evil.example.com.attacker.net`'i reddettiğini doğrulayın.

5. Resmi kayıttan eski bir HTTP+SSE sunucusu alın (birkaç tane var) ve geçişi çizin: uç noktası elemede, oturum id üretiminde ve başlık anlambiliminde ne değişir.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| stdio transport | "Yerel çocuk süreç" | stdin/stdout üzerinden JSON-RPC, satır sonu ile sınırlı |
| Streamable HTTP | "Uzak taşıma" | Tek uç noktalı POST + GET + isteğe bağlı SSE, 2025-03-26 teknik dokümanı |
| HTTP+SSE | "Eski" | 2026 ortasında kaldırılan iki uç noktalı model |
| `Mcp-Session-Id` | "Oturum başlığı" | Sunucu tarafından atanan rastgele id, sonraki her istekte yinelenir |
| `Origin` izin listesi | "DNS yeniden bağlama savunması" | Origin'i onaylı olmayan istekleri reddeder |
| Tek uç nokta | "Tek URL" | `/mcp` tüm oturum işlemleri için POST / GET / DELETE'i ele alır |
| `last-event-id` | "SSE tekrar oynatma" | Düşen bir akışı olay kaçırmadan devam ettirmek için kullanılan başlık |
| Geriye uyumlu prob | "Eski vs yeni algılama" | Otomatik olarak taşımayı seçen istemci yanıt şekli kontrolü |
| Uzun ömürlü HTTP | "SSE akışı" | Sunucu, tek bir TCP bağlantısı üzerinde dakikalarca veya saatlerce olay iter |
| Oturum iptali | "Yeniden başlatmaya zorla" | Sunucu bir oturum id'sini geçersizleştirir; istemci yeniden el sıkışmalıdır |

## İleri Okuma

- [MCP — Basic transports spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) — stdio ve Streamable HTTP için kanonik referans
- [MCP — Basic transports spec 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) — Streamable HTTP'yi tanıtan revizyon
- [Cloudflare — MCP transport](https://developers.cloudflare.com/agents/model-context-protocol/transport/) — Workers-hosted Streamable HTTP paternleri
- [AWS — MCP transport mechanisms](https://builder.aws.com/content/35A0IphCeLvYzly9Sw40G1dVNzc/mcp-transport-mechanisms-stdio-vs-streamable-http) — dağıtım şekilleri arası karşılaştırma
- [Atlassian — HTTP+SSE deprecation notice](https://community.atlassian.com/forums/Atlassian-Remote-MCP-Server/HTTP-SSE-Deprecation-Notice/ba-p/3205484) — somut geçiş tarihi örneği
