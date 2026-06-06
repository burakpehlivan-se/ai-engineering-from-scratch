# vLLM Serving Internals: PagedAttention, Continuous Batching, Chunked Prefill

> vLLM'in 2026'daki hakimiyeti tek bir hileye değil, üç birleşik varsayılana dayanır. PagedAttention her zaman açıktır. Continuous batching, yeni istekleri decode iterasyonları arasında aktif batch'e enjekte eder. Chunked prefill, uzun istemleri (prompt) dilimler, böylece decode tokenları asla aç kalmaz. Üçünü de açın ve Llama 3.3 70B FP8, tek bir H100 SXM5 üzerinde 128 eşzamanlıda 2.200-2.400 tok/s iter — kabaca vLLM'in kendi varsayılanının %25 üzerinde ve naif bir PyTorch döngüsünün 3-4 katı. Bu ders, scheduler ve attention çekirdeğini diyagramlayabileceğiniz bir seviyede okur ve `code/main.py`'de vLLM'in yaptığı gibi prefill ve decode'u zamanlayan oyuncak bir continuous batcher ile biter.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak continuous batching scheduler)
**Önkoşullar:** Faz 17 · 01 (Model Sunma), Faz 11 (LLM Mühendisliği)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- PagedAttention'ı bir KV cache tahsisçisi olarak açıklayın: bloklar, blok tabloları ve parçalanmanın üretim yükünde %4'ün altında kalmasının nedeni.
- Continuous batching'i iterasyon düzeyinde diyagramlayın: biten dizilerin batch'ten nasıl çıktığı ve yenilerinin drenaj olmadan nasıl katıldığı.
- Chunked prefill'i tek bir cümlede açıklayın ve hangi gecikme metriğini koruduğunu adlandırın (ipucu: TTFT kuyruğu, ortalama verim değil).
- Her optimizasyonu aynı anda etkinleştiren ekipleri ısıran 2026 vLLM v0.18.0 tuzağını adlandırın.

## Sorun

Naif bir PyTorch sunma döngüsü bir seferde tek bir istek çalıştırır: tokenize et, prefill yap, EOS'a kadar decode et, döndür. Tek kullanıcıda bu çalışır. Yüz kullanıcıda bu sabırlı insanlardan oluşan bir kuyruktur. Belirgin düzeltme — statik batching — her isteği penceredeki en uzun isteme, her decode'u beklenen en uzun çıktıya doldurur ve tüm batch'i en yavaş dizide durdurur. Asla kullanmadığınız dolgulama için ödeme yaparsınız ve hızlı istekler yavaş olanları bekler.

vLLM aynı anda üç sorunu çözer. PagedAttention, KV cache parçalanmasının klasik sürekli tahsisin yaptığı gibi GPU belleğinin %60-80'ini yemesini durdurur. Continuous batching, isteklerin her decode iterasyonu arasında batch'e katılmasına ve batch'ten ayrılmasına izin verir, böylece batch her zaman gerçek işle doludur. Chunked prefill, 32k-token'lık bir istemi ~512-token'lık dilimlere böler ve decode ile iç içe geçirir, böylece uzun bir istem GPU üzerindeki her decode tokenını dondurmaz.

2026 üretim varsayılanı üçünün de açık olmasıdır. Her birinin ne yaptığını anlamanız gerekir çünkü hata modlarının tümü modelde değil, scheduler'dadır.

## Kavram

### PagedAttention sanal bellek sistemi olarak

Bir KV cache, dizi başına `num_layers × 2 × num_heads × head_dim × seq_len × bytes_per_element`'tir. 8192 token'da Llama 3.3 70B için bu, BF16'da dizi başına yaklaşık 1,25 GB'dir. Her istek için 8192 yeri önceden ayırırsanız ancak ortalama istek yalnızca 1500 token kullanırsa, ayırdığınız HBM'nin yaklaşık %82'sini israf edersiniz. Klasik batching bu israfı öder.

PagedAttention fikri OS sanal bellekten ödünç alır. KV cache dizi başına sürekli değildir. Sabit boyutlu bloklarda (varsayılan 16 token) tahsis edilir. Her dizinin, mantıksal token konumlarını fiziksel blok ID'lerine eşleyen bir blok tablosu vardır. Bir dizi tahsis edilen bloklarının ötesine büyüdüğünde, bir blok daha eklenir. Bittiğinde, blokları havuza döner.

Parçalanma, %60-80'den (klasik) %4'ün altına (PagedAttention) düşer. PagedAttention'ı bir bayrakla etkinleştirmezsiniz — vLLM'in gönderdiği tek tahsisçi odur. Düğme, ağırlıklar ve aktivasyonlar yüklendikten sonra vLLM'e KV blokları için ne kadar HBM ayıracağını söyleyen `--gpu-memory-utilization` (varsayılan 0,9)'dur.

### İterasyon düzeyinde continuous batching

Eski "dinamik batching" bir pencere (diyelim 10 ms) batch'i doldurması için beklerdi, sonra her dizi bitene kadar prefill + decode + decode + decode çalıştırırdı. Hızlı diziler erken ayrılır ve GPU yavaş olanları bitirirken boşta otururdu.

