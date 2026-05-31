# BERT — Maskeli Dil Modelleme (Masked Language Modeling)

> GPT bir sonraki kelimeyi tahmin eder. BERT eksik bir kelimeyi tahmin eder. Bir cümle fark — ve gömme (embedding) biçimindeki her şeyin yarısı.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 05 (Tam Transformer), Faz 5 · 02 (Metin Temsili)
**Süre:** ~45 dakika

## Sorun

2018'de her NLP görevi — duygu analizi, isim varlığı tanıma (NER), soru cevaplama (QA), çıkarsama (entailment) — kendi etiketli verisiyle sıfırdan kendi modelini eğitiyordu. İncelenebilecek önceden eğitilmiş "İngilizce anlayan" bir kontrol noktası yoktu. ELMo (2018), önişlemeli gömmeleri (contextual embeddings) çift yönlü bir LSTM ile eğitebileceğinizi gösterdi; yardım etti ancak genellemedi.

BERT (Devlin ve diğerleri, 2018) şunu sordu: ya bir transformer encoder alıp, internet'teki her cümlede eğitip, her iki taraftaki bağlamdan eksik kelimeleri tahmin etmeye zorlasaydık? Ardından downstream göreviniz için bir kafa eğitirsiniz. Parametre verimliliği devrim niteliğindeydi.

Sonuç: 18 ay içinde BERT ve varyantları (RoBERTa, ALBERT, ELECTRA) mevcut her NLP sıralama tablosuna egemen oldu. 2020'ye kadar dünyadaki her arama motoru, içerik denetimi hattı ve anlamsal arama sisteminin içinde bir BERT vardı.

2026'da sadece encoder modelleri hala sınıflandırma, getirme ve yapılandırılmış çıkarma için doğru araçtır — token başına decoder'lardan 5-10× daha hızlı çalışırlar ve gömmeleri modern her getirme yığınının omurgasıdır. ModernBERT (Aralık 2024) mimariyi Flash Attention + RoPE + GeGLU ile 8K bağlam uzunluğuna kadar itti.

## Kavram

