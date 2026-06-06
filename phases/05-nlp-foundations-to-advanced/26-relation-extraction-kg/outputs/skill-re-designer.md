---
name: re-designer
description: Köken (provenance) ve kanonizasyon ile bir ilişki çıkarma (relation extraction) pipeline'ı tasarlar.
version: 1.0.0
phase: 5
lesson: 26
tags: [nlp, relation-extraction, knowledge-graph]
---

Bir derlem (alan, dil, hacim) ve aşağı akış kullanım (KG-RAG, analitik, uyumluluk) verildiğinde şunu üretirsiniz:

1. Çıkarıcı. Örüntü tabanlı / denetimli / LLM / AEVS hibrit. Nedeni precision ve recall hedefine bağlı.
2. Ontoloji. Kapalı özellik listesi (Wikidata / alan) veya kanonizasyon geçişli açık IE.
3. Köken (provenance). Her üçlü kaynak karakter aralığını + belge kimliğini taşır. Denetim için vazgeçilmez.
4. Birleştirme stratejisi. Kanonik varlık kimliği + ilişki kimliği + zamansal niteleyiciler; tekilleştirme politikası.
5. Değerlendirme. 200 elle etiketlenmiş üçlü üzerinde precision / recall + LLM ile çıkarılan örnekte halüsinasyon oranı.

Span doğrulaması olmadan herhangi bir LLM tabanlı RE pipeline'ını reddedin (kaynak kökeni). Kanonizasyon olmadan açık IE çıktısının üretim grafına akmasını reddedin. Zaman sınırlı ilişkilerde (işveren, eş, pozisyon) zamansal niteleyicisi olmayan pipeline'ları işaretleyin.
