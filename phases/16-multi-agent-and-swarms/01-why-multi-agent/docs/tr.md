# Neden Multi-Agent?

> Tek bir agent tavana çarpar. Akıllı hamle daha büyük bir agent değil — daha fazla agent'tır.

**Tür:** Öğren
**Diller:** TypeScript
**Ön Koşullar:** Faz 14 (Agent Mühendisliği)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Tek-agent tavanını (context overflow — bağlam taşması, mixed expertise — karışık uzmanlık, sequential bottleneck — sıralı darboğaz) tespit edin ve görevi birden fazla agent'a bölmenin ne zaman doğru hamle olduğunu açıklayın
- Orkestrasyon kalıplarını (pipeline, parallel fan-out — paralel yayılım, supervisor — denetçi, hierarchical — hiyerarşik) karşılaştırın ve belirli bir görev yapısı için doğru olanı seçin
- Net rol sınırları, paylaşılan durum (shared state) ve iletişim sözleşmesi olan bir multi-agent sistem tasarlayın
- Multi-agent karmaşıklığının (gecikme, maliyet, hata ayıklama zorluğu) getirdiği ödünleşimleri tek-agent sadeliğiyle karşılaştırarak analiz edin

## Problem

Faz 14'te tek bir agent inşa ettiniz. Çalışıyor. Dosya okuyabiliyor, komut çalıştırabiliyor, API çağırabiliyor ve sonuçlar üzerinde akıl yürütebiliyor. Sonra onu gerçek bir kod tabanına yönlendiriyorsunuz: 200 dosya, üç dil, altyapıya bağımlı testler ve kod yazmadan önce dış API'leri araştırma gerekliliği.

Agent boğulur. Bunun nedeni LLM'in aptal olması değil, görevin tek bir agent döngüsünün kaldırabileceğini aşmasıdır. Bağlam penceresi (context window) dosya içerikleriyle doluyor. Agent 40 araç çağrısı önce ne okuduğunu unutuyor. Aynı anda hem araştırmacı, hem kod yazarı, hem de incelemeci olmaya çalışıyor ve üçünü de kötü yapıyor.

Bu, tek-agent tavanıdır (single-agent ceiling). Bir görev aşağıdakileri gerektirdiğinde bu tavana her seferinde çarparsınız:

- **Tek bir pencereye sığmayan context** — 50 dosya okumak 200k token'ı aşıyor
- **Farklı aşamalarda farklı uzmanlık** — araştırma, kod üretiminden farklı bir promptlama gerektirir
- **Paralel yapılabilecek iş** — neden üç dosyayı sırayla okuyasınız ki, aynı anda okuyabilirsiniz

## Kavram

### Tek-Agent Tavanı

Tek bir agent, tek bir döngü, tek bir bağlam penceresi, tek bir sistem promptudur. Şöyle hayal edin:

```
┌─────────────────────────────────────────┐
│            TEK AGENT                    │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │         Bağlam Penceresi          │  │
│  │                                   │  │
│  │  araştırma notları                │  │
│  │  + kod dosyaları                  │  │
│  │  + test çıktısı                   │  │
│  │  + inceleme geri bildirimi        │  │
│  │  + API dokümanları                │  │
│  │  + ...                            │  │
│  │                                   │  │
│  │  ██████████████████████ DOLU ███  │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Tek sistem promptu araştırma +         │
│  kodlama + inceleme + test'i            │
│  kapsamaya çalışıyor                    │
│                                         │
│  Sonuç: her şeyde vasat                 │
└─────────────────────────────────────────┘
```

Üç şey kırılır:

1. **Bağlam doygunluğu (context saturation)** — araç sonuçları yığılır. 30. turda agent dosya içerikleri, komut çıktıları ve önceki akıl yürütmeleri için 150k token tüketmiştir. 5. turdaki kritik detaylar kaybolur.

2. **Rol karmaşası (role confusion)** — "sen bir araştırmacı, kod yazarı, incelemeci ve testçisin" diyen bir sistem promptu, yarı yarıya araştırma yapan, yarı yarıya kod yazan ve incelemeyi hiç bitirmeyen bir agent üretir.

