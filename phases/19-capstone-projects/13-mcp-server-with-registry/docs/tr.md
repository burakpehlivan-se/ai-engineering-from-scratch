# Capstone 13 — Kayıt Defteri (Registry) ve Yönetişim ile MCP Sunucusu

> Model Context Protocol 2026'da gelecek olmaktan çıkıp varsayılan tool-kullanım spesifikasyonu oldu. Anthropic, OpenAI, Google ve her büyük IDE MCP istemcileri yayınlıyor. Pinterest dahili MCP sunucuları ekosistemini yayınladı. AAIF Registry, `.well-known` konumunda yetenek meta verilerini resmileştirdi. AWS ECS referans durumsuz dağıtımı yayınladı. Block'un goose-agent aynı protokolü hosted bir asistanın içine yerleştirdi. 2026 üretim şekli: StreamableHTTP taşıma, OAuth 2.1 kapsamları, OPA politika geçidi ve platform ekiplerinin sunucuları keşfetmesine, doğrulamasına ve etkinleştirmesine izin veren bir kayıt defteri. Bunu uçtan uca inşa edin.

**Type:** Capstone
**Languages:** Python (sunucu, FastMCP ile) veya TypeScript (@modelcontextprotocol/sdk), Go (kayıt defteri hizmeti)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools and MCP), Phase 14 (agents), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:** P11 · P13 · P14 · P17 · P18
**Time:** 25 saat

## Problem

MCP, tool-kullanımının lingua franca'sı oldu. Claude Code, Cursor 3, Amp, OpenCode, Gemini CLI ve her yönetilen ajan artık MCP sunucularını tüketiyor. Üretim zorlukları sunucu yazmak (FastMCP bunu kolaylaştırır) değil, onları kurumsal gereksinimlerle ölçekte dağıtmaktır: kiracı başına OAuth kapsamları, yıkıcı tool'lar üzerinde OPA politikası, StreamableHTTP durumsuz ölçeklendirme, keşif için bir kayıt defteri, tool çağrısı başına denetim günlükleri. Pinterest'in dahili MCP ekosistemi ve AAIF Registry spesifikasyonu 2026 çıtasını belirledi.

10 dahili tool (yalnızca-okunur Postgres, S3 listeleme, Jira, Linear, Datadog vb.) açığa çıkaran bir MCP sunucusu, platform keşfi için bir kayıt defteri arayüzü ve yıkıcı tool'lar için bir insan-onay kapısı inşa edeceksiniz. Yük testi, StreamableHTTP yatay ölçeklendirmesini gösterir. Denetim izi, kurumsal bir güvenlik incelemesini karşılar.

## Concept

MCP 2026 revizyonu, varsayılan taşıma olarak StreamableHTTP'yi zorunlu kılar. Daha önceki stdio-ve-SSE şeklinden farklı olarak, StreamableHTTP varsayılan olarak durumsuzdur: tek bir HTTP uç noktası JSON-RPC isteklerini kabul eder, yanıtları akıtır ve bildirimler için uzun-ömürlü bağlantıları destekler. Durumsuz, bir yük dengeleyicinin arkasında yatay olarak ölçeklenebilir demektir.

Yetkilendirme, tool-başına kapsamlarla OAuth 2.1'dir. Bir belirteç `jira:read`, `s3:list`, `postgres:query:readonly` gibi kapsamları taşır. MCP sunucusu yalnızca oturum başlangıcında değil tool çağrısı zamanında da kapsamları kontrol eder. Yüksek-riskli tool'lar için, sunucu kapsamı son N dakika içinde `approved:by:human`'a yükseltilmemiş her çağrıyı reddeder — bu yükseltme bir Slack inceleme kartından gelir.

Kayıt defteri ayrı bir hizmettir. Her MCP sunucusu, tool manifestosu, taşıma URL'si, kimlik doğrulama gereksinimleri ile bir `.well-known/mcp-capabilities` belgesi sunar. Kayıt defteri yoklar, doğrular ve indeksler. Platform ekipleri, hangi tool'ların mevcut olduğunu, hangi kapsamları gerektirdiğini ve hangi ekiplerin sahip olduğunu görmek için kayıt defteri arayüzünü kullanır.

## Architecture

```
MCP client (Claude Code, Cursor 3, ...)
          |
          v
StreamableHTTP over HTTPS (JSON-RPC + streaming)
          |
          v
MCP server (FastMCP) behind load balancer
          |
   +------+------+---------+----------+------------+
   v             v         v          v            v
Postgres    S3 listing  Jira       Linear     Datadog
(read-only) (paged)     (read)     (read)     (query)
          |
   +------+-------------+
   v                    v
 OPA policy gate   destructive tool MCP (separate server)
                        |
                        v
                   human approval via Slack
                        |
                        v
                   audit log (append-only, per-tenant)

  registry service
     |
     v  GET /.well-known/mcp-capabilities from each server
     v
     UI: search / validate / enable-disable / ownership
```

