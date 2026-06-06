# LangGraph — Agent'lar için Durum Makineleri

> Elle yazılmış bir ReAct döngüsü bir `while True`'dur. LangGraph ile yazılmış bir ReAct döngüsü, checkpoint alabileceğiniz, duraklatabileceğiniz, dallanabileceğiniz ve zaman yolculuğu yapabileceğiniz bir graf'tır. Agent değişmedi. Etrafındaki harness değişti.

**Tür:** Build
**Diller:** Python
**Önkoşullar:** Phase 11 · 09 (Function Calling), Phase 11 · 14 (Model Context Protocol)
**Süre:** ~75 dakika

## Sorun

Bir function-calling agent'ı (fonksiyon çağrısı yapan agent) yayımlıyorsunuz. Üç tur boyunca çalışıyor, sonra bir şeyler ters gidiyor: model 500 hatası döndüren bir aracı deniyor, kullanıcı görev ortasında fikrini değiştiriyor veya agent insan onayı olmadan bir siparişi iade etmeye karar veriyor. `while True:` döngüsünün hook'u yok. Duraklatamıyorsunuz, geri alamıyorsunuz ve "model diğer aracı seçseydi ne olurdu" dalına separatesiniz. Bunu bir demodan öteye taşıdığınızda, agent ya çalışan ya da çalışmayan bir kara kutuya dönüşüyor.

Sonraki adım görünür olduğunda açıktır. Agent zaten bir durum makinesidir — system prompt artı mesaj geçmişi artı bekleyen araç çağrısı artı sonraki eylem. Durum makinesini açık hale getirin: "model düşünür", "bir araç çalışır", "bir insan onaylar" için düğümler ve aralarındaki koşullu geçişler için kenarlar. Graf açık hale geldiğinde, harness ücretsiz olarak dört şey kazanır: checkpointing (adımlar arası durum kaydetme), interrupts (insan için duraklama), streaming (token ve ara olayları yayınlama) ve time-travel (önceki bir duruma geri dönme ve farklı bir dal deneme).

LangGraph bu soyutlamayı sunan kütüphanedir. LangChain anlamında bir agent framework'ü değil ("bu bir AgentExecutor, iyi şanslar"). Birinci sınıf duruma, birinci sınıf kalıcılığa ve birinci sınıf interrupt'lara sahip bir graf runtime'ıdır. Agent döngüsü çizeceğiniz bir şeydir, elle yazdığınız değil.

## Kavram

![LangGraph StateGraph: düğümler, kenarlar ve checkpoint](../assets/langgraph-stategraph.svg)

Bir `StateGraph`'in üç şeyi vardır.

1. **State** (Durum). Graf boyunca akan tipli bir dict (TypedDict veya Pydantic modeli). Her düğüm tam durumu alır ve kısmi bir güncelleme döndürür; LangGraph bunu alan başına bir *reducer* (yeniden oluşturucu) ile birleştirir — biriktirilmesi gereken listeler için `operator.add`, varsayılan olarak üzerine yazma.
2. **Nodes** (Düğümler). `state -> partial_state` Python fonksiyonları. Her biri ayrı bir adımdır: "modeli çağır", "araçları çalıştır", "özetle".
3. **Edges** (Kenarlar). Düğümler arası geçişler. Statik kenarlar tek bir yere gider. Koşullu kenarlar bir router fonksiyonu `state -> next_node_name` alır, böylece graf model çıktısına göre dallanabilir.

Grafı derlersiniz. Derleme topolojiyi bağlar, bir checkpoint ekler (opsiyonel ama üretim için zorunludur) ve çalıştırılabilir bir nesne döndürür. Başlangıç durumu ve bir `thread_id` ile çağırırsınız. Çalıştırmanın her adımı `(thread_id, checkpoint_id)` ile anahtarlanan bir checkpoint depolar.

### Dört süper güç

**Checkpointing.** Her düğüm geçişi yeni durumu bir depoya yazar (testler için bellek içi, üretim için Postgres/Redis/SQLite). Aynı `thread_id` ile grafı tekrar çağırarak devam edin. Graf durduğu yerden devam eder.

