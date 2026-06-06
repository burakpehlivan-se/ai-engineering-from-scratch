# AutoGen v0.4: Actor Model ve Agent Framework

> AutoGen v0.4 (Microsoft Research, Ocak 2025) agent orkestrasyonunu actor modeli etrafında yeniden tasarladı. Asenkron mesaj değişimi, olay驱动lı agent'lar, hata izolasyonu, doğal eşzamanlılık. Framework artık bakım modunda (maintenance mode) ve Microsoft Agent Platformu (Ekim 2025'te halka açık önizleme) halefi olarak ortaya çıkıyor.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 14 · 12 (Workflow Kalıpları)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Actor modelini tanımlayın: agent'lar actor olarak, mesajlar tek IPC olarak, her actor için hata izolasyonu.
- AutoGen v0.4'ün üç API katmanını — Core, AgentChat, Extensions — ve her birinin amacını adlandırın.
- Mesaj teslimatını işlemden ayırmanın neden hata izolasyonu ve doğal eşzamanlılık sağladığını açıklayın.
- Python'da stdlib bir actor runtime uygulayın ve iki agent'lı bir kod inceleme akışını üzerine taşıyın.

## Problem

Çoğu agent framework'ü senkroniktir: bir agent üretir, bir agent tüketir, bir çağrma yığını içinde. Hatalar yığını çöker. Eşzamanlılık sonradan eklenir. Dağıtım yeniden yazma gerektirir.

AutoGen v0.4'ün cevabı: actor modeli. Her agent özel bir gelen kutusuna (inbox) sahip bir actor'dur. Mesajlar tek etkileşim yoludur. Runtime teslimatı işlemden ayırır. Hatalar bir actor'a izole olur. Eşzamanlılık doğalır. Dağıtım yalnızca farklı bir taşımadır.

## Kavram

### Actor'lar

Bir actor'un şunları vardır:

- Özel bir durum (dışarıdan asla doğrudan dokunulmaz).
- Bir gelen kutusu (mesaj kuyruğu).
- Bir işleyici (handler): `receive(message) -> effects` — efektler "yanıtla", "diğer actor'a gönder", "yeni actor oluştur", "state'i güncelle", "kendini durdur" olabilir.

İki actor bellek paylaşamaz. Yalnızca mesaj gönderebilirler.

### AutoGen v0.4'te üç API katmanı

1. **Core.** Düşük düzeyli actor framework'ü. `AgentRuntime`, `Agent`, `Message`, `Topic`. Asenkron mesaj değişimi, olay驱动lı.
2. **AgentChat.** Görev驱动lı üst düzey API (v0.2'nin ConversableAgent yerine). `AssistantAgent`, `UserProxyAgent`, `RoundRobinGroupChat`, `SelectorGroupChat`.
3. **Extensions.** Entegrasyonlar — OpenAI, Anthropic, Azure, araçlar, hafıza.

### Neden ayrışma önemli

v0.2 modelinde `agent_a.chat(agent_b)` çağırmak senkron olarak agent_a'yı agent_b dönene kadar bloke eder. v0.4'te `send(agent_b, msg)` mesajı agent_b'nin gelen kutusuna koyar ve döner. Runtime daha sonra teslim eder. Üç sonuç:

- **Hata izolasyonu.** Agent B'nin çökmesi Agent A'yı çökertmez — runtime B'nin işleyicisindeki hatayı yakalar ve ne yapacağına karar verir (log, retry, dead-letter).
- **Doğal eşzamanlılık.** Bir anda çok fazla mesaj yolda; actor'lar gelen kutularını eş zamanlı işler.
- **Dağıtıma hazır.** Gelen kutusu + taşıma soyutlaması, actor process içinde olsun ya da başka bir makinede olsun aynıdır.

### Topolojiler

- **RoundRobinGroupChat.** Agent'lar sabit rotasyonda sırayla gider.
- **SelectorGroupChat.** Bir seçici agent konuşma bağlamına göre bir sonraki kimin gideceğini seçer.
- **Magentic-One.** Web tarama, kod çalıştırma, dosya işleme için referans çoklu-agent takımı. AgentChat üzerine inşa edilmiş.

### Gözlem

OpenTelemetry desteği yerleşiktir. Her mesaj bir span emit eder; araç çağrıları 2026 OTel GenAI semantik inançlarına (Ders 23) göre `gen_ai.*` öznitelikleri taşır.

### Durum: bakım modu

2026 başları: AutoGen v0.7.x araştırma ve prototipleme için kararlıdır. Microsoft aktif geliştirmeyi Microsoft Agent Platformu'na (Ekim 2025'te halka açık önizleme; 1.0 GA hedefi 2026 Q1 sonu) kaydırmıştır. AutoGen kalıpları temiz taşınır — actor model dayanıklı fikirdir.

