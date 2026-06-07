# LangGraph: Durumlu Graf'lar ve Dayanıklı Çalıştırma

> LangGraph 2026'da düşük düzeyli durumlu orkestrasyon için referanstır. Agent bir durum makinesidir (state machine); düğümler fonksiyonlardır; kenarlar geçişlerdir; state immutabledir (değişmez) ve her adımdan sonra checkpoint edilir (denetim noktası). Herhangi bir hata durumunda tam kaldığı yerden devam eder.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 14 · 12 (Workflow Kalıpları)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- LangGraph'in temel modelini tanımlayın: değişmez state, fonksiyon düğümleri, koşullu kenarlar ve adım sonrası checkpoint'li durum makinesi.
- Dokümanın vurguladığı dört yeteneği adlandırın: dayanıklı çalıştırma (durable execution), streaming (akış), human-in-the-loop (insan döngüde), kapsamlı hafıza.
- LangGraph'in desteklediği üç orkestrasyon topolojisini açıklayın: supervisor (yönetici), peer-to-peer (swarm/yardımcısız), hiyerarşik (iç içe subgraph'lar).
- Değişmez state, koşullu kenarlar ve checkpoint/devam döngüsüyle stdlib bir durum grafiği uygulayın.

## Problem

Agent'lar ve workflow'lar ortak bir sorunu paylaşır: 40 adımlık bir çalıştırmada 38. adımda başarısız olursa, 38. adımdan devam etmek istersiniz, baştan başlamak değil. İkincil sınıf state modelleri, operatörleri taze çalıştırmalar varsayan bir kitaplığın etrafında yeniden denemelerle baş başa bırakır.

LangGraph'in tasarım cevabı: state birinci sınıf tipli bir nesnedir, mutasyonlar açıktır ve checkpoint'ler her düğümden sonra kalıcı hale gelir. Devam etmek bir `load_state(session_id)` çağrısıdır.

## Kavram

### Graf

Bir graf şu şekilde tanımlanır:

- **State tipi.** Her düğümün okuduğu ve değiştirdiği tipli bir dict (veya Pydantic modeli).
- **Düğümler.** Saf fonksiyonlar `(state) -> state_update`. Güncellemeler return sonrası state'e birleştirilir.
- **Kenarlar.** Koşullu veya doğrudan geçişler.
- **Giriş ve çıkış.** `START` ve `END` sentinelleri sınırı işaretler.

Örnek: `classify`, `refund`, `bug`, `sales`, `done` düğümlü bir agent — graf olarak bir yönlendirme workflow'u.

### Dayanıklı çalıştırma

Her düğümden sonra, runtime state'i serileştirir ve bir checkpoint'e (SQLite, Postgres, Redis, özel) yazar. N. adımda başarısızlıkta, runtime `resume(session_id)` yapabilir ve tam state ile N+1. adımdan devam edebilir.

LangGraph dokümanları production kullanıcılarını açıkça vurgular: Klarna, Uber, J. P. Morgan. İddia graf şekli değil; graf şekli artı checkpointing'i kurtarmayı ucuza yapar.

### Streaming

Her düğüm kısmi çıktı üretebilir. Graf, düğüm başına delta olaylarını çağrıcıya aktarır, böylece UI graf çalışırken güncellenir.

### Human-in-the-loop

Düğümler arasında state'i inceleyin ve değiştirin. Uygulamalar: kritik bir düğüm önce duraklatın, state'i bir insana gösterin, değişiklikleri kabul edin, devam edin. Checkpointing bunu kolaylaştırır çünkü state zaten serileştirilmiş.

### Hafıza