#### Açıklama

Bu mimari bir MCP istemcisinden yıkıcı tool onayına kadar tam veri akışını gösterir. Claude Code veya Cursor 3 gibi istemciler HTTPS üzerinden StreamableHTTP ile bağlanır. Yük dengeleyicinin arkasındaki FastMCP sunucusu istekleri kabul eder ve onları çeşitli arka uç hizmetlerine yönlendirir: yalnızca-okunur Postgres, sayfalanmış S3 listeleme, Jira/Linear okuma, Datadog sorguları. Her çağrı bir OPA politika kapısından geçer. Yıkıcı tool'lar ayrı bir MCP sunucusunda yaşar; bu sunucu Slack üzerinden insan onayı gerektirir. Her tool çağrısı kiracı başına salt-ekleme bir denetim günlüğüne yazılır. Kayıt defteri hizmeti ayrıca tüm sunuculardan `.well-known/mcp-capabilities` belgelerini yoklar ve arama/doğrulama/etkinleştirme arayüzü sunar.

## Stack

- Sunucu çatısı: FastMCP (Python) veya `@modelcontextprotocol/sdk` (TypeScript)
- Taşıma: HTTPS üzerinden StreamableHTTP (durumsuz)
- Kimlik doğrulama: SPIFFE / SPIRE ile iş yükü kimliği aracılığıyla OAuth 2.1
- Politika: Tool başına OPA / Rego kuralları; istek başına politika karar hizmeti
- Kayıt defteri: Self-hosted, `.well-known/mcp-capabilities` manifestolarını tüketir
- İnsan onayı: Yıkıcı tool'lar için Slack etkileşimli mesajı
- Dağıtım: AWS ECS Fargate veya Fly.io, kiracı başına bir sunucu veya kiracı kapsamıyla paylaşılan
- Denetim: Çağrı soyu ile kiracı başına yapılandırılmış JSONL

## Build It

1. **Tool yüzeyi.** 10 dahili tool'u açığa çıkarın: Postgres yalnızca-okunur sorgu, S3 nesneleri listele, Jira ara/getir, Linear ara/getir, Datadog metrik sorgusu, PagerDuty nöbetçi araması, GitHub yalnızca-okunur, Notion arama, Slack arama, Salesforce okuma. Her tool'un tipli bir şeması ve bir kapsam etiketi vardır.

2. **FastMCP sunucusu.** Tool'ları bağlayın. StreamableHTTP taşımasını yapılandırın. OAuth belirteç inceleme ve kapsam uygulaması için bir ara yazılım ekleyin.

3. **OPA politikası.** Tool başına Rego politikası: hangi kapsamlar çağrıya izin verir, hangi PII redaksiyonu uygulanır, hangi yük boyutu sınırları geçerlidir. Her tool çağrısında çağrılan karar hizmeti.

4. **Kayıt defteri hizmeti.** Kayıtlı sunuculardan `.well-known/mcp-capabilities` belgelerini yoklayan, JSON Schema ile doğrulayan ve bir listeleme / arama / doğrulama / etkinleştirme-devre-dışı bırakma arayüzü sunan ayrı bir Go veya TS hizmeti.

5. **Yetenek manifestosu.** Her sunucu, `.well-known/mcp-capabilities` ile tool listesi, kimlik doğrulama gereksinimleri, taşıma URL'si, sahip ekip, SLO sunar.

6. **Yıkıcı tool ayrımı.** Durumu değiştiren tool'lar (Jira oluştur, Linear oluştur, Postgres yaz) daha sıkı bir kimlik doğrulama akışına sahip ikinci bir MCP sunucusunda yaşar: belirteçler 15 dakika içinde Slack kartı ile yükseltilmiş bir `approved:by:human` kapsamına sahip olmalıdır.

7. **Denetim günlüğü.** Kiracı başına salt-ekleme JSONL: `{timestamp, user, tool, args_redacted, response_redacted, outcome}`. Yazmadan önce Presidio ile PII redaksiyonu.

8. **Yük testi.** StreamableHTTP üzerinde 100 eşzamanlı istemci. İkinci bir çoğaltma ekleyerek yatay ölçeklendirmeyi gösterin; yük dengeleyicinin oturum yapışkanlığı olmadan yeniden dağıttığını gösterin.

9. **Uyum testleri.** Her iki sunucuya karşı resmi MCP uyum paketini çalıştırın. Tüm zorunlu bölümleri geçin.

## Use It

