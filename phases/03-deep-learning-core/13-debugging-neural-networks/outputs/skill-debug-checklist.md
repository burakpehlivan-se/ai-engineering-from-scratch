---
name: skill-debug-checklist
description: Sinir ağı eğitim hatalarını ayıklamak için karar ağacı kontrol listesi
version: 1.0.0
phase: 3
lesson: 13
tags: [hata-ayıklama, sinir-ağları, eğitim, tanılama, derin-öğrenme]
---

# Sinir Ağı Hata Ayıklama Kontrol Listesi

Eğitim yanlış gittiğinde sistematik hata ayıklama protokolü. Bunları sırayla işleyin — hataların çoğu ilk 3 adımda yakalanır.

## Eğitimden önce (hataları önle)

1. Model mimarisini ve parametre sayısını yazdır. Boyut verileriniz için mantıklı mı?
2. Rastgele girdiyle tek bir ileri geçiş çalıştır. Çıktı şekli hedef şeklinizle eşleşiyor mu?
3. Etiketlerin doğru dtype olduğunu kontrol et (CrossEntropyLoss Long gerektirir, BCELoss Float gerektirir)
4. Veri normalleştirmesini doğrula: girdilerin ortalaması 0'a yakın ve std'si 1'e yakın olmalıdır
5. 5 rastgele (girdi, etiket) çifti yazdır. Etiketler beklediğiniz şeyle eşleşiyor mu?
6. Eğitim/test bölünmesinde kopya örnek olmadığını onayla

## Tek-toplu-iş-aşırı-uyum testi (60 saniye, hataların %80'ini yakalar)

1. Eğitim setinizden 8-32 örnek alın
2. Makul bir öğrenme hızıyla 200 adım eğitin
3. Kayıp 0'a yaklaşmalı. Eğitim doğruluğu %100'e ulaşmalı
4. Başarısız olursa: hata modelinizde, kayıp fonksiyonunuzda veya eğitim döngünüzde — verilerinizde veya hiperparametrelerinizde değil
5. Geçerse: tam eğitime geç

## Kayıp azalmıyor

1. Öğrenme hızını kontrol et. 3 değer dene: mevcut/10, mevcut, mevcut*10
2. Katman başına gradyan normlarını yazdır. Hepsi sıfırsa, ağ ölüdür veya grafik ayrılmıştır
3. Parametrelerde `requires_grad=True` olduğunu kontrol et. `loss.backward()` çağrıldığını kontrol et
4. `loss.backward()` çağrılmadan önce `optimizer.zero_grad()` çağrıldığını kontrol et
5. `loss.backward()` çağrıldıktan sonra `optimizer.step()` çağrıldığını kontrol et
6. Model parametrelerinin optimize ediciye geçirildiğini doğrula: `optimizer = Adam(model.parameters())`

## Kayıp NaN veya Inf

1. Öğrenme hızını 10x azalt
2. Tüm log() çağrılarına epsilon ekle: `torch.log(x + 1e-7)`
3. Tüm bölmelere epsilon ekle: `x / (y + 1e-8)`
4. Tahminleri sıkıştır (clamp): BCE kaybından önce `torch.clamp(pred, 1e-7, 1 - 1e-7)`
5. Tam işlemi bulmak için `torch.autograd.detect_anomaly()` kullan
6. Girdi verilerinde NaN olup olmadığını kontrol et: `assert not torch.isnan(x).any()`

## Kayıp salınıyor

1. Öğrenme hızını 3-10x azalt
2. Toplu iş boyutunu artır (gradyan gürültüsünü azaltır)
3. Gradyan kırpma ekle: `torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)`
4. SGD'den Adam'a geç (parametre başına uyarlanabilir LR)
5. Eğitimin ilk %5-10'u için öğrenme hızı ısınması ekle

## Aşırı uyum (eğitim doğruluğu yüksek, test doğruluğu düşük)

1. Dropout ekle (p=0.1 ile başla, 0.5'e kadar artır)
2. Optimize ediciye ağırlık azalması ekle: `Adam(params, weight_decay=1e-4)`
3. Model boyutunu azalt (daha az katman veya daha dar katmanlar)
4. Veri artırma ekle
5. Erken durdurma kullan: doğrulama kaybı 5+ epok boyunca arttığında dur
6. Eğitim ve test kümeleri arasında veri sızıntısı olup olmadığını kontrol et

## Yetersiz uyum (hem eğitim hem test doğruluğu düşük)

1. Model kapasitesini artır (daha fazla katman, daha geniş katmanlar)
2. Daha fazla epok eğit
3. Öğrenme hızını artır (dikkatlice)
4. Modelin öğrenebildiğini doğrulamak için düzenlileştirmeyi geçici olarak kaldır
5. Modelin görev için yeterince ifade gücüne sahip olup olmadığını kontrol et

## Ölü ReLU nöronları

1. Katman başına sıfır aktivasyon oranını kontrol et. >%50 bir sorundur
2. LeakyReLU(0.01) veya GELU'ya geç
3. Ağırlıklar için Kaiming başlatma kullan
4. Öğrenme hızını azalt (büyük güncellemeler nöronları ölü bölgeye itebilir)
5. Aktivasyon fonksiyonlarından önce toplu iş normalleştirmesi ekle

## Hızlı referans: öğrenme hızı başlangıç noktaları

| Optimize Edici | Görev | Başlangıç LR'si |
|-----------|------|------------|
| Adam | Sıfırdan eğitim | 1e-3 |
| Adam | Önceden eğitilmişin ince ayarı | 1e-5 |
| SGD + momentum | Sıfırdan eğitim | 1e-1 |
| SGD + momentum | Önceden eğitilmişin ince ayarı | 1e-3 |
| AdamW | Transformer eğitimi | 3e-4 |

## Hızlı referans: toplu iş boyutu etkileri

| Toplu iş boyutu | Gradyan gürültüsü | Bellek | Genelleme |
|-----------|---------------|--------|---------------|
| 8-16 | Yüksek (gürültülü) | Düşük | Genellikle daha iyi |
| 32-64 | Orta | Orta | İyi varsayılan |
| 128-256 | Düşük (pürüzsüz) | Yüksek | Isınma gerekebilir |
| 512+ | Çok düşük | Çok yüksek | LR ölçekleme gerekir |

## Hiçbir şey işe yaramadığında

1. Modeli 1 gizli katmana basitleştir. Öğreniyor mu?
2. Veriyi 100 örneğe basitleştir. Aşırı uyum yapıyor mu?
3. Kaybınızı MSE ile değiştirin. Yakınsıyor mu?
4. Optimize edicinizi SGD(lr=0.01) ile değiştirin. İlerleme kaydediyor mu?
5. Verilerinizi sentetik verilerle değiştirin (örn. y = x[0] > 0). Öğreniyor mu?
6. Bunların hiçbiri işe yaramazsa: hata bakmadığınız bir kodda (veri yükleme, ön işleme, tensör şekilleri)
