# Show-o ve Ayrık Diffüzyonlu Birliği Modelleri

> Transfusion sürekli ve ayrık temsilleri harmanlar. Show-o (Xie ve ark., Ağustos 2024) bunun tersini yapar: metin token'ları nedensel (causal) next-token tahmini kullanırken, görüntü token'ları MaskGIT ruhuyla maskeli ayrık diffüzyon kullanır. Her ikisi de hibrit (hybrid) attention mask'ı olan tek bir transformer içinde yer alır. Sonuç olarak VQA, text-to-image, inpainting ve karışık modalli (multimodal) üretimi tek bir omurga, her modallık için tek bir tokenizer ve tek bir kayıp formülasyonunda birleştirir (next-token tahmini masked prediction'a genişletilmiş hali). Bu ders Show-o tasarımını — neden masked discrete diffusion'ın paralel, az adımlı bir görüntü üretici olduğunu — ve Transfusion ile Emu3 ile karşılaştırmasını ele alır.

**Tür:** Öğren
**Diller:** Python (stdlib, masked-discrete-diffusion sampler)
**Ön koşullar:** Faz 12 · 13 (Transfusion)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Masked discrete diffusion'ı açıklayın: token'ları düzgün bir şekilde maskeler然后 transformer'dan kurtarmasını isteyen zaman çizelgesi.
- Paralel görüntü çözümlemesini (Show-o, MaskGIT) otoregressive görüntü çözümlemesiyle (Chameleon, Emu3) hız ve kalite açısından karşılaştırın.
- Show-o'nun tek bir checkpoint'ta hangi üç görevi ele aldığını adlandırın: T2I, VQA, image inpainting.
- Bir maskeleme zaman çizelgesi seçin (cosine, linear, truncated) ve örnek kalitesi üzerindeki etkisini tartın.

## Problem

Transfusion'un iki-kayıplı eğitimi çalışır ancak daha karmaşık dinamiklere sahiptir — sürekli diffüzyon kaybı, ayrık NTP kaybından farklı bir sayısal ölçekte yaşar. Kayıp ağırlıklarını dengelemek bir hiperparametre aramasıdır. Mimari etkilidir ancak komplekstir.

Show-o'nun cevabı: her iki modallığı da ayrık tutun (Chameleon gibi), ancak görüntüleri sıralı olarak üretmek yerine masked discrete diffusion aracılığıyla paralel üretin. Eğitim hedefi, next-token tahminini doğal olarak genişleten tek bir masked-token-prediction haline gelir.

## Kavram

### Masked discrete diffusion (MaskGIT)

