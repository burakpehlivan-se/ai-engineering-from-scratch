# Flamingo ve Few-Shot VLM'ler için Kapılı Çapraz-Dikkat

> DeepMind'ın Flamingo'su (2022) herkesten önce iki şey yaptı. Tek bir modelin rastgele aralıklı (interleaved) görüntü, video ve metin dizilerini işleyebileceğini gösterdi. Ve VLM'lerin bağlam-içi (in-context) öğrenebileceğini gösterdi — üç örnek (görüntü, açıklama) çifti içeren bir few-shot istemi verin ve model herhangi bir gradyan adımı yapmadan yeni bir görüntünün açıklamasını yapsın. Mekanizma: kapılı çapraz-dikkat katmanları (gated cross-attention), donmuş LLM'in mevcut katmanları arasına yerleştirilir, sıfırla başlatılan öğrenilmiş bir tanh kapısı sayesinde LLM'in metin yeteneği başlangıçta korunur. Bu ders Flamingo'nun Perceiver yeniden örnekleme ve kapılı çapraz-dikkat mimarisini inceler — Gemini'nin aralıklı girdilerinin ve Idefics2'nin görsel token'larının atası.

**Tür:** Öğren
**Diller:** Python (stdlib, kapılı çapraz-dikkat + Perceiver yeniden örnekleme demosu)
**Önkoşullar:** Faz 12 · 03 (BLIP-2 Q-Former)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Kapılı çapraz-dikkatin donmuş bir LLM'in metin yeteneğini başlangıçta tanh(gate) = 0 ile nasıl koruduğunu açıklama.
- Bir Perceiver yeniden örnekleme (resampler) üzerinde yürüyüş: N görüntü yaması → K sabit "latant" sorgu çapraz-dikkatle.
- Flamingo'nun görüntü yerleşimini (image placement) sayan nedensel maskeleme (causal masking) ile aralıklı görüntü-metin dizilerini nasıl işlediğini tasvir etme.
- Bir few-shot multimodal istem yapısını (3 görüntü-açıklama çifti ardından sorgu görüntüsü) yeniden üretme.

## Sorun

BLIP-2, donmuş bir LLM'in girdi katmanına 32 görsel token besler. İstem başına tek görüntü için çalışır. Ama ya "işte görüntü A, açıkla; işte görüntü B, açıkla; şimdi görüntü C, açıkla" şeklinde metinle aralıklı *birçok* görüntü beslemek isterseniz? LLM'in öz-dikkati görüntü token'larını ve metin token'larını tek bir akışta işlemeniz gerekir ve hangi konumların hangi görüntülere dikkat edebileceği sorusu karmaşıklaşır.

Flamingo'nun cevabı: LLM'in girdi akışını hiç değiştirmeyin. Mevcut LLM blokları arasına ekstra çapraz-dikkat katmanları yerleştirin. Metin token'ları her zaman olduğu gibi LLM'in nedensel öz-dikkatinden akar. Her birkaç LLM bloğundan sonra metin token'ları yeni kapılı bir katman üzerinden görüntü özelliklerine de çapraz-dikkat uygular. Kapı (sıfırla başlatıldığı için) başlangıçta yeni katmanların işlem yapmamasını sağlar — model tam olarak ön-eğitilmiş LLM gibi davranır. Eğitim ilerledikçe kapı açılır ve görsel bilgi akmaya başlar.

Flamingo'nun cevap verdiği ikinci soru: istem başına değişken sayıda görüntüyü (0, 1 veya birçok) nasıl işlersiniz? Bir Perceiver yeniden örnekleme — hangi sayıda yamanız olursa olsun sabit sayıda görsel latant token üreten küçük bir çapraz-dikkat modülü. LLM çapraz-dikkat katmanı istemde kaç görüntü olursa olsun aynı şekli görür.

## Kavram

### Donmuş LLM

Flamingo donmuş bir Chinchilla 70B LLM ile başlar. 70B ağırlığa dokunulmaz. Mevcut metin öz-dikkati ve FFN normal çalışır.

