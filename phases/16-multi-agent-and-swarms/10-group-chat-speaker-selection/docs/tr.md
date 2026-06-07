# Grup Sohbeti ve Konuşmacı Seçimi

> AutoGen GroupChat ve AG2 GroupChat, N agent arasında bir konuşmayı paylaşır; bir seçici fonksiyon (LLM, round-robin veya özel) bir sonraki konuşanı seçer. Bu, ortaya çıkan multi-agent konuşmasının arketipidir — agent'lar statik bir graf içindeki rollerini bilmez, yalnızca paylaşılan havuza tepki verir. AutoGen v0.2'nin GroupChat semantiği AG2 çatalında korundu; AutoGen v0.4 onu olay güdümlü bir actor modeli olarak yeniden yazdı. Microsoft, Şubat 2026'da AutoGen'i bakım moduna aldı ve onu Semantic Kernel ile birleştirerek Microsoft Agent Framework'e (RC Şubat 2026) dahil etti. GroupChat ilkeli hem AG2'de hem de Microsoft Agent Framework'te hayatta kalıyor — bir kez öğrenin, her yerde kullanın.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 16 · 04 (İlkel Model)
**Süre:** ~60 dakika

## Problem

Statik grafikler (LangGraph) iş akışı bilindiğinde harikadır. Gerçek konuşmalar statik değildir: bazen kod yazarı incelemeciye sorar, bazen araştırmacıya, bazen yazara. Her olası handoff'u elle kodlamak kenar patlaması üretir. *Paylaşılan bir havuza tepki veren agent'lar* istersiniz, bir sonraki konuşanı kimin olacağına bazı fonksiyonlar karar verir.

Tam olarak AutoGen GroupChat'in yaptığı budur.

## Kavram

### Şekil

```
 ┌─── paylaşılan havuz ────┐
 │ m1 m2 m3 ... │
 └─────────┬──────────┘
 │ (herkes hepsini okur)
 ┌───────┬─────────┼─────────┬───────┐
 ▼ ▼ ▼ ▼ ▼
 Agent A Agent B Agent C Agent D Seçici
 │
 ▼
 "sonraki konuşan = C"
```

Her agent her mesajı görür. Her turda bir sonraki konuşanı seçen bir seçici fonksiyon çağrılır.

### Üç seçici çeşidi

**Round-robin.** Sabit döngü. Deterministik. N'de doğrusal ölçeklenir ancak bağlamı yok sayar — konu hukuk incelemesi olduğunda bile kod yazarı sırayı alır.

**LLM seçili.** Havuzun son kısmını okuyan ve en iyi bir sonraki konuşanı döndüren bir LLM çağrısı. Bağlama duyarlı ama yavaş: her tur bir LLM çağrısı ekler. AutoGen'in varsayılanı.

**Özel.** İstediğiniz mantığa sahip bir Python fonksiyonu. Tipik: geri dönüş kurallarıyla LLM seçili (örn. "kod yazarından sonra her zaman doğrulayıcıya sırayı ver").

### ConversableAgent API'si

```
agent = ConversableAgent(
 name="coder",
 system_message="You write Python.",
 llm_config={...},
)
chat = GroupChat(agents=[coder, reviewer, tester], messages=[])
manager = GroupChatManager(groupchat=chat, llm_config={...})
```

`GroupChatManager` seçiciyi tutar. Bir agent bir turu tamamladığında, yönetici seçiciyi çağırır; bu bir sonraki agent'ı döner. Bir sonlandırma koşulu karşılanana kadar döngü devam eder.

### Sonlandırma

Üç yaygın kalıp:

- **Maks tur.** Toplam turlar üzerinde sert sınır.
- **"TERMINATE" belirteci.** Agent'lar sentinel bir mesaj yayabilir; biri göründüğünde yönetici durur.
- **Hedefe ulaşma kontrolü.** Her turda hafif bir doğrulayıcı çalışır ve tamamlandığında sohbeti durdurur.

### AutoGen → AG2 bölünmesi ve Microsoft Agent Framework birleşmesi

2025'in başında Microsoft, AutoGen'in (v0.4) büyük bir yeniden yazımını olay güdümlü bir actor modeli etrafında başlattı. Topluluk, AutoGen v0.2'nin GroupChat semantiğini AG2 olarak çatalladı ve ilk benimseyenlerin entegre ettiği API'yi korudu.

Şubat 2026'da Microsoft, AutoGen'in bakım moduna gireceğini ve olay güdümlü actor modelinin **Microsoft Agent Framework**'e (RC Şubat 2026, artık Semantic Kernel ile birleşti) taşınacağını duyurdu. GroupChat kavramı her iki hatta da hayatta kalıyor; uygulama detayları farklı. AG2, v0.2 uyumlu kod için tercih edilen yukarı yöndür.

### GroupChat ne zaman uyar

- **Ortaya çıkan konuşmalar.** Her olası bir sonraki konuşmacıyı önceden bağlamak istemezsiniz.
- **Rol karıştırma görevleri.** Kod yazarı araştırmacıya sorar, araştırmacı arşivciye sorar, arşivci kod yazarına geri sorar. Akış bir DAG değildir.
- **Keşif amaçlı problem çözme.** "Montaj hattı" değil, "beyin fırtınası toplantısı" olarak düşünün.

### Ne zaman başarısız olur

