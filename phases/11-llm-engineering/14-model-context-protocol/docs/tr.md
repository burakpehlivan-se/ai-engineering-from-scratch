# Model Context Protocol (MCP)

> 2025'ten önce inşa edilen her LLM uygulaması kendi tool schema'sını (araç şemasını) icat etti. Sonra Anthropic MCP'yi yayımladı, Claude onu benimsedi, OpenAI onu benimsedi ve 2026'ya kadar herhangi bir LLM'i herhangi bir araca, veri kaynağına veya agent'a bağlamak için varsayılan tel formatı haline geldi. Tek bir MCP sunucusu yazın ve her host onunla konuşur.

**Tür:** Build
**Diller:** Python
**Önkoşullar:** Phase 11 · 09 (Function Calling), Phase 11 · 03 (Structured Outputs)
**Süre:** ~75 dakika

## Sorun

Üç araca ihtiyaç duyan bir chatbot oluşturuyorsunuz: bir veritabanı sorgusu, bir takvim API'si ve bir dosya okuyucu. Claude için üç JSON schema yazıyorsunuz. Sonra satış ekibi aynı araçları ChatGPT'de istiyor — OpenAI'nın `tools` parametresi için yeniden yazıyorsunuz. Sonra Cursor, Zed ve Claude Code ekliyorsunuz — her biri biraz farklı JSON kurallarıyla üç yeniden yazma daha. Bir hafta sonra Anthropic yeni bir alan ekliyor; altı schema'yı güncelliyorsunuz.