**Interrupts.** Bir düğümü `interrupt_before=["human_review"]` ile işaretleyin ve çalışma o düğüm çalışmadan önce durur. Durum depolanır. API'niz kullanıcıya "onay bekliyor" yanıtını verir. Sonraki istek aynı `thread_id` ile `Command(resume=...)` ile çalışmayı sürdürür.

**Streaming.** `graph.stream(state, mode="updates")` gerçekleşirken durum farklarını üretir. `mode="messages"`, model düğümleri içindeki LLM token'larını yayınlar. `mode="values"` tam anlık görüntüler üretir. Arayüzünüzde neyi göstermek istediğinizi seçersiniz.

**Time-travel** (zaman yolculuğu). `graph.get_state_history(thread_id)` tam checkpoint günlüğünü döndürür. Herhangi bir önceki `checkpoint_id`'yi `graph.invoke`'a verin ve o noktadan dallanın. Hata ayıklama için harikadır ("model B aracını seçseydi ne olurdu?") ve üretim izlerini yeniden oynatan regresyon testleri için.

### Reducer'lar asıl mesele

Her durum alanının bir reducer'ı vardır. Çoğu varsayılan iyidir — yeni değer eskinin üzerine yazar. Ama mesaj listeleri `operator.add` gerektirir, böylece yeni mesajlar üzerine yazma yerine eklenir. Paralel kenarlar güncellemelerini reducer üzerinden birleştirir. İki düğüm de `messages`'ı güncelliyorsa ve `Annotated[list, add_messages]`'ı unuttuysanız, ikincisi sessizce kazanır ve turun yarısını kaybedersiniz. Reducer kütüphanedeki tek inceliğidir; bunu doğru yapın gerisi compose olur.

### Dört düğümlü ReAct grafı

Üretimdeki bir ReAct agent'ı dört düğüm ve iki kenardır:

1. `agent` — mevcut mesaj geçmişiyle LLM'i çağırır. Asistan mesajını döndürür (tool_calls içerebilir).
2. `tools` — son asistan mesajındaki herhangi bir tool_calls'ı çalıştırır, araç sonuçlarını araç mesajları olarak ekler.
3. `agent`'den koşullu bir kenar: son mesajda tool_calls varsa `tools`'a, yoksa `END`'e yönlendirir.
4. `tools`'dan `agent`'e statik bir kenar.

Bu kadar. Tam ReAct döngüsünü (Thought → Action → Observation → Thought → …) checkpoint, interrupt ve streaming ile yaklaşık 40 satır kodda elde edersiniz.

### StateGraph vs Send (fanout)

`Send(node_name, state)` bir düğümün paralel alt graf'lar göndermesini sağlar. Örnek: agent üç retriever'ı aynı anda sorgulamaya karar verir. Her `Send` hedef düğümün paralel bir çalıştırmasını başlatır; çıkışları durum reducer üzerinden birleşir. LangGraph bunu iplik (threading) primitive'leri olmadan orkestratör-worker kalıbını ifade eder.

### Alt graf'lar

Derlenmiş bir graf başka bir graf içinde bir düğüm olabilir. Dış graf tek bir düğüm görür; iç graf kendi durumuna ve kendi checkpoint'lerine sahiptir. Ekipler supervisor-agent'ları (yönetici-agent) böyle inşa eder: yönetici grafı kullanıcı niyetini alan bazlı işçi alt graf'ına yönlendirir.

## Yap

### Adım 1: durum ve düğümler

```python
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

def agent_node(state: State) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: State) -> str:
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else END

tool_node = ToolNode(tools=[search_web, read_file])

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=MemorySaver())
```

`add_messages`, mesaj listesinin üzerine yazma yerine biriktirmesini sağlayan reducer'dır. Unutmak en yaygın LangGraph hatasıdır.

### Adım 2: bir thread ile çalıştırma

```python
config = {"configurable": {"thread_id": "user-42"}}
for event in app.stream(
    {"messages": [HumanMessage("find the Anthropic headquarters address")]},
    config,
    stream_mode="updates",
):
    print(event)
```

Her güncelleme bir `{node_name: state_delta}` dict'idir. Frontend'iniz bunları UI'a yayınlayabilir, böylece kullanıcılar "agent düşünüyor… search_web çağırılıyor… sonuç alındı… yanıt veriliyor" görür.

### Adım 3: insan döngüsü interrupt'u ekleyin

