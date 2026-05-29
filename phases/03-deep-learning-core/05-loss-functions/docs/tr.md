> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/03-deep-learning-core/05-loss-functions/docs/en.md)

# Kayıp Fonksiyonları

> Ağınız bir tahmin yapıyor. Gerçek değer ise tam tersini söylüyor. Ne kadar yanlış? O sayı kayıptır. Yanlış kayıp fonksiyonunu seçerseniz modeliniz tamamen yanlış şey için optimize olur.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Ders 03.04 (Aktivasyon Fonksiyonları)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- MSE, ikili çapraz entropi, kategorik çapraz entropi ve karşıtlıklı kaybı (InfoNCE) sıfırdan gradyanlarıyla uygulayın
- MSE'in sınıflandırma için neden başarısız olduğunu "her şey için 0.5 tahmin et" başarısızlık modunu göstererek açıklayın
- Çapraz entropiye etiket yumuşatma uygulayın ve aşırı kendine güvenen tahminleri nasıl önlediğini açıklayın
- Regresyon, ikili sınıflandırma, çoklu sınıflandırma ve gömme öğrenme görevleri için doğru kayıp fonksiyonunu seçin

## Sorun

Sınıflandırma sorunu üzerinde MSE'yi asgari yapan bir model, her şey için güvenle 0.5 tahmin edecektir. Kaybı asgari yapıyor. Ama aynı zamanda işe yaramaz.

Kayıp fonksiyonu, modelinizin gerçekten optimize ettiği tek şeydir. Doğruluk değil. F1 puanı değil. Yöneticinize raporladığınız herhangi bir metrik değil. Optimize edici, kayıp fonksiyonunun gradyanını alır ve o sayıyı küçültmek için ağırlıkları ayarlar. Kayıp fonksiyonu sizin önem verdiğiniz şeyi yakalamıyorsa, model onu tatmin etmenin matematiksel olarak en ucuz yolunu bulur ve bu yol neredeyse hiç istediniz olmaz.

Somut bir örnek: İkili sınıflandırma göreviniz var. İki sınıf, %50/%50 bölünme. Kayıp olarak MSE kullanıyorsunuz. Model her girdi için 0.5 tahmin ediyor. Ortalama MSE 0.25, ki bu hiçbir şey öğrenmeden mümkün olan minimumdur. Modelin sıfır ayırt edici gücü vardır ama teknik olarak kayıp fonksiyonunuzu asgari yapmıştır. Çapraz entropiye geçin ve aynı model, tahminleri 0 veya 1'e itilmeye zorlanır, çünkü -log(0.5) = 0.693 berbat bir kayıptır, oysa -log(0.99) = 0.01 kendine güvenli doğru tahminleri ödüllendirir.

Daha da kötüsü, öz-denetimli öğrenmede etiketleriniz bile yoktur. Karşıtlıklı kayb, öğrenme sinyalini tamamen tanımlar: ne benzer sayılır, ne farklı sayılır ve model onları ne kadar zor ayırmalıdır.

## Kavram

### Ortalama Kare Hata (MSE)

Regresyon için varsayılan. Tahmin ile hedef arasındaki kare farkı hesaplayın, tüm örneklerin ortalamasını alın.

```
MSE = (1/n) × Σ((y_tahmin - y_gerçek)²)
```

Neden kare önemli: büyük hataları karesel olarak cezalandırır. 2 hata, 1 hatasının 4 katı maliyetlidir. 10 hata 100 katıdır. Bu, MSE'i aykırı değerlere duyarlı yapar — tek bir çılgınca yanlış tahmin kayıpta hakim olur.

### Çapraz Entropi Kaybı

Sınıflandırma için kayıp fonksiyonu. Bilgi teorisine dayanır — tahmin edilen olasılık dağılımı ile gerçek dağılım arasındaki ıraksamayı ölçer.

**İkili Çapraz Entropi (BCE):**

```
BCE = -(y × log(p) + (1 - y) × log(1 - p))
```

Burada y gerçek etikettir (0 veya 1) ve p tahmin edilen olasılıktır.

Neden -log(p) çalışır: gerçek etiket 1 ise ve p = 0.99 tahmin ederseniz, kayıp -log(0.99) = 0.01'dir. p = 0.01 tahmin ederseniz, kayıp -log(0.01) = 4.6'dır. Bu 460 kat fark, çapraz entropinin neden çalıştığının kanıtıdır. Kendine güvenli yanlış tahminleri acımasızca cezalandırırken, kendine güvenli doğru tahminleri neredeyse hiç cezalandırmaz.

**Kategorik Çapraz Entropi:**

Çoklu sınıflandırma için, one-hot kodlanmış hedeflerle.

```
CCE = -Σ(y_i × log(p_i))
```

Sadece gerçek sınıf katkısı sağlar (diğer tüm y_i sıfır olduğu için). 10 sınıf varsa ve doğru sınıf 0.1 olasılık alırsa (rastgele tahmin), kayıp -log(0.1) = 2.3'tür. Doğru sınıf 0.9 olasılık alırsa, kayıp -log(0.9) = 0.105'tir.

### Karşıtlıklı Kayıp (InfoNCE)

Gömme öğrenmek için kullanılır. Benzer çiftleri yakın, farklı çiftleri uzak tutar.

```
InfoNCE = -log(exp(sim(positive) / τ) / Σ exp(sim(negative) / τ))
```

τ (sıcaklık) parametresi ne kadar agresif ayıracağını kontrol eder.

## Kayıp Fonksiyonu Seçimi

| Görev | Kayıp Fonksiyonu | Neden |
|-------|------------------|-------|
| Regresyon | MSE veya MAE | Sayısal çıktı |
| İkili sınıflandırma | BCE | İki sınıf, olasılık çıktısı |
| Çoklu sınıflandırma | CCE | Birçok sınıf, olasılık çıktısı |
| Gömme öğrenme | InfoNCE | Benzerlik tabanlı |
| Üreteç modeller | Adversarial kayıp | Gerçek/sahte ayrımı |

## Alıştırmalar

1. Sıfırdan MSE ve BCE uygulayın
2. Aynı sınıflandırma görevinde MSE ve BCE'yi karşılaştırın
3. Karşıtlıklı kaybı basit bir gömme göreviyle test edin

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Kayıp fonksiyonu | "Hata ölçüsü" | Tahmin ile gerçek arasındaki farkı ölçen fonksiyon |
| MSE | "Ortalama kare hata" | Kare farkların ortalaması, regresyon için |
| Çapraz entropi | "Sınıflandırma hatası" | Olasılık dağılımları arasındaki fark |
| Karşıtlıklı kayıp | "Benzerlik farkı" | Benzer ve farklı çiftleri ayıran kayıp |
| Etiket yumuşatma | "Aşırı güven azaltma" | Aşırı kendine güvenen tahminleri önleme |
