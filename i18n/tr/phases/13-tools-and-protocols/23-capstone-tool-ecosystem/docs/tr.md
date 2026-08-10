# Capstone  Tam bir Araç Ekosistemi Oluşturun

> Bu kapı taşı, tüm parçaları bir üretim şeklinde bir sisteme bağlar: araç + kaynak + istek + görev + UI ile bir MCP sunucusu, kenarda OAuth 2.1, bir RBAC geçit, bir çok sunucu istemcisi, bir A2A alt-astı çağrısı, bir koleksiyoncuya OTel izleme, CI'de araç zehirlenmesi tespit ve bir AGENTS.md + SKILL.md paketi.

**Type:** Build
**Languages:** Python (stdlib, end-to-end ecosystem harness)
**Prerequisites:** Phase 13 · 01 through 21
**Time:** ~120 minutes

## Öğrenme Hedefleri

- Bir MCP sunucusu oluşturup araçları, kaynakları, istekleri ve bir görevi bir `ui://`uygulama.
- RBAC ve sabitlenmiş hashleri zorlayan bir OAuth 2.1 geçidi ile sunucuya karşı.
- OTel GenAI özelliklerini sonundan sonuna kadar izleyen bir çok sunucu istemcisi yazın.
- Bir iş yükünün bir kısmını A2A alt-evciline aktarın; açıklığın korunmuş olduğunu kontrol edin.
- Tüm yığınları AGENTS.md + SKILL.md ile paketle, böylece diğer ajanlar onu kullanabilir.

## Sorun

"Araştırma ve raporlama" sistemini gönder:

- Kullanıcı soruyor: "Agent protokoller üzerine en çok alıntılanan 2026 arXiv makaleleri özetleyin".
- Sistem: arXiv'i MCP üzerinden aramak; A2A üzerinden uzman bir yazar ajanına makale özetini devretmek; toplam sonuçlar; bir etkileşimli rapor MCP Uygulamaları olarak oluşturmak `ui://`Kaynak; her adımı OTel'e kaydet.

