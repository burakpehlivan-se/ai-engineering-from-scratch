# Bitirme Projesi — Eksiksiz Bir Araç Ekosistemi İnşa Edin

> Faz 13 her parçayı öğretti. Bu bitirme projesi, bunları bir üretim şekilli sistemde bir araya getirir: araçlar + kaynaklar + istemler + görevler + UI ile bir MCP sunucusu, kenarda OAuth 2.1, bir RBAC ağ geçidi, çoklu sunucu istemcisi, bir A2A alt ajan çağrısı, OTel izleme, CI'da araç zehirleme algılaması ve bir AGENTS.md + SKILL.md paketi. Sonunda her mimari seçimi savunabilirsiniz.

**Tür:** İnşa Et
**Diller:** Python (stdlib, uçtan uca ekosistem donanımı)
**Ön koşullar:** Faz 13 · 01 ila 21
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Araçlar, kaynaklar, istemler ve `ui://` uygulaması ile bir MCP sunucusu oluştur.
- Sunucuyu RBAC ve sabitlenmiş hash'ler zorlayan bir OAuth 2.1 ağ geçidinin önüne koy.
- OTel GenAI nitelikleriyle uçtan uca iz yapan bir çoklu sunucu istemcisi yaz.
- İş yükünün bir kısmını bir A2A alt ajana devret; opaklığın korunduğunu doğrula.
- Tüm yığını AGENTS.md + SKILL.md ile paketle, böylece diğer ajanlar onu sürebilsin.

## Sorun

"Araştırma ve rapor" sistemini yayınlayın:

- Kullanıcı sorar: "2026'da ajan protokolleri hakkında en çok atıfta bulunulan üç arXiv makalesini özetle."
- Sistem: MCP aracılığıyla arXiv'da ara; makale özetlemesini özel bir yazan ajana A2A ile devret; sonuçları topla; etkileşimli bir raporu bir MCP Apps `ui://` kaynağı olarak oluştur; her adımı OTel'de günlüğe kaydet.

Faz 13'teki tüm primitifler burada. Bu bir oyuncak değil — Anthropic (Claude Research ürünü), OpenAI (Apps SDK'lı GPT'ler) ve üçüncü taraflar tarafından 2026'da yayınlanan araştırma asistanı sistemleri tam olarak bu şekle sahiptir.

## Kavram

### Mimari

```
[kullanıcı] -> [istemci] -> [ağ geçidi (OAuth 2.1 + RBAC)] -> [araştırma MCP sunucusu]
 |
 +- MCP aracı: arxiv_search (saf)
 +- MCP kaynağı: notes://recent
 +- MCP istemi: /research_topic
 +- MCP görevi: generate_report (uzun)
 +- MCP Apps UI: ui://report/current
 +- A2A çağrısı: writer-agent (tasks/send)
 |
 +- OTel GenAI aralıkları
```

### İz hiyerarşisi

```
agent.invoke_agent
 ├── llm.chat (başlatma)
 ├── mcp.call -> tools/call arxiv_search
 ├── mcp.call -> resources/read notes://recent
 ├── mcp.call -> prompts/get research_topic
 ├── a2a.tasks/send -> writer-agent
 │ └── görev geçişleri (opak içler)
 ├── mcp.call -> tools/call generate_report (görev-artırılmış)
 │ └── tasks/status sorgulaması
 │ └── tasks/result (tamamlandı, ui:// kaynağı döndürür)
 └── llm.chat (son sentez)
```

Tek bir iz id'si. Her aralık doğru `gen_ai.*` niteliklerine sahiptir.

### Güvenlik duruşu

- OAuth 2.1 + PKCE, kaynak göstergesi ile hedef kitlesini ağ geçidine sabitleyen.
- Ağ geçidi yukarı akış kimlik bilgilerini tutar; kullanıcı asla görmez.
- RBAC: `alice` `research:read`, `research:write`'a sahip, tüm araçları çağırabilir. `bob` `research:read`'e sahip, `generate_report`'u çağıramaz.
- Sabitlenmiş açıklama manifestosu: araç hash'leri değişen her sunucu düşürülür.
- İki Kuralı denetimi: hiçbir araç güvenilmeyen girdi, hassas veri ve sonuçlu eylemi birleştirmiyor.

### Oluşturma (Rendering)

Son `generate_report` görevi içerik blokları artı bir `ui://report/current` kaynağı döndürür. İstemcinin ana programı (Claude Desktop vb.) etkileşimli panoyu sandboxlanmış bir iframe'de oluşturur. Pano sıralanmış bir makale listesi, alıntı sayıları ve kullanıcının tıkladığı herhangi bir makale için `host.callTool('summarize_paper', {arxiv_id})` çağıran bir düğme içerir.

### Paketleme

Tümü şu şekilde yayınlanır:

```
research-system/
 AGENTS.md # proje kuralları
 skills/
 run-research/
 SKILL.md # üst düzey iş akışı
 servers/
 research-mcp/ # MCP sunucusu
 pyproject.toml
 src/
 agents/
 writer/ # A2A ajanı
 gateway/
 config.yaml # RBAC + sabitlenmiş manifest
```

Kullanıcılar `docker compose up` ile dağıtır. Claude Code, Cursor, Codex ve opencode kullanıcıları `run-research` yeteneğini çağırarak sistemi sürebilir.

