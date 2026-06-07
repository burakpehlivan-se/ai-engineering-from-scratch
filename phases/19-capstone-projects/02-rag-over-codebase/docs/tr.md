# Capstone 02 — Codebase Üzerinde RAG (Retrieval-Augmented Generation — Geri Getirmeyle Desteklenmiş Üretim) (Repo-Ötesi Anlamsal Arama)

> 2026'da her ciddi mühendislik organizasyonu anlamı (sadece dizileri değil) anlayan dahili bir kod araması çalıştırıyor. Sourcegraph Amp, Cursor'ın codebase yanıtları, Augment'ın kurumsal grafı, Aider'ın repomap'ı, Pinterest'in dahili MCP'si — hep aynı şekil. Birçok repoyu (repo) hazmedin, tree-sitter ile ayrıştırın, fonksiyon ve sınıf düzeyinde parçalara (chunk) gömün, hibrit arayın, yeniden sıralayın, alıntılarla (citation) yanıtlayın. Bu capstone sizden 10 repoda 2 milyon satır kodu yöneten ve her git push'ta artımlı yeniden indekslemeye dayanan bir tane inşa etmenizi istiyor.

**Type:** Capstone
**Languages:** Python (ingestion), TypeScript (API + UI)
**Prerequisites:** Phase 5 (NLP foundations), Phase 7 (transformers), Phase 11 (LLM engineering), Phase 13 (tools), Phase 17 (infrastructure)
**Phases exercised:** P5 · P7 · P11 · P13 · P17
**Time:** 30 saat

## Problem

2026'da her frontier kodlama ajanı, bağlam pencerelerinin repo-ötesi soruları tek başına çözmediği için bir codebase geri getirme katmanı ile geliyor. Claude'ın 1M-token bağlamı yardımcı olur; sıralanmış geri getirme ihtiyacını ortadan kaldırmaz. Ham parçalar üzerinde naif kosinüs araması, üretilmiş kod, monorepo kopyalanması ve nadiren-içe-aktarılan simgelerin uzun kuyruğu üzerinde sonuçları zehirlendiriyor. Üretim yanıtı, AST-farkında parçalar üzerinde hibrit (yoğun + BM25) arama, yeniden sıralayıcı ve bir simge referansları grafından oluşuyor.

Bunu, gerçek bir filo üzerinde indeksleyerek — tek bir eğitsel repo değil — ve MRR@10, alıntı sadakati (citation faithfulness) ve artımlı tazelik ölçerek öğrenirsiniz. Hata modları altyapısaldır: 100k-dosyalık bir monorepo, dosyaların yarısını elden geçiren bir push, doğru yanıtlamak için dört repoyu geçmesi gereken bir sorgu.

## Concept

AST-farkında bir hazmetme (ingestion) hattı, her dosyayı tree-sitter ile ayrıştırır, fonksiyon ve sınıf düğümlerini çıkarır ve sabit token pencereleri yerine düğüm sınırlarında parçalar. Her parça üç temsil alır: yoğun bir gömme (embedding) (Voyage-code-3 veya nomic-embed-code), seyrek BM25 terimleri ve kısa bir doğal-dil özeti. Özet, üçüncü bir geri getirilebilir modalite ekler — kullanıcılar "X nasıl yetkilendirilir?" diye sorar ve özet "authz"den bahseder, kodda yalnızca `check_permission` olsa bile.

Geri getirme hibrittir. Bir sorgu hem yoğun hem BM25 aramalarını tetikler, top-k'yı birleştirir ve birleşimi çapraz kodlayıcı (cross-encoder) yeniden sıralayıcısına (Cohere rerank-3 veya bge-reranker-v2-gemma-2b) verir. Yeniden sıralanmış liste, her iddiayı dosya ve satır aralığıyla alıntılaması talimatıyla uzun-bağlam sentezleyiciye (Claude Sonnet 4.7 prompt önbelleği ile veya self-hosted Llama 3.3 70B) gider. Alıntıları olmayan yanıtlar bir son-çıktı süzgeci (post-filter) tarafından reddedilir.

