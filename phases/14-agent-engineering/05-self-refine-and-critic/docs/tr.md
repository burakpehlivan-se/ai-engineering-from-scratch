# Self-Refine ve CRITIC: Yinelemeli Çıktı İyileştirmesi

> Self-Refine (Madaan ve diğerleri, 2023) tek bir LLM'i üç rolde kullanır — üret, geri bildir, iyileştir — bir döngü içinde. Ortalama kazanç: 7 görevde +20 mutlak. CRITIC (Gou ve diğerleri, 2023) geri bildirim adımını doğrulamayı harici araçlara yönlendirerek güçlendirir. 2026'da bu kalıp her framework'te "evaluator-optimizer" (Anthropic) veya guardrail döngüsü (OpenAI Agents SDK) olarak sunulur.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 14 · 03 (Reflexion)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Self-Refine'ın üç prompt'unu (üret, geri bildir, iyileştir) belirtin ve geçmişin (history) neden refine prompt'u için önemli olduğunu açıklayın.
- CRITIC'in kritik içgörüsünü açıklayın: LLM'ler harici temel olmadan öz-doğrulamada güvenilir değildir.
- Geçmiş ve isteğe bağlı harici bir doğrulayıcıyla stdlib bir Self-Refine döngüsü uygulayın.
- Bu kalıbı Anthropic'in "evaluator-optimizer" workflow'uyla ve OpenAI Agents SDK'nın çıktı guardrail'leriyle eşleştirin.

## Problem

Bir agent neredeyse doğru bir cevap üretir. Belki bir kod satırında sözdizimi hatası vardır. Belki bir özet çok uzundur. Belki bir plan bir uç durumu (edge case) kaçırır. İstediğiniz şey: agent kendi çıktısını eleştirsin, sonra düzeltsin.

Self-Refine bunun tek bir modelle, eğitim verisi olmadan, RL olmadan çalıştığını gösterir. Ancak bir sorun var: LLM'ler zorolgeler üzerinde öz-doğrulamada kötüdür. CRITIC düzeltmeyi adlandırır — doğrulama adımını harici araçlara yönlendirin (arama, kod yorumlayıcı, hesap makinesi, test çalıştırıcı).

Bu iki makale birlikte 2026 varsayılanını tanımlar: üret, mümkünse harici olarak doğrula, iyileştir, doğrulayıcı geçtiğinde dur.

## Kavram

### Self-Refine (Madaan ve diğerleri, NeurIPS 2023)

Tek bir LLM, üç rol:

```text
generate(task) -> output_0
feedback(task, output_0) -> critique_0
refine(task, output_0, critique_0, history) -> output_1
feedback(task, output_1) -> critique_1
refine(task, output_1, critique_1, history) -> output_2
...
feedback "sorun yok" dediğinde veya bütçe tükendiğinde dur.
```

Kritik detay: `refine` tüm geçmişi görür — tüm önceki çıktıları ve eleştirileri — böylece hataları tekrarlamaz. Makale bunu ablatır: geçmişi düşürürseniz kalite keskin düşer.

Manşet: 7 görevde (matematik, kod, kısaltma, diyalog) GPT-4 dahil ortalama +20 mutlak iyileştirme. Eğitim yok, harici araç yok, tek model.

### CRITIC (Gou ve diğerleri, arXiv:2305.11738, v4 Şubat 2024)

Self-Refine'ın zayıflığı: geri bildirim adımı kendini puanlayan bir LLM'dir. Olgusal iddialar için bu güvenilir değildir (bir hallücinasyon, onu üreten model için genellikle ikna edici görünür). CRITIC `feedback(task, output)` yerine `verify(task, output, tools)` koyar; burada `tools` şunları içerir:

