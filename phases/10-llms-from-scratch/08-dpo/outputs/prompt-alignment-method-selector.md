---
name: prompt-alignment-method-selector
description: Kullanım senaryonuz için doğru hizalama yöntemini seçin (SFT, RLHF, DPO, KTO, ORPO, SimPO)
version: 1.0.0
phase: 10
lesson: 8
tags: [alignment, dpo, rlhf, kto, orpo, simpo, preference-optimization, fine-tuning]
---

# Hizalama Yöntemi Seçici

Bir dil modeli için hizalama yöntemi seçerken, verilerinizi, hesaplama ve kalite gereksinimlerinizi değerlendirmek ve kısıtlamalarınıza en uygun yöntemi seçmek için bu çerçeveyi kullanın.

## Girdi Gereksinimleri

Şunları sağlayın:
- **Temel model** (örneğin, Llama 3 8B, Mistral 7B, Qwen 2.5 72B)
- **Başlangıç noktası** (temel model mi, yoksa zaten SFT uygulandı mı?)
- **Mevcut veri** (talimat çiftleri, tercih çiftleri, eşleştirilmemiş derecelendirmeler veya hiçbiri)
- **Hesaplama bütçesi** (GPU saatleri, GPU sayısı)
- **Kalite hedefi** (prototip için yeterli, açık kaynak ile rekabetçi, son teknoloji)
- **Zaman çizelgesi** (günler, haftalar, aylar)

## Karar Matrisi

### Hızlı Seçim

| Durumunuz | Önerilen Yöntem | Neden |
|---------------|-------------------|-----|
| Tercih verisi yok, yalnızca talimat çiftleri | Yalnızca SFT | Tercih sinyali olmadan hizalayamazsınız |
| < 5,000 tercih çifti, sınırlı hesaplama | DPO | Daha basit pipeline, küçük veriyle iyi çalışır |
| Eşleştirilmemiş geri bildirim (yukarı/aşağı oy) | KTO | İkili karşılaştırma olmadan çalışan tek yöntem |
| Hizalama tek bir eğitim turunda istiyorum | ORPO | SFT + hizalamayı birleştirir, referans model gerektirmez |
| Bellek kısıtlı (referans model sığmıyor) | SimPO | Referans modele gerek yok |
| Büyük ölçekli, çok amaçlı hizalama | RLHF (PPO) | Ayrı ödül modeli karmaşık tercihleri yakalar |
| Çevrimiçi veriyle yinelemeli hizalama | RLHF (PPO) | Döngü içinde üretebilir, puanlayabilir ve yeniden eğitebilir |
| RLHF sonrası iyileştirme | DPO | RLHF modelini hedefli tercihlerle ince ayar yapın |

### Detaylı Karşılaştırma

| Yöntem | Veri Gereksinimi | Bellekteki Modeller | Eğitim Döngüleri | Stabilite | En İyi Ölçek |
|--------|-----------------|-----------------|----------------|-----------|------------|
| SFT | Talimat çiftleri (10K+) | 1 | 1 | Yüksek | Herhangi |
| RLHF | Tercih çiftleri (20K+) | 3-4 | 3 | Düşük | Büyük (70B+) |
| DPO | Tercih çiftleri (5K+) | 2 | 2 (SFT + DPO) | Yüksek | Küçük-Orta (7B-70B) |
| KTO | Eşleştirilmemiş derecelendirmeler (5K+) | 2 | 2 (SFT + KTO) | Yüksek | Herhangi |
| ORPO | Tercih çiftleri (10K+) | 1 | 1 | Yüksek | Küçük-Orta |
| SimPO | Tercih çiftleri (5K+) | 1 | 2 (SFT + SimPO) | Yüksek | Küçük-Orta |

## Yönteme Özgü Yapılandırma

### SFT (Denetimli İnce Ayar)

- **Ne zaman durulur**: 1-3 epoch sonra veya doğrulama kaybı azalmayı bıraktığında
- **Anahtar hiperparametre**: Öğrenme oranı (1e-5 ile 5e-5, daha büyük modeller için daha düşük)
- **Kritik detay**: Kayıp fonksiyonunda talimat token'larını maskeleyin
- **Tuzak**: 3'ten fazla epoch ezberlemeye neden olur; %2-5 ön-eğitim verisi karıştırın

### RLHF (PPO)

- **Ne zaman kullanılır**: 20K+ karşılaştırma çiftiniz var, çok amaçlı hizalama gerekiyor veya yinelemeli çevrimiçi öğrenme istiyorsunuz
- **Anahtar hiperparametreler**: KL katsayısı (0.01-0.05), PPO kırpma oranı (0.1-0.3), öğrenme oranı (5e-6 ile 3e-5)
- **Kritik detay**: Ödül modeli >= politika modeli boyutunda olmalı
- **Tuzak**: PPO kararsızdır; KL diverjansını ve ödül eğrilerini sürekli izleyin

### DPO (Doğrudan Tercih Optimizasyonu)

- **Ne zaman kullanılır**: Tercih çiftleriniz var ve RLHF'den daha basit bir pipeline istiyorsunuz
- **Anahtar hiperparametre**: Beta (0.1-0.5; düşük = referanstan daha fazla sapmaya izin verir)
- **Kritik detay**: Referans model, SFT kontrol noktasının dondurulmuş bir kopyası olmalı
- **Tuzak**: Beta'ya çok hassas; [0.05, 0.1, 0.2, 0.5] üzerinde tarama yapın

