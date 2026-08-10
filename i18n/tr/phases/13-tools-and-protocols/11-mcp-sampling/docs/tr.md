# MCP Örnekleme  Server İsteği LLM Tamamlamaları ve Ajan Çubukları

> Çoğu MCP sunucusu aptal uygulayıcılar: argümanları al, kod çalıştır, içeriği geri getir. Örnekleme, bir sunucuyu yön değiştirmeye zorlar: müşterinin LLM'sinden bir karar vermesi için sorar. Bu, sunucu'nun herhangi bir model kimlik bilgisi sahibi olmadan sunucu barındırılmış ajan döngüleri etkinleştirir. SEP-1577, 2025-11-25'te birleştirildi, örneğe ihtiyaç duyulan araçlar eklendi, böylece döngü daha derin bir mantıklama içerebilir. Drift risk notu: SEP-1577 örneğe girme aracı şekli, 2026'ın birinci çeyreğine kadar deneysel olarak kullanıldı ve hala SDK API'lerinde yerleşmektedir.

**Type:** Build
**Languages:** Python (stdlib, sampling harness)
**Prerequisites:** Phase 13 · 07 (MCP server), Phase 13 · 10 (resources and prompts)
**Time:** ~75 minutes

## Öğrenme Hedefleri

- Neyi açıkla `sampling/createMessage`çözüyor (server tarafından barındırılan, sunucu taraflı API anahtarları olmayan döngüler).
- Bir sunucu uygulamak, istemciyi bir çok dönüşlü çağrıyı örneklemesini ve tamamlanmayı geri getirmesini ister.
- Kullanım`modelPreferences`(maliyet / hız / istihbarat öncelikleri) müşteri model seçimini yönlendirmek için.
- Bir tane yapın .`summarize_repo`Hard-coding davranışları yerine örneği kullanarak içten olarak tekrarlayan bir araç.

## Sorun

Bir kod özetleme iş akışı için yararlı bir MCP sunucusu: bir dosya ağacını yürümek, hangi dosyaları okumak için seçmek, bir özet sentezlemek ve geri vermek gerekir. LLM mantıklaşması nerede gerçekleşir?

A. Seçenek: sunucu kendi LLM'ini çağırır. API anahtarı gerekir, sunucu tarafında faturalar, kullanıcı başına pahalıdır.

Seçenek B: sunucu ham içeriği gönderir; istemcinin ajanı mantık yürütür. Çalışır ama kırılgan olan istemci istekine sunucu mantığını taşır.

Seçenek C: sunucu, müşterinin LLM'sini `sampling/createMessage`.Server algoritmayı ( hangi dosyaları okumak, kaç geçiş yapmak) saklarken, müşteri faturalama ve model seçimini saklar.Server'in hiçbir kimliği yoktur.

Örnekleme, C. Bir güvenilir sunucunun, bir temsilci döngüsünü kendisi tam bir LLM sunucusu olmadan barındırması için kullanılan mekanizmadır.

## Anlaşım

### `sampling/createMessage`taleb

Sunucu gönderir:

```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "method": "sampling/createMessage",
  "params": {
    "messages": [{"role": "user", "content": {"type": "text", "text": "..."}}],
    "systemPrompt": "...",
    "includeContext": "none",
    "modelPreferences": {
      "costPriority": 0.3,
      "speedPriority": 0.2,
      "intelligencePriority": 0.5,
      "hints": [{"name": "claude-3-5-sonnet"}]
    },
    "maxTokens": 1024
  }
}
```

Müşteri LLM'ini yürütür, geri gönderir:

```json
{"jsonrpc": "2.0", "id": 42, "result": {
  "role": "assistant",
  "content": {"type": "text", "text": "..."},
  "model": "claude-3-5-sonnet-20251022",
  "stopReason": "endTurn"
}}
```

### `modelPreferences`

1.0'a kadar toplam üç akış:

