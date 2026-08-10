# Bir MCP Müşteri Oluşturma  Bulma, Çağırma, Oturum Yönetimi

> Çoğu MCP içeriği sunucu öğretim yayınları ve müşterinin el salladı. Müşteri kodu zor orkestrasyonun yaşadığı yerdir: süreç doğurma, kapasite müzakere, birden fazla sunucu arasında araç listesi birleşimi, örnekleme geri çağrıları, yeniden bağlantı ve isim alanı çarpışma çözümü. Bu ders, üç farklı MCP sunucusu ile model için tek düz bir araç isim alanına yükselen bir çok sunucu istemcisi oluşturur.

**Type:** Build
**Languages:** Python (stdlib, multi-server MCP client)
**Prerequisites:** Phase 13 · 07 (building an MCP server)
**Time:** ~75 minutes

## Öğrenme Hedefleri

- Bir çocuk süreci olarak bir MCP sunucusu oluşturun, tamamlayın `initialize`, ve bir gönderelim .`notifications/initialized`- Evet .
- Sunucu başına oturum durumunu korumak (eğitimler, araç listesi, son kez görüntülenen bildirim kimlikleri).
- Çarpışma işlemleri ile birden fazla sunucu listelerini bir isim alanına birleştirin.
- Bir araç çağrısını sahip olduğu sunucuya yönlendirin ve yanıtı yeniden birleştirin.

## Sorun

Gerçek bir ajan barındırması (Claude Desktop, Cursor, Goose, Gemini CLI) birden fazla MCP sunucusu yükler. Bir kullanıcının bir dosya sistemi sunucusu, Postgres sunucusu ve GitHub sunucusu aynı anda çalışması olabilir.

1. Her sunucuyu doğur.
2. El sıkışın.
3. Arama .`tools/list`Her birinde ve sonuçta düzeltmek.
4. Modelle yayıldığında `notes_search`, birleşik isim alanında arayın ve doğru sunucuya yönlendirin.
5. Herhangi bir sunucudan gelen bildirimleri yönet (`tools/list_changed`) engelleme yapmadan.
6. - Nakliye başarısızlığı üzerine tekrar bağlan.

Bu oyuncakları elle oynatmak ve kullanılabilir olmak arasında ayrım yapılır.

## Anlaşım

### Çocuk işlemleri ile nesli

`subprocess.Popen`- Evet .`stdin=PIPE, stdout=PIPE, stderr=PIPE`- Yapılandır .`bufsize=1`ve satır-satır okumalar için metin modunu kullanın. Her sunucu bir işlemdir; istemci bir işlem tutmaktadır `Popen`Sunucu başına.

### Sunucu başına oturum durumu

A.`Session`Sunucu başına nesne:

- `process`Popen elini.
- `capabilities` sunucu tarafından açıklanan`initialize`- Evet .
- `tools`Sonuncusu .`tools/list`Sonuç.
- `pending` Bir söz/geleceğe bir talebinin cevabını bekleyen bir kimliğin haritası.

Talepler doğasıyla eşzamanlı değildir .`tools/call`A sunucusuna gönderilen A sunucusunun B'si çağrı sırasında olduğu sürece, bloklanmamalıdır.

### Birleştirilmiş isim alanı

Müşteri toplu araç listesini gördüğünde isimler çarpışabilir.`search`Müşterinin üç seçeneği var:

1. **Prefix by server name.** `notes/search`- Evet .`files/search`- Açık ama çirkin.
2. **Silent first-come.**Daha sonra sunucuları `search`Daha önce olanları üstlenir.
3. **Collision rejection.**İkinci sunucu yüklenmeyi reddedin, kullanıcıya bildirin.

Claude Desktop, sunucuya göre prefix kullanır. Cursor, açık bir hatayla çarpışma reddetimi kullanır. VS Code MCP, sunucuya göre prefix de kullanır.

### Yollama

Birleştirildikten sonra, bir gönderme masa haritası `tool_name -> session`. Modelle isimli bir çağrı gönderir; müşteri oturumunu bulur ve bir `tools/call`O sunucu'nun stdin'ine mesaj gönderilir ve sonra cevap bekler.

### Örnekleme geri çağırma

Eğer sunucu `sampling``initialize`, gönderebilir .`sampling/createMessage`Müşteriye LLM'sini yürütmesini istemek.

1. Örnek çözülene kadar bu sunucuya yapılan daha fazla talebi veya uygulamasını eşzamanlılığı destekleyen bir boru hattı engelle.
2. LLM sağlayıcısını ara.
3. Cevapı sunucuya geri gönder.

11. ders sonundan sonuna kadar örnek almayı kapsar.

### İletişim işlemi

`notifications/tools/list_changed`Yeniden çağrı anlamına gelir.`tools/list`- Evet .`notifications/resources/updated`İletişimler cevaplar üretmemelidir  onları oluşturmaya çalışmayın.

Genel bir istemci hatası: okuma döngüsünü kapatmak `tools/call`Bir bildirim akışta otururken. Her mesajı bir kuyrukta atan arka plan okuyucu düğümünü kullanın; ana düğüm, devreye ve gönderilere gönderir.