![Maskeli dil modelleme: token'ları seç, maskeleri uygula, orijinallerini tahmin et](../assets/bert-mlm.svg)

### Eğitim sinyali

Bir cümle alın: `the quick brown fox jumps over the lazy dog`.

Token'ların %15'ini rastgele maskeler:

```
input:  the [MASK] brown fox jumps [MASK] the lazy dog
target: the  quick brown fox jumps  over  the lazy dog
```

#### Açıklama
Model, maskeli konumlardaki orijinal token'ları tahmin etmeye eğitilir. Encoder çift yönlü olduğu için, 1. konumda `[MASK]`'ı tahmin etmek 2+. konumlardaki `brown fox jumps`'u kullanabilir. Bu, GPT'nin yapamadığı şeydir.

### BERT maske kuralları

Tahmin için seçilen token'ların %15'inden:

- %80'i `[MASK]` ile değiştirilir.
- %10'u rastgele bir token ile değiştirilir.
- %10'u değiştirilmez.

Neden her zaman `[MASK]` değil? Çünkü `[MASK]` çıkarım (inference) sırasında hiç görünmez. Modelin maskeli konumların %100'ünde `[MASK]` beklemesi için eğitilmesi, ön-eğitim (pretraining) ve inceltme (fine-tuning) arasında dağılım kayması (distribution shift) yaratırdı. %10 rastgele + %10 değiştirilmez, modeli dürüst tutar.

### Sonraki Cümle Tahmini (NSP) — ve neden bırakıldı

Orijinal BERT ayrıca NSP üzerinde eğitildi: iki cümle A ve B verildiğinde, B'nin A'yı izleyip izlemediğini tahmin etme. RoBERTa (2019) bunu ablasyonla test etti ve NSP'nin yardımcı değil zararlı olduğunu gösterdi. Modern encoder'lar bunu atlıyor.

### 2026'da ne değişti: ModernBERT

2024 ModernBERT makalesi bloğu 2026 primitifleriyle yeniden inşa etti:

| Bileşen | Orijinal BERT (2018) | ModernBERT (2024) |
|-----------|----------------------|-------------------|
| Konumsal | Öğrenilmiş mutlak | RoPE |
| Aktivasyon | GELU | GeGLU |
| Normalizasyon | LayerNorm | Ön-normalizasyon RMSNorm |
| Dikkat | Tam yoğun | Alternatif yerel (128) + küresel |
| Bağlam uzunluğu | 512 | 8192 |
| Tokenizer | WordPiece | BPE |

Ve 2018 yığınından farklı olarak, Flash Attention-native'dir. Dizi uzunluğu 8K'da DeBERTa-v3'ten 2-3× daha hızlı çıkarım yapar ve daha iyi GLUE puanlarına sahiptir.

### 2026'da hala encoder seçen kullanım alanları

| Görev | Neden encoder decoder'dan iyidir |
|------|---------------------------|
| Getirme / anlamsal arama gömmeleri | Çift yönlü bağlam = token başına daha iyi gömme kalitesi |
| Sınıflandırma (duygu, niyet, toksisite) | Tek ileriye doğru geçiş; üretim overhead'i yok |
| NER / token etiketleme | Konum bazlı çıktı, doğal olarak çift yönlü |
| Sıfır-atımlık çıkarsama (NLI) | Encoder üzerinde sınıflandırıcı kafası |
| RAG için yeniden sıralayıcı (Reranker) | Çapraz-encoder puanlama, LLM yeniden sıralayıcılarından 10× daha hızlı |

## İnşa Et

### Adım 1: maskeleme mantığı

`code/main.py`'ye bakın. `create_mlm_batch` fonksiyonu bir token ID listesi, sözlük boyutu ve olasılık parametresi alır. Maskeler uygulanmış girdi ID'leri (sadece maskeli konumlarda, diğer yerlerde -100 — PyTorch'un yok sayma dizin kuralı) ve etiketler döndürür.

```python
def create_mlm_batch(tokens, vocab_size, mask_prob=0.15, rng=None):
    input_ids = list(tokens)
    labels = [-100] * len(tokens)
    for i, t in enumerate(tokens):
        if rng.random() < mask_prob:
            labels[i] = t
            r = rng.random()
            if r < 0.8:
                input_ids[i] = MASK_ID
            elif r < 0.9:
                input_ids[i] = rng.randrange(vocab_size)
            # else: keep original
    return input_ids, labels
```

#### Açıklama
Bu fonksiyon, %15 olasılıkla token'ları maskeler. Maskelenen token'ların %80'i [MASK] ile, %10'u rastgele bir token ile, %10'u ise değiştirilmeden bırakılır. Bu dağılım, modelin çıkarma sırasında [MASK] token'ı görmemesini telafi eder.

### Adım 2: küçük bir metin üzerinde MLM tahmini çalıştırın

20 kelimelik bir sözlükte, 200 cümlede 2 katmanlı encoder + MLM kafası eğitin. Gradyan yok — ileriye doğru geçiş doğrulamaları yapıyoruz. Tam eğitim için PyTorch gerekir.

### Adım 3: maske türlerini karşılaştırın

Üç yönlü kuralın modeli `[MASK]` olmadan nasıl kullanılabilir tuttuğunu gösterin. Masksız bir cümlede ve maskeli bir cümlede tahmin edin. Her ikisi de makul token dağılımları üretmelidir çünkü model eğitimde her iki kalıbı görmüştür.

### Adım 4: ince ayar kafası (fine-tune head)

MLM kafasını küçük bir duygu veri kümesinde sınıflandırma kafasıyla değiştirin. Sadece kafa eğitilir; encoder donmuşdur. Bu, her BERT uygulamasının izlediği kalıptır.

## Kullan

```python
from transformers import AutoModel, AutoTokenizer

tok = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
model = AutoModel.from_pretrained("answerdotai/ModernBERT-base")

text = "Attention is all you need."
inputs = tok(text, return_tensors="pt")
out = model(**inputs).last_hidden_state   # (1, N, 768)
```

#### Açıklama
ModernBERT, 2024 itibarıyla çift yönlü bağlam gömmeleri için en iyi encoder modelidir. 8K bağlam uzunluğuna sahiptir.

**Gömme modelleri incelenmiş BERT'lerdir.** `sentence-transformers` modelleri, karşılaştırma kaybıyla (contrastive loss) eğitilmiş BERT'lerdir. Encoder aynıdır. Kayıp değişmiştir.

**Çapraz-encoder yeniden sıralayıcıları da incelenmiş BERT'lerdir.** `[CLS] query [SEP] doc [SEP]` üzerinde çift-sınıflandırma. Sorgu ve belge arasındaki çift yönlü dikkat, çapraz-encoder'lara çift-encoder'lara karşı kalite avantajını sağlayan şeyin ta kendisidir.

**2026'da BERT'i ne zaman seçmemelisiniz.** Üretim (generative) olan her şey. Encoder'ın otonom olarak (autoregressively) token üretmesi için mantıklı bir yolu yoktur. Ayrıca: 1B'nin altındaki her şey — küçük bir decoder daha esneklikle aynı kaliteyi yakalayabilir (Phi-3-Mini, Qwen2-1.5B).

## Teslim Et

`outputs/skill-bert-finetuner.md`'ye bakın. Bu beceri, yeni bir sınıflandırma veya çıkarma görevi için BERT inceltmesi (omurga seçimi, kafa specification'ı, veri, değerlendirme, durdurma) kapsamlarını belirler.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın ve 10,000 token üzerindeki maske dağılımını yazdırın. ~%15'inin seçildiğini ve bunların ~%80'inin `[MASK]` haline geldiğini doğrulayın.
2. **Orta.** Bütün kelime maskelemesini (whole-word masking) uygulayın: bir kelime alt-kelime tokenize edilmişse, tüm alt-kelimeleleri birlikte veya hiçbiri masksiz bırakın. Bunun 500 cümlelik bir metin kümesinde MLM doğruluğunu iyileştirip iyileştirmediğini ölçün.
3. **Zor.** Herkese açık bir veri kümesinden 10,00re cümle üzerinde küçük bir (2 katman, d=64) BERT eğitin. SST-2 duygu analizi için `[CLS]` token'ını inceltin. Eşleşen parametrelerde sadece-decoder bir temel çizgiyle (baseline) karşılaştırın — hangisi kazanır?

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| MLM | "Maskeli dil modelleme" | Eğitim sinyali: token'ların %15'ini rastgele `[MASK]` ile değiştir, orijinallerini tahmin et. |
| Çift yönlü (Bidirectional) | "Her iki yöne bakar" | Encoder dikkatında nedensel maske (causal mask) yoktur — her konum diğer her konumu görür. |
| `[CLS]` | " havuzlayıcı token" | Her dizinin başına eklenen özel token; son gömmesi cümle düzeyinde temsil olarak kullanılır. |
| `[SEP]` | "Bölüm ayırıcı" | Eşleştirilmiş dizileri (ör. sorgu/belge, cümle A/B) ayırır. |
| NSP | "Sonraki cümle tahmini" | BERT'in ikincil ön-eğitim görevi; RoBERTa'da işe yaramaz olduğu gösterildi, 2019'dan sonra bırakıldı. |
| İnceltme (Fine-tuning) | "Bir göreve uyarla" | Encoder'ı çoğunlukla donmuş tutun; downstream görev için üstte küçük bir kafa eğitin. |
| Çapraz-encoder | "Yeniden sıralayıcı" | Hem sorguyu hem belgeyi girdi olarak alan, ilgililik puanı üreten bir BERT. |
| ModernBERT | "2024 yenilemesi" | RoPE, RMSNorm, GeGLU, alternatif yerel/küresel dikkat, 8K bağlam ile yeniden inşa edilmiş encoder. |

## İleri Okuma

- [Devlin ve diğerleri (2018). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) — orijinal makale.
- [Liu ve diğerleri (2019). RoBERTa: A Robustly Optimized BERT Pretraining Approach](https://arxiv.org/abs/1907.11692) — BERT'i doğru nasıl eğitilir; NSP'yi öldürür.
- [Clark ve diğerleri (2020). ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators](https://arxiv.org/abs/2003.10555) — değiştirilmiş-token tespiti, eşleşen hesaplamada MLM'yi geçer.
- [Warner ve diğerleri (2024). Smarter, Better, Faster, Longer: A Modern Bidirectional Encoder](https://arxiv.org/abs/2412.13663) — ModernBERT makalesi.
- [HuggingFace `modeling_bert.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/bert/modeling_bert.py) — kanonik encoder referansı.