- Olgusal iddialar için bir arama motoru.
- Kod doğruluğu için bir kod yorumlayıcı (code interpreter).
- Aritmetik için bir hesap makinesi.
- Alan-specific doğrulayıcılar (birim testleri, tip denetleyicileri, linter'lar).

Doğrulayıcı, araç sonuçlarına dayalı yapılandırılmış bir eleştiri üretir. İyileştirici sonra bu eleştiriye koşullandırılır.

Manşet: CRITIC,olgusal görevlerde eleştiri temellendirildiğinden Self-Refine'ı geçer. Harici doğrulayıcı olmayan görevlerde (yarattıcı yazma, biçimlendirme), CRITIC Self-Refine'a düşer.

### Durma koşulu

İki yaygın şekil:

1. **Doğrulayıcı geçer.** Harici test başarı döndürür. Mevcut olduğunda tercih edilir (birim testleri, tip denetleyicisi, guardrail assertion'ı).
2. **Geri bildirim verilmez.** Model "çıkış iyi" der. Daha ucuz ama güvenilir değil; maks iterasyon üst sınırıyla eşleştirin.

2026 varsayılanı: birleştirin. "Doğrulayıcı geçerse VEYA model iyi derse VE iterasyonlar >= 2 VEYA iterasyonlar >= max_iterations ise dur."

### Evaluator-Optimizer (Anthropic, 2024)

Anthropic'in Aralık 2024 yazısı bunu beş workflow kalıbından biri olarak adlandırır. İki rol:

- Evaluator: çıktıyı puanlar ve bir eleştiri üretir.
- Optimizer: eleştiriye göre çıktıyı revize eder.

Evaluator geçene kadar döngü. Bu, Anthropic'in çerçevesinde Self-Refine/CRITIC'tir. Anthropic'in eklediği kritik mühendislik detayı: evaluator ve optimizer prompt'ları modelin yalnızca onay damgası vurmaması için substantially farklı olmalıdır.

### OpenAI Agents SDK çıktı guardrail'leri

OpenAI Agents SDK bu kalıbı "output guardrails" olarak sunar. Bir guardrail, bir agent'ın son çıktısı üzerinde çalışan bir doğrulayıcıdır. Guardrail tetiklenirse (OutputGuardrailTripwireTriggered fırlatırsa), çıktı reddedilir ve agent tekrar deneyebilir. Guardrail'ler araç çağırabilir (CRITIC tarzı) veya saf fonksiyonlar olabilir (Self-Refine tarzı).

### 2026 tuzakları

- **Onay damgası döngüleri.** Aynı model üretimi ve eleştiriyi aynı prompt stiliyle yapıyorsa "bana iyi görünüyor"da yakınsar. Farklı yapısal prompt'lar veya eleştiri için küçük ucuz bir model kullanın.
- **Aşırı iyileştirme.** Her refine geçişi gecikme ve token ekler. 1-3 geçiş bütçele; sonrasında insan incelemesine yükseltin.
- **Basit görevlerde CRITIC.** Harici doğrulayıcı yoksa CRITIC Self-Refine'a düşer; stub doğrulayıcı için gecikme ödemeyin.

## İnşa Et

`code/main.py` Self-Refine ve CRITIC'i bir oyuncak görevde uygular: verilen bir konu hakkında kısa bir madde listesi (bullet list) üret. Doğrulayıcı biçimi kontrol eder (3 madde, her biri 60 karakterden kısa). CRITIC, bilinen hallüsinasyonları cezalandıran harici bir "olgusal doğrulayıcı" ekler.

Bileşenler:

- `generate` — betiklenmiş üretici.
- `feedback` — LLM tarzı öz-eleştiri.
- `verify_external` — CRITIC tarzı temellendirilmiş doğrulayıcı.
- `refine` — geçmişi vererek çıktıyı yeniden yazar.
- Durma koşulu — doğrulayıcı geçer veya maks 4 iterasyon.

Çalıştırın:

```bash
python3 code/main.py
```

Self-Refine ve CRITIC çalıştırmalarını karşılaştırın. CRITIC, öz-eleştirisinin temellendirmeye sahip olmadığı dış doğrulayıcı sayesinde Self-Refine'ın kaçırdığı olgusal bir hatayı yakalar.

## Kullan

Anthropic'in evaluator-optimizer'ı bu kalıbın Claude-dostu dildeki karşılığıdır. OpenAI Agents SDK'nın çıktı guardrail'leri CRITIC şeklindedir (guardrail'ler araç çağırabilir). LangGraph Self-Refine gibi okunan bir yansıma düğümü sunar. Google'ın Gemini 2.5 Computer Use, CRITIC bir varyantı olan adım başı (per-step) bir güvenlik değerlendiricisi ekler: her eylem commit'ten önce doğrulanır.

## Teslim Et

`outputs/skill-refine-loop.md`, görev şekli, doğrulayıcı kullanılabilirliği ve iterasyon bütçesine göre bir evaluator-optimizer döngüsü yapılandırır. Üreteç, evaluator/doğrulayıcı ve optimizer için prompt'lar üretir, artı bir durma politikası.

## Alıştırmalar

1. Toy kodu max_iterations=1 ile çalıştırın. CRITIC hâlâ yardımcı oluyor mu?
2. Harici doğrulayıcıyı gürültülü biriyle (%30 rastgele pozitif) değiştirin. Döngü ne yapar? Bu, 2026'daki çoğu guardrail yığınının gerçeğidir.
3. "Farklı modellerde üretici-eleştirmen" varyantı uygulayın: büyük model üretir, küçük model eleştirir. Aynı modeli geçer mi?
4. CRITIC Bölüm 3'ü okuyun (arXiv:2305.11738 v4). Üç doğrulama aracı kategorisini adlandırın ve her biri için bir örnek verin.
5. OpenAI Agents SDK'nın `output_guardrails`'ını CRITIC'in doğrulayıcı rolüyle eşleştirin. SDK'nın neyi yanlış neyi doğru yaptığını söyleyin.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Self-Refine | "Kendini düzelten LLM" | Tek modelde geçmişle üret -> geri bildirim -> refine döngüsü |
| CRITIC | "Araç temelli doğrulama" | Geri bildirimi harici bir doğrulayıcıyla (arama, kod, hesap, testler) değiştirir |
| Evaluator-Optimizer | "Anthropic workflow kalıbı" | İki rol — evaluator puanlar, optimizer revize eder — yakınsamaya kadar döngü |
| Output guardrail | "Sonradan yapılan kontrol" | Agent bir çıktı ürettikten sonra çalışan OpenAI Agents SDK doğrulayıcısı |
| Verify step | "Eleştiri aşaması" | Temellendirilmiş mi yoksa öz-muameleli mi — kritik karar |
| Refine history | "Modelin zaten denediği" | Önceki çıktılar + eleştiriler refine prompt'unun başına eklenir; düşürülürse kalite çöker |
| Rubber-stamp loop | "Öz-onay hatası" | Aynı prompt eleştirisi "iyi görünüyor" döndürür; farklı yapısal prompt'larla çözülür |
| Stop condition | "Yakınsama testi" | Doğrulayıcı geçer VEYA geri bildirim yok VE iterasyon üst sınırı; asla tek koşul |

## İleri Okuma

- [Madaan ve diğerleri, Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) — kanonik makale
- [Gou ve diğerleri, CRITIC (arXiv:2305.11738)](https://arxiv.org/abs/2305.11738) — araç temelli doğrulama
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — evaluator-optimizer workflow kalıbı
- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) — CRITIC şeklindeki doğrulayıcılar olarak çıktı guardrail'leri