3. **Sıralı darboğaz (sequential bottleneck)** — agent A dosyasını, sonra B dosyasını, sonra C dosyasını okur. Üç sıralı LLM çağrısı. Üç sıralı araç çalıştırması. Paralellik yok.

### Multi-Agent Çözümü

İşi bölün. Her agent'a bir görev, bir bağlam penceresi ve o görev için ayarlanmış bir sistem promptu verin:

```
┌──────────────────────────────────────────────────────────┐
│                    ORKESTRATÖR                            │
│                                                          │
│  "Kullanıcı yönetimi için REST API inşa et"              │
│                                                          │
│         ┌──────────┬──────────┬──────────┐               │
│         │          │          │          │               │
│         ▼          ▼          ▼          ▼               │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│   │ARAŞTIRMACI│ │ KOD YAZARI│ │İNCELEME  │ │ TESTÇİ   │  │
│   │          │ │          │ │          │ │          │  │
│   │ Belgeleri │ │ Araştır- │ │ Kalite   │ │ Testleri │  │
│   │ okur,    │ │ ma +     │ │ kontrol  │ │ çalıştı- │  │
│   │ kalıpları│ │ spec'e   │ │ eder,    │ │ rır,     │  │
│   │ bulur    │ │ dayalı   │ │ hataları │ │ sonuçları│  │
│   │          │ │ kod yaz- │ │ bulur    │ │ raporlar │  │
│   │          │ │ ar       │ │          │ │          │  │
│   └─────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│         │           │            │             │         │
│         └───────────┴────────────┴─────────────┘         │
│                          │                               │
│                     Sonuçları birleştir                  │
└──────────────────────────────────────────────────────────┘
```