## İnşa Et

`code/main.py` stdlib bir actor runtime uygular:

- `Message` — `sender`, `recipient`, `topic`, `body` alanlı tipli payload.
- `Actor` — `receive(message, runtime)` ile soyut.
- `Runtime` — paylaşılan kuyruk, teslim, hata izolasyonuyla olay döngüsü.
- İki actor'lu demo: `ReviewerAgent` kodu inceler, `ChecklistAgent` kontrol listesi çalıştırır; uzlaşana kadar mesajlaşır.

Çalıştırın:

```bash
python3 code/main.py
```

Trace mesaj teslimatını, bir actor'daki simüle edilmiş hatanın diğerini çökertmediğini ve paylaşılan bir karara yakınsamayı gösterir.

## Kullan

- **AutoGen v0.4/v0.7** (bakım) — araştırma, prototipleme, çoklu-agent kalıpları için kararlı.
- **Microsoft Agent Platformu** (halka açık önizleme) — ileri yol; aynı actor-model fikirleri yenilenmiş API'da.
- **LangGraph swarm topolojisi** (Ders 13) — paylaşılan-araç geçişleriyle benzer kalıp.
- **Özel actor runtime** — belirli bir taşıma (NATS, RabbitMQ, gRPC) gerektiğinde.

## Teslim Et

`outputs/skill-actor-runtime.md`, verilen bir çoklu-agent görevi için asgari bir actor runtime artı bir takım şablonu (RoundRobin veya Selector) üretir.

## Alıştırmalar

1. Dead-letter kuyruğu ekleyin: bir işleyici hata fırlattığında, başarısız mesajı insan incelemesi için park edin. Toy'unuzda DLQ ne sıklıkla tetiklenir?
2. `SelectorGroupChat` uygulayın: bir seçici actor, konuşma durumuna göre bir sonraki mesajı kimin işleyeceğini seçer.
3. Dağıtımlı taşıma ekleyin:-process içi kuyruğu HTTP üzerinden JSON sunucusuyla değiştirin ki actor'lar ayrı process'lerde çalışabilsin.
4. Her mesaj için bir OTel span bağlayın. Ders 23'e göre `gen_ai.agent.name`, `gen_ai.operation.name` emit edin.
5. AutoGen v0.4'ün mimari yazısını okuyun. Toy kodu gerçek `autogen_core` API'sine taşıyın. Production'da önemli olan hangi şeyleri atladınız?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Actor | "Agent" | Özel durum + gelen kutusu + işleyici; paylaşılan bellek yok |
| Message | "Olay" | Tipli payload; actor'ların etkileşiminin tek yolu |
| Inbox | "Posta kutusu" | Actor başına bekleyen mesaj kuyruğu |
| Runtime | "Agent sunucusu" | Mesajları yönlendiren ve hataları izole eden olay döngüsü |
| Topic | "Kanal" | Actor'lar arası adlandırılmış publish-subscribe yolu |
| Fault isolation | "Bırak çöksün" | Bir actor'un başarısızlığı diğerlerini çökertmez |
| RoundRobinGroupChat | "Sabit rotasyonlu takım" | Agent'lar sırayla sırayla gider |
| SelectorGroupChat | "Bağlam yönlü takım" | Seçici bir sonraki kimin gideceğini seçer |
| Magentic-One | "Referans takım" | Web + kod + dosyalar için çoklu-agent ekibi |

## İleri Okuma

- [AutoGen v0.4, Microsoft Research](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) — yeniden tasarım yazısı
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — graf şeklinde alternatif
- [OpenTelemetry GenAI semantik inançları](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — AutoGen'in varsayılan olarak emit ettiği span'lar
