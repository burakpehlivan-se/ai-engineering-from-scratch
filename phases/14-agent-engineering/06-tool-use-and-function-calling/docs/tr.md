# Araç Kullanımı ve Function Calling

> Toolformer (Schick ve diğerleri, 2023) öz-denetimli (self-supervised) araç notlandırmasını başlattı. Berkeley Function Calling Leaderboard V4 (Patil ve diğerleri, 2025) 2026 standardını belirler: %40 agentic, %30 multi-turn, %10 live, %10 non-live, %10 hallücinasyon. Tek tur (single-turn) çözülmüştür. Hafıza, dinamik karar alma ve uzun vadeli araç zincirleri henüz değildir.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 13 · 01 (Function Calling Derinlemesine)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Toolformer'ın öz-denetimli eğitim sinyalini açıklayın: yalnızca çalıştırma sonraki token loss'unu düşürüyorsa araç notlarını tutun.
- BFCL V4'ün beş değerlendirme kategorisini ve her birinin neyi ölçtüğünü adlandırın.
- Schema doğrulaması, argüman zorlaması (coercion) ve çalıştırma sandbox'ıyla stdlib bir araç kaydı (tool registry) uygulayın.
- Üç 2026 açık sorununu teşhis edin: uzun vadeli araç zincirleme, dinamik karar alma ve hafıza.

## Problem

Erken dönem araç kullanımı şunu soruyordu: model doğru bir function çağrısı yapabilir mi? Modern araç kullanımı şunu soruyor: model 40 adımda araçları zincirleyebilir mi, hafızayla, kısmi gözlemlilikle, araç hatalarından kurtulmayla, mevcut olmayan araçları uydurmadan?

Toolformer temeli kurdu: modeller öz-denetimle ne zaman araç çağıracağını öğrenebilir. BFCL V4 2026 değerlendirme hedefini tanımlar. İkisi arasındaki boşluk, production agent'ların yaşadığı alandır.

## Kavram

### Toolformer (Schick ve diğerleri, NeurIPS 2023)

Fikir: modelin kendi ön-eğitim corpus'una aday API çağrılarıyla not bırakmasına izin verin. Her aday için çalıştırın. Aracın sonucu dahil edildiğinde sonraki token loss'unu düşürüyorsa notu saklayın. Filtrelenmiş corpus üzerinde fine-tune edin.

Kapsanan araçlar: hesap makinesi, SSS sistemi, arama motorları, çevirmen, takvim. Öz-denetimli sinyal tamamen aracın metin tahmin etmeye yardımcı olup olmadığıyla ilgilidir — insan etiketi yoktur.

Ölçek sonucu: araç kullanımı ölçekle ortaya çıkar. Daha küçük modeller araç notlarından zarar görür; daha büyük modeller kazanır. Bu yüzden 2026 frontier modelleri güçlü araç kullanımını içselleştirirken, çoğu 7B modelinin güvenilir olması için açık araç kullanımı fine-tune'una ihtiyacı vardır.

### Berkeley Function Calling Leaderboard V4 (Patil ve diğerleri, ICML 2025)

BFCL 2026'da de facto değerlendirme aracıdır. V4 bileşimi:

- **Agentic (%40)** — tam agent trajectory'leri: hafıza, çoklu tur, dinamik kararlar.
- **Multi-Turn (%30)** — araç zincirleriyle etkileşimli konuşmalar.
- **Live (%10)** — kullanıcı tarafından gönderilen gerçek istekler (daha zor dağılım).
- **Non-Live (%10)** — sentetik test durumları.
- **Hallücinasyon (%10)** — hiçbir araç çağrılmaması gerektiğinde tespit.

V3 durum tabanlı (state-based) değerlendirme getirdi: bir araç dizisinden sonra, API'nin gerçek durumunu kontrol edin (ör. "dosya oluşturuldu mu?") araç çağrılarının AST eşleştirmesi yerine. V4 arama motoru, hafıza ve biçim hassasiyeti kategorileri ekledi.

Anahtar 2026 bulgusu: tek tur function calling neredeyse çözülmüştür. Başarısızlıklar hafızada (turlar arası bağlam taşıma), dinamik karar alma (önceki sonuçlara göre araç seçme), uzun vadeli zincirler (20+ adımdan sonra kayma) ve hallücinasyon tespitinde (hiçbir araç uymadığında çağırmayı reddetme) yoğunlaşır.

### Araç şeması (tool schema)

Her sağlayıcının bir şeması vardır. Detaylarda farklılık gösterirler ancak aynı şekli paylaşırlar:

```text
name: string
description: string (ne yapar, ne zaman kullanılır)
input_schema: JSON Schema (properties, required, types, enums)
```

Anthropic doğrudan `input_schema` kullanır. OpenAI `function.parameters` kullanır. Her ikisi de JSON Schema kabul eder. Açıklamalar kritiktir — model doğru aracı seçmek için bunları okur. Kötü araç açıklamaları yanlış-aracın-seçilmesi (wrong-tool-picked) başarısızlıklarının bir numaralı kök nedenidir.

### Argüman doğrulaması

Hiçbir araç çağrısına güvenmeyin. Doğrulayın:

1. **Tip zorlaması (coercion).** Model, şemanın int dediği yerde string "5" döndürebilir. Belirsizse zorlayın; belirsizse reddedin.
2. **Enum doğrulaması.** Şema `status in {"open", "closed"}` diyorsa ve model `"in_progress"` emit ediyorsa, tanımlayıcı hata ile reddedin.
3. **Zorunlu alanlar.** Eksik zorunlu alan -> modele anında hata gözlemi, crash değil.
4. **Biçim doğrulaması.** Tarihler, e-postalar, URL'ler — regex ile değil somut ayrıştırıcılarla doğrulayın.