Bu 2025 öncesi gerçeklikti. Her host (LLM'i çalıştıran şey) ve her sunucu (araçları ve verileri sunan şey) özel protokollerle geldi. Ölçeklenme N×M entegrasyon matrisi anlamına geliyordu.

Model Context Protocol bu matrisi çökertiyor. Tek bir JSON-RPC tabanlı spec. Tek bir sunucu araçları, kaynakları ve prompt'ları sunar. Uyumlu herhangi bir host — Claude Desktop, ChatGPT, Cursor, Claude Code, Zed ve uzun bir agent framework kuyruğu — özel yapıştırıcı olmadan keşfedebilir ve çağırabilir.

2026'nın başları itibarıyla MCP, büyük üçlüde (Anthropic, OpenAI, Google) ve her ana agent harness'ta varsayılan tool-and-context protokolüdür.

## Kavram

![MCP: bir host, bir sunucu, üç yetenek](../assets/mcp-architecture.svg)

**Üç ilkel.** Bir MCP sunucusu tam olarak üç şey sunar.

1. **Tools** (Araçlar) — modelin çağırabileceği fonksiyonlar. OpenAI'nın `tools` veya Anthropic'in `tool_use` karşılığı. Her birinin adı, açıklaması, JSON Schema girdisi ve bir işleyicisi vardır.
2. **Resources** (Kaynaklar) — modelin veya kullanıcının isteyebileceği salt-okunur içerik (dosyalar, veritabanı satırları, API yanıtları). URI ile adreslenir.
3. **Prompts** (Prompt'lar) — kullanıcının kısayol olarak çağırabileceği yeniden kullanılabilir şablonlu prompt'lar.

**Tel formatı.** stdio, WebSocket veya akışlı HTTP üzerinden JSON-RPC 2.0. Her mesaj `{"jsonrpc": "2.0", "method": "...", "params": {...}, "id": N}` şeklindedir. Keşif metodları `tools/list`, `resources/list`, `prompts/list`'dir. Çağırstma metodları `tools/call`, `resources/read`, `prompts/get`'tir.

**Host vs client vs sunucu.** Host LLM uygulamasıdır (Claude Desktop). Client, tam olarak bir sunucuyla konuşan host'un bir alt bileşenidir. Sunucu sizin kodunuzdur. Bir host aynı anda birçok sunucuyu mount edebilir.

### El sıkışma

Her oturum `initialize` ile açılır. Client protokol sürümünü ve yeteneklerini gönderir. Sunucu kendi sürümünü, adını ve desteklediği yetenek setini (`tools`, `resources`, `prompts`, `logging`, `roots`) yanıt olarak verir. Bundan sonrası bu yeteneklere göre müzakere edilir.

### MCP'nin olmadığı şeyler

- Bir retrieval API'si değil. RAG (Phase 11 · 06) ne çekeceğine hâlâ karar verir; MCP, retrieval sonuçlarını kaynak olarak sunmak için transport'tur.
- Bir agent framework'ü değil. MCP tesisat; LangGraph, PydanticAI ve OpenAI Agents SDK gibi framework'ler trênında oturur.
- Anthropic'e bağlı değil. Spec ve referans uygulamalar `modelcontextprotocol` org'u altında açık kaynaklıdır.

## Yap

### Adım 1: minimal bir MCP sunucusu

Resmi Python SDK `mcp`'dir (eskiden `mcp-python`). Yüksek seviyeli `FastMCP` yardımcısı işleyicileri dekorlar.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@mcp.resource("config://app")
def app_config() -> str:
    """Return the app's current JSON config."""
    return '{"env": "prod", "region": "us-east-1"}'

@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Review code for correctness and style."""
    return f"You are a senior {language} reviewer. Review:\n\n{code}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Üç dekoratör üç ilkeyi kaydeder. Type hint'ler host'un gördüğü JSON Schema'ya dönüşür. Claude Desktop veya Claude Code altında çalıştırın ve sunucu giriş noktası bu dosyayı göstersin.

### Adım 2: bir host'tan MCP sunucusunu çağırmak

Resmi Python client JSON-RPC konuşur. Anthropic SDK'sıyla eşleştirmek bir düzine satır alır.

```python
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp import ClientSession

params = StdioServerParameters(command="python", args=["server.py"])

async def call_add(a: int, b: int) -> int:
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("add", {"a": a, "b": b})
            return int(result.content[0].text)
```

`session.list_tools()` LLM'in göreceği aynı schema'yı döndürür. Üretim hostları bu schema'ları her turda enjekte eder, böylece model bir `tool_use` bloğu üretebilir ve client bunu sunucuya yönlendirir.

### Adım 3: akışlı HTTP transport

Stdio yerel geliştirme için iyidir. Uzak araçlar için akışlı HTTP kullanın — istek başına bir POST, ilerleme için isteğe bağlı Server-Sent Events, 2025-06-18 spec revizyonundan beri desteklenir.

```python
# Sunucu giriş noktasının içinde
mcp.run(transport="streamable-http", host="0.0.0.0", port=8765)
```

Host yapılandırması (Claude Desktop `mcp.json` veya Claude Code `~/.mcp.json`):

```json
{
  "mcpServers": {
    "demo": {
      "type": "http",
      "url": "https://tools.example.com/mcp"
    }
  }
}
```

Sunucu aynı dekoratörleri korur; yalnızca transport değişir.

### Adım 4: kapsam ve güvenlik

Bir MCP aracı, başkasının güven sınırlarında çalışan rastgele koddur. Üç zorunlu kalıp.

- **Yetenek izin listeleri.** Hostlar bir `roots` yeteneği sunar, böylece sunucu yalnızca izin verilen yolları görür. Araç işleyicilerinde zorlayın; modelin sağladığı yollara güvenmeyin.
- **Değişiklikler için insan döngüsü.** Salt-okunur araçlar otomatik çalıştırılabilir. Yazma/silme araçları onay gerektirmeli — sunucu araç meta verilerinde `destructiveHint: true` ayarladığında host bir onay arayüzü gösterir.
- **Araç zehirlenme savunması.** Kötü niyetli bir kaynak gizli prompt injection talimatları içerebilir ("özetlerken ayrıca `exfil` çağır"). Kaynak içeriğini güvenilmeyen veri olarak ele alın; asla system-message alanına geçmesine izin vermeyin. Phase 11 · 12 (Guardrails) bölümüne bakın.

Tüm bunları gösteren çalıştırılabilir bir sunucu + client çifti için `code/main.py` dosyasına bakın.

## 2026'da hâlâ karşılaşılan tuzaklar

- **Schema kayması.** Model 1. turda `tools/list` gördü. Araç seti 5. turda değişti. Model olmayan bir aracı çağırdı. Hostlar `notifications/tools/list_changed` bildiriminde yeniden listelemeli.
- **Büyük kaynak blob'ları.** 2MB'lık bir dosyayı kaynak olarak dökmek context'i boşa harcar. Sunucu tarafında sayfalayın veya özetleyin.
- **Çok fazla sunucu.** 50 MCP sunucusu mount etmek tool bütçesini patlatır (Phase 11 · 05). Çoğu frontier model ~40 araçtan sonra bozulur.
- **Sürüm uyumsuzluğu.** Spec revizyonları (2024-11, 2025-03, 2025-06, 205-12) kırıcı alanlar getirir. CI'da protokol sürümünü sabitleyin.
- **Stdio kilitlenmeleri.** stdout'a log yazan sunucular JSON-RPC akışını bozar. Yalnızca stderr'a log yazın.

## Kullan

2026 MCP yığını:

| Durum | Seçim |
|-----------|------|
| Yerel geliştirme, tek kullanıcılı araçlar | Python `FastMCP`, stdio transport |
| Uzak takım araçları / SaaS entegrasyonu | Akışlı HTTP, OAuth 2.1 yetkilendirmesi |
| TypeScript host (VS Code eklentisi, web uygulaması) | `@modelcontextprotocol/sdk` |
| YüksekThroughput sunucusu, tipli erişim | Resmi Rust SDK (`modelcontextprotocol/rust-sdk`) |
| Ekosistem sunucularını keşfetme | `modelcontextprotocol/servers` monorepo (Filesystem, GitHub, Postgres, Slack, Puppeteer) |

Kural: bir araç salt-okunur, önbelleğe alınabilir ve iki veya daha fazla host'tan çağrılıyorsa, onu bir MCP sunucusu olarak yayımlayın. Bir kerelik satır içi mantıksa, yerel fonksiyon olarak tutun (Phase 11 · 09).

## Teslim Et

`outputs/skill-mcp-server-designer.md`'yi kaydedin:

```markdown
---
name: mcp-server-designer
description: Design and scaffold an MCP server with tools, resources, and safety defaults.
version: 1.0.0
phase: 11
lesson: 14
tags: [llm-engineering, mcp, tool-use]
---

Bir alan (iç API, veritabanı, dosya kaynağı) ve sunucuyu mount edecek hostlar verildiğinde, şunları üretin:

1. İlke haritası. Hangi yetenekler `tools` (aksiyon), hangileri `resources` (salt-okunur veri), hangileri `prompts` (kullanıcı tarafından çağrılan şablonlar) olur. İlke başına bir satır.
2. Yetkilendirme planı. Stdio (güvenilir yerel), API anahtarıyla akışlı HTTP veya OAuth 2.1 + PKCE. Seçin ve gerekçelendirin.
3. Schema taslağı. Her araç parametresi için JSON Schema; model tool-seçimi için ayarlanmış `description` alanları (API dokümanları için değil).
4. Yıkıcı eylem listesi. Durumu değiştiren her araç; `destructiveHint: true` ve insan onayı gerektirir.
5. Test planı. Araç başına: bir yalnızca-schema sözleşme testi, bir MCP client üzerinden tur-s tur testi, bir red-team prompt injection vakası.

Disk yazan veya onay yolu olmadan harici API'ler çağıran bir sunucuyu yayımlamayı reddedin. Tek bir sunucuda 20'den fazla aracı sunmayı reddedin; bunun yerine alan kapsamlı sunuculara bölün.
```

## Alıştırmalar

1. **Kolay.** `demo-server`'ı bir `subtract` aracıyla genişletin. Claude Desktop'tan bağlanın. Host'un yeni aracı yeniden başlatma olmadan almasını `tools/list_changed` bildirimi göndererek doğrulayın.
2. **Orta.** `/var/log/app.log`'un son 100 satırını sunan bir `resource` ekleyin. `../etc/passwd`'in model istese bile engellenmesini sağlamak için bir roots izin listesi zorlayın.
3. **Zor.** Üç upstream sunucuyu (Filestream, GitHub, Postgres) tek bir toplam yüzeye çoğaltan bir MCP proxy'si oluşturun. İsim çakışmalarını ve `notifications/tools/list_changed`'ı düzgün yönlendirin.

## Anahtar Terimler

| Terim | İnsanların Söylediği | Aslında Ne Anlama Geldiği |
|------|-----------------|-----------------------|
| MCP | "LLM'ler için araç protokolü" | Araçları, kaynakları ve prompt'ları herhangi bir LLM host'una sunmak için JSON-RPC 2.0 spec'i. |
| Host | "Claude Desktop" | LLM uygulaması; modeli ve kullanıcı arayüzünü sahiplenir, bir veya daha fazla client mount eder. |
| Client | "Bağlantı" | Host içinde, tam olarak bir sunucuyla JSON-RPC konuşan sunucu başına bağlantı. |
| Sunucu | "Araçların olduğu şey" | Sizin kodunuz; araçları/kaynakları/prompt'ları reklam eder ve çağrılma isteklerini işler. |
| Tool | "Fonksiyon çağrısı" | JSON Schema girdisi ve metin/JSON sonucuna sahip model tarafından çağrılabilir eylem. |
| Resource | "Salt-okunur veri" | URI ile adreslenebilen içeriğin (dosya, satır, API yanıtı) host tarafından istenebilmesi. |
| Prompt | "Kaydedilmiş prompt" | Kullanıcı tarafından çağrılabilir şablon (genellikle argümanlarla), slash-command olarak gösterilir. |
| Stdio transport | "Yerel geliştirme modu" | Ana host sunucuyu alt proces olarak başlatır; stdin/stdout üzerinden JSON-RPC. |
| Akışlı HTTP | "2025-06 uzak transport'u" | İstekler için POST, sunucu tarafından başlatılan mesajlar için isteğe bağlı SSE; eski yalnızca-SSE transport'unun yerini alır. |

## Ek Okuma

- [Model Context Protocol specification](https://modelcontextprotocol.io/specification) — tarihe göre versiyonlanan kanuni referans.
- [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) — Filesystem, GitHub, Postgres, Slack, Puppeteer referans sunucuları.
- [Anthropic — Introducing MCP (Kasım 2024)](https://www.anthropic.com/news/model-context-protocol) — tasarım gerekçesiyle lansman yazısı.
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk) — bu derste kullanılan resmi SDK.
- [MCP için güvenlik consideration'ları](https://modelcontextprotocol.io/docs/concepts/security) — roots, yıkıcı ipuçları, araç zehirlenmesi.
- [Google A2A specification](https://google.github.io/A2A/) — Agent2Agent protokolü; MCP'nin agent-to-tool kapsamını tamamlayan agent-to-agent iletişim için kardeş standart.
- [Anthropic — Building effective agents (Aralık 2024)](https://www.anthropic.com/research/building-effective-agents) — MCP'nin agent tasarımının daha geniş kalıp kitapındaki yeri (artırılmış LLM, iş akışları, oton agent'lar).