Her agent'ın şunları vardır:
- Odaklanmış bir sistem promptu ("Sen bir kod incelemecisin. Tek işin hata bulmaktır.")
- Kendi bağlam penceresi (diğer agent'ların işiyle kirlenmemiş)
- Net bir girdi/çıktı sözleşmesi (araştırma notlarını alır, kod çıktısı verir)

### Bunu Yapan Gerçek Sistemler

**Claude Code subagent'ları** — Claude Code `Task` ile bir subagent başlattığında, kapsamı belirlenmiş bir görevle bir çocuk agent (child agent) oluşturur. Ana (parent) bağlamını temiz tutar. Çocuk odaklanmış iş yapar ve bir özet döner.

**Devin** — bir planner agent, bir coder agent ve bir browser agent çalıştırır. Planner işi adımlara böler. Coder kod yazar. Browser dokümanları araştırır. Her birinin ayrı bağlamı vardır.

**Multi-agent kodlama takımları (SWE-bench)** — SWE-bench'te en yüksek performans gösteren sistemler, kod tabanını okuyan bir araştırmacı, düzeltmeyi tasarlayan bir planlayıcı ve uygulayan bir kod yazarı kullanır. Tek-agent sistemler daha düşük puan alır.

**ChatGPT Deep Research** — her biri farklı bir açıyı keşfeden birden fazla arama agent'ını paralel olarak başlatır, sonra sonuçları sentezler.

### Spektrum

Multi-agent ikili bir durum değildir. Bir spektrumdur:

```
BASİT ──────────────────────────────────────────── KARMAŞIK

 Tek            Sub-         Pipeline      Takım         Swarm
 Agent          agent

 ┌───┐       ┌───┐        ┌───┐───┐    ┌───┐───┐    ┌─┐┌─┐┌─┐
 │ A │       │ A │        │ A │ B │    │ A │ B │    │ ││ ││ │
 └───┘       └─┬─┘        └───┘─┬─┘    └─┬─┬─┘    └┬┘└┬┘└┬┘
                │                │        │ │       ┌┴──┴──┴┐
              ┌─┴─┐          ┌───┘───┐    │ │       │paylaşı-│
              │ a │          │ C │ D │  ┌─┴─┴─┐    │ lan     │
              └───┘          └───┘───┘  │ mesaj│    │ durum   │
                                        │ veri │    └────────┘
                                        │ yolu │
  1 döngü     Ebeveyn +    Aşamalı      │       │   N eş,
  1 bağlam    çocuk         aşamalı     └───────┘   ortaya
  penceresi   görevler                                çıkan
                                                       davranış
                                        Açık
                                        roller
```

**Tek agent** — bir döngü, bir prompt. Basit görevler için iyidir.

**Subagent'lar** — bir ebeveyn, odaklanmış alt görevler için çocuklar başlatır. Ebeveyn planı korur. Çocuklar geri bildirir. Claude Code'un yaptığı budur.

**Pipeline** — agent'lar sırayla çalışır. A agent'ının çıktısı, B agent'ının girdisi olur. Aşamalı iş akışları için iyidir: araştır → kodla → incele → test et.

**Takım** — agent'lar paylaşılan bir mesaj veri yolu (message bus) üzerinden paralel çalışır. Her birinin bir rolü vardır. Bir orkestratör koordine eder. Farklı becerilerin aynı anda gerekli olduğu durumlarda iyidir.

**Swarm** — paylaşılan durumla çok sayıda özdeş veya özdeşe yakın agent. Sabit bir orkestratör yoktur. Agent'lar bir kuyruktan iş alır. Yüksek verimli paralel görevler için iyidir.

### Dört Multi-Agent Kalıbı

#### Kalıp 1: Pipeline

```
Girdi ──▶ Agent A ──▶ Agent B ──▶ Agent C ──▶ Çıktı
          (araştırma) (kod)      (inceleme)
```

Her agent veriyi dönüştürür ve ileriye aktarır. Akıl yürütmesi kolaydır. Bir aşamadaki hata geri kalanını engeller.

#### Kalıp 2: Yayılım / Toplama (Fan-out / Fan-in)

```
                ┌──▶ Agent A ──┐
                │              │
Girdi ──▶ Böl  ├──▶ Agent B ──├──▶ Birleştir ──▶ Çıktı
                │              │
                └──▶ Agent C ──┘
```

İşi paralel agent'lara bölün, sonra sonuçları birleştirin. Bağımsız alt görevlere ayrılabilen görevler için iyidir.

#### Kalıp 3: Orkestratör-İşçi (Orchestrator-Worker)

```
                    ┌──────────┐
                    │ Ork.     │
                    └──┬───┬───┘
                  görev│   │ görev
                  ┌────┘   └────┐
                  ▼            ▼
            ┌──────────┐  ┌──────────┐
            │ İşçi A   │  │ İşçi B   │
            └──────────┘  └──────────┘
```

Akıllı bir orkestratör ne yapılacağına karar verir, işçilere devreder ve sonuçları sentezler. Orkestratör kendisi de işçi başlatma araçlarına (tools) sahip bir agent'tır.

#### Kalıp 4: Eşler Arası Swarm (Peer Swarm)

```
         ┌───┐ ◄──── mesaj ───▶ ┌───┐
         │ A │                    │ B │
         └─┬─┘                    └─┬─┘
           │                        │
      mesaj│    ┌───────────┐       │ mesaj
           └───▶│  Paylaşılan│◀──────┘
                │  Durum     │
           ┌───▶│  / Kuyruk  │◀─────┐
           │    └───────────┘      │
      mesaj│                       │ mesaj
         ┌─┴─┐                    ┌─┴─┐
         │ C │ ◄──── mesaj ────▶ │ D │
         └───┘                    └───┘
```

Merkezi bir orkestratör yoktur. Agent'lar eşler arası iletişir. Kararlar etkileşimden doğar. Hata ayıklaması daha zordur, ama çok sayıda agent'a ölçeklenir.

### Multi-Agent Ne Zaman Kullanılmaz

Multi-agent karmaşıklık ekler. Agent'lar arasındaki her mesaj potansiyel bir hata noktasıdır. Hata ayıklama "tek bir konuşmayı okumak"tan "beş agent arasında mesaj izlemek"e geçer.

**Tek-agent kalın şu durumlarda:**
- Görev tek bir bağlam penceresine sığıyor (~100k token'ın altında çalışma verisi)
- Farklı aşamalar için farklı sistem promptlarına ihtiyacınız yok
- Sıralı yürütme yeterince hızlı
- Görev, bölmenin değerden çok ek yük getireceği kadar basit

**Karmaşıklık maliyeti:**
- Her agent sınırı, kayıplı bir sıkıştırma adımıdır: A agent'ının tüm bağlamı, B agent'ı için bir mesaja özetlenir
- Koordinasyon mantığı (kim neyi, ne zaman, hangi sırayla yapar) kendi başına bir hata kaynağıdır
- Gecikme artar: N agent, en az N sıralı LLM çağrısı demektir; agent'ların ileri geri konuşması gerekirse daha fazla
- Maliyet çoğalır: her agent bağımsız olarak token yakar

Pratik kural: bir görev 20'den az araç çağrısı gerektiriyorsa ve 100k token'a sığıyorsa, tek-agent olarak kalın.

## İnşa Et

### Adım 1: Aşırı Yüklü Tek Agent

Her şeyi yapmaya çalışan tek bir agent. Devasa bir sistem promptu ve araştırma, kod ve incelemeleri tutan tek bir bağlam penceresi:

```typescript
type AgentResult = {
  content: string;
  tokensUsed: number;
  toolCalls: number;
};

async function singleAgentApproach(task: string): Promise<AgentResult> {
  const systemPrompt = `Sen tam yığın (full-stack) bir geliştiricisin. Şunları yapmalısın:
1. Gereksinimleri araştır
2. Kodu yaz
3. Kodu hatalar için incele
4. Testleri yaz
Bunların TÜMÜNÜ tek bir konuşmada yap.`;

  const contextWindow: string[] = [];
  let totalTokens = 0;
  let totalToolCalls = 0;

  const research = await fakeLLMCall(systemPrompt, `Araştır: ${task}`);
  contextWindow.push(research.output);
  totalTokens += research.tokens;
  totalToolCalls += research.calls;

  const code = await fakeLLMCall(
    systemPrompt,
    `Bu araştırmaya dayanarak:\n${contextWindow.join("\n")}\n\nŞimdi şunu kodla: ${task}`
  );
  contextWindow.push(code.output);
  totalTokens += code.tokens;
  totalToolCalls += code.calls;

  const review = await fakeLLMCall(
    systemPrompt,
    `Önceki tüm bağlama dayanarak:\n${contextWindow.join("\n")}\n\nKodu incele.`
  );
  contextWindow.push(review.output);
  totalTokens += review.tokens;
  totalToolCalls += review.calls;

  return {
    content: contextWindow.join("\n---\n"),
    tokensUsed: totalTokens,
    toolCalls: totalToolCalls,
  };
}
```

#### Açıklama

Bu fonksiyon, tek bir agent'ın ardışık üç LLM çağrısıyla tüm araştırma-kodlama-inceleme döngüsünü yürütmeye çalıştığını gösterir. Her adımda `contextWindow` birikerek büyür; aynı `systemPrompt` her aşamada kullanılır. Bu, "context saturation" ve "role confusion" sorunlarının en somut halidir — agent her aşamanın birikmiş çıktısını bir sonraki adımda da görmek zorundadır.

Bu yaklaşımın sorunları:
- Bağlam penceresi her aşamada büyür. İnceleme adımına gelindiğinde hem araştırma notlarını HEM kodu HEM önceki akıl yürütmeyi içerir.
- Sistem promptu geneldir. Her aşama için ayarlanamaz.
- Hiçbir şey paralel çalışmaz.

### Adım 2: Uzman Agent'lar

Şimdi bölün. Her agent tek bir iş alır:

```typescript
type SpecialistAgent = {
  name: string;
  systemPrompt: string;
  run: (input: string) => Promise<AgentResult>;
};

function createSpecialist(name: string, systemPrompt: string): SpecialistAgent {
  return {
    name,
    systemPrompt,
    run: async (input: string) => {
      const result = await fakeLLMCall(systemPrompt, input);
      return {
        content: result.output,
        tokensUsed: result.tokens,
        toolCalls: result.calls,
      };
    },
  };
}

const researcher = createSpecialist(
  "researcher",
  "Sen teknik bir araştırmacısın. Dokümanları oku, kalıpları bul ve bulguları özetle. Yalnızca uygulama için gereken gerçekleri çıktıla."
);

const coder = createSpecialist(
  "coder",
  "Sen kıdemli bir TypeScript geliştiricisin. Gereksinimler ve araştırma notlarına dayanarak temiz, test edilmiş kod yaz. Başka bir şey yazma."
);

const reviewer = createSpecialist(
  "reviewer",
  "Sen bir kod incelemecisin. Hataları, güvenlik sorunlarını ve mantık hatalarını bul. Spesifik ol. Satır numaralarını belirt."
);
```

#### Açıklama

`createSpecialist` yardımcı fonksiyonu, `(name, systemPrompt)` ikilisini alıp `run(input)` ile çağrılabilen bir `SpecialistAgent` üretir. Üç ayrı agent — `researcher`, `coder`, `reviewer` — kendi odaklanmış promptlarıyla tanımlanır. Her birinin kendi temiz bağlam penceresi olur; sadece ihtiyacı olan girdiyi alır. Bu, "role confusion" sorununu çözer: artık her agent tek bir role sıkı bir şekilde kilitlenmiştir.

Her uzmanın odaklanmış bir promptu vardır. Her biri yalnızca ihtiyacı olan girdiyle temiz bir bağlam penceresi alır.

### Adım 3: Mesajlar Üzerinden Koordine Et

Uzmanları açık mesaj geçişi (message passing) ile bağlayın:

```typescript
type AgentMessage = {
  from: string;
  to: string;
  content: string;
  timestamp: number;
};

async function multiAgentApproach(task: string): Promise<AgentResult> {
  const messages: AgentMessage[] = [];
  let totalTokens = 0;
  let totalToolCalls = 0;

  const researchResult = await researcher.run(task);
  messages.push({
    from: "researcher",
    to: "coder",
    content: researchResult.content,
    timestamp: Date.now(),
  });
  totalTokens += researchResult.tokensUsed;
  totalToolCalls += researchResult.toolCalls;

  const coderInput = messages
    .filter((m) => m.to === "coder")
    .map((m) => `[${m.from}'dan]: ${m.content}`)
    .join("\n");

  const codeResult = await coder.run(coderInput);
  messages.push({
    from: "coder",
    to: "reviewer",
    content: codeResult.content,
    timestamp: Date.now(),
  });
  totalTokens += codeResult.tokensUsed;
  totalToolCalls += codeResult.toolCalls;

  const reviewerInput = messages
    .filter((m) => m.to === "reviewer")
    .map((m) => `[${m.from}'dan]: ${m.content}`)
    .join("\n");

  const reviewResult = await reviewer.run(reviewerInput);
  messages.push({
    from: "reviewer",
    to: "orchestrator",
    content: reviewResult.content,
    timestamp: Date.now(),
  });
  totalTokens += reviewResult.tokensUsed;
  totalToolCalls += reviewResult.toolCalls;

  return {
    content: messages.map((m) => `[${m.from} -> ${m.to}]: ${m.content}`).join("\n\n"),
    tokensUsed: totalTokens,
    toolCalls: totalToolCalls,
  };
}
```

#### Açıklama

`AgentMessage`, agent'lar arası her iletişimi `{from, to, content, timestamp}` dörtlüsüyle temsil eder. `multiAgentApproach` işlevi üç agent'ı sırayla çalıştırır; her birinin çıktısı bir sonraki agent'a yönelik bir `AgentMessage` olarak kaydedilir. `filter((m) => m.to === "coder")` gibi ifadelerle her agent yalnızca kendisine hitap eden mesajları görür. Bu, "context pollution"ı — yani bir agent'ın diğerlerinin işleriyle kirlenmesini — engeller.

Her agent yalnızca kendisine hitap eden mesajları alır. Bağlam kirliliği yok. Araştırmacının 50k token'lık doküman okuması, incelemeci'nin bağlamına asla girmez.

### Adım 4: Karşılaştır

```typescript
async function compare() {
  const task = "Express.js API için bir hız sınırlayıcı (rate limiter) middleware inşa et";

  console.log("=== Tek Agent ===");
  const single = await singleAgentApproach(task);
  console.log(`Token: ${single.tokensUsed}`);
  console.log(`Araç çağrıları: ${single.toolCalls}`);

  console.log("\n=== Multi-Agent ===");
  const multi = await multiAgentApproach(task);
  console.log(`Token: ${multi.tokensUsed}`);
  console.log(`Araç çağrıları: ${multi.toolCalls}`);
}
```

#### Açıklama

Bu demo fonksiyonu, aynı görevi (`"Express.js API için rate limiter middleware inşa et"`) her iki yaklaşımla çalıştırır ve toplam token tüketimi ile araç çağrısı sayısını karşılaştırır. Multi-agent sürümü daha fazla toplam token kullanır (üç agent, üç ayrı LLM çağrısı) ancak her agent'ın bağlamı temiz kalır. Her aşamanın kalitesi artar çünkü sistem promptu özelleştirilmiştir.

Multi-agent sürümü daha fazla toplam token kullanır (üç agent, üç ayrı LLM çağrısı) ancak her agent'ın bağlamı temiz kalır. Her aşamanın kalitesi artar çünkü sistem promptu özelleştirilmiştir.

## Kullan

Bu ders, multi-agent'a ne zaman geçileceğine karar vermek için yeniden kullanılabilir bir prompt üretir. Bkz. `outputs/prompt-multi-agent-decision.md`.

## Alıştırmalar

1. Dördüncü bir uzman ekleyin: kod yazarından kod, incelemeci'den geri bildirim alan ve sonra test yazan bir "tester" agent'ı
2. Pipeline'ı, incelemeci'nin bir düzeltme döngüsü için geri bildirimi kod yazarına geri gönderebileceği şekilde değiştirin (maks 2 tur)
3. Sıralı pipeline'ı bir fan-out'a dönüştürün: araştırmacıyı ve bir "gereksinim analisti" agent'ını paralel çalıştırın, sonra kod yazarına geçmeden önce çıktılarını birleştirin

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Swarm | "AI agent'lardan oluşan bir kovan zihin" | Paylaşılan durumu olan ve sabit bir lideri bulunmayan eş agent'lar kümesi. Davranış yerel etkileşimlerden doğar. |
| Orchestrator | "Patron agent" | Araçları arasında başka agent'ları başlatma ve yönetme bulunan bir agent. Plan yapar ve devreder, ancak asıl işi yapmayabilir. |
| Coordinator | "Trafik polisi" | Agent olmayan bir bileşen (genellikle sadece kod, LLM değil) ki kurallara dayalı olarak agent'lar arasında mesaj yönlendirir. |
| Consensus | "Agent'lar anlaşıyor" | Birden fazla agent'ın devam etmeden önce anlaşmaya varmasını gerektiren bir protokol. Çatışan çıktıların çözülmesi gerektiğinde kullanılır. |
| Emergent behavior (ortaya çıkan davranış) | "Agent'lar kendi başlarına çözdü" | Agent etkileşimlerinden doğan ancak açıkça programlanmamış sistem düzeyindeki kalıplar. Yararlı veya zararlı olabilir. |
| Fan-out / fan-in | "Agent'lar için map-reduce" | Bir görevi paralel agent'lara bölme (fan-out — yayılım), sonra sonuçlarını birleştirme (fan-in — toplama). |
| Message passing (mesaj geçişi) | "Agent'lar birbirleriyle konuşur" | Agent'lar arasındaki iletişim mekanizması: paylaşılan bağlam pencerelerinin yerini alan, bir agent'tan diğerine gönderilen yapılandırılmış veri. |

## İleri Okuma

- [The Landscape of Emerging AI Agent Architectures](https://arxiv.org/abs/2409.02977) — multi-agent kalıplarının taraması
- [AutoGen: Enabling Next-Gen LLM Applications](https://arxiv.org/abs/2308.08155) — Microsoft'un multi-agent konuşma çatısı
- [Claude Code subagents belgeleri](https://docs.anthropic.com/en/docs/claude-code) — Claude Code'un `Task` ile nasıl delege ettiği
- [CrewAI belgeleri](https://docs.crewai.com/) — role tabanlı multi-agent çatısı
