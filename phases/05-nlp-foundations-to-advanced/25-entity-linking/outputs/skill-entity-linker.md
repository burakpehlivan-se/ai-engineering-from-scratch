---
name: entity-linker
description: Varlık bağlama (entity linking) pipeline'ı tasarlar — KB, aday üretici, anlam ayırıcı, değerlendirme.
version: 1.0.0
phase: 5
lesson: 25
tags: [nlp, entity-linking, knowledge-graph]
---

Bir kullanım senaryosu (alan KB, dil, hacim, gecikme bütçesi) verildiğinde şunu üretirsiniz:

1. Bilgi tabanı. Wikidata / Wikipedia / özel KB. Sürüm tarihi. Yenileme sıklığı.
2. Aday üretici. Diğer ad dizini, embedding veya hibrit. Hedef anma @ K.
3. Anlam ayırıcı. Öncelik + bağlam, embedding-tabanlı, üretken veya LLM-istemli.
4. NIL stratejisi. En yüksek puanda eşik, sınıflandırıcı veya açık NIL adayı.
5. Değerlendirme. Held-out kümesinde anma @ 30, top-1 doğruluk, NIL tespit F1.

Anma-recall baseline'ı olmayan herhangi bir EL (Entity Linking) pipeline'ını reddedin (aday üretiminin doğru varlığı yüzeye çıkardığını bilmeden anlam ayırıcıyı değerlendiremezsiniz). Geçerli KB kimliklerine kısıtlanmış çıktı olmadan LLM-istemli EL kullanan herhangi bir pipeline'ı reddedin. Popülerlik yanlılığının, alan ince ayarı olmadan azınlık varlıklarını (örn. isim çakışmaları) etkilediği sistemleri işaretleyin.