Kısa vadeli (bir çalışma içinde — state'te konuşma geçmişi) ve uzun vadeli (çalışmalar arası — checkpoint artı ayrı bir uzun vadeli depo aracılığıyla kalıcı). LangGraph, araçlar aracılığıyla harici hafıza sistemleriyle (Mem0, özel) entegre olur.

### Üç topoloji

1. **Supervisor.** Merkezi yönlendirici LLM uzman subagent'lara yönlendirir. `langgraph-supervisor`'da `create_supervisor()` (ancak LangChain ekibi 2026'da daha fazla bağlam kontrolü için bunu doğrudan araç çağrılarıyla yapmayı önerir).
2. **Swarm / peer-to-peer.** Agent'lar doğrudan paylaşılan bir araç yüzeyi aracılığıyla devreder. Merkezi yönlendirici yok.
3. **Hyerarşik.** Sub-supervisor'ları yöneten supervisor'lar, iç içe subgraph'lar olarak uygulanır.

### Bu kalıp nerede yanlış gider

- **Checkpoint'ler çok küçük.** Yalnızca konuşma turlarını checkpoint etmek araç state'ini ve hafıza yazmalarını kurtarılmaz bırakır. Tam state serileştirilmelidir.
- **Belirsiz düğümler.** Devam etme, düğüm girdilerinin aynı state güncellemesini ürettiğini varsayar. Rastgele tohumlar, duvar saati, harici API'ler yakalanmalıdır.
- **Koşullu kenarların aşırı kullanımı.** Her kenarın koşullu olduğu bir graf, akıl yürütülemez bir durum makinesidir. Seyrek dallanmalarla doğrusal zincirleri tercih edin.

## İnşa Et

`code/main.py` stdlib dayanıklı bir graf uygular:

- `State` — `messages`, `step`, `route`, `output`, `human_approval` alanlı tipli dict.
- `Node` — state alan ve güncelleme dict'ini döndüren callable.
- `StateGraph` — düğümler + kenarlar + koşullu kenarlar + çalıştır + devam.
- `SQLiteCheckpointer` (bellek içi sahte) — her düğümden sonra state'i serileştirir; `load(session_id)` geri yükler.
- Demo graf: classify -> branch(refund / bug / sales) -> human gate -> send.

Çalıştırın:

```bash
python3 code/main.py
```

Trace ilk çalıştırmada human gate'te başarısızlığı, persistansı, sonra devamın son çıktıyı üretmesini gösterir.

## Kullan

- **LangGraph** — referans, production-ready. `create_react_agent`, `create_supervisor` veya kendi grafiğinizi oluşturun.
- **AutoGen v0.4** (Ders 14) — yüksek eşzamanlılık senaryoları için actor model alternatifi.
- **Claude Agent SDK** (Ders 17) — yerleşik oturum deposuyla yönetilen harness.
- **Özel** — state şekli veya checkpointer arka ucunda tam kontrol gerektiğinde.

## Teslim Et

`outputs/skill-state-graph.md`, checkpointing ve devam bağlı herhangi bir hedef runtime'da LangGraph şeklinde bir durum grafiği üretir.

## Alıştırmalar

1. Sınıflandırma güveni eşiğin altında olduğunda `classify`'dan `end`'e koşullu kenar ekleyin. İnsan `route`'u manuel ayarladıktan sonra çalıştırmanın devamını sağlayın.
2. SQLite benzeri sahteyi gerçek bir SQLite checkpointer'ıyla değiştirin. Adım başına serileştirme overhead'ini ölçün.
3. Paralel kenarlar uygulayın: iki düğüm eş zamanlı çalışır, özel bir reducer ile birleşir. Değişmez state burada ne kazandırır?
4. `langgraph-supervisor` referansını okuyun. Toy kodu `create_supervisor`'a taşıyın. Trace şekillerini karşılaştırın.
5. Streaming ekleyin: her düğüm çalışırken kısmi state üretsin. Delta'lar geldikçe yazdırın.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| State graph | "Agent durum makinesi" | Tipli state + düğümler + kenarlar + reducer'lar |
| Checkpointer | "Dayanıklılık arka ucu" | Her düğümden sonra state'i serileştirir; devamı sağlar |
| Reducer | "State birleştirici" | Mevcut durumu bir düğümün güncellemesiyle birleştiren fonksiyon |
| Conditional edge | "Dal" | State'in bir fonksiyonuyla seçilen kenar |
| Subgraph | "İç içe graf" | Başka bir graf içinde düğüm olarak kullanılan graf |
| Durable execution | "Hatadan devam" | Tam state ile son başarılı düğümden yeniden başlatma |
| Supervisor | "Yönlendirici LLM" | Uzman subagent'lar için merkezi yönlendirici |
| Swarm | "P2P agent'lar" | Agent'lar paylaşılan araçlarla devreder; merkezi yönlendirici yok |

## İleri Okuma

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — referans dokümanlar
- [langgraph-supervisor reference](https://reference.langchain.com/python/langgraph/supervisor/) — supervisor kalıbı API'si
- [AutoGen v0.4, Microsoft Research](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) — actor model alternatifi
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview) — oturum deposu ve subagent'lar
