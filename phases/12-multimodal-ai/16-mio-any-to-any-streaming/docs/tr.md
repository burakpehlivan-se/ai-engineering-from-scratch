# MIO ve Her Şeyden Her Şeye Akışlı Multimodal Modeller

> GPT-4o, çoğu açık modelin çoğaltamayacağı bir ürün sunar: sesi duyan, videoyu gören ve gerçek zamanlı olarak konuşan bir ajan. 2024 sonundaki açık ekosistem cevabı MIO'ydu (Wang ve ark., Eylül 2024). MIO metni, görüntüyü, konuşmayı ve müziği tokenize eder, iç içe geçmiş diziler üzerinde tek bir nedensel transformer eğitir ve herhangi bir modallıktan herhangi bir modallığa üretir. AnyGPT (Zhan ve ark., Şubat 2024) kanıt kavramıydı; MIO ölçek büyütme oldu; Unified-IO 2 (Allen AI, Aralık 2023) ise görme + eylem temelli (grounding) kuzenidir. Bu ders her şeyden her şeye (any-to-any) paternini okur: dört tokenizer, bir transformer, akış dostu çözümleme.

**Tür:** Öğren
**Diller:** Python (stdlib, dört-modallık token ayırıcısı + akışlı çözümleme döngüsü)
**Ön koşullar:** Faz 12 · 11 (Chameleon), Faz 6 (Speech and Audio)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Metin, görüntü, konuşma ve müzik token'larını çakışma olmadan barındıran ortak bir sözcük dağarcığı (vocabulary) tasarlayın.
- SEED-Tokenizer (görüntüler) ve SpeechTokenizer residual-VQ'sunu (konuşma) sıkıştırma + yeniden oluşturma tavizleri açısından karşılaştırın.
- Her şeyden her şeyi oluşturan dört aşamalı müfredatı açıklayın.
- Üç açık her şeyden her şeye reçetesini ve temel tavizlerini adlandırın: MIO, AnyGPT, Unified-IO 2.

## Problem

Birleşik bir multimodal model iddia etmek kolaydır ancak ölçekli olarak zordur. 2024'e kadar çoğu "her şeyden her şey" sistemi boru hattı (pipeline)ydı: görme modeli → metin temsili → konuşma modeli → ses. Her geçiş bilgi kaybeder, gecikme ekler ve eğitimi zorlaştırır. GPT-4o'nun demo videosu, saniyenin altında yanıt veren tek model alternatifini gösterdi; açık sistemler aylarca geride kaldı.

Mühendislik zorlukları:

- Tokenizer'lar her modallık için var olmalı, yeniden oluşturma için yeterince kayıpsız sıkıştırmalı ve transformer'ın tüketebileceği hızlarda token üretmeli.
- Tek bir sözcük dağarcığı, metin (32k+), görüntü (16k+), konuşma (4k+), müzik (8k+) için alan ayırmalıdır. Minimum kırk binin üzerinde giriş.
- Eğitim verisi her girdi-çıktı çiftini (text→image, image→speech, speech→image vb.) kapsamalı veya model bileşim yapabilmelidir.
- Çıkarım, konuşma gecikmesi için yeterince hızlı akışlı çıktı token'ları üretmelidir (<500ms time-to-first-audio-byte).

## Kavram

### Dört modallık için dört tokenizer

MIO'nun tokenizer yığını:

