# Supervisor / Orkestratör-İşçi Kalıbı

> Bir ana (lead) agent plan yapar ve delege eder; uzmanlaşmış işçiler paralel bağlamlarda yürütür ve geri bildirir. Bu, Anthropic'in Research sisteminin (Claude Opus 4 ana, Sonnet 4 subagent'lar olarak) arkasındaki kalıptır ve dahili araştırma değerlendirmelerinde tek-agent Opus 4'e göre +%90.2 ölçülmüştür. Anthropic'in mühendislik yazısı, BrowseComp üzerindeki varyansın %80'inin tek başına token kullanımıyla açıklandığını bildiriyor — multi-agent büyük ölçüde her subagent'ın temiz bir bağlam penceresi alması nedeniyle kazanıyor. Bu ders, supervisor kalıbını ilkellerden inşa eder ve üretim dağıtımlarından 2026 mühendislik derslerini kapsar.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib, `threading`)
**Ön Koşullar:** Faz 16 · 04 (İlkel Model)
**Süre:** ~75 dakika

## Problem

Araştırma, tek-agent sistemlerin başarısız olduğu prototipik görevdir. "Multi-agent sistemlerinde 2023 ile 2026 arasında ne değişti?" diye sorarsınız. Tek bir agent beş makaleyi sırayla okur, bağlamının yarısını metinleriyle doldurur ve sonra hepsi hakkında birlikte akıl yürütmek zorundadır. Beşinci makaleye geldiğinde birinciyi unutur. Paralelleştiremez.

Supervisor kalıbı bunu düzeltir: bir ana agent aramayı planlar, her alt soruyu bir işçiye devreder ve sentezler. Her işçi dar bir soru için kendi 200k-tokenlık penceresini alır. Ana, ham makaleleri asla görmez — yalnızca işçi özetlerini görür.

Anthropic'in üretim Research sistemi, dahili araştırma değerlendirmelerinde tek bir Opus 4'e karşı +%90.2 bildiriyor. Aynı yazı, BrowseComp varyansının %80'inin *yalnızca token kullanımıyla* açıklandığını not ediyor. Subagent başına temiz bağlam ana mekanizmadır.

## Kavram

### Kalıbın kendisi

```
                 ┌──────────────┐
                 │   Ana        │  planlar, ayrıştırır,
                 │  (Opus 4)    │  sentezler
                 └──┬────┬───┬──┘
                    │    │   │
            ┌───────┘    │   └───────┐
            ▼            ▼           ▼
       ┌─────────┐  ┌─────────┐  ┌─────────┐
       │ İşçi1   │  │ İşçi2   │  │ İşçi3   │
       │(Sonnet) │  │(Sonnet) │  │(Sonnet) │
       └─────────┘  └─────────┘  └─────────┘
          temiz       temiz        temiz
          bağlam      bağlam       bağlam
```

Ana, ham malzemeleri asla okumaz. İşçiler, ana sentezlenene kadar birbirlerinin işini görmez. Her ok, dar bir yapıt taşıyan bir handoff'tur.

### Neden kazanıyor

Üç mekanizma:

1. **Subagent başına temiz bağlam.** "FIPA-ACL mirası"nı keşfeden bir işçi, ananın planlarken harcadığı 40k token'ı taşımaz. Tek bir soru için 200k pencere alır.
2. **Prompt yoluyla uzmanlaşma.** Ananın promptu "ayrıştır ve sentezle"dir, "araştır" değil. Her işçinin promptu dardır: "X'te ne değişti?" bul. Odaklanmış promptlar odaklanmış çıktılar üretir.
3. **Paralellik.** İşçiler eşzamanlı çalışır. Duvar saati yaklaşık olarak `max(işçi_süreleri) + plan + sentez`'dir, `sum(işçi_süreleri)` değil.

### Mühendislik dersleri (Anthropic 2025)

Anthropic yazısı, 2026'da hâlâ geçerli olan birkaç üretim dersi listeler:

