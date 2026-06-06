# Janus-Pro: Birliği Sağlayan Modeller İçin Ayrıştırılmış Encoder'lar

> Birleşik multimodal modeller kaçınılmaz bir gerilim taşır. Anlama, kavram düzeyinde zengin semantik özellikler ister — SigLIP veya DINOv2'nin çıkardığı vektörler gibi. Üretim ise yeniden oluşturmaya uygun kodlar ister — piksellere temiz bir şekilde geri dönen VQ token'ları gibi. İki hedef tek bir encoder'da uyumlu değildir. Janus (DeepSeek, Ekim 2024) ve Janus-Pro (DeepSeek, Ocak 2025) sorunun çözümünün iki encoder'dan vazgeçmek olduğunu savunur: iki encoder'ı ayrıştırın. Transformer gövdesini görevler arasında paylaşın, ancak anlama işlemini SigLIP üzerinden, üretimi ise VQ tokenizer üzerinden yönlendirin. 7B ile Janus-Pro, MMMU'da LLaVA'ya eşleşirken GenEval'da DALL-E 3'ü yener. Bu ders neden tek encoder'ın başarısız olduğu yerde iki encoder'ın çalıştığını okur.

**Tür:** İnşa Et
**Diller:** Python (stdlib, dual-encoder routing + shared-body signal)
**Ön koşullar:** Faz 12 · 13 (Transfusion), Faz 12 · 14 (Show-o)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Neden tek bir paylaşımlı encoder'ın anlama veya üretim kalitesinden ödün verdiğini açıklayın.
- Janus-Pro'nun yönlendirmesini (routing) tanımlayın: girdi tarafında anlama için SigLIP özellikleri, hem girdi hem çıktı tarafında üretim için VQ token'ları.
- Janus-Pro'nun Janus'un başaramadığı yerde başarılı olmasını sağlayan veri ölçeklemesini (data-mix scaling) izleyin.
- Ayrıştırılmış (Janus-Pro), birleşik-sürekli (Transfusion) ve birleşik-ayrık (Show-o) mimarilerini karşılaştırın.

## Problem

Birleşik modeller, anlama ve üretim arasında bir transformer gövdesini paylaşır. Önceki girişimler (Chameleon, Show-o, Transfusion) her iki yön için de tek bir görsel tokenizer kullanır. Tokenizer bir uzlaşmadır:

- Yeniden oluşturma için optimize edilmiş (üretim): VQ-VAE ince piksel ayrıntısını yakalar ancak zayıf semantik tutarlılığa sahip token'lar üretir.
- Semantikler için optimize edilmiş (anlama): embedding'ler "kedi" görüntülerini "kedi" token'larının yakınına gruplandırır ancak iyi yeniden oluşturmaya izin vermez.

Show-o ve Transfusion bunun bedelini bir yönde görünür bir kalite vergisiyle öder. Janus-Pro şunu sorar: görevlerin farklı ihtiyaçları varsa neden tek bir tokenizer gerekir?

## Kavram

### Ayrıştırılmış görsel kodlama

Janus-Pro'nun mimarisi iki encoder'ı ayırır:

- Anlama yolu. Girdi görüntüsü → SigLIP-SO400m → 2 katmanlı MLP → transformer gövdesi.
- Üretim yolu. Girdi görüntüsü (mevcut bir görsele koşulluysa) → VQ tokenizer → token ID'leri → transformer gövdesi.
- Çıktı üretimi. Transformer tarafından tahmin edilen görüntü token'ları → VQ decoder → pikseller.

Transformer gövdesi paylaşılır. Gövdenin yukarısındaki ve altındaki her şey göreldir.

Girdiler prompt formatıyla ayrıştırılır: `<understand>` etiketi SigLIP üzerinden yönlendirir; `<generate>` VQ üzerinden yönlendirir. Veya yönlendirme göreve göre örtüktür.

### Neden çalışır

