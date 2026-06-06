# İstem Önbellekleme ve Semantik Önbellekleme Ekonomisi

> **Fiyatlandırma anlık görüntüsü 2026-04 tarihli.** Aşağıdaki sayısal iddialar, bu dersin yayınlanmasında yakalanan satıcı fiyat kartlarını yansıtır; aşağı akış alıntılamadan önce bağlantılı dokümanlara karşı doğrulayın.

> Önbellekleme iki katmanda olur. L2 (sağlayıcı-düzeyi) istem/önek önbellekleme, tekrarlanan önekler için attention KV'yi yeniden kullanır — Anthropic'in istem-önbellekleme dokümanları uzun istemlerde %90'a kadar maliyet azalması ve %85 gecikme azalması reklamını yapar; Claude 3.5 Sonnet için önbellek okumaları taze ile 0,30$/M vs 3,00$/M, 5 dakikalık TTL ve 1-saatlik TTL seçeneği için 2x yazma primi (docs.anthropic.com, 2026-04). OpenAI istem önbellekleme, ≥1024 token istemler için otomatik olarak uygulanır ve önbellekten girişi taze ile kabaca %90 indirimle fiyatlandırır (platform.openai.com, 2026-04); modele-göre tam önbellek oranı canlı fiyat kartına bağlıdır. L1 (uygulama-düzeyi) semantik önbellekleme, gömme benzerliği isabetlerinde LLM'i tamamen atlar. Satıcı "%95 doğruluk" ifadesi eşleşme doğruluğunu ifade eder, isabet oranını değil — rapor edilen üretim isabet oranları %10 (açık-uçlu sohbet) ile %70 (yapılandırılmış SSS) arasında değişir; iki sağlayıcı da resmi bir taban çizgisi yayınlamaz, bu nedenle bunları garanti yerine topluluk telemetrisi olarak ele alın. Üretim tuzakları: paralelleştirme önbelleği öldürür (ilk önbellek yazımından önce verilen N paralel istek harcamayı birkaç kat şişirebilir) ve önek içindeki dinamik içerik önbellek isabetlerini tamamen engeller. ProjectDiscovery, dinamik metni önbelleklenebilir önekten çıkararak %7'den %74 isabet oranına geçtiğini bildirdi (2025-11).

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak iki-katmanlı önbellek simülatörü)
**Önkoşullar:** Faz 17 · 04 (vLLM Serving Internals), Faz 17 · 06 (SGLang RadixAttention)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- L2 istem/önek önbelleklemeyi (sağlayıcıda KV yeniden kullanımı) L1 semantik önbelleklemeden (benzer istemlerde LLM atlama) ayırt edin.
- Anthropic'in `cache_control` açık işaretlemesini ve fiyat çarpanlarıyla iki TTL seçeneğini (5-dk vs 1-saat) açıklayın.
- İsabet oranı, istem/yanıt karışımı ve token fiyatları verildiğinde beklenen aylık tasarrufu hesaplayın.
- Faturaları 5-10x şişiren paralelleştirme anti-örüntüsünü ve isabet oranını çökerten dinamik-içerik anti-örüntüsünü adlandırın.

## Sorun

RAG servisinize istem önbellekleme eklersiniz. Fatura düz kalır. İsabet oranını ölçersiniz; %7. İstemleriniz statik görünüyor, ancak değil — sistem istemi, dakikaya kadar biçimlendirilmiş geçerli tarihi, bir istek kimliğini ve çeşitlilik için rastgele bir örnek yeniden sıralamayı içerir. Her istek yeni bir önbellek girdisi yazar, sıfır okur.

Ayrı olarak, agent'ınız kullanıcı sorusu başına on paralel araç çağrısı çalıştırır. Onu da sağlayıcı, ilk önbellek yazımı tamamlanmadan önce görür. On yazma, sıfır okuma. Faturanız "önbellekleme ile" olması gerekenden 5-10x.

Önbellekleme bir bayrak değil, bir protokoldür. İki katman, iki farklı hata modu.

## Kavram

### L2 — sağlayıcı istem/önek önbellekleme

Sağlayıcı, önbelleklenebilir bir önek için attention KV'yi saklar ve öneki eşleşen bir sonraki istekte onu yeniden kullanır. Yazma maliyetini bir kez ödersiniz, okumalar neredeyse bedava.

