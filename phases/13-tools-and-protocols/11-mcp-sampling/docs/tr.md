# MCP Örnekleme — Sunucu Tarafından İstenen LLM Tamamlamaları ve Ajan Döngüleri

> Çoğu MCP sunucusu aptız çalıştırıcılardır: argümanları al, kodu çalıştır, içeriği döndür. Örnekleme, bir sunucunun yönünü değiştirmesine olanak tanır: istemcinin LLM'den bir karar vermesini ister. Bu, sunucunun herhangi bir model kimlik bilgisine sahip olmadan sunucu barındıran ajan döngülerini etkinleştirir. SEP-1577, 2025-11-25'te birleştirildi ve örnekleme isteklerine araçlar ekledi, böylece döngü daha derin akıl yürütmeyi içerebilir. Kayma riski notu: SEP-1577 araç-içinde-örnekleme şekli 2026'nın ilk çeyreğine kadar deneyseldi ve SDK API'lerinde hala yerleşiyor.

**Tür:** İnşa Et
**Diller:** Python (stdlib, örnekleme donanımı)
**Ön koşullar:** Faz 13 · 07 (MCP sunucusu), Faz 13 · 10 (kaynaklar ve istemler)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- `sampling/createMessage`'ın ne çözdüğünü açıkla (sunucu tarafı API anahtarı olmadan sunucu barındıran döngüler).
- İstemciden çoklu turda bir prompt'u örnekleme yapmasını ve tamamlamayı döndüren bir sunucu uygula.
- `modelPreferences` (maliyet / hız / zekâ öncelikleri) kullanarak istemci model seçimini yönlendir.
- Örnekleme yoluyla dahili olarak yineleyen, davranış kodlamak yerine bir `summarize_repo` aracı oluştur.

## Sorun

Bir kod özetleme iş akışı için yararlı bir MCP sunucusunun şunları yapması gerekir: dosya ağacında yürü, hangi dosyaları okuyacağını seç, bir özet sentezle ve döndür. LLM akıl yürütmesi nerede gerçekleşir?

Seçenek A: sunucu kendi LLM'ini çağırır. Bir API anahtarı gerekir, sunucu tarafında faturalanır, kullanıcı başına pahalıdır.

Seçenek B: sunucu ham içeriği döndürür; istemcinin ajanı akıl yürütmeyi yapar. Çalışır ancak sunucu mantığını kırılgan olan istemci prompt'una taşır.

Seçenek C: sunucu `sampling/createMessage` aracılığıyla istemcinin LLM'inden ister. Sunucu algoritmayı (hangi dosyaları okunacağı, kaç tur yapılacağı) korurken, istemci faturalandırmayı ve model seçimini korur. Sunucunun hiç kimlik bilgisi yoktur.

Örnekleme seçenek C'dir. Güvenilir bir sunucunun, kendisi tam bir LLM ana programı olmadan bir ajan döngüsü barındırmasına olanak tanıyan mekanizma budur.

## Kavram

