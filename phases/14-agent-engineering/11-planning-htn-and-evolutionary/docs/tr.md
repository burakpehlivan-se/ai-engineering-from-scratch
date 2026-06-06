# HTN ve Evrimsel Arama ile Planlama

> Sembolik planlama, planın ispatlanabilir doğru olduğu durumları ele alır. Evrimsel kod araması, fitness fonksiyonunun makine tarafından kontrol edilebilir olduğu durumları ele alır. ChatHTN (2025) ve AlphaEvolve (2025) bir LLM ile eşleştirildiğinde her birinin neyi açtığını gösterir.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 02 (ReWOO ve Plan-and-Execute)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Hierarchical Task Networks'i (HTN) açıklayın: görevler, yöntemler, operatörler, ön koşullar, etkiler.
- ChatHTN'in hibrit döngüsünü — LLM geri dönüş çözümlemeli (fallback decomposition) semantik aramasını — açıklayın.
- AlphaEvolve'ın evrimsel döngüsünü ve neden yalnızca programlı bir değerlendiriciyle çalıştığını açıklayın.
- Stdlib'da bir oyuncak HTN planlayıcısı artı bir oyuncak evrimsel arama uygulayın.

## Problem

ReWOO (Ders 02), Plan-and-Execute ve ReAct çoğu agent planlamasını kapsar. İyi kapsamadığı iki durum:

1. **İspatlanabilir doğruluklu planlar.** Zamanlama, uçuş rotası, uyumluluk workflow'ları — plan yapısal olarak tutarlı olmalıdır. Bazen bir adımı uyduran akıcı bir LLM planı kabul edilemezdir.
2. **Makine tarafından kontrol edilebilir fitness fonksiyonuyla optimizasyonlar.** Matris çarpımı, sezgisel zamanlama, derleyici geçişleri — hedef "doğru bir plan" değil "en iyi plan"dır.

HTN planlaması ve AlphaEvolve iki farklı sorunu çözer. İkisi de LLM'leri yerine koymak için değil, amplifiye etmek için kullanır.

## Kavram

### Hierarchical Task Networks

Bir HTN şöyledir:

- **Görevler** — birleştirilmiş (decompose edilecek) ve temel (doğrudan çalıştırılabilir).
- **Yöntemler** — birleştirilmiş bir görevi alt görevlere分解 yolları, ön koşullarla.
- **Operatörler** — ön koşulları ve etkileri olan temel eylemler.
- **Durum** — olgular kümesi.

Planlama: bir hedef görev ve başlangıç durumu verildiğinde, ön koşullarının sırayla sağlandığı temel operatörlere bir çözümleme bulun.

HTN LLM'lerden eskidir ve hâlâ ispatlanabilir doğru planlar için referanstır.

### ChatHTN (Gopalakrishnan ve diğerleri, 2025)

ChatHTN (arXiv:2505.11814) semantik HTN ile LLM sorgularını iç içe geçirir:

1. Mevcut yöntemlerle mevcut birleşik görevi çözmeyi deneyin.
2. Hiçbir yöntem uymazsa LLM'e sorun: "`s` durumunda `görev`i nasıl çözersiniz?"
3. LLM yanıtını aday alt görevlere çevirin.
4. Operatör şemasına göre doğrulayın; geçersiz çözümlemeleri reddedin.
5. Recursive edin.

Makalenin merkez iddiası: üretilen her plan ispatlanabilir tutarlıdır çünkü LLM önerileri yalnızca aday çözümlemeler olarak girer, doğrudan plan düzenlemeleri olarak değil. Sembolik katman doğruluğu sahiplenir; LLM yöntem kütüphanesini genişletir.

Çevrimiçi yöntem öğrenmesi (OpenReview `gwYEDY9j2x`, 2025 takibi) LLM tarafından üretilen çözümlemeleri regresyonla genelleştiren bir öğrenici ekler — LSG sorgu sıklığını %75'e kadar azaltır.

### AlphaEvolve (Novik ve diğerleri, 2025)

AlphaEvolve (arXiv:2506.13131, DeepMind, Haziran 2025) farklı bir canavar: Gemini 2.0 Flash/Pro topluluğu tarafından orkestra edilen evrimsel kod araması.

Döngü:

1. Tohum program + programlı değerlendirici ile başlayın (fitness puanı döndürür).
2. LLM topluluğu mutasyonlar önerir.
3. Mutasyonları değerlendiriciyle çalıştırın.
4. En iyiyi koruyun; tekrar mutasyona uğratın.

Yayınlanan kazançlar:

- 56 yılda 4x4 kompleks matris çarpımı için Strassen'in ilk iyileştirmesi (48 skaler çarpım).
- Bir Borg zamanlama sezgiseliyle %0.7 geri kazanılmış Google hesaplama.
- Bir frontier iş yükünde %32 FlashAttention hızlanması.

Katı kısıtlama: fitness fonksiyonu makine tarafından kontrol edilebilir olmalıdır. Düz metin cevapları üzerinde evrimsel arama yakınsamaz.

### Hangisini ne zaman kullanmalı

