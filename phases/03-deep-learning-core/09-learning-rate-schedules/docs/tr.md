> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/09-learning-rate-schedules/docs/en.md)

# Öğrenme Hızı Programları ve Isınma (Warmup)

> Öğrenme hızı en önemli tek hiperparametredir. Mimari değil. Veri seti boyutu değil. Aktivasyon fonksiyonu değil. Öğrenme hızı. Başka hiçbir şeyi ayarlamayacaksanız, bunu ayarlayın.

**Tür:** Build
**Diller:** Python
**Ön Koşullar:** Ders 03.06 (Optimize Ediciler), Ders 03.08 (Ağırlık Başlatma)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Sabit, adım azaltmalı, kosinüs tavlamalı, ısınma + kosinüs ve 1cycle öğrenme hızı programlarını sıfırdan uygulayın
- Öğrenme hızı seçiminin üç başarısızlık modunu gösterin: ıraksama (çok yüksek), takılma (çok düşük), salınım (azaltma yok)
- Adam tabanlı optimize edicilerde ısınmanın neden gerekli olduğunu ve erken eğitimi nasıl stabilize ettiğini açıklayın
- Beş programı aynı görevde karşılaştırın ve eğitim bütçesine göre doğru programı seçin

## Sorun

Öğrenme hızını 0.1 yapın. Eğitim ıraksar — kayıp 3 adımda sonsuza gider. 0.0001 yapın. Eğitim sürünür — 100 epoch sonra model rastgele halden zar zor ayrılmıştır. 0.01 yapın. 50 epoch çalışır, sonra kayıp salınır.

Optimal öğrenme hızı sabit değildir. Erken aşamalarda büyük adımlar, geç aşamalarda küçük adımlar istersiniz. Son üç yılda yayınlanan her büyük model bir öğrenme hızı programı kullanır.

## Kavram

### Sabit Öğrenme Hızı
En basit. Her adımda aynı lr. Nadiren optimal.

### Adım Azaltmalı (Step Decay)
lr = lr₀ × γ^(floor(epoch/step_size)). ResNet-50 bunu kullandı. Sorun: geçişler ani, kayıp sıçrayabilir.

### Kosinüs Tavlamalı (Cosine Annealing)
lr = lr_min + 0.5 × (lr_max - lr_min) × (1 + cos(π × t/T)). Çoğu modern eğitimin varsayılanıdır.

### Isınma (Warmup)
Adam'ın gradyan istatistikleri kararlı hale gelene kadar küçük lr ile başlayın:
lr(t) = lr_max × (t / warmup_steps). Tipik olarak toplam adımların %1-5'i.

### Doğrusal Isınma + Kosinüs Azaltma
Modern varsayılan. Llama, GPT, PaLM ve çoğu modern transformer bunu kullanır.

### 1cycle Politikası
Leslie Smith (2018): eğitimin ilk yarısında lr'yi artır, ikinci yarısında azalt. Yüksek lr düzenleme görevi görür.

## Uygulama

Aşağıdaki kodları `code/main.py` içinde inşa edin: `constant_schedule`, `step_decay_schedule`, `cosine_schedule`, `warmup_cosine_schedule`, `one_cycle_schedule`, tüm programların görselleştirmesi ve hız karşılaştırması.

## Kullanım

PyTorch `torch.optim.lr_scheduler` içinde programlar sunar:
```python
scheduler = CosineAnnealingLR(optimizer, T_max=1000, eta_min=1e-5)
```
HuggingFace: `get_cosine_schedule_with_warmup` Llama/GPT ince ayarında yaygındır.

## Temel Terimler

| Terim | Gerçekte ne anlama geldiği |
|-------|--------------------------|
| Öğrenme hızı | Gradyanı çarparak parametre güncelleme boyutunu belirleyen skaler |
| Program | Eğitim adımını öğrenme hızına eşleyen fonksiyon |
| Isınma | Optimize edici istatistikleri stabilize olana kadar lr'yi artırma |
| Kosinüs tavlamalı | lr'yi kosinüs eğrisiyle lr_max'tan lr_min'a düşürme |
| 1cycle | lr'yi önce artırıp sonra azaltma |
| LR aralık testi | Iraksamadan hemen önceki optimal lr'yi bulma |

## Alıştırmalar

1. Üstel azaltma uygulayın ve kosinüsle karşılaştırın
2. Öğrenme hızı aralık testi (LR range test) uygulayın
3. Isınma uzunluğunu değiştirerek kararlılığı test edin
4. Kosinüs + sıcak yeniden başlatma (SGDR) uygulayın
5. Kaybı izleyip lr'yi otomatik ayarlayan "program cerrahı" inşa edin
