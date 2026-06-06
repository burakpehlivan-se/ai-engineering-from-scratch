---
name: prompt-gpt-architecture-analyzer
description: Herhangi bir GPT tarzı transformer modelindeki mimari seçimleri analiz edin
version: 1.0.0
phase: 10
lesson: 4
tags: [gpt, transformer, architecture, attention, kv-cache, scaling, pre-training]
---

# GPT Mimari Analizcisi

Bir teknik rapor, model kartı veya eğitim günlüğünden GPT tarzı bir modeli değerlendirirken, mimariyi parçalara ayırmak ve tasarım ödünleşimlerini belirlemek için bu çerçeveyi kullanın.

## Analiz Protokolü

### 1. Parametre Tahsisi Dağılımı

Her bileşen için tam parametre sayısını hesaplayın:

- **Token embedding'leri**: vocab_size x embed_dim
- **Konum embedding'leri**: max_seq_len x embed_dim
- **Blok başına attention**: 4 x embed_dim x embed_dim (Q, K, V, çıktı projeksiyonları)
- **Blok başına FFN (Feed-Forward Network)**: 2 x embed_dim x ff_dim + embed_dim + ff_dim (iki doğrusal katman + sapmalar)
- **Blok başına LayerNorm**: 4 x embed_dim (iki norm, her biri ölçek + sapma)
- **Son LayerNorm**: 2 x embed_dim
- **Çıktı kafası (output head)**: vocab_size x embed_dim (token embedding'leri ile ağırlık paylaşılmıyorsa 0)

Herhangi bir tek bileşen toplam parametrelerin %40'ını aşarsa işaretleyin. Embedding matrisi küçük modellerde baskındır. Attention ve FFN büyük modellerde baskındır.

### 2. Attention Tasarımı Analizi

Attention yapılandırmasını değerlendirin:

- **Kafa (head) boyutu**: embed_dim / num_heads. Standart 64 (GPT-2) veya 128 (Llama 3). 32'nin altı, kafa başına ifade gücünü sınırlar. 128'in üzeri, az faydayla birlikte hesaplamayı israf eder.
- **Katman başına kafa sayısı**: Daha fazla kafa = daha çeşitli attention kalıpları, ancak KV cache için daha fazla bellek.
- **Gruplanmış Sorgu Attention'ı (GQA)**: Model, K/V kafalarını birden fazla Q kafası arasında paylaşıyor mu? Llama 3, 32 Q kafası için 8 KV kafasıyla GQA kullanır. Bu, KV cache'i 4 kat azaltır.
- **Bağlam uzunluğu**: Maksimum konum embedding'leri. RoPE, eğitim uzunluğunun ötesine çıkarıma (extrapolation) izin verir. Mutlak konum embedding'leri vermez.

### 3. Bellek Bütçesi

Modelin maksimum bağlam uzunluğunda çıkarım için:

- **Ağırlıklar (FP16)**: total_params x 2 bayt
- **KV Cache (FP16)**: 2 x num_layers x num_kv_heads x head_dim x max_seq_len x 2 bayt
- **Aktivasyonlar**: batch_size x seq_len x embed_dim x 2 bayt x num_layers (yaklaşık)

KV cache ağırlık belleğini aşarsa işaretleyin. Bu, uzun bağlam modellerinde (128K+) olur ve modelin kod çözme (decode) sırasında bellek bağımlı (memory-bound) olduğunu gösterir.

### 4. Hesaplama Profili

- **Token başına ön dolgu (prefill) FLOPS'ı**: yaklaşık 2 x total_params (parametre başına bir matmul, ileri geçiş)
- **Token başına kod çözme (decode) FLOPS'ı**: ön dolgu ile aynı, ancak tek bir token üzerinde
- **Ön dolgu darboğazı**: hesaplama bağımlı (GPU TFLOPS)
- **Kod çözme darboğazı**: bellek bağımlı (GPU bellek bant genişliği)
- **Aritmetik yoğunluk**: Erişilen belleğin baytı başına FLOPS. 100'ün altı = bellek bağımlı.

### 5. Ölçeklendirme Kararları

Bilinen ölçeklendirme yasalarına göre değerlendirin:

- **Chinchilla optimali**: Belirli bir hesaplama bütçesi C için, optimal model boyutu N ve token sayısı D, N ~ D ilişkisini sağlar (kabaca eşit ölçeklendirme). 7B'lık bir model ~140B token'a ihtiyaç duyar.
- **Llama 3 aşırı eğitimli**: Meta, Llama 3 8B'yi 15T token üzerinde eğitti (Chinchilla optimalinin 100 katı). Küçük modelleri daha fazla veri üzerinde aşırı eğitmek, token başına daha iyi çıkarım maliyeti üretir.
- **Genişlik vs derinlik**: Aynı parametre sayısı için daha derin modeller (daha fazla katman), daha geniş modellerden (daha büyük embed_dim) genel olarak daha örnek verimlidir.

## Kırmızı Bayraklar

- **FFN oranı 4x değil**: Standart, ff_dim = 4 x embed_dim'dir. Llama, SwiGLU ile 8/3 x embed_dim kullanır. Sapmalar gerekçelendirilmelidir.
- **Ağırlık eşlemesi (weight tying) yok**: Çıktı kafası, vocab_size embed_dim'e göre çok büyük olmadıkça token embedding'leri ile ağırlık paylaşmalıdır.
- **13B üzerinde GQA yok**: Gruplanmış sorgu attention'ı olmayan 13B üzerindeki modeller, aşırı büyük KV cache'lere sahip olacaktır.
- **Uzun bağlam için RoPE yok**: Mutlak konum embedding'leri, eğitim uzunluğunun ötesine çıkarım yapmaz. 32K+ bağlam hedefleyen modeller rotary embedding'ler kullanmalıdır.
- **Model boyutu için çok yüksek öğrenme oranı**: Daha büyük modeller daha düşük pik öğrenme oranlarına ihtiyaç duyar. GPT-2 Small 6e-4 kullanır. Llama 3 405B 8e-5 kullanır.

## Çıktı Formatı

1. **Parametre Tablosu**: Yüzdeli bileşen-bileşen parametre sayıları
2. **Bellek Bütçesi**: Maksimum bağlam uzunluğunda ağırlıklar, KV cache ve aktivasyon belleği
3. **Hesaplama Profili**: A100/H100 için ön dolgu ve kod çözme verim tahminleri
4. **Tasarım Değerlendirmesi**: Modelin doğru yaptığı şeyler ve standart dışı olan şeyler
5. **Ölçeklendirme Kararı**: Modelin eğitim verisi için uygun şekilde boyutlandırılıp boyutlandırılmadığı
