# Multi-Agent İlkel Modeli (Primitive Model)

> 2026'da gönderilen her multi-agent çatısı — AutoGen, LangGraph, CrewAI, OpenAI Agents SDK, Microsoft Agent Framework — dört boyutlu bir tasarım uzayında bir noktadır. Dört ilkel (primitive), başka bir şey değil: agent, handoff, paylaşılan durum, orkestratör. Bu ders onları sıfırdan inşa eder, dördünde de oyuncak bir sistem çalıştırır, sonra her büyük çatıyı aynı eksenlere eşler, böylece her yeni sürümü bir paragrafta okuyabilirsiniz.

**Tür:** Öğren
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 (Agent Mühendisliği), Faz 16 · 01 (Neden Multi-Agent)
**Süre:** ~60 dakika

## Problem

Her altı ayda bir yeni bir multi-agent çatısı gönderilir. 2023'te AutoGen. 2024'te CrewAI. 2024'te LangGraph ve OpenAI Swarm. Nisan 2025'te Google ADK. Şubat 2026'da Microsoft Agent Framework RC. Her basın bülteni "doğru soyutlama" olduğunu iddia eder.

Bunları teker teker öğrenmeye çalışırsanız tükenirsiniz. API'ler farklı görünür. Dokümanlar bir "agent"ın ne olduğu konusunda anlaşamaz. Bir çatı paylaşılan belleğine "blackboard" (karatahta) der, diğeri "message pool" (mesaj havuzu) der, üçüncüsü "StateGraph" der. Alanın sadece çalkantı içinde olduğundan şüphelenmeye başlarsınız.

Değil. Pazarlamanın altında, dört ilkel stabildir. Bir kez öğrenin, her yeni çatıyı bir paragrafta okuyun.

## Kavram

### Dört ilkel

1. **Agent** — bir sistem promptu artı bir araç listesi. Durumsuzdur; her çalıştırma sistem promptundan ve geçerli mesaj geçmişinden başlar.
2. **Handoff** — bir agent'tan diğerine kontrollün yapılandırılmış aktarımı. Mekanik olarak, yeni bir agent döndüren bir araç çağrısı veya bir koşulu izleyen bir graf kenarı.
3. **Paylaşılan durum (shared state)** — birden fazla agent'ın okuyabildiği (bazen yazabildiği) herhangi bir veri yapısı. Mesaj havuzu, karatahta, anahtar-değer deposu, vektör belleği.
4. **Orkestratör** — bir sonraki konuşanın kim olduğuna karar veren. Seçenekler: açık bir graf (deterministik), bir LLM konuşmacı seçici (yumuşak), son konuşanın handoff çağrısı (OpenAI Swarm) veya bir kuyruk üzerinde zamanlayıcı (swarm mimarisi).

Tüm tasarım uzayı budur. Her çatı her eksen için varsayılanlar seçer; gerisi yüzey sözdizimidir.

### Her 2026 çatısı buna nasıl eşlenir

| Çatı | Agent | Handoff | Paylaşılan durum | Orkestratör |
|-----------|-------|---------|--------------|--------------|
| OpenAI Swarm / Agents SDK | `Agent(instructions, tools)` | Agent döndüren araç | çağıranın problemi | LLM'in bir sonraki handoff çağrısı |
| AutoGen v0.4 / AG2 | `ConversableAgent` | GroupChat üzerinde konuşmacı seçici | mesaj havuzu | seçici fonksiyon (LLM veya round-robin) |
| CrewAI | `Agent(role, goal, backstory)` | `Process. Sequential / Hierarchical` | zincirlenmiş görev çıktıları | yönetici LLM veya statik sıra |
| LangGraph | düğüm fonksiyonu | graf kenarı + koşul | `StateGraph` reducer | graf, deterministik |
| Microsoft Agent Framework | agent + orkestrasyon kalıpları | kalıba özgü | iş parçacığı / bağlam | kalıba özgü |
| Google ADK | agent + A2A card | A2A görevi | A2A yapıtları | ev sahibi karar verir |

Yüzey farklılıkları devasa görünür. Altında: aynı dört düğme.

### Bu neden önemli

İlkelleri bir kez gördüğünüzde, çatı karşılaştırması kısa bir kontrol listesine dönüşür:

- Orkestratör, yönlendirmeyi LLM'e güveniyor mu (Swarm) yoksa yönlendirmeyi kodda sabitliyor mu (LangGraph)?
- Paylaşılan durum tam geçmiş mi (GroupChat) yoksa projeksiyon mu (StateGraph reducer)?
- Agent'lar birbirlerinin promptlarını değiştirebilir mi (CrewAI yöneticisi) yoksa yalnızca handoff yapabilir mi (Swarm)?

Bu üç soru, belirli bir probleme hangi çatının uyduğunun %80'ini yanıtlar. "En iyi multi-agent çatısı"nı aramayı bırakır ve gerçekten önemsediğiniz eksen için tasarlamaya başlarsınız.