Artımlı tazelik altyapı sorunudur. Git push bir fark (diff) tetikler: hangi dosyalar değişti, hangi simgeler değişti. Yalnızca etkilenen parçalar yeniden gömülür. Etkilenen repo-ötesi simge kenarları (içe aktarmalar, metot çağrıları) yeniden hesaplanır. İndeks, her commit'te 2M satırı yeniden işlemeden tutarlı kalır.

## Architecture

```
git push --> webhook --> ingest worker (LlamaIndex Workflow)
 |
 v
 tree-sitter parse + AST chunk
 |
 +--------------+----------------+
 v v v
 dense BM25 index summary (LLM)
 (Voyage / bge) (Tantivy) (Haiku 4.5)
 | | |
 +------> Qdrant / pgvector <----+
 |
 v
 symbol graph (Neo4j / kuzu)
 |
 query --> LangGraph agent (retrieve -> rerank -> synth)
 |
 v
 Claude Sonnet 4.7 1M context
 |
 v
 answer + file:line citations
```

#### Açıklama

Bu mimari bir git push'tan alıntılı bir yanıta kadar tam veri akışını gösterir. Webhook bir hazmetme işçisini tetikler; tree-sitter dosyaları ayrıştırır ve AST düğüm sınırlarında parçalara ayırır. Her parça üç temsil kanallarına yazılır: yoğun gömmeler (Voyage veya bge), Tantivy üzerinde BM25 endeksi ve Haiku 4.5 tarafından üretilen özetler. Üçü de Qdrant veya pgvector'da toplanır ve Neo4j/kuzu'daki simge grafı tarafından zenginleştirilir. Sorgu zamanında bir LangGraph ajanı paralel olarak yoğun ve BM25 aramasını yapar, sonuçları birleştirir, yeniden sıralar ve Claude Sonnet 4.7'ye dosya:satır alıntıları gerektiren bir sentez için gönderir.

## Stack

- Ayrıştırma: 17 dil dilbilgisi (Python, TS, Rust, Go, Java, C++, vb.) ile tree-sitter
- Yoğun gömmeler: Voyage-code-3 (hosted) veya nomic-embed-code-v1.5 (self-host), bge-code-v1 yedek
- Seyrek endeks: BM25F ile Tantivy (Rust), simge adına vs gövdeye alan ağırlıklı
- Vektör veritabanı: Hibrit arama ile Qdrant 1.12 veya 50M vektörün altındaki ekipler için pgvector + pgvectorscale
- Parça özet modeli: Claude Haiku 4.5 veya Gemini 2.5 Flash, prompt önbellekli
- Yeniden sıralayıcı: Cohere rerank-3 veya bge-reranker-v2-gemma-2b self-hosted
- Orkestrasyon: Hazmetme için LlamaIndex Workflows, sorgu ajanı için LangGraph
- Sentezleyici: Prompt önbelleği ile Claude Sonnet 4.7 (1M bağlam)
- Simge grafı: İçe aktarma ve çağrı kenarları için Neo4j (yönetilen) veya kuzu (gömülü)
- Gözlemlenebilirlik: Geri getirme + sentez adımı başına Langfuse span'leri

## Build It

1. **Hazmetme gezgini.** Her push kancasında git geçmişini yürütün. Değişen dosyaları toplayın. Her dosya için tree-sitter ile ayrıştırın, tam kaynak aralıklarıyla fonksiyon ve sınıf düğümlerini çıkarın. `{repo, path, start_line, end_line, symbol, body}` parça kayıtlarını yayınlayın.

2. **Parça özetleyici.** Parçaları, sistem önsözünde (preamble) prompt önbelleği ile Haiku 4.5 çağrılarına toplu olarak gönderin. İstem: "Bu fonksiyonu tek bir cümlede özetleyin, genel sözleşmesini ve yan etkilerini adlandırın." Özeti parçanın yanında saklayın.

