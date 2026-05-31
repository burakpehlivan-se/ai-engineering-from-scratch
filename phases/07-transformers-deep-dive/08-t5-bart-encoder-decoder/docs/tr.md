# T5, BART — Encoder-Decoder Modelleri

> Encoder'lar anlar. Decoder'lar üretir. Onları tekrar bir araya getirdiğinizde, girdi → çıktı görevleri için oluşturulmuş bir model elde edersiniz: çevirin, özetleyin, yeniden yazın, transkribe edin.

**Tür:** Öğren
**Diller:** Python
**Önkoşullar:** Faz 7 · 05 (Tam Transformer), Faz 7 · 06 (BERT), Faz 7 · 07 (GPT)
**Süre:** ~45 dakika

## Sorun

Sadece-decoder GPT ve sadece encoder BERT, 2017 mimarisini her biri farklı bir hedef için soyundurmuştur. Ancak birçok görev doğası gereği girdi-çıktı şeklindedir:

- Çeviri: İngilizce → Fransızca.
- Özetleme: 5.000 token'lık makale → 200 token'lık özet.
- Konuşma tanıma: ses token'ları → metin token'ları.
- Yapılandırılmış çıkarma: düz metin → JSON.

Bunlar için encoder-decoder en temiz eşleşmeyi sağlar. Encoder kaynağın yoğun bir temsilini (dense representation) üretir. Decoder çıktıyı, her adımda bu temsile çapraz-dikkat (cross-attention) uygulayarak üretir. Eğitim, çıktı tarafında bir kaydırma ile yapılır. GPT ile aynı kayıp, sadece encoder çıktısına koşullu.

İki makale modern oyun kitabını belirledi:

1. **T5** (Raffel ve diğerleri, 2019). "Metin-metne Dönüştüren Transformer (Text-to-Text Transfer Transformer)." Her NLP görevi metin-girdi, metin-çıktı olarak yeniden çerçevelendi. Tek mimari, tek sözlük, tek kayıp. Maskeli aralık tahmini (span prediction) üzerinde ön-eğitildi (girdide aralıkları bozun, çıktıda onları çözümleyin).
2. **BART** (Lewis ve diğerleri, 2019). "Çift Yönlü ve Otonom Dönüştürücü (Bidirectional and Auto-Regressive Transformer)." Gürültülü oto-kodlayıcı (denoising autoencoder): girdiyi birden fazla yolla bozun (karıştırma, maskeleme, silme, döndürme), orijinali yeniden oluşturma için decoder'a sorun.

2026'da encoder-decoder biçimi, girdi yapısının önemli olduğu yerlerde varlığını sürdürür:

- Whisper (ses → metin).
- Google'ın çeviri yığını.
- Farklı bağlam-anda-düzenleme yapılarına sahip bazı kod tamir modelleri.
- Flan-T5 ve varyantları, yapılandırılmış muhakeme görevleri için.

Sadece-decoder-spotlight'ı kazandı, ancak encoder-decoder hiç gitmedi.

## Kavram

![Çapraz-dikkatli encoder-decoder](../assets/encoder-decoder.svg)

### İleriye doğru döngü

```
kaynak token'ları ─▶ encoder ─▶ (N_src, d_model)  ──┐
                                                     │
hedef token'ları ─▶ decoder bloğu                    │
                 ├─▶ maskelenmiş self-attention       │
                 ├─▶ çapraz-dikkat ◀─────────────────┘
                 └─▶ FFN
                ↓
              bir sonraki token logit'leri
```

#### Açıklama
Önemli olan, encoder'ın girdi başına bir kez çalışmasıdır. Decoder otonom olarak çalışır ancak her adımda *aynı* encoder çıktısına çapraz-dikkat uygular. Encoder çıktısını önbelleğe almak, uzun girdiler için ücretsiz bir hız kazancıdır.

### T5 ön-eğitimi — aralık bozulması (span corruption)

Girdide rastgele aralıklar seçin (ortalama 3 token, toplam %15). Her aralığı benzersiz bir bekleyen (sentinel) ile değiştirin: `<extra_id_0>`, `<extra_id_1>`, vb. Decoder yalnızca bekleyen ön ekli bozulmuş aralıkları çıktı olarak verir:

