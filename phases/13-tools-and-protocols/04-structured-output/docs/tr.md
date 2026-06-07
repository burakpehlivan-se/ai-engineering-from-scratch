# Yapılandırılmış Çıkış — JSON Schema, Pydantic, Zod, Kısıtlı Kod Çözme

> "Modele nazikçe JSON döndürmesini söylemek" sınır modellerde bile %5 ila %15 oranında başarısız olur. Yapılandırılmış çıkışlar (structured outputs) bu boşluğu kısıtlı kod çözmeyle kapatır: modelin şemayı ihlal edecek bir token üretmesi kelimenin tam anlamıyla engellenir. OpenAI'ın strict modu, Anthropic'in şema tipli araç kullanımı, Gemini'nin `responseSchema`'sı, Pydantic AI'ın `output_type`'ı ve Zod'ın `.parse`'ı aynı fikrin beş yüzey shape'idir. Bu ders, öğrenenlerin her üretim çıkarma hattında kullanacağı şema doğrulayıcısını ve strict mod sözleşmesini oluşturur.

**Tür:** İnşa Et
**Diller:** Python (stdlib, JSON Schema 2020-12 alt kümesi)
**Ön koşullar:** Faz 13 · 02 (function calling derinlemesine)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Doğru kısıtlamaları (enum, min/max, required, pattern) kullanarak bir çıkarma hedefi için JSON Schema 2020-12 yaz.
- Strict modun ve kısıtlı kod çözmenin neden "üretimden sonra doğrulama"dan farklı garantiler verdiğini açıkla.
- Üç hata modunu ayırt et: ayrıştırma hatası, şema ihlali, model reti.
- Tipli onarım ve tipli ret işleyicili bir çıkarma hattı sun.

## Sorun

Bir satınalma siparişi e-postasını okuyan bir ajanın serbest metni `{customer, line_items, total_usd}`'ye dönüştürmesi gerekir. Üç yaklaşım.

**Yaklaşım bir: JSON iste.** "JSON ile yanıt ver, customer, line_items, total_usd alanlarını içer." Sınır modellerde %85 ila %95 çalışır. Altı şekilde başarısız olur: eksik parantez, virgül sonrası, yanlış türler, uydurulmuş alanlar, token limitinde kesilme, "Here is your JSON:" gibi sızıntı metni.

**Yaklaşık iki: Üretimden sonra doğrula.** Serbest üret, ayrıştır, şemaya göre doğrula, başarısız olursa yeniden dene. Güvenilir ama pahalı — her yeniden deneme için ödeme yaparsınız ve kesme hataları her oluşumda ekstra bir tur harcar.

**Yaklaşım üç: Kısıtlı kod çözme.** Sağlayıcı, kod çözme sırasında şemayı zorlar. Geçersiz token'lar örnekleme dağılımından maskelenir. Çıktının ayrıştırılması ve doğrulanması garanti edilir. Hata bir moda düşer: ret (model girdinin şemaya uymadığına karar verir).

2026'daki her sınır sağlayıcı, üçüncü yaklaşıma ilişkin bir形式 yayınlar.

- **OpenAI.** `response_format: {type: "json_schema", strict: true}` artı model reddederse yanıtta `refusal`.
- **Anthropic.** `tool_use` girdilerinde şema zorlaması; `stop_reason: "refusal"` bir şey değil, ancak araç çağrısı olmadan `end_turn` sinyalidir.
- **Gemini.** İstek düzeyinde `responseSchema`; 2026'da Gemini seçili türler için token düzeyinde dilbilgisi kısıtlamaları yayınlar.
- **Pydantic AI.** `output_type=InvoiceModel`, `InvoiceModel`'e tipli bir `RunResult` üretir.
- **Zod (TypeScript).** Sağlayıcı çıktısını bir Zod şemasına göre doğrulayan çalışma zamanı ayrıştırıcısı; OpenAI'ın `beta.chat.completions.parse`'u ile eşlenir.

Ortak iplik: şemayı bir kez beyan et, uçtan uca zorla.

## Kavram

### JSON Schema 2020-12 — ortak dil

Her sağlayıcı JSON Schema 2020-12'yi kabul eder. En çok kullandığınız yapılar:

- `type`: `object`, `array`, `string`, `number`, `integer`, `boolean`, `null`'dan biri.
- `properties`: alan adından alt şemaya eşleme.
- `required`: görünmesi gereken alan adlarının listesi.
- `enum`: izin verilen değerlerin kapalı kümesi.
- `minimum` / `maximum` (sayılar), `minLength` / `maxLength` / `pattern` (stringler).
- `items`: her dizi elemanına uygulanan alt şema.
- `additionalProperties`: `false` ek alanları yasaklar (varsayılan moda göre değişir).