### Perceiver yeniden örnekleme

İstemdeki her görüntü için ViT N yama token'ı üretir. Perceiver yeniden örneklemede K sabit öğrenilebilir latant vardır (Flamingo K=64 kullanır). Her yeniden örnekleme bloğu iki alt adımdan oluşur:

1. Çapraz-dikkat: K latant, N yama token'ı üzerinde dikkat uygular (Q latantlardan, K/V yamalardan).
2. Latantlar arasında öz-dikkat + FFN.

6 yeniden örnekleme bloğundan sonra çıktı, ViT kaç yama üretirse üretsin 1024 boyutunda K=64 görsel token'dır. 224x224 görüntü (196 yama) ve 480x480 görüntü (900 yama) her ikisi de 64 yeniden örnekleme token'ı olarak çıkar.

Video için yeniden örnekleme zamansal olarak uygulanır: her karenin yamaları 64 latant üretir ve zamansal konumsal kodlama (temporal positional encoding) modelin t=0 ile t=N'yi ayırt etmesini sağlar. Tam video T * 64 görsel token olur.

### Kapılı çapraz-dikkat

Donmuş LLM'in her M katmanında (Flamingo M=4 kullanır) yeni bir kapılı çapraz-dikkat bloğu yerleştirilir:

```
x_after_llm_block = llm_block(x_before)
cross = cross_attn(x_after, resampler_output)
gated = tanh(alpha) * cross + x_after
x_before_next_block = gated
```

#### Açıklama
- `alpha` sıfırla başlatılan öğrenilebilir bir skalerdir.
- `tanh(0) = 0`, dolayısıyla başlangıçta kapılı dal sıfır katkı sağlar.
- `alpha` sıfırdan uzaklaştıkça çapraz-dikkat katkısı düzgün artar.
- Artıklık bağlantısı (residual connection) sayesinde tamamen açık kapı bile LLM'in metin temsilini override etmez; yalnızca üzerine görsel bilgi ekler.

Bu Flamingo'daki en önemli tasarım kararıdır: görsel koşullandırma (visual conditioning) toplamsaldır (additive), kapılıdır ve başlangıçta sıfırdır. 0. adımdaki Flamingo, saf metin girdileri üzerinde mükemmel bir Chinchilla 70B'dir.

### Aralıklı girdiler için maskeli çapraz-dikkat

"<image A> açıklama A <image B> açıklama B <image C> ?" şeklinde bir istemde her metin token'ı yalnızca dizide kendisinden önce gelen görüntüleri görmelidir. Çapraz-dikkat maskesi zorlar: konum `t`'deki metin token'ı, yalnızca görüntü indeksi `i < i_t` olan görüntü yeniden örnekleme token'larına dikkat eder, burada `i_t` konum `t`'den önceki en son görüntüdür. "Yalnızca en son önceki görüntüyü görür" veya "tüm önceki görüntüleri görür" her ikisi de geçerli seçeneklerdir; Flamingo ilkini seçti.

### Bağlam-içi few-shot öğrenme

Bir Flamingo istemi şöyle görünür:

```
<image1> Bir kedinin fotoğrafı. <image2> Bir köpeğin fotoğrafı. <image3> Bir
```

