# OpenAI Agents SDK: Handoffs, Guardrails, Tracing

> OpenAI Agents SDK, Responses API üzerine inşa edilmiş hafif çoklu-agent framework'üdür. Beş temel unsur: Agent, Handoff, Guardrail, Session, Tracing. Handoffs `transfer_to_<agent>` olarak adlandırılmış araçlardır. Guardrails girdi veya çıktıda tetiklenir. Varsayılan olarak açıktır.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 14 · 06 (Araç Kullanımı)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- OpenAI Agents SDK'nın beş temel unsurunu adlandırın.
- Handoffs'u açıklayın: neden araç olarak modellendiği, modelin gördüğü isim şekli ve bağlamın nasıl devredildiğini.
- Input guardrail'leri, output guardrail'leri ve tool guardrail'leri ayırın; `run_in_parallel` vs blokaj modunu açıklayın.
- Handoffs + guardrail'ler + span tarzı tracing ile stdlib bir runtime uygulayın.

## Problem

Temiz şekilde delege edemeyen agent'lar her şeyi tek bir prompt'a sığdırır. Guardrail'leri olmayan agent'lar PII, politika ihlali çıkan çıktılar üretir veya sonsuza kadar döngüye girer. OpenAI'ın SDK'sı çoklu-agent çalışmasını yönetilebilir kılan üç temel unsuru kodlar.

## Kavram

### Beş temel unsur

1. **Agent.** LLM + talimatlar + araçlar + handoffs.
2. **Handoff.** Başka bir agent'a devir. Modele `transfer_to_<agent_name>` adlı bir araç olarak temsil edilir.
3. **Guardrail.** Girdi (yalnızca ilk agent), çıktı (yalnızca son agent) veya araç çağrısı (function tool başına) doğrulaması.
4. **Session.** Turlar arası otomatik konuşma geçmişi.
5. **Tracing.** LLM nesilleri, araç çağrıları, handoffs, guardrail'ler için yerleşik span'lar.

### Handoffs araç olarak

Model araç listesinde `transfer_to_billing_agent`'ı görür. Çağrılması runtime'a şunu bildirir:

