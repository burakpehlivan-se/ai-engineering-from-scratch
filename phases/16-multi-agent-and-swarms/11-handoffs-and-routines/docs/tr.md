# Handoff'lar ve Routine'ler — Durumsuz Orkestrasyon

> OpenAI'nin Swarm'ı (Ekim 2024), multi-agent orkestrasyonu iki ilkele indirgedi: **routine'ler** (bir sistem promptu olarak talimatlar + araçlar) ve **handoff'lar** (başka bir Agent döndüren bir araç). Durum makinesi yok, dallanma DSL'i yok — LLM, doğru handoff aracını çağırarak yönlendirir. OpenAI Agents SDK (Mart 2025) üretim halefidir. Swarm'ın kendisi en temiz kavramsal referans olmaya devam ediyor — tüm kaynağı birkaç yüz satıra sığar. Kalıbın viral olmasının nedeni, API yüzeyinin kabaca "agent = prompt + tools; handoff = agent döndüren fonksiyon" olmasıdır. Sınırlama: durumsuz, bu nedenle bellek çağıranın problemidir.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 16 · 04 (İlkel Model)
**Süre:** ~60 dakika

## Problem

Her multi-agent çatısı DSL'ini öğrenmenizi ister: LangGraph düğümleri ve kenarları, CrewAI ekipleri ve görevleri, AutoGen GroupChat ve yöneticileri. DSL'ler gerçek soyutlamalardır, ancak şeyi ihtiyaç duyduğundan daha ağır hissettirirler.

Swarm, ters yönde iterir: modelin zaten sahip olduğu araç çağrısı yeteneğini kullanın. Handoff'lar araç çağrıları olur. Orkestratör, konuşmayı o an elinde tutan agent'tır. Durum makinesi, agent'ların sistem promptlarında örtüktür.

## Kavram

### İki ilkel

**Routine.** Bir agent'ın rolünü ve mevcut araçlarını tanımlayan bir sistem promptu. Kapsamlı bir talimat seti olarak düşünün: "sen bir triyaj agent'ısın; kullanıcı iadeleri sorarsa, iade agent'ına handoff yap."

**Handoff.** Agent'ın çağırabileceği, yeni bir Agent nesnesi döndüren bir araç. Swarm çalışma zamanı, Agent dönüş değerini algılar ve bir sonraki tur için etkin agent'ı değiştirir.

Tüm soyutlama budur.

```
def transfer_to_refunds():
    return refund_agent  # Swarm Agent dönüşünü görür → etkin agent'ı değiştirir

triage_agent = Agent(
    name="triage",
    instructions="Kullanıcıyı doğru uzmana yönlendir.",
    functions=[transfer_to_refunds, transfer_to_sales, transfer_to_support],
)
```

Triyaj agent'ının sistem promptu, kullanıcı mesajına göre doğru handoff'u seçmesini sağlar. LLM'in araç çağrısı yönlendirmeyi yapar.

### Neden viral

- **Küçük API.** Öğrenilecek iki kavram.
- **Modelin zaten yaptığını kullanır.** Araç çağrısı sağlayıcılar arasında zaten üretim kalitesindedir.
- **Durum makinesi yükü yok.** Grafı tanımlamazsınız; agent'ların promptları kime handoff yapacaklarını tanımlar.

### Durumsuz ödün

Swarm, çalıştırmalar arasında açıkça durumsuzdur. Çatı, bir çalıştırma sırasında bir mesaj geçmişi tutar, ancak hiçbir şeyi kalıcı kılmaz. Bellek, süreklilik, uzun süren görevler — hepsi çağıranın problemi.

Üretimde (OpenAI Agents SDK, Mart 2025) değişen başlıca şeylerden biri buydu: SDK, handoff ilkelini korurken yerleşik oturum yönetimi, koruma bariyerleri (guardrails) ve izleme ekledi.

### Swarm/handoff'lar ne zaman uyar

- **Triyaj kalıpları.** Ön cephe agent'ı kullanıcıyı bir uzmana yönlendirir.
- **Beceri tabanlı handoff'lar.** "Görev kod gerektiriyorsa, kod yazarını çağır; araştırma gerektiriyorsa, araştırmacıyı çağır."
- **Kısa, sınırlı konuşmalar.** Müşteri desteği, SSS'den bilete, basit iş akışları.

### Swarm ne zaman zorlanır

- **Paylaşılan bellekle uzun oturumlar.** Handoff'lar, konuşma durumunu yeni agent'ın promptuna artı geçmişe sıfırlar. Çağıran tarafından yönetilen bellek olmadan, agent'lar arasında kalıcı durum yoktur.
- **Paralel yürütme.** Handoff birer birer — etkin agent değişir. Paralellik, birden fazla Swarm çalıştırmasını düzenleyen çağıranı gerektirir.
- **Denetim ve yeniden oynatma.** Durumsuz çalıştırmalar tam olarak yeniden oynatılamaz; LLM'in handoff seçimi deterministik değildir.

### OpenAI Agents SDK (Mart 2025)

Üretim halefi şunları ekler:

- **Oturum durumu.** Çalıştırmalar arasında kalıcı iş parçacığı.
- **Guardrails (Koruma bariyerleri).** Girdi/çıktı doğrulama kancaları.
- **İzleme (Tracing).** Her araç çağrısı ve handoff günlüğe kaydedilir.
- **Handoff filtreleri.** Handoff'ta hangi bağlamın aktarılacağını kontrol eder.

