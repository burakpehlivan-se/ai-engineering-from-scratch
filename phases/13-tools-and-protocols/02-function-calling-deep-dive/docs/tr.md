# Function Calling Derinlemesine — OpenAI, Anthropic, Gemini

> Üç sınır sağlayıcı 2024'te aynı araç çağrısı döngüsünde birleşti ve ardından her şeyde ayrıldı. OpenAI `tools` ve `tool_calls` kullanır. Anthropic `tool_use` ve `tool_result` blokları kullanır. Gemini `functionDeclarations` ve benzersiz-id eşleştirmesi kullanır. Bu ders üçünü yan yana karşılaştırır, böylece bir sağlayıcıda yayınlanan kodu taşıdığınızda bozulmaz.

**Tür:** İnşa Et
**Diller:** Python (stdlib, şema dönüştürücüleri)
**Ön koşullar:** Faz 13 · 01 (araç arayüzü)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- OpenAI, Anthropic ve Gemini function-calling yükleri arasındaki üç şekil farkını (beyan, çağrı, sonuç) belirt.
- Bir araç beyanını üç sağlayıcı formatının her birine çevir ve strict mod kısıtlamalarının nerede farklılaşacağını tahmin et.
- Her sağlayıcıda `tool_choice` kullanarak araç çağrısını zorla, yasakla veya otomatik seç.
- Sağlayıcı başına sert sınırları (araç sayısı, şema derinliği, argüman uzunluğu) ve sınırlar aşıldığında her birinin ürettiği hata imzalarını bil.

## Sorun

Bir function-calling isteğinin şekli sağlayıcıya göre değişir. 2026 üretim yığınlarından üç somut örnek:

**OpenAI Chat Completions / Responses API.** `tools: [{type: "function", function: {name, description, parameters, strict}}]` geçersiniz. Modelin yanıtı `choices[0].message.tool_calls: [{id, type: "function", function: {name, arguments}}]` içerir; burada `argümanları` ayrıştırmanız gereken bir JSON stringidir. Strict mod (`strict: true`), kısıtlı kod çözmeyle şema uyumluluğunu zorlar.

**Anthropic Messages API.** `tools: [{name, description, input_schema}]` geçersiniz. Yanıt `content: [{type: "text"}, {type: "tool_use", id, name, input}]` olarak gelir. `input` zaten ayrıştırılmıştır (bir string değil, bir nesne). `{type: "tool_result", tool_use_id, content}` bloğu içeren yeni bir `user` mesajıyla yanıt verirsiniz.

**Google Gemini API.** `tools: [{functionDeclarations: [{name, description, parameters}]}]` geçersiniz ( `functionDeclarations` altında iç içe). Yanıt `candidates[0].content.parts: [{functionCall: {name, args, id}}]` olarak gelir; burada `id` Gemini 3 ve üzeri için paralel çağrı eşleştirmesinde benzersizdir. `{functionResponse: {name, id, response}}` ile yanıt verirsiniz.

Aynı döngü. Farklı alan adları, farklı iç içe geçme, farklı string/nesne kuralları, farklı eşleme mekanizmaları. Bir ekip OpenAI'da bir hava durumu ajanı yazdığında, Anthropic'e taşımak için iki gün, Gemini'ye taşımak için bir gün harcar.

Bu ders, üç formatı tek bir kanonik araç beyanına birleştiren ve kenarda yönlendiren bir çevirmen (translator) oluşturur. Faz 13 · 17 aynı patikayı bir LLM ağ geçidine (gateway) genelleştirir.

## Kavram

### Ortak yapı

Her sağlayıcı beş şeye ihtiyaç duyar:

1. **Araç listesi.** Araç başına ad, açıklama ve girdi şeması.
2. **Araç seçimi.** Belirli bir aracı zorla, araçları yasakla veya modele bırak.
3. **Çağrı üretimi.** Aracı ve argümanları belirten yapılandırılmış çıkış.
4. **Çağrı id'si.** Yanıtı doğru çağrıyla eşle (paralel için önemli).
5. **Sonuç enjeksiyonu.** Sonucu geri bağlayan bir mesaj veya blok.

### Şekil farkları, alan alanı

| Yön | OpenAI | Anthropic | Gemini |
|--------|--------|-----------|--------|
| Beyan zarfı | `{type: "function", function: {...}}` | `{name, description, input_schema}` | `{functionDeclarations: [{...}]}` |
| Şema alanı | `parameters` | `input_schema` | `parameters` |
| Yanıt konteyneri | Asistan mesajında `tool_calls[]` | `content[]` tipi `tool_use` | `parts[]` tipi `functionCall` |
| Argüman türü | string halinde JSON | ayrıştırılmış nesne | ayrıştırılmış nesne |
| ID formatı | `call_...` (OpenAI üretir) | `toolu_...` (Anthropic) | UUID (Gemini 3+) |
| Sonuç bloğu | rol `tool`, `tool_call_id` | `tool_result` ile `user`, `tool_use_id` | eşleşen `id` ile `functionResponse` |
| Aracı zorla | `tool_choice: {type: "function", function: {name}}` | `tool_choice: {type: "tool", name}` | `tool_config: {function_calling_config: {mode: "ANY"}}` |
| Araçları yasakla | `tool_choice: "none"` | `tool_choice: {type: "none"}` | `mode: "NONE"` |
| Strict şema | `strict: true` | şema-şemadır (her zaman zorlanır) | İstek düzeyinde `responseSchema` |

