# Vision Transformers (ViT)

> Görüntüyü parçalara (patch) ayır, her parçayı bir kelime olarak ele al, standart bir transformer çalıştır. Arkana bakma.

**Tür:** Build
**Diller:** Python
**Ön Koşullar:** Phase 7 Lesson 02 (Self-Attention), Phase 4 Lesson 04 (Image Classification)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Patch embedding, öğrenilmiş konumsal gömme (learned positional embedding), sınıf token'ı (class token) ve transformer encoder bloklarını sıfırdan uygulayarak minimal bir ViT inşa etmek
- ViT'nin DeiT ve MAE kanıtlayana kadar neden devasa ön eğitim verisine (massive pretraining data) ihtiyaç duyduğu düşünüldüğünü açıklamak
- ViT, Swin ve ConvNeXt'i mimari ön kabulleri (architectural priors) açısından karşılaştırmak (hiçbiri, yerel pencere attention'ı, evrişim omurgası)
- Ön eğitimli bir ViT'yi `timm` kullanarak küçük bir veri kümesinde ince ayar (fine-tune) yapmak ve standart linear-probe / fine-tune reçetesini uygulamak

## Problem

On yıl boyunca evrişim (convolution), bilgisayarlı görü ile eşanlamlıydı. CNN'lerin güçlü sezgisel ön kabulleri (inductive biases) vardı — yerelellik, öteleme eşdeğişkenliği (translation equivariance) — ve kimse bunların yerine başka bir şey konabileceğini düşünmüyordu. Ta ki Dosovitskiy ve ark. (2020), düzleştirilmiş görüntü parçalarına uygulanan sade bir transformer'ın, hiçbir evrişim mekanizması olmadan, ölçek büyüdükçe en iyi CNN'lerle rekabet edebileceğini hatta geçebileceğini gösterene kadar.

İşin püf noktası "ölçek büyüdükçe"ydi. ImageNet-1k üzerinde ViT, ResNet'e kaybetti. ImageNet-21k veya JFT-300M'de ön eğitilip ImageNet-1k'de ince ayar yapılan ViT ise onu geçti. Sonuç şuydu: transformer'lar kullanışlı ön kabullere sahip değildi ama yeterli veriden öğrenebilirlerdi. Sonraki çalışmalar (DeiT, MAE, DINO), doğru eğitim reçeteleriyle — güçlü veri artırımı (augmentation), kendinden denetimli ön eğitim (self-supervised pretraining), damıtma (distillation) — ViT'lerin küçük verilerde de iyi eğitilebildiğini gösterdi.

2026 itibarıyla, saf CNN'ler uç cihazlarda hâlâ rekabetçi (ConvNeXt en güçlüsü), ancak transformer'lar diğer her alana hükmediyor: bölütleme (segmentation) (Mask2Former, SegFormer), nesne tespiti (detection) (DETR, RT-DETR), çok kipli (multimodal) (CLIP, SigLIP), video (VideoMAE, VJEPA). ViT blok yapısı bilinmesi gereken yapıdır.

## Konsept

### Pipeline

```mermaid
flowchart LR
    IMG["Görüntü<br/>(3, 224, 224)"] --> PATCH["Patch embedding<br/>conv 16x16 s=16<br/>-> (768, 14, 14)"]
    PATCH --> FLAT["Düzleştir<br/>(196, 768) token"]
    FLAT --> CAT["[CLS] token'ını<br/>başa ekle"]
    CAT --> POS["Öğrenilmiş konumsal<br/>gömme ekle"]
    POS --> ENC["N transformer<br/>encoder bloğu"]
    ENC --> CLS["[CLS] token<br/>çıktısını al"]
    CLS --> HEAD["MLP sınıflandırıcı"]

    style PATCH fill:#dbeafe,stroke:#2563eb
    style ENC fill:#fef3c7,stroke:#d97706
    style HEAD fill:#dcfce7,stroke:#16a34a
```

Yedi adım. Parçalar -> token -> attention -> sınıflandırıcı. Her varyant (DeiT, Swin, ConvNeXt, MAE ön eğitimi) yediden birini veya ikisini değiştirir, gerisini olduğu gibi bırakır.

#### Açıklama
Pipeline şeması: Görüntü önce patch embedding ile parçalanır, ardından düzleştirilip [CLS] token eklenir, konumsal gömme (positional embedding) eklenir, N adet transformer encoder bloğundan geçirilir ve [CLS] token çıktısı MLP sınıflandırıcıya verilir.

### Patch embedding

