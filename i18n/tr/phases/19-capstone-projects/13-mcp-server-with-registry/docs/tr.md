# Capstone 13  MCP Server'ı Kayıt ve Yönetim ile

> Model Kontext Protokolü geleceğin bir parçası olmaya devam etti ve 2026'da standart araç kullanım özellikleri haline geldi. Anthropic, OpenAI, Google ve tüm büyük IDE gemisi MCP müşterileri. Pinterest, MCP sunucularının iç ekosistemini yayınladı. AAIF Registry, yetenek metadatalarını resmileştirdi `.well-known`AWS ECS referans stateless dağıtım yayınladı. Block'un kaz ajanı aynı protokolü barındırılmış bir asistanın içine koydu. 2026 üretim şekli: StreamableHTTP taşımacılığı, OAuth 2.1 kapsamları, OPA politika kapısı ve platform ekiplerinin sunucuları keşfetmesine, doğrulamasına ve etkinleştirmesine izin veren bir kayıt.

**Type:** Capstone
**Languages:** Python (server, via FastMCP) or TypeScript (@modelcontextprotocol/sdk), Go (registry service)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools and MCP), Phase 14 (agents), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:**P11 · P13 · P14 · P17 · P18
**Time:** 25 hours

## Sorun

MCP, araç kullanımı lingua franca haline geldi. Claude Code, Cursor 3, Amp, OpenCode, Gemini CLI ve her yönetilen ajan şimdi MCP sunucularını kullanıyor. Üretim zorlukları, sunucuların oluşturulması değil (FastMCP bunu kolaylaştırır), ancak işletme gereksinimleriyle birlikte ölçekte dağıtmak: kiracı başına OAuth kapsamları, yıkıcı araçlar üzerindeki OPA politikası, StreamableHTTP devletsiz ölçeklendirme, keşif için bir kayıt, araç çağrısı başına denetim günceleri. Pinterest'in iç MCP ekosisteminin ve AAIF Kayıt Spec'inin 2026 barını belirlediği.

10 iç araç (Postgres sadece okuma, S3 listing, Jira, Linear, Datadog, vb.) açığa çıkaran bir MCP sunucusu, platform keşfi için bir kayıtlı kullanıcı kullanımı ve yıkıcı araçlar için bir insan onaylı kapısı inşa edeceksiniz.

## Anlam

MCP 2026 revizyonu, StreamableHTTP'i varsayılan nakliye olarak görevlendirir. Daha önceki stdio- ve SSE biçiminden farklı olarak, StreamableHTTP varsayılan olarak devletsizdir: tek bir HTTP son noktası JSON-RPC isteklerini kabul eder, cevapları akışlar ve bildirimler için uzun ömürlü bağlantıları destekler.

Yetki, araç başına alanlar olan OAuth 2.1'dir.`jira:read`- Evet .`s3:list`- Evet .`postgres:query:readonly`MCP sunucusu, arama alanını yalnızca seans başlaması değil, araç çağrısı sırasında kontrol eder. Yüksek riskli araçlar için sunucu, alanı                                                                                                                                                                                                                                              `approved:by:human`Son N dakika içinde  bu yüksekliğin Slack inceleme kartından geldiği.

Kayıt ayrı bir hizmettir. her MCP sunucusu bir`.well-known/mcp-capabilities`Bu, bir araç açıklaması, taşıma URL'si, yazar gereksinimleri ile birlikte belgeler oluşturur.

## Mimarlık

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

## Yüküm

- Sunucu çerçevesini: FastMCP (Python) veya `@modelcontextprotocol/sdk`- Evet .
- Nakliye: StreamableHTTP üzerinden HTTPS (stateless)
- Auth: OAuth 2.1 ile SPIFFE / SPIRE üzerinden iş yükü kimliği
- Politikası: Araç başına OPA / Rego kuralları; talep üzerine politika kararları veren hizmet
- Kayıt: kendi kendine konutlanmış, tüketilen `.well-known/mcp-capabilities`Manifestolar
- İnsan onaylaması: Yıkıcı araçlar için Slack etkileşimli mesajı
- Uygulama: AWS ECS Fargate veya Fly.io, kiracı başına bir sunucu veya kiracı alanı ile paylaşılan
- Denetim: Aramalar için düzenli JSONL bir kiracılık çöpü

```figure
cf-mcp-gate
```

## Yapın

1. **Tool surface.**10 iç araç açın: Postgres sadece okuyucu sorgu, S3 listesi nesneleri, Jira arama/alış, Düzsel arama/alış, Datadog metrik sorgu, PagerDuty on-call arama, GitHub sadece okuyucu, Notion arama, Slack arama, Salesforce okuma. Her araç bir yazılmış şema ve bir kapsam etiketine sahiptir.

2. **FastMCP server.**Araçları monte edin. StreamableHTTP nakliyeyi yapılandırın. OAuth token introspection ve kapsam uygulanması için bir middleware ekleyin.

