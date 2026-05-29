> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/13-debugging-neural-networks/docs/en.md)

# Sinir Ağlarında Hata Ayıklama

> Ağın derlendi. Çalıştı. Bir sayı üretti. Sayı yanlış ve hiçbir şey çökmedi. En zor hata ayıklama türüne hoş geldin — hata mesajı olmayan tür.

**Tür:** Practice
**Diller:** Python, PyTorch
**Ön Koşullar:** Faz 03 Ders 01-10 (özellikle geri yayılım, kayıp fonksiyonları, optimize ediciler)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Yaygın sinir ağı başarısızlıklarını (NaN kaybı, düz kayıp eğrisi, aşırı uyum, salınım) sistematik stratejilerle teşhis edin
- "Tek toplu işe aşırı uyum" tekniğini kullanarak model mimarisinin ve eğitim döngüsünün doğru olduğunu doğrulayın
- Gradyan büyüklüklerini, aktivasyon dağılımlarını ve ağırlık normlarını inceleyerek kaybolan/patlayan gradyan sorunlarını belirleyin
- Veri hattı, model mimarisi, kayıp fonksiyonu, optimize edici ve öğrenme hızı sorunlarını kapsayan bir hata ayıklama kontrol listesi oluşturun

## Sorun

Geleneksel yazılım kırıldığında çöker. Boş bir işaretçi istisna fırlatır. Tip uyuşmazlığı derlemede başarısız olur.

Sinir ağları bu lüksü vermez.

Kırık bir sinir ağı tamamlanana kadar çalışır, bir kayıp değeri yazdırır ve tahminler üretir. Kayıp azalabilir. Tahminler makul görünebilir. Ama model sessizce yanlıştır. Google araştırmacıları, ML hata ayıklama süresinin %60-70'inin hata üretmeyen ama model kalitesini düşüren "sessiz" hatalara harcandığını tahmin ediyor.

## Kavram

### Hata Ayıklama Zihniyeti

Altın kural: **basit başla, karmaşıklığı tek tek ekle, her parçayı bağımsız doğrula.**

### Belirti 1: Kayıp Azalmıyor

**Yanlış öğrenme hızı.** Çok yüksek: kayıp salınır veya NaN olur. Çok düşük: kayıp neredeyse hiç hareket etmez. Adam için 1e-3'ten başlayın. SGD için 1e-1 veya 1e-2'den başlayın.

**Ölü ReLU'lar.** Bir ReLU nöronu büyük negatif girdi alırsa 0 çıktısı verir ve gradyanı 0 olur. Bir daha asla aktive olmaz. Kontrol: her ReLU katmanından sonra tam olarak 0 olan aktivasyonların oranını yazdırın. >%50 ise LeakyReLU'ya geçin.

**Kaybolan gradyanlar.** Derin ağlarda sigmoid/tanh ile gradyanlar üssel küçülür. Düzeltme: ReLU/GELU kullanın, artık bağlantılar ekleyin.

**Patlayan gradyanlar.** Gradyanlar üssel büyür. RNN'lerde yaygın. Düzeltme: gradyan kırpma (gradient clipping).

### Belirti 2: Kayıp Azalıyor Ama Model Kötü

**Aşırı uyum.** Eğitim-validasyon kayıp farkı büyür. Düzeltme: dropout, ağırlık azaltma, erken durdurma.

**Veri sızıntısı.** Test verisi eğitime sızdı. Önce ayır, sonra ön işle.

**Etiket hataları.** Çoğu veri setinde etiketlerin %5-10'u yanlıştır.

### Belirti 3: Kayıpta NaN veya Inf

Öğrenme hızı çok yüksek. log(0) veya log(negatif). Sıfıra bölme. Sayısal taşma.

### Teknik 1: Gradyan Kontrolü

Analitik gradyanları sayısal gradyanlarla karşılaştırın. `rel_diff < 1e-5` ise doğru, `> 1e-3` ise hata.

### Teknik 2: Aktivasyon İstatistikleri

Her katman aktivasyonlarının ortalama ve standart sapmasını izleyin. Sağlıklı: ortalama ~0, std ~1.