1. Konuşma bağlamını kopyalayın (veya `nest_handoff_history` beta'sı vasıtasıyla sıkıştırın).
2. Hedef agent'ı talimatlarıyla başlatın.
3. Hedef agent ile çalıştırmaya devam edin.

Bu, supervisor kalıbının (Ders 13 / Ders 28) ürünleştirilmiş halidir.

### Guardrails

Üç tür:

- **Input guardrail'leri.** İlk agent'ın girdisi üzerinde çalışır. Herhangi bir LLM çağrısından önce güvensiz veya kapsam dışı istekleri reddeder.
- **Output guardrail'leri.** Son agent'ın çıktısı üzerinde çalışır. PII sızıntılarını, politika ihlallerini, hatalı biçimlendirmeleri yakalar.
- **Tool guardrail'leri.** Function tool başına çalışır. Argümanları doğrular, izinleri kontrol eder, çalıştırmayı denetler.

Mod:

- **Parallel** (varsayılan). Guardrail LLM ana LLM ile birlikte çalışır. Daha düşük kuyruk gecikmesi. Tetiklenirse, ana LLM'in çalışması discarded edilir (token israfı).
- **Blocking** (`run_in_parallel=False`). Guardrail LLM önce çalışır. Tetiklenirse, ana çağrıda token israfı olmaz.

Tetikleyiciler `InputGuardrailTripwireTriggered` / `OutputGuardrailTripwireTriggered` fırlatır.

### Tracing

Varsayılan olarak açıktır. Her LLM nesili, araç çağrısı, handoff ve guardrail bir span emit eder. `OPENAI_AGENTS_DISABLE_TRACING=1` ile kapatılır. `add_trace_processor(processor)` span'ları kendi arka ucunuza OpenAI'ın yanı sıra fan-out eder.

### Sessions

`Session` konuşma geçmişini bir arka uçta (SQLite, Redis, özel) saklar. `Runner.run(agent, input, session=session)` otomatik yükler ve ekler.

### Bu kalıp nerede yanlış gider

- **Handoff kayması.** Agent A, Agent B'ye devreder, Agent B tekrar Agent A'ya devreder. Bir hop sayacı ekleyin.
- **Guardrail bypass.** Tool guardrail'leri yalnızca function tool'larda çalışır; yerleşik araçlar (dosya okuyucu, web getirme) ayrı politika gerektirir.
- **Aşırı tracing.** Span'larda hassas içerik. OTel GenAI içerik yakalama kurallarıyla eşleştirin (Ders 23).

## İnşa Et

`code/main.py` SDK şeklini stdlib'da uygular:

- `Agent`, `FunctionTool`, `Handoff` (transfer semantiğiyle function tool olarak).
- Input/output/tool guardrail'leri, handoff yönlendirmesi ve hop sayacıyla `Runner`.
- Trace şeklini gösteren basit bir span üreteci.
- Kullanıcının sorgusuna göre billing veya destek'e handoff yapan bir triage agent'ı; bir girdide guardrail tetiklenir.

Çalıştırın:

```bash
python3 code/main.py
```

Trace iki başarılı handoff'u, bir input guardrail tetiklemesini ve gerçek SDK'nın emit ettiğini yansıtan bir span ağacını gösterir.

## Kullan

- **OpenAI Agents SDK** OpenAI-öncelikli ürünler için.
- **Claude Agent SDK** (Ders 17) Claude-öncelikli ürünler için.
- **LangGraph** (Ders 13) açık state ve dayanıklı devam gerektiğinde.
- **Özel** tam kontrol gerektiğinde (ses, çoklu-sağlayıcı, birleşik deployment'lar).

## Teslim Et

`outputs/skill-agents-sdk-scaffold.md` bir triage agent, handoffs, input/output/tool guardrail'ler, oturum deposu ve bir trace işleyicisiyle bir Agents SDK uygulaması iskeletler.

## Alıştırmalar

1. Handoff hop sayacı ekleyin: N devirden sonra reddedin. Davranışı izleyin.
2. `nest_handoff_history`'yi bir seçenek olarak uygulayın: devretmeden önce önceki mesajları tek bir özetle sıkıştırın.
3. Blokaj bir output guardrail yazın. Tetiklenecek promptlar ile geçecekler arasındaki gecikmeyi karşılaştırın.
4. `add_trace_processor`'ı bir JSON loglayıcıya bağlayın. Her span için ne şekil emit eder?
5. SDK dokümanlarını okuyun. Stdlib toy'u `openai-agents-python`'a taşıyın. Neyi yanlış modelladiniz?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Agent | "LLM + talimatlar" | SDK'daki agent türü; araçları ve handoffs'u sahiplenir |
| Handoff | "Transfer" | Modelin başka bir agent'a devretmek için çağırdığı araç |
| Guardrail | "Politika kontrolü" | Girdi / çıktı / araç çağrısı doğrulaması |
| Tripwire | "Guardrail tetiklenmesi" | Guardrail reddettiğinde fırlatılan istisna |
| Session | "Geçmiş deposu" | Çalışmalar arası kalıcı konuşma hafızası |
| Tracing | "Span'lar" | LLM + araç + handoff + guardrail üzerine yerleşik gözlem |
| Blocking guardrail | "Sıralı kontrol" | Guardrail önce çalışır; tetiklemede token israfı yok |
| Parallel guardrail | "Eş zamanlı kontrol" | Guardrail birlikte çalışır; daha düşük gecikme, tetiklemede token israfı |

## İleri Okuma

- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) — temel unsurlar, handoffs, guardrail'ler, tracing
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview) — Claude tarzı karşılık
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — ne zaman handoffs'a ihtiyaç var
- [OpenTelemetry GenAI semantik inançları](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — Agents SDK span'larının eşleştiği standart