Model tamamlama kalıbını görür ve "kuş" (veya image3'ün gösterdiği her neyse) çıkarır. Gradyan adımı yok. Donmuş LLM'in bağlam-içi öğrenme yeteneği kapılı çapraz-dikkat üzerinden akar — bu makalenin vurgusudur ve neden önemli olduğunu açıklar.

### Eğitim verileri

Flamingo üç veri seti üzerinde eğitildi:

1. MultiModal MassiveWeb (M3W): aralıklı görüntüler ve metin içeren 43M web sayfası, okuma sırası yeniden oluşturulmuş.
2. Görüntü-Metin Çiftleri (ALIGN + LTIP): 4.4B çift.
3. Video-Metin Çiftleri (VTP): 27M kısa video klibi.

OBELICS (2023) aralıklı web corpusunun açık yeniden üretimidir; Idefics, Idefics2 ve çoğu açık "Flamingo benzeri" model bunun üzerinde eğitilir.

### OpenFlamingo ve Otter

OpenFlamingo (2023) açık yeniden üretimdir. Mimari özdeştir (Perceiver yeniden örnekleme + donmuş LLaMA veya MPT üzerinde kapılı çapraz-dikkat). 3B, 4B, 9B kontrol noktaları. Daha küçük temel LLM ve daha az veri nedeniyle Flamingo'nun gerisinde kalır.

Otter (2023) OpenFlamingo üzerine inşa edilir, MIMIC-IT (talimatlı multimodal veri seti) üzerinde talimat ince ayarıyla kapılı çapraz-dikkatin talimat takibi için de çalıştığını gösterir.

### Soyundanları

- Idefics / Idefics2 / Idefics3: Hugging Face'in kapılı çapraz-dikkat soyu, giderek basitleşmiş (Idefics2 adaptif havuzlamayla doğrudan yama token'ları için yeniden örnelemeyi bıraktı).
- Flamingo'dan Chameleon'a geçiş: 2024'e kadar birçok ekip erken birleştimeye (early fusion, Ders 12.11) geçti; Flamingo tarzı kapılı çapraz-dikkat, omurga dondurmanın gerekli olduğu üretimde kaldı.
- Gemini'nin aralıklı girdisi: kavramsal olarak Flamingo'nun aralıklı biçim esnekliğini devralır, ama kesin mekanizma özeldir.

### BLIP-2 ile karşılaştırma

| | BLIP-2 | Flamingo |
|---|---|---|
| Görsel köprü | Girdide tek seferde Q-Former | Her M katmanında kapılı çapraz-dikkat |
| Görsel token'lar | Görüntü başına 32 | Görüntü başına çapraz-dikkat katmanı başına 64 |
| Donmuş LLM | Evet | Evet |
| Few-shot bağlam-içi | Zayıf | Güçlü — makalenin odak noktası |
| Aralıklı girdiler | Doğal destek yok | Evet, tasarım hedefi |
| Eğitim verileri | 130M çift | 1.3B çift + 43M aralıklı sayfa |
| Parametre sayısı | 188M eğitilmiş | ~10B eğitilmiş (çapraz-dikkat katmanları) |
| Hesaplama | 8 A100 üzerinde birkaç gün | Binlerce TPUv4 üzerinde haftalarca |

Bütçeli tek görüntü VQA için BLIP-2 seçin. Aralıklı, few-shot veya çoklu görüntü akıl yürütmesi için Flamingo/Idefics2 seçin.

## Kullan

`code/main.py` şunları gösterir:

1. 36 sahte yama token'ı üzerinde 8 öğrenilebilir latant ile Perceiver yeniden örnekleme (saf Python çapraz-dikkat).
2. `alpha = 0` ile kapılı çapraz-dikkat adımı → çıktı girdiye eşit (LLM değişmedi), ardından `alpha = 2.0` → görsel katıkı karıştırılır.
3. "(görüntü 1) (metin 1) (görüntü 2) (metin 2)" dizisi için 2B dikkat maskesi üreten aralıklı maske oluşturucu.

## Teslimat

Bu ders `outputs/skill-gated-bridge-diagnostic.md` dosyasını üretir. Açık bir VLM'in yapılandırması (yeniden örnekleme Y/N, çapraz-dikkat sıklığı, kapı şeması) verildiğinde, Flamingo soyu unsurlarını tanımlar ve dondurma stratejisini açıklar. Bir ince ayarın metin performansını neden bozduğunu ayırt etmek için kullanışlıdır (cevap: kapı çok hızlı açıldı).

## Alıştırmalar