3. **Gömme havuzu.** İki paralel kuyruk: yoğun (Voyage-code-3 toplu 128) ve özet (aynı model, ancak özet dizesi üzerinde). Vektörleri `{repo, path, start_line, end_line, symbol, kind}` yükü ile Qdrant'a yazın.

4. **BM25 endeksi.** Alan ağırlıklı Tantivy endeksi: simge adı ağırlığı 4, simge gövdesi ağırlığı 1, özet ağırlığı 2. "X adlı fonksiyonu bul" sorgularını "X'i yapan fonksiyonu bul" sorgularının yanında etkinleştirir.

5. **Simge grafı.** Her parça için kenarları kaydedin: içe aktarmalar (bu dosya Z reposundan Y simgesini kullanıyor), çağrılar (bu fonksiyon C sınıfı üzerinde M metotunu çağırıyor), kalıtım. kuzu'da saklayın. Sorgu zamanında repo sınırları arasında geri getirmeyi genişletmek için kullanılır.

6. **Sorgu ajanı.** Üç düğümlü LangGraph. `retrieve` paralel olarak yoğun + BM25 tetikler, (repo, path, symbol) ile tekilleştirir. `rerank` ilk 50 üzerinde çapraz kodlayıcıyı çalıştırır ve ilk 10'u tutar. `synth` Claude Sonnet 4.7'yi yeniden sıralanmış parçalarla bağlamda çağırır, sistem istemini önbelleğe alır, dosya:satır alıntıları gerektirir.

7. **Alıntı zorunluluğu.** Model çıktısını ayrıştırın; `(repo/path:start-end)` bağlayıcısı olmayan her iddia yeniden sorma için işaretlenir veya düşürülür. Yalnızca alıntılanmış yanıtı kullanıcıya döndürün.

8. **Artımlı yeniden indeksleme.** Her webhook'ta simge-düzey farkı hesaplayın. Yalnızca metni değişen parçaları yeniden gömün. İçe aktarmaları değişen parçalar için simge kenarlarını yeniden hesaplayın. 2M-LOC filo için 50-dosyalık bir push'un 60 saniyenin altında yeniden indekslendiğini ölçün.

9. **Eval.** 100 repo-ötesi soruyu altın dosya:satır yanıtlarıyla etiketleyin. MRR@10, nDCG@10, alıntı sadakati (doğrulanabilir bağlayıcılara sahip iddiaların oranı) ve p50/p99 gecikmesini ölçün.

## Use It

```
$ code-rag ask "how is S3 multipart abort wired into our retry budget?"
[retrieve] 12 chunks dense + 7 chunks bm25, 16 unique after dedup
[rerank] top-5 kept (cohere rerank-3)
[synth] claude-sonnet-4.7, cache hit rate 68%, 2.1s
answer:
 Multipart aborts are triggered by `AbortMultipartOnFail` in
 services/uploader/retry.go:122-148, which decrements the per-bucket
 retry budget defined in config/budgets.yaml:34-51 ...
 citations: [services/uploader/retry.go:122-148, config/budgets.yaml:34-51,
 libs/s3client/multipart.ts:44-61]
```

#### Açıklama

Bu örnek bir repo-ötesi sorgunun tam yaşam döngüsünü gösterir. Kullanıcı S3 çok parçalı iptalinin retry bütçesine nasıl bağlandığını sorar. Sistem 12 yoğun ve 7 BM25 parçası getirir, tekilleştirir, Cohere rerank-3 ile ilk 5'e indirir ve Claude Sonnet 4.7 ile önbellek vuru oranı %68'de sentezler. Yanıt her iddiayı dosya ve satır aralığıyla alıntılar; kullanıcı bağlantılara tıklayarak iddiaları doğrulayabilir.

## Ship It