- **Çabayı sorgu karmaşıklığına göre ölçeklendirin.** Basit sorgular: bir agent, 3-10 araç çağrısı. Karmaşık sorgular: 10+ agent. Ana bunu tahmin etmelidir, çağıran değil.
- **Önce geniş, sonra dar.** Önce geniş alt sorulara ayırın, sonra cevap derinliği haklı kılıyorsa her alt soru için daha fazla işçi başlatın.
- **Gökkuşağı dağıtımları (rainbow deployments).** Agent'lar uzun ömürlüdür ve durum bilgisidir. Geleneksel mavi-yeşil işe yaramaz. Anthropic gökkuşağı kullanır: yenilerini kademeli olarak kullanıma sunarken eskilerinin sönmesini sağlar.
- **Token kullanımı baskındır.** Multi-agent, tek-agent'ın yaklaşık 15 katı token kullanır. Yalnızca görevin değeri maliyeti haklı kıldığında çalıştırın.

### LangGraph dönüşü

LangGraph başlangıçta yüksek düzeyli bir `create_supervisor` yardımcısıyla bir `langgraph-supervisor` kütüphanesi gönderdi. 2025'te LangChain önerisini supervisor kalıbını doğrudan araç çağrısı yoluyla uygulamaya taşıdı, çünkü araç çağrıları *supervisor'ın ne gördüğü* üzerinde daha fazla kontrol sağlar (bağlam mühendisliği). Kütüphane hâlâ çalışıyor; belgeler artık araç çağrısı biçimini öneriyor.

### Başarısızlık modları

- **Ana planı halüsinasyon yapar.** Ana, gerçek soruyu ayrıştırmayan alt sorular üretirse, işçiler yanlış hedef üzerinde hassas araştırma yapar.
- **İşçiler aşırı keşfe çıkar.** Açık kapsam sınırları olmadan, işçiler atanmış alt sorularının ötesine sürüklenir ve sentez adımını kirletir.
- **Sentez çakışmaları.** İki işçi çelişkili gerçekler döner. Ana ya yeniden sormalı (bir tur ekler) ya da anlaşmazlığı açıkça not etmelidir. Bir tarafı sessizce seçmek en kötü başarısızlıktır: kullanıcı anlaşmazlığın olduğunu asla bilmez.

### Supervisor ne zaman yanlıştır

- **Sıralı görevler.** Adım 2, kelimenin tam anlamıyla Adım 1'in çıktısına ihtiyaç duyuyorsa, paralellik hiçbir şey kazandırmaz. Bir pipeline kullanın (CrewAI Sequential, LangGraph doğrusal graf).
- **Basit sorgular.** Tek-agent onları daha hızlı ve ucuz halleder. İşçi başlatmadan önce ananın "çabayı ölçeklendir" kontrolünü kullanın.
- **Sıkı determinizm.** Supervisor, LLM seçili delegasyon kullanır. Statik grafikler, uyarlanabilirlikten çok denetim/yeniden oynatma önemli olduğunda daha iyidir.

## İnşa Et

`code/main.py`, `threading` kullanarak üç paralel işçili bir supervisor uygular. Ana bir sorguyu alt sorulara ayırır, işçiler her alt soruda eşzamanlı çalışır ve ana sentezler. Gerçek LLM yok — işçiler fetch-and-summarize'ı simüle etmek için komut dosyası olarak yazılmıştır.

Anahtar yapı:

- `Lead.plan(query)` bir sorguyu 3 alt soruya böler.
- `Worker.run(sub_q)` sahte bir özet döner (üretimde herhangi bir araç kullanan agent olabilir).
- `Lead.run(query)` işçileri iş parçacıklarında başlatır, birleştirir ve sentezler.

Çalıştırın:

```
python3 code/main.py
```

Çıktı planı, paralel işçi izlerini başlangıç/bitiş zaman damgalarıyla ve son sentezi gösterir. Duvar saati kazancını görebilirsiniz: üç 0.3 saniyelik işçi ~0.35 saniyede çalışır, 0.9'da değil.

## Kullan

`outputs/skill-supervisor-designer.md`, bir kullanıcı sorgusu alır ve bir supervisor kalıbı tasarımı üretir: ana sistem promptu, işçi rolleri, alt soru ayrıştırma kuralları ve sentez şablonu. Yeni bir araştırma tarzı agent sistemi inşa etmeden önce bunu kullanın.

## Dağıt

Supervisor kalıbını dağıtmadan önce kontrol listesi:

