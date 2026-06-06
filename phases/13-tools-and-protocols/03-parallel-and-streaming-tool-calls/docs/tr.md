# Paralel Araç Çağrıları ve Araçlarla Akış

> Üç bağımsız hava durumu sorgusu sıralı olarak çalıştırılırsa üç tur yolculuğudur. Bunları paralel çalıştırın ve toplam süre en yavaş tek çağrıya düşer. Her sınır sağlayıcı artık tek turda birden fazla araç çağrısı üretir. Ödül gerçektir; tesisat incedir. Bu ders her iki yarıyı da işler: paralel fan-out ve akışlı argüman yeniden birleştirme, id-eşleme tuzağına vurgu yaparak.

**Tür:** İnşa Et
**Diller:** Python (stdlib, iş havuzu + akış donanımı)
**Ön koşullar:** Faz 13 · 02 (function calling derinlemesine)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- `parallel_tool_calls: true`'nın neden var olduğunu ve ne zaman devre dışı bırakılacağını açıkla.
- Paralel fan-out sırasında akışlı argüman parçacıklarını doğru araç çağrısı id'siyle eşle.
- Kısmi `argüman` stringlerini erken ayrıştırma yapmadan eksiksiz JSON olarak yeniden birleştir.
- Sıralı ve paralel gecikmeyi gösteren üç şehir hava durumu karşılaştırmasını çalıştır.

## Sorun

Paralel çağrılar olmadan, "Bengaluru, Tokyo ve Zürih'te hava durumu nasıl" sorusunu yanıtlayan bir ajan şunu yapar:

```
kullanıcı -> LLM
LLM -> get_weather(Bengaluru) çağır
ana program -> çalıştırıcıyı çalıştır, sonuçla yanıt ver
LLM -> get_weather(Tokyo) çağır
ana program -> çalıştırıcıyı çalıştır, sonuçla yanıt ver
LLM -> get_weather(Zürih) çağır
ana program -> çalıştırıcıyı çalıştır, sonuçla yanıt ver
LLM -> son metin yanıtı
```

Üç LLM tur yolculuğu, her biri de çalıştırıcı gecikmesini öder. Kabaca ideal duvar saati süresinin 4 katı.

Paralel çağrılarla:

```
kullanıcı -> LLM
LLM -> get_weather(Bengaluru) çağır; get_weather(Tokyo) çağır; get_weather(Zürih) çağır
ana program -> üç çalıştırıcıyı eş zamanlı çalıştır, üç sonuçla yanıt ver
LLM -> son metin yanıtı
```

Bir LLM tur yolculuğu. Çalıştırıcı süresinin en büyüğüdür, toplamı değil. OpenAI, Anthropic ve Gemini üzerindeki üretim karşılaştırmaları, fan-out iş yüklerinde %60 ila %70 duvar saati azalması gösteriyor.

Fiyat eşleme karmaşıklığıdır. Üç çağrı sırayı bozarak tamamlandığında, sonuçlarınızın eşleşen `tool_call_id`'yi taşıması gerekir, böylece model onları hizalayabilir. Sonuçlar aktığında, çalıştırmadan önce kısmi argüman parçalarını eksiksiz JSON olarak birleştirmeniz gerekir. Gemini 3, aynı araca yapılan iki paralel çağrının ayırt edilemediği gerçek dünya sorununu çözmek için kısmen benzersiz id'ler ekledi.

## Kavram

### Paraleli etkinleştirme

- **OpenAI.** `parallel_tool_calls: true` varsayılan olarak açıktır. Sıralı için `false` ayarlayın.
- **Anthropic.** `disable_parallel_tool_use: false` ile paralel (Claude 3.5 ve üzeri varsayılan). Sıralı için `true` ayarlayın.
- **Gemini.** Her zaman paralel yetenekli; `tool_config.function_calling_config.mode = "AUTO"` modelin karar vermesine olanak tanır.

Araçlarda sıralama bağımlılıkları olduğunda, bir çağrının çıktısı diğerinin girdisini beslediğinde veya hız sınırlayıcı (rate limiter) fan-out'u işleyemediğinde paraleli devre dışı bırakın.

### ID eşleme

Modelin ürettiği her çağrının bir `id`'si vardır. Ana programın döndürdüğü her sonuç aynı id'yi içermelidir. Bunu yapmazsanız, sonuçlar belirsizleşir.

- **OpenAI.** Her tool-rol mesajında `tool_call_id`.
- **Anthropic.** Her `tool_result` bloğunda `tool_use_id`.
- **Gemini.** Her `functionResponse`'ta `id` (Gemini 3 ve üzeri; Gemini 2 aynı isimle eşleşti ve bu aynı isimli paralel çağrılar için kırıldı).

### Çağrıları eş zamanlı çalıştırma

Ana program her çağrının çalıştırıcısını kendi iş parçacığında, coroutine'inde veya uzak işçisinde çalıştırır. En basit donanım bir iş havuzu (thread pool) kullanır; üretim asyncio ile `asyncio.gather` veya yapılandırılmış eşzamanlılık kullanır. Tamamlanma sırası öngörülemezdir — id tanımlayıcıdır.

