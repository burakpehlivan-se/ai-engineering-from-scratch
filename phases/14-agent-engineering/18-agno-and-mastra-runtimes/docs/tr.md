# Agno ve Mastra: Production Runtime'ları

> Agno (Python) ve Mastra (TypeScript) 2026 production runtime eşleşmesidir. Agno mikrosaniye düzeyinde agent başlatmayı ve durumsuz FastAPI arka uçlarını hedefler. Mastra agent'ları, araçları, workflow'ları, birleşik model yönlendirmesini ve Vercel AI SDK substratı üzerinde bileşik depolamayı sunar.

**Tür:** Öğren
**Diller:** Python, TypeScript
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 14 · 13 (LangGraph)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Agno'nun performans hedeflerini ve ne zaman önemli olduklarını tanımlayın.
- Mastra'nın üç temel unsurunu — Agents, Tools, Workflows — ve desteklenen sunucu adaptörlerini adlandırın.
- Neden durumsuz session-scoped bir FastAPI arka ucunun önerilen Agno production yolu olduğunu açıklayın.
- Verilen bir stack için Agno vs Mastra seçin (Python-öncelikli vs TypeScript-öncelikli).

## Problem

LangGraph, AutoGen, CrewAI ağırlıklı framework'lerdir. "Sadece agent döngüsü, hızlı, benim runtime'ımda" isteyen ekipler Agno'ya (Python) veya Mastra'ya (TypeScript) başvurur. İkisi de framework'ün sahiplendiği temel unsurların bir kısmını ham hız ve çevre stack ile daha sıkı bir uyum karşılığında takas eder.

## Kavram

### Agno

- Python runtime'ı, eskiden Phi-data.
- "Graf, zincir veya karmaşık kalıplar yok — saf python."
- Dokümanlardan performans hedefleri: ~2μs agent başlatma, agent başına ~3.75 KiB bellek, ~23 model sağlayıcısı.
- Production yolu: durumsuz session-scoped FastAPI arka ucunu. Her istek taze bir agent başlatır; oturum durumu DB'de yaşar.
- Native multimodal (metin, görüntü, ses, video, dosya) ve agentic RAG.

Hız hedefleri saniyede binlerce kısa ömürlü agent'ınız olduğunda önemlidir (sohbet fan-in, değerlendirme pipeline'ları). Bir agent 10 dakika çalıştığında daha az önemlidir.

### Mastra

- TypeScript, Vercel AI SDK üzerine inşa edilmiş.
- Üç temel unsur: **Agents**, **Tools** (Zod tipli), **Workflows**.
- Unified Model Router — Mart 2026 itibarıyla 94 sağlayıcıda 3.300+ model.
- Bileşik depolama: hafıza, workflow'lar, gözlem farklı arka uçlara; gözlem için ölçekленده ClickHouse önerilir.
- Apache 2.0, kaynak-kodlu enterprise lisansı altında `ee/` dizinleriyle.
- Express, Hono, Fastify, Koa için sunucu adaptörleri; birinci sınıf Next.js ve Astro entegrasyonu.
- Hata ayıklama için Mastra Studio (localhost:4111) sunar.
- 1.0'da (Ocak 2026) 22k+ GitHub yıldızı, 300k+ haftalık npm indirme.

### Konumlandırma

Hiçbiri LangGraph olmaya çalışmıyor. Şu alanlarda yarışırlar:

- **Dil uyumu.** Python-öncelikli ekipler için Agno; TypeScript-öncelikli için Mastra.
- **Runtime ergonomisi.** Agno = sıfıra yakın overhead; Mastra = Vercel ekosistemiyle entegre.
- **Gözlem.** İkisi de Langfuse/Phoenix/Opik (Ders 24) ile entegre ancak Mastra Studio birinci taraf.

### Hangisini ne zaman seçmeli

