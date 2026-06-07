# Bir MCP Sunucusu İnşa Etmek — Python + TypeScript SDK'ları

> Çoğu MCP eğitimi yalnızca stdio merhaba-dünyaları gösterir. Gerçek bir sunucu araçların yanı sıra kaynaklar ve istemleri de sunar, yetenek müzakeresini ele alır, yapılandırılmış hatalar üretir ve SDK'lar arasında aynı şekilde çalışır. Bu ders, bir notlar sunucusunu uçtan uca inşa eder: stdlib stdio taşıması, JSON-RPC dağıtımı, üç sunucu primitifi ve Python SDK'sının FastMCP'ine veya TypeScript SDK'sına geçiş yaptığınızda devredilebilir saf fonksiyon tarzı.

**Tür:** İnşa Et
**Diller:** Python (stdlib, stdio MCP sunucusu)
**Ön koşullar:** Faz 13 · 06 (MCP temelleri)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- `initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list` ve `prompts/get` metodlarını uygula.
- stdin'den JSON-RPC mesajları okuyan ve stdout'a yanıt yazan bir dağıtım döngüsü yaz.
- JSON-RPC 2.0 teknik dokümanına ve MCP'in ek hata kodlarına göre yapılandırılmış hata yanıtları üret.
- Stdlib uygulamasını FastMCP (Python SDK) veya TypeScript SDK'sına araç mantığını yeniden yazmadan geçir.

## Sorun

Uzak bir taşıyıcıya (Faz 13 · 09) veya bir kimlik doğrulama katmanına (Faz 13 · 16) geçmeden önce, temiz bir yerel sunucuya ihtiyacınız var. Yerel demek stdio: sunucu istemci tarafından çocuk proces olarak başlatılır, mesajlar stdin/stdout üzerinden satır sonu ile sınırlı akar.