Anlama kaybı SigLIP özelliklerini alır; bunlar CLIP tarzı ön eğitimle semantik benzerlik için ayarlanmıştır. Modelin algılama benchmark'ları Show-o / Transfusion'dan iyileşir çünkü girdi özellikleri görev için daha uygundur.

Üretim kaybı VQ token'larını alır; bunlar bir tokenizer tarafından yeniden oluşturma için ayarlanmıştır. Görüntü kalitesi Show-o'ya göre iyileşir çünkü VQ kodları piksellere temiz bir şekilde geri döner.

Paylaşılan transformer gövdesi iki girdi dağılımı (SigLIP ve VQ) görür ve her ikisiyle çalışmayı öğrenir. İddia: yeterli veri + yeterli parametre, gövde geçişi absorbe eder.

### Veri ölçeklemesi — Janus vs Janus-Pro

Janus (orijinal, arXiv 2410.13848) ayrıştırmayı tanıttı ancak küçük ölçekte (1.3B parametre, sınırlı veri). Janus-Pro (arXiv 2501.17811) ölçeklendirdi:

- 7B parametre (1.3B'ye kıyasla).
- 1. adım (hizalama) için 72M'den 90M görüntü-metin çifti.
- 2. adım (birleşik) için 26M'den 72M.
- 3. adım için 200k görüntü-üretim talimat örneği eklendi.

Sonuç: Janus-Pro-7B MMMU'da LLaVA'ya eşleşir (60.3'e kıyasla ~58) ve GenEval'da DALL-E 3'ü yener (0.80'e kıyasla 0.67). Tek bir açık model, birleşik spektrumun her iki tarafında rekabetçi.

### JanusFlow — rectified flow varyantı

JanusFlow (arXiv 2411.07975) VQ üretim yolunu rectified-flow üretim yoluyla (sürekli) değiştirir. Bölünme SigLIP-anlama-artı-rectified-flow-üretim haline gelir. Kalite tavanları daha da yükselir. Mimari ayrıştırılmış-encoder-paylaşımlı-gövde olarak kalır.

### Paylaşılan gövdenin görevi

Transformer gövdesi, iki girdi dağılımıyla ancak birleşik bir dizi işler. Görevi şudur:

- Anlama için: SigLIP özellikleri + metin token'larını tüketir → metni otoregressive olarak üretir.
- Üretim için: metin token'larını + (isteğe bağlı görüntü VQ token'larını) tüketir → görüntü VQ token'larını otoregressive olarak üretir.

Gövde, blok başına modallığa özgü ağırlığa sahip değildir. Qwen veya Llama içinde beklediğiniz metin tarzı transformer'dır, artı iki girdi adaptörü.

İlginç bir şekilde, bu Janus-Pro'nun gövdesinin önceden eğitilmiş bir LLM'den başlatılabileceği anlamına gelir. Janus-Pro DeepSeek-MoE-7B'den başlatılır. Bu seçim önemlidir: LLM, sıfırdan üretilmiş birleşik modellerin ulaşmakta zorlandığı çıkarım yeteneği sağlar.

### InternVL-U ile karşılaştırma

InternVL-U (Ders 12.10) 2026 devamıdır. Şunları birleştirir:

- Doğal multimodal ön eğitim (InternVL3 omurgası).
- Ayrıştırılmış encoder yönlendirmesi (SigLIP girdi, VQ + diffüzyon başlıkları çıktı).
- Birleşik anlama + üretim + düzenleme.

InternVL-U, Janus-Pro'nun mimari seçimini daha büyük bir çerçeve içine alır. Ayrıştırılmış encoder fikri artık ölçekli birleşik modeller için varsayılan haline gelmiştir.

### Sınırlamalar

Ayrıştırılmış encoder'lar mimari karmaşıklık ekler. Eğitilecek iki tokenizer, bakılacak iki girdi yolu, iki hata modu kümesi. Üretim ihtiyacı olmayan ürünler için Janus-Pro aşırı mühendisliktir — bir LLaVA ailesi anlama modeli seçin.

