# Prefix-Ağırlıklı İş Yükleri için SGLang ve RadixAttention

> SGLang, KV cache'i bir radix ağacında (radix tree) birinci sınıf, yeniden kullanılabilir bir kaynak olarak ele alır. vLLM istekleri FCFS (ilk gelen, ilk hizmet) ile zamanladığı yerde, SGLang'ın cache-farkında scheduler'ı daha uzun paylaşılan prefix'lere sahip istekleri önceliklendirir — etkili bir şekilde bir derinlik-ilk radix geçişi, böylece sıcak dallar HBM'de kalır. ShareGPT-benzeri 1K istemlerle Llama 3.1 8B üzerinde, SGLang vLLM'in ~12.500'üne karşı ~16.200 tok/s'ye ulaşır, kabaca %29'luk bir fark. Prefix-ağırlıklı RAG iş yüklerinde avantaj 6,4x'e ulaşır. Ses klonlama şeklindeki iş yüklerde cache hit oranı %86,4'ü aştı. 2026'da xAI, LinkedIn, Cursor, Oracle, GCP, Azure, AWS genelinde 400.000+ GPU üzerinde dağıtıldı. Gotcha, prefix sıralaması tutarsız olduğunda 6,4x sayısının buharlaşmasıdır — sıralama mühendisin koludur.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak radix-ağacı cache + cache-farkında scheduler)
**Önkoşullar:** Faz 17 · 04 (vLLM Serving Internals), Faz 14 (Agentic RAG)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- RadixAttention'ı şematize edin: prefix'ler radix ağacında nasıl saklanır ve KV blokları aynı daldan köklenen diziler arasında nasıl paylaşılır.
- Cache-farkında zamanlamayı açıklayın ve FCFS'nin prefix-ağırlıklı trafik için neden yanlış olduğunu belirtin.
- Bir iş yükü için, prefix-cache hit oranı ve istem uzunluğu dağılımı verildiğinde beklenen hızlanmayı hesaplayın.
- 6,4x sayısını gerçek kılan prompt-sıralama disiplininin adını verin ve kaybedilen bir potansiyele karşı adlandırın.

## Sorun

Klasik sunma, her isteğin istemini opak olarak ele alır. 5.000 RAG isteğinin tümü aynı 2.000-token'lık sistem istemi artı aynı retrieval preamble'ı ile başlasa bile, vLLM o 2.000-token'lık prefix'i 5.000 kez prefill eder. GPU aynı işi tekrar tekrar yapar.

Gözlem: agentic ve RAG iş yüklerinde istemler neredeyse her zaman uzun prefix'leri paylaşır. Sistem istemi, araç şemaları, few-shot örnekleri, retrieval başlıkları, konuşma geçmişi — tümü istekler arasında tekrarlanır. O prefix'in KV cache'ini bir kez saklayıp yeniden kullansaydınız, onu yeniden prefill etmezdiniz.

RadixAttention tam olarak bunu yapar. Tokenlar bir radix ağacında indekslenir; her düğüm, yoldan token dizisi için KV bloklarına sahiptir. Yeni bir istek ağaçta yürür: token'ları eşleşen herhangi bir düğüm, o düğümün KV bloklarını yeniden kullanır. Prefill maliyeti, tam istem yerine "yeni" sonek ile orantılı hale gelir.

Zorluk zamanlamadır. İki istek 2.000-token'lık bir prefix'i paylaşıyorsa ve üçüncüsü aynı prefix'in yalnızca 200 tokenini paylaşıyorsa, uzun prefix'i HBM'de tutmak için iki uzun-paylaşılan isteği birlikte sunmak istersiniz. FCFS bunun tersini yapar — kim önce geldiyse ona hizmet eder, potansiyel olarak bir sonraki uzun-prefix isteği gelmeden önce sıcak dalı çıkarır.

## Kavram

### Bir KV indeksi olarak radix ağacı

Bir radix ağacı (kompakt trie) token dizilerini saklar. Her düğüm bir token aralığına ve o aralık için hesaplanan KV bloklarına sahiptir. Çocuklar diziyi bir veya daha fazla token genişletir.

```
root
 |- "You are a helpful assistant..." (2,000 tokens, 124 KV blocks)
 |- "Context: <doc A>..." (500 tokens, 31 blocks)
 |- "Question: Alice..." (80 tokens, 5 blocks)
 |- "Question: Bob..." (95 tokens, 6 blocks)
 |- "Context: <doc B>..." (520 tokens, 33 blocks)
```