```
source: The quick <extra_id_0> fox jumps <extra_id_1> dog
target: <extra_id_0> brown <extra_id_1> over the lazy
```

#### Açıklama
Bu, tüm diziyi tahmin etmekten daha ucuz bir sinyaldir. T5 makalesinin ablasyonunda MLM (BERT) ve ön-ek-LM (UniLM) ile rekabetçidir.

### BART ön-eğitimi — çoklu gürültü ile giderme

Beş gürültü işlevi dener:

1. Token maskeleme.
2. Token silme.
3. Metin doldurma (text infilling) — bir aralığı maskeler, decoder doğru uzunluğu ekler.
4. Cümle permütasyonu.
5. Belge döndürme.

Metin doldurma + cümle permütasyonunu birleştirme en iyi downstream sonuçlarını verdi. Decoder her zaman orijinali yeniden oluşturur. BART'ın çıktısı yalnızca bozulmuş aralıklar değil tüm dizi olduğu için, ön-eğitim hesaplama maliyeti T5'ten daha yüksektir.

### Çıkarım

GPT ile aynı otonom üretim. Açgözlü / ışın / top-p örnelemesi uygulanır. Işın araması (width 4–5), çıktı dağılımı sohbetkinden daha dar olduğu için çeviri ve özetleme için standarttır.

### 2026'da her bir varyant ne zaman seçilir

| Görev | Encoder-decoder mi? | Neden |
|------|------------------|-----|
| Çeviri | Evet, genellikle | Net kaynak dizisi; sabit çıktı dağıtımı; ışın araması çalışır |
| Sesten metne | Evet (Whisper) | Girdi modallığı çıktıdan farklı; encoder ses özelliklerini şekillendirir |
| Sohbet / muhakeme | Hayır, sadece-decoder | Kalıcı "girdi" yok — konuşma dizidir |
| Kod tamamlama | Genellikle hayır | Uzun bağlam ile sadece-decoder kazanır; Qwen 2.5 Coder gibi kod modelleri sadece-decoder'dır |
| Özetleme | İkisi de olur | BART, PEGASUS önceki sadece-decoder temel çizgilerini geçti; modern sadece-decoder LLM'ler onlara eşit |
| Yapılandırılmış çıkarma | İkisi de | T5 temizdir çünkü "metin → metin" her çıktı biçimini özümsedir |

~2022'den beri eğilim: sadece-decoder, encoder-decoder'ın sahip olduğu görevleri devralır çünkü (a) eğitilmiş (instruction-tuned) sadece-decoder LLM'ler her şeyi istemlerle (prompting) genelleştirir, (b) tek mimari iki mimariden daha kolay ölçeklenir, (c) RLHF bir decoder varsayar. Encoder-decoder, girdi modallığı farklı olduğu yerlerde (ses, görüntüler) veya ışın araması kalitesinin önemli olduğu yerlerde hayatta kalır.

## İnşa Et

`code/main.py`'ye bakın. Küçük bir metin kümesi için T5 tarzı aralık bozulması uyguluyoruz — bu dersteki en faydalı tek parça çünkü o zamandan beri her encoder-decoder ön-eğitim tarifinde ortaya çıkıyor.

### Adım 1: aralık bozulması

```python
def corrupt_spans(tokens, mask_rate=0.15, mean_span=3.0, rng=None):
    """Pick spans summing to ~mask_rate of tokens. Return (corrupted_input, target)."""
    n = len(tokens)
    n_mask = max(1, int(n * mask_rate))
    n_spans = max(1, int(round(n_mask / mean_span)))
    ...
```

#### Açıklama
Bu fonksiyon, token'ların yaklaşık %15'ini bozar. Hedef biçimi T5 kuralına göredir: `<sent0> span0 <sent1> span1 ...`. Bozulmuş girdi, değişmemiş token'ları aralık konumlarındaki bekleyen token'larla harmanlar.

Hedef biçimi T5 kuralıdır: `<sent0> span0 <sent1> span1 ...`. Bozulmuş girdi, değişmemiş token'ları aralık konumlarındaki bekleyen token'larla harmanlar.

### Adım 2: geri dönüş doğrulaması