Handoff ilkeli hayatta kalır; üretim ergonomisi onun etrafına eklenir.

### Swarm ve GroupChat

İkisi de LLM güdümlü yönlendirme kullanır, ancak **bir sonrakini kimin seçtiği** konusunda farklılaşırlar:

- GroupChat: bir seçici (fonksiyon veya LLM) dışarıdan bir sonraki konuşanı seçer.
- Swarm: mevcut agent, bir handoff aracı çağırarak halefini seçer.

Swarm "agent neyin sırada olduğuna karar verir"; GroupChat "yönetici neyin sırada olduğuna karar verir". Swarm'ın kararı, etkin agent'ın araç çağrısında yaşar; GroupChat'inki `GroupChatManager`'da yaşar.

## İnşa Et

`code/main.py` Swarm'ı sıfırdan uygular: bir Agent dataclass'ı, bir handoff mekanizması (araç Agent döner) ve agent değişikliklerini algılayan bir çalıştırma döngüsü.

Demo: bir triyaj agent'ı iade, satış veya destek uzmanlarına yönlendirir. Her uzmanın kendi araçları vardır. Çalıştırma döngüsü her handoff'u yazdırır.

Çalıştırın:

```
python3 code/main.py
```

## Kullan

`outputs/skill-handoff-designer.md`, belirli bir görev için bir handoff topolojisi tasarlar: hangi agent'lar var, hangi handoff'ları çağırabilirler, hangi bağlam aktarılır.

## Dağıt

Kontrol listesi:

- **Handoff günlüğü.** Her handoff, agent'tan, agent'a, bağlam anlık görüntüsüyle bir iz olayı yazar.
- **Bağlam aktarım kuralları.** Handoff'ta ne taşınacağına karar verin: tam geçmiş (pahalı), son N mesaj veya bir özet.
- **Handoff'ta guardrail.** Farklı araç izinleri olan bir uzmana yapılan bir handoff, kimliği doğrulanmalıdır — aksi takdirde prompt enjeksiyonu istenmeyen handoff'ları zorlayabilir.
- **Döngü tespiti.** İki agent'ın birbirine geri vermesi yaygın bir başarısızlıktır; basit bir son-K halka kontrolüyle tespit edin.
- **Geri dönüş agent'ı.** Bir handoff hedefi yoksa, güvenli bir varsayılana geri dönün.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın, iade agent'ına triyaj yapın. İkinci turun etkin agent'ının iade olduğunu doğrulayın.
2. Bir döngü tespit kuralı ekleyin: aynı iki agent art arda 3 kez handoff yaptıysa, çıkışı zorlayın. Geri dönüşü tasarlayın.
3. OpenAI Agents SDK belgelerinde handoff filtrelerini okuyun. "Handoff'ta özetle" sürümünü uygulayın: giden agent, gelen agent devralmadan önce bağlamı bir madde özetine sıkıştırır.
4. Swarm handoff'ını bir GroupChatManager seçici ile karşılaştırın. Hangi kalıp prompt enjeksiyonunu daha kötü yapar ve neden?
5. Swarm cookbook'unu (https://developers.openai.com/cookbook/examples/orchestrating_agents) okuyun. OpenAI Agents SDK'nın değiştirdiği veya koruduğu Swarm'ın bir açık tasarım kararını belirleyin.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Routine | "Agent promptu" | Sistem promptu + araç listesi. Rolü ve mevcut handoff'ları tanımlar. |
| Handoff | "Başka bir agent'a aktar" | Etkin agent'ın çağırabileceği, yeni bir Agent döndüren bir araç. Çalışma zamanı etkin agent'ı değiştirir. |
| Stateless (Durumsuz) | "Çalıştırmalar arasında bellek yok" | Swarm hiçbir şeyi kalıcı kılmaz; bellek çağıranın sorumluluğundadır. |
| Active agent (Etkin agent) | "Şu an kim konuşuyor" | Şu anda konuşmayı elinde tutan agent. Handoff bunu değiştirir. |
| Context transfer (Bağlam aktarımı) | "Handoff'ta ne taşınır" | Gelen agent'ın ne göreceğine dair politika: tam, son N veya özetlenmiş. |
| Handoff loop (Handoff döngüsü) | "Agent'lar ping-pong" | İki agent'ın birbirine geri vermeye devam ettiği başarısızlık modu. |
| OpenAI Agents SDK | "Üretim Swarm'ı" | Mart 2025 halefi; oturumları, guardrails'ı, izlemeyi handoff ilkelinin üzerine ekler. |
| Handoff filter (Handoff filtresi) | "Aktarımda kapı" | Handoff sınırında bağlamı incelemek ve değiştirmek için SDK özelliği. |

## İleri Okuma

- [OpenAI cookbook — Orchestrating Agents: Routines and Handoffs](https://developers.openai.com/cookbook/examples/orchestrating_agents) — referans ifade
- [OpenAI Swarm deposu](https://github.com/openai/swarm) — orijinal uygulama, kavramsal referans olarak tutulur
- [OpenAI Agents SDK belgeleri](https://openai.github.io/openai-agents-python/) — oturumlar ve izleme ile üretim halefi
- [Anthropic handoff-in-Claude notları](https://docs.anthropic.com/en/docs/claude-code) — Claude Code subagent'larının `Task` yoluyla handoff benzeri bir kalıbı nasıl kullandığı
