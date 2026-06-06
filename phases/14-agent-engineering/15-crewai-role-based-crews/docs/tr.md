# CrewAI: Role-Based Crews ve Flows

> CrewAI 2026'da role-based çoklu-agent framework'üdür. Dört temel unsur: Agent, Task, Crew, Process. İki üst düzey şekil: Crews (otonom, role-based işbirliği) ve Flows (ola驱动lı, deterministik). Dokümanlar açıktır: "herhangi bir production-ready uygulama için bir Flow ile başlayın."

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 12 (Workflow Kalıpları), Faz 14 · 14 (Actor Model)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- CrewAI'nin dört temel unsurunu (Agent, Task, Crew, Process) ve her birinin sahipliğini adlandırın.
- Sequential, Hierarchical ve planlanan Consensus süreçlerini ayırın; iş yükü başına birini seçin.
- Crews (otonom role-based) ile Flows (ola驱动lı deterministik) arasındaki ayrımı ve dokümanın production önerisini açıklayın.
- `@tool` dekoratörü ve `BaseTool` alt sınıfıyla araçları bağlayın; yapılandırılmış çıktılar vs serbest metin üzerinde akıl yürütmeli.
- CrewAI'nin dört hafıza türünü ve her birinin ne zaman işe yaradığını adlandırın.
- Araştırmacı, yazar, editörden oluşan stdlib üç agent'lı bir crew uygulayın.
- Üç CrewAI başarısızlık modunu tanıyın: prompt-bloat, manager-LLM vergisi, kırılgan geçişler.

## Problem

Çoklu-agent framework'lerini benimseyen ekipler aynı duvara çarpar. "Otonom işbirliği" demoda harika görünür. Sonra bir müşteri hata bildirir ve siz deterministik tekrar üretme (replay) istersiniz. Veya finans bir LLM-yönlü crew'ın çalıştırmada ne kadara malolduğunu sorar. Veya nöbet 3'te hangi agent'ın takıldığını bilmeniz gerekir.

Serbest formsuz LLM-yönlü crew'lar bunların hiçbirine temiz cevap vermez. Saf DAG'lar hepsine cevap verir ancak beyin fırtınası yapan bir agent'ın gereksinimdiği keşif şeklini kaybeder.

CrewAI'nin ayrımı tavizler konusunda dürüsttür. Crews için işbirlikçi, role-based, keşifçi çalışmalar. Flows için ola驱动lı, kod-sahipli, denetlenebilir production. Aynı framework, iki şekil, yüzeye göre seçim.

## Kavram

### Dört temel unsur

CrewAI'nin yüzeyi küçüktür. Bunu ezberleyin gerisi konfigürasyondur.

- **Agent.** `role + goal + backstory + tools + (isteğe bağlı) llm`. Arka plan hikayesi (backstory) kritiktir. Tonu, yargılamayı, agent'ın ne zaman duracağını şekillendirir.
- **Task.** `description + expected_output + agent + (isteğe bağlı) context + (isteğe bağlı) output_pydantic`. Yeniden kullanılabilir bir iş birimi. `expected_output` sözleşmedir.
- **Crew.** Kap. `agents`, `tasks`, `process` ve isteğe bağlı `memory` + `verbose` + `manager_llm` ayarlarını sahiplenir.
- **Process.** Çalıştırma stratejisi. Sequential, Hierarchical, Consensus (planlanmış). Çalıştırmanın şeklini seçer.

Agent'lar birbirini doğrudan görmez. Task'lar agent'ları referans alır. Crew task'ları sıralar. Process bir sonraki task'ı kimin seçeceğine karar verir. Tüm zihinsel model budur.