Teslim edilen skill `outputs/skill-codebase-rag.md`. Bir repo korpusu verildiğinde, hazmetme hattını, hibrit endeksi ve sorgu ajanını kurar ve her repo-ötesi soru için alıntılanmış bir yanıt döndürür. Değerlendirme ölçütü:

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Geri getirme kalitesi | 100-soruluk holdout kümesinde MRR@10 ve nDCG@10 |
| 20 | Alıntı sadakati | Doğrulanabilir dosya:satır bağlayıcılarına sahip yanıt iddialarının oranı |
| 20 | Gecikme ve ölçek | Endekslenen korpus boyutunda 10k QPS'de p95 sorgu gecikmesi |
| 20 | Artımlı indeksleme doğruluğu | 50-dosyalık bir commit'te git push'tan aranabilirliğe kadar geçen süre |
| 15 | UX ve yanıt biçimlendirme | Alıntı tıklanabilirliği, parça önizlemeleri, takip kolaylığı |
| **100** | | |

## Exercises

1. Voyage-code-3'ü self-hosted nomic-embed-code ile değiştirin. MRR@10 farkını ölçün. Yeniden sıralama etkinken aradaki farkın kapanıp kapanmadığını raporlayın.

2. Korpusa %20 üretilmiş kod (LLM üretimli boilerplate) enjekte edin ve yeniden değerlendirin. Geri getirme zehirlenmesini gözlemleyin. Yüke bir "generated" (üretilmiş) bayrağı ekleyin ve bu eşleşmelerin ağırlığını düşürün.

3. Korpus boyutunuzda Qdrant hibrit aramayı pgvector + pgvectorscale ile kıyaslayın. Toplu iş boyutu 1'de p99'u raporlayın.

4. Örnekleme tabanlı bir drift (kayma) kontrolü ekleyin: haftalık olarak 100-soruluk eval'i yeniden çalıştırın. MRR@10 düşüşü > %5 olduğunda uyarı verin.

5. Diller arası simge çözümlemesine genişletin: bir Python fonksiyonu gRPC üzerinden bir Go hizmetini çağırıyor. Bunları bağlamak için simge grafını kullanın.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| AST-farkında parçalama | "Fonksiyon-düzey bölünmeler" | Sabit token pencereleri yerine tree-sitter düğüm sınırlarında kod kesmek |
| Hibrit arama | "Yoğun + seyrek" | BM25 ve vektör aramasını paralel çalıştırın, top-k'yı birleştirin, yeniden sıralayın |
| Cross-encoder rerank | "İkinci-aşama sıralama" | Her (sorgu, aday) çiftini birlikte puanlayan, kosinüsden daha doğru model |
| Prompt önbelleği | "Önbelleklenmiş sistem istemi" | 2026 Claude / OpenAI özelliği: tekrar eden önek token'larını %90'a kadar indirimli sayar |
| Simge grafı | "Kod grafı" | Dosyalar ve repolar arasında içe aktarma, çağrı, kalıtım kenarları |
| Alıntı sadakati | "Temellenmiş yanıt oranı" | Kullanıcının bağlayıcıya tıklayıp başvurulan aralığı okuyarak doğrulayabileceği iddiaların oranı |
| Artımlı yeniden indeksleme | "Push'tan aramaya süre" | Git push'tan değişen simgelerin sorgulanabilir olmasına kadar geçen duvar-saati süresi |

## Further Reading

- [Sourcegraph Amp](https://ampcode.com) — üretim seviyesinde repo-ötesi kod zekâsı
- [Sourcegraph Cody RAG architecture](https://sourcegraph.com/blog/how-cody-understands-your-codebase) — bu capstone için referans derin dalış
- [Aider repo-map](https://aider.chat/docs/repomap.html) — tree-sitter sıralanmış repo görünümü
- [Augment Code enterprise graph](https://www.augmentcode.com) — ticari simge-grafı RAG
- [Qdrant hybrid search docs](https://qdrant.tech/documentation/concepts/hybrid-queries/) — referans uygulama
- [Voyage AI code embeddings](https://docs.voyageai.com/docs/embeddings) — Voyage-code-3 detayları
- [Cohere rerank-3](https://docs.cohere.com/reference/rerank) — cross-encoder referansı
- [Pinterest MCP internal search](https://medium.com/pinterest-engineering) — dahili platform referansı