İlk evrişim (conv) işin sırrıdır. Çekirdek boyutu 16, adım (stride) 16, yani 224x224'lik bir görüntü 16x16'lık parçalardan oluşan 14x14'lük bir ızgaraya dönüşür ve her parça 768 boyutlu bir gömme (embedding) uzayına yansıtılır. Bu tek evrişim, hem parçalama (patchify) hem de doğrusal yansıtma (linear projection) işlemini yapar.

```
Giriş:  (3, 224, 224)
Conv (3 -> 768, k=16, s=16, padding yok):
Çıktı: (768, 14, 14)
Uzamsal düzleştirme: (196, 768)
```

#### Açıklama
196 parça = 196 token. Her token'ın öznitelik boyutu 768 (ViT-B), 1024 (ViT-L) veya 1280 (ViT-H)'dir.

### Sınıf token'ı (Class token)

Diziye başa eklenen tek bir öğrenilmiş vektör:

```
token = [CLS; patch_1; patch_2; ...; patch_196]   boyut (197, 768)
```

#### Açıklama
N transformer bloğundan sonra, `[CLS]` çıktısı küresel görüntü temsilidir (global image representation). Sınıflandırma başlığı (classification head) sadece bu vektörü okur.

### Konumsal gömme (Positional embedding)

Transformer'ların doğası gereği uzamsal konum kavramı yoktur. Her token'a öğrenilmiş bir vektör eklenir:

```
token = token + learned_pos_embedding   (yine boyut (197, 768))
```

#### Açıklama
Gömme, modelin bir parametresidir; gradyan tabanlı eğitim onu 2B görüntü yapısına uyarlar. Sinüzoidal 2B alternatifleri mevcuttur ancak pratikte nadiren kullanılır.

### Transformer encoder bloğu

Standart. Multi-head self-attention, MLP, artık bağlantılar (residual connections), ön LayerNorm (pre-LayerNorm).

```
x = x + MSA(LN(x))
x = x + MLP(LN(x))

MLP iki katmanlı ve GELU'lu: Linear(d -> 4d) -> GELU -> Linear(4d -> d)
```

#### Açıklama
ViT-B/16, her biri 12 attention başlıklı (head) 12 bloktan oluşur, toplam 86M parametre.

### Neden ön-LN (pre-LN)

İlk transformer'lar sonra-LN (post-LN) (`x = LN(x + sublayer(x))`) kullanırdı ve ısınma (warmup) olmadan 6-8 katmanı geçmekte zorlanırdı. Ön-LN (`x = x + sublayer(LN(x))`) ısınma gerektirmeden daha derin ağları kararlı bir şekilde eğitir. Her ViT ve her modern LLM ön-LN kullanır.

### Parça boyutu ödünleşimi (Patch size trade-off)

- 16x16 parça -> 196 token, standart.
- 32x32 parça -> 49 token, daha hızlı ama daha düşük çözünürlük.
- 8x8 parça -> 784 token, daha ince ama O(n^2) attention maliyeti çok artar.

Büyük parçalar = daha az token = daha hızlı ama daha az uzamsal detay. SwinV2, hiyerarşik pencerelerde 4x4 parça kullanır.

### DeiT'in ImageNet-1k'de ViT eğitme reçetesi

Orijinal ViT, CNN'leri geçmek için JFT-300M'ye ihtiyaç duyuyordu. DeiT (Touvron ve ark., 2020), ViT-B'yi sadece ImageNet-1k ile %81.8 top-1 doğruluğuna dört değişiklikle ulaştırdı:

1. Yoğun veri artırımı: RandAugment, Mixup, CutMix, Random Erasing.
2. Stokastik derinlik (stochastic depth — eğitim sırasında rastgele blokları tamamen düşürme).
3. Tekrarlı artırım (repeated augmentation — aynı görüntüyü batch başına 3 kez örnekleme).
4. Bir CNN öğretmenden damıtma (distillation) (isteğe bağlı, doğruluğu daha da artırır).

Her modern ViT eğitim reçetesi DeiT'ten türemiştir.

### Swin vs ConvNeXt

- **Swin** (Liu ve ark., 2021) — pencere tabanlı attention. Her blok, yerel bir pencere içinde attention yapar; dönüşümlü bloklar bilgiyi pencereler arasında karıştırmak için pencereyi kaydırır. Attention operatörünü korurken CNN benzeri bir yerelellik ön kabulünü geri getirir.
- **ConvNeXt** (Liu ve ark., 2022) — Swin'in mimari seçimlerini (depthwise conv, LayerNorm, GELU, ters çevrilmiş darboğaz) eşleşecek şekilde yeniden tasarlanmış CNN. Aradaki farkın "attention vs evrişim" değil, "modern eğitim reçetesi + mimari" olduğunu gösterdi.