Yaygın bir hata: sonuçları tamamlanma sırası yerine çağrı listesi sırasıyla döndürmek. Bu genellikle işe yarar çünkü model yalnızca `tool_call_id`'yle ilgilenir, ancak bir sonuç düşürülür veya çoğaltılırsa, sıradışı gönderim hata ayıklamayı zorlaştırır. Eksik id'lerle tamamlanma sırasında yanıtlamayı tercih edin.

### Akışlı araç çağriları

Model akış halindeyken, `argümanlar` parçalar halinde gelir. Üç paralel çağrı için üç ayrı parçacık akışı teldede iç içe geçer. Her id için bir biriktiriciye (accumulator) ihtiyacınız vardır.

Sağlayıcıya göre şekil:

- **OpenAI.** Her parçacık `choices[0].delta.tool_calls[i].function.arguments` (kısmi string) şeklindedir. Parçacık `index` (çağrı listesindeki konum) taşır. Index başına biriktirirsiniz, `id`'yi ilk göründüğünde okursunuz ve `finish_reason = "tool_calls"` olduğunda JSON ayrıştırırsınız.
- **Anthropic.** Akış olayları `message_start`, ardından her blok için bir `content_block_start` (tip `tool_use`, id, name, boş input içerir). `content_block_delta` olayları `input_json_delta` parçacıkları taşır. `content_block_stop` her bloğu kapatır.
- **Gemini.** `streamFunctionCallArguments` (Gemini 3 ve üzeri) `functionCallId` ile parçacıklar üretir böylece çağrılar temiz şekilde iç içe geçer. Gemini 3 öncesi, akış bir seferde bir eksiksiz çağrı döndürdü.

### Kısmi JSON ve erken ayrıştırma tuzağı

`argümanlar` tamamlanmadan önce ayrıştıramazsınız. `{"city": "Beng` gibi kısmi JSON geçerlidir ve hata verir. Doğru kapı, sağlayıcının çağrı sonu sinyalidir: OpenAI'ın `finish_reason = "tool_calls"`, Anthropic'in `content_block_stop`'u veya Gemini'nin akış sonu olayı. Ancak o zaman `json.loads` deneyin. Daha robust bir yaklaşım, yapı tamamlandığında olaylar üreten artımlı bir JSON ayrıştırıcısı kullanmaktır; OpenAI'ın akış kılavuzu, canlı "düşünme" göstergesi gösteren UX için bunu önerir. Parantez sayımı (brace-counting) tamamlılık testi olarak güvenilmez (tırnak içindeki stringler veya kaçışlı içerik yanlış pozitiflere neden olur) ve yalnızca informal hata ayıklama sezgisi olarak kullanılmalıdır.

### Sıradışı tamamlanma

```
çağrı_A: hızlı API, ilk döner
çağrı_B: yavaş API, ikinci döner
çağrı_C: orta API, üçüncü döner
```

Ana program yanıtı hala id'leri belirtmelidir:

```
[{role: "tool", tool_call_id: "call_A", content: ...},
 {role: "tool", tool_call_id: "call_B", content: ...},
 {role: "tool", tool_call_id: "call_C", content: ...}]
```

OpenAI veya Anthropic'te doğruluk için yanıt sırası önemli değildir. Gemini, id'ler eşleştiği sürece herhangi bir sırayı kabul eder.

### Karşılaştırma: sıralı vs paralel

`code/main.py`'deki donanım, 400, 600 ve 800 ms gecikmeli üç çalıştırıcı simüle eder. Sıralı 1800 ms toplamda çalışır. Paralel max(400, 600, 800) = 800 ms çalışır. Fark sabittir, oransal değildir, bu yüzden tasarruf araç sayısına göre büyür.

Gerçek dünya uyarısı: paralel çağrılar aşağı akış API'lerini zorlar. Hız sınırlı bir servise 10 yollu fan-out başarısız olur. Faz 13 · 17 ağ geçidi düzeyindeki geri basıncı (backpressure) kapsar; yeniden deneme anlambilimi gelecek bir faz için planlanmıştır.

### Akışlı fan-out duvar saati

Modelin kendisi akış yapıyorsa, tüm çağrılar sonlanmadan bir çağrının argümanları tamamlandığında çalıştırmaya başlayabilirsiniz. OpenAI bunu belgeler ancak tüm SDK'lar sunmaz. Bu dersteki donanım bunu yapar: simüle edilmiş akış eksiksiz bir argüman nesnesi üretir üretmez, ana program o çağrıyı başlatır.

## Kullan

`code/main.py`'in iki yarısı vardır. İlk kısım `concurrent.futures.ThreadPoolExecutor` kullanarak üç simüle hava durumu çağrısını sıralı ve paralel çalıştırır ve duvar saati süresini yazdırır. İkinci kısım sahte bir akışlı yanıtı tekrar oynatır — bir akışta iç içe geçmiş üç paralel çağrı için `argüman` parçacıkları — ve bunları `StreamAccumulator` ile id başına yeniden birleştirir. LLM yok, ağ yok, yalnızca yeniden birleştirme mantığı.