### Her Faz 13 dersinin katkısı

| Ders | Bitirme projesinin kullandığı |
|--------|------------------------|
| 01-05 | Araç arayüzü, sağlayıcı taşınabilirliği, paralel çağrılar, şemalar, denetleme |
| 06-10 | MCP primitifleri, sunucu, istemci, taşıyıcılar, kaynaklar + istemler |
| 11-14 | Örnekleme, kökler + ricada bulunma, asenkron görevler, `ui://` uygulamaları |
| 15-17 | Araç zehirleme, OAuth 2.1, ağ geçidi + kayıt |
| 18 | A2A alt ajan devretmesi |
| 19 | OTel GenAI izleme |
| 20 | LLM katmanı için yönlendirme ağ geçidi |
| 21 | SKILL.md + AGENTS.md paketleme |

## Kullan

`code/main.py`, önceki derslerin paternlerini çalıştırılabilir bir demoda bir araya getirir. Tümü stdlib, tümü süreç içinde, böylece uçtan uca okuyabilirsiniz. Araştırma ve rapor senaryosu için tam akışı çalıştırır: ağ geçidiyle el sıkışma, OAuth 2.1 simüle edilmiş, tools/list birleştirilmiş, generate_report bir görev olarak, writer'a A2A çağrısı, ui:// kaynağı döndürülmüş, OTel aralıkları üretilmiş.

Neye bakılmalı:

- Her atlama boyunca tek bir iz id'si.
- Ağ geçidi politikası ikinci kullanıcının yazmasını engelliyor.
- Görev yaşam döngüsü working → completed ve hem metni hem de ui:// içeriğini döndürüyor.
- A2A çağrısının iç durumu orkestratör için opak.
- AGENTS.md ve SKILL.md, iş akışını tekrarlamak için başka bir ajanın ihtiyaç duyduğu tek dosyalar.

## Sun

Bu ders `outputs/skill-ecosystem-blueprint.md` dosyasını üretir. Bir ürün ihtiyacı (araştırma, özetleme, otomasyon) verildiğinde, beceri eksiksiz mimariyi üretir: hangi MCP primitifleri, hangi ağ geçidi kontrolleri, hangi A2A çağrıları, hangi telemetri, hangi paketleme.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. Tek iz id'sini ve aralıkların nasıl iç içe geçtiğini not edin. Demonun Faz 13'ten kaç primitife dokunduğunu sayın.

2. Demoyu genişletin: ikinci bir arka plan MCP sunucusu (ör. `bibliography`) ekleyin ve ağ geçidinin araçlarını aynı ad前三refixüne birleştirdiğini doğrulayın.

3. Sahte A2A yazan ajanı bir alt süreçte çalışan gerçek bir ajanla değiştirin. Ders 19 donanımını kullanın.

4. Yönlendirme ağ geçidinde orkestratör ile LLM arasında bir Kişisel Bilgi sansürleme adımı ekleyin. Kullanıcı sorgusundaki e-postaların temizlendiğini doğrulayın.

5. Bu sistemi sürdürecek bir takım arkadaşınız için bir AGENTS.md yazın. Beş dakikadan kısa sürede okunabilmeli ve bitirme projesini Cursor veya Codex'te sürebilmek için gereken her şeyi vermelidir.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Bitirme projesi (Capstone) | "Faz-13 entegrasyon demosu" | Her primitifi kullanan uçtan uca sistem |
| Araştırma ve rapor | "Senaryo" | Ara, özetle, oluştur paterni |
| Ekosistem | "Tüm parçalar bir arada" | Sunucu + istemci + ağ geçidi + alt ajan + telemetri + paket |
| İz hiyerarşisi | "Tek iz id'si" | Her atlamanın aralığı izi paylaşır; ebeveyn-çocuk aralık id'leriyle |
| Ağ geçidi tarafından verilen token | "Dolaylı auth" | İstemci yalnızca ağ geçidinin jetonunu görür; ağ geçidi yukarı akış kimlik bilgilerini tutar |
| Birleştirilmiş ad前三refixü | "Tüm araçlar düz listede" | Ağ geçidinde çoklu sunucu birleştirme, çakışmada前三refix |
| Opaklık sınırı | "A2A çağrısı içleri gizler" | Alt ajanın akıl yürütmesi orkestratör için görünmez |
| Üç katmanlı yığın | "AGENTS.md + SKILL.md + MCP" | Proje bağlamı + iş akışı + araçlar |
| Derinlemesine savunma | "Birden fazla güvenlik katmanı" | Sabitlenmiş hash'ler, OAuth, RBAC, İki Kuralı, denetim günlüğü |
| Teknik doküman uyumluluk matrisi | "Teknik dokümanın gerektirdiğini sunduğumuz" | Teslim edilebilirleri 2025-11-25 gereksinimleriyle eşleyen kontrol listesi |

## İleri Okuma

- [MCP — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — birleşik referans
- [MCP blog — 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — protokolün nereye gittiği
- [a2a-protocol.org](https://a2a-protocol.org/latest/) — A2A v1.0 referansı
- [OpenTelemetry — GenAI semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — kanonik izleme kuralları
- [Anthropic — Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) — üretim ajanı çalışma zamanı paternleri