3. **OPA policy.**Araç başına Rego politikası: hangi alanlar çağırabilir, hangi PII redaksiyonu uygulanır, hangi payload boyutları sınırları uygulanır.

4. **Registry service.**Seçim yapan ayrı bir Go veya TS hizmeti `.well-known/mcp-capabilities`kayıtlı sunuculardan, JSON Schema ile onaylar ve bir liste / arama / onay / etkinleştirme / devre dışı bir kullanıcı arazisini ortaya çıkarır.

5. **Capability manifest.**Her sunucu açığa çıkarır `.well-known/mcp-capabilities`Bu listeye: araç listesi, yazarlık gereksinimleri, taşıma adresleri, sahip ekibi, SLO.

6. **Destructive tool separation.**Mutasyon durumunda bulunan araçlar (Jira yarat, Linear yarat, Postgres yaz) daha sıkı bir ot akışı olan ikinci bir MCP sunucusunda canlıdır: tokenler bir `approved:by:human`Slack kartı üzerinden 15 dakika içinde genişletilmiş bir alan.

7. **Audit log.**Kiracı başına sadece eklenen JSONL: `{timestamp, user, tool, args_redacted, response_redacted, outcome}`- Presidio'dan önce bilgiyi düzenle.

8. **Load test.**StreamableHTTP'de 100 eşzamanlı istemci. İkinci bir kopya ekleyerek yatay ölçeklendirmeyi göster; oturma yapışkanlığı olmadan yük dengeleyici yeniden dağıtımı göster.

9. **Conformance tests.**Resmi MCP uyumluluk paketini her iki sunucuya karşı çalıştırın.

## Kullan

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

## Gönder

`outputs/skill-mcp-server.md`OAuth 2.1 kapsamları ve OPA kaplamaları ile iç araçlar için üretim derecesindeki MCP sunucusu + kayıt + denetim katmanı.

| Weight | Criterion | How it is measured |
|:-:|---|---|
| 25 | Spec conformance | StreamableHTTP + capability manifest passes MCP conformance tests |
| 20 | Security | Scope enforcement, OPA coverage across every tool, secret hygiene |
| 20 | Observability | Per-tool-call audit log with PII redaction |
| 20 | Scale | 100-client load test horizontal scale demonstration |
| 15 | Registry UX | Discover / validate / enable-disable workflow |
| **100** | | |

## Egzersizler

1. Yeni bir araç ekleyin (Confluence arama). Ana sunucuya dokunmadan kayıt kayıt kayıtları doğrulama akışından gönderin.

2. Postgres sorgu sonuçlarını , isimli sütunlar içeren bir OPA politikası yazın `email`- Evet .`ssn`veya`phone`- Bir sonda sorusuyla egzersiz.

3. Yerel gecikme için StreamableHTTP vs stdio değerlendirme.

4. Kiracı başına kvote uygulanması: kiracı başına araç başına dakika başına maksimum N çağrı. İkinci bir OPA kuralıyla uygulanması.

5. MCP uyumluluk paketini [mcp-conformance-tests](https://github.com/modelcontextprotocol/conformance)ve her başarısızlığı düzeltmek.

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|-----------------|------------------------|
| StreamableHTTP | "2026 MCP transport" | Stateless HTTP + streaming; replaces SSE + stdio for networked servers |
| Capability manifest | "Well-known doc" | `.well-known/mcp-capabilities` with tool list, auth, transport URL |
| OPA / Rego | "Policy engine" | Open Policy Agent for authorizing tool calls against external rules |
| Scope elevation | "Approved-by-human" | Short-lived scope granted via Slack approval, required for destructive tools |
| Registry | "Tool discovery" | Service that indexes MCP servers from their capability manifests |
| Workload identity | "SPIFFE / SPIRE" | Cryptographic service identity for OAuth token issuance |
| Conformance suite | "Spec tests" | Official MCP test battery for StreamableHTTP + tool manifest correctness |

## Daha Fazla Okumak

- [Model Context Protocol 2026 Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) StreamableHTTP, yetenek metadataları, kayıt
- [AAIF MCP Registry spec](https://github.com/modelcontextprotocol/registry) 2026 kayıt özellikleri
- [AWS ECS reference deployment](https://aws.amazon.com/blogs/containers/deploying-model-context-protocol-mcp-servers-on-amazon-ecs/) Referans üretiminin yerleştirilmesi
- [Pinterest internal MCP ecosystem](https://www.infoq.com/news/2026/04/pinterest-mcp-ecosystem/) referans iç dağıtım
- [Block `goose` MCP usage](https://block.github.io/goose/) Referans ajan tüketimi modeli
- [FastMCP](https://github.com/jlowin/fastmcp) Python sunucu çerçevesini
- [Open Policy Agent](https://www.openpolicyagent.org/) Politika motor referansı
- [SPIFFE / SPIRE](https://spiffe.io) İş yükü kimlik referansı