2025-11-25 teknik dokümanı, stdio mesajlarının açık bir `\n` ayıracıyla JSON nesneleri olarak kodlanmasını_buyurur. Burada SSE yok; SSE eski uzak moddu ve 2026 ortasında kaldırılıyor (Atlassian'ın Rovo MCP sunucusu 30 Haziran 2026'da kaldırdı; Keboola 1 Nisan 2026'da). Stdio için satır başına bir JSON nesnesi tüm tel formatıdır.

Bir notlar sunucusu iyi bir şekildir çünkü üç sunucu primitifinin hepsini çalıştırır. Araçlar değişiklik yapar (`notes_create`). Kaynaklar veri sunar (`notes://{id}`). İstemler şablonlar yayınlar (`review_note`). Bu dersin şekli herhangi bir alan için genelleştirilebilir.

## Kavram

### Dağıtım döngüsü

```
döngü:
 satır = stdin.readline()
 msg = json.loads(satır)
 if id varsa:
 isteği ele al -> yanıtı yaz
 else:
 bildirimi ele al -> yanıt yok
```

Üç kural:

- stdout'a JSON-RPC zarfı olmayan hiçbir şey yazmayın. Hata ayıklama günlükleri stderr'a gider.
- Her istek, aynı `id`'yi taşıyan bir yanıtla eşleştirilmelidir.
- Bildirimlere yanıt verilmemelidir.

### `initialize`'ı uygulama

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
#### Açıklama
initialize, sunucunun yeteneklerini ve kimlik bilgilerini istemciye beyan ettiği el sıkışma mesajıdır.
```

Yalnızca desteklediğiniz şeyi beyan edin. İstemci, özellikleri kontrol etmek için yetenek kümesine güvenir.

### `tools/list` ve `tools/call`'ı uygulama

`tools/list`, her girişin `name`, `description`, `inputSchema` içerdiği `{tools: [...]}` döndürür. `tools/call`, `{name, arguments}` alır ve `{content: [bloklar], isError: bool}` döndürür.

İçerik blokları tiplidir. En yaygın olanları:

```json
{"type": "text", "text": "2 not bulundu"}
{"type": "resource", "resource": {"uri": "notes://14", "text": "..."}}
{"type": "image", "data": "<base64>", "mimeType": "image/png"}
#### Açıklama
İçerik blokları, araç sonuçlarının tipli elemanlarıdır: metin, kaynak veya görsel olabilir.
```

Araç hataları iki şekilde gelir. Protokol düzeyindeki hatalar (bilinmeyen method, kötü parametreler) JSON-RPC hatalarıdır. Araç düzeyindeki hatalar (geçerli çağrı ancak araç başarısız oldu) `{content: [...], isError: true}` olarak döndürülür. Bu, modelin bağlamda hatayı görmesini sağlar.

### Kaynakları uygulama

Kaynaklar tasarıma göre salt okunur. `resources/list` bir manifesto döndürür; `resources/read` içeriği döndürür. URI'ler `file://...`, `http://...` veya `notes://` gibi bir özel şema olabilir.

Verileri araç yerine kaynak olarak sunduğunuzda:

- Model bunu "çağırmaz"; istemci kullanıcı isteği üzerine bağlama enjekte edebilir.
- Abonelikler, kaynak değiştiğinde sunucunun güncelleme göndermesine olanak tanır (Faz 13 · 10).
- Faz 13 · 14, `ui://` ile etkileşimli kaynakları genişletir.

### İstemleri uygulama

İstemler, adlı argümanlara sahip şablonlardır. Ana program bunları slash-komutları olarak yüzey çıkarır. Bir `review_note` istemi bir `note_id` argümanı alabilir ve istemcinin modeline beslediği çok mesajlı bir istem şablonu üretebilir.

### Stdio taşıma incelikleri

- Satır sonu ile sınırlı JSON. Uzunluk önekli çerçeveleme yok.
- Tampon yapmayın. Her yazmadan sonra `sys.stdout.flush()`.
- İstemci ömrü kontrol eder. stdin kapandığında (EOF), temiz şekilde çıkın.
- SIGPIPE'ı sessizce ele almayın; günlük yazın ve çıkın.

### Eklemeler (Annotations)

Her araç, güvenlik özelliklerini tanımlayan `annotations` taşıyabilir:

- `readOnlyHint: true` — saf okuma, yeniden deneme için güvenli.
- `destructiveHint: true` — geri dönüşsüz yan etkiler; istemci onaylamalıdır.
- `idempotentHint: true` — aynı girdiler aynı çıktıları üretir.
- `openWorldHint: true` — dış sistemlerle etkileşir.

İstemci bunları UX (onay dialogları, durum göstergeleri) ve yönlendirme (Faz 13 · 17) için kullanır.

### Geçiş yolu

`code/main.py`'deki stdlib sunucusu yaklaşık 180 satırdır. FastMCP (Python) aynı mantığı dekoratör tarzına küçültür:

```python
from fastmcp import FastMCP
app = FastMCP("notes")

@app.tool()
def notes_search(query: str, limit: int = 10) -> list[dict]:
 ...
#### Açıklama
FastMCP, dekoratör tabanlı üst düzey bir MCP sunucu çerçevesidir.
```

TypeScript SDK'sının eşdeğer bir şekli vardır. Hazır olduğunuzda geçiş doğrudan yapılır; kavramlar (yetenekler, dağıtım, içerik blokları) aynıdır.

## Kullan

`code/main.py`, stdio üzerinden eksiksiz bir notlar MCP sunucusudur, yalnızca stdlib. `initialize`, üç araç (`notes_list`, `notes_search`, `notes_create`) için `tools/list`, `tools/call`, her not için `resources/list` ve `resources/read` ve bir `review_note` istemini ele alır. JSON-RPC mesajları göndererek sürebilirsiniz:

```
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python main.py
```

Neye bakılmalı:

- Dağıtıcı, method adıyla anahtarlanmış bir `dict[str, Callable]`.
- Her araç çalıştırıcısı, çıplak bir string yerine içerik blokları listesi döndürür.
- `isError: true`, çalıştırıcı fırlattığında ayarlanır.

## Sun

Bu ders `outputs/skill-mcp-server-scaffolder.md` dosyasını üretir. Bir alan (notlar, talepler, dosyalar, veritabanı) verildiğinde, beceri doğru araçlar / kaynaklar / istemler bölünmesi ve SDK geçiş yoluyla bir MCP sunucusu iskeleti (scaffold) oluşturur.

## Alıştırmalar

1. `code/main.py`'i çalıştırın ve elle oluşturulmuş JSON-RPC mesajlarıyla sürün. `notes_create`'i çalıştırın, ardından yeni notu almak için `resources/read`'i çalıştırın.

2. `annotations: {destructiveHint: true}` ile bir `notes_delete` aracı ekleyin. İstemcinin bir onay dialogu göstereceğini doğrulayın (gerçek bir ana program gerektirir; Claude Desktop çalışır).

3. Bir not her değiştirildiğinde sunucunun `notifications/resources/updated` göndermesini sağlayacak `resources/subscribe` uygulayın. Bir canlı tutma görevi ekleyin.

4. Sunucuyu FastMCP'e taşıyın. Python dosyası 80 satırın altına düşmelidir. Tel davranışı aynı olmalıdır; aynı JSON-RPC test donanımıyla doğrulayın.

5. Teknik dokümanın `server/tools` bölümünü okuyun ve bu dersin sunucusunda uygulanmayan bir araç tanımı alanı belirleyin. (İpucu: birkaç tane var; birini seçin ve ekleyin.)

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| MCP sunucusu | "Araçları sunan şey" | stdio veya HTTP üzerinden MCP JSON-RPC konuşan süreç |
| stdio transport | "Çocuk süreç modeli" | Sunucu istemci tarafından başlatılır; stdin/stdout aracılığıyla iletişim kurar |
| Dispatcher | "Method yönlendirici" | JSON-RPC method adından işleyici fonksiyona eşleme |
| Content block (İçerik bloğu) | "Araç sonucu parçası" | Araç yanıtının `content` dizisindeki tipli eleman |
| `isError` | "Araç düzeyinde hata" | Aracın başarısız olduğunu belirtir; JSON-RPC hatasından ayırt eder |
| Annotations (Eklemeler) | "Güvenlik ipuçları" | readOnly / destructive / idempotent / openWorld bayrakları |
| FastMCP | "Python SDK" | MCP protokolü üzerine kurulu dekoratör tabanlı üst düzey çerçeve |
| Resource URI (Kaynak URI) | "Adreslenebilir veri" | Bir kaynağı tanımlayan `file://`, `db://` veya özel şema |
| Prompt template (İstem şablonu) | "Slash-komutu özeti" | Ana program UI'ları için argumentli sunucu tarafından sağlanan şablon |
| Capability declaration (Yetenek beyanı) | "Özellik anahtarı" | `initialize`'da beyan edilen primitif başına bayraklar |

## İleri Okuma

- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk) — referans Python uygulaması
- [Model Context Protocol — TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) — paralel TS uygulaması
- [FastMCP — server framework](https://gofastmcp.com/) — MCP sunucuları için dekoratör tarzı Python API'si
- [MCP — Quickstart server guide](https://modelcontextprotocol.io/quickstart/server) — her iki SDK'yı kullanan uçtan uca eğitim
- [MCP — Server tools spec](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) — tools/* mesajları için eksiksiz referans
