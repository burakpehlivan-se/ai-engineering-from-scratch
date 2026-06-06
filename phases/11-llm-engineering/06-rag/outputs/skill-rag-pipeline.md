---
name: skill-rag-pipeline
description: RAG işlem hatlarını ilkelerden (first principles) inşa edin ve hata ayıklayın
version: 1.0.0
phase: 11
lesson: 6
tags: [rag, retrieval, embeddings, vector-search, llm-engineering]
---

# RAG İşlem Hattı Kalıbı

Her RAG sistemi şu kalıbı izler:

```
dokümanlar -> parçala -> göm -> sakla
sorgu -> göm -> ara(top_k) -> prompt oluştur -> üret
```

İndeksleme doküman başına bir kez olur. Sorgulama her kullanıcı isteğinde olur.

## RAG Ne Zaman Kullanılır

- LLM'nin özel veya güncel dokümanlara erişmesi gerekiyor
- İnce ayar (fine-tuning) güncellemek için çok pahalı veya çok yavaş
- Cevaplar için kaynak belirtmeniz gerekiyor
- Bilgi tabanı sık sık değişiyor

## RAG Ne Zaman Kullanılmaz

- Cevap, LLM'nin zaten sahip olduğu genel bilgidir
- Görev yaratıcıdır (yazma, beyin fırtınası), olgusal değil
- Modelin belirli bir akıl yürütme stilini benimsemesini istiyorsunuz (ince ayar kullanın)

## Uygulama kontrol listesi

1. Dokümanları 256-512 token'lik segmentlere, 50 token çakışma ile parçalayın
2. Her parçayı tutarlı bir gömme modeli kullanarak gömün
3. Gömme vektörlerini orijinal metinle birlikte bir vektör veritabanında saklayın
4. Sorgu zamanında, kullanıcı sorusunu aynı modelle gömün
5. Kosinüs benzerliği ile en benzer top-k (5-10) parçayı geri getirin
6. Bir prompt oluşturun: sistem talimatı + geri getirilen bağlam + kullanıcı sorusu
7. Cevabı, geri getirilen bağlama dayandırarak üretin
8. Cevabı kaynak referanslarıyla birlikte döndürün

## Yaygın hatalar

- İndeksleme ve sorgulama için farklı gömme modelleri kullanmak (vektörler uyumsuzdur)
- Parçaların çok küçük (bağlam kaybı) veya çok büyük (alaka düşüklüğü) olması
- Parçalar arasında çakışma olmaması (cümleleri sınırlarda böler)
- Dokümanlar değiştiğinde yeniden indekslemeyi unutmak
- Geri getirilen parçaları tutarlı bir cevap üretmeden kullanıcıya döndürmek
- Olgusal RAG sorguları için temperature=0 ayarlamamak (yüksek sıcaklık = daha fazla halüsinasyon)

## Geri getirmeyi hata ayıklama

Doğru parçalar geri getirilmiyorsa:

1. Sorgu gömme vektörünü yazdırın ve sıfır olmadığını doğrulayın
2. Bilinen ilgili bir parça için kosinüs benzerliklerini manuel olarak kontrol edin
3. Doküman kelime hazinesine uyması için sorguyu yeniden ifade etmeyi deneyin
4. Gömme modelinin indeks ve sorgu zamanında eşleştiğini doğrulayın
5. İlgili içeriğin parçalama sırasında kaybolup kaybolmadığını kontrol edin

## Üretim parametreleri

- Parça boyutu: 256-512 token
- Çakışma: 50 token (parça boyutunun %10-20'si)
- Top-k: Çoğu kullanım senaryosu için 5-10
- Sıcaklık (temperature): Olgusal cevaplar için 0
- Gömme modeli: text-embedding-3-small (maliyet etkin) veya text-embedding-3-large (daha yüksek doğruluk)