```
$ curl -H "Authorization: Bearer eyJhbGc..." \
       -X POST https://mcp.internal.example.com/ \
       -d '{"jsonrpc":"2.0","method":"tools/call",
            "params":{"name":"postgres.readonly","arguments":{"sql":"SELECT 1"}}}'
[registry]   capability validated: postgres.readonly v1.2
[policy]    scope postgres:query:readonly present; allowed
[audit]     logged: user=u42 tool=postgres.readonly outcome=ok
response:    { "result": { "rows": [[1]] } }
```

#### Açıklama

Bu örnek tipik bir MCP tool çağrısının uçtan uca akışını gösterir. İstemci bir OAuth taşıyıcı belirteciyle `postgres.readonly` tool'unu çağırır. Kayıt defteri tool'un yetenek bildirimini doğrular (sürüm 1.2). OPA politikası `postgres:query:readonly` kapsamının mevcut olduğunu kontrol eder ve çağrıyı izin verir. Sonuç denetim günlüğüne yazılır ve istemciye döndürülür. Bu desen her tool çağrısı için tekrarlanır; yıkıcı tool'lar aynı boru hattını Slack onayı ek bir adımla geçer.

## Ship It

`outputs/skill-mcp-server.md` teslim edilen şeyi tanımlar. OAuth 2.1 kapsamları ve OPA geçidi ile dahili tool'lar için üretim-düzeyinde bir MCP sunucusu + kayıt defteri + denetim katmanı.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Spesifikasyon uyumu | StreamableHTTP + yetenek manifestosu MCP uyum testlerini geçer |
| 20 | Güvenlik | Kapsam uygulaması, her tool'da OPA kapsamı, gizli bilgi hijyeni |
| 20 | Gözlemlenebilirlik | PII redaksiyonu ile tool çağrısı başına denetim günlüğü |
| 20 | Ölçek | 100-istemci yük testi yatay ölçek gösterimi |
| 15 | Kayıt defteri UX | Keşfet / doğrula / etkinleştir-devre-dışı bırak iş akışı |
| **100** | | |

## Exercises

1. Yeni bir tool (Confluence arama) ekleyin. Çekirdek sunucuya dokunmadan onu kayıt defteri doğrulama akışı üzerinden yayınlayın.

2. `email`, `ssn` veya `phone` adlı sütunları içeren Postgres sorgu sonuçlarını yeniden düzenleyen bir OPA politikası yazın. Bir sonda sorgusu ile çalıştırın.

3. Yerel gecikme üzerinde StreamableHTTP'yi stdio ile kıyaslayın. Çağrı başına p50/p95 raporlayın.

4. Kiracı başına kota uygulayın: kiracı başına tool başına dakikada maksimum N çağrı. İkinci bir OPA kuralı ile uygulayın.

5. [mcp-conformance-tests](https://github.com/modelcontextprotocol/conformance) paketinden MCP uyum paketini çalıştırın ve her hatayı düzeltin.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| StreamableHTTP | "2026 MCP taşıması" | Durumsuz HTTP + akış; ağa bağlı sunucular için SSE + stdio'nun yerini alır |
| Yetenek manifestosu | "Well-known belge" | Tool listesi, kimlik doğrulama, taşıma URL'si ile `.well-known/mcp-capabilities` |
| OPA / Rego | "Politika motoru" | Dış kurallara karşı tool çağrılarını yetkilendiren Open Policy Agent |
| Kapsam yükseltme | "İnsan-onaylı" | Slack onayı ile verilen kısa-ömürlü kapsam; yıkıcı tool'lar için gereklidir |
| Kayıt defteri | "Tool keşfi" | Yetenek manifestolarından MCP sunucularını indeksleyen hizmet |
| İş yükü kimliği | "SPIFFE / SPIRE" | OAuth belirteç verilmesi için kriptografik hizmet kimliği |
| Uyum paketi | "Spesifikasyon testleri" | StreamableHTTP + tool manifestosu doğruluğu için resmi MCP test pili |

## Further Reading

- [Model Context Protocol 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — StreamableHTTP, yetenek meta verileri, kayıt defteri
- [AAIF MCP Registry spec](https://github.com/modelcontextprotocol/registry) — 2026 kayıt defteri spesifikasyonu
- [AWS ECS reference deployment](https://aws.amazon.com/blogs/containers/deploying-model-context-protocol-mcp-servers-on-amazon-ecs/) — referans üretim dağıtımı
- [Pinterest internal MCP ecosystem](https://www.infoq.com/news/2026/04/pinterest-mcp-ecosystem/) — referans dahili dağıtım
- [Block `goose` MCP usage](https://block.github.io/goose/) — referans ajan tüketim deseni
- [FastMCP](https://github.com/jlowin/fastmcp) — Python sunucu çatısı
- [Open Policy Agent](https://www.openpolicyagent.org/) — politika motoru referansı
- [SPIFFE / SPIRE](https://spiffe.io) — iş yükü kimliği referansı