1. Flamingo-9B'nin görsel parametre sayısını hesaplayın: 9B LLM + 1.4B kapılı çapraz-dikkat katmanı + 64M yeniden örnekleme. Toplam parametrelerin kaçta kaçı eğitilir?

2. Kapılı artıklığı `y = tanh(alpha) * cross + x` PyTorch'ta uygulayın. `alpha=0` ile başlangıçta `y==x` olduğunu deneysel olarak gösterin.

3. OpenFlamingo Bölüm 3.2'yi okuyun (arXiv:2308.01390) — her istemin farklı görüntü sayısına sahip olduğu bir toplu işte birden fazla görüntüyü nasıl işlediklerini. Doldurma (padding) stratejisini açıklayın.

4. Flamingo'nun çapraz-dikkat maskesi neden bir metin token'ının *yalnızca en son* önceki görüntüye değil de tüm önceki görüntülere dikkat etmesine izin verir? Flamingo makalesinin Bölüm 2.4'ünü okuyun ve uzlaşmayı açıklayın.

5. Bağlam-içi few-shot: yeni bir Flamingo çeşidi için "görüntü → ana nesnenin rengi" görevinde 4 örnek içeren bir istem oluşturun. Örnek sayısını 0'dan 8'e değiştirdiğinizde beklenen doğruluk kalıbını açıklayın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Perceiver yeniden örnekleme | "Sabit-latant çapraz-dikkat" | Değişken sayıda giriş yamasından K sabit token üreten modül |
| Kapılı çapraz-dikkat | "Tanh kapılı köprü" | Artıklık katmanı `y = tanh(alpha)*cross + x`, öğrenilebilir alpha, 0 ile başlatma |
| Aralıklı giriş | "Karışık dizi" | Görüntülerin ve metnin okuma sırasında serbestçe karıştığı istem biçimi |
| Donmuş LLM | "LLM gradyanı yok" | Metin LLM'in ağırlıkları güncellenmez; yalnızca yeniden örnekleme + çapraz-dikkat katmanları eğitilir |
| Few-shot | "Bağlam-içi örnekler" | İsteme birkaç (görüntü, cevap) çifti verme; model ince ayar yapmadan genelleştirir |
| OBELICS | "Aralıklı web corpusu" | Görüntüler ve metin içeren 141M web sayfasından oluşan açık veri seti |
| Chinchilla | "70B donmuş temel" | Flamingo'nun donmuş metin LLM'i, DeepMind'ın Chinchilla makalesinden |
| Kapı takvimi | "Alpha nasıl hareket eder" | Eğitim sırasında çapraz-dikkat kapısının açılma hızı |
| Çapraz-dikkat sıklığı | "Her M katmanda" | Kapılı çapraz-dikkat bloğunun ne sıklıkla eklendiği; Flamingo M=4 kullanır |
| OpenFlamingo | "Açık yeniden üretim" | MosaicML/LAION'ın 3-9B açık kontrol noktası; Flamingo ile özdeş mimari |

## İleri Okuma

- [Alayrac ve diğerleri — Flamingo (arXiv:2204.14198)](https://arxiv.org/abs/2204.14198) — orijinal makale.
- [Awadalla ve diğerleri — OpenFlamingo (arXiv:2308.01390)](https://arxiv.org/abs/2308.01390) — açık yeniden üretim.
- [Laurençon ve diğerleri — OBELICS (arXiv:2306.16527)](https://arxiv.org/abs/2306.16527) — aralıklı web corpusu.
- [Jaegle ve diğerleri — Perceiver IO (arXiv:2107.14795)](https://arxiv.org/abs/2107.14795) — genel Perceiver mimarisi.
- [Li ve diğerleri — Otter (arXiv:2305.03726)](https://arxiv.org/abs/2305.03726) — talimatlanmış Flamingo soyundanı.
- [Laurençon ve diğerleri — Idefics2 (arXiv:2405.02246)](https://arxiv.org/abs/2405.02246) — Flamingo yaklaşımının modern basitleştirilmesi.
