# MCP Server Oluşturma  Python + TypeScript SDK'leri

> Çoğu MCP öğretim programı sadece stüdyo selam dünyasını gösterir. Gerçek bir sunucu, araçları, kaynakları ve ipuçlarını ortaya çıkarır, yetenek müzakerelerini ele alır, yapılandırılmış hatalar yayar ve SDK'ler arasında aynı şekilde çalışır. Bu ders bir not sunucu sonu-sonu oluşturur: stdlib stdio taşıma, JSON-RPC gönderme, üç sunucu primitifi ve Python SDK'nin FastMCP veya TypeScript SDK'sine mezuniyet yaptığınızda düşen saf bir işlev tarzı.

**Type:** Build
**Languages:** Python (stdlib, stdio MCP server)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals)
**Time:** ~75 minutes

## Öğrenme Hedefleri

- Uygulama`initialize`- Evet .`tools/list`- Evet .`tools/call`- Evet .`resources/list`- Evet .`resources/read`- Evet .`prompts/list`ve`prompts/get`- Yöntemleri.
- Stdin'den JSON-RPC mesajlarını okuyan ve stdout'a cevaplar yazan bir gönderim döngüsü yazın.
- JSON-RPC 2.0 spesifikasyonu ve MCP'nin ek kodlarına göre yapılandırılmış hata cevapları gönderin.
- Bir stdlib uygulamasını FastMCP (Python SDK) veya TypeScript SDK'ye araç mantığını yeniden yazmadan tamamlayın.

## Sorun

Uzaktan bir nakliye (Fase 13 · 09) veya bir auth katman (Fase 13 · 16) kullanabilmeden önce temiz bir yerel sunucu gerekir.