### Durumsuz içgörü

Paylaşılan durum dışında her ilkel durumsuzdur. Agent, (prompt, tools) bir fonksiyonudur. Handoff bir fonksiyon çağrısıdır. Orkestratör bir zamanlayıcıdır. **Sistemdeki tek durum bilgisi olan şey paylaşılan durumdur.** İlginç hataların yaşadığı yer orasıdır: bellek zehirlenmesi (Ders 15), mesaj sıralaması, sürümleme, yazma çakışması.

Paylaşılan durumu gizleyen çatılar (Swarm) sorunu çağırana iter. Onu merkezileştiren çatılar (LangGraph checkpoint, AutoGen havuzu) onu incelenebilir kılar ama koordinasyon maliyetini paylaşılan durum uygulamasına kaydırır.

### Tek bir ilkelin anatomisi

#### Agent

```
Agent = (system_prompt, tools, model, optional_name)
```

Bellek yok. Durum yok. Aynı sistem promptu ve araçlara sahip iki agent birbirinin yerine kullanılabilir. Agent başına durum gibi görünen her şey aslında paylaşılan durumda veya handoff protokolündedir.

#### Handoff

```
Handoff = (from_agent, to_agent, reason, payload)
```

Üç uygulama baskındır:

- **Fonksiyon dönüşü** — araç sonraki agent'ı döner. Bu OpenAI Swarm kalıbıdır. Agent'lar yönlendirmeyi araç şemalarında taşır.
- **Graf kenarı** — LangGraph. Kenarlar bildirimseldir. LLM bir değer üretir; bir koşul sonraki düğümü seçer.
- **Konuşmacı seçimi** — AutoGen GroupChat. Bir seçici fonksiyon (bazen kendisi bir LLM çağrısı) havuzu okur ve bir sonraki konuşanı seçer.

#### Paylaşılan Durum

```
SharedState = { messages: [], artifacts: {}, context: {} }
```