Orijinal Chang ve ark. (2022) MaskGIT hilesi zariftir. Tamamen maskelenmiş bir görüntüden başlayın (her token özel `<MASK>` id'sidir). Her adımda, tüm maskelenmiş token'ları paralel olarak tahmin edin, ardından en yüksek güvenli K tahmini saklayın ve geri kalanını tekrar maskleyin. Yaklaşık 8-16 iterasyondan sonra tüm token'lar doldurulur. Her adımda kaç token'ın maskesinin kaldırılacağı zaman çizelgesi ayarlanır — cosine zaman çizelgeleri iyi çalışır.

Eğitim basittir: rastgele bir maskeleme oranını [0, 1] aralığından örnekleyin, görüntü VQ token'larına uygulayın ve transformer'ı maskelenmiş olanları kurtarmak için eğitin. BERT'in metin için yaptığının aynısı, görüntü üretimine ölçeklendirilmiş hali.

### Show-o: tek transformer, hibrit mask

Show-o, MaskGIT'i nedensel dil modeli transformer'ının içine yerleştirir. Attention mask şöyledir:

- Metin token'ları: nedensel (standart LLM).
- Görüntü token'ları: görüntü bloğu içinde tam çift yönlü (bidirectional) (böylece maskelenmiş token'lar tahmin sırasında diğer tüm görüntü token'larını görebilir).
- Text-to-image: metin önceki görüntülere dikkat eder, görüntü önceki metne dikkat eder.

Eğitim şu durumlar arasında alternatif yapar:
1. Metin dizileri üzerinde standart NTP.
2. T2I örnekleri: maskeleme görüntü token'larıyla metin → görüntü, masked-token-prediction kaybı.
3. VQA örnekleri: maskeleme metin token'larıyla görüntü → metin (aslında sadece NTP).

Birleşik kayıp, `<MASK>` token'ları üzerinde cross-entropy'dir; bu hem metin NTP'sini (sadece son token "masked"tür) hem de görüntü masked-diffusion'ını (rastgele alt küme masked'ır) kapsar.

### Paralel örnekleme

Show-o bir görüntüyü yaklaşık 16 adımda üretir (otoregressive olarak token başına ~1000 veya diffüzyonla ~20 yerine). Her adımda tüm maskelenmiş token'ları paralel olarak tahmin edin; en yüksek güvenli olanları onaylayın; tekrarlayın.

Karşılaştırma:
- Chameleon / Emu3 (token üzerinde otoregressive): N_tokens ileri geçiş, görüntü başına tipik olarak 1024-4096.
- Transfusion (sürekli diffüzyon): ~20 adım, her biri tam bir transformer geçişi.
- Show-o (masked discrete diffusion): ~16 adım, her biri tam bir transformer geçişi.

Show-o, benzer ölçekli modellere göre Chameleon'dan daha hızlıdır, Transfusion adım sayısına yaklaşık olarak eşleşir ancak adım başına daha düşük maliyetle (sözcük dağarcığı logit'leri sürekli MSE kaybına göre).

### Tek checkpoint'ta görevler

Show-o, çıkarımda prompt formatıyla seçilen dört görevi destekler:

- Metin üretimi: standart otoregressive metin çıktısı.
- VQA: görüntü girdi, metin çıktı.
- T2I: metin girdi, masked discrete diffusion aracılığıyla görüntü çıktı.
- Inpainting: bazı token'ları maskelenmiş görüntü, doldurma.

Inpainting yeteneği masked-prediction eğitiminden ücretsiz olarak gelir. VQ-token ızgarasının bir bölgesini maskelyin, geri kalanını artı bir metin prompt'u verin, maskelenmiş token'ları tahmin edin.

### Maskeleme zaman çizelgesi

Her adımda kaç token'ın maskesinin kaldırılacağı zaman çizelgesi kaliteyi belirler. Show-o cosine'i önerir:

```
mask_ratio(t) = cos(pi * t / (2 * T)) # t = 0.. T
```

0. adımda tüm token'lar maskelidir (oran 1.0). T. adımda hiçbir token maskeli değildir. Cosine, tahminin en bilgilendirici olduğu orta aralık oranlarında kütleyi yoğunlaştırır. Linear zaman çizelgeleri de çalışır ancak daha hızlı plato yapar.

### Show-o2

Show-o2 (2025 devamı, arXiv 2506.15564), Show-o'yu ölçeklendirir: daha büyük LLM temeli, daha iyi tokenizer, geliştirilmiş maske zaman çizelgesi. Aynı mimari yapı.

### Show-o'nun konumu

2026 sınıflandırmasında:

- Ayrık token + NTP: Chameleon, Emu3. Basit ancak yavaş çıkarım.
- Ayrık token + masked diffusion: Show-o, MaskGIT, LlamaGen, Muse. Paralel örnekleme, hâlâ tokenizer tarafından kayıplı.
- Sürekli + diffüzyon: Transfusion, MMDiT, DiT. En yüksek kalite, daha karmaşık eğitim.
- Sürekli + VLM'de flow matching: JanusFlow, InternVL-U. En yenisi.

Göre göre seçin: Show-o, tek bir açık modelde T2I + inpainting + VQA istendiğinde makul hızla; Transfusion, kalite en üst düzeyde olduğunda ve iki-kayıplı boru hattını göze alabildiğinizde.

## Kullan

`code/main.py` Show-o örneklemini simüle eder:

- 16 VQ token'ından oluşan oyuncak bir ızgara.
- Prompt'a ve şu anda maskesi kaldırılmış token'lara göre logit tahmin eden sahte bir "transformer".
- 8 adımda cosine zaman çizelgeli paralel masked örnekleme.
- Ara durumları (maske deseni evrimi) ve son token'ları yazdırır.

Çalıştırın, maskenin adım adım nasıl çözüldüğünü izleyin.

## Teslim Et

Bu ders `outputs/skill-unified-gen-model-picker.md` dosyasını üretir. Hem anlama (VQA, captioning) hem de üretim (T2I, inpainting) gerektiren ve açık ağırlıklar kısıtlaması olan bir ürün için Show-o ailesi, Transfusion/MMDiT ailesi ve Emu3 / Chameleon ailesi arasında somut tavizlerle seçim yapar.

## Alıştırmalar

1. Masked discrete diffusion ~16 adımda örnekler. Neden 1 değil? 0. adımda her şeyin maskesini kaldırırsa ne bozulur?

2. Inpainting masked diffusion ile ücretsizdir. Show-o'nun inpainting'inin uzman bir modeli yendiği bir ürün kullanım durumu önerin (gerçek veya hayali).

3. Cosine zaman çizelgesi vs linear zaman çizelgesi: T=8 için her adımda maskesi kaldırılmış token sayısını izleyin. Hangisi daha dengeli?

4. 512x512'lik bir Show-o görüntüsü 1024 token'dır. vocab K=16384 ile model, 1024 * log2(16384) = 14,336 bit (~1.75 KiB) veri üretir. Stable Diffusion 512*512*24 bit = 6,291,456 bit (~768 KiB) ham piksel çıkarır. Sıkıştırma oranı nedir ve bu ne tür bir kalite satın alır?

5. LlamaGen'i okuyun (arXiv:2406.06525). LlamaGen'in sınıflı koşullu otoregressive görüntü modeli Show-o'nun masked yaklaşımından nasıl farklıdır?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Masked discrete diffusion | "MaskGIT tarzı" | Maskelenmiş token'ları tahmin etmek için eğitim; çıkarımda en yüksek güvenli tahminlerin masked'ını iteratif olarak kaldırmak |
| Cosine zaman çizelgesi | "Maskesini kaldırma zaman çizelgesi" | Çıkarım adımları boyunca maske oranının azalması; güven artışını orta aralıkta yoğunlaştırır |
| Paralel çözümleme | "Tüm token'lar bir anda" | Her adım, masked token'ların tüm dizisini tek bir ileri geçişte tahmin eder ve en yüksek güvenli olanları onaylar |
| Hibrit attention | "Nedensel + çift yönlü" | Metin token'larında nedensel, görüntü blokları içinde çift yönlü olan mask |
| Inpainting | "Doldurma üretimi" | Bazı token'ları maskelenmiş bir görüntüye koşullu olarak, eksik olanları tahmin etme; eğitim hedefinden ücretsiz |
| Onaylama oranı | "Adım başına en yüksek K" | Her iterasyonda "bitti" ilan edilen token sayısı; çıkarım-kalite dengesini kontrol eder |

## Daha Fazla Kaynak

- [Xie ve ark. — Show-o (arXiv:2408.12528)](https://arxiv.org/abs/2408.12528)
- [Show-o2 (arXiv:2506.15564)](https://arxiv.org/abs/2506.15564)
- [Chang ve ark. — MaskGIT (arXiv:2202.04200)](https://arxiv.org/abs/2202.04200)
- [Sun ve ark. — LlamaGen (arXiv:2406.06525)](https://arxiv.org/abs/2406.06525)
- [Chang ve ark. — Muse (arXiv:2301.00704)](https://arxiv.org/abs/2301.00704)