### Teknik 3: Gradyan Akışı Görselleştirme

Her katmanın ortalama gradyan büyüklüğünü çizin. Erken katmanlar 1000x daha küçükse kaybolan gradyan var.

### Teknik 4: Tek Toplu İşe Aşırı Uyum Testi

Tek bir küçük toplu iş (8-32 örnek) alın. 100+ iterasyon eğitin. Kayıp sıfıra yakın gitmeli. Gitmezse temel bir hata var.

### Teknik 5: Öğrenme Hızı Bulucu

Öğrenme hızını 1e-7'den 10'a kadar tarayın. Optimal lr, kaybın en hızlı düştüğü noktanın 10 kat küçüğüdür.

### Yaygın PyTorch Hataları

| Hata | Belirti | Düzeltme |
|------|---------|----------|
| `optimizer.zero_grad()` unutuldu | Gradyanlar birikir, kayıp salınır | backward öncesi zero_grad ekle |
| `model.eval()` unutuldu | Test doğruluğu değişken | eval() ve torch.no_grad() ekle |
| Yanlış tensor şekilleri | Sessiz yayılma yanlış sonuç | Şekilleri yazdır |
| CPU/GPU uyuşmazlığı | CUDA tensor hatası | .to(device) kullan |
| Veri normalize edilmedi | Kayıp rastgele seviyede | Girdileri normalize et |

## Uygulama

Aşağıdaki kodları `code/main.py` içinde inşa edin:

**NetworkDebugger sınıfı:** Her katmana kancalar (hooks) takarak aktivasyon ve gradyan istatistikleri kaydeder. Kayıp sağlığı, aktivasyon sağlığı ve gradyan sağlığı kontrolleri yapar.

**Tek toplu işe aşırı uyum testi:** 200 adımda kaybın 0.1'in altına düşüp düşmediğini kontrol eder.

**Öğrenme hızı bulucu:** 1e-7'den 10'a üssel tarama yapar, optimal lr'yi önerir.

**Gradyan kontrolcüsü:** Sonlu farklarla analitik gradyanları karşılaştırır.

**Kasıtlı bozuk ağlar:** Çok yüksek lr, ölü ReLU'lar, eksik zero_grad — her birini teşhis edin.

## Kullanım

PyTorch'un yerleşik araçları:
```python
with torch.autograd.detect_anomaly():
    loss.backward()
```

Hata ayıklama kontrol listesi (tam eğitimden önce):
1. Tek toplu iş testini çalıştır. Başarısızsa dur.
2. Model özetini yazdır.
3. Rastgele veriyle tek ileri geçiş yap.
4. 5 epoch eğit, kaybın azaldığını doğrula.
5. Aktivasyon istatistiklerini kontrol et.
6. Gradyan akışını kontrol et.
7. Veri hattını doğrula (5 rastgele örnek yazdır).

## Temel Terimler

| Terim | Gerçekte ne anlama geldiği |
|-------|--------------------------|
| Sessiz hata | Hata üretmeyen ama model kalitesini düşüren hata |
| Ölü ReLU | Girdisi hep negatif olan, 0 çıktısı veren ve gradyan almayan nöron |
| Kaybolan gradyan | Gradyanların katmanlar boyunca üssel küçülmesi |
| Patlayan gradyan | Gradyanların üssel büyümesi, kaybın NaN olması |
| Gradyan kontrolü | Geri yayılım gradyanlarını sayısal gradyanlarla doğrulama |
| Tek toplu iş testi | Modelin öğrenebildiğini doğrulamak için tek toplu işte eğitim |
| LR bulucu | Optimal öğrenme hızını bulmak için tarama |
| Veri sızıntısı | Test verisinin eğitime karışması |
| Gradyan kırpma | Gradyan normu eşiği aştığında ölçekleme |

## Alıştırmalar

1. Patlayan gradyan dedektörü ekleyin
2. Ölü nöron canlandırıcı inşa edin
3. LR bulucuyu matplotlib ile çizdirin
4. Veri hattı doğrulayıcı oluşturun
5. Mini framework'te gizli bir hata bulun ve gradyan kontrolüyle teşhis edin
