# Capstone 17 — Kişisel AI Eğitmeni (Adaptif, Çok Modlu, Bellekli)

> Khanmigo (Khan Academy), Duolingo Max, Google LearnLM / Gemini for Education, Quizlet Q-Chat ve Synthesis Tutor 2026'da ölçekte adaptif çok modlu eğitimi hayata geçirdi. Ortak şekil: Sokratik politika (asla cevabı olduğu gibi dökme), her etkileşimden sonra güncellenen bir öğrenci modeli (Bayesyen bilgi izleme tarzı), ses + metin + fotoğraf-matematik girdisi, müfredat grafı geri getirme (retrieval), aralıklı tekrar (spaced-repetition) zamanlaması ve yaşa uygun içerik için sert güvenlik filtreleri. Capstone, konu-spesifik bir eğitmen (K-12 cebir veya giriş Python) göndermek, 10 öğrenciyle iki haftalık bir etkinlik çalışması yürütmek ve bir içerik-güvenliği denetimini geçmektir.

**Type:** Capstone
**Languages:** Python (backend, öğrenci modeli), TypeScript (web uygulaması), SQL (Postgres + Neo4j üzerinden müfredat grafı)
**Prerequisites:** Phase 5 (NLP), Phase 6 (konuşma), Phase 11 (LLM mühendisliği), Phase 12 (çok modlu), Phase 14 (ajanlar), Phase 17 (altyapı), Phase 18 (güvenlik)
**Phases exercised:** P5 · P6 · P11 · P12 · P14 · P17 · P18
**Time:** 30 saat

## Problem

Adaptif eğitim eskiden bir eğitim teknolojisi araştırma nişiydi. 2026 itibariyle bu bir tüketici ürünüdür. Khanmigo ABD'deki çoğu okul bölgesinde dağıtıldı. Duolingo Max on milyonlarca aylık aktif kullanıcıya (MAU) ulaştı. Google'ın LearnLM'i / Gemini for Education, Google Classroom'da eğitim verme (tutoring) yapıyor. Quizlet Q-Chat bilgi kartlarının yanında duruyor. Synthesis Tutor, meraklı çocuklar için eğitmen ile viral oldu. Ortak unsurlar: çok modlu girdi (yaz, konuş, denklem fotoğrafla), Sokratik pedagoji (önce sor, sonra açıkla), her etkileşimden sonra güncellenen bir öğrenci modeli ve sıkı yaşa uygun güvenlik.

Bunu belirli bir kohort için inşa edeceksiniz. Ölçüt çıtası gerçek bir etkinlik çalışmasıdır: 10 öğrenciyle iki hafta boyunca ön-test ve son-test puanları. Ses döngüsü doğal hissettirmelidir (capstone 03 alt-yığını). Bellek gizliliğe saygılı olmalıdır. Güvenlik filtresi K-12 için COPPA-farkında (COPPA-aware) red-team'i geçmelidir.

## Concept

Dört bileşen. **Eğitmen politikası (tutor policy)** bir Sokratik döngüdür: öğrenci cevabı istediğinde, politika yönlendirici bir soru sorar; doğru yaptıklarında, bir sonraki kavrama geçer; takıldıklarında, iskeletlenmiş (scaffolded) bir ipucu sunar. **Öğrenci modeli**, her etkileşimden sonra müfredat düğümü başına ustalık olasılığını güncelleyen Bayesyen bilgi izleme (BKT) veya basit bir varyantıdır. **Müfredat grafı**, önkoşul kenarlarıyla kavramların bir Neo4j'üdür; politika bir sonraki kavramı seçmek için grafı yürür. **Bellek**, geçmiş etkileşimleri, hataları ve tercihleri tutan epizodik + anlamsal bir depodur (agentmemory tarzında).