| Sorun sınıfı | Kullan | Neden |
|---------------|--------|-------|
| Katı kısıtlamalı zamanlama | HTN + ChatHTN | İspatlanabilir tutarlılık |
| Derleyici optimizasyonu | AlphaEvolve | Makine tarafından kontrol edilebilir fitness |
| Çoklu adım görev yürütmesi | ReAct / ReWOO | Döngüde LLM, resmi garanti yok |
| Testlerle kod iyileştirmesi | AlphaEvolve | Testler değerlendiricidir |
| Politika bağlı otomasyon | HTN | Ön koşullar politikayı kodlar |

### Bu kalıp nerede yanlış gider

- **Operatör olmadan HTN.** Ön koşul/etki şemaları olmadan tutarlılık iddiası çöker. ChatHTN'in "LLM çözümleme öneriyor" claim'i, geçersiz hamleleri reddetmek için şemaya ihtiyaç duyar.
- **Gerçek bir değerlendirici olmadan AlphaEvolve.** "LLM'e kodun daha iyi olup olmadığını sor" bir fitness fonksiyonu değildir. Değerlendirici deterministik ve hızlı olmalıdır.
- **Aşırı mühendislik.** Çoğu agent görevi bunların hiçbirini gerektirmez. Önce ReAct veya ReWOO'ya başvurun.

## İnşa Et

`code/main.py` iki oyuncak uygular:

- Operatörler, yöntemler, ön koşullar, etkiler ve birleşik bir göreve hiçbir yöntem uymadığında devreye giren `LLMFallback` ile stdlib bir HTN planlayıcısı. "LLM" betiklenmiş bir çözümleyicidir böylece planlayıcı çevrimdışı çalışır.
- Aritmetik programlar üzerinde stdlib evrimsel araması: çıktıların `|f(x) - target|`'ı test kümesi üzerinde en aza indiren ifadeleri büyütün. Değerlendirici deterministiktir.

Çalıştırın:

```bash
python3 code/main.py
```

Trace, HTN planlayıcısının birleşik bir görevi (plan ortasında LLM geri dönüşüyle) çözümlemesini ve evrimsel döngünün bir hedef ifadeye yakınsamasını gösterir.

## Kullan

- **HTN planlayıcıları** — `pyhop`, `SHOP3` veya alan-specific politika uygulaması için kendi planlınızı oluşturun.
- **ChatHTN** — araştırma kodu; kalıp (sembolik + LLM geri dönüşü) herhangi bir HTN planlayıcısına temiz taşınır.
- **AlphaEvolve** — DeepMind makalesi; kalıp (topluluk + değerlendirici) yeniden üretilebilir. OpenEvolve ve benzeri açık kaynak çatalları ortaya çıkıyor.
- **Agent framework'leri** — henüz birincil sınıf HTN veya AlphaEvolve sunmuyor. Bunu bir subagent veya arka plan işçisi olarak inşa edin.

## Teslim Et

`outputs/skill-hybrid-planner.md`, LLM rolü açıkça sınırlanmış bir hibrit planlayıcı iskeleti (HTN veya evrimsel) üretir.

## Alıştırmalar

1. HTN planlayıcısını geri adım atma (backtracking) ile genişletin: bir operatörün post-koşulu çalışma zamanında başarısız olursa, geri sarın ve sonraki yöntemi deneyin.
2. ChatHTN'e bir LLM-yöntem önbelleği ekleyin: LLM durum deseninde `P` içinde `T` görevini çözümlediğinde sonucu saklayın. Sonraki çağrıda önce yöntem kütüphanesini kontrol edin.
3. Evrimsel arama değerleyicisini gerçek bir test paketine değiştirin. 20 test durumundan geçen bir sıralama fonksiyonu evrimleştirin; yakınsamaya kadar nesil sayısını raporlayın.
4. AlphaEvolve'ın değerlendirici tasarım notlarını okuyon. Önemsediğiniz bir alan (SQL sorgu optimizasyonu, test paketi küçültme, deployment YAML) için bir değerlendirici tasarlayın.
5. Birleştirin: birleşik bir görevi alt görevlere çözümlemek için HTN kullanın, sonra her alt görevin temel operatöründe evrimsel arama kullanın. Nerede parlıyor, nerede aşırı mühendislik yapıyor?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| HTN | "Hiyerarşik planlayıcı" | Operatörler, ön koşullar, etkilerle görev çözümlemesi |
| Method | "Çözümleme kuralı" | Birleşik bir görevi alt görevlere ayırma yolu |
| Operator | "Temel eylem" | Ön koşul ve etkisi olan somut adım |
| ChatHTN | "LLM + HTN" | Sembolik planlayıcı hiçbir yöntem uymadığında LLM'e sorar |
| AlphaEvolve | "Evrimsel kod araması" | Topluluk LLM'leri kodu mutasyona uğratır; deterministik değerlendirici seçer |
| Fitness function | "Değerlendirici" | Çıktılar üzerinde deterministik, makine tarafından kontrol edilebilir puan |
| Online method learning | "Önbelleklenmiş LLM çözümlemesi" | Sorgu maliyetini azaltmak için LLM planlarını sakla + genelleştir |

## İleri Okuma

- [Gopalakrishnan ve diğerleri, ChatHTN (arXiv:2505.11814)](https://arxiv.org/abs/2505.11814) — semantik + LLM hibrit planlayıcı
- [Novik ve diğerleri, AlphaEvolve (arXiv:2506.13131)](https://arxiv.org/abs/2506.13131) — LLM mutasyonlarıyla evrimsel kod araması
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — ne zaman bir planlayıcıya ne zaman basit bir döngüye ihtiyaç var