Neye bakılmalı:

- Sıralı zamanlayıcı 1,8 saniyeye ulaşır. Paralel zamanlayıcı aynı gecikmelerle 0,8 saniyeye ulaşır.
- Biriktirici, parçacıkların sırayı bozarak gelmesini id başına tamponlayarak ve yalnızca her çağrının JSON'u tamamlandığında ayrıştırarak ele alır.
- Çalıştırıcı, bir id'nin argümanları sonlanır sonlanmaz başlar, tüm akışlar bitene kadar değil.

## Sun

Bu ders `outputs/skill-parallel-call-safety-check.md` dosyasını üretir. Bir araç kaydı verildiğinde, beceri hangi araçların paralelleştirilebilir güvenli olduğunu, hangilerinin sıralama bağımlılıklarına sahip olduğunu ve hangilerinin aşağı akış hız sınırlarını aşırı yükleyeceğini denetler — araç başına `parallel_safe` bayraklarıyla revize edilmiş bir kayıt döndürür.

## Alıştırmalar

1. `code/main.py`'i çalıştırın ve simüle edilmiş gecikmeleri değiştirin. Paralel/sıralı oranın kabaca `max/sum` olduğunu doğrulayın (gerçek çalıştırmalar iş parçacığı zamanlaması, serileştirme ve donanımoverhead'i nedeniyle idealden hafif sapar). Hangi gecikme dağılımında paralel önemini kaybeder?

2. Biriktiriciyi "çağrı akış ortasında iptal edildi" durumunu ele alacak şekilde genişletin: tamponunu bırakın ve `cancelled` bir olay üretin. Hangi sağlayıcı bu durumu açıkça belgeler? Anthropic'in `content_block_stop` anlambilimine ve OpenAI'ın `finish_reason: "length"` davranışına bakın.

3. İş havuzunu `asyncio.gather` ile değiştirin. Her ikisini de karşılaştırın. Asenkron üzerinde küçük kazanımlar görmelisiniz因为 alt bağlam değiştirme maliyeti daha düşüktür, ancak yalnızca çalıştırıcılar gerçek I/O yapıyorsa.

4. Paralelleştirilmemesi gereken iki araç seçin (ör. `create_file` ardından `write_file`). Kayda bir `ordering_dependency` grafı ekleyin ve paralel fan-out'u bu grafğa göre kontrol edin. Bu, gelecek bir ajan mühendisliği fazında resmileştirilen bağımlılık farkındalıklı zamanlama için minimum mekanizmadır.

5. OpenAI'ın paralel function calling bölümünü ve Anthropic'in `disable_parallel_tool_use` belgelerini okuyun. Anthropic'in paralelliği devre dışı bırakmayı önerdiği tek gerçek dünya araç türünü belirleyin. (İpucu: aynı kaynağa yönelik sonuçlu değişiklikler.)

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Parallel tool calls | "Bir turda fan-out" | Model tek bir asistan mesajında birden fazla araç çağrısı üretir |
| `parallel_tool_calls` | "OpenAI'ın bayrağı" | Çoklu çağrı üretimini etkinleştirir veya devre dışı bırakır |
| `disable_parallel_tool_use` | "Anthropic'in tersi" | Çıkış bayrağı; varsayılan paralel etkin |
| Tool call id | "Eşleme sapı" | Sonuç mesajının yinelemesi gereken çağrı başına tanımlayıcı |
| Accumulator | "Akış tamponu" | Kısmi `argüman` parçacıkları için id başına string tamponu |
| Out-of-order completion | "En hızlı önce" | Paralel çağrılar öngörülemez sırada tamamlanır; id'ler yapıştırıcıdır |
| Dependency graph | "Sıralama kısıtlamaları" | Çıktıları diğer araçların girdilerini besleyen araçlar; paralelleştirilemez |
| Parse-early trap | "JSON.parse patladı" | Tamamlanmamış bir `argüman` stringini ayrıştırma denemesi |
| `streamFunctionCallArguments` | "Gemini 3 özelliği" | Çağrı başına benzersiz id ile akışlı argüman parçacıkları |
| Completion-order reply | "Tümünü bekleme" | Sonuçlar geldikçe, id ile anahtarlanmış olarak yanıt verme |

## İleri Okuma

- [OpenAI — Parallel function calling](https://platform.openai.com/docs/guides/function-calling#parallel-function-calling) — varsayılan davranış ve çıkış bayrağı
- [Anthropic — Tool use: implementing tool use](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implementing-tool-use) — `disable_parallel_tool_use` ve sonuç toplu işlemleri
- [Google — Gemini function calling parallel section](https://ai.google.dev/gemini-api/docs/function-calling) — Gemini 3'ten itibaren id eşlemeli paralel çağrılar
- [OpenAI — Streaming responses with tools](https://platform.openai.com/docs/api-reference/responses-streaming) — OpenAI akışları için parçalanmış argüman yeniden birleştirme
- [Anthropic — Streaming messages](https://docs.anthropic.com/en/api/messages-streaming) — `input_json_delta` ile `content_block_delta`
