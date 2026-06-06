---
name: skill-embedding-patterns
description: Embedding'ler, vektör arama ve benzerlik için üretim kalıpları
version: 1.0.0
phase: 11
lesson: 4
tags: [embeddings, vectors, similarity, search, chunking, quantization]
---

# Embedding Kalıpları

Her embedding iş akışı bu sözleşmeyi izler:

```
metin -> embedding(metin) -> vektör (ondalık dizi)
benzerlik(vektör_a, vektör_b) -> puan (ondalık)
```

Embedding modeli ve benzerlik metriği, önemli olan tek iki karardır. Geri kalan her şey tesisattır.

## Embedding'ler Ne Zaman Kullanılır

- Belgeler arasında anlamsal arama (anahtar kelime değil, anlam bulma)
- Benzer öğeleri kümeleme (destek biletleri, ürün yorumları, hata raporları)
- En yakın komşularla sınıflandırma (etiketli örneklere benzerliğe göre yeni öğeleri etiketleme)
- Öneri sistemleri (kullanıcının beğendiğine benzer öğeler bulma)
- Tekilleştirme (benzerlik eşiği kullanarak yakın kopya içerik bulma)

## Embedding'ler Ne Zaman KULLANILMAZ

- Tam anahtar kelime eşleştirme (tam metin araması kullanın)
- Yapılandırılmış sorgular (SQL, filtreler kullanın)
- Manuel etiketlemenin daha hızlı olduğu küçük veri kümeleri (<100 öğe)
- Açıklanabilirliğin doğruluktan daha önemli olduğu görevler (embedding'ler opaktır)

## Model Seçimi

Kısıtlamalarınıza göre seçin:

- **API gerekli, en iyi değer**: OpenAI text-embedding-3-small (1536d, 1M token için 0.02$)
- **Maksimum doğruluk gerekli**: Voyage-3 (1024d, 1M token için 0.06$, en yüksek MTEB)
- **Yerel/özel gerekli**: BGE-M3 (1024d, ücretsiz, çok dilli, GPU önerilir)
- **Hızlı yerel prototipleme gerekli**: all-MiniLM-L6-v2 (384d, ücretsiz, CPU'da çalışır)
- **Çok dilli gerekli**: Cohere embed-v3 (1024d) veya BGE-M3 (ikisi de güçlü çok dilli)

Kural: indeksleme ve sorgulama arasında asla embedding modellerini karıştırmayın. Farklı modellerden gelen vektörler uyumsuz uzaylarda yaşar.

## Parçalama (Chunking) Kuralları

1. 50 token örtüşmeyle parça başına 256-512 token hedefleyin
2. Mümkünse cümlenin ortasında asla bölmeyin
3. Her parçayla birlikte meta verileri (kaynak dosya, bölüm başlığı, konum) ekleyin
4. Yapılandırılmış belgeler (Markdown, HTML) için önce başlık sınırlarında bölün
5. Bilinen cevapları arayarak ve getirmeyi kontrol ederek parça kalitesini test edin

## Benzerlik Metriği Seçimi

- **Kosinüs benzerliği**: varsayılan seçim, değişken uzunluklu metni işler, normalleştirilmiş
- **Nokta çarpımı**: vektörler zaten birim-normalleştirilmiş olduğunda (OpenAI modelleri öyledir), biraz daha hızlı
- **Öklid mesafesi**: kümeleme için, mutlak konum önemli olduğunda

Vektörler normalleştirildiğinde üçü de aynı sıralamayı verir. Seçim yalnızca normalleştirilmemiş vektörler için önemlidir.

## Depolama Optimizasyonu

Üç sıkıştırma seviyesi, istiflenebilir:

1. **Matryoshka kırpma**: boyutları azaltın (1536 -> 256 = 6x tasarruf, %3-5 doğruluk kaybı)
2. **Float16 nicemleme**: boyut başına depolamayı yarıya indirin (2x tasarruf, <%1 doğruluk kaybı)
3. **İkili nicemleme**: boyut başına 1 bit (32x tasarruf, %5-10 doğruluk kaybı, yeniden puanlama ile kullanın)

Üretim kalıbı: tam derlem üzerinde ikili arama, ilk 1000'i float32 vektörlerle yeniden puanlama.

## Getir-Sonra-Yeniden-Sırala

En iyi doğruluk için iki aşamalı pipeline:

1. Bi-encoder ilk 100 adayı getirir (hızlı, önceden hesaplanmış embedding'leri kullanır)
2. Cross-encoder ilk 10'a yeniden sıralar (yavaş, her sorgu-belge çiftini işler)

Bu, hassasiyet metriklerinde tek aşamalı getirmeden %10-15 daha iyi performans gösterir. Doğruluk gecikmeden daha önemli olduğunda kullanın.

## Yaygın Hatalar

- İndeksleme ve sorgulama için farklı embedding modelleri kullanmak
- Parçalar yerine tüm belgeleri embedding yapmak (embedding her şeyin ortalaması haline gelir)
- Kosinüs benzerliğinden önce vektörleri normalleştirmemek (çoğu model önceden normalleştirir, ancak doğrulayın)
- Parça örtüşmesini göz ardı etmek (sınırlarda bölünen cümleler bağlamı kaybeder)
- Yalnızca orijinal metin olmadan vektörleri depolamak (getirme için ikisine de ihtiyacınız var)
- Model değiştiğinde yeniden embedding yapmamak (eski vektörler uyumsuzdur)
- Boyutları yalnızca doğruluğa dayalı seçmek (depolama ve gecikme boyutlarla doğrusal olarak ölçeklenir)

## Embedding'lerde Hata Ayıklama

Arama sonuçları kötüyse:

1. Sorgu embedding'inin sıfır olmadığını doğrulayın (boş veya boşluk girdisi sıfır vektörler üretir)
2. Bilinen-ilgili bir belgenin benzerlik puanını manuel olarak kontrol edin
3. Belge kelime hazinesiyle eşleşecek şekilde sorguyu yeniden ifade etmeyi deneyin
4. İlgili içeriğin parçalar arasında bölünmediğinden emin olmak için parça sınırlarını inceleyin
5. Normalleştirme sorunlarını tespit etmek için metrikler (kosinüs, nokta, öklid) arasında ilk-k sonuçlarını karşılaştırın
6. Pipeline'ın çalıştığını doğrulamak için önemsiz bir eşleşen sorguyla (belgeden bir cümle kopyalayın) test edin

## Üretim Parametreleri

- Parça boyutu: 256-512 token
- Parça örtüşmesi: 50 token (parça boyutunun %10-20'si)
- İlk-k getirme: doğrudan kullanım için 5-10, yeniden sıralama için 50-100
- Benzerlik eşiği: kosinüs için 0.7+ (bunun altında, sonuçlar genellikle alakasızdır)
- Toplu embedding: verim için API çağrısı başına 100-500 metin işleyin
- İndeks yeniden oluşturma: model değiştiğinde veya belgeler önemli ölçüde güncellendiğinde yeniden embedding yapın
