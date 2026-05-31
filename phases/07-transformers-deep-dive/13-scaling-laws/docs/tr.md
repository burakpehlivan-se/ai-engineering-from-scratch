# Ölçekleme Yasaları (Scaling Laws)

> 2020 Kaplan makalesi şunu dedi: daha büyük model, daha düşük kayıp. 2022 Hoffmann makalesi şunu dedi: yetersiz eğitilmişsiniz. Hesaplama iki kovaya giriyor — parametreler ve token'lar — ve ayrım açıktan uzak.

**Tür:** Öğren
**Diller:** Python
**Önkoşullar:** Faz 7 · 05 (Tam Transformer), Faz 7 · 07 (GPT)
**Süre:** ~45 dakika

## Sorun

C FLOP eğitim hesaplamanız varsa ve en iyi modeli istiyorsanız, önünüzde iki düğme var:

1. **Kaç parametre (N)?** Daha büyük model, daha yüksek kapasite.
2. **Kaç eğitim token'ı (D)?** Daha fazla veri, kapasitenin daha iyi kullanımı.

FLOP'lar yaklaşık olarak `6 × N × D` ile ölçeklenir. N'yi yukarı ve D'yi aşağı veya D'yi yukarı ve N'yi aşağı itebilirsiniz. Hangisi daha iyi?

2022'den önce cevap "N'yi sert it" idi. GPT-3 (2020) ~300B token üzerinde eğitilmiş 175B parametreliydi. Parametre başına yaklaşık 1.7 token oranı. Kaplan ölçekleme yasaları bunu destekledi.

Hoffmann ve diğerleri (2022), Chinchilla adlı küçük bir model ailesini eğiterek farklı bir şey buldu: optimum oran **parametre başına 20 token**'a daha yakındır. GPT-3 10× yetersiz eğitilmişti. Chinchilla (70B parametre, 1.4T token), GPT-3'ü (175B, 300B token) 2,5× daha düşük çıkarım maliyetiyle her kıyaslama testinde geçti.

