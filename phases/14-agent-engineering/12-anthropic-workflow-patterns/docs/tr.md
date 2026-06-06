# Anthropic'in Workflow Kalıpları: Basiti Karmaşıklık Üstüne

> Schluntz ve Zhang (Anthropic, Aralık 2024) workflow'ları (önceden tanımlanmış yollar) agent'lardan (dinamik araç kullanımı) ayırır. Beş workflow kalıbı çoğu durumu kapsar. Doğrudan API çağrılarıyla başlayın. Adımlar öngörülemez olduğunda yalnızca agent ekleyin.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Anthropic'in beş workflow kalıbını adlandırın: prompt chaining (prompt zincirleme), routing (yönlendirme), parallelization (paralelleştirme), orchestrator-workers (orkestratör-işçiler), evaluator-optimizer.
- Agent-vs-workflow ayrımını ve her birinin mühendislik maliyetini açıklayın.
- Ne zaman bir workflow'un bir agent'dan tercih edileceğini (ve tersini) tanımlayın.
- Beş kalıbın hepsini betiklenmiş bir LLM'e karşı stdlib'da uygulayın.

## Problem

Ekipler tek bir function çağrısı isteyen sorunlar için çoklu-agent framework'lerine başvurur. Maliyet gerçektir: framework'ler promptları gizleyen, kontrol akışını saklayan ve zamansız karmaşıklığı davet eden katmanlar ekler. Schluntz ve Zhang'in Aralık 2024 yazısı en çok atıfta bulunulan endüstri geri bildirimdir: basit başlayın, karmaşıklığı yalnızca maliyetini hak ettiğinde ekleyin.

## Kavram

### Workflow'lar vs agent'lar

- **Workflow.** LLM'ler ve araçlar önceden tanımlanmış kod yollarıyla orkestra edilir. Mühendisler grafiği sahiplenir.
- **Agent.** LLM'ler dinamik olarak kendi araçlarını yönetir ve kendi adımlarını atar. Model grafiği sahiplenir.

Her ikisinin de yeri vardır. Workflow'lar daha ucuz, daha hızlı ve daha kolay hata ayıklanır. Agent'lar açık uçlu sorunları açar ancak hata modlarını daha zor akıl yürütmeye yapar.

### Artırılmış LLM

Beş kalıbın temeli: arama (retrieval), araçlar (eylemler), hafıza (kalıcılık) olarak bağlanmış üç yeteneğe sahip bir LLM. Her API çağrısı bunları kullanabilir.

### Beş kalıp

1. **Prompt chaining.** 1. çağrının çıktısı 2. çağrının girdisidir. Bir görevin temiz bir doğrusal çözümlemesi olduğunda kullanın. Adımlar arasında isteğe bağlı programlı kapılar.

2. **Routing.** Bir sınıflandırıcı LLM hangi downstream LLM veya aracın çağrılacağını seçer. Kategorik olarak farklı girdilerin farklı işleme gerektiğinde kullanın (1. seviye destek vs geri ödeme vs hata vs satış).

3. **Parallelization.** N LLM çağrısını eş zamanlı çalıştırın, sonuçları toplayın. İki şekil: bölümleme (farklı parçalar) ve oylama (aynı prompt, N çalışma, çoğunluk/sentez).