OpenAI strict modu üç ek gereklilik ekler: her özelliğin `required`'ta listelenmesi, her yerde `additionalProperties: false` ve çözümlenmemiş `$ref` olmaması. Bunu yıkarsanız, API istek zamanında 400 döndürür.

### Pydantic, Python bağlaması

Pydantic v2, `model_json_schema()` aracılığıyla dataclass benzeri modellerden JSON Schema üretir. Pydantic AI bunu sarar, böylece şunu yazarsınız:

```python
class Invoice(BaseModel):
 customer: str
 line_items: list[LineItem]
 total_usd: Decimal
#### Açıklama
Pydantic BaseModel sınıfı, Python'da JSON Schema üreten tipli veri modelleri tanımlar.
```

ve ajan çerçevesi şemayı kenarda OpenAI strict moduna, Anthropic `input_schema`'sına veya Gemini `responseSchema`'sına dönüştürür. Modelin çıktısı tipli bir `Invoice` örneği olarak geri gelir. Doğrulama hataları tipli hata yollarıyla `ValidationError` fırlatır.

### Zod, TypeScript bağlaması

Zod (`z.object({customer: z.string(), ...})`), TS karşılığıdır. OpenAI'ın Node SDK'sı `zodResponseFormat(Invoice)`'ı sunar, bu API'nin JSON Schema yüküne dönüştürülür.

### Redler (Refusals)

Strict mod, modeli yanıtlamaya zorlayamaz. Giriş şemaya uymuyorsa ("e-posta bir şiirdi, fatura değildi"), model内因ını içeren bir `refusal` alanı üretir. Kodunuz bunu bir birincil sonuç olarak işlemeli, bir hata olarak değil. Red aynı zamanda bir güvenlik sinyali olarak kullanışlıdır: korumalı içerikli bir e-postadan kredi kartı numarası çıkarması istenen bir model, güvenlik nedeni eklenmiş bir red döndürür.

### Açık kaynakta kısıtlı kod çözme

Açık ağırlıklı (open-weights) uygulamalar üç teknik kullanır.

1. **Dilbilgisine dayalı kod çözme** (`outlines`, `guidance`, `lm-format-enforcer`): şemadan belirli sonlu otomatik (FSM) inşa edin; her adımda, FSM'i ihlal edecek token'ların logitlerini maskelen.
2. **JSON ayrıştırıcıyla logit maskeleme**: modelle senkronize çalışan bir akışlı JSON ayrıştırıcı çalıştırın; her adımda geçerli bir sonraki token kümesini hesaplayın.
3. **Doğrulayıcıyla spekülatif kod çözme**: ucuz taslak model token önerir, doğrulayıcı şemayı zorlar.

Ticari sağlayıcılar bunlardan birini perde arkasında seçer. 2026 teknoloji durumu, kısa yapılandırılmış çıkışlar için düz üretime göre daha hızlı ve uzun olanlar için kabaca aynı hızdadır.

### Üç hata modu

1. **Ayrıştırma hatası.** Çıktı geçerli JSON değil. Strict mod altında mümkün değil. Strict olmayan sağlayıcılarda hala olabilir.
2. **Şema ihlali.** Çıktı ayrıştırılıyor ancak şemayı ihlal ediyor. Strict mod altında mümkün değil. Dışında yaygın.
3. **Ret.** Model reddediyor. Tipli bir sonuç olarak ele alınmalıdır.

### Yeniden deneme stratejisi

Strict modun dışındayken (Anthropic araç kullanımı, non-strict OpenAI, eski Gemini), kurtarma paterni:

```
üret -> ayrıştır -> doğrula -> başarısız olursa, hata ekle ve yeniden dene, max 3x
```

Bir yeniden deneme genellikle yeterlidir. Üç yeniden deneme zayıf model dalgalanmalarını yakalar. Üçün ötesi kötü bir şemanın işaretidir: model bazı girdiler için bunu karşılayamaz ve prompt veya şemanın düzeltilmesi gerekir.

### Küçük model desteği

Kısıtlı kod çözme küçük modellerde çalışır. Dilbilgisi zorlamalı 3B parametreli açık kaynak model, ham kullanımlı 70B parametreli modeli yapılandırılmış görevlerde geçer. Bu, yapılandırılmış çıkışların üretim için neden önemli olduğunun ana nedenidir: güvenilirliği model boyutundan ayırır.

## Kullan

`code/main.py`, stdlib'da minimal bir JSON Schema 2020-12 doğrulayıcısı sunar (türler, required, enum, min/max, pattern, items, additionalProperties). Bir `Invoice` şemasını sarar ve sahte bir LLM çıktısını doğrulayıcıdan çalıştırarak ayrıştırma hatası, şema ihlali ve red yollarını gösterir. Sahte çıktıyı üretimde herhangi bir sağlayıcının gerçek yanıtıyla değiştirin.