Bir düğümü işaretleyin, çalışma çalıştırılmadan önce duraklasın.

```python
app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["tools"],  # her araç çağrısından önce durakla
)

state = app.invoke({"messages": [HumanMessage("delete the production database")]}, config)
# state["__interrupt__"] ayarlı. Önerilen araç çağrılarını inceleyin.
# Onaylanırsa:
from langgraph.types import Command
app.invoke(Command(resume=True), config)
# Reddedilirse: bir red mesajı yazın ve sürdürün
app.update_state(config, {"messages": [AIMessage("Blocked by human reviewer.")]})
```

Durum, checkpoint ve thread interrupt boyunca depolanır. Çalıştırma sırasında dışında hiçbir şey bellekte değildir.

### Adım 4: hata ayıklama için zaman yolculuğu

```python
history = list(app.get_state_history(config))
for snapshot in history:
    print(snapshot.values["messages"][-1].content[:80], snapshot.config)

# Önceki checkpoint'ten dallanma
target = history[3].config  # üç adım geri
for event in app.stream(None, target, stream_mode="values"):
    pass  # o noktadan ileriye doğru yeniden oynatma
```

Girdi olarak `None` geçirmek verilen checkpoint'ten yeniden oynatır; bir değer geçirmek, sürdürmeden önce o checkpoint'in durumuna bir güncelleme olarak ekler. Bu, tüm konuşmayı yeniden çalıştırmadan kötü bir agent çalışmasını nasıl yeniden ürettiğinizdir.

### Adım 5: üretimi için checkpointer'ı değiştirin

```python
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    checkpointer.setup()
    app = graph.compile(checkpointer=checkpointer)
```

SQLite, Redis ve Postgres sunulmaktadır. `MemorySaver` testler içindir. Yeniden başlatmalar arası kalıcılık isteyen her şey gerçek bir depo ister.

## Beceri

> Agent'ları `while True` döngüleri yerine graf olarak inşa edersiniz.

LangGraph'e uzanmadan önce 60 saniyelik bir tasarım yapın:

1. **Düğümleri adlandırın.** Her ayrık karar veya yan etki eylemi bir düğümdür. "Agent düşünür", "araç çalışır", "inceleyen onaylar", "yanıt yayınlanır". Bunları listeleyemiyorsanız, görev hâlâ agent şekli almamıştır.
2. **Durumu beyan edin.** Her liste alanı için bir reducer ile minimal TypedDict. Her şeyi `messages`'a doldurmayın; görev-spesifik alanları (bir çalışma `plan`, bir `budget` sayacı, bir `retrieved_docs` listesi) üst düzeye çıkarın.
3. **Kenarları çizin.** Sonraki adım model çıktısına bağlı olmadıkça statik. Her koşullu kenarın adlı dallara sahip bir router fonksiyonu vardır.
4. **Checkpoint'i önceden seçin.** Testler için `MemorySaver`, diğer her şey için Postgres/Redis/SQLite. Biri olmadan yayımlamayın — checkpointer yok resume yok, interrupt yok, time-travel yok.
5. **Araçlar çalışmadan önce interrupt'lara karar verin, çalıştıktan sonra değil.** Onaylar yan etki eylemli bir düğüme giden kenara gider, böylece zarardan önce iptal edebilirsiniz; doğrulama modelden çıkan kenara gider, böylece kötü çağrıları ucuza reddedebilirsiniz.
6. **Varsayılan olarak yayınlayın.** UI için `mode="updates"`, model düğümleri içinde token seviyesinde streaming için `mode="messages"`, eval sırasında tam anlık görüntüler için `mode="values"`.

Checkpointer'sız bir LangGraph agent'ı yayımlamayı reddedin. Yan etkiden *sonra* interrupt yapan birini yayımlamayı reddedin. `messages` alanını `add_messages` reducer'ı olmadan yayımlamayı reddedin.

## Alıştırmalar