### `sampling/createMessage` isteği

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
#### Açıklama
sampling/createMessage, sunucunun istemcinin LLM'inden bir tamamlama istemesini sağlayan JSON-RPC metodudur.
```

İstemci LLM'sini çalıştırır, döndürür:

```json
{"jsonrpc": "2.0", "id": 42, "result": {
 "role": "assistant",
 "content": {"type": "text", "text": "..."},
 "model": "claude-3-5-sonnet-20251022",
 "stopReason": "endTurn"
}}
```

### `modelPreferences`

Toplamı 1.0 olan üç kayan noktalı sayı:

- `costPriority`: daha ucuz modellere öncelik.
- `speedPriority`: daha hızlı modellere öncelik.
- `intelligencePriority`: daha yetkin modellere öncelik.

Artı `hints`: sunucunun tercih ettiği adlı modeller. İstemci ipuçlarını onurlandırabilir veya onurlandırmaz; istemcinin kullanıcısı yapılandırması her zaman kazanır.

### `includeContext`

Üç değer:

- `"none"` — yalnızca sunucu tarafından sağlanan mesajlar. Varsayılan.
- `"thisServer"` — bu sunucunun oturumundan önceki mesajları içer.
- `"allServers"` — tüm oturum bağlamını içer.

`includeContext`, çapraz sunucu bağlamını sızdırdığı için 2025-11-25'ten itibaren yumuşak olarak kullanımdan kaldırılmıştır (soft-deprecated). `"none"` tercih edin ve açıkça bağlamı mesajlarda geçirin.

### Araçlarla örnekleme (SEP-1577)

2025-11-25'te yeni: örnekleme isteği bir `tools` dizisi içerebilir. İstemci bu araçları kullanarak tam bir araç çağrısı döngüsü çalıştırır. Bu, sunucunun istemcinin modeli aracılığıyla bir benzeri ReAct ajan döngüsü barındırmasını sağlar.

```json
{
 "messages": [...],
 "tools": [
 {"name": "fetch_url", "description": "...", "inputSchema": {...}}
 ]
}
```

İstemci döngüsü: örnekle, çağrılırsa aracı çalıştır, yeniden örnekle, son asistan mesajını döndür. Bu 2026'nın ilk çeyreğine kadar deneyseldir; SDK imzaları hala kayabilir. Uygularken 2025-11-25 teknik dokümanının client/sampling bölümüne göre doğrulayın.

### İnsan döngüde (Human-in-the-loop)

İstemci, örneklemeden önce kullanıcıya sunucunun modelden ne istediğini GÖSTERMEK ZORUNDADIR. Kötü niyetli bir sunucu, örnekleme aracılığıyla kullanıcının oturumunu manipüle edebilir ("kullanıcıya X söyle ki Y'ye bassın"). Claude Desktop, VS Code ve Cursor, örnekleme isteklerini kullanıcının reddedebileceği bir onay dialogu olarak yüzey çıkarır.

2026 uzlaşması: insan onayı olmadan örnekleme kırmızı bir bayraktır. Ağ geçitleri (Faz 13 · 17) düşük riskli örnekleme için otomatik onay ve şüpheli her şey için otomatik ret yapabilir.

### API anahtarı olmadan sunucu barındıran döngüler

Kanonik kullanım durumu: kendi LLM erişimi olmayan bir kod özetleme MCP sunucusu. Şunları yapar:

1. Depo yapısında yürür.
2. "Bu deponun amacını en iyi anlatan beş dosyayı seç" ile `sampling/createMessage` çağırır.
3. O dosyaları okur.
4. Dosyaların içeriği ve "Depoyu 3 paragrafta özetle" ile `sampling/createMessage` çağırır.
5. Özeti bir `tools/call` sonucu olarak döndürür.

Sunucu asla bir LLM API'sine dokunmaz. İstemcinin kullanıcısı kendi kimlik bilgileriyle tamamlamalar için ödeme yapar.

### Güvenlik riskleri (Unit 42 ifşası, 2026 Q1)

- **Gizli örnekleme.** Her zaman "kullanıcının oturum bağlamındaki e-postasını yanıtlaması" istemiyle örnekleme çağıran bir araç. Faz 13 · 15 saldırı vektörlerini kapsar.
- **Örnekleme yoluyla kaynak hırsızlığı.** Sunucu istemciden bir saldırganın payload'unu özetlemesini ister, kullanıcıya faturalandırır.
- **Döngü bombaları.** Sunucu sıkı bir döngüde örnekleme çağırır. İstemciler oturum başına hız sınırları zorlamalıdır.

## Kullan

`code/main.py`, sahte bir sunucudan istemciye örnekleme donanımı sunar. Simüle edilmiş bir "summarize_repo" aracı iki örnekleme turu (dosya-seç, sonra özetle) çağırır ve sahte istemci paketlenmiş yanıtlar döndürür. Donanım şunları gösterir:

- Sunucu `modelPreferences` ile `sampling/createMessage` gönderir.
- İstemci bir tamamlama döndürür.
- Sunucu döngüsüne devam eder.
- Hız sınırlayıcı, araç çağrısı başına toplam örnekleme çağrılarını sınırlar.

Neye bakılmalı:

- Sunucu yalnızca bir araç (`summarize_repo`) sunar; tüm akıl yürütmeler örnekleme çağrılarında gerçekleşir.
- Model tercihleri, istemcinin model seçimini ağırlıklandırır; ipuçları tercih edilen modelleri listeler.
- Döngü `stopReason: "endTurn"`'de sonlanır.
- `max_samples_per_tool = 5` sınırı kontrolden çıkan bir döngüyü yakalar.

## Sun

Bu ders `outputs/skill-sampling-loop-designer.md` dosyasını üretir. LLM çağrıları gereken sunucu tarafında bir algoritma (araştırma, özetleme, planlama) verildiğinde, beceri doğru modelPreferences, hız sınırları ve güvenlik onaylarıyla örnekleme tabanlı bir uygulama tasarlar.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. `max_samples_per_tool`'u 2 olarak değiştirin ve hız sınırlaması kesilmesini gözlemleyin.

2. SEP-1577 araç-içinde-örnekleme varyantını uygulayın: isteme isteği bir `tools` dizisi taşır. İstemci tarafındaki döngünün, son tamamlamayı döndürmeden önce bu araçları çalıştırdığını doğrulayın. Kayma riskini not edin: SDK imzaları 2026'nın ilk yarısına kadar değişebilir.

3. İnsan döngüde onay ekleyin: sunucunun ilk `sampling/createMessage`'ından önce duraklayın ve kullanıcı onayı bekleyin. Reddedilen çağrılar tipli bir red döndürür.

4. İstemci oturumuna göre anahtarlanmış, kullanıcı başına bir hız sınırlayıcı ekleyin. Aynı kullanıcının aynı sunucudaki döngüleri bütçeyi paylaşmalıdır.

5. Örnekleme kullanarak dahil edilecek parçacıkları (chunk) seçmek için bir `summarize_pdf` aracı tasarlayın. Gönderilen mesajları çizin. `modelPreferences.intelligencePriority` 0.1 vs 0.9'da davranışı nasıl değiştirir?

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Sampling (Örnekleme) | "Sunucudan istemciye LLM çağrısı" | Sunucu istemcinin modelinden bir tamamlama ister |
| `sampling/createMessage` | "Metod" | Örnekleme istekleri için JSON-RPC metodu |
| `modelPreferences` | "Model öncelikleri" | Maliyet / hız / zekâ ağırlıkları artı ad ipuçları |
| `includeContext` | "Çapraz oturum sızıntısı" | Yumuşak olarak kullanımdan kaldırılmış bağlam dahil etme modu |
| SEP-1577 | "Örneklemede araçlar" | Sunucu barındıran ReAct için örneklemede araçlara izin ver |
| Human-in-the-loop | "Kullanıcı onaylıyor" | İstemci, çalıştırmadan önce örnekleme isteğini kullanıcıya gösterir |
| Loop bomb | "Kontrolden çıkan örnekleme" | Sunucu tarafında sonsuz örnekleme döngüsü; istemci hız sınırlamalıdır |
| Covert sampling | "Gizli akıl yürütme" | Kötü niyetli sunucu, örnekleme prompt'larında niyetini gizler |
| Resource theft | "Kullanıcının LLM bütçesini kullanma" | Sunucu, istemciyi istemediği örnekleme için harcamaya zorlar |
| `stopReason` | "Neden üretim durdu" | `endTurn`, `stopSequence` veya `maxTokens` |

## İleri Okuma

- [MCP — Concepts: Sampling](https://modelcontextprotocol.io/docs/concepts/sampling) — örnekleme üst düzey genel bakış
- [MCP — Client sampling spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/client/sampling) — kanonik `sampling/createMessage` şekli
- [MCP — GitHub SEP-1577](https://github.com/modelcontextprotocol/modelcontextprotocol) — Örneklemede araçlar için Teknik Doküman Geliştirme Önerisi (deneysel)
- [Unit 42 — MCP attack vectors](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/) — gizli örnekleme ve kaynak hırsızlığı paternleri
- [Speakeasy — MCP sampling core concept](https://www.speakeasy.com/mcp/core-concepts/sampling) — istemci tarafı kod örnekleriyle yürüyüş