Bozulmuş girdi ve hedef verildiğinde, orijinal cümleyi yeniden oluşturun. Bozumanız geri alınabilirse, ileriye doğru geçiş iyi tanımlıdır. Bu bir doğrulama kontrolüdür — gerçek eğitim bunu asla yapmaz, ancak test ucuzdur ve aralık kitapçılığındaki bir eksik hatalarını (off-by-one bugs) yakalar.

### Adım 3: BART gürültülendirme

Beş işlev: `token_mask`, `token_delete`, `text_infill`, `sentence_permute`, `document_rotate`. İkisini birleştirin ve sonucu gösterin.

## Kullan

HuggingFace referansı:

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer
tok = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

inputs = tok("translate English to French: Attention is all you need.", return_tensors="pt")
out = model.generate(**inputs, max_new_tokens=32)
print(tok.decode(out[0], skip_special_tokens=True))
```

#### Açıklama
T5 numarası: görev adı girdi metnine girer. Aynı model düzinelerce görevi işler çünkü her görev metin-girdi, metin-çıktıdır. 2026'da bu kalıp, eğitilmiş sadece-decoder modelleri tarafından genelleştirildi, ancak T5 bunu ilk kez kodladı.

## Teslim Et

`outputs/skill-seq2seq-picker.md`'ye bakın. Bu beceri, girdi-çıktı yapısı, gecikme ve kalite hedefleri verildiğinde encoder-decoder ile sadece-decoder arasında seçim yapar.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın, 30 token'lık bir cümleye aralık bozulması uygulayın, bekleyen-dışı kaynak token'larının çözümlenmiş hedef aralıklarıyla birleştirilmesinin orijinali yeniden ürettiğini doğrulayın.
2. **Orta.** BART'ın `text_infill` gürültüsünü uygulayın: rastgele aralıkları tek bir `<mask>` token'ı ile değiştirin ve decoder doğru aralık uzunluğunu artı içeriği çıkarmalıdır. Bir örnek gösterin.
3. **Zor.** `flan-t5-small`'ı küçük bir İngilizce → pig-Latin corpus'u üzerinde inceltin (200 çift). 50 çiftlik test seti üzerinde BLEU ölçün. Aynı hesaplamada aynı veri üzerinde `Llama-3.2-1B` inceltmesiyle karşılaştırın.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Encoder-decoder | "Seq2seq transformer" | İki yığın: girdi için çift yönlü encoder, çıktı için çapraz-dikkatli nedensel decoder. |
| Çapraz-dikkat (Cross-attention) | "Kaynak hedefle nerede konuşur" | Decoder'ın Q × encoder'ın K/V. Encoder bilgisinin decoder'a girdiği tek yer. |
| Aralık bozulması (Span corruption) | "T5'in ön-eğitim hilesi" | Rastgele aralıkları bekleyen token'larla değiştir; decoder aralıkları çıktı olarak verir. |
| Giderme amacı (Denoising objective) | "BART'ın oyunu" | Girdiye bir gürültü işlevi uygula, temiz diziyi yeniden oluşturma için decoder'ı eğit. |
| Bekleyen token (Sentinel token) | "`<extra_id_N>` yer tutucusu" | Kaynakta bozulmuş aralıkları etiketleyen ve hedefte yeniden etiketleyen özel token'lar. |
| Flan | "Eğitilmiş T5" | 1.800'den fazla görevde inceltilmiş T5; encoder-decoder'ı talimat izlemede rekabetçi yaptı. |
| Işın araması (Beam search) | "Çözümleme stratejisi" | Her adımda en iyi k kısmi diziyi koru; çeviri/özetleme için standarttır. |
| Öğretmen zorlaması (Teacher forcing) | "Eğitim-zamanı girdisi" | Eğitim sırasında, örnekleneni değil gerçek bir önceki çıktı token'ını decoder'a besle. |

## İleri Okuma

- [Raffel ve diğerleri (2019). Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer](https://arxiv.org/abs/1910.10683) — T5.
- [Lewis ve diğerleri (2019). BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension](https://arxiv.org/abs/1910.13461) — BART.
- [Chung ve diğerleri (2022). Scaling Instruction-Finetuned Language Models](https://arxiv.org/abs/2210.11416) — Flan-T5.
- [Radford ve diğerleri (2022). Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356) — Whisper, kanonik 2026 encoder-decoder.
- [HuggingFace `modeling_t5.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/t5/modeling_t5.py) — referans uygulaması.