#### Açıklama

Bu ASCII diyagramı bir radix ağacının yapısını gösterir. Kök düğümden başlayarak her dal ortak bir token dizisini temsil eder; örneğin iki ayrı konuşma ("Alice" ve "Bob") aynı 2.500-token'lık önekini paylaşır. SGLang bu ağaçta, yeni gelen bir istek eşleşen bir dal bulduğunda o dalın KV bloklarını yeniden kullanır — yalnızca yeni token'lar için tahsis yapar.

Sistem istemi + "Context: <doc A>" + "Question: Carol" ile yeni bir istek gelir. Scheduler yürür: sistem prefix'i eşleşir (124 blok yeniden kullanılır), doc-A dalı eşleşir (31 blok yeniden kullanılır), sonra yalnızca "Question: Carol" için yeni bloklar tahsis eder (4 blok). Prefill maliyeti: 4 blok yeni token. Ağaç olmadan: 160 blok. Prefill'de ~40x tasarruf.

### Cache-farkında zamanlama

Radix-ağacı destekli yeniden kullanım, cache çalkalanırsa anlamsızdır. İki anahtar politika:

1. **Derinlik-ilk gönderim**. Kuyruktan bir sonraki isteği seçerken, mevcut çalışan kümesiyle aynı daldan köklenen istekleri tercih edin. Bu, sıcak dalı sabitler.
2. **Dal düzeyinde LRU, blok düzeyinde değil**. Tek tek bloklar yerine tüm dalları (en kısa-kullanılan yapraklardan başlayarak) çıkarın, böylece cache şekli radix şekliyle eşleşir.

FCFS ikisini de ihlal eder. 2.000 token paylaşan bir istek, 50 paylaşan bir isteğin arkasında oturur, sonra 2.000-token'lık dal, 50-token'lık olanı kabul etmek için çıkarılır.

### Ezberlemeniz gereken kıyaslama sayıları

- Llama 3.1 8B, H100, ShareGPT 1K istemler: SGLang ~16.200 tok/s vs vLLM ~12.500 (~%29 fark).
- Prefix-ağırlıklı RAG (aynı sistem + aynı belge, değişen soru): SGLang'da 6,4x'e kadar.
- Ses klonlama iş yükleri: %86,4 prefix-cache hit oranı.
- SGLang müşterilerinde üretim hit oranları: istem disiplinine bağlı olarak %50-99.
- 2026'da 400.000+ GPU üzerinde dağıtıldı.

### Sıralama gotcha'sı

6,4x sayısı tutarlı istem-şablonu sıralamasına dayanır. İstemci, istemleri bazı isteklerde `[system, tools, context, history, question]` ve diğerlerinde `[system, context, tools, history, question]` olarak oluşturursa, ağaç paylaşılan prefix'i bulamaz. Bir insan için paylaşılan prefix gibi görünen şey, radix ağacı için iki ayrı dizidir.

Mühendisin kolu: istem şablonunuz bir cache anahtarıdır. Sırayı sabitleyin. Her şeyi değişmez (sistem, araçlar, şemalar) başa koyun. Retrieval bağlamını sonra. Kullanıcı sorusunu en sona. Dinamik içeriği prefix'in içine serpiştirmeyin.

Araştırmadan gerçek vaka: dinamik içeriği cacheable prefix'ten çıkarmak, bir dağıtımı tek bir değişiklikle %7'den %74 cache hit oranına taşıdı.

### RadixAttention'ın kazandığı ve kaybettiği yerler

Kazandığı:
- RAG (aynı retrieval preamble'ı, değişen soru).
- Agent'lar (aynı araç şemaları, değişen sorgu).
- Uzun sistem istemiyle sohbet.
- Tekrarlanan preamble'ları olan ses / görüntü iş yükleri.

Kaybettiği (vLLM-düzey verime döner):
- Benzersiz istemlerle tek-çekim üretim (sistem istemi olmadan kod tamamlama, açık-uçlu sohbet).
- Her isteğin benzersiz içeriği prefix'e serpiştirdiği dinamik istemler.

### Bu neden bir çekirdek problemi değil, bir scheduler problemidir

KV yeniden kullanımını bir çekirdek hilesi olarak uygulayabilirsiniz. SGLang'ın içgörüsü, yeniden kullanımın yalnızca scheduler sıcak dalı yerinde tutarsa ödediğidir. Naif bir "mevcutsa yeniden kullan" politikası, karışık yük altında cache'i çalkalar. Radix-ağacı indeksli scheduler, çekirdek hilesini %29'luk bir üretim avantajına dönüştüren şeydir.

### vLLM ile etkileşim

İki sistem sıkı rakipler değildir. 2026'da vLLM prefix caching'i (`--enable-prefix-caching`) ve cache-farkında bir router'ı (Rust'ta vLLM Router) ekledi. Boşluk kapandı ancak tamamen kaybolmadı — SGLang'ın tüm yığını radix-ilk; vLLM onu aşılattı. Yeniden kullanımın baskın olduğu iş yükleri için SGLang varsayılan olarak kalır. Güçlü prefix örüntüleri olmadan genel-amaçlı sunma için vLLM eşit veya daha iyi kalır.