Continuous batching her decode adımı arasında çalışır. Çalışan diziler kümesine `RUNNING` listesi diyelim. Her iterasyonda:

1. `RUNNING`'de az önce EOS veya max_tokens'a ulaşan her dizi kaldırılır.
2. Scheduler, bekleyen kuyruğa bakar. Boş KV blokları varsa, yeni dizileri kabul eder (prefill veya devam eden).
3. Forward pass, artık `RUNNING`'de olan her şey üzerinde, dizi başına bir yeni token yayar.

Batch boyutu asla sabit bir sayıya doldurulmaz. Çıktılarının farklı konumlarındaki diziler tek bir birleşik forward'u paylaşır. 2026'da vLLM'de buna `V1 scheduler` denir. Anahtar değişmez: scheduler, istek başına değil, decode iterasyonu başına bir kez çalışır.

### Chunked prefill TTFT kuyruğunu korur

Prefill hesaplama-bağlıdır (compute-bound). Llama 3.3 70B üzerinde 32k-token'lık bir istem, tek bir H100'de ~800 ms saf prefill sürer. Prefill çalışırken, batch'teki diğer her dizinin decode tokenları bekler. Bir sunma döngüsünde, bir uzun istemin ilk-token gecikmesi (TTFT), düzinelerce diğer kullanıcının tokenlar-arası gecikmesinin (ITL) sarsıntısı haline gelir.

Chunked prefill, prefill'i sabit boyutlu parçalara (varsayılan 512 token) böler ve her parçayı bir birim olarak zamanlar. Parçalar arasında scheduler, decode dizilerini bir token ilerletebilir. Mutlak prefill gecikmesinde küçük bir artış (parça başına birkaç ms) karşılığında çok daha düşük decode-zamanı sarsıntısı alırsınız. Karışık yük altında P99 ITL, yayınlanan kıyaslamalarda ~50 ms'den ~15 ms'ye düşer.

### Üç varsayılan birbiriyle etkileşir

Üç özellik de birbirini varsayar. PagedAttention, scheduler'a takas edilecek ince-taneli bir KV kaynağı verir. Continuous batching, yeni bir dizinin kabulünün küresel bir yeniden düzenleme zorlamaması için o ince-taneli kaynağa ihtiyaç duyar. Chunked prefill, scheduler'ın aynı `RUNNING` listesinde verdiği bir karardır — ayrı bir sistem değil, bir scheduler politikasıdır.

Her bayrağı bilmeniz gerekmez. Scheduler'ın neyi optimize ettiğini bilmeniz gerekir: KV-blok bütçesi altında goodput, chunked prefill dilimlemeye tabi.

### 2026 v0.18.0 tuzağı

vLLM v0.18.0'da `--enable-chunked-prefill`'i draft-model spekülatif decode ile (`--speculative-model`) birleştiremezsiniz. Belgelenen istisna, V1 scheduler'da N-gram GPU spekülatik decode'dur. Her bayrağı okumadan açan ekipler, çalışma zamanında yumuşak bir regresyon yerine başlangıçta bir hata alır. Eğer spekülatif kazancınız chunked prefill'i etkinleştirmeye değecekse, seçimi yeniden gözden geçirin — 2026'da doğru cevap genellikle chunked prefill olmadan EAGLE-3'tür, derlenmeyen draft model artı chunked prefill değil.

### Hatırlamanız gereken sayılar

- Llama 3.3 70B FP8, H100 SXM5, 128 eşzamanlı, üçü de açık: 2.200-2.400 tok/s.
- Aynı model, varsayılan vLLM (chunked prefill yok): ~1.800 tok/s.
- Aynı model, naif PyTorch forward döngüsü: ~600 tok/s.
- Üretim yükünde PagedAttention altında KV parçalanma israfı: <%4.
- Karışık yük altında P99 ITL: chunked prefill ile ~15 ms, olmadan ~50 ms.

### Scheduler nasıl görünür

```
while True:
    finished = [s for s in RUNNING if s.is_done()]
    for s in finished: release_blocks(s); RUNNING.remove(s)

    while WAITING and have_free_blocks_for(WAITING[0]):
        s = WAITING.pop(0)
        allocate_initial_blocks(s)
        RUNNING.append(s)

    # schedule prefill chunks + decode in one batch
    batch = []
    for s in RUNNING:
        if s.in_prefill:
            batch.append(next_prefill_chunk(s))   # e.g. 512 tokens
        else:
            batch.append(decode_one_token(s))     # 1 token

    run_forward(batch)                            # one fused GPU call
```

#### Açıklama

Bu sözde kod, vLLM tarzı bir inference scheduler'ın çekirdek döngüsünü gösterir. Her iterasyonda: (1) tamamlanan dizilerin bloklarını serbest bırak ve kaldır; (2) yeterli boş KV bloğu varsa WAITING kuyruğundan yeni dizileri kabul et; (3) RUNNING listesindeki tüm dizileri (hem prefill parçaları hem tek decode tokenları) tek bir birleşik GPU forward'una paketle. Bu, sıralı istek işlemeyi dinamik, asla boş durmayan bir batch'e dönüştürür.