1. **Kolay.** Yukarıdaki dört düğümlü ReAct grafını bir hesap makinesi aracı ve bir web arama aracıyla uygulayın. `list(app.get_state_history(config))`'in iki turlu bir konuşma için en az dört checkpoint döndürdüğünü doğrulayın.
2. **Orta.** `agent`'den önce çalışan ve state'e yapılandırılmış bir `plan: list[str]` yazan bir `planner` düğümü ekleyin. `agent`'in plan adımlarını tamamlanmış olarak işaretlemesini sağlayın. Checkpoint resume'unda `plan`'ın kaybolduğunu (yanlış reducer) test edin ve testi başarısız kılın.
3. **Zor.** `Send` kullanarak üç alt graf (`researcher`, `writer`, `reviewer`) arasında yönlendiren bir yönetici grafı oluşturun. Her alt grafın kendi durumu ve checkpoint'i olsun. Dış graf'a bir `interrupt_before=["writer"]` ekleyin, böylece bir insan araştırma brief'ini onaylayabilsin. Önceki checkpoint'ten zaman yolculuğunun yalnızca dallanmış dalı yeniden çalıştırdığını doğrulayın.

## Anahtar Terimler

| Terim | İnsanların Söylediği | Aslında Ne Anlama Geldiği |
|------|-----------------|-----------------------|
| StateGraph | "LangGraph grafı" | Derlemeden önce düğüm ve kenar eklediğiniz oluşturucu nesne. |
| Reducer | "Alan nasıl birleşir" | Bir düğüm o alan için bir güncelleme döndürdüğünde uygulanan `(old, new) -> merged` fonksiyonu; varsayılan üzerine yazmadır, `add_messages` ekler. |
| Thread | "Bir konuşma ID'si" | Bir oturumun tüm checkpoint'lerini kapsayan bir `thread_id` dizesi. |
| Checkpoint | "Duraklatılmış durum" | Bir düğüm geçişinden sonra tam graf durumunun depolanan anlık görüntüsü, `(thread_id, checkpoint_id)` ile anahtarlanır. |
| Interrupt | "İnsan için duraklama" | `interrupt_before` / `interrupt_after` bir düğüm sınırlamasında çalışmayı durdurur; `Command(resume=...)` ile sürdürülür. |
| Time-travel | "Önceki adımdan dallanma" | `graph.invoke(None, config_with_old_checkpoint_id)` o checkpoint'ten ileriye doğru yeniden oynatır. |
| Send | "Paralel alt graf gönderimi" | Bir düğümün bir hedef düğümün N paralel çalıştırmasını başlatmak için döndürebileceği bir oluşturucu. |
| Alt graf | "Bir düğüm olarak derlenmiş graf" | Başka bir graf içinde düğüm olarak kullanılan derlenmiş StateGraph; kendi durum kapsamını korur. |

## Ek Okuma

- [LangGraph documentation](https://langchain-ai.github.io/langgraph/) — StateGraph, reducer'lar, checkpoint'ler ve interrupt'lar için kanuni referans.
- [LangGraph kavramları: state, reducers, checkpointers](https://langchain-ai.github.io/langgraph/concepts/low_level/) — bu dersin kullandığı zihinsel model, doğrudan kaynaktan.
- [LangGraph Kalıcılık ve Checkpoint'ler](https://langchain-ai.github.io/langgraph/concepts/persistence/) — Postgres/SQLite/Redis depoları, checkpoint namespace'leri ve thread ID'leri hakkında ayrıntı.
- [LangGraph İnsan Döngüsü](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/) — `interrupt_before`, `interrupt_after`, `Command(resume=...)` ve durum düzenleme kalıbı.
- [Yao vd., "ReAct: Synergizing Reasoning and Acting in Language Models" (ICLR 2023)](https://arxiv.org/abs/2210.03629) — her LangGraph agent'ının uyguladığı kalıp; muhakeme izi gerekçesi için okuyun.
- [Anthropic — Building effective agents (Aralık 2024)](https://www.anthropic.com/research/building-effective-agents) - hangi graf şekillerinin (zincir, router, orkestratör-worker, değerlendirici-optimize edici) tercih edileceği ve ne zaman.
- Phase 11 · 09 (Function Calling) — her LangGraph agent düğümünün yeniden kullandığı araç çağrısı ilkesi.
- Phase 11 · 14 (Model Context Protocol) — MCP adaptörü aracılığıyla LangGraph `ToolNode`'una takılan harici araç keşfi.
- Phase 11 · 17 (Agent framework tradeoffs) — LangGraph'i CrewAI, AutoGen veya Agno'ya tercih etme zamanı.