**Anthropic (Claude 3.5 / 3.7 / 4 serisi)**: istekte açık `cache_control` işaretçisi. Hangi blokların önbelleklenebilir olduğunu etiketlersiniz. TTL: 5 dakika (yazma maliyetleri 1,25x taban) veya 1 saat (yazma maliyetleri 2x taban). Önbellek okumaları: Claude 3.5 Sonnet'te taze ile 0,30$/M vs 3,00$/M — 10x daha ucuz (docs.anthropic.com, 2026-04 itibarıyla). Oranlar modele göre farklılık gösterir (Opus/Haiku ayrı yayınlanır); her zaman canlı fiyatlandırma sayfasını çapraz-kontrol edin.

**OpenAI**: ≥1024 token istemler için otomatik önbellekleme (platform.openai.com, 2026-04). Açık bayrak yok. Önbellekten giriş, mevcut gpt-4o/gpt-5 fiyat kartlarında kabaca 10x daha ucuz. Dokümanlar veya sürüm notları resmi bir isabet oranı taban çizgisi yayınlamaz; topluluk raporları dikkatli istem tasarımıyla %30-60 çevresinde kümelenir. Kendi oranınızı ölçmek için `usage.cached_tokens`'ı izleyin.

**Google (Gemini)**: açık API aracılığıyla bağlam önbellekleme; 1M-token bağlamı önbelleklemeyi daha da kârlı kılar.

**Self-hosted (vLLM, SGLang)**: Faz 17 · 06, RadixAttention'ı kapsar — kendi hesaplamanızda aynı örüntü.

### L1 — uygulama-düzeyi semantik önbellekleme

LLM'i hiç çağırmadan önce, istemi hash'leyin, gömün ve benzer bir önbelleklenmiş istek arayın (tipik olarak 0,95+ kosinüs benzerliği). İsabet'te, önbelleklenmiş yanıtı döndürün. Kaçırmada, LLM'i çağırın ve sonucu önbelleğe alın.

Açık kaynak: Redis Vector Similarity, GPTCache, Qdrant. Ticari: Portkey Cache, Helicone Cache.

Satıcı doğruluk iddiaları, döndürülen önbelleklenmiş yanıtın ne sıklıkta semantik olarak uygun olduğunu ifade eder — ne sıklıkta isabet ettiğinizi değil. Üretim isabet oranları:

- Açık-uçlu sohbet: %10-15.
- Yapılandırılmış SSS / destek: %40-70.
- Kod soruları: %20-30 (küçük varyantlar isabetleri öldürür).
- İstemleri tekrarlayan sesli agent'lar: %50-80 (ses normalleştirme sabit kümesi).

### Paralelleştirme anti-örüntüsü

Agent'ınız paralel olarak 10 araç çağrısı yapar. 10'unun da aynı 4K-token sistem istemi var. Anthropic önbellek yazımları istek başınadır; sağlayıcı istemi gördükten yaklaşık 300 ms sonra ilk önbellek-yazımı tamamlanır. İstekler 2-10 aynı milisaniye penceresinde gelir ve her biri önbellek kaçırması görür. 10 yazma primi ödersiniz, 0 okuma indirimi.

Düzeltme: sıralı-ilk ile toplu işleyin — istek 1'i yalnız yapın, sonra 1'in önbelleği yerleştiğinde 2-10'u tetikleyin. İlk araç çağrısına 300 ms ekler; faturanın 5-10x'ini tasarruf eder.

### Dinamik içerik anti-örüntüsü

Sistem isteminiz şöyle görünür:

```
You are a helpful assistant. The current time is 14:32:17.
User ID: abc123. Today is Tuesday...
```

Her istek benzersiz. Her istek yazar. Sıfır isabet.

Düzeltme: gerçekten statik olan her şeyi önbelleklenebilir öneke taşıyın; dinamik içeriği önbellek sınırının sonuna ekleyin:

```
[cacheable]
You are a helpful assistant. [rules, examples, instructions]
[/cacheable]
[dynamic, not cached]
Current time: 14:32:17. User: abc123.
```

#### Açıklama

Bu örnek, önbelleklenebilir ve dinamik içeriği nasıl ayıracağınızı gösterir. `[cacheable]` bloğu her istekte aynıdır ve sağlayıcının KV cache'inde paylaşılabilir; `[dynamic, not cached]` bloğu istek başına değişir ve önbellek anahtarını kirletmemek için dışarıda bırakılır. Bu ayrım, statik sistem talimatlarının tüm istekler arasında yeniden kullanılmasını sağlar.

ProjectDiscovery bu şekilde %7'den %74 önbellek isabet oranına geçti ve anatomiyi yayınladı.

### Gece iş yükleri için batch + önbellek yığını