- `costPriority`: daha ucuz modeller tercih.
- `speedPriority`Daha hızlı modeller tercih edilir.
- `intelligencePriority`: daha yetenekli modeller için tercih edilir.

Ayrıca .`hints`: sunucu tercih eden isimli modeller. Müşteri ipuçlarını saymayabilir veya saymayabilir; müşteri'nin kullanıcı yapılandırması her zaman kazanır.

### `includeContext`

Üç değer:

- `"none"`- Sadece sunucu tarafından gönderilen mesajlar.
- `"thisServer"` bu sunucu oturumundan önceki mesajları içerir.
- `"allServers"` tüm oturum bağlamını içerir.

`includeContext`2025-11-25'te güvenlik endişesi olan sunucu çapındaki bağlamı sızdırdığı için hafif derecede azalmıştır.`"none"`Ve mesajlarda açık bir bağlam geçiriyorlar.

### Araçlarla örnekleme (SEP-1577)

2025-11-25 yıllarında yeni: örnekleme talebinde bir `tools`array. istemci bu araçları kullanarak tam bir araç çağrı döngüsü çalıştırır. Bu, sunucuyu istemcinin modelini ReAct tarzı bir ajan döngüsünü barındırmaya izin verir.

```json
{
  "messages": [...],
  "tools": [
    {"name": "fetch_url", "description": "...", "inputSchema": {...}}
  ]
}
```

Müşteri döngüleri: örnek, çağrıldığında çalıştırma aracı, tekrar örnek, son asistan mesajını gönder. Bu, 1. yüzyıl 2026; SDK imzaları hala sürüklenebilir. Uyguladığınızda 2025-11-25 spesifikasyonunun müşteri / örnekleme bölümüne karşı onaylayın.

### - İnsanlık.

Müşteri, örneği çalıştırmadan önce sunucunun modelden ne yapmasını istediğini kullanıcıya göstermelidir. Kötü bir sunucu, kullanıcı oturumunu manipüle etmek için örneği kullanır ("kullanıcıya X deyin ki Y'yi tıklasınlar"). Kullanıcı onay diyalogi olarak Claude Desktop, VS Code ve Cursor yüzey örneği isteklerini reddedebilir.

2026'da yapılan bir fikir birliği: insan onayı olmadan örnek almak kırmızı bir bayrak. Gateways (Fase 13 · 17) düşük riskli örneklemeyi otomatik olarak onaylayabilir ve şüpheli herhangi bir şeyi otomatik olarak reddedebilir.

### API anahtarları olmayan sunucu barındırılmış döngüler

Kanonik kullanım durumunda: kendi LLM erişimi olmayan bir kod-sözleme MCP sunucusu.

1. Reklam yapısını yürüyün.
2. Arama .`sampling/createMessage`"Bu repo'nun amacını açıklayacak beş dosya seç".
3. Dosyaları oku.
4. Arama .`sampling/createMessage`Dosyaların içeriği ve "Repo'yu 3 paragrafla özetle".
5. Özetlemeyi bir olarak gönderin .`tools/call`Sonuç.

Sunucu hiçbir zaman LLM API'ye dokunmaz. Müşteri kullanıcıları kendi kimliklerini kullanarak tamamlamaları için ödeme yaparlar.

### Güvenlik riskleri (Bölüm 42'nin açıklaması, 2026 Q1)

- **Covert sampling.**Her zaman "işaret bağlamından kullanıcı e-postalarına cevap ver" ile örnekleme çağrısı yapan bir araç.
- **Resource theft via sampling.**Sunucu, istemciyi saldırganın pay yükünü özetlemesini ister, kullanıcıya faturalar verir.
- **Loop bombs.**Sunucu, sıkı bir döngü içinde örnekleme çağrısı yapıyor.

```figure
t3-sampling-flip
```

## Kullan