- **Sıkı determinizm.** LLM seçici tutarsız olabilir. Aynı prompt, farklı çalıştırmalar, farklı bir sonraki konuşmacılar.
- **Dalkavukluk basamakları.** Agent'lar en kendinden emin konuşana boyun eğer. Açıkça karşı-prompt verin.
- **Bağlam şişmesi.** Her agent her mesajı okur; 10 turdan sonra bağlam devasadır. Görünümleri kapsamak için projeksiyonlar (Ders 15) kullanın.
- **Sıcak konuşmacılar.** Bir agent, seçici onun uzmanlıklarını tercih ettiği için konuşmaya egemen olur. Seçici özelliği olarak konuşmacı dengesi tanıtın.

### Grup sohbeti ve supervisor

Aynı ilkeller, farklı varsayılanlar:

- Supervisor: bir agent planlar ve diğerleri yürütür. Seçici "planlayıcıya ne yapılacağını sor"dur.
- Grup sohbeti: tüm agent'lar eştir; seçici paylaşılan havuz üzerinde bir fonksiyondur.

İkisi de Ders 04'ten dört ilkeli kullanır. Grup sohbeti, LLM seçili orkestrasyon ve tam havuz paylaşılan durumuna varsayılan olarak gelir.

## İnşa Et

`code/main.py` stdlib'de sıfırdan bir GroupChat uygular. Üç agent (kod yazarı, incelemeci, yönetici), round-robin ve LLM seçili varyantlar ve bir `TERMINATE` belirteci üzerinde sonlandırma.

Demo, her iki varyant için konuşma transkriptini ve seçicinin karar izini yazdırır.

Çalıştırın:

```
python3 code/main.py
```

## Kullan

`outputs/skill-groupchat-selector.md`, belirli bir görev için bir GroupChat seçici yapılandırır — round-robin ve LLM seçili ve özel arasında ve hangi seçici girdilerinin (son mesajlar, agent uzmanlıkları, tur sayıları) kullanılacağını.

## Dağıt

Kontrol listesi:

- **Maks tur sınırı.** Her zaman. Tipik görevler için 10-20.
- **Konuşmacı dengesi metriği.** Agent başına turları izleyin; dengesizlik bir eşiği aştığında alarm verin.
- **Sonlandırma belirteci.** `TERMINATE` veya özel bir doğrulayıcı agent.
- **Projeksiyon veya kapsamlı bellek.** ~10 mesajdan sonra, bağlam şişmesini önlemek için her agent'a yalnızca kapsamlı bir görünüm vermeyi düşünün.
- **Seçici günlüğü.** LLM seçili varyantlar için, seçicinin hem girdisini hem de seçimini günlüğe kaydedin. Aksi takdirde hata ayıklama imkansızdır.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Round-robin ile LLM seçili altında konuşmayı karşılaştırın. Her birinin altında hangi agent egemendir?
2. Seçiciye bir "agent başına maks konuşma" kuralı ekleyin. Transkripti nasıl etkiler?
3. Bir hedefe-ulaşma sonlandırması uygulayın: incelemeci "approved" döndüğünde durun. Tur sınırından önce ne sıklıkta tetiklenir?
4. AutoGen kararlı belgelerinde GroupChat'i okuyun (https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/group-chat.html). `GroupChatManager` tarafından kullanılan varsayılan seçiciyi belirleyin.
5. AG2 deposunu (https://github.com/ag2ai/ag2) okuyun ve v0.2 GroupChat'ini v0.4 olay güdümlü sürümle karşılaştırın. v0.4 hangi somut özelliği (verim, hata toleransı, birleştirilebilirlik) ekler?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| GroupChat | "Agent'lar bir sohbet odasında" | Paylaşılan mesaj havuzu + seçici fonksiyon. AutoGen / AG2 ilkeli. |
| Speaker selection (Konuşmacı seçimi) | "Sırada kim konuşuyor" | Bir sonraki agent'ı seçen fonksiyon. Round-robin, LLM seçili veya özel. |
| GroupChatManager | "Toplantı yöneticisi" | AutoGen bileşeni, seçiciyi sahiplenir ve turlar üzerinde döngü yapar. |
| ConversableAgent | "Temel agent" | AutoGen temel sınıfı; mesaj gönderebilen ve alabilen bir agent. |
| Termination token (Sonlandırma belirteci) | "Durdurma kelimesi" | Sohbeti bitiren sentinel string (genellikle `TERMINATE`). |
| Hot speaker (Sıcak konuşmacı) | "Bir agent egemen oluyor" | Seçicinin aynı agent'ı tekrar tekrar seçtiği başarısızlık modu. |
| Context bloat (Bağlam şişmesi) | "Havuz sınırsız büyür" | Her agent önceki her mesajı okur; bağlam turlarla büyür. |
| Projection (Projeksiyon) | "Kapsamlı görünüm" | Bağlam şişmesini önlemek için paylaşılan havuza role özgü görünüm. |

## İleri Okuma

- [AutoGen grup sohbeti belgeleri](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/group-chat.html) — referans uygulama
- [AG2 deposu](https://github.com/ag2ai/ag2) — topluluk AutoGen v0.2 devamı
- [Microsoft Agent Framework belgeleri](https://microsoft.github.io/agent-framework/) — birleşik halef, RC Şubat 2026
- [AutoGen v0.4 sürüm notları](https://microsoft.github.io/autogen/stable/) — olay güdümlü actor modeli yeniden yazım detayları
