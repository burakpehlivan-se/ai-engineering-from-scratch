---
name: skill-advanced-rag
description: Hibrit arama, yeniden sıralama ve değerlendirme ile üretim kalitesinde RAG oluşturun
version: 1.0.0
phase: 11
lesson: 7
tags: [rag, hybrid-search, bm25, reranking, hyde, evaluation]
---

# Gelişmiş RAG Kalıbı

Temel RAG: sorguyu embedding yap -> vektör araması -> ilk-k -> üret.
Gelişmiş RAG: sorguyu embedding yap + BM25 -> sıraları birleştir -> yeniden sırala -> ilk-k -> üret.

```
sorgu -> [vektör arama (ilk-50)] -+-> RRF füzyon -> yeniden sıralayıcı (ilk-5) -> prompt -> LLM
 |
sorgu -> [BM25 arama (ilk-50)] --+
```

## Temel RAG'den Ne Zaman Yükseltilir

- Getirme kalitesi %70 Recall@5'in altına düşer
- Kullanıcılar yanlış veya alakasız cevaplar bildirir
- Derlem 100K parçanın ötesine büyür
- Sorgular, belgelerden farklı bir kelime hazinesi kullanır
- Çok adımlı (multi-hop) sorular tutarlı bir şekilde başarısız olur

## Uygulama kontrol listesi

1. Vektör indeksinin yanında BM25 indeksi ekleyin
2. Her iki aramayı paralel çalıştırın (her biri ilk-50)
3. Ters Sıralama Füzyonu (RRF) ile birleştirin (k=60)
4. İlk adayları bir cross-encoder ile yeniden sıralayın
5. Son prompt için ilk-5'i alın
6. Bir test seti üzerinde sadakat değerlendirmesi ekleyin

## Teknik seçim kılavuzu

- **Hibrit arama**: üretimde her zaman kullanın. Sorgu zamanında ekstra maliyeti yoktur.
- **Yeniden sıralama**: Recall@50 iyiyken Recall@5 kötüyse kullanın. 50-200ms gecikme ekler.
- **HyDE**: sorgular belirsiz olduğunda veya belgelerden farklı kelime hazinesi kullandığında kullanın. Bir LLM çağrısı ekler.
- **Ebeveyn-çocuk parçaları**: küçük parçalar bağlamdan yoksun olduğunda ancak büyük parçalar ilgililiği seyreltitiğinde kullanın.
- **Meta veri filtreleme**: derlemin net kategorileri (tarih, kaynak türü, departman) olduğunda kullanın.
- **Sorgu ayrıştırma**: birden fazla belgeden bilgi gerektiren çok adımlı sorular için kullanın.

## Yaygın hatalar

- BM25 ve vektör aramasını farklı parça kümeleriyle çalıştırmak (aynı derlemi aramalıdırlar)
- Yeniden sıralama için çok küçük bir aday havuzu kullanmak (ilk-10 çok az; ilk-50 kullanın)
- Her sorgu için HyDE eklemek (yalnızca kelime hazinesi uyumsuzluğu darboğaz olduğunda yardımcı olur)
- Değişiklikleri değerlendirmemek (her tekniği eklemeden önce ve sonra Recall@k ölçmek)
- Nerede başarısız olduğunu ölçmeden pipeline'ı aşırı mühendislik etmek

## Değerlendirme iş akışı

1. Bilinen cevap parçalarıyla 50+ test sorusu oluşturun
2. Her getirme yöntemi için Recall@5 ve Recall@10 ölçün
3. Getirmenin başarılı olduğu sorgular için, üretilen cevapların sadakatini ölçün
4. Derlem büyüdükçe metrikleri haftalık olarak izleyin
5. Daha fazla teknik eklemeden önce bireysel başarısızlıkları araştırın