### KTO (Kahneman-Tversky Optimizasyonu)

- **Ne zaman kullanılır**: Yalnızca ikili karşılaştırmalar olmadan "iyi" veya "kötü" etiketleriniz var
- **Anahtar hiperparametre**: Beta (DPO ile aynı), kayıp kaçınma çarpanı (kötü yanıtlarda 1.5x)
- **Kritik detay**: Kabaca dengeli iyi/kötü örnekler gerekir (%40-60 dağılım)
- **Tuzak**: Çiftler olmadan gradyan sinyali daha zayıftır; DPO'dan daha fazla veri gerekebilir

### ORPO (Olasılık Oranı Tercih Optimizasyonu)

- **Ne zaman kullanılır**: SFT'yi tamamen atlayıp temelden hizalanmış modele doğrudan geçmek istiyorsunuz
- **Anahtar hiperparametre**: Lambda (tercih teriminin SFT terimine ağırlığı)
- **Kritik detay**: Tek bir veri kümesinde hem talimat etiketleri HEM DE tercih çiftleri gerekir
- **Tuzak**: Birleşik hedefi dengelemek zor olabilir; SFT kaybı baskınsa hizalama zayıftır

### SimPO (Basit Tercih Optimizasyonu)

- **Ne zaman kullanılır**: Referans model tutamadığınız bellek kısıtlı kurulum
- **Anahtar hiperparametre**: Beta, gamma (uzunluk normalleştirme üssü)
- **Kritik detay**: Uzunluk normalleştirme, modelin kısa yanıtları tercih etmesini önler
- **Tuzak**: Referans model çıpası olmadan model daha fazla sapabilir; dikkatlice izleyin

## Pipeline Şablonları

### Şablon 1: Hızlı Prototip (1-2 gün)

```
Temel Model -> SFT (1 epoch, 10K örnek) -> DPO (3 epoch, 5K çift)
```

Hesaplama: 7B model için A100'de ~4 GPU-saat
Kalite: Sağlam talimat takibi, temel tercih hizalaması

### Şablon 2: Üretim Kalitesi (1-2 hafta)

```
Temel Model -> SFT (2 epoch, 50K örnek) -> DPO (5 epoch, 20K çift) -> Değerlendirme -> Yineleme
```

Hesaplama: 7B için ~40 GPU-saat, 70B için ~200 GPU-saat
Kalite: Açık kaynak RLHF modelleriyle rekabetçi

### Şablon 3: Son Teknoloji (1-3 ay)

```
Temel Model -> SFT (2 epoch, 100K+ örnek) -> RLHF (PPO, 50K+ çift) -> DPO (hedefli iyileştirme) -> Değerlendirme -> Yineleme
```

Hesaplama: 70B için ~500+ GPU-saat
Kalite: Sınır modeli hizalamasına yaklaşan

### Şablon 4: Asgari Veri (1-2 gün)

```
Temel Model -> SFT (1 epoch, 5K örnek) -> KTO (kullanıcılardan eşleştirilmemiş yukarı/aşağı oy)
```

Hesaplama: 7B için ~2 GPU-saat
Kalite: Asgari veri toplama yüküyle yalnızca SFT'den daha iyi

## Değerlendirme Protokolü

Hizalama sonrasında şu boyutlarda değerlendirin:

1. **Tercih kazanma oranı**: 200+ test promptunda hizalanmış modeli SFT modeliyle insan hakemlerle karşılaştırın. Hedef: > %60 kazanma oranı.
2. **Kıyaslama tutma**: MMLU, HumanEval veya alana özgü kıyaslamalar. SFT temelinden > %5 düşmemelidir.
3. **MT-Bench veya AlpacaEval**: Standart hizalama kalitesi kıyaslamaları. Yayınlanmış temel değerlerle karşılaştırın.
4. **Güvenlik değerlendirmesi**: Düşmanca promptlara, jailbreak'lere ve zararlı istek kategorilerine karşı test edin.
5. **Yanıt çeşitliliği**: 100 prompt üzerinde yanıtların entropisini ölçün. Düşük entropi = mod çöküşü.

## Yaygın Başarısızlık Modları

| Belirti | Neden | Yönteme Özgü Çözüm |
|---------|-------|-------------------|
| Ayrıntılı, doldurulmuş yanıtlar | Ödül modeli / örtük ödül uzunluğu tercih ediyor | DPO: beta'yı artırın. RLHF: uzunluk cezası ekleyin. SimPO: gamma'yı ayarlayın. |
| Model her şeye katılıyor | Tercih verisi önyargısından kaynaklanan dalkavukluk (sycophancy) | Doğru yanıtın kullanıcıyla aynı fikirde olmadığı tercih çiftleri ekleyin |
| Zararsız istekleri reddediyor | Güvenlik verisi üzerinde aşırı hizalama | Güvenlik örneği oranını azaltın, daha fazla zararsız-red çifti ekleyin |
| Çıktılar SFT ile neredeyse aynı | Beta çok yüksek (DPO/KTO) veya KL katsayısı çok yüksek (PPO) | Beta / KL katsayısını düşürün; model öğrenmiyor |
| Eğitim kaybı salınıyor | Öğrenme oranı çok yüksek veya yetersiz veri | Öğrenme oranını 2-3x düşürün; tercih verisini artırın |
