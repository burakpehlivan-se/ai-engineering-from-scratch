# Görüntü Transformeri (Vision Transformers / ViT)

> Bir görüntü yama (patch) ızgarasıdır. Bir cümle token ızgarasıdır. Aynı transformer ikisini de yer.

**Tür:** İnşa Et
**Diller:** Python
**Önkoşullar:** Faz 7 · 05 (Tam Transformer), Faz 4 · 03 (CNN'ler), Faz 4 · 14 (Görüntü Transformer girişi)
**Süre:** ~45 dakika

## Sorun

2020'den önce, bilgisayar görmesi konvolüsyon (convolution) demekti. ImageNet, COCO ve algılama (detection) kıyaslama testlerindeki her SOTA bir CNN omurgası kullanıyordu. Transformer'lar dil içindi.

Dosovitskiy ve diğerleri (2020) — "Bir Görüntü 16x16 Kelimeye Değer" — konvolüsları tamamen bırakabileceğinizi gösterdi. Bir görüntüyü sabit boyutlu yamalara dilimleyin, her yamayı doğrusal olarak bir gömmeye projekte edin, diziyi vanilya bir transformer encoder'ına besleyin. Yeterli ölçekte (ImageNet-21k ön-eğitimi veya daha büyük), ViT tabanlı ResNet modellerini eşler veya geçer.

ViT, 2026'da daha geniş bir kalıbın başlangıcıydı: tek mimari, birçok modalite. Whisper ses tokenize eder. ViT görüntü tokenize eder. Robotik için eylem token'ları. Video için piksel token'ları. Transformer'ın umurunda değil — bir dizi besleyin ve öğrenir.

2026'ya kadar ViT ve soyluları (DeiT, Swin, DINOv2, ViT-22B, SAM 3) görmenin çoğuna sahiptir. CNN'ler hala kenar cihazlarında (edge) ve gecikmeye duyarlı görevlerde kazanır. Diğer her şeyin bir yerinde bir ViT vardır.

## Kavram

![Görüntü → yamalar → token'lar → transformer](../assets/vit.svg)

### Adım 1 — yamalara bölme (patchify)

`H × W × C` boyutundaki bir görüntüyü `N × (P·P·C)` düz yama dizisine bölün. Tipik kurulum: `224 × 224` görüntü, `16 × 16` yamalar → herbiri 768 değer olan 196 yama.

```
image (224, 224, 3) → 14 × 14 grid of 16x16x3 patches → 196 vectors of length 768
```

#### Açıklama
Yama boyutu kaldıraçtır. Daha küçük yamalar = daha fazla token, daha iyi çözünürlük, karesel dikkat maliyeti. Daha büyük yamalar = daha kaba, daha ucuz.

### Adım 2 — doğrusal gömme (linear embedding)

Öğrenilmiş tek bir matris, her düz yamayı `d_model` boyutuna projekte eder. `P` çekirdek (kernel) boyutlu ve `P` adım (stride) genişliğinde bir konvolüsyonla eşdeğerdir. PyTorch'ta bu kelimenin tam anlamıyla `nn.Conv2d(C, d_model, kernel_size=P, stride=P)`'dir — 2 satırlık bir uygulama.

### Adım 3 — `[CLS]` token'ı başına ekle, konumsal gömmeleri ekle

- Öğrenilebilir bir `[CLS]` token'ı başına ekleyin. Son gizli durumu (hidden state), sınıflandırma için kullanılan görüntü temsilidir.
- Öğrenilebilir konumsal gömmeler (ViT-orijinal) veya sinüzoidal 2D (sonraki varyantlar) ekleyin.
- 2024'ten sonra RoPE 2D'ye genişletildi, bazen açık gömmeler olmadan.

### Adım 4 — standart transformer encoder

`LayerNorm → Self-Attention → + → LayerNorm → MLP → +` bloklarını L kez yığın. BERT ile aynı. Görüntüye özel katman yok. Makalenin pedagojik sonuç noktası budur.

### Adım 5 — kafa

Sınıflandırma için: `[CLS]` gizli durumunu → doğrusal → softmax alin. DINOv2 veya SAM için `[CLS]`'i atın, yama gömmelerini doğrudan kullanın.

### Önemli varyantlar

| Model | Yıl | Değişiklik |
|-------|------|--------|
| ViT | 2020 | Orijinali. Sabit yama boyutu, tam küresel dikkat. |
| DeiT | 2021 | Distilasyon; yalnızca ImageNet-1k üzerinde eğitilebilir. |
| Swin | 2021 | Kaydırılmış pencereli hiyerarşik. Alt-karesel maliyet düzeltildi. |
| DINOv2 | 2023 | Kendi kendine denetimli (labelsiz). En iyi genel görüntü özellikleri. |
| ViT-22B | 2023 | 22B parametre; ölçekleme yasaları geçerli. |
| SigLIP | 2023 | ViT + dil çifti, sigmoid karşılaştırma kaybı. |
| SAM 3 | 2025 | Her şeyi bölütleme; ViT-Large + istem-başlatılabilir maske decoder'ı. |

### Neden biraz sürdü

ViT, CNN'lerin hiçbir endüksiyon önyargısını (translation invariance, locality) taşımadığı için CNN'lerle eşleşmek için *çok* fazla veriye ihtiyaç duyar. 100M'den fazla etiketli görüntü veya güçlü kendi kendine denetimli ön-eğitim olmadan, eşleşen hesaplamada CNN'ler hala kazanır. DeiT bunu 2021'de distilasyon numaralarıyla düzeltti; DINOv2 2023'te kendi kendine denetimle kalıcı olarak düzeltti.

## İnşa Et

`code/main.py`'ye bakın. Saf stdlib yamalama + doğrusal gömme + doğrulama kontrolleri. Eğitim yok — ViT herhangi bir gerçekçi ölçekte PyTorch ve saatlerce GPU süresi gerektirir.

### Adım 1: sahte görüntü

24 × 24 RGB görüntü, `(R, G, B)` demetlerinin satır listesi olarak. 6×6 yamalar → 16 yama, herbiri 108 boyutlu gömme vektörü.

### Adım 2: yamalara bölme

```python
def patchify(image, P):
    H = len(image)
    W = len(image[0])
    patches = []
    for i in range(0, H, P):
        for j in range(0, W, P):
            patch = []
            for di in range(P):
                for dj in range(P):
                    patch.extend(image[i + di][j + dj])
            patches.append(patch)
    return patches
```

#### Açıklama
Raster sırası: ızgara boyunca satır-başlı (row-major). Her ViT bu sıralamayı kullanır.

Raster sırası: ızgara boyunca satır-başlı. Her ViT bu sıralamayı kullanır.

### Adım 3: doğrusal gömme

Her düz yamayı rastgele `(patch_flat_size, d_model)` matrisi ile çarpın. `[CLS]` eklendikten sonra çıktı形状ının `(N_patches + 1, d_model)` olduğunu doğrulayın.

### Adım 4: gerçekçi ViT için parametre sayısını saydırın

ViT-Base parametre sayısını yazdırın: 12 katman, 12 baş, d=768, yama=16. ResNet-50 ile karşılaştırın (~25M). ViT-Base ~86M'a düşer. ViT-Large ~307M. ViT-Huge ~632M.

## Kullan

```python
from transformers import ViTImageProcessor, ViTModel
import torch
from PIL import Image

processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
model = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")

img = Image.open("cat.jpg")
inputs = processor(img, return_tensors="pt")
out = model(**inputs).last_hidden_state   # (1, 197, 768): [CLS] + 196 patches
cls_emb = out[:, 0]                       # image representation
```

#### Açıklama
ViT-Base, 2024 itibarıyla görüntü özellikleri için en yaygın temel modeldir. [CLS] token'ının son gizli durumu, görüntü temsili olarak kullanılır.

**DINOv2 gömmeleri 2026'da görüntü özellikleri için varsayılandır.** Omurgayı dondurun, küçük bir kafa eğitin. Sınıflandırma, getirme, algılama, resim yazısı (captioning) için çalışır. Meta'nın DINOv2 kontrol noktaları, metin-dışı görüntü görevlerinin her birinde CLIP'i geçer.

**Yama boyutu seçimi.** Küçük modeller 16×16 kullanır (ViT-B/16). Yoğun tahmin (bölümleme / segmentation) 8×8 veya 14×14 kullanır (SAM, DINOv2). Çok büyük modeller 14×14 kullanır.

## Teslim Et

`outputs/skill-vit-configurator.md`'ye bakın. Bu beceri, veri kümesi boyutu, çözünürlük ve hesaplama bütçesi verildiğinde yeni bir görüntü görevi için bir ViT varyantı ve yama boyutu seçer.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Yama sayısının `(H/P) * (W/P)`'ye eşit olduğunu ve düz yama boyutunun `P*P*C`'ye eşit olduğunu doğrulayın.
2. **Orta.** 2D sinüzoidal konumsal gömmeler uygulayın — her yamanın `satır` ve `sütun` bağımsız sinüzoidal kodları, birleştirilmiş. Bunları küçük bir PyTorch ViT'ine besleyin ve CIFAR-10'da öğrenilebilir konumsal gömmelere karşı doğruluğu karşılaştırın.
3. **Zor.** 3 katmanlı bir ViT (PyTorch) oluşturun, 4×4 yamalarla 1.000 MNIST görüntüsü üzerinde eğitin. Test doğruluğunu ölçün. Şimdi aynı 1.000 görüntü üzerinde DINOv2 ön-eğitimi ekleyin (basitleştirilmiş: encoder'ı maskeli yamalardan yama gömmelerini tahmin etmeye çalışın). Doğruluk artar mı?

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Yama (Patch) | "Görüntü-transformer token'ı" | Görüntünün `P × P × C` bölgesi için piksel değerlerinin düz vektörü. |
| Yamalama (Patchify) | "Dilimle + düzleştir" | Görüntüyü çakışmayan yamalara dilimle, herbirini bir vektöre düzleştir. |
| `[CLS]` token'ı | "Görüntü özeti" | Başa eklenmiş öğrenilebilir token; son gömmesi görüntü temsilidir. |
| Endüksiyon önyargısı (Inductive bias) | "Modelin varsayımı" | ViT, CNN'lerden daha az önkabul taşır; farkı kapatmak için daha fazla veriye ihtiyaç duyar. |
| DINOv2 | "Kendi kendine denetimli ViT" | Labelsiz, görüntü artırma + momentum öğretmenle eğitildi. 2026'da en iyi genel görüntü özellikleri. |
| SigLIP | "CLIP'in halefi" | ViT + dil encoder'ı sigmoid karşılaştırma kaybıyla eğitildi; eşleşen hesaplamada CLIP'ten iyi. |
| Swin | "Pencereli ViT" | Yerel dikkat + kaydırılmış pencereli hiyerarşik ViT; alt-karesel. |
| Kayıt token'ları (Register tokens) | "2023 hilesi" | Dikkat çukurlarını (sink) emen birkaç ekstra öğrenilebilir token; DINOv2 özelliklerini iyileştirir. |

## İleri Okuma

- [Dosovitskiy ve diğerleri (2020). An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929) — ViT makalesi.
- [Touvron ve diğerleri (2021). Training data-efficient image transformers & distillation through attention](https://arxiv.org/abs/2012.12877) — DeiT.
- [Liu ve diğerleri (2021). Swin Transformer: Hierarchical Vision Transformer using Shifted Windows](https://arxiv.org/abs/2103.14030) — Swin.
- [Oquab ve diğerleri (2023). DINOv2: Learning Robust Visual Features without Supervision](https://arxiv.org/abs/2304.07193) — DINOv2.
- [Darcet ve diğerleri (2023). Vision Transformers Need Registers](https://arxiv.org/abs/2309.16588) — DINOv2 için kayıt-token düzeltmesi.