Batch API'leri (Faz 17 · 15) 24 saatlik dönüşle %50 indirim verir. Üzerine önbellekten giriş, kabaca onun üzerine ~10x alır. Gece sınıflandırma, etiketleme ve rapor oluşturma iş yükleri, yığarak senkron-önbelleksiz maliyetin ~%10'una düşebilir.

### Hatırlamanız gereken sayılar

Fiyatlandırma noktaları 2026-04'te bağlantılı satıcı dokümanlarından yakalanır ve birkaç ayda bir kayar — güvenmeden önce yeniden kontrol edin.

- Anthropic önbellek okuma: Claude 3.5 Sonnet'te 0,30$/M, taze girişten kabaca 10x daha ucuz (docs.anthropic.com).
- Anthropic önbellek yazma primi: 1,25x (5-dk TTL) veya 2x (1-saat TTL).
- OpenAI otomatik-önbellek: ≥1024 token istemler için uygulanır; önbellekten giriş mevcut fiyat kartlarında taze girişin kabaca %10'u olarak fiyatlandırılır (platform.openai.com).
- Semantik önbellek isabet oranı (topluluk-bildirimi): açık sohbette ~%10; yapılandırılmış SSS'de ~%70'ye kadar. Satıcı-belgelenmiş taban çizgisi değil.
- ProjectDiscovery: önekten dinamik çıkararak %7 → %74 isabet oranı (proje blogu, 2025-11).
- Paralelleştirme anti-örüntüsü: N paralel istek ilk önbellek yazımını kaçırdığında tipik 5-10x fatura şişmesi raporları.

## Kullan

`code/main.py`, karışık iş yüklerinde L1 + L2 önbelleklemeyi simüle eder. İsabet oranlarını, faturayı raporlar ve paralelleştirme cezasını gösterir.

## Üret

Bu ders `outputs/skill-cache-auditor.md` üretir. İstem şablonu ve trafik verildiğinde, önbelleklenebilirliği denetler ve yeniden yapılandırma önerir.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Paralelleştirme bayrağını açıp kapatın. Fatura ne kadar değişir?
2. Sistem isteminizin bir tarihi var. Onu çıkarın. Önce/sonra isabet oranı matematiğini gösterin.
3. İstek geliş oranınız verildiğinde, 1-saatlik TTL (2x yazma) vs 5-dakikalık TTL (1,25x yazma) için başabaş hesaplayın.
4. 0,95 eşiğinde semantik önbellek %20 isabet ediyor. 0,85'te %50 isabet ediyor, ancak yanlış önbelleklenmiş yanıtlar görüyorsunuz. Doğru eşiği seçin ve gerekçelendirin.
5. Kullanıcı sorusu başına 10 paralel alt sorgu topluyorsunuz. Uçtan-uca gecikme eklemeden önbellek-dostu olacak şekilde yeniden yazın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| L2 istem önbelleği | "önek önbelleği" | Sağlayıcı tekrarlanan önek için KV saklar |
| `cache_control` | "Anthropic önbellek işaretçisi" | Önbelleklenebilir blokları işaretleyen açık öznitelik |
| Önbellek yazma primi | "yazma vergisi" | İlk kaçırmadan-önbelleğe ekstra maliyet (1,25x veya 2x) |
| L1 semantik önbellek | "gömme önbelleği" | LLM'i çağırmadan önce uygulama-düzeyi hash-ve-göm |
| GPTCache | "LLM önbellekleme kütüphanesi" | Popüler OSS L1 önbellek kütüphanesi |
| Önbellek isabet oranı | "isabetler / toplam" | Önbellekten sunulan isteklerin kesri |
| Paralelleştirme anti-örüntüsü | "N-yazma tuzağı" | N paralel istek önbelleği N kez kaçırır |
| Dinamik içerik tuzağı | "zamanda-isteme tuzağı" | Önekteki dinamik byte'lar isabet oranını öldürür |
| RadixAttention | "replika-içi önbellek" | SGLang'in önek-önbellek uygulaması |

## İleri Okuma

- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — resmi `cache_control` semantiği ve TTL'ler.
- [OpenAI Prompt Caching](https://platform.openai.com/docs/guides/prompt-caching) — otomatik önbellekleme davranışı ve uygunluk.
- [TianPan — Semantic Caching for LLMs Production](https://tianpan.co/blog/2026-04-10-semantic-caching-llm-production)
- [ProjectDiscovery — Cut LLM Costs 59% With Prompt Caching](https://projectdiscovery.io/blog/how-we-cut-llm-cost-with-prompt-caching)
- [DigitalOcean / Anthropic — Prompt Caching](https://www.digitalocean.com/blog/prompt-caching-with-digital-ocean)
