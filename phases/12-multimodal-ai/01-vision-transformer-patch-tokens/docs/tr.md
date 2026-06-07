# Görüntü Transformer'ları ve Yama-Token (Patch-Token) İlkel Birimi

> Herhangi bir multimodal şeyden önce, bir görüntünün transformer'ın işleyebileceği bir token dizisine dönüşmesi gerekir. 2020 ViT makalesi bunu 16x16 piksel yamaları, bir doğrusal projeksiyon ve bir konumsal gömme (positional embedding) ile çözdü. Beş yıl sonra 2026'nın tüm çığır açan modeli (2576px yerel çözünürlüğe sahip Claude Opus 4.7, Gemini 3.1 Pro, Qwen3.5-Omni) hâlâ bu şekilde başlıyor — kodlayıcı ViT'ten DINOv2'ye, ardından SigLIP 2'ye dönüştü, register token'ları eklendi, konumsal şema 2D-RoPE oldu ama ilkel birim korundu. Bu ders, yama-token hattını baştan sona inceler ve Faz 12'nin geri kalanının "görsel token"lar hakkında somut bir zihinsel model oluşturması için stdlib Python'da uygular.

**Tür:** Öğren
**Diller:** Python (stdlib, yama tokenize edici + geometri hesaplayıcı)
**Önkoşullar:** Faz 7 (Transformer'lar), Faz 4 (Bilgisayar Görüsü)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- HxWx3 boyutundaki bir görüntüyü doğru konumsal kodlamayla (positional encoding) bir yama token'ı dizisine dönüştürme.
- Verilen (yama boyutu, çözünürlük, gizli boyut, derinlik) parametreleriyle bir ViT için dizi uzunluğunu, parametre sayısını ve FLOPs'ları hesaplama.
- ViT'i 2020 araştırma aşamasından 2026 üretim aşamasına taşıyan üç yükseltmeyi adlandırma: kendi kendine denetimli ön-eğitim (DINO / MAE), register token'ları ve yerel çözünürlüklü paketleme (native-resolution packing).
- Bir alt görev için havuzlama stratejisi olarak CLS havuzlaması (CLS pooling), ortalama havuzlama (mean pooling) ve register token'ları arasında seçim yapma.

## Sorun

Transformer'lar vektör dizileri üzerinde çalışır. Metin zaten bir dizidir (byte'lar veya token'lar). Bir görüntü ise üç renk kanallı piksellerden oluşan iki boyutlu bir ızgaradır — bir dizi değildir. Her pikseli düzleştirdiğinizde 224x224 RGB görüntü 150.528 token'a dönüşür ve bu uzunluktaki öz-dikkat (self-attention) çalışılamaz (dizi uzunluğuna karesel bağımlılık).

2020 öncesi yaklaşımlar ön tarafa bir CNN özelliği çıkarıcı eklerdi: ResNet 2048 boyutlu vektörlerden oluşan 7x7 boyutunda bir harita üretir, bu 49 token'ı bir transformer'a beslerdi. Bu işe yarar ama CNN'in önyargılarını (örtüşme eşdeğeri, yerel alma alanları) devralır ve transformernın ölçek iştahını kaybeder.

Dosovitskiy ve diğerleri (2020) doğrudan soruyu sordu: ya CNN'i atlar, görüntüyü sabit boyutlu yamalara (örneğin 16x16 piksel) böler, her yamayı doğrusal olarak bir vektöre projekte eder, bir konumsal gömme ekler ve diziyi vanilya bir transformer'a beslersek? O zamanlar bu kutsallık ihlaliydi — konvolüsyonsuz görüntü. Yeterli veriyle (JFT-300M, ardından LAION) ImageNet'te ResNet'i yendi ve gelişmeye devam etti.

2026'da ViT ilkel birimi tartışmasız temeldir. Her açık ağırlıklı (open-weights) VLM'in görüntü kulesi (vision tower) bir ViT soyundan gelir (DINOv2, SigLIP 2, CLIP, EVA, InternViT). Soru artık "yama kullanmalı mıyız?" değil, "hangi yama boyutu, hangi çözünürlük takvimi, hangi ön-eğitim hedefi, hangi konumsal kodlama?" şeklindedir.

## Kavram

### Yamalar token olarak

Şekli `(H, W, 3)` olan bir görüntü `x` ve yama boyutu `P` verildiğinde, görüntüyü `(H/P) x (W/P)` boyutunda çaprazlamayan (non-overlapping) yama ızgarasına bölersiniz. Her yama `P x P x 3` boyutunda bir piksel küpüdür. Her küpü `3 P^2` boyutunda bir vektöre düzleştirin. Her yamayı modelin gizli boyutuna `D` haritalayan `(3 P^2, D)` boyutunda paylaşımlı bir doğrusal projeksiyon `W_E` uygulayın.

ViT-B/16 kanonik yapılandırması için:
- Çözünürlük 224, yama boyutu 16 → ızgara 14x14 → 196 yama token'ı.
- Her yama `16 x 16 x 3 = 768` piksel değeridir, `D = 768` boyutuna projekte edilir.
- Öğrenilebilir `[CLS]` token'ı eklenir → dizi uzunluğu 197.

Yama projeksiyonu matematiksel olarak `P` çekirdek boyutlu, `P` adım genişliğinde ve `D` çıkış kanallı 2D konvolüsyonla özdeştir. Üretim kodu bunu tam olarak böyle uygular — `nn. Conv2d(3, D, kernel_size=P, stride=P)`. "Doğrusal projeksiyon" çerçevelemesi kavramsaldır; çekirdek çerçevelemesi verimlidir.

### Konumsal gömmeler (positional embeddings)

Yamaların doğal bir sırası yoktur — transformer onları bir çuval gibi görür. İlk ViT'ler öğrenilebilir 1D konumsal gömme eklerdi (her konum için bir 768 boyutlu vektör, toplam 197 tane). İşe yarar ama modeli eğitim çözünürlüğüne bağlar: ızgarayı değiştirdiğinizde çıkarım sırasında konum tablosunu enterpolasyon (interpolation) yapmanız gerekir.

Modern görüntü omurgaları 2D-RoPE (Qwen2-VL'nin M-RoPE'si, SigLIP 2'nin varsayılanı) veya çarpanlı 2D konumları (factorized 2D positions) kullanır. 2D-RoPE, sorgu (query) ve anahtar (key) vektörlerini yamanın (satır, sütun) indeksine göre döndürerek modelin göreli 2D konumunu döndürme açısından çıkarmasını sağlar. Konum tablosu yoktur. Model çıkarım sırasında rastgele ızgara boyutlarını işler.

### CLS token'ı, havuzlanmış çıktı ve register token'ları

Görüntü düzeyinde temsil nedir? Üç seçenek bir arada var olur:

1. `[CLS]` token'ı. Yama dizisinin başına öğrenilebilir bir vektör eklenir. Tüm transformer bloklarından sonra CLS token'ının gizli durumu görüntü temsilidir. BERT'ten devralınmıştır. Orijinal ViT, CLIP tarafından kullanılır.
2. Ortalama havuzlama (mean pool). Yama token'larının çıktı gizli durumlarının ortalaması alınır. SigLIP, DINOv2 ve çoğu modern VLM tarafından kullanılır.
3. Register token'ları. Darcet ve diğerleri (2023), açık bir batık (sink) token'ı olmadan eğitilen ViT'lerin yüksek normlu "artefakt" yamaları geliştirdiğini ve bu yamaların öz-dikkati (self-attention) kaçırdığını gözlemledi. 4–16 öğrenilebilir register token'ı eklenmesi bu yükü absorbe eder ve yoğun tahmin (segmentasyon, derinlik) kalitesini artırır. DINOv2 ve SigLIP 2'nin her ikisi de register ile gelir.

Seçim alt görevler için önemlidir. CLS sınıflandırma için uygundur. Yama token'larını bir LLM'e besleyen VLM'ler için havuzlamayı tamamen atlayabilirsiniz — her yama bir LLM girdi token'ı olur. Register'lar devretme öncesinde atılır ( bunlar iskelet yapıdır, içerik değil).

### Ön-eğitim: denetimli, karşıtlıklı, maskeli, kendi kendine damıtılmış

2020 ViT, JFT-300M üzerinde denetimli sınıflandırma ile ön-eğitilmişti. Hızla yerini alanlar:

- CLIP (2021): 400M çift üzerinde karşıtlıklı görüntü-metin. Ders 12.02.
- MAE (2021, He ve diğerleri): %75 yamayı maskeleyin, pikselleri yeniden oluşturun. Kendi kendine denetimli, saf görüntü üzerinde çalışır.
- DINO (2021) / DINOv2 (2023): öğrenci-öğretmen ile kendi kendine damıtma, etiket yok, açıklama yok. 2023 DINOv2 ViT-g/14 en güçlü saf görüntü omurgasıdır ve "yoğun özellikler" (dense features) kullanım alanı için varsayılandır.
- SigLIP / SigLIP 2 (2023, 2025): sigmoid kayıplı ve yerel en boy oranı için NaFlex'li CLIP. 2026 açık VLM'lerinde baskın görüntü kulesi (Qwen, Idefics2, LLaVA-OneVision).

Ön-eğitim seçiminiz omurganın neyi iyi yaptığını belirler: CLIP/SigLIP metinle anlamsal eşleşme için, DINOv2 yoğun görsel özellikler için, MAE alt görev ince ayarı için bir başlangıç noktası olarak.

### Ölçekleme yasaları (scaling laws)

ViT ölçeklemesi (Zhai ve diğerleri 2022), bir ViT kalitesinin model boyutu, veri boyutu ve hesaplama gücünde öngörülebilir yasalara uyduğunu ortaya koydu. Sabit hesaplama gücünde:
- Daha büyük model + daha fazla veri → daha iyi kalite.
- Yama boyutu, dizi uzunluğu ile hassasiyet arasında bir kaldıraçtır. Patch 14 (DINOv2/SigLIP SO400m için tipik) görüntü başına daha fazla token üretir; OCR ve yoğun görevler için daha iyi, hız için daha kötü.
- Çözünürlük diğer büyük kaldıraçtır. 224'ten 384'e, oradan 512'ye geçmek neredeyse her zaman FLOPs'larda karesel maliyetle yardım eder.

ViT-g/14 (1B parametre, patch 14, 224 çözünürlük → 256 token) ve SigLIP SO400m/14 (400M parametre, patch 14) 2026 açık VLM'lerinin iki ana at işi (workhorse) kodlayıcısıdır.

### ViT parametre sayısı

Hesaplama `code/main.py` dosyasında yer alır. 224 çözünürlükte ViT-B/16 için:

```
patch_embed = 3 * 16 * 16 * 768 + 768 = 591k
cls + pos = 768 + 197 * 768 = 152k
block = 4 * 768^2 (QKVO) + 2 * 4 * 768^2 (MLP) + 2 * 2*768 (LN)
 = 12 * 768^2 + 3k = 7.1M
12 blocks = 85M
final LN = 1.5k
total ≈ 86M
```

#### Açıklama
Her ViT'i kontrol noktasını (checkpoint) yüklemeden önce bu şekilde topyekûn hesaplayın. Omurga boyutu herhangi bir alt VLM'de VRAM zemininizi belirler.

### 2026 üretim yapılandırması

2026'da çoğu açık VLM'in sunduğu kodlayıcı, NaFlex ile yerel çözünürlükte SigLIP 2 SO400m/14'tür. Özellikleri:
- 400M parametre.
- Yama boyutu 14, varsayılan çözünürlük 384 → görüntü başına 729 yama token'ı.
- Görüntü düzeyindeki görevler için ortalama havuzlama; VQA için 729 yamanın tamamı LLM'e akar.
- 4 register token'ı, LLM devretme öncesinde atılır.
- Yerel en boy oranı için görüntü düzeyinde ölçeklemeli 2D-RoPE.

Bu yapılandırmadaki her karar, okuyabileceğiniz bir makaleye kadar izlenebilir.

## Kullan

`code/main.py` bir yama tokenize edici ve geometri hesaplayıcısıdır. (Görüntü H, W, yama P, gizli boyut D, derinlik L) alır ve şunları raporlar:

- Yamalama sonrası ızgara şekli ve dizi uzunluğu.
- Sentetik 8x8 piksel oyuncu görüntü için token dizisi (düzleştirme + projeksiyon yolunun adım adım incelenmesi).
- Yamalama gömmesi, konum gömmesi, transformer blokları ve kafaya göre ayrılmış parametre sayısı.
- Hedef çözünürlükte ileri geçiş (forward pass) başına FLOPs.
- ViT-B/16 @ 224, ViT-L/14 @ 336, DINOv2 ViT-g/14 @ 224, SigLIP SO400m/14 @ 384 arasında karşılaştırma tablosu.

Çalıştırın. Parametre sayılarını yayınlanmış değerlerle eşleştirin. Yama boyutu ve çözünürlükle oynayarak token sayısı maliyetini hissedin.

## Teslimat

Bu ders `outputs/skill-patch-geometry-reader.md` dosyasını üretir. Bir ViT yapılandırması (yama boyutu, çözünürlük, gizli boyut, derinlik) verildiğinde, gerekçelendirmelerle birlikte token sayısı, parametre sayısı ve VRAM tahmini üretir. Bir VLM için görüntü omurgası seçerken bu beceriyi kullanın — "token'lar patladı ve LLM bağlamım doldu" sürprizlerini önler.

## Alıştırmalar

1. Qwen2.5-VL'in yerel 1280x720 girişi ve 14 yama boyutuyla yama token dizisi uzunluğunu hesaplayın. Bu, yalnızca CLS temsiline kıyasla nasıl karşılaştırılır?

2. 1080p kare (1920x1080), 14 yama boyutuyla kaç token üretir? 30 FPS ile 5 dakikalık videoda toplam kaç görsel token vardır? En fazla maliyet tasarrufunu sağlayan hangisidir: havuzlama, kare örnekleme (frame sampling) yoksa token birleştirme (token merging)?

3. Saf Python'da yama token'ları üzerinde ortalama havuzlama uygulayın. DINOv2 çıktısının 196 token'ı üzerindeki ortalama havuzlamanın, havuzlanmış bir gömme istediğinizde modelin `forward` metodunun döndürdüğüyle eşleştiğini doğrulayın.

4. "Vision Transformers Need Registers" makalesinin (arXiv:2309.16588) 3. Bölümünü okuyun. Register'ların hangi artefaktı absorbe ettiğini ve bunun alt görev yoğun tahminleri için neden önemli olduğunu iki cümleyle açıklayın.

5. `code/main.py` dosyasını patch-n'-pack'i destekleyecek şekilde değiştirin: farklı çözünürlüklerde bir görüntü listesi verildiğinde, tek bir paketlenmiş dizi ve blok çapraz (block-diagonal) dikkat maskesi üretin. 12.06 dersine ulaştığınızda doğrulayın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Patch (Yama) | "16x16 piksel kare" | Giriş görüntüsünün sabit boyutlu çaprazlamayan bölgesi; bir token'a dönüşür |
| Patch embedding (Yama gömmesi) | "Doğrusal projeksiyon" | Düzleştirilmiş yama piksellerini D boyutlu vektörlere haritalayan paylaşımlı öğrenilmiş matris (veya stride=P olan Conv2d) |
| CLS token'ı | "Sınıf token'ı" | Başına eklenen öğrenilebilir vektör; son gizli durumu tüm temsil eder; 2026'da isteğe bağlıdır |
| Register token'ı | "Batık token'ı" | ViT'lerin ön-eğitim sırasında geliştirdiği yüksek normlu dikkat artefaktlarını absorbe eden ekstra öğrenilebilir token'lar |
| Position embedding (Konumsal gömme) | "Konumsal bilgi" | Sırayı fark eden konum-bazlı vektör veya döndürme; 2D-RoPE modern varsayılandır |
| Grid (Izgara) | "Yama ızgarası" | Belirli bir çözünürlük ve yama boyutu için (H/P) x (W/P) 2B yama dizisi |
| NaFlex | "Yerel esnek çözünürlük" | SigLIP 2 özelliği: tek model yeniden eğitmeden çoklu en boy oranı ve çözünürlüğü sunar |
| Backbone (Omurga) | "Görüntü kulesi" | Önceden eğitilmiş görüntü kodlayıcısı; yama token çıktıları VLM'de LLM'e beslenir |
| Pooling (Havuzlama) | "Görüntü düzeyinde özet" | Yama token'larını bir vektöre dönüştürme stratejisi: CLS, ortalama, dikkat havuzlaması veya register tabanlı |
| Patch 14 vs 16 | "Daha ince vs daha kaba ızgara" | Patch 14 görüntü başına daha fazla token üretir, OCR için daha iyi hassasiyet, daha yavaş; patch 16 klasik varsayılandır |

## İleri Okuma

- [Dosovitskiy ve diğerleri — Bir Görüntü 16x16 Kelimeye Değer (arXiv:2010.11929)](https://arxiv.org/abs/2010.11929) — orijinal ViT.
- [He ve diğerleri — Maskeli Otokodlayıcılar Ölçeklenebilir Görüntü Öğrenicileridir (arXiv:2111.06377)](https://arxiv.org/abs/2111.06377) — MAE, kendi kendine denetimli ön-eğitim.
- [Oquab ve diğerleri — DINOv2 (arXiv:2304.07193)](https://arxiv.org/abs/2304.07193) - Ölçekte kendi kendine damıtma, etiket yok.
- [Darcet ve diğerleri — Vision Transformers Need Registers (arXiv:2309.16588)](https://arxiv.org/abs/2309.16588) — register token'ları ve artefakt analizi.
- [Tschannen ve diğerleri — SigLIP 2 (arXiv:2502.14786)](https://arxiv.org/abs/2502.14786) — 2026 varsayılan görüntü kulesi.
- [Zhai ve diğerleri — Görüntü Transformer'larını Ölçeklendirmek (arXiv:2106.04560)](https://arxiv.org/abs/2106.04560) — deneysel ölçekleme yasaları.
