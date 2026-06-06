---
name: production-rag
description: Rol + yargı alanı filtreleme, istem önbelleği, koruma setleri ve canlı sapma izleme ile düzenlenmiş-alanda bir RAG sohbet botu dağıt
version: 1.0.0
phase: 19
lesson: 08
tags: [capstone, rag, chatbot, regulated, llama-guard, nemo-guardrails, ragas, langfuse]
---

Düzenlenmiş alan derlemi (yasal sözleşmeler, klinik araştırma protokolleri, sigorta poliçeleri veya benzeri) verildiğinde, doğrulanabilir alıntılarla yanıt veren, rol ve yargı alanı erişim politikalarına saygı gösteren ve sapma için izlenen bir sohbet botu dağıt.

İnşa planı:

1. Derlemi docling veya Unstructured ile ayrıştır; görsel olarak zengin belgeleri ColPali üzerinden yönlendir. Parçaları rol ve yargı alanı etiketleriyle yay.
2. Yoğun (Voyage-3 veya Nomic-embed-v2) indeksini pgvector + pgvectorscale'a; seyrek BM25'i Tantivy üzerinden indeksle.
3. LangGraph konuşma ajanını bağla: retrieve (rol + yargı alanına göre filtrele, hibrit yoğun+BM25, karşılıklı sıra birleştirme), rerank (bge-reranker-v2-gemma-2b veya Voyage rerank-2), synth (istem önbceği ile Claude Sonnet 4.7).
4. Kararlı öneklerle istemleri kur: sistem önsözü -> politika bloğu -> yeniden sıralanmış bağlam -> kullanıcı sorgusu. %60-80 istem-önbellek isabet oranını hedefle.
5. Koruma setleri: girdi ve çıktıda Llama Guard 4, alan-dışı ve politika-yasaklı sorular için NeMo Guardrails v0.12 rayları, çıktıda Presidio PII temizleme, alıntı zorlama son-filtresi.
6. (yanıt, alıntılar) ile 200 soruluk uzman-etiketli altın küme inşa et. Tam-alıntı eşleşme, yanıt doğruluğu, RAGAS sadakati üzerinde puanla.
7. 50-istemlik bir kırmızı takım inşa et (PAIR, TAP, PII çıkarma, alan-dışı, çapraz-yargı alanı sondaları).
8. Erişim nDCG'sini ve alıntı sadakatini haftalık olarak izleyen Arize Phoenix sapma panosu; %5 düşüşte uyar.
9. Langfuse maliyet raporu: istem-önbellek isabet oranı, sorgu başına token, aşamaya göre sorgu başına $.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | RAGAS sadakati + yanıt ilgililiği | 200 soruluk altın küme üzerinde çevrimiçi puanlar |
| 20 | Alıntı doğruluğu | Doğrulanabilir kaynak çapalarına sahip yanıtların kesri |
| 20 | Koruma seti kapsamı | Llama Guard 4 geçme oranı + hapis kırma paketi sonucu |
| 20 | Maliyet / gecikme mühendisliği | İstem-önbellek isabet oranı, p95 gecikme, sorgu başına $ |
| 15 | Sapma izleme panosu | Haftalık erişim kalitesi trendiyle canlı Phoenix panosu |

Kesin redler:

- Çapraz-yargı alanı verisi sızdıran herhangi bir sohbet botu. Rol+yargı alanı filtreleme, erişimden sonra değil, önce zorlanmalıdır.
- Önbellek öneklerini bozan (sistem ve bağlam arasında politikayı yeniden sıralayan) sentez istemleri. Önbellek ekonomisini yok eder.
- Kaydedilmiş kırmızı takım çalıştırmaları olmadan koruma seti yapılandırmaları.
- Alıntıları olmayan yanıtlar; doğrulanabilir çapaları olmayan alıntılar.

Ret kuralları:

- Her parça üzerinde yargı alanı etiketleri olmadan düzenlenmiş bir alanda dağıtmayı reddet.
- Uzman-etiketli altın küme soruları üzerinde erişimi eğitmeyi reddet. Kirlenme, değerlendirme güvenilirliğini yok eder.
- README'de açık bir SOC2/HIPAA/GDPR uygulanabilirlik matrisi olmadan "uyumlu" olduğunu iddia etmeyi reddet.

Çıktı: Alım hattını, LangGraph konuşma ajanını, 200 soruluk altın kümeyi, 50-istemlik kırmızı takımı, Phoenix sapma panosunu, Langfuse maliyet panosunu ve gözlemlediğiniz en önemli üç alıntı-kırılma kalıbını ve her biri için erişim veya istem düzeltmesini adlandıran bir yazıyı içeren bir depo.