En azından, bir mesaj listesi. Genellikle daha fazlası: yapılandırılmış yapıtlar (CrewAI görev çıktıları), tipli bağlam (LangGraph reducer'ları), dış bellek (MCP, vektör veritabanı).

İki topoloji: **tam havuz** (her agent her mesajı görür) ve **projeksiyon** (agent'lar role-kapsamlı bir görünüm görür). Tam havuzlar basittir ve kötü ölçeklenir. Projeksiyon havuzları ölçeklenir ama önceden şema tasarımı gerektirir.

#### Orkestratör

```
Orchestrator = ({state, last_speaker}) -> next_agent
```

Dört çeşit:

- **Statik** — graf derleme zamanında sabitlenir (LangGraph deterministik, CrewAI Sequential).
- **LLM seçili** — bir LLM havuzu okur ve bir sonraki konuşanı seçer (AutoGen, CrewAI Hierarchical).
- **Handoff güdümlü** — mevcut agent bir handoff aracı çağırarak karar verir (Swarm).
- **Kuyruk güdümlü** — işçiler paylaşılan bir kuyruktan çeker; açık bir sonraki-konuşan yoktur (swarm mimarileri, Matrix).

### Çatılar arasında ne değişir

İlkeller sabitlendiğinde, kalan tasarım kararları şunlardır:

- **Bellek stratejisi** — kısa ömürlü mü yoksa dayanıklı mı kontrol noktası (LangGraph checkpointer).
- **Güvenlik sınırı** — bir handoff'ı kim onaylayabilir (insan döngüde).
- **Maliyet muhasebesi** — agent başına token bütçeleri.
- **Gözlemlenebilirlik** — handoff'ları izleme, yeniden oynatma için durumu kalıcı kılma.

Hepsi ilkellerin üzerine uygulanabilir. Hiçbiri yeni ilkel değildir.

## İnşa Et

`code/main.py`, dört ilkeli yaklaşık 150 satır stdlib Python'da uygular. Gerçek LLM yok — her agent, odağın koordinasyon yapısında kalması için komut dosyası (scripted) bir politikadır.

Dosya dışa aktarır:

- `Agent` — ad, sistem promptu, araçlar, politika fonksiyonunun dataclass'ı.
- `Handoff` — yeni bir agent döndüren bir fonksiyon.
- `SharedState` — iş parçacığı güvenli mesaj havuzu.
- `Orchestrator` — üç varyant: `StaticOrchestrator`, `HandoffOrchestrator`, `LLMSelectorOrchestrator` (simüle edilmiş).

Demo, aynı üç agent'lık pipeline'ı (araştır → yaz → incele) üç orkestratör türü boyunca çalıştırır ve sonunda mesaj havuzunu yazdırır. Çıktıların yalnızca *bir sonrakini kimin seçtiği* konusunda farklılaştığını görebilirsiniz; agent'lar ve paylaşılan durum tüm çalıştırmalarda aynıdır.

Çalıştırın:

```
python3 code/main.py
```

Beklenen çıktı: orkestratör başına bir çalıştırma olmak üzere üç çalıştırma. Her biri son mesaj havuzunu yazdırır. Handoff güdümlü çalıştırma, araştırmacı erken bittiğine karar verirse daha az agent'a ulaşır — bu, LLM yönlendirmesinin minyatürdeki ödünleşimidir.

## Kullan

`outputs/skill-primitive-mapper.md`, herhangi bir multi-agent kod tabanını veya çatı belgesini okuyan ve dört-ilkel eşlemesini döndüren bir yetenektir. Belgeleri derinlemesine okumadan önce bir paragraftalık anlayış için onu yeni bir çatı sürümünde çalıştırın.

## Dağıt

Yeni bir çatıyı benimsemeden önce, ilkel eşlemesini onun için yazın. Yazamıyorsanız, belgeler eksiktir veya çatı beşinci bir ilkel icat ediyordur (nadir — görmediğiniz bir paylaşılan durum çeşidi olup olmadığını kontrol edin).

Eşlemeyi mimari belgenizde sabitleyin. Yeni bir takım üyesi katıldığında, ona API belgelerinden önce eşlemeyi gönderin. Çatı sürümleri değiştiğinde, değişim günlüğünü değil eşlemeyi diff'leyin.

## Alıştırmalar

1. `code/main.py`'yi farklı agent politikalarıyla üç kez çalıştırın. Orkestratör seçiminin hangi agent'ların çalıştığını nasıl değiştirdiğini gözlemleyin.
2. Dördüncü bir orkestratör türü uygulayın: agent'ların iş için paylaşılan durumu yokladığı kuyruk güdümlü bir tane. Ne tür bir deadlock oluşabilir ve bunu nasıl tespit edersiniz?
3. LangGraph hızlı başlangıcını (https://docs.langchain.com/oss/python/langgraph/workflows-agents) alın ve dört ilkel olarak yeniden yazın. LangGraph'ın soyutlamalarından hangileri 1:1 eşlenir, hangileri kolaylık sarmalayıcılarıdır?
4. OpenAI Swarm cookbook'unu (https://developers.openai.com/cookbook/examples/orchestrating_agents) okuyun. Swarm'ın dört ilkelden hangisini en ergonomik hale getirdiğini ve hangisini çağırana ittiğini belirleyin.
5. Bu tablodaki paylaşılan durumu tamamen gizleyen bir çatı bulun. Agent'ların geçmişi yeniden okumadan handoff'lar arasında koordine olması gerektiğinde neyin kırıldığını açıklayın.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Agent | "Araçları olan bir LLM" | Bir `(system_prompt, tools, model)` üçlüsü. Durumsuz. |
| Handoff | "Kontrol aktarımı" | Bir sonraki agent'ı ve isteğe bağlı yükü adlandıran yapılandırılmış bir çağrı. Üç uygulama: fonksiyon dönüşü, graf kenarı, konuşmacı seçimi. |
| Shared state (Paylaşılan durum) | "Bellek" / "bağlam" | Multi-agent sisteminin tek durum bilgisi olan kısmı. Mesaj havuzu veya karatahta. |
| Orchestrator (Orkestratör) | "Koordinatör" | Bir sonrakinin kim çalışacağına karar veren. Statik graf, LLM seçici, handoff güdümlü veya kuyruk güdümlü. |
| Primitive (İlkel) | "Soyutlama" | Her çatının parametrelediği dört eksenden biri. Çatı özelliği değil. |
| Message pool (Mesaj havuzu) | "Paylaşılan sohbet geçmişi" | Tam geçmişli paylaşılan durum. Akıl yürütmesi kolay, kötü ölçeklenir. |
| Projected state (Projeksiyon durumu) | "Kapsamlı görünüm" | Paylaşılan duruma role özgü görünüm. Ölçeklenir, şema tasarımı gerektirir. |
| Speaker selection (Konuşmacı seçimi) | "Sırada kim konuşuyor" | Bir fonksiyonun (genellikle bir LLM) gruptan bir sonraki agent'ı seçtiği orkestratör kalıbı. |

## İleri Okuma

- [OpenAI cookbook: Orchestrating Agents — Routines and Handoffs](https://developers.openai.com/cookbook/examples/orchestrating_agents) — handoff güdümlü orkestrasyonun en net ifadesi
- [AutoGen kararlı belgeleri](https://microsoft.github.io/autogen/stable/) — GroupChat + konuşmacı seçimi LLM seçili orkestrasyon için referanstır
- [LangGraph iş akışları ve agent'ları](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — graf kenarı orkestrasyonu ve reducer tabanlı paylaşılan durum
- [CrewAI tanıtımı](https://docs.crewai.com/en/introduction) — rol-hedef-arka hikaye agent'ları, Sıralı / Hiyerarşik süreçler
- [AG2 (topluluk AutoGen devamı)](https://github.com/ag2ai/ag2) — Microsoft v0.4'ü bakıma aldıktan sonra canlı AutoGen v0.2 hattı