2025-11-25 spesifikasyonunda stdio mesajlarının açık bir şekilde JSON nesneleri olarak kodlandırdığı belirtildi.`\n`SSE, eski uzaktan moddu ve 2026 yılının ortalarında kaldırılıyor. (Atlassian'ın Rovo MCP sunucusu 30 Haziran 2026'da geriye dönmüştür; 1 Nisan 2026'da Keboola).

Not sunucu, üç sunucu primitifinin de uygulanması nedeniyle iyi bir şekil.`notes_create`Resurslar verileri açığa çıkarır (`notes://{id}`). Gemiden şablonları gösterir (`review_note`Bu dersin şekli herhangi bir alan için genelleşir.

## Anlaşım

### Gönderme döngüsü

```
loop:
  line = stdin.readline()
  msg = json.loads(line)
  if has id:
    handle request -> write response
  else:
    handle notification -> no response
```

Üç kural:

- JSON-RPC zarfı olmayan hiçbir şeyi stdout'a yazdırmayın. Debug logları stderr'e gider.
- Her talebe aynı cevapla eşleşmek gerekir .`id`- Evet .
- İletişlere cevap verilmemelidir.

### Uygulama`initialize`

```python
def initialize(params):
    return {
        "protocolVersion": "2025-11-25",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"listChanged": True, "subscribe": False},
            "prompts": {"listChanged": False},
        },
        "serverInfo": {"name": "notes", "version": "1.0.0"},
    }
```

Müşteri kapı özelliklerine ayarlanmış yeteneklere dayanır.

### Uygulama`tools/list`ve `tools/call`

`tools/list`Devamı`{tools: [...]}`Her giriş ile `name`- Evet .`description`- Evet .`inputSchema`- Evet .`tools/call`Alıyor .`{name, arguments}`ve geri dönüşleri`{content: [blocks], isError: bool}`- Evet .

İçerik blokları yazılır. En yaygın olan:

```json
{"type": "text", "text": "Found 2 notes"}
{"type": "resource", "resource": {"uri": "notes://14", "text": "..."}}
{"type": "image", "data": "<base64>", "mimeType": "image/png"}
```

Araç hataları iki şekilde gelir. Protokol düzeyde hatalar (bilinmeyen yöntem, kötü parametre) JSON-RPC hatalarıdır. Araç düzeyde hatalar (valüde çağrı ama araç başarısız) olarak geri gönderilmektedir.`{content: [...], isError: true}`Bu da modelin başarısızlığı bağlamında görmesine izin verir.

### Uygulama kaynakları

Kaynaklar tasarlanmış olarak sadece okunur. `resources/list`bir belgeyi gönderir .`resources/read`URI'ler `file://...`- Evet .`http://...`, veya özel bir düzen gibi`notes://`- Evet .

Verileri bir araç yerine bir kaynak olarak açığa çıkarırken:

- Modelle "davet" edilmez; müşteri, kullanıcı isteği üzerine bağlamda enjekte edebilir.
- Abonelikler , sunucu kaynak değişken güncellemeleri gönderebilir (Fase 13 · 10).
- 13 · 14 aşaması bunu genişletiyor `ui://`etkileşimli kaynaklar için.

### Uygulama uyarıları

İstekler isimli argümanlarla şablonlardır. Ev sahibi onları kesme komutları olarak ortaya çıkarır.`review_note`- Bu bir süredir .`note_id`Bu, bir programın bir programı oluşturmak için kullanılır.

### İstanbul'da taşımacılık incelikleri

- Yeni çizgi sınırlı JSON. Uzunluk prefiksine sahip bir çerçeve yok.
- Buffer yapmayın.`sys.stdout.flush()`Her yazıdan sonra.
- Müşteri hayatını kontrol eder. stdin kapanırken temiz çık.
- SIGPIPE' yi sessizce kullanmayın; giriş ve çıkış yapın.

### Notasyonlar

Her alet taşıyabilir .`annotations`Güvenlik özelliklerini tanımlayan:

- `readOnlyHint: true` saf okuma, tekrar denemek için güvenli.
- `destructiveHint: true` Geri dönüşü olmayan yan etkileri; müşteri onaylamalıdır.
- `idempotentHint: true` Aynı girişler aynı çıkışlar üretir.
- `openWorldHint: true` dış sistemlerle etkileşim kurar.

Müşteri bunları UX (tutsatma diyalogları, durum göstergeler) ve yönlendirmeyi (Fase 13 · 17) belirlemek için kullanır.

### Mezunluk yolu

Stdlib sunucusu içeriyor .`code/main.py`FastMCP (Python) aynı mantığı dekorasyon tarzına düşürüyor:

```python
from fastmcp import FastMCP
app = FastMCP("notes")

@app.tool()
def notes_search(query: str, limit: int = 10) -> list[dict]:
    ...
```

TypeScript SDK'nin eşdeğer bir şekli vardır. Mezunluk yolu hazır olduğunda düşer; kavramlar (eğitme, gönderme, içerik blokları) aynıdır.

```figure
t3-dispatch-loop
```

## Kullan

`code/main.py`Stdio, stdlib üzerinde MCP sunucusu.`initialize`- Evet .`tools/list`- Evet .`tools/call`Üç alet için (`notes_list`- Evet .`notes_search`- Evet .`notes_create`), `resources/list`ve `resources/read`Her not için ve bir `review_note`JSON-RPC mesajlarını yollayarak kullanabilirsiniz:

```
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python main.py
```

Neye bakılır:

- - Depoyucu bir .`dict[str, Callable]`Metod adı ile belirlenmiş.
- Her araç uygulayıcısı, bir dizi değil, içerik bloklarının bir listesini gönderir.
- `isError: true`İcracı'nın yüklemesiyle ayarlanır.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-mcp-server-scaffolder.md`. Bir alan (notlar, biletler, dosyalar, veritabanı) verildiğinde, beceri bir MCP sunucusu üzerinde doğru araçlar / kaynaklar / istekler bölünmesi ve SDK mezuniyet yolu ile kuruluyor.

## Egzersizler

1. Çık .`code/main.py`Ve el yapımı JSON-RPC mesajları ile çalıştırın.`notes_create`O zaman ...`resources/read`Yeni notu almak için.

2. Bir ekle`notes_delete` ile araç`annotations: {destructiveHint: true}`. Verify istemcisinin doğrulama diyalogunun ortaya çıkmasını sağlar (bu gerçek bir barındırma gerektirir; Claude Desktop çalışır).

3. Uygulama`resources/subscribe`Böylece sunucu itti .`notifications/resources/updated`Bir not değiştirildiğinde, bir tutma görevi ekle.

4. Sunucuyu FastMCP'ye aktarın. Python dosyası 80 satırın altına küçülmelidir. Kablo davranışı aynı olmalıdır; aynı JSON-RPC test harnesini kullanarak doğrulayın.

5. Spec'in yazısını oku.`server/tools`bölüm ve bu ders sunucusunda uygulanmayan bir araç tanımının alanını belirleyin. (İpucu: bir kaç tane var; birini seçin ve ekleyin.)

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| MCP server | "The thing that exposes tools" | Process that speaks MCP JSON-RPC over stdio or HTTP |
| stdio transport | "Child process model" | Server is spawned by client; communicates via stdin/stdout |
| Dispatcher | "Method router" | Map of JSON-RPC method name to handler function |
| Content block | "Tool result chunk" | Typed element in the `content` array of a tool response |
| `isError` | "Tool-level failure" | Signals the tool failed; distinguishes from JSON-RPC error |
| Annotations | "Safety hints" | readOnly / destructive / idempotent / openWorld flags |
| FastMCP | "Python SDK" | Decorator-based higher-level framework on top of the MCP protocol |
| Resource URI | "Addressable data" | `file://`, `db://`, or custom scheme identifying a resource |
| Prompt template | "Slash-command brief" | Server-supplied template with argument slots for host UIs |
| Capability declaration | "Feature toggle" | Per-primitive flags declared in `initialize` |

## Daha Fazla Okumak

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk) Referans Python uygulaması
- [Model Context Protocol — TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) paralel TS uygulaması
- [FastMCP — server framework](https://gofastmcp.com/) MCP sunucular için dekorasyon tarzı Python API
- [MCP — Quickstart server guide](https://modelcontextprotocol.io/quickstart/server) SDK'yi kullanan sonundan sonuna kadar öğretim
- [MCP — Server tools spec](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) araçlar/* mesajlar için tam referans