2026 Chinchilla'nın dünyasıdır — ancak önemli bir twist ile. Llama 3 8B, 15 trilyon token üzerinde eğitildi, parametre başına 1.875 token oranı. Chinchilla-optimal'in 94 katı. Ölçeklecek modeller için çıkarım maliyeti eğitim maliyetinden daha önemli olduğundan, daha küçük bir dağıtılabilir ayak izi için aşırı-eğitim (Chinchilla'yı aşan) 2026'nın varsayılanıdır.

## Kavram

![Chinchilla eğrileri: çeşitli N/D oranlarında kayıp vs hesaplama](../assets/scaling-laws.svg)

### Hoffmann yasası

Chinchilla makalesinden, kayıp şu şekilde takip eder:

```
L(N, D) = A / N^α + B / D^β + E
```

- `N` = parametreler (gömme-dışı).
- `D` = eğitim token'ları.
- `α ≈ 0.34`, `β ≈ 0.28` (yaklaşık simetrik).
- `E ≈ 1.69`, indirgenemez kayıp tavanı.
- `A ≈ 406`, `B ≈ 411`.

#### Açıklama
İki terim, ölçeklendirdiğinizde birbirine karşı takas eder. Sabit hesaplamada (C = 6ND) `N`'ye göre türev alıp çözün: optimize edilmiş parametre başına ~20 token.

İki terim ölçeklendirdiğinizde birbirine karşı takas eder. Sabit hesaplamada (C = 6ND) `N`'ye göre türev alıp çözün:

```
N_opt ≈ 0.6 × (C/6)^0.5
D_opt ≈ 0.6 × (C/6)^0.5
D_opt / N_opt ≈ 20
```

Hesaplama-optimal: parametre başına 20 token.

### Neden yine de aşırı-eğitim

Chinchilla-optimal, eğitim FLOP'ı başına eğitim kaybını en aza indirir. Ancak eğitim maliyetini bir kez ödersiniz; çıkarım maliyetini sonsuza kadar.

Ayda bir trilyon token hizmet veren bir sohbet botu için, çıkarım toplam maliyeti domine eder. Llama'nın yaklaşımı: daha küçük, daha uzun eğitin. 15T token'da 8B, derin bir şekilde çıkarım-optimaldir:

- Tüketici GPU'larına sığar.
- Gecikmesi 70B Chinchilla-optimal'in bir kesridir.
- Çoğu görev için yeterince yakın kalite.

DeepMind'in 2024 makalesi ("Aşırı-eğitim yeni optimaldir") bunu resmileştirdi. Çıkarımın domine ettiği iş yükleri için doğru oran, sunum hacmine bağlı olarak parametre başına 100–500 token'a daha yakındır.

### Ortaya çıkış (emergence) vs pürüzsüzlük

İddia: bazı beceriler (aritmetik, çoklu adım muhakeme, düşünce zincirini izleme) belirli bir ölçekte aniden "ortaya çıkar".

Schaeffer ve diğerleri (2023) bunun bir ölçüm yap-bozu (artifact) olduğunu savundu: ortaya çıkış metrikleri, temel logit'lerdeki pürüzsüz iyileşmeyi gizleyen kesintisiz puanlama (tam eşleşme, eşik doğruluğu) kullanır. Sürekli metrikler (çapraz-entropi) pürüzsüz eğriler gösterir.

2026'da uzlaşı: sürekli kayıp üzerinden yapılan tahminler güvenilirdir. Kıyaslama sıçramaları genellikle puanlama yap-bozudur. Bütçeleri sürekli metriklere göre planlayın.

### 2026 manzarası

Ölçekleme yasaları hala çalışır, ancak:

| Faktör | Nasıl değişti |
|--------|-------------|
| Veri kalitesi | "İyi" token'ları küratörlüğü (Phi tarzı) eğrileri >2× etkin hesaplama kadar kaydırır |
| MoE | Toplam parametre etkin FLOP'lardan ayrılır; etkin-FLOP başına ölçekleme yasaları |
| Sonraki eğitim | Bazı beceriler (talimat izleme, kod) ön-eğitimden ziyade SFT+RLHF ile kayar |
| Çoklu-modalite | Görüntü + metin token'ları birlikte ölçeklenir; modalite başına ayrı eğriler |
| Sentetik veri | Modeller eğitim verisi üretir; etkin hesaplama birikerek çarpabilir |

Muon optimize edicisi (Kimi Moonlight, 2024), eşleşen veride AdamW'a kıyasla ~2× etkin hesaplama kazancı gösterdi. Bazı 2026 eğitim çalışları varsayılan olarak Muon kullanır. Ölçekleme yasasındaki mutlak sabiti değiştirir, şeklini değil.

## İnşa Et

`code/main.py`'ye bakın. Chinchilla kayıp denklemini uyguluyoruz ve birkaç hesaplama bütçesinde hesaplama-optimal `(N, D)`'yi çözüyoruz.

### Adım 1: Chinchilla kaybı

```python
def chinchilla_loss(N, D, A=406.4, B=410.7, alpha=0.34, beta=0.28, E=1.69):
    return A / N ** alpha + B / D ** beta + E
```

#### Açıklama
Bu işlev, verilen parametre ve token sayıları için Chinchilla kaybını hesaplar. A ve B sabitleri, α ve β üsleri ve E indirgenemez kayıp terimi ile.
`L`'yi sabit `C = 6ND` üzerinde `(N, D)` kontur grafiği olarak çizin. Minimumu bulun.

### Adım 2: hesaplama-optimal sınır

`1e17`'den `1e25` FLOP'a kadar hesaplama bütçeleri için, `6ND = C` kısıtı altında kaybı en aza indiren `(N, D)`'yi bulun. `D/N ≈ 20` oranını doğrulayın.

### Adım 3: aşırı-eğitim maliyeti

Optimal N'nin 1/10'u olan 10× daha küçük bir modeli eğitmek için ödenen ekstra kaybı hesaplayın (optimal D'nin 10 katı). Karşılığında çıkarım FLOP tasarrufunu (N'ye orantılı) bildirin.

### Adım 4: gerçek modellerle karşılaştırma

GPT-3, Chinchilla, Llama 3 8B, DeepSeek-V3 (etkin parametreler) için bilinen `(N, D)` çiftlerini bırakın ve tahmin edilen vs bildirilen kaybı karşılaştırın.

## Kullan

Sınır bir modeli muhtemelen kendiniz eğitmeyeceksiniz. Ancak ölçekleme yasaları şunları söyler:

1. **İnceltmenizin yeterli verisi olup olmadığı.** Görev-özel veriniz temel modelin parametre başına 20 token'ının altındaysa, bir kayıp zemininde doygunluk bekleyin.
2. **Daha büyük bir temel model seçip seçmemeniz.** Bütçenizin çoğunu çıkarıma harcıyorsanız, daha küçük, daha uzun eğitilmiş bir modeli tercih edin.
3. **Getirilerin nerede azaldığı.** Chinchilla-optimal'in 1000× ötesinde, log-kayıp değişimleri gürültü haline gelir.

**2026'da araştırma yol haritası:**

- **Veri-kısıtlı rejim.** Web'in sınırlı sayıda yüksek kaliteli token'ı var (filtreleme sonrası ~5–10 trilyon İngilizce). Sınır ön-eğitimi bu tavana yaklaşıyor. Sentetik veri, çok dilli, çoklu-modalite ve RLHF ölçekli inceltme sonraki kaldıraçlar.
- **Hesaplama-çarpan numaraları.** Muon optimize edicisi, MoE, daha iyi küratörlük — her biri mutlak sabitleri, asimptotu kaydırır.
- **RL için ölçekleme yasaları.** Açık soru. Erken kanıtlar, RL örneklerinde kuvvet-yasası (power-law) olduğunu ancak ön-eğitimden çok farklı üslere sahip olduğunu gösteriyor.

## Teslim Et

`outputs/skill-training-budget-estimator.md`'ye bakın. Bu beceri, hesaplama bütçesi, dağıtım kısıtlamaları ve hedef kayıp verildiğinde yeni bir eğitim çalışması için `(N, D, saat, GPU)` seçer.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. `1e20`, `1e22`, `1e24` hesaplama bütçeleri için Chinchilla-optimal `(N, D)`'yi yazdırın. Gerçek model tablosuyla karşılaştırın.
2. **Orta.** Hoffmann kayıp-fonksiyonu-hesaplama eğrisini uygulayın. Hesaplama-optimal sınır için kaybı `log10(C)`'ye göre çizin. Yasamızın çapraz-entropide sonraki 0,1 azalma için `>10^28` FLOP gerektiğini ne zaman tahmin ettiğini belirleyin.
3. **Zor.** 5 küçük model (100K'dan 10M parametre) üzerinde kendi ölçekleme yasanızı sığdırın (fit). Aynı veri kümesi üzerinde eğitildi. `α` ve `E`'yi tahmin edin. Üsleriniz yayınlananlarla ne kadar uyumlu?

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Parametreler (N) | "Model boyutu" | Gömme-dışı ağırlık sayısı; kapasiteyi belirler. |
| Token'lar (D) | "Eğitim verisi" | Görülen eğitim token sayısı; parametrelerin ne kadar iyi kullanıldığını belirler. |
| Hesaplama (C) | "Harcanan FLOP" | Standart bir transformer için yaklaşık `6 × N × D`. |
| Chinchilla-optimal | "D/N ≈ 20" | Ön-eğitim FLOP'ı başına kaybı en aza indiren oran. |
| Aşırı-eğitim | "Chinchilla'yı aşan" | Ekstra eğitim FLOP'ı harcayarak çıkarım FLOP'larından tasarruf et; D/N >> 20. |
| İndirgenemez kayıp | "Zemin" | Ölçekleme yasasındaki `E` terimi; verinin kendisinin entropisi. |
| Ortaya çıkan beceri (Emergent capability) | "Ölçekte ani sıçramalar" | Genellikle bir puanlama yap-bozu; sürekli kayıp pürüzsüzdür. |
| Ekin hesaplama (Effective compute) | "Eğitim-verimliliği çarpanı" | Daha iyi veri / optimize edici / mimari, bir FLOP'un ne kadar uzağa gittiğini çarpar. |

## İleri Okuma

- [Kaplan ve diğerleri (2020). Scaling Laws for Neural Language Models](https://arxiv.org/abs/2001.08361) — ilk ölçekleme yasası makalesi; yetersiz eğitilmiş.
- [Hoffmann ve diğerleri (2022). Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556) — Chinchilla.
- [Schaeffer ve diğerleri (2023). Are Emergent Abilities of Large Language Models a Mirage?](https://arxiv.org/abs/2304.15004) — ortaya çıkışın ölçüm yap-bozu olduğu.
- [Sardana, Frankle (2024). Beyond Chinchilla-Optimal: Accounting for Inference in Language Model Scaling Laws](https://arxiv.org/abs/2401.00448) — neden Llama'nın aşırı-eğitimi iş yükü için doğru.
- [Jordan ve diğerleri (2024). Muon: An optimizer for hidden layers in neural networks](https://kellerjordan.github.io/posts/muon/) — 2× hesaplama çarpanı.