`code/main.py`, sahte token sayıları ve sahte forward gecikmesiyle stdlib Python'da tam olarak bu döngüdür. Çalıştırmak, chunked prefill'in uzun bir prefill sırasında decode dizilerini nasıl canlı tuttuğunu gösterir.

## Kullan

`code/main.py`, açılıp kapatılabilen özelliklerle vLLM tarzı bir scheduler simüle eder. Görmek için çalıştırın:

- `NAIVE` modu: bir seferde tek istek, batching yok.
- `STATIC` modu: doldur ve bekle, klasik batching.
- `CONTINUOUS` modu: iterasyon düzeyinde kabul ve serbest bırakma.
- `CONTINUOUS + CHUNKED` modu: prefill dilimleri decode ile iç içe.

Çıktı, toplam verimi (saniyedeki sanal token), TTFT ortalamasını ve P99 ITL'yi gösterir. `CONTINUOUS + CHUNKED` satırı karışık trafikte baskın olmalıdır.

## Üret

Bu ders `outputs/skill-vllm-scheduler-reader.md` üretir. Bir serving konfigürasyonu (batch boyutu, KV bellek kullanımı, chunked prefill boyutu, spekülatif konfigürasyon) verildiğinde, üç varsayılandan hangisinin darboğaz oluşturduğunu ve neyi ayarlamanız gerektiğini adlandıran bir scheduler tanısı üretir.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Karışık kısa ve uzun isteklerden oluşan bir iş yükünde `STATIC`'i `CONTINUOUS` ile karşılaştırın. Verim farkı nereden geliyor — prefill verimliliği, decode verimliliği veya kuyruk gecikmesi?
2. Oyuncak scheduler'a `--max-num-batched-tokens` eklemek için değiştirin. H100 üzerinde Llama 3.3 70B FP8 çalıştırmak için doğru değer nedir? (İpucu: ham HBM'nin değil, KV blok boyutu ve boş blok sayısının bir fonksiyonudur.)
3. vLLM v0.18.0 sürüm notlarını yeniden okuyun. Hangi bayrak kombinasyonları birbirini dışlıyor? Listeleyin.
4. Ortalama 1.500 çıktı token, standart sapma 600 token olan 1.000 isteklik bir iz için KV cache parçalanma israfını (a) 8192 maks'da dizi başına sürekli tahsis, (b) 16-token bloklarla PagedAttention altında hesaplayın.
5. Chunked prefill'in P99 ITL'ye neden yalnız başına verim değil, yardım ettiğini bir paragrafta açıklayın. Pratikte verim kazancı nereden geliyor?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| PagedAttention | "KV hilesi" | KV cache için sabit boyutlu blok tahsisçisi; parçalanma <%4 |
| Blok tablosu | "sayfa tablosu" | Mantıksal token konumundan fiziksel KV bloğuna dizi başına eşleme |
| Continuous batching | "dinamik batching, ama doğru" | Kabul/serbest bırakma kararları her decode iterasyonunda verilir |
| Chunked prefill | "prefill bölme" | Uzun prefill'i decode ile iç içe geçmiş 512-token dilimlerine böl |
| TTFT | "ilk token süresi" | Prefill + kuyruk + ağ; uzun istemlerde prefill baskın |
| ITL | "tokenlar-arası gecikme" | Ardışık decode tokenları arasındaki süre; batch boyutunda baskın |
| Goodput | "SLO'yu karşılayan verim" | Her isteğin hâlâ TTFT ve ITL hedeflerini karşıladığı token/sn |
| V1 scheduler | "yeni scheduler" | vLLM'in 2026 scheduler'ı; N-gram spec decode chunked-prefill-uyumlu yol |
| `--gpu-memory-utilization` | "bellek düğmesi" | Ağırlıklar ve aktivasyonlar yüklendikten sonra KV blokları için ayrılan HBM kesri |

## İleri Okuma

- [vLLM documentation — Speculative Decoding](https://docs.vllm.ai/en/latest/features/spec_decode/) — chunked-prefill ve spekülatif-decoding uyumluluğu üzerine resmi kaynak.
- [vLLM Release Notes (NVIDIA)](https://docs.nvidia.com/deeplearning/frameworks/vllm-release-notes/index.html) — 2026 sürüm temposu ve sürüme özgü davranış.
- [vLLM Blog — PagedAttention](https://blog.vllm.ai/2023/06/20/vllm.html) — tahsisçiyi nasıl düşünmemiz gerektiğini hâlâ tanımlayan orijinal yazı.
- [PagedAttention paper (arXiv:2309.06180)](https://arxiv.org/abs/2309.06180) — parçalanma analizi ve scheduler tasarımı.
- [Aleksa Gordic — Inside vLLM](https://www.aleksagordic.com/blog/vllm) — flame grafikleriyle ayrıntılı V1 scheduler yürüyüşü.
