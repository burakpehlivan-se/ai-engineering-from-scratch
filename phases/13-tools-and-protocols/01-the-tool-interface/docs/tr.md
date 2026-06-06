# Araç Arayüzü — Ajanlar Neden Yapılandırılmış G/Ç'ye İhtiyaç Duyar

> Bir dil modeli token üretir. Bir program eylemler gerçekleştirir. Bu ikisi arasındaki boşluk, modelin bir eylem istemesine ve ana programın bunu çalıştırmasına olanak tanıyan sözleşme olan araç arayüzüdür (tool interface). 2026'daki her yığın — OpenAI, Anthropic ve Gemini üzerindeki function calling; MCP'nin `tools/call`; A2A'nın task parts — aynı döngü adımı döngüsünün farklı bir kodlamasıdır. Bu ders, döngüyü isimlendirir ve çalıştırmak için gereken minimum mekanizmayı gösterir.

**Tür:** Öğren
**Diller:** Python (stdlib, LLM yok)
**Ön koşullar:** Faz 11 (LLM completion API'leri)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Yalnızca metin üretebilen bir LLM'in neden kendi başına gerçek dünyada eylem gerçekleştiremeyeceğini açıkla.
- Dört adımlı araç çağrısı döngüsünü (açıkla → karar ver → çalıştır → gözlemle) çiz ve her adımı kimin sahiplendiğini belirt.
- Bir araç tanımını üç parça olarak yaz: ad, JSON Schema girdisi ve deterministik bir çalıştırıcı fonksiyonu.
- Saf ve yan etkili araçları (pure vs consequential) ayırt et ve bu ayrımın neden güvenlik için önemli olduğunu belirt.

## Sorun

Bir LLM, bir sonraki token üzerinde olasılık dağılımı üretir. Tüm çıkış yüzeyi budur. Bir sohbet modeline "Şu anda Bengaluru'da hava durumu nasıl?" diye sorarsanız, makul bir cümle yazabilir, ancak bir hava durumu API'sini arayamaz. Cümle tesadüfen doğru olabilir veya üç gün önceki bilgiyi içerebilir.

Bu boşluğu kapatmak, araç arayüzünün amacıdır. Ana program — ajan çalışma zamanınız, Claude Desktop, ChatGPT, Cursor veya özel bir betik — modele çağrılabilir bir araç listesi sunar. Model, bir eyleme ihtiyaç olduğuna karar verdiğinde, bir aracı ve argümanlarını belirten yapılandırılmış bir yük (payload) üretir. Ana program bu yükü ayrıştırır, aracı gerçekten çalıştırır ve sonucu geri besler. Model daha fazla çağrı gerekmediğine karar verene kadar döngü devam eder.

Bu sözleşmenin ilk versiyonu, Haziran 2023'te OpenAI'ın "functions" parametresi olarak yayınlandı. Anthropic, Claude 2.1'de `tool_use` bloklarıyla takip etti. Gemini birkaç ay sonra `functionDeclarations` ekledi. Her sağlayıcı artık aynı şekli sunuyor: JSON-Schema tipli bir araç listesi giriş, JSON yüklü bir araç çağrısı çıkışı. Model Bağlam Protokolü (Model Context Protocol, Kasım 2024), sözleşmeyi genelleştirdi böylece bir araç kaydı her modeli sunabildi. A2A (Nisan 2026, v1.0), ajanlar arası yetkilendirme için aynı ilkeyi katmanladı.

Dört adımlı döngü, bunların altındaki değişmezdir (invariant). Faz 13'teki her şey bir ayrıntılandırmadır.

## Kavram

### Adım bir: açıkla

Ana program her aracı üç alanla beyan eder.

- **Ad.** Kararlı, makine-okunabilir bir tanımlayıcı. `get_weather`, "hava durumu şeyi" değil.
- **Açıklama.** Bir paragraflık doğal dil özeti. "Kullanıcı belirli bir şehirdeki mevcut koşullar hakkında sorduğunda kullanın. Tarihsel veriler için kullanmayın."
- **Girdi şeması.** Aracın argümanlarını tanımlayan bir JSON Schema nesnesi (taslak 2020-12).

Model listayı alır. Modern sağlayıcılar bu beyanları sağlayıcıya özgü bir şablon kullanarak system prompt'a dönüştürür, böylece çağıran olarak yalnızca yapılandırılmış formla ilgilenirsiniz.

### Adım iki: karar ver

Kullanıcının mesajı ve mevcut araçlar göz önüne alındığında, model üç davranıştan birini seçer.

1. **Doğrudan yanıt ver.** Metin olarak. Araç çağrısı yok.
2. **Bir veya daha fazla aracı çağır.** Yapılandırılmış çağrı nesneleri üretir. `parallel_tool_calls: true` altında (OpenAI ve Gemini'de varsayılan, Anthropic'te isteğe bağlı) model bir turda birden fazla çağrı üretebilir.
3. **Reddet.** Strict modlu yapılandırılmış çıkışlar, çağrı yerine tipli bir `refusal` bloğu üretebilir.

Bir araç çağrısı yükünde üç kararlı alan vardır: bir çağrı `id`'si, bir araç `adı` ve bir JSON `argümanları` nesnesi. ID, ana programın sonraki sonucu belirli bir çağrıyla eşleştirebilmesi için vardır; bu, paralel çağrilar sırayı bozarak döndüğünde önemlidir.

### Adım üç: çalıştır

Ana program çağrıyı alır, argümanları beyan edilen şemaya göre doğrular ve çalıştırıcıyı (executor) çalıştırır. Geçersiz argümanlar, modelin bir alanı uydurduğunu (hallucinate) veya yanlış türü kullandığını gösterir — bu, zayıf modellerde çok yaygın bir hata modudur. Üretimdeki ana programlar geçersiz argümanlarda üç şeyden birini yapar: hata verir ve modele hatayı iletir, kısıtlı bir ayrıştırıcıyla JSON'u onar veya doğrulama hatasını prompt'a ekleyerek modeli yeniden dener.

Çalıştırıcı kendi başına sıradan bir koddur. Python, TypeScript, bir kabuk komutu, bir veritabanı sorgusu. Bir sonuç üretir; bu genellikle bir stringdir ancak herhangi bir JSON değeri veya yapılandırılmış bir içerik bloğu (MCP'ta metin, görsel veya kaynak referansı) olabilir. Sonuç seri hale getirilebilir olmalıdır.

### Adım dört: gözlemle

Ana program araç sonucunu konuşmaya ekler (`id` ile eşleşen bir `tool` rol mesajı olarak) ve modeli yeniden çağırır. Model artık araç çıkışını bağlamda görür ve son bir yanıt üretebilir veya daha fazla çağrı isteyebilir. Model çağrileri üretmeyi bırakana veya ana program iterasyon sayısında bir güvenlik sınırına ulaşana kadar devam eder.

### Güven bölünmesi

Araçlar güvenlik için önemli olan iki türde gelir.

- **Saf (Pure).** Salt okunur, deterministik, yan etki yok. `get_weather`, `search_docs`, `get_current_time`. Spekülatif olarak çağırmak güvenlidir.
- **Sonuçlu (Consequential).** Durumu değiştirir, para harcar, kullanıcı verilerine dokunur. `send_email`, `delete_file`, `execute_trade`. Kontrollü olmalıdır.

Meta'nın 2026 "İki Kuralı" (Rule of Two) ajan güvenliği, bir turda en fazla ikisinin birleştirilebileceğini söylüyor: güvenilmeyen girdi, hassas veri, sonuçlu eylem. Araç arayüzü bu kuralı uyguladığınız yerdir — çağrıları reddederek, kullanıcı onayı isteyerek veya kapsamları yükselterek. Tam güvenlik bölümü için Faz 13 · 15'e ve ajan düzeyindeki izin politikaları için Faz 14 · 09'a bakın.

### Döngü nerede yaşıyor

| Bağlam | Kimi açıklar | Kim karar verir | Kim çalıştırır |
|---------|---------------|-------------|--------------|
| Tek tur function calling (OpenAI/Anthropic/Gemini) | Uygulama geliştirici | LLM | Uygulama geliştirici |
| MCP | MCP sunucusu | LLM (MCP istemcisi aracılığıyla) | MCP sunucusu |
| A2A | Agent Card yayıncısı | Çağrı yapan ajan | Çağrılan ajan |
| Web tarayıcısı (function-calling ajanı) | Tarayıcı eklentisi / WebMCP | LLM | Tarayıcı çalışma zamanı |

Her yerde aynı dört adım. Sütun adları değişir; yapı değişmez.

### Modelden JSON üretmesini istemek neden yetersiz?

"Modele JSON ile yanıt vermesini söylemek" function calling öncesi bir patikaydı. Sınır modellerde %5 ila %15 oranında başarısız olur ve daha küçük modellerde çok daha fazla. Hata modları arasında eksik parantez, virgül sonrası (trailing comma), uydurulmuş alanlar ve yanlış türler bulunur. Ardından bir JSON onarma geçişi, yeniden deneme veya kısıtlı bir kod çözücüye ihtiyacınız vardır.

Yerleşik function calling üç nedenle daha iyidir. Birincisi, sağlayıcı modeli tam çağrı şekli üzerinde uçtan uca eğitir, bu yüzden geçerli JSON oranı strict modda %98 ila %99'a yükselir. İkincisi, çağrı yükü kendi protokol slotunda oturur, serbest metnin içinde değil — böylece bir araç çağrısı kullanıcıya görünür yanıta asla sızma. Üçüncüsü, sağlayıcılar şema uyumluluğunu kısıtlı kod çözmeyle zorlar (OpenAI'ın strict modu, Anthropic'in `tool_use`'u, Gemini'nin `responseSchema`'sı). Çıktının doğrulanması garanti edilir.

Faz 13 · 02 üç sağlayıcı API'sini yan yana inceler. Faz 13 · 04 yapılandırılmış çıkışlar hakkında derinlemesine bilgi verir.

### Devre kesiciler

Döngü, model çağrileri üretmeyi bıraktığında veya ana program maksimum tur sayısına ulaştığında sonlanır. Üretimdeki ana programlar bunu 5 ila 20 tur aralığına ayarlar. Bunun ötesinde, modelin çıkamadığı bir döngüdesiniz neredeyse. Claude Code varsayılan olarak 20; OpenAI Assistants 10; Cursor'ın ajan modu 25'tir.

Alternatif — sınırsız döngüler — altı ayda bir "ajan gece boyunca API çağrılarında 400 dolar harcadı" başlıklı otopsi (post-mortem) olarak ortaya çıkar. Sınırsız olarak sunmayın.

Faz 14 · 12 hata kurtarma ve öz-iyileşme konusunu derinlemesine işler; Faz 17 üretim hız sınırlamalarını kapsar.

### Faz 13 buradan nereye gidiyor

- Dersler 02 ila 05, sağlayıcı düzeyindeki araç çağrısı yüzeyini cilalar.
- Dersler 06 ila 14, döngüyü MCP'ta genelleştirir.
- Dersler 15 ila 18, döngüyü düşmanca sunuculara, düşmanca kullanıcılara ve doğrulanmamış uzak auth yüzeylerine karşı savunur.
- Dersler 19 ila 22, patikayı ajanlar arası işbirliği, gözlemlenebilirlik, yönlendirme ve paketleme için genişletir.
- Ders 23, her primitifi kullanarak eksiksiz bir ekosistem sunar.

Kalan her ders bu dört adımlı döngünün bir ayrıntılandırmasıdır. Bunu değişmez olarak aklınızda tutun.

## Kullan

`code/main.py`, bir LLM olmadan dört adımlı döngüyü çalıştırır. Sahte bir "karar verici" fonksiyon, kullanıcı mesajında kalıp eşleştirmesi yaparak modeli taklit eder; çalıştırıcı, şema doğrulayıcı ve gözlem adımı gerçekçidir. Tam istek/yanıt koreografisini yazdırılabilir ara durumla görmek için çalıştırın, ardından sahte karar vericiyi sonraki bir derste gerçek bir sağlayıcıyla değiştirin.

Neye bakılmalı:

- Araç kaydı, araç başına üç alan tutar: ad, açıklama, şema ve bir çalıştırıcı referansı.
- Doğrulayıcı, yalnızca stdlib kullanılarak yazılmış minimal bir JSON Schema alt kümesidir (türler, required, enum, min/max). Faz 13 · 04 daha eksiksiz bir tane sunar.
- Döngü iterasyon sayısını beşte sınırlar. Üretim ajanlarının tam olarak bu tür bir devre kesiciye ihtiyacı vardır.

## Sun

Bu ders `outputs/skill-tool-interface-reviewer.md` dosyasını üretir. Bir tasarım aracı tanımı (ad + açıklama + şema + çalıştırıcı taslağı) verildiğinde, beceri onu döngü uyumluluğu için denetler: ad makine-kararlı mı, açıklama eksiksiz bir kullanım özeti mi, şema JSON Schema 2020-12'yi doğru mu kullanıyor ve saf/suçlu sınıflandırması açık mı.

## Alıştırmalar

1. `code/main.py`'e `get_stock_price(ticker)` adında dördüncü bir araç ekleyin. Açıklamasını "Kullanıcı bir ticker ile güncel hisse senedi fiyatını sorduğunda kullanın. Tarihsel fiyatlar veya piyasa özeti için kullanmayın" olarak yazın. Demoyu çalıştırın ve sahte karar vericinin ticker içeren sorguları yeni araca yönlendirdiğini doğrulayın.

2. Şema doğrulayıcısını bozun. `argümanları` nesnesinde zorunlu bir alanın eksik olduğu bir çağrı verin ve ana programın bunu çalıştırmadan önce reddettiğini doğrulan. Ardından bilinmeyen ekstra alanlı bir çağrı verin. Karar verin: ana program reddetmeli mi yoksa görmezden gelmeli mi? Seçiminizi bir güvenlik argümanıyla gerekçelendirin.

3. Demodaki her aracı saf veya sonuçlu olarak sınıflandırın. Gereken giriş kayıtlarına `consequential: true` bayrağı ekleyin ve döngüyü, bir sonuçlu araç seçildiğinde "kullanıcıya onay sorulacak" satırını yazacak şekilde değiştirin. Bu, her üretim ana programının ihtiyaç duyduğu onay kapısının (confirmation gate)_shape'dir.

4. Dört adımlı döngüyü kağıda çizin ve yukarıdaki sütun tablosunu en sevdiğiniz istemciyle (Claude Desktop, Cursor, ChatGPT veya özel bir yığın) doldurun. Faz 13 · 06'daki MCP'e özgü varyantla çapraz referans verin.

5. OpenAI'ın function calling kılavuzunu baştan sona okuyun. Burada sunulan dört adımlı döngüde yer almayan ancak istekte bulunan tek alanı belirleyin. Ne eklediğini ve neden gerekli değil de kullanışlı olduğunu açıklayın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| Tool (Araç) | "Modelin çağırabileceği bir şey" | Ad + JSON-Schema tipli girdi + çalıştırıcı fonksiyonu üçlemesi |
| Function calling | "Yerleşik araç kullanımı" | Yapılandırılmış araç çağrısı üretmek için sağlayıcı düzeyinde API desteği |
| Tool call (Araç çağrısı) | "Modelin eylem isteği" | Model tarafından üretilen `id`, `name`, `argümanları` içeren JSON yükü |
| Tool result (Araç sonucu) | "Aracın döndürdüğü" | Çalıştırıcının çıktısı, eşleşen id ile bir `tool` rol mesajına sarılmış |
| Parallel tool calls (Paralel araç çağriları) | "Bir anda birçok çağrı" | Bir model turunda birden fazla çağrı nesnesi, bağımsız ve id ile sıralanabilir |
| Strict mode | "Garantili JSON" | Modelin çıktısının beyan edilen şemaya uymasını zorlayan kısıtlı kod çözme |
| Pure tool (Saf araç) | "Salt okunur araç" | Yan etki yok; yeniden çalıştırmak güvenlidir |
| Consequential tool (Sonuçlu araç) | "Eylem aracı" | Dış durumu değiştirir; kapı, denetim veya kullanıcı onayı gerektirir |
| Four-step loop (Dört adımlı döngü) | "Araç çağrısı döngüsü" | açıkla → karar ver → çalıştır → gözlemle |
| Host (Ana program) | "Ajan çalışma zamanı" | Araç kaydını tutan, modeli çağıran ve çalıştırıcıyı çalıştıran program |

## İleri Okuma

- [OpenAI — Function calling guide](https://platform.openai.com/docs/guides/function-calling) — OpenAI tarzı araç beyanları ve çağrı şekilleri için kanonik referans
- [Anthropic — Tool use overview](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview) — Claude'un `tool_use` / `tool_result` blok formatı
- [Google — Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling) — Gemini'de `functionDeclarations` ve paralel çağrı anlambilimi
- [Model Context Protocol — Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — sağlayıcıdan bağımsız araç arayüzünün genelleştirilmesi
- [JSON Schema — 2020-12 release notes](https://json-schema.org/draft/2020-12/release-notes) — her modern araç API'sinin konuştuğu şema diyalekti
