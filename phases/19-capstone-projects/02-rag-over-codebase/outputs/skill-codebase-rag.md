---
name: codebase-rag
description: AST-farkında parçacıklandırma, hibrit erişim, artımlı yeniden indeksleme ve alıntılanmış yanıtlarla çapraz-depo semantik arama sistemi inşa et
version: 1.0.0
phase: 19
lesson: 02
tags: [capstone, rag, code-search, tree-sitter, qdrant, bm25, hybrid-retrieval]
---

Toplamda en az 2M satır kod olan 10+ depo verildiğinde, bir alım hattı, bir hibrit indeks ve doğrulanabilir dosya:satır çapalarıyla çapraz-depo soruları yanıtlayan bir alıntı-zorunlu sorgu ajanı inşa et.

İnşa planı:

1. Her dosyayı tree-sitter ile ayrıştır. Fonksiyon ve sınıf düğüm sınırlarında parçacıklandır. `{repo, yol, başlangıç_satırı, bitiş_satırı, sembol, gövde}` depola.
2. Her parçayı, istem-önbellekli sistem istemleriyle Claude Haiku 4.5 veya Gemini 2.5 Flash kullanarak özetle. Tek cümlelik özeti parçanın yanında depola.
3. Üç yapıya indeksle: Qdrant (yoğun, Voyage-code-3 veya nomic-embed-code), Tantivy (alan ağırlıklı BM25) ve kuzu (içe aktarmalar, çağrılar, kalıtım için sembol grafik kenarları).
4. Üç düğümlü bir LangGraph sorgu ajanı inşa et: retrieve (BM25'e paralel yoğun), rerank (Cohere rerank-3 veya bge-reranker-v2-gemma-2b), synth (istem önbelleği ve dosya:satır alıntı gereksinimiyle Claude Sonnet 4.7).
5. Son-izleme: doğrulanabilir bir `(repo/yol:başlangıç-bitiş)` çapası olmadan herhangi bir iddiayı reddet; yeniden sor veya bırak.
6. Sembol düzeyinde bir fark hesaplayan ve yalnızca değişen parçaları yeniden gömen bir git push webhook'u bağla. Hedef: 2M satırlık bir filoda 50-dosyalık commit 60 saniyenin altında aranabilir.
7. 100 soruluk elenmiş bir küme ile değerlendir. MRR@10, nDCG@10, alıntı sadakati ve gecikme yüzdeliklerini raporla.
8. Değerlendirmeyi haftalık olarak yeniden çalıştıran ve MRR@10 düşüşü >%5 olduğunda uyaran haftalık bir sapma işi çalıştır.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Erişim kalitesi | 100 soruluk elenmiş küme üzerinde MRR@10 ve nDCG@10 |
| 20 | Alıntı sadakati | Doğrulanabilir dosya:satır çapalarına sahip yanıt iddialarının kesri |
| 20 | Gecikme ve ölçek | İndekslenen derlem boyutunda 10k QPS'de p95 sorgu gecikmesi |
| 20 | Artımlı indeksleme doğruluğu | 50-dosyalık commit'te git push'tan aranabilirliğe kadar geçen süre |
| 15 | UX ve yanıt biçimlendirme | Alıntı tıklanabilirliği, parçacık önizlemeleri, takip kolaylığı |

Kesin redler:

- AST-farkında parçacıklandırma yerine sabit boyutlu token parçacıklandırma. Üretilmiş-kod-ağırlıklı derlemleri zehirler.
- BM25 veya rerank olmadan yalnızca kosinüs erişimi. Tam-sembol-adı sorgularında başarısız olduğu biliniyor.
- Zorunlu dosya:satır alıntıları olmadan yanıtlar.
- Her git push'ta tam derlem yeniden gömme; artımlı olmalıdır.

Ret kuralları:

- Lisanslarını okumadan depoları indekslemeyi reddet. Bazıları üçüncü taraf vektör depolarına gömülmeyi yasaklar.
- İndeksin hiç görmediği dosyaları alıntıladığını iddia eden sorguları yanıtlamayı reddet; döndürmeden önce her zaman çapayı doğrula.
- p95'i 4 saniyenin üzerinde bir yanıt sunmayı reddet; bunun yerine bir takip tutamağıyla kısmi sonuç döndür.

Çıktı: Alım hattını, LangGraph sorgu ajanını, 100 soruluk etiketli değerlendirme kümesini, bir Langfuse pano bağlantısını ve düzelttiğiniz üç erişim başarısızlık kipini (üretilmiş-kod zehirlenmesi, uzun-kuyruk sembol geri çağırma, çapraz-depo sembol çözümü) ve her birini düzelten tam değişikliği adlandıran bir yazıyı içeren bir depo.