Neye bakılmalı:

- Doğrulayıcı, yol ve mesaj içeren tipli bir `[ValidationError]` listesi döndürür. Bu, yeniden deneme prompt'una yüzey çıkarmak istediğiniz shape'dir.
- Red dalı yeniden deneme YAPMAZ. Günlükler ve tipli bir red döndürür. Faz 14 · 09 redleri bir güvenlik sinyali olarak kullanır.
- `additionalProperties: false` kontrolü düşmanca test girdisinde tetiklenir, bu yüzden strict modun uydurulmuş alanlara neden kapı kapattığını gösterir.

## Sun

Bu ders `outputs/skill-structured-output-designer.md` dosyasını üretir. Serbest metin çıkarma hedefi (faturalar, destek talepleri, özgeçmişler vb.) verildiğinde, beceri strict mod uyumlu bir JSON Schema 2020-12 ve onu yansıtan bir Pydantic modeli üretir; tipli ret ve yeniden deneme işleyicisi taslak olarak yer alır.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. `total_usd`'nin negatif sayı olduğu dördüncü bir test vakası ekleyin. Doğrulayıcının `minimum` kısıt yoluyla bunu reddettiğini doğrulayın.

2. Ayırt edici (discriminator) ile `oneOf` desteği ekleyin. Yaygın durum: `line_item` bir ürün veya hizmettir, `kind` ile etiketlenir. Strict modda burada ince kurallar vardır; OpenAI'ın yapılandırılmış çıkışlar kılavuzuna bakın.

3. Aynı Invoice şemasını bir Pydantic BaseModel olarak yazın ve `model_json_schema()` çıktısını el yapımı şemanızla karşılaştırın. Pydantic'in varsayılan olarak ayarladığı ancak el yapımı versiyonun atladığı tek alanı belirleyin.

4. Red oranlarını ölçün. Çıkarılamayacak on girdi oluşturun (bir şarkı sözü, bir matematik kanıtı, boş bir e-posta) ve bunları strict modda gerçek bir sağlayıcıdan çalıştırın. Red sayısını vs uydurulmuş çıktıları sayın. Bu, red farkındalıklı yeniden denemeler için temel gerçektir.

5. OpenAI'ın yapılandırılmış çıkışlar kılavuzunu baştan sona okuyun. Strict modda açıkça yasakladığı ancak düz JSON Schema'nın izin verdiği tek yapıyı belirleyin. Ardından yasak yapıyı özünde kullanmayan bir şema tasarlayın ve strict uyumlu olacak şekilde yeniden düzenleyin.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| JSON Schema 2020-12 | "Şema teknik dokümanı" | Her modern sağlayıcının konuştuğu IETF taslak şema diyalekti |
| Strict mode | "Garantili şema" | Kısıtlı kod çözmeyle şemayı zorlayan OpenAI bayrağı |
| Constrained decoding | "Logit maskeleme" | Kod çözme sırasında geçersiz sonraki token'ları maskeleme |
| Refusal | "Model reddediyor" | Girişin şemaya uymadığı tipli sonuç |
| Parse error | "Geçersiz JSON" | Çıktı JSON olarak ayrıştırılamadı; strict altında imkansız |
| Schema violation | "Yanlış şekil" | Ayrıştırıldı ancak türleri / required'ı / enum'u / aralığı ihlal etti |
| `additionalProperties: false` | "Ek izin verilmez" | Bilinmeyen alanları yasaklar; OpenAI strict'te gerekli |
| Pydantic BaseModel | "Tipli çıkış" | JSON Schema üreten ve doğrulayan Python sınıfı |
| Zod schema | "TypeScript çıkış türü" | Sağlayıcı çıktısı doğrulaması için TS çalışma zamanı şeması |
| Grammar enforcement | "Açık ağırlıklı kısıtlı kod çözme" | outlines / guidance'daki FSM tabanlı logit maskeleme |

## İleri Okuma

- [OpenAI — Structured outputs](https://platform.openai.com/docs/guides/structured-outputs) — strict mod, retler ve şema gereklilikleri
- [OpenAI — Introducing structured outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) — Ağustos 2024 lansman yazısı, kod çözme garantisi açıklaması
- [Pydantic AI — Output](https://ai.pydantic.dev/output/) — her sağlayıcıya serileştirilen tipli output_type bağlamaları
- [JSON Schema — 2020-12 release notes](https://json-schema.org/draft/2020-12/release-notes) — kanonik teknik doküman
- [Microsoft — Structured outputs in Azure OpenAI](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs) — kurumsal dağıtım notları ve strict mod uyarıları