## Kullan

`code/main.py`, iki politikayla bir oyuncak radix-ağacı KV cache artı bir scheduler uygular: FCFS ve cache-farkında. Aynı iş yükünü her ikisinde çalıştırır, prefix-cache hit oranını ve verim deltasını raporlar. Sonra 6,4x çöküşünü göstermek için "karışık sıralama" iş yükü çalıştırır.

## Üret

Bu ders `outputs/skill-radix-scheduler-advisor.md` üretir. İş yükü açıklaması (istem-şablonu şekli, retrieval örüntüsü, eşzamanlı kiracı sayısı) verildiğinde, bir istem-sıralama reçetesi ve SGLang benimsenmesi için bir go/no-go üretir.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Aynı iş yükünde FCFS ve cache-farkında'yı karşılaştırın. Delta nereden geliyor — prefill tasarrufu, decode tasarrufu veya kuyruk gecikmesi?
2. İş yükünü, istemlerin `[system, tools, context]`'i rastgele permute ettiği şekilde değiştirin. Yeniden çalıştırın. Hit oranına ne olur? Neden?
3. Llama 3.1 8B üzerinde 2.000-token'lık bir sistem istemini bir radix dalı olarak yerleşik tutmanın HBM maliyetini hesaplayın. Prefix yeniden kullanımı olmadan 16-dizilik bir batch'in maliyetiyle karşılaştırın.
4. SGLang RadixAttention makalesini okuyun. Ağaç-şekilli LRU çıkarmanın, prefix-ağırlıklı yük altında blok-şekilli LRU'yu neden yendiğini üç cümlede açıklayın.
5. Bir müşteri yalnızca %8 cache hit oranı bildiriyor. Üç olası nedeni ve her biri için çalıştıracağınız tanıyı adlandırın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| RadixAttention | "SGLang şeyi" | Paylaşılan prefix'lerin blokları yeniden kullanması için KV cache'in radix ağacı olarak indekslenmesi |
| Radix ağacı | "kompakt trie" | Her düğümün bir token aralığına ve KV bloklarına sahip olduğu ağaç |
| Cache-farkında scheduler | "sıcak-dal-ilk" | Yerleşik dalı paylaşan istekleri tercih eden scheduler |
| Prefix-cache hit oranı | "isteminizin ne kadarı bedavaydı" | Yeniden kullanılan KV bloklarından sunulan istem tokenlerinin kesri |
| FCFS | "ilk gelen ilk hizmet" | Prefix yerelliğini bozan varsayılan zamanlama |
| Dal-düzeyi LRU | "yaprağı çıkar" | Radix şekliyle eşleşen çıkarma politikası |
| İstem şablonu sıralaması | "cache anahtarı" | İstemin bileşen sırası, ağacın neyi paylaşabileceğini belirler |
| Sistem istemi sabitleme | "yerleşik prefix" | Değişmez sistem kısmını çıkarma çalkantısından kaçınmak için sabitleyin |

## İleri Okuma

- [SGLang GitHub](https://github.com/sgl-project/sglang) — kaynak ve dokümanlar.
- [SGLang documentation](https://sgl-project.github.io/) — RadixAttention ve zamanlama ayrıntıları.
- [SGLang paper — Efficiently Programming Large Language Models (arXiv:2312.07104)](https://arxiv.org/abs/2312.07104) — tasarım referansı.
- [LMSYS blog — SGLang with RadixAttention](https://www.lmsys.org/blog/2024-01-17-sglang/) — kıyaslama sayıları ve scheduler gerekçesi.
- [vLLM — Prefix Caching](https://docs.vllm.ai/en/latest/features/prefix_caching.html) — karşılaştırma için vLLM'in kendi radix-benzeri uygulaması.