> **CrewAI 0.86 (2026-05) ile doğrulanmıştır.** Daha yeni sürümler process türlerini yeniden adlandırabilir veya birleştirebilir; belirli bir şekle güvenmeden önce [CrewAI Processes docs](https://docs.crewai.com/concepts/processes) kontrol edin.

### Sequential vs Hierarchical vs Consensus

- **Sequential.** Task'lar beyan sırasıyla çalışır. Task N'in çıktısı task N+1'e `context` olarak kullanılabilir. En düşük maliyet. En öngörülebilir. Sıra sabitse kullanın.
- **Hierarchical.** Bir yönetici Agent (ayrı LLM çağrısı) uzmanlar arasında yönlendirir. CrewAI yöneticinizi `manager_llm` konfigürasyonunuzdan veya varsayılan olarak oluşturur. Yönetici her turda bir sonraki task'ı seçer ve reddedebilir veya yeniden yönlendirebilir. Dört veya daha fazla uzmanınız varsa ve sıra gerçekten önceki çıktıya bağlıysa kullanın.
- **Consensus.** Planlanmış, ancak halka açık API'da henüz uygulanmamıştır. Gelecekte oylama tabanlı bir process için adı saklı tutulmuştur. Bugün güvenmeyin.

Hierarchical, her uzman çağrısının üzerine tur başına bir LLM çağrısı (yönetici) ekler. Beş adımlık bir çalıştırmada token maliyeti üçe katlanabilir. Yalnızca yönlendirmeye ihtiyacınız olduğunda ödeyin.

### Crews vs Flows

Bu, 2026'da dokümanınLeading framing'idir.

- **Crew.** LLM驱动lı otonomluk. Framework şeklini runtime'da seçer. Araştırma, beyin fırtınası, ilk taslaklar için iyi. Tekrar üretmesi zor. Test etmesi zor. Prototipleme için ucuz.
- **Flow.** Sizin sahip olduğunuz ola驱动lı graf. `@start` girişini işaretler. `@listen(topic)` başka bir adım o topic'i emit ettiğinde çalışan bir adımı işaretler. Her adım saf Python'dur (içinde bir Crew çağırabilir). Production için iyi. Gözlemlenebilir. Test edilebilir. Deterministik.

Dokümanın 2026 production önerisi: bir Flow ile başlayın. Otonomluğun maliyetini hak ettiği yerde Flow adımlarından `Crew.kickoff()` çağrısı olarak Crews ekleyin. Flow size denetim izini, Crew size keşfi verir. Birleştirin, seçim yapmayın.

### Araç entegrasyonu

Bir Agent'a araç vermenin üç yolu. Uyan en basit olanı seçin.

1. **`@tool` dekoratörü.** Saf fonksiyonlar araçlara dönüşür. İmza şemadır; docstring LLM'in gördüğü açıklamadır.
2. **`BaseTool` alt sınıfı.** Sınıf tabanlı araç, açık args şeması, async desteği, yeniden denemeler. Araçta durum (bir istemci, bir önbellek) olduğunda veya yapılandırılmış args gerektiğinde kullanın.
3. **Yerleşik araç takımları.** CrewAI birinci taraf adaptörler sunar: `SerperDevTool`, `FileReadTool`, `DirectoryReadTool`, `CodeInterpreterTool`, `RagTool`, `WebsiteSearchTool`. Tek import ile bağlanır.

Yapılandırılmış çıktılar Pydantic kullanır. Task üzerinde `output_pydantic=MyModel` geçirin. CrewAI LLM yanıtını modele göre doğrular ve zorlar veya yeniden dener. Bunu sıkı bir `expected_output` string'iyle eşleştirin.

### Hafıza kancaları

CrewAI dört hafıza türünü kutudan çıkar çıkmaz sunar. Birleşirler: bir Crew hepsini aynı anda etkinleştirebilir.

- **Kısa vadeli.** Tek çalışma içinde konuşma tamponu. Sonda silinir.
- **Uzun vadeli.** Çalışmalar arası kalıcı. Vektör DB'de (varsayılan Chroma) saklanır. Mevcut göreve benzerlikle alınır.
- **Varlık (Entity).** Varlık başına olgular. "Müşteri X enterprise planında." Varlıkla anahtarlanır, benzerlikle değil. Çalışmalar arası hayatta kalır.
- **Bağlamsal (Contextual).** Toplama zamanında arama. Agent'ın ihtiyacı olduğu anda ilgili hafızayı çeker, önceden yüklenmez.

Crew'da `memory=True` veya tür başına konfigürasyonla etkinleştirin. Yaptığınız bir embedding sağlayıcısıyla desteklenir (varsayılan OpenAI, yerel olarak değiştirilebilir).

### CrewAI ne zaman uyan

- Adlandırılmış roller ve işbirlikçi bir workflow ile üç ila altı agent. Taslak yazma, inceleme, planlama, beyin fırtınası.
- Bir sonraki adımda LLM'in yargılamasının değerin parçası olduğu yönlendirme (Hierarchical).
- Ekiplerin `role + goal + backstory` okumayı graf tanımı okumaktan daha çok tercih ettiği her yer.

### CrewAI ne zaman uymaz

- Sıkı sıralamalı deterministik DAG'lar. LangGraph (Ders 13) kullanın.
- Alt saniye gecikme bütçeleri. Hierarchical gidiş-dönüş ekler.
- Tek agent döngüleri. Framework'ü atlayın; bir agent döngüsü (Ders 1) artı bir araç kaydı daha kısadır.

### Bağımlılık şekli

LangChain'den bağımsız. Python 3.10 ila 3.13. `uv` kullanır.

### Bu kalıp nerede yanlış gider

- **Backstory'den prompt bloat.** Agent başına 2000 kelimelik backstory ve beş agent'lı bir crew, ilk araç çağrısından önce bağlam bütçesini yakar. Backstory'leri 200 kelimenin altında tutun.
- **Manager-LLM token vergisi.** Hierarchical process her uzman çağrısından önce bir yönetici LLM çağrısı ekler. Beş task'lı bir crew'da altı LLM çağrısı olur.
- **Kırılgan geçişler.** Task N'in `expected_output`'u "bir anahat". Task N+1 bunu `context` olarak okur ve üç bölümü ayrıştırmaya çalışır. LLM dört tane üretmiştir.
- **Crew-as-prod.** Flow sarmalı olmadan üretime gönderilen serbest formsuz Crew. Çıktı değişkenliği yüksek; tekrar üretmesi imkansız; nöbet kötü bir çalışmayı iyi biriyle karşılaştıramaz. Bir Flow ile sarmalayın.

## İnşa Et

`code/main.py` her iki şeklin stdlib versiyonlarını artı üç agent'lı bir crew uygular.

Şekil:

- CrewAI'nin yüzeyiyle eşleşen `Agent`, `Task` dataclass'ları.
- `SequentialCrew.kickoff(inputs)` task'ları beyan sırasıyla çalıştırır, çıktıları `context` olarak işler.
- `HierarchicalCrew.kickoff(topic)` her turda bir sonraki uzmanı seçerek yönetici Agent ekler, "done" ile durur.
- `@start` ve `@listen(topic)` dekoratörleriyle `Flow`, küçük bir olay döngüsü ve bir trace.
- CrewAI'nin `@tool` şeklini yansıtan `tool(name)` dekoratörü.
- `short_term`, `long_term`, `entity` depolarıyla `Memory`; numpy ile mock edilmiş benzerlik.
- Mock LLM yanıtları rol artı input prefix'ine göre kodlanmış string'lerdir. Ağ yok. Deterministik.

Somut demo: "agent engineering 2026" konusunda brief üreten araştırmacı, yazar, editör crew'ı. Aynı crew deterministik şekli göstermek için bir Flow üzerinden çalışır.

Çalıştırın:

```bash
python3 code/main.py
```

## Kullan

- **CrewAI Flow** production için. Flow tek bir `Crew.kickoff()` çağran adım olsa bile. Flow denetim sınırını verir.
- **CrewAI Crew (Sequential)** net sıralamalı işbirlikçi çalışmalar için.
- **CrewAI Crew (Hierarchical)** yönlendirme çıktıya bağlıysa ve dört veya daha fazla uzmanınız varsa.
- **LangGraph** (Ders 13) açık durum makineleri, dayanıklı devam, sıkı sıralama için.
- **AutoGen v0.4** (Ders 14) actor-model eşzamanlılığı ve hata izolasyonu için.
- **OpenAI Agents SDK** (Ders 16) geçişler ve guardrail'lerle OpenAI-öncelikli ürünler için.
- **Claude Agent SDK** (Ders 17) subagent'lar ve oturum deposuyla Claude-öncelikli ürünler için.

## Teslim Et

`outputs/skill-crew-or-flow.md` bir görev için Crew vs Flow seçer ve asgari uygulamayı iskeletler.

## Alıştırmalar

1. Sequential crew'u Flow'a dönüştürün. Değişkenliğin düştüğü dokunma noktalarını sayın. Okunabilirliğin düştüğü yerleri not edin.
2. Crew'a varlık hafızası ekleyin: müşteri hakkında olgular kickstart'lar arası kalıcı.
3. Yöneticinin editöre yönlendirmeyi reddettiği, yazarın çıktısında en az üç paragraf olana kadar Hierarchical bir process uygulayın.
4. (Mock edilmiş) web araması için bir `BaseTool` alt sınıfı bağlayın.
5. Editor task'ına `output_pydantic=Brief` ekleyin. Yazar task'ının bir kez hatalı JSON üretmesini sağlayın; CrewAI'nin yeniden deneme davranışını trace'de doğrulayın.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Agent | "Kişilik" | Rol + hedef + geçmiş hikaye + araçlar |
| Task | "İş birimi" | Açıklama + beklenen çıktı + sorumlu + isteğe bağlı yapılandırılmış çıktı |
| Crew | "Agent takımı" | Agent'lar + Task'lar + Process için kap |
| Process | "Çalıştırma stratejisi" | Sequential / Hierarchical / Consensus (planlanmış) |
| Flow | "Deterministik workflow" | Ola驱动lı, kod-sahipli, test edilebilir |
| Backstory | "Kişilik prompt'u" | Agent için ton ve yargılayıcı şekillendirici |
| `@tool` | "Function tool" | Bir fonksiyonu Agent'ın çağırabileceği bir araca dönüştüren dekoratör |
| `BaseTool` | "Class tool" | Args şeması, yeniden denemeler, async desteği olan sınıf tabanlı araç |
| Entity memory | "Varlık başına olgular" | Müşteri / hesap / sorunla sınırlı hafıza |
| Long-term memory | "Çalışmalar arası hafıza" | Kickstart'lar arası hayatta kalan vektör destekli hafıza |
| Contextual memory | "Tam zamanında arama" | Agent'ın ihtiyacı anda çekilen hafıza |
| Manager LLM | "Yönlendirici agent" | Hierarchical process'de bir sonraki task'ı seçen ekstra LLM |
| `expected_output` | "Görev sözleşmesi" | Agent'a (ve denetçione) ne şekil döneceğini söyleyen string |

## İleri Okuma

- [CrewAI docs introduction](https://docs.crewai.com/en/introduction): kavramlar ve önerilen production yolu
- [CrewAI Flows guide](https://docs.crewai.com/en/concepts/flows): ola驱动lı şekil, `@start`, `@listen`
- [CrewAI tools reference](https://docs.crewai.com/en/concepts/tools): `@tool`, `BaseTool`, yerleşik araç takımları
- [CrewAI memory](https://docs.crewai.com/en/concepts/memory): kısa vadeli, uzun vadeli, varlık, bağlamsal
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents): ne zaman çoklu-agent yardımcı olur ne zaman olmaz
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview): durum makinesi alternatifi
