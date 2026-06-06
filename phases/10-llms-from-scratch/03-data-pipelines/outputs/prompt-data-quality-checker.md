---
name: prompt-data-quality-checker
description: LLM ön-eğitim (pre-training) pipeline'larında veri kalitesini doğrulayın ve hata ayıklayın
version: 1.0.0
phase: 10
lesson: 3
tags: [data-pipeline, deduplication, quality-filter, pre-training, llm, data-cleaning]
---

# LLM Ön-Eğitimi için Veri Kalitesi Denetçisi

LLM ön-eğitimi için bir veri pipeline'ı oluştururken veya denetlerken, sorunlar modele ulaşmadan önce yakalamak için bu çerçeveyi kullanın.

## Pipeline Çıktısındaki Kırmızı Bayraklar

**Tekilleştirme (deduplication) web verisinin %20'sinden azını kaldırdı.** Common Crawl tipik olarak %30-40 kopya içerir. Tekilleştirme adımınız %20'den az kaldırıyorsa, MinHash parametreleriniz çok muhafazakâr veya eşik değeriniz çok yüksek. Kontrol edin: shingle boyutu k, hash fonksiyonu sayısı, LSH banda sayısı, Jaccard eşiği.

**Sıkıştırma oranı 2.0 karakter/token'ın altında.** Bu, tokenizer'ınızın çok agresif böldüğü anlamına gelir. Ya daha fazla birleştirmeyle yeniden eğitin, kelime hazinesi boyutunu artırın ya da ön-tokenizasyonun metni gereksiz yere parçalamadığını kontrol edin.

**Sıkıştırma oranı 6.0 karakter/token'ın üzerinde.** Tokenizer'ınız genelleşmeyebilecek çok alana özgü birleştirmeler öğrenmiş. Bu, alana özgü bir model için sorun değil, ancak genel amaçlı modeller için uyarı işaretidir.

**Dizi kullanımı %90'ın altında.** Çok fazla dolgu (padding). Ya belgeleriniz çok kısa (onları filtreleyin veya minimum belge uzunluğunu artırın) ya da dizi paketlemeniz (sequence packing) verimsiz (naif dolgudan çoklu belge paketlemeye geçin).

**Kelime hazinesi kullanımı %50'nin altında.** Kelime hazinenizin yarısından fazlası bu derlemde kullanılmıyor. Ya kelime hazinesi alanınız için çok büyük ya da tokenizer çok farklı veriler üzerinde eğitilmiş.

## Kalite Filtresi Kalibrasyonu

Her pipeline aşamasında 1.000 belgelik rastgele bir örneklem üzerinde şu kontrolleri çalıştırın:

1. **Temizlemeden sonra 20 rastgele belgeyi okuyun.** Artık HTML, JavaScript, gezinme metni veya şablon metin içeriyor mu? Evet ise, HTML çıkarma işleminiz eksiktir.

2. **Kalite filtresini GEÇEN 20 rastgele belgeyi okuyun.** Herhangi biri spam, anahtar kelime listesi veya makine tarafından üretilmiş mi? Evet ise, filtre eşiklerini sıkılaştırın.

3. **Kalite filtresinde BAŞARISIZ olan 20 rastgele belgeyi okuyun.** Herhangi biri gerçekten iyi içerik mi? Evet ise, filtreniz çok agresiftir. Eşikleri gevşetin veya belirli kalıplar için istisnalar ekleyin.

4. **Tekilleştirmeden 20 rastgele yakın kopya çiftini okuyun.** Gerçekten benzerler mi? Değilse, Jaccard eşiğini düşürün veya hash fonksiyonu sayısını artırın.

## Veri Karıştırma Oranları

Evrensel bir formül yoktur. Bu temel değerlerle başlayın ve değerlendirmeye göre ayarlayın:

| Kategori | Llama 3 Oranı | Başlangıç Noktası |
|----------|--------------|-------------------|
| Web metni | %50 | %50 |
| Kod | %25 | %15-25 |
| Kitaplar/akademik | %13 | %10-15 |
| Matematik | %8 | %5-10 |
| Çok dilli web | %4 | %5-10 |

Model programlama konusunda güçlü olmalıysa kod oranını artırın. Akıl yürütme önemliyse matematik oranını artırın. Daha az gürültü istiyorsanız web oranını azaltın. Oranları değiştirdikten sonra her zaman kıyaslamalar (benchmarks) üzerinde değerlendirin.

## Ölçeklendirme Tahminleri

Belirli bir hedef token sayısı için:

- Web'den 1T token: yaklaşık 3-5TB ham metin, temizleme ve tekilleştirmeden sonra ~1.5-2TB
- Tokenizasyon hızı (Rust): çekirdek başına ~100M token/saniye
- Tokenizasyon hızı (Python): çekirdek başına ~1-10M token/saniye
- 128 hash, 16 bantla MinHash tekilleştirme: çekirdek başına ~10K belge/saniye
- Dizi paketleme: G/Ç (I/O) bağımlı, 10GB'ın üzerindeki derlemler için belleğe eşlenmiş dosyalar (memory-mapped files) kullanın

15T token için (Llama 3 ölçeği), ~30-50TB ham girdi verisi, 64 çekirdekli bir makinede 1-2 haftalık ön işleme ve ara dosyalar için 100TB+ disk planlayın.

## Eğitim Öncesi Kontrol Listesi

1. Toplam token sayısı, hesaplama bütçenizle eşleşiyor (kılavuz olarak Chinchilla ölçeklendirmesini veya Llama 3 aşırı eğitim oranını kullanın)
2. Tekilleştirme, web verisinin %30-40'ını kaldırdı
3. Kalite filtresi, kalan verinin %10-20'sini kaldırdı
4. Sıkıştırma oranı İngilizce için 3-5 karakter/token
5. Dizi kullanımı %95'in üzerinde
6. Rastgele örnek kontroller, her pipeline aşamasında temiz, tutarlı metin gösteriyor
7. Veri karışım oranları küçük ölçekli bir eğitim çalışmasında doğrulandı
8. KVK (PII - Kişisel Tanımlanabilir Bilgi) kaldırma, bir örneklem üzerinde doğrulandı
9. Tüm ikili formatlar (paketlenmiş diziler, token kimlik dizileri) gidiş-dönüş kodlama/kod çözme testlerini geçiyor
10. Pipeline tekrarlanabilir: aynı girdi, sabit rastgele tohumlarla özdeş çıktı üretiyor