Bu bir oyuncak değil  üretim araştırma-asistan sistemleri 2026 yılında Anthropic (Claude Research ürünü), OpenAI (GPT'ler ile Uygulama SDK) tarafından gönderilen ve üçüncü taraflar bu tam şekil sahip.

## Anlaşım

### Mimarlık

```
[user] -> [client] -> [gateway (OAuth 2.1 + RBAC)] -> [research MCP server]
                                                      |
                                                      +- MCP tool: arxiv_search (pure)
                                                      +- MCP resource: notes://recent
                                                      +- MCP prompt: /research_topic
                                                      +- MCP task: generate_report (long)
                                                      +- MCP Apps UI: ui://report/current
                                                      +- A2A call: writer-agent (tasks/send)
                                                      |
                                                      +- OTel GenAI spans
```

### İz hiyerarşi

```
agent.invoke_agent
 ├── llm.chat (kick off)
 ├── mcp.call -> tools/call arxiv_search
 ├── mcp.call -> resources/read notes://recent
 ├── mcp.call -> prompts/get research_topic
 ├── a2a.tasks/send -> writer-agent
 │    └── task transitions (opaque internals)
 ├── mcp.call -> tools/call generate_report (task-augmented)
 │    └── tasks/status polling
 │    └── tasks/result (completed, returns ui:// resource)
 └── llm.chat (final synthesis)
```

Bir iz kimliği.`gen_ai.*`- Bu özellikler.

### Güvenlik duruşu

- OAuth 2.1 + PKCE, kaynak göstergesiyle izleyicileri geçit kapısına bağlar.
- Gateway, yukarı akımlı kimlik bilgileri tutar; kullanıcı onları asla görmez.
- RBAC: `alice`- Evet .`research:read`- Evet .`research:write`, tüm araçları çağırabilir.`bob`- Evet .`research:read`, aramayı .`generate_report`- Evet .
- Pinned description manifest: araç hashleri değiştirilen herhangi bir sunucu düşürüldü.
- İkinci kural: hiçbir araç güvenilmeyen girişleri, hassas verileri ve sonuçta uygulanmış eylemleri birleştirmez.

### Sıfırlama

Sonuncusu .`generate_report`Görev içeriği bloklarını artı bir `ui://report/current`kaynak. Müşteri'nin sunucusu (Claude Desktop, vb.) etkileşimli araci tablosunu kum kutu iframe'de gösterir. Araci tablosu sıralanmış bir kağıt listesini, alıntı sayısını ve arama yapan bir düğmeyi içerir `host.callTool('summarize_paper', {arxiv_id})`Kullanıcı tıkladığı her kağıt için.

### Paketleme

Bütün bu şey şöyle:

```
research-system/
  AGENTS.md                     # project conventions
  skills/
    run-research/
      SKILL.md                  # the top-level workflow
  servers/
    research-mcp/               # the MCP server
      pyproject.toml
      src/
  agents/
    writer/                     # the A2A agent
  gateway/
    config.yaml                 # RBAC + pinned manifest
```

Kullanıcılar `docker compose up`Claude Code, Cursor, Codex ve Opencode kullanıcıları sistemleri kullanmak için `run-research`- Yetenek.

### 13. Fase derslerinin her birinin katkısı

| Lesson | What the capstone uses |
|--------|------------------------|
| 01-05 | Tool interface, provider-portability, parallel calls, schemas, linting |
| 06-10 | MCP primitives, server, client, transports, resources + prompts |
| 11-14 | Sampling, roots + elicitation, async tasks, `ui://` apps |
| 15-17 | Tool poisoning, OAuth 2.1, gateway + registry |
| 18 | A2A sub-agent delegation |
| 19 | OTel GenAI tracing |
| 20 | Routing gateway for the LLM layer |
| 21 | SKILL.md + AGENTS.md packaging |

```figure
t3-capstone-chain
```

## Kullan

`code/main.py`Tüm stdlib, tüm sürec içinde böylece onu sonuna kadar okuyabilirsiniz. Araştırma ve rapor senaryo için tam akış yürütür: geçitle el sıkışması, OAuth 2.1 simülasyonu, araçlar / listeler birleştirildi, bir görev olarak oluştur_report, A2A yazarı çağrısı, ui:// kaynak geri döndü, OTel uzadı yayınlandı.

Neye bakılır:

- Her atışta bir iz kimliği var.
- Giriş politikası ikinci bir kullanıcının yazmasını engeller.
- Görev yaşam döngüsü çalışmaya devam eder → tamamlanmış ve hem metin hem de ui:// içeriği geri verir.
- A2A çağrısının iç durumu orkeströr için açık değildir.
- AGENTS.md ve SKILL.md, başka bir ajansın iş akışını yeniden üretmek için ihtiyaç duyduğu tek dosyadır.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-ecosystem-blueprint.md`. Bir ürün ihtiyacı ( araştırma, özetleme, otomasyon) göz önüne alındığında, beceriler tüm mimariyi üretir: hangi MCP primitifleri, hangi geçit kontrolü, hangi A2A çağrısı, hangi telemetri, hangi ambalaj.

## Egzersizler

1. Çık .`code/main.py`Tek iz kimliği ve yuva genişliği not edin.

2. Demo'yu uzat: ikinci bir arka uç MCP sunucusu ekle (örneğin `bibliography`) ve geçit araçlarını aynı isim alanına birleştirdiğini onaylamak.

3. Sahte A2A yazarı ajanını alt işlemle çalışan gerçek bir ajanla değiştir.

4. Orkestratör ve LLM arasındaki yönlendirme geçidi'ne PII düzenleme adımını ekleyin. Kullanıcı sorgularında onay e-postaları silinir.

5. Bu sistemi koruyacak bir takım arkadaşınız için bir AGENTS.md yazın.

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Capstone | "Phase-13 integration demo" | End-to-end system using every primitive |
| Research and report | "The scenario" | Search, summarize, render pattern |
| Ecosystem | "All the pieces together" | Server + client + gateway + sub-agent + telemetry + package |
| Trace hierarchy | "Single trace id" | Every hop's span shares the trace; parent-child via span ids |
| Gateway-issued token | "Transitive auth" | Client sees only gateway's token; gateway holds upstream creds |
| Merged namespace | "All tools in one flat list" | Multi-server merge at the gateway, prefix-on-collision |
| Opacity boundary | "A2A call hides internals" | Sub-agent's reasoning invisible to orchestrator |
| Three-layer stack | "AGENTS.md + SKILL.md + MCP" | Project context + workflow + tools |
| Defense-in-depth | "Multiple security layers" | Pinned hashes, OAuth, RBAC, Rule of Two, audit log |
| Spec compliance matrix | "What we ship that the spec requires" | Checklist mapping deliverables to 2025-11-25 requirements |

## Daha Fazla Okumak

- [MCP — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) Konsolide edilmiş referans
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) Protokolün yönü
- [a2a-protocol.org](https://a2a-protocol.org/latest/) A2A v1.0 referansı
- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) Kanonik izleme konvensiyonları
- [Anthropic — Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) Üretim ajanı çalıştırma süresi