2026'da ConvNeXt-V2 ve Swin-V2'nin ikisi de üretim kalitesindedir; doğru seçim, çıkarım (inference) yığınınıza (ConvNeXt uç cihazlar için daha iyi derlenir) ve ön eğitim külliyatınıza bağlıdır.

### MAE ön eğitimi

Maskeli Otomatik Kodlayıcı (Masked Autoencoder — He ve ark., 2022): parçaların %75'ini rastgele maskele, kodlayıcıyı (encoder) sadece görünen %25'i işleyecek şekilde eğit, küçük bir kod çözücüyü (decoder) kodlayıcının çıktısından maskelenmiş parçaları yeniden inşa edecek şekilde eğit. Ön eğitimden sonra kod çözücüyü at ve kodlayıcıya ince ayar yap.

MAE, ViT'yi sadece ImageNet-1k ile eğitilebilir hale getirir, en güncel başarımı (SOTA) yakalar ve mevcut varsayılan kendinden denetimli (self-supervised) reçetedir.

## Build It

### Adım 1: Patch embedding

```python
import torch
import torch.nn as nn

class PatchEmbedding(nn.Module):
    def __init__(self, in_channels=3, patch_size=16, dim=192, image_size=64):
        super().__init__()
        assert image_size % patch_size == 0
        self.proj = nn.Conv2d(in_channels, dim, kernel_size=patch_size, stride=patch_size)
        num_patches = (image_size // patch_size) ** 2
        self.num_patches = num_patches

    def forward(self, x):
        x = self.proj(x)
        return x.flatten(2).transpose(1, 2)
```

#### Açıklama
Bir evrişim, bir düzleştirme, bir transpoz. Görüntüden token'a geçiş adımının tamamı budur.

### Adım 2: Transformer bloğu

Ön-LN, çok başlı self-attention (multi-head self-attention), GELU'lu MLP, artık bağlantılar.

```python
class Block(nn.Module):
    def __init__(self, dim, num_heads, mlp_ratio=4, dropout=0.0):
        super().__init__()
        self.ln1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.ln2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, dim * mlp_ratio),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim * mlp_ratio, dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        a, _ = self.attn(self.ln1(x), self.ln1(x), self.ln1(x), need_weights=False)
        x = x + a
        x = x + self.mlp(self.ln2(x))
        return x
```

#### Açıklama
`nn.MultiheadAttention`, başlıklara ayırma, ölçeklendirilmiş nokta çarpımı (scaled dot-product) ve çıktı yansıtmasını (output projection) halleder. `batch_first=True` ile şekiller `(N, seq, dim)` olur.

### Adım 3: ViT

```python
class ViT(nn.Module):
    def __init__(self, image_size=64, patch_size=16, in_channels=3,
                 num_classes=10, dim=192, depth=6, num_heads=3, mlp_ratio=4):
        super().__init__()
        self.patch = PatchEmbedding(in_channels, patch_size, dim, image_size)
        num_patches = self.patch.num_patches
        self.cls_token = nn.Parameter(torch.zeros(1, 1, dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches + 1, dim))
        self.blocks = nn.ModuleList([
            Block(dim, num_heads, mlp_ratio) for _ in range(depth)
        ])
        self.ln = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, num_classes)
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)

    def forward(self, x):
        x = self.patch(x)
        cls = self.cls_token.expand(x.size(0), -1, -1)
        x = torch.cat([cls, x], dim=1)
        x = x + self.pos_embed
        for blk in self.blocks:
            x = blk(x)
        x = self.ln(x[:, 0])
        return self.head(x)

vit = ViT(image_size=64, patch_size=16, num_classes=10, dim=192, depth=6, num_heads=3)
x = torch.randn(2, 3, 64, 64)
print(f"output: {vit(x).shape}")
print(f"params: {sum(p.numel() for p in vit.parameters()):,}")
```

#### Açıklama
Yaklaşık 2.8M parametre — CPU'da çalıştırılabilen küçük bir ViT. Gerçek ViT-B 86M'dir; aynı sınıf tanımı `dim=768, depth=12, num_heads=12` ile kullanılır.

### Adım 4: Sağlık kontrolü — tek görüntü çıkarımı

```python
logits = vit(torch.randn(1, 3, 64, 64))
print(f"logits: {logits}")
print(f"probs:  {logits.softmax(-1)}")
```

#### Açıklama
Hatasız çalışmalıdır. Olasılıklar toplamı 1 olur.

## Use It