### Yeniden bağlantı

Transport başarısız olabilir: sunucu çöktü, işletim sistemi işlemini öldürdü, stadio borusu kırıldı.

- Sessizlikle sunucuyu yeniden başlatın ve el sıkın.
- Başarısızlığı kullanıcıya bildirin. Kullanıcı görebilen oturumlar olan durumlu sunucular için tamam.

13 · 09 aşaması, Streamable HTTP yeniden bağlantı semantiklerini kapsar; stdio daha basit.

### Kalıcı ve seans kimliği

Akışlanabilir HTTP bir `Mcp-Session-Id`stdio'nun sesyon kimliği  işlem kimliği SESSION'dur.

```figure
tp-client-merge
```

## Kullan

`code/main.py`Bu işlem, üç simülasyonlu MCP sunucusu ile birlikte alt işlem olarak oluşturulur, her biri el sıkışır, araç listelerini birleştirir ve araç çağrılarını sağ olana yönlendirir. "Serverler" aslında oyuncak yanıtlayıcıları (gerçek LLM yok) çalışan diğer Python süreçleridir.

- Üç başlangıç, her biri kendi yetenekleriyle.
- Üç .`tools/list`Sonuçlar 7 araç isim alanına birleştirildi.
- Araç adı üzerine kurulmuş bir yönlendirme kararı.
- Ad alanı önlemleri ile engellenmiş bir çarpışma.

Neye bakılır:

- - Evet .`Session`Dataclass, her sunucu durumu temiz tutmaktadır.
- Arka plan okuyucu dizisi ana dizini engellemeden stdout'taki her satırı temizler.
- Gönderi masası basit bir şey .`dict[str, Session]`- Evet .
- Çarpışma işlemleri açıkça belirlenir: iki sunucu aynı ismi açıkladığında, sonrakı bir önlükle yeniden adlandırılır.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-mcp-client-harness.md`MCP sunucularının (ad, komut, args) bir açıklama listesini göz önüne alarak, bu becerin onları oluşturan, araç listelerini birleştiren ve çarpışma çözünürlüğü ile yönlendirme işlevi gönderilen bir harnes üretir.

## Egzersizler

1. Çık .`code/main.py`SIGTERM ile simülasyonlu sunucu süreçlerinden birini öldür ve müşteri EOF'i nasıl tespit ettiğini ve bu oturumun ölü olduğunu işaretlediğini gözlemle.

2. İki sunucu ortaya çıktığında `search`, ikinciye adını değiştir .`<server>/search`- Gönderi tablosunu güncelle ve araç çağrılarının yolunu doğru şekilde doğrulay.

3. Sunucu yeniden başlatmak için bağlantı havuzu tarzında bir yedekleme ekleyin: ardıcıl hatalarda eksponensel yedekleme, 30 saniyelik bir sınırlama, üç hata sonrasında kullanıcıya bir bildirim gönderin.

4. 100 eşzamanlı MCP sunucusunu destekleyen bir istemci çizin. Basit gönderme diktini hangi veri yapısı değiştirir? (Tip: prefix isim boşluğu için trie, ayrıca sunucu başına araç sayımı için bir metrik.)

5. Müşteriyi resmi MCP Python SDK'ye aktarın.`stdio_client`ve `ClientSession`. Kod, çoklu sunucu yönlendirmeyi korurken ~ 200 satırdan ~ 40 satırına küçülmelidir.

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP client | "The agent host" | Process that spawns servers and orchestrates tool calls |
| Session | "Per-server state" | Capabilities, tool list, and pending-request bookkeeping |
| Merged namespace | "One tool list" | Flat set of tool names across all active servers |
| Namespace collision | "Two servers same tool" | Client must prefix, reject, or first-come the duplicate |
| Routing | "Who gets this call?" | Dispatch from tool name to owning server |
| Background reader | "Non-blocking stdout" | Thread or task that drains server stdout into a queue |
| Sampling callback | "LLM-as-a-service" | Client handler for `sampling/createMessage` from server |
| `notifications/*_changed` | "Primitive mutated" | Signal the client must re-discover or re-read |
| Reconnection policy | "When server dies" | Restart semantics when transport fails |
| Stdio session | "Process = session" | No session id; child process lifetime is the session |

## Daha Fazla Okumak

- [Model Context Protocol — Client spec](https://modelcontextprotocol.io/specification/2025-11-25/client) Kanonik müşteri davranışları
- [MCP — Quickstart client guide](https://modelcontextprotocol.io/quickstart/client)Python SDK ile hello-world istemci öğretmenliği
- [MCP Python SDK — client module](https://github.com/modelcontextprotocol/python-sdk) referans `ClientSession`ve `stdio_client`
- [MCP TypeScript SDK — Client](https://github.com/modelcontextprotocol/typescript-sdk) TS paralel
- [VS Code — MCP in extensions](https://code.visualstudio.com/api/extension-guides/ai/mcp) VS Code'un birden fazla MCP sunucusunu tek bir editör host'ta nasıl çoğaltması