Anlama ihtiyacı olmayan ürünler için Janus-Pro aşırı yetkindir — bir Stable Diffusion 3 / Flux modeli seçin.

Her ikisine de ihtiyaç duyan ürünler için Janus-Pro artık referans açık mimaridir.

## Kullan

`code/main.py` Janus-Pro yönlendirmesini simüle eder:

- SigLIP benzeri (256 boyutlu semantik vektörler üreten) ve VQ benzeri (tamsayı kodları üreten) iki sahte encoder.
- Görev etiketine göre encoder'ı seçen bir prompt yönlendirici.
- Hangi encoder üretirse üretsin token dizilerini işleyen paylaşımlı gövde (yer tutucu).
- 1. adımdan (hizalama) 3. adıma (talimat ayarı) ağırlıklı örnek zaman çizelgesine geçiş.

3 örnek için yönlendirilmiş yolları yazdırın: görüntü soru-cevabı, T2I, görüntü düzenleme.

## Teslim Et

Bu ders `outputs/skill-decoupled-encoder-picker.md` dosyasını üretir. Birleşik üretim + anlama isteyen ve sınır kalitesine yakın bir ürün için Janus-Pro, JanusFlow veya InternVL-U'yu somut veri ölçeği önerisiyle seçer.

## Alıştırmalar

1. Janus-Pro-7B GenEval'da DALL-E 3'ü yener. Neden 7B'lik bir açık model, üretimde sınırlı bir özel modele eşleşebilirken anlamada eşleyemez?

2. Bir yönlendirici fonksiyon uygulayın: verilen metin prompt'unu `understand` veya `generate` olarak sınıflandırın. "Tanımla sonra çiz" gibi belirsiz prompt'ları nasıl ele alırsınız?

3. JanusFlow VQ yolunu rectified flow ile değiştirir. Transformer gövdesi artık ne üretir ve kayıpta ne değişir?

4. Janus-Pro mimarisinin bir encoder'ı daha ayrıştırarak işleyebileceği dördüncü bir görev önerin. Örnekler: görüntü segmentasyonu (DINO tarzı), derinlik (MiDaS tarzı).

5. Janus-Pro Bölüm 4.2'yi veri ölçeklemesi üzerine okuyun. Janus'a kıyasla T2I kalite kazancına en çok hangi veri aşaması katkıda bulunur?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Ayrıştırılmış kodlama | "İki görsel encoder" | Yön başına ayrı tokenizer veya encoder: anlama için semantik, üretim için yeniden oluşturma |
| Paylaşılan gövde | "Tek transformer" | Tek bir transformer her iki encoder'ın çıktısını işler; modallığa özgü ağırlık yoktur |
| Anlama için SigLIP | "Semantik özellikler" | CLIP ailesi görüntü kulesi; zengin kavramsal özellikler sağlar ancak yeniden oluşturma zayıftır |
| Üretim için VQ | "Yeniden oluşturma kodları" | Piksellere temiz bir şekilde geri decode edilen vektör-quantize edilmiş token'lar |
| JanusFlow | "Rectified-flow varyantı" | VQ yerine sürekli flow-matching üretim başlığına sahip Janus-Pro |
| Yönlendirme etiketi | "Görev etiketi" | Girdi encoder'ını seçen prompt işareti (`<understand>` / `<generate>`) |

## Daha Fazla Kaynak

- [Wu ve ark. — Janus (arXiv:2410.13848)](https://arxiv.org/abs/2410.13848)
- [Chen ve ark. — Janus-Pro (arXiv:2501.17811)](https://arxiv.org/abs/2501.17811)
- [Ma ve ark. — JanusFlow (arXiv:2411.07975)](https://arxiv.org/abs/2411.07975)
- [InternVL-U (arXiv:2603.09877)](https://arxiv.org/abs/2603.09877)
- [Dong ve ark. — DreamLLM (arXiv:2309.11499)](https://arxiv.org/abs/2309.11499)