UX çok modludur. Yazılı cevaplar için metin girdisi. LiveKit + Whisper (capstone 03'ü yeniden kullanın) aracılığıyla ses girdisi. Matematik problemleri için dots.ocr veya PaliGemma 2 ile fotoğraf girdisi. Cartesia Sonic-2 ile ses çıktısı. Güvenlik, Llama Guard 4 artı yaşa uygun bir filtre (yetişkin içeriğini, şiddeti, öz-zararı engeller) ve COPPA-farkında bir bellek saklama politikası kullanır.

Etkinlik çalışması teslim edilen şeydir. 10 öğrenci, ön-test, iki hafta eğitmen etkileşimi (haftada 3 oturum), son-test. Aynı içeriği eğitmen politikası olmadan doğrusal olarak teslim eden adaptif-olmayan bir baseline kohortuyla karşılaştırın.

## Architecture

```
learner device
 |
 +-- text -> web app
 +-- voice -> LiveKit Agents (ASR + TTS)
 +-- photo math -> dots.ocr / PaliGemma 2
 |
 v
 tutor policy (LangGraph)
 - Socratic decision head
 - next-concept chooser (curriculum graph walk)
 - hint scaffolder
 - mastery update
 |
 v
 learner model (BKT / item-response theory)
 - per-concept mastery probability
 - spaced-repetition scheduler (SM-2 or FSRS)
 |
 v
 memory (agentmemory-style)
 - episodic: every interaction
 - semantic: learned mistakes, preferences
 - retention policy: COPPA / GDPR aware
 |
 v
 curriculum graph (Neo4j)
 - prerequisite edges
 - OER content attached
 |
 v
 safety:
 Llama Guard 4 + age-appropriate filter
 memory access guarded by learner ID scope
```

#### Açıklama

Bu mimari, öğrenci cihazından güvenlik ve gizlilik son noktalarına kadar tam veri akışını gösterir. Öğrenci cihazı üç mod sunar: yazılı cevaplar için metin (web uygulamasına gider), konuşma için ses (LiveKit Agents'a gider) ve matematik problemleri için fotoğraf (dots.ocr veya PaliGemma 2 ile tanınır). Bu kanalların tümü bir LangGraph'ta uygulanan eğitmen politikasına akar; politika dört düğümden oluşur: Sokratik karar başı, sonraki kavram seçici (müfredat grafında yürüyüş), ipucu iskeleci ve ustalık güncelleyici. Öğrenci modeli kavram başına ustalık olasılığını izler ve SM-2 veya FSRS ile aralıklı tekrar zamanlar. Bellek agentmemory tarzında iki katmanlıdır: epizodik (her etkileşim) ve anlamsal (öğrenilen hatalar ve tercihler); COPPA/GDPR-farkında bir saklama politikasına tabidir. Müfredat grafı Neo4j'dir; kavram düğümleri önkoşul kenarlarıyla bağlıdır ve OER içeriği (Open Educational Resources) her düğüme eklenmiştir. Güvenlik katmanı, tüm model çıktılarını yaşa uygun filtreyle birlikte Llama Guard 4'ten geçirir; bellek erişimi öğrenci kimliği kapsamıyla korunur.

## Stack

- Konu seçimi: K-12 cebir veya giriş Python (derinlik için birini seçin)
- Eğitmen politikası: LangGraph üzerinde Claude Sonnet 4.7 (prompt önbelleğe alma ile)
- Öğrenci modeli: Bayesyen bilgi izleme (klasik) veya aralıklı tekrar için FSRS
- Müfredat grafı: Kavramların + önkoşul kenarlarının + OER içeriğinin Neo4j'ü
- Bellek: agentmemory tarzında kalıcı vektör + epizodik + anlamsal depo
- Ses: LiveKit Agents 1.0 + Cartesia Sonic-2 (capstone 03 alt-yığınını yeniden kullanın)
- Fotoğraf-matematik: Denklem tanıma için dots.ocr veya PaliGemma 2
- Güvenlik: Llama Guard 4 + özel yaşa uygun filtre
- Değerlendirme: Bloom-düzeyli soru üretimi, ön/son test çatısı, etkinlik çalışması araçları

## Build It

1. **Müfredat grafı.** Önkoşul kenarlarıyla 50-150 kavram düğümünden (ör. K-12 cebir, "sayı doğrusu"ndan "ikinci dereceden formül"e) oluşan bir Neo4j inşa edin. Düğüm başına OER içeriği (Open Textbook, OpenStax) ekleyin.

2. **Öğrenci modeli.** Bayesyen bilgi izleme'yi (Bayesian Knowledge Tracing - BKT) önsel olasılıklarla başlatın: tahmin (guess), kayma (slip), öğrenme oranı (learn-rate). Her etkileşimden sonra kavram başına ustalığı güncelleyin. Öğrenci başına kalıcı hale getirin.

3. **Eğitmen politikası.** Düğümlerle LangGraph: `read_signal` (öğrencinin cevabı doğru mu / kısmi mi / takılı mıydı?), `select_concept` (en yüksek öncelikli kavramı seçmek için müfredat grafında yürü), `scaffold` (Sokratik istem), `update_mastery`.

4. **Bellek.** Her etkileşim epizodik depoya yazılır. Hatalar ve tercihler anlamsal belleğe terfi eder. COPPA-farkında saklama politikası: 1 yıl sonra otomatik silme, ebeveyn-erişilebilir.

5. **Ses yolu.** Eğitmen politikasına bağlı LiveKit Agents işçisi. ASR Whisper-v3-turbo aracılığıyla. TTS Cartesia Sonic-2 aracılığıyla. Barge-in desteklenir (capstone 03 mekaniklerini yeniden kullanın).

6. **Fotoğraf-matematik yolu.** Görüntü yükle veya yakala; denklemi tanımak için dots.ocr veya PaliGemma 2 çalıştır; yapılandırılmış girdi olarak eğitmene besle.

7. **Güvenlik.** Her model çıktısı Llama Guard 4'ten ve yaşa uygun bir filtreden geçer (öz-zarar, yetişkin içeriği, şiddeti engeller). Bellek erişimi öğrenci kimliğiyle kapsamlanır; silme için ebeveyn erişim yüzeyi.

8. **Etkinlik çalışması.** 10 öğrenci, ön-test (standartlaştırılmış 30-soruluk temel çizgi), iki hafta eğitmen etkileşimi (haftada 3 oturum), son-test. Aynı içerikte adaptif-olmayan bir baseline kohortu (10 öğrenci) ile karşılaştırın.

9. **Haftalık ilerleme raporları.** Öğrenci başına, keşfedilen konuların, ustalık yörüngelerinin ve önerilen sonraki adımların PDF özetini otomatik olarak oluşturun.

## Use It

```
learner: "I don't understand why 3x + 6 = 12 means x = 2"
[signal] stuck
[concept] 'isolating variables' (prerequisite: addition-subtraction-equality)
[scaffold] "what number would you subtract from both sides to start?"
learner: "6"
[signal] correct
[mastery] addition-subtraction-equality: 0.62 -> 0.77
[concept] continue 'isolating variables'
[scaffold] "great. now what is 3x / 3 equal to?"
```

#### Açıklama

Bu örnek, eğitmenin tipik bir Sokratik dönüşünü gösterir. Öğrenci 3x + 6 = 12 denkleminden x = 2 çıkarımını anlamadığını söylüyor. Sistem bunu bir "takılı" sinyali olarak sınıflandırır, mevcut kavramı "değişkenleri yalıtma" (önkoşul: toplama-çıkarma-eşitliği) olarak seçer ve yönlendirici bir soru sorar: "başlamak için her iki taraftan hangi sayıyı çıkarırdın?". Öğrenci "6" yanıtını verir; bu doğrudur. Sistem "toplama-çıkarma-eşitliği" kavramı için ustalık olasılığını 0.62'den 0.77'ye günceller, "değişkenleri yalıtma" kavramıyla devam eder ve bir sonraki adımı sorar: "3x / 3 neye eşittir?". Süreç, cevabı asla doğrudan vermeden, ipucu ipucu öğrenciyi doğru sonuca yönlendirir.

## Ship It

`outputs/skill-ai-tutor.md` teslim edilen şeydir. Çok modlu girdi, bir öğrenci modeli, bellek, güvenlik ve ölçülmüş etkinlik ile konuya özgü adaptif bir eğitmen.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Öğrenme kazancı deltası | 10 öğrenciyle iki haftalık çalışmada ön/son-test deltası |
| 20 | Sokratik sadakat | Transkript örnekleri üzerinde rubrik puanı |
| 20 | Çok modlu UX | Ses + fotoğraf + metin uçtan uca tutarlılığı |
| 20 | Güvenlik + gizlilik duruşu | Llama Guard 4 geçme oranı + COPPA-farkında saklama |
| 15 | Müfredat genişliği ve graf kalitesi | Kavram kapsamı + önkoşul grafı tutarlılığı |
| **100** | | |

## Exercises

1. Etkinlik çalışmasını adaptif öğrenci modeli olmadan (rastgele kavram sırası) çalıştırın. Deltayı raporlayın. Adaptif'in kazanmasını bekleyin, ama ilginç olan sayı boyutudur.

2. Bir çok modlu sonda ekleyin: aynı kavram sorusu metin, ses ve fotoğraf olarak teslim edilir. Öğrencilerin tercih ettikleri modlite ile daha hızlı yakınsayıp yakınsamadığını ölçün.

3. Bir ebeveyn panosu inşa edin: pratik yapılan konular, ustalık yörüngeleri, yaklaşan kavramlar, güvenlik olayları (herhangi bir guardrail isabeti). COPPA-uyumlu.

4. Bir dil-değiştirme modu ekleyin: eğitmen İspanyolca girdi kabul eder ve İspanyolca öğretir. X-Guard kapsamını ölçün.

5. Bellek gizliliğini zorlayın: öğrenci A'nın verilerini, bir ses-klibi yeniden-yükleme saldırısı (voice-clip re-ingest attack) yoluyla bile öğrenci B'nin göremediğini doğrulayın. Denenen erişimi kaydedin ve uyarı verin.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Sokratik politika | "Sor, dökme" | Eğitmen cevabı vermek yerine yönlendirici bir soru sorar |
| Bayesyen bilgi izleme | "BKT" (Bayesian Knowledge Tracing) | Kavram başına ustalık olasılığı için klasik öğrenci-model denklemleri |
| FSRS | "Ücretsiz Aralıklı Tekrar Zamanlayıcısı" (Free Spaced Repetition Scheduler) | 2024 aralıklı tekrar zamanlayıcısı, SM-2'den daha iyi |
| Müfredat grafı | "Kavram DAG'ı" (Directed Acyclic Graph) | Önkoşul kenarlarıyla kavramların Neo4j'ü |
| Epizodik bellek | "Etkileşim başına günlük" | Her etkileşim sonradan geri getirme için depolanır |
| Anlamsal bellek | "Öğrenilmiş kalıp deposu" | Epizodikten terfi eden sıkıştırılmış hatalar ve tercihler |
| COPPA | "Çocuk gizliliği yasası" (Children's Online Privacy Protection Act) | 13 yaşından küçük çocuklardan veri toplamayı kısıtlayan ABD yasası |

## Further Reading

- [Khanmigo (Khan Academy)](https://www.khanmigo.ai) — referans tüketici K-12 eğitmeni
- [Duolingo Max](https://blog.duolingo.com/duolingo-max/) — referans dil-öğrenme eğitmeni
- [Google LearnLM / Gemini for Education](https://blog.google/technology/google-deepmind/learnlm) — hosted referans model
- [Quizlet Q-Chat](https://quizlet.com) — alternatif referans
- [Synthesis Tutor](https://www.synthesis.com) — startup referans
- [FSRS algorithm](https://github.com/open-spaced-repetition/fsrs4anki) — aralıklı tekrar zamanlayıcısı
- [Bayesian Knowledge Tracing](https://en.wikipedia.org/wiki/Bayesian_knowledge_tracing) — öğrenci-modeli klasiği
- [LiveKit Agents](https://github.com/livekit/agents) — ses yığını