### Gerçekten karşılaşacağınız sınırlar

- **OpenAI.** İstek başına 128 araç. Şema derinliği 5. Argüman stringi <= 8192 byte. Strict mod, `$ref`, `oneOf`/`anyOf`/`allOf` ile örtüşme ve `required`'ta listelenmeyen özellikler gerektirmez.
- **Anthropic.** İstek başına 64 araç. Şema derinliği pratikte sınırsız ancak pratik sınır 10. Strict mod bayrağı yok; şema bir sözleşmedir ve model uyma eğilimindedir.
- **Gemini.** İstek başına 64 fonksiyon. Şema türleri OpenAPI 3.0 alt kümesidir (JSON Schema 2020-12'den hafif farklılık). Paralel çağrılar Gemini 3'ten itibaren benzersiz-id kullanır.

### `tool_choice` davranışı

Herkesin desteklediği üç mod, farklı isimlendirilmiş.

- **Auto.** Model araç veya metin seçer. Varsayılan.
- **Required / Any.** Model en az bir araç çağırmalıdır.
- **None.** Model araç çağırmamalıdır.

Artı her sağlayıcıya özgü bir mod:

- **OpenAI.** Belirli bir aracı adla zorla.
- **Anthropic.** Belirli bir aracı adla zorla; `disable_parallel_tool_use` bayrağı tekli ile çoklu'yu ayırır.
- **Gemini.** `mode: "VALIDATED"` model niyetinden bağımsız olarak her yanıtı bir şema doğrulayıcıdan geçirir.

### Paralel çağrılar

OpenAI'ın `parallel_tool_calls: true`'sı (varsayılan) bir asistan mesajında birden fazla çağrı üretir. Hepsini çalıştırır ve `tool_call_id` başına bir giriş içeren toplu bir tool-rol mesajıyla yanıt verirsiniz. Anthropic tarihsel olarak tekli çağrı yaptı; `disable_parallel_tool_use: false` (Claude 3.5'ten itibaren varsayılan) çoklu'yu etkinleştirir. Gemini 2 paralel çağrıya izin verdi ancak kararlı id'ler vermedi; Gemini 3 UUID'ler ekler böylece sıradışı yanıtlar temiz şekilde eşleşir.

### Akış (Streaming)

Üçü de akışlı araç çağrısını destekler. Tel formatı farklıdır:

- **OpenAI.** `tool_calls[i].function.arguments` delta parçacıkları (chunk) kademeli olarak gelir. `finish_reason: "tool_calls"` gelene kadar biriktirirsiniz.
- **Anthropic.** Blok başlangıcı / blok-delta / blok-durdurma olayları. `input_json_delta` parçacıkları kısmi argümanları taşır.
- **Gemini.** `streamFunctionCallArguments` (Gemini 3'te yeni), `functionCallId` ile parçacıklar üretir böylece birden fazla paralel çağrı iç içe geçebilir.

Faz 13 · 03 paralel + akış yeniden birleştirme hakkında derinlemesine bilgi verir. Bu ders beyan ve tekli çağrı şekillerine odaklanır.

### Hatalar ve onarım

Geçersiz argüman hataları da farklı görünür:

- **OpenAI (non-strict).** Model `arguments: "{kötü json}"` döndürür, JSON ayrıştırmanız başarısız olur, bir hata mesajı eklersiniz ve yeniden çağırırsınız.
- **OpenAI (strict).** Doğrulama kod çözme sırasında gerçekleşir; geçersiz JSON mümkün değildir ancak `refusal` görünebilir.
- **Anthropic.** `input` beklenmedik alanlar içerebilir; şema tavsiye niteliğindedir. Sunucu tarafında doğrulayın.
- **Gemini.** OpenAPI 3.0 tuhaflığı: nesne alanlarındaki `enum` sessizce göz ardı edilir; kendiniz doğrulayın.

### Çevirmen paterni

Kodunuzdaki kanonik araç beyanı şöyle görünür (siz şekli seçersiniz):

```python
Tool(
    name="get_weather",
    description="Kullanım zamanı ...",
    input_schema={"type": "object", "properties": {...}, "required": [...]},
    strict=True,
)
#### Açıklama
Tool sınıfı, bir aracın kanonik tanımını temsil eder. name, description, input_schema ve strict alanlarını içerir.
```

Üç küçük fonksiyon, bunu üç sağlayıcı şekline dönüştürür. `code/main.py`'deki demoyu tam olarak bunu yapar, ardından sahte bir aracı her sağlayıcının yanıt şekli aracılığıyla döngüye sokar. Ağ gerekmez — bu ders şekilleri öğretir, HTTP'yi değil.

Üretim ekipleri bu çevirmeni `AbstractToolset` (Pydantic AI), `UniversalToolNode` (LangGraph) veya `BaseTool` (LlamaIndex) içine sarar. Faz 13 · 17, herhangi birinin önüne OpenAI-şekilli bir API sunan bir ağ geçidi yayınlar.

## Kullan

`code/main.py`, bir kanonik `Tool` dataclass'ı ve OpenAI, Anthropic ve Gemini beyan JSON'larını üreten üç çevirmen tanımlar. Ardından her biçimdeki elle hazırlanmış bir sağlayıcı yanıtını aynı kanonik çağrı nesnesine ayrıştırır ve anlambilimin özünde aynı olduğunu gösterir. Çalıştırın ve üç beyanı yan yana karşılaştırın.

Neye bakılmalı:

- Üç beyan bloğu yalnızca zarf ve alan adlarında farklılık gösterir.
- Üc yanıt blokları, çağrının nerede yaşadığında farklılık gösterir (üst düzey `tool_calls`, `content[]` bloğu, `parts[]` girişi).
- Bir `canonical_call()` fonksiyonu, üç yanıt shape'inden de `{id, name, args}` çıkarır.

## Sun

Bu ders `outputs/skill-provider-portability-audit.md` dosyasını üretir. Bir sağlayıcıya karşı bir function-calling entegrasyonu verildiğinde, beceri bir taşınabilirlik denetimi üretir: hangi sağlayıcı sınırlarına güvendiğini, hangi alanların yeniden adlandırılması gerektiğini ve diğer sağlayıcılara taşındığında neyin bozulduğunu belirtir.

## Alıştırmalar

1. `code/main.py`'i çalıştırın ve üç sağlayıcı beyan JSON'unun tümünün aynı temel `Tool` nesnesini serileştirdiğini doğrulayın. Kanonik araca bir enum parametresi ekleyin ve yalnızca Gemini çevirmeninin OpenAPI tuhaflığını ele alması gerektiğini doğrulayın.

2. Her sağlayıcı için, bir `list_tools` veya keşif çağrısından sonra modelin döndürdüğü araç listesini çıkaran bir `ListToolsResponse` ayrıştırıcısı ekleyin. OpenAI'ın bunu yerel olarak yok; bu asimetriyi not edin.

3. `tool_choice` dönüşümünü uygulayın: kanonik `ToolChoice(mode="force", tool_name="x")`'i üç sağlayıcı şekline de eşleyin. Ardından `mode="any"` ve `mode="none"` eşleyin. Dersin fark tablosunu kontrol edin.

4. Üç sağlayıcıdan birini seçin ve function calling kılavuzunu baştan sona okuyun. Şema teknik dokümanında diğer ikisinin desteklemediği bir alan bulun. Adaylar: OpenAI `strict`, Anthropic `disable_parallel_tool_use`, Gemini `function_calling_config.allowed_function_names`.

5. Bir test vektörü yazın: argümanları beyan edilen şemayı ihlal eden bir araç çağrısı. Her sağlayıcının doğrulayıcısından çalıştırın (Ders 01'deki stdlib olan vekil olarak iş görür) ve hangi hataların tetiklendiğini kaydedin. Üretimde katılık için hangi sağlayıcıyı kullanacağınızı belgeleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Function calling | "Araç kullanımı" | Yapılandırılmış araç çağrısı üretimi için sağlayıcı düzeyinde API |
| Tool declaration (Araç beyanı) | "Araç teknik dokümanı" | Ad + açıklama + JSON Schema girdi yükü |
| `tool_choice` | "Zorla / yasakla" | auto / required / none / specific-name modları |
| Strict mode | "Şema zorlaması" | Şemaya uyması için kod çözmeyi kısıtlayan OpenAI bayrağı |
| `tool_use` bloğu | "Anthropic'in çağrı şekli" | id, name, input içeren satır içi içerik bloğu |
| `functionCall` kısmı | "Gemini'nin çağrı şekli" | name, args ve id içeren bir `parts[]` girişi |
| Arguments-as-string | "String halinde JSON" | OpenAI, argümanları bir nesne yerine JSON stringi olarak döndürür |
| Parallel tool calls | "Bir turda fan-out" | Bir asistan mesajında birden fazla araç çağrısı |
| Refusal | "Model reddediyor" | Strict modda çağrı yerine red bloğu |
| OpenAPI 3.0 subset | "Gemini şema tuhaflığı" | Gemini, JSON Schema'ya benzer ama küçük farklılıklara sahip bir diyalekt kullanır |

## İleri Okuma

- [OpenAI — Function calling guide](https://platform.openai.com/docs/guides/function-calling) — strict mod ve paralel çağrılar dahil kanonik referans
- [Anthropic — Tool use overview](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview) — `tool_use` ve `tool_result` blok anlambilimi
- [Google — Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling) — paralel çağrılar, benzersiz id'ler ve OpenAPI alt kümesi
- [Vertex AI — Function calling reference](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling) — Gemini'nin kurumsal yüzeyi
- [OpenAI — Structured outputs](https://platform.openai.com/docs/guides/structured-outputs) — strict mod şema zorlama detayları