- **Agno** — Python arka ucunuz, çok sayıda kısa ömürlü agent, güçlü performans gereksinimleri, FastAPI mağazası.
- **Mastra** — TypeScript arka ucunuz, Next.js / Vercel deploy, birleşik çoklu-sağlayıcı model yönlendirmesi, Zod tipli araçlar.
- **LangGraph** (Ders 13) — dayanıklı state ve açık graf akıl yürütmesi ham hızdan daha önemli olduğunda.
- **OpenAI / Claude Agent SDK** — sağlayıcının ürünleştirilmiş şeklini istediğinizde (Ders 16-17).

### Bu kalıp nerede yanlış gider

- **Performans için performans.** "2μs" kulağa hoş geldiği için Agno'yu seçmek ancak iş yükü istek başına yavaş bir agent çağrısıysa. Overhead darboğaz değil.
- **Ekosisteme kilitlenme.** Mastra'nın Vercel tadında entegrasyonu Vercel'de artı, başka yerde eksi.
- **Enterprise lisans kafa karışıklığı.** Mastra'nın `ee/` dizinleri Apache 2.0 değil, kaynak-kodlu. Çatalama (fork) planlıyorsanız lisansları okuyun.

## İnşa Et

Bu ders ağırlıklı olarak karşılaştırmalıdır — her iki framework'e de adalet yapacak tek bir kod artefaktı yoktur. `code/main.py`'deki yan yana oyuncak koda bakın: "bir agent çalıştır, çıktıyı akıt, oturumu kalıcı hale getir" akışı iki kez uygulanmış (bir kez Agno şeklinde, bir kez Mastra şeklinde).

Çalıştırın:

```bash
python3 code/main.py
```

İki yapısal olarak farklı ancak işlevsel olarak eşdeğer trace.

## Kullan

- **Agno** — hız ve FastAPI şekli gerektiren Python arka ucunuz.
- **Mastra** — çok sayıda sağlayıcı ve workflow temel unsurlarıyla TypeScript arka ucunuz.
- Her ikisi de birinci taraf gözlem kancaları sunar. Her ikisi de Langfuse ile entegre olur.

## Teslim Et

`outputs/skill-runtime-picker.md` stack, gecikme bütçesi ve operasyonel şekle göre Agno, Mastra, LangGraph veya bir sağlayıcı SDK seçer.

## Alıştırmalar

1. Agno dokümanlarını okuyun. Stdlib ReAct döngüsünü (Ders 01) Agno'ya taşıyın. Ne kayboldu? Ne kaldı?
2. Mastra dokümanlarını okuyun. Aynı döngüyü Mastra'ya taşıyın. Araç tiplemesinde (Zod vs hiç) ne değişti?
3. Benchmark: stack'inizde agent başlatma gecikmesini ölçün. Agno'nun 2μs'i iş yükünüz için önemli mi?
4. Bir geçiş tasarlayın: Python'da CrewAI çalıştırıyorsanız, Agno'ya geçtiğinizde ne kırılır?
5. Mastra'nın `ee/` lisans şartlarını okuyun. Açık kaynak çatalamasını etkileyecek kısıtlamalar nelerdir?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Agno | "Hızlı Python agent'ları" | Durumsuz session-scoped agent runtime'ı |
| Mastra | "Vercel AI SDK üzerinde TypeScript agent'ları" | Agents + Tools + Workflows + Model Router |
| Unified Model Router | "Çoklu-sağlayıcı erişimi" | 94 sağlayıcıda 3.300+ model için tek istemci |
| Composite storage | "Çoklu arka uç" | Hafıza/workflow'lar/gözlem her biri farklı bir depoya |
| Mastra Studio | "Yerel hata ayıklayıcı" | Agent'ları içe gözlemlemek için localhost:4111 UI'ı |
| Source-available | "OSS değil" | Kaynak okumaya izin veren ancak ticari kullanımı kısıtlayan lisans |

## İleri Okuma

- [Agno Agent Framework docs](https://www.agno.com/agent-framework) — performans hedefleri, FastAPI entegrasyonu
- [Mastra docs](https://mastra.ai/docs) — temel unsurlar, sunucu adaptörleri, Model Router
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — durumlu graf alternatifi
- [Comet Opik](https://www.comet.com/site/products/opik/) — Mastra entegrasyonları tarafından atıfta bulunulan gözlem karşılaştırmaları