`code/main.py`simülasyonlu bir "summarize_repo" aracı iki örnekleme turunu (pick-file, sonra özetle) çağrıştırır ve sahte istemci konserve cevapları iade eder. Harnes gösterir:

- Sunucu gönderir `sampling/createMessage`- Evet .`modelPreferences`- Evet .
- Müşteri bir tamamlama gönderir.
- Sunucu döngüsünü devam ettiriyor.
- Aralık sınırlayıcı, araç çağrısı başına toplam örnekleme çağrılarını sınırlandırır.

Neye bakılır:

- Sunucu sadece bir aracı açığa çıkarır (`summarize_repo`); tüm akıl yürütme örnekleme çağrısında gerçekleşir.
- Model tercihleri, müşterinin model seçimini ağırlaştırır; ipuçları tercih edilen modeller listesi yapar.
- Çubuk açılıyor .`stopReason: "endTurn"`- Evet .
- - Evet .`max_samples_per_tool = 5`Limit kaçış döngüsünü yakalar.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-sampling-loop-designer.md`. LLM çağrılarına ( araştırma, özetleme, planlama) ihtiyaç duyan bir sunucu taraflı algoritma göz önüne alındığında, beceriler doğru model tercihleri, oran sınırları ve güvenlik onayları ile örnekleme tabanlı bir uygulamayı tasarlar.

## Egzersizler

1. Çık .`code/main.py`Değiş .`max_samples_per_tool`2'ye kadar ve oran sınırının sınırını izleyin.

2. SEP-1577 örneğe girme aracı varianını uygula: örneğe girme talebinde bir `tools`Array. Son tamamlama gönderilmeden önce bu araçları istemci taraflı döngü tarafından çalıştırıldığını kontrol edin.

3. İnsan-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-da-`sampling/createMessage`İptal edilen aramalar, yazılmış bir reddedilme gönderir.

4. Müşteri oturumuna göre tıklanmış bir kullanıcı oran sınırlayıcı ekleyin. Aynı kullanıcı tarafından aynı sunucu döngüleri bütçeyi paylaşmalıdır.

5. Bir tasarım`summarize_pdf`Bu, örnekleme kullanarak parçaları seçmek için kullanılacak bir araç.`modelPreferences.intelligencePriority`0.1 vs. 0.9'da davranış değişimi?

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Sampling | "Server-to-client LLM call" | Server asks client's model for a completion |
| `sampling/createMessage` | "The method" | JSON-RPC method for sampling requests |
| `modelPreferences` | "Model priorities" | Cost / speed / intelligence weights plus name hints |
| `includeContext` | "Cross-session leakage" | Soft-deprecated context inclusion mode |
| SEP-1577 | "Tools in sampling" | Allow tools inside sampling for server-hosted ReAct |
| Human-in-the-loop | "User confirms" | Client surfaces sampling request to user before running |
| Loop bomb | "Runaway sampling" | Server-side infinite sampling loop; client must rate-limit |
| Covert sampling | "Hidden reasoning" | Malicious server hides intent in sampling prompts |
| Resource theft | "Using user's LLM budget" | Server forces client to spend on sampling it does not want |
| `stopReason` | "Why generation halted" | `endTurn`, `stopSequence`, or `maxTokens` |

## Daha Fazla Okumak

- [MCP — Concepts: Sampling](https://modelcontextprotocol.io/docs/concepts/sampling) Örnek alma işinin yüksek düzeyde genel bakış
- [MCP — Client sampling spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling) Kanonik `sampling/createMessage`şekli
- [MCP — GitHub SEP-1577](https://github.com/modelcontextprotocol/modelcontextprotocol) Spec Evolution Örnekleme araçları önerisi (deney)
- [Unit 42 — MCP attack vectors](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/) Gizli örnekleme ve kaynak hırsızlığı örneği
- [Speakeasy — MCP sampling core concept](https://www.speakeasy.com/mcp/core-concepts/sampling) Müşteri tarafındaki kod örnekleriyle yürüyüş