Her doğrulama başarısızlığı, modelin doğru形状 ile tekrar deneyebilmesi için yapılandırılmış bir gözlem döndürmelidir.

### Paralel araç çağrıları

Modern sağlayıcılar tek bir asistan turunda paralel araç çağrılarını destekler. Döngü:

1. Model farklı `tool_use_id`'leriyle 3 araç çağrısı üretir.
2. Runtime bunları çalıştırır (bağımsızsa paralel).
3. Her sonuç `tool_use_id` ile korele edilmiş bir `tool_result` bloğu olarak geri gider.

Mühendislik kuralı: korelasyon ID'lerini kritik olarak kabul edin. Değiştirirseniz yanlış-aracın-yanlış-sonuca yönlendirilmesi (wrong-tool-to-wrong-result routing) alırsınız.

### Sandbox

Araç çalıştırması sandbox sınırıdır. Ayrıntılar için Ders 09'a bakın. Kısa versiyon: her araç okuma/yazma yüzeyi, ağ erişimi, zaman aşımı ve hafıza sınırı belirtmelidir. Genel `run_shell(cmd)` bir kırmızı bayraktır; belirli `git_status()` daha güvenlidir.

## İnşa Et

`code/main.py` production şekilli bir araç kaydı uygular:

- JSON Schema alt küme doğrulayıcı (yalnızca stdlib).
- Açıklama, giriş şeması, zaman aşımı ve çalıştırıcıyla araç kaydı.
- Argüman zorlaması ve enum doğrulaması.
- Korelasyon ID'leriyle paralel araç yönlendirmesi.
- Hata gözlemleri yapılandırılmış string'ler olarak.

Çalıştırın:

```bash
python3 code/main.py
```

Trace, tek bir turda üç araç çağıran mini bir agent'ı, tanımlayıcı bir hata ile reddedilen kasıtlı olarak hatalı bir çağrıyı gösterir.

## Kullan

Her sağlayıcının kendi araç şeması vardır — Anthropic, OpenAI, Gemini, Bedrock. Çoklu sağlayıcıya ihtiyacınız varsa bir çeviri katmanı (OpenAI Agents SDK, Vercel AI SDK, LangChain tool adapter) kullanın. BFCL referans benchmark'ıdır — araç kullanımı ürünün merkezindeyse, teslim etmeden önce agent'ınıza karşı çalıştırın.

## Teslim Et

`outputs/skill-tool-registry.md` verilen bir görev alanı için araç kataloğu, şema ve kaydı üretir. Açıklama kalitesi kontrolleri içerir (her aracın açıklaması modelin ne zaman kullanacağını söylüyor mu?).

## Alıştırmalar

1. Modelin diğer hiçbir aracı kullanmayı açıkça reddetmesine izin veren "no-op" bir araç ekleyin. BFCL benzeri bir hallücinasyon testinde ölçün.
2. Int-as-string ve float-as-string için argüman zorlaması uygulayın. Zorlama gerçek hataları gizlemeye nerede başlar?
3. Araç başına zaman aşımı ve bir devre kesici (circuit breaker) ekleyin (ardışık 3 başarısızlıktan sonra 60s boyunca aracı reddedin). Bu modelin kurtulma şeklini nasıl değiştirir?
4. BFCL V4 açıklamasını okuyun. Bir kategori seçin (ör. "multi-turn") ve 10 örnek isteği agent'ınızdan geçirin. Geçme oranını raporlayın.
5. Stdlib doğrulayıcıyı Pydantic veya Zod'a taşıyın. Pydantic/Zod oyuncak olanın kaçırdığı neyi yakaladı?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Function calling | "Araç kullanımı" | Doğrulanmış şemayla yapılandırılmış çıktı araç çağrısı |
| Toolformer | "Öz-denetimli araç notlandırma" | Schick 2023 — sonuçları sonraki token loss'unu düşüren araç çağrılarını tutun |
| BFCL | "Berkeley Function Calling Leaderboard" | 2026 benchmark'ı: %40 agentic, %30 multi-turn, %10 live, %10 non-live, %10 hallücinasyon |
| Tool schema | "Model için function imzası" | name, description, argümanların JSON Schema'sı |
| tool_use_id | "Korelasyon ID'si" | Bir araç çağrısını sonucuyla bağlar; paralel yönlendirme için gerekli |
| Hallucination detection | "Ne zaman çağrılmayacağını bilmek" | V4 kategorisi: hiçbir araç uymadığında çağırmayı reddetme |
| Argument coercion | "String-to-int onarımı" | Öngörülebilir şema uyumsuzluğu için dar düzeltmeler; belirsizse reddet |
| Sandboxing | "Araç çalıştırma sınırı" | Araç başına okuma/yazma yüzeyi, ağ, zaman aşımı, hafıza sınırı |

## İleri Okuma

- [Schick ve diğerleri, Toolformer (arXiv:2302.04761)](https://arxiv.org/abs/2302.04761) — öz-denetimli araç notlandırma
- [Berkeley Function Calling Leaderboard (V4)](https://gorilla.cs.berkeley.edu/leaderboard.html) — 2026 eval benchmark'ı
- [Anthropic, Tool use documentation](https://platform.claude.com/docs/en/agent-sdk/overview) — Claude Agent SDK'daki production araç şeması
- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) — function tool türü ve Guardrails