4. **Orchestrator-workers.** Bir orkestratör LLM dinamik olarak hangi işçileri (LLM'ler) çalıştıracağına karar verir ve çıktılarını sentezler. Agent döngülerine benzer ancak orkestratör sınırsız döngü yapmaz.

5. **Evaluator-optimizer.** Bir LLM bir cevap önerir, başka bir LLM değerlendirir. Değerlendirici geçene kadar yineleyin. Bu genelleştirilmiş Self-Refine'dır (Ders 05).

### Workflow'ların agent'ları yendiği yerler

- **Öngörülebilir görevler.** Adımları listeleyebiliyorsanız, listeleyin.
- **Bütçe kısıtlı görevler.** Workflow'ların sınırlı adım sayıları vardır; agent'lar içinden çıkamayabilir.
- **Uyum kısıtlı görevler.** Denetçiler grafı okumak ister, trajectory'lerden çıkarmaz.

### Agent'ların workflow'ları yendiği yerler

- **Açık uçlu araştırma.** Bir sonraki adım bir öncekinin ne döndüğüne bağlı olduğunda.
- **Değişken uzunluklu görevler.** Dakikalardan saatlere kadar, adım sayısının bilinmediği çalışmalar.
- **Yeni alanlar.** Henüz doğru workflow'u bilmediğinizde — önce keşfedin, sonra kodlandırın.

### Bağlam mühendisliği yoldaşı

"Effective context engineering for AI agents" (Anthropic 2025) komşu disiplini resmileştirir: 200k pencere bir bütçedir, bir kap değildir. Ne dahil edilir, ne zaman sıkıştırılır, ne zaman bağlam büyütülür. Faz 14'ün bağlam sıkıştırma dersinde (bu müfredatta yeniden numaralandırmadan önceki ders 06) ayrıntılı olarak ele alınır.

## İnşa Et

`code/main.py` beş workflow kalıbının hepsini bir `ScriptedLLM`'e karşı uygular:

- `prompt_chain(input, steps)` — sıralı.
- `route(input, classifier, handlers)` — sınıflandırma + yönlendirme.
- `parallel_vote(prompt, n, aggregator)` — N çalışma, toplama.
- `orchestrator_workers(task, workers)` — orkestratör işçileri seçer.
- `evaluator_optimizer(task, proposer, evaluator, max_iter)` — geçene kadar döngü.

Çalıştırın:

```bash
python3 code/main.py
```

Her kalıp trace'ini yazdırır. Kalıp başına toplam kod satırı ~10-15; bir framework'ün maliyeti binlerle ölçülür.

## Kullan

- Çoğu görev için doğrudan API çağrıları.
- Kalıp gerçekten dayanıklı state (LangGraph), actor-model eşzamanlılığı (AutoGen v0.4) veya rol şablonlama (CrewAI) gerektirdiğinde yalnızca framework.
- Claude Code harness şeklini yeniden inşa etmeden istediğinizde Claude Agent SDK'ya başvurun.

## Teslim Et

`outputs/skill-workflow-picker.md`, verilen bir görev açıklaması için doğru kalıbı seçer, karar gerekçesini ve workflow'lar yetersiz kaldığında bir agent'a geçiş yolunu içerir.

## Alıştırmalar

1. Güven eşiğiyle yönlendirme uygulayın. Eşik altında -> insana yükseltin. 1. seviye destek kullanım durumunda eşik nerede?
2. `parallel_vote`'a zaman aşımı ekleyin. Bir çağrı asılı kaldığında ne olur? Eksik oylarla nasıl toplarsınız?
3. `evaluator_optimizer`'ı bir bandit'e dönüştürün: geç iterations boyunca en iyi 2 çıktıyı koruyun ki geç bir iyi sonuç geç bir kötü tarafından üzerine yazılmasın.
4. Prompt chaining'i yönlendirmeyle birleştirin: bir yönlendirici üç zincirden birini seçer. Token maliyetini tek büyük prompt alternatifiyle karşılaştırın.
5. Production özelliklerinizden birini seçin. Workflow grafiğini çizin. Adımları sayın. Bir agent burada gerçekten daha iyi olur muydu?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Workflow | "Önceden tanımlanmış akış" | Mühendis tarafından sahiplenilen LLM ve araç çağrısı grafiği |
| Agent | "Otonom AI" | Model tarafından sahiplenilen graf; dinamik araç yönetimi |
| Augmented LLM | "Araçlı LLM" | LLM + arama + araçlar + hafıza; atomik birim |
| Prompt chaining | "Sıralı çağrılar" | N. çağrının çıktısı N+1. çağrının girdisi |
| Routing | "Sınıflandırıcı yönlendirmesi" Hangi zincirin/modelin girdiyi işleyeceğini seçin |
| Parallelization | "Fan out" | N eş zamanlı çağrı; bölümleme veya oylamayla toplama |
| Orchestrator-workers | "Yönlendirici agent" | Orkestratör LLM uzman LLM'leri dinamik olarak seçer |
| Evaluator-optimizer | "Öneri + hakem" | Değerlendirici geçene kadar yinele; genelleştirilmiş Self-Refine |

## İleri Okuma

- [Anthropic, Building Effective Agents (Aralık 2024)](https://www.anthropic.com/research/building-effective-agents) — beş workflow kalıbı
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — komşu disiplin
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — durumlu graf'lar ne zaman maliyetlerini hak eder
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — orkestratör-işçiler kalıbı, ürünleştirilmiş