- Metin: standart BPE, sözcük dağarcığı ~32000.
- Görüntü: SEED-Tokenizer (2023) — ayrık sözcük dağarcığıyla quantize edilmiş VAE, 4096 giriş, görüntü başına 32x32 token.
- Konuşma: SpeechTokenizer residual-VQ (2023) — 16kHz dalga formunu 8 hiyerarşik sözcük dağarcığına kodlar; ilk düzey kaba içeriktir, sonraki düzeyler vurgu ve konuşmacı kimliği ekler.
- Müzik: benzer residual-VQ (Meta'nın MusicGen / Encodec ailesi), 4-8 sözcük dağarcığı.

Her modallık tamsayı token'ları üretir. Token'lar ortak sözcük dağarcığında birbirinden ayrı ID aralıklarına sahiptir:

```
text: 0..31999
image: 32000..36095 (4096 görüntü token'ı)
speech: 36096..40191 (4096 konuşma temel token'ı, artı arta kalan katmanlar)
music: 40192..48383 (8192 müzik token'ı)
sep: 48384..48390 (<image>, <speech>, <music>, </...> vb.)
```

Toplam: ~48k sözcük dağarcığı. Girdi embedding'i ve çıktı projeksiyonu bunun tamamını kapsar.

### Akışlı çözümleme

Konuşma üretimi residual-VQ kullanır. Transformer temel (katman 0) konuşma token'larını tahmin eder; paralel çözümlenmiş bir residual quantizer sonraki katmanları tahmin eder. Her katman 0 token'ı, 16kHz'de yaklaşık 50ms sese karşılık gelir.

Akışlı patern:

1. Kullanıcı mikrofona konuşur; gerçek zamanlı audio tokenizer her 50ms'de bir konuşma token'ı üretir.
2. MIO token'lar geldikçe tüketir (prompt doldurma + artımlı ileri geçiş).
3. Çıktı token'ları üretilirken akar; paralel bir konuşma decoder'ı bunları ~50-150ms gecikmeyle ses örneklerine dönüştürür.
4. Time-to-first-audio-byte: MIO makalesinde ~300-500ms, GPT-4o'nun ~250ms'ine yaklaşıyor.

Mini-Omni (arXiv:2408.16725), GLM-4-Voice (arXiv:2412.02612) ve Moshi (arXiv:2410.00037) tamamlayıcı akışlı konuşma-LLM tasarımlarıdır. Moshi özellikle tek bir GPU'da 160ms round-trip'e ulaşır.

### Dört aşamalı müfredat

MIO'nun eğitim müfredatı:

1. 1. Aşama — hizalama. Ölçekli modallık-çifti derlemleri: text-image, text-speech, text-music. Her çift kendi token sözcük dağarcığı segmentini kullanır. Ortak sözcük dağarcığını eğitir.
2. 2. Aşama — iç içe geçmiş. Çok modallıklı iç içe geçmiş belgeler (görüntü + video içeren bloglar, transkriptli podcast'ler vb.). Çapraz modallık bağlamını eğitir.
3. 3. Aşama — konuşma iyileştirmeli. Metin yeteneğini kaybetmeden konuşma kalitesini artırmak için ek ses verisi.
4. 4. Aşama — SFT. Modallıklar arası talimat ayarı: VQA, captioning, anlatım, speech-to-speech diyalog.

Bir aşamanın atlanması belirli yetenekleri bozar: 2. aşamayı atlarsanız model çapraz modallık bağlamını kaybeder; 3. aşamayı atlarsanız konuşma kötü olur.

### Zincir-görsel-düşünce (chain-of-visual-thought)

MIO, zincir-görsel-düşünceyi (chain-of-visual-thought) tanıtır: model bir çıkarım adımı olarak ara görüntü token'ları üretir. "Kedi ağaç mı tırmanıyor?" sorusu için model:

1. Sahneyi gösteren `<image>` token'ları üretir (girdi görüntüsünden veya bir eskizden).
2. Eskizi analiz eden metin üretir.
3. Son cevabı üretir.

Render edilmiş ara görüntü bir karalama kağıdı (scratchpad) olarak görev yapar. Uzamsal çıkarım görevlerinde benchmark'lar iyileşir. Fikir, metin çıkarma için zincir-düşünceyi (chain-of-thought) yansıtır.

### Her şeyden her şeyde rakipler

- AnyGPT (arXiv:2402.12226): 4 modallık (metin, görüntü, konuşma, müzik), benzer tasarım.
- Unified-IO 2 (arXiv:2312.17172): görme eylem çıktıları, derinlik, normal ekler. Daha fazla görev çeşitliliği, daha küçük ölçek.
- NExT-GPT (arXiv:2309.05519): LLM + modallığa özgü diffüzyon decoder'ları. Tek model yaklaşımı değil.
- CoDi (arXiv:2305.11846): bileşenebilir diffüzyon; ortak gizli uzay (latent) aracılığıyla her şeyden her şeye.

MIO saf token tabanlı her şeyden her şeye en yakındır. AnyGPT kavramsal atalarıdır.

### Gecikme bütçesi

Bir konuşma ürünü için her bileşenin gecikmesi önemlidir:

- Mikrofondan ses token'larına: ~50ms.
- Doldurma (audio token'ları + geçmiş): 8B modelde ~100ms.
- İlk çıktı token'ı: ~50ms.
- Paralel residual-VQ + speech decoder: ~100-150ms.

Toplam time-to-first-audio-byte: minimum ~300ms. GPT-4o ~250ms iddia ediyor. Moshi 160ms iddia ediyor. MIO/AnyGPT kamu benchmark'larında 400-600ms aralığındadır.

### Neden her şeyden her şey hâlâ zor

2026'da bile, açık her şeyden her şey modelleri kapalı modellerin iki eksende gerisindedir:

- Konuşma kalitesi. Residual-VQ tokenizer kayıplıdır; konuşma sohbet ürünleri ElevenLabs sınıfı seslerle karşılaştırıldığında mekanik duyulur.
- Çapraz modallık çıkarma. Modelden "gördüğün şey hakkında şarkı söyle" demek hâlâ saf görevlere göre daha sık başarısız olur.

Bu açık araştırma sorunlarıdır. Qwen3-Omni (Ders 12.20) 2025'teki en gelişmiş açık girişimdir.

## Kullan

`code/main.py`:

- Dört modallık sözcük dağarcığı dağılımını tanımlar ve yazdırır.
- Bir multimodal girdi listesini (metin, görüntü, ses klibi, müzik) tokenizer yönlendirici üzerinden yönlendirir.
- Metinden sese yanıt için gecikme sayımıyla akışlı çözümlemeyi simüle eder.
- encoder, doldurma ve decoder gecikmeleri verildiğinde beklenen time-to-first-audio-byte'ı hesaplar.

## Teslim Et

Bu ders `outputs/skill-any-to-any-pipeline-auditor.md` dosyasını üretir. Bir konuşma ürün özelgesi (girdi modallıkları, çıktı modallıkları, gecikme hedefi) verildiğinde, MIO ailesi tasarım kararlarını denetler ve gecikme bütçesini hesaplar.

## Alıştırmalar

1. Ürününüz konuşma girdisi kabul ediyor ve konuşma çıktısı döndürüyor. Uçtan uca gecikme bütçesi hedefi nedir? Zaman harcayan bileşenleri listele.

2. SpeechTokenizer residual-VQ 8 sözcük dağarcığı kullanır. Neden arta kalan düzeylerin paralel çözümlenmesinin gerekli olduğunu (sıralıya kıyasla) ve ne tür gecikme tasarrufu sağladığını önerin.

3. Sözcük dağarcığınız 32k metin + 4k görüntü + 4k konuşma. 8k müzik ve ~10 ayracı ekleyin. Gizli boyut 4096 ise embedding matrisi parametre maliyeti nedir?

4. Zincir-görsel-düşünce bir ara görüntü üretir. Hangi tür sorular yararlanır? Hangi tür sorular ekstra token'lardan zarar görür?

5. Moshi'yi okuyun (arXiv:2410.00037). "İç monolog" tekniğini tanımlayın ve MIO'nun zincir-görsel-düşüncesiyle karşılaştırın.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Her şeyden her şey | "Multimodal girdi/çıktı" | Metin, görüntü, konuşma ve müziği her yönde kabul eden ve üreten tek model |
| Residual-VQ | "Konuşma tokenizer yığını" | Her katmanın bilgi eklediği çok sözcük dağarcıklı tokenize etme; temel katman içerik, sonraki katmanlar vurgudur |
| SEED-Tokenizer | "Görüntü kodları" | MIO tarafından kullanılan 4096 girişli sözcük dağarcığına sahip ayrık görüntü tokenizer'ı |
| Zincir-görsel-düşünce | "Görsel karalama kağıdı" | Modelin son cevabından önce bir çıkarım adımı olarak ara görüntü üretmesi |
| Time-to-first-audio-byte | "TTFAB" | Kullanıcı sesinden ilk ses çıktısına kadar gecikme; konuşma hissi için <500ms |
| Dört aşamalı müfredat | "Eğitim reçetesi" | Hizalama → iç içe geçmiş → konuşma iyileştirmeli → SFT, bu sırayla |

## Daha Fazla Kaynak

- [Wang ve ark. — MIO (arXiv:2409.17692)](https://arxiv.org/abs/2409.17692)
- [Zhan ve ark. — AnyGPT (arXiv:2402.12226)](https://arxiv.org/abs/2402.12226)
- [Lu ve ark. — Unified-IO 2 (arXiv:2312.17172)](https://arxiv.org/abs/2312.17172)
- [Wu ve ark. — NExT-GPT (arXiv:2309.05519)](https://arxiv.org/abs/2309.05519)
- [Tang ve ark. — CoDi (arXiv:2305.11846)](https://arxiv.org/abs/2305.11846)