`timm`, ImageNet ön eğitimli ağırlıklarla her ViT varyantını sunar. Tek satır:

```python
import timm

model = timm.create_model("vit_base_patch16_224", pretrained=True, num_classes=10)
```

#### Açıklama
`timm`, 2026'da vision transformer'lar için üretim standardıdır. ViT, DeiT, Swin, Swin-V2, ConvNeXt, ConvNeXt-V2, MaxViT, MViT, EfficientFormer ve düzinelercesini aynı API altında destekler.

Çok kipli (multimodal) çalışmalar (görüntü + metin) için `transformers`, CLIP, SigLIP, BLIP-2, LLaVA sağlar. Bunların hepsinde görüntü kodlayıcı bir ViT varyantıdır.

## Ship It

Bu ders şunları üretir:

- `outputs/prompt-vit-vs-cnn-picker.md` — veri kümesi boyutu, hesaplama ve çıkarım yığınına göre ViT, ConvNeXt veya Swin arasında seçim yapan bir prompt.
- `outputs/skill-vit-patch-and-pos-embed-inspector.md` — bir ViT'nin patch embedding ve positional embedding şekillerinin modelin beklenen dizi uzunluğuyla eşleştiğini doğrulayan, en yaygın taşıma (porting) hatalarını yakalayan bir skill.

## Alıştırmalar

1. **(Kolay)** Küçük ViT üzerinden bir ileri geçişte (forward pass) her ara tensor'ün şeklini yazdırın. Şunları doğrulayın: girdi `(N, 3, 64, 64)` -> parçalar `(N, 16, 192)` -> CLS ile `(N, 17, 192)` -> sınıflandırıcı girdisi `(N, 192)` -> çıktı `(N, num_classes)`.
2. **(Orta)** Ön eğitimli bir `timm` ViT-S/16'yı Ders 4'teki sentetik CIFAR veri kümesinde ince ayar yapın. Aynı veride ResNet-18 ince ayarıyla karşılaştırın. Eğitim süresini ve nihai doğruluğu raporlayın.
3. **(Zor)** Küçük ViT için MAE ön eğitimi uygulayın: parçaların %75'ini maskeleyin, kodlayıcı + maskelenmiş parçaları yeniden inşa edecek küçük bir kod çözücüyü eğitin. Ön eğitim öncesi ve sonrası sentetik veride linear-probe doğruluğunu değerlendirin.

## Anahtar Terimler

| Terim | Ne denir | Gerçek anlamı |
|-------|----------|---------------|
| Patch embedding | "İlk evrişim" | Çekirdek boyutu = adım = parça boyutu olan bir evrişim; görüntüyü token gömmelerinden oluşan bir ızgaraya dönüştürür |
| Class token | "[CLS]" | Token dizisinin başına eklenen öğrenilmiş bir vektör; nihai çıktısı küresel görüntü temsilidir |
| Positional embedding | "Öğrenilmiş konum" | Her token'a eklenen öğrenilmiş bir vektör; transformer her parçanın nereden geldiğini bilir |
| Pre-LN | "LayerNorm alt katmandan önce" | Kararlı transformer varyantı: `x + sublayer(LN(x))`, `LN(x + sublayer(x))` yerine |
| Multi-head attention | "Paralel attention" | Standart transformer attention'ı num_heads bağımsız alt uzaya böler, sonra birleştirir |
| ViT-B/16 | "Base, patch 16" | Kanonik boyut: dim=768, depth=12, heads=12, patch_size=16, image=224; ~86M parametre |
| DeiT | "Data-efficient ViT" | Sadece ImageNet-1k ile güçlü artırım kullanarak eğitilmiş ViT; büyük ön eğitim veri kümelerinin zorunlu olmadığını kanıtladı |
| MAE | "Maskeli otomatik kodlayıcı" | Kendinden denetimli ön eğitim: parçaların %75'ini maskele, yeniden inşa et; baskın ViT ön eğitim reçetesi |

## Daha Fazla Okuma

- [An Image is Worth 16x16 Words (Dosovitskiy ve ark., 2020)](https://arxiv.org/abs/2010.11929) — ViT makalesi
- [DeiT: Data-efficient Image Transformers (Touvron ve ark., 2020)](https://arxiv.org/abs/2012.12877) — ViT'yi sadece ImageNet-1k ile eğitme yöntemi
- [Masked Autoencoders are Scalable Vision Learners (He ve ark., 2022)](https://arxiv.org/abs/2111.06377) — MAE ön eğitimi
- [timm dökümantasyonu](https://huggingface.co/docs/timm) — üretimde kullanacağınız her vision transformer için referans