- **Model eşleştirme.** Ana, akıl yürütme seviyesi bir modelde (Opus sınıfı, `o3` sınıfı). İşçiler, daha hızlı, daha ucuz bir modelde (Sonnet, `o4-mini`).
- **İşçi zaman aşımı.** Medyan çalışma süresinin 2 katını aşan her işçi öldürülür; ana ya daha dar kapsamla yeniden başlatır ya da onsuz devam eder.
- **İşçi başına token tavanı.** Katı sınır (diyelim ki beklenen sentez girdisinin 10 katı), çığır açan bir işçinin bütçeyi patlatmasını engeller.
- **Gözlemlenebilirlik.** Ananın planını, her işçinin araç çağrılarını ve sentezi izleyin. Bu, herhangi bir post-mortem hata ayıklamanın temelidir.
- **Gökkuşağı dağıtımı.** Durum bilgisi olan uzun ömürlü agent'ların kademeli sürüm geçişine ihtiyacı vardır, anında değişime değil.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın, sonra anayı 3 yerine 5 işçi başlatacak şekilde değiştirin. Duvar saati etkisini gözlemleyin. Bu demoda hangi işçi sayısında başlatma ek yükü paralel tasarrufları aşıyor?
2. Bir işçi zaman aşımı uygulayın: 0.5 saniyeden uzun çalışan her işçiyi öldürün ve ananın kalan sonuçları sentezlemesini sağlayın. Bir işçinin kesildiğini bilmek için hangi gözlemlenebilirliğe ihtiyacınız var?
3. Ananın sentezine bir çakışma tespit adımı ekleyin: iki işçi çelişkili yanıtlar dönerse, ana birini seçmek yerine anlaşmazlığı not eder. LLM çağırmadan çelişkiyi nasıl tespit edersiniz?
4. Anthropic'in Research-sistemi mühendislik yazısını okuyun. Bu oyuncak demonun üretimde çalışması için benimsemesi gereken üç pratiği listeleyin.
5. LangGraph'ın `create_supervisor` (eski) ile yeni araç çağrısı önerisini karşılaştırın. Hangisi supervisor'ın ne gördüğü üzerinde size daha iyi kontrol sağlar? Anthropic neden senteze yalnızca alt yanıtları geçiriyor, ham işçi bağlamını değil?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Supervisor | "Ana agent" | Planlayan, devreden ve sentezleyen bir orkestratör agent. İşi kendisi yapmaz. |
| Worker (İşçi) | "Subagent" | Supervisor tarafından dar kapsam ve kendi bağlam penceresiyle çağrılan odaklanmış bir agent. |
| Orchestrator-worker | "Supervisor kalıbı" | Aynı şey, farklı ad. 2026 literatürü ikisini de kullanır. |
| Fresh context (Temiz bağlam) | "Temiz pencere" | Bir işçinin bağlamı, ananın geçmişinden değil, kendi sistem promptundan ve atanmış sorusundan başlar. |
| Rainbow deployment (Gökkuşağı dağıtımı) | "Kademeli kullanıma sunma" | Uzun ömürlü durum bilgisi olan agent'ların sürümlenmiş sönüm-değiştirmeye ihtiyacı vardır, mavi-yeşile değil. |
| Token dominance (Token baskınlığı) | "Bağlam değişkendir" | Anthropic'e göre araştırma değerlendirme varyansının %80'i toplam kullanılan token'lardan gelir, model seçiminden değil. |
| Scale effort (Çabayı ölçeklendir) | "Agent sayısını karmaşıklığa eşle" | Ana, sorgu zorluğunu tahmin eder ve buna göre 1 veya 10+ işçi başlatır. |
| Synthesis conflict (Sentez çakışması) | "İşçiler anlaşamıyor" | İki işçi çelişkili gerçekler döner; ana birini sessizce seçmek yerine anlaşmazlığı yüzeye çıkarmalıdır. |

## İleri Okuma

- [Anthropic mühendislik — Multi-agent araştırma sistemimizi nasıl inşa ettik](https://www.anthropic.com/engineering/multi-agent-research-system) — supervisor kalıbı için üretim referansı
- [LangGraph iş akışları ve agent'ları](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — araç çağrısı supervisor artık önerilen biçim
- [LangGraph supervisor referansı](https://reference.langchain.com/python/langgraph-supervisor) — eski yardımcı, 2026 üretimde hâlâ kullanılıyor
- [OpenAI cookbook — Orchestrating Agents: Routines and Handoffs](https://developers.openai.com/cookbook/examples/orchestrating_agents) — handoff tabanlı supervisor varyantı
