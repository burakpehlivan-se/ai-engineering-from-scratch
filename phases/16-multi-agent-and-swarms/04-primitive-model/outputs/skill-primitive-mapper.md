---
name: primitive-mapper
description: Herhangi bir çok-agent'lı framework'ü veya kod tabanını dört ilkel eksenine (agent, devir, paylaşılan durum, orkestratör) eşleyin.
version: 1.0.0
phase: 16
lesson: 04
tags: [multi-agent, primitives, framework-comparison, architecture]
---

Bir çok-agent'lı framework (veya bir framework kullanan bir kod tabanı) verildiğinde, okuyucunun framework'ü tek paragrafta anlayabilmesi için dört-ilkel eşlemesini üretin.

Üretin:

1. **Agent tanımı.** Bir agent nasıl oluşturulur? Hangi parametrelerle? Hangi durumu taşır? Tam sınıfı veya fabrikayı adlandırın.
2. **Devir (handoff) mekanizması.** Üç devir örüntüsünden hangisini kullanıyor — fonksiyon dönüşü, grafik kenarı veya konuşmacı seçimi? Hibrit ise, hangisi birincil? Bir devri tetikleyen minimum kodu gösterin.
3. **Paylaşılan durum modeli.** Tam mesaj havuzu mu yoksa öngörülen görünüm mü? Bellek içi mi yoksa dayanıklı mı (checkpoint'li)? Eşzamanlı yazarlar için thread-safe mi? Çakışmaları kim çözüyor?
4. **Orkestratör türü.** Statik, LLM-seçimli, devir-tahrikli veya kuyruk-tahrikli? LLM-seçimli ise, varsayılan olarak hangi model? Statik ise, grafik döngüsel mi yoksa DAG mı?
5. **Eksenler-arası ödünleşimler.** Her biri için bir cümle: determinizm, ölçeklenebilirlik tavanı, hata ayıklanabilirlik, tipik başarısızlık modu.

Keskin redler:

- Dört ilkele indirgenemediğini göstermeden bir soyutlamanın "yeni" olduğunu iddia eden herhangi bir eşleme. İndirgeyemiyorsanız, beşinci bir ilkel uydurmak yerine boşluğu kesin olarak adlandırın.
- Yalnızca pazarlama dokümanlarını gösteren framework karşılaştırmaları. Her zaman framework'ün reposundan veya resmi cookbook'tan somut bir kod örneği gösterin.
- Framework'ün hangi ilkeli optimize ettiğini belirtmeden "X framework'ü agent'lar için daha iyi" gibi ifadeler.

Ret kuralları:

- Framework kapalı-kaynak ise ve genel dokümanlar agent-devir-durum-orkestratör yüzeyini açığa çıkarmıyorsa, dahili bilgiler olmadan eşlemenin mümkün olmadığını belirtin.
- Kullanıcı bir kod tabanı sağlıyor ancak framework yok (elle-yazılmış agent'lar), bunun yerine özel uygulamayı eşleyin ve hangi ilkelin yetersiz tasarlandığını işaretleyin.
- Framework 2024'ten eskiyse (orijinal AutoGen v0.2, Swarm-öncesi) ve artık sürdürülmüyorsa, halefinin eşlemeyi koruyup korumadığına dair tek satırlık bir not ekleyin.

Çıktı: Tek sayfalık framework özeti. Tek cümlelik bir özetle başlayın ("Framework X, devri grafik kenarı olarak sabitler ve paylaşılan durumu bir reducer (indirgeyici) aracılığıyla sunar."), sonra yukarıdaki beş bölüm, sonra bu framework'ün ilkellerinin en iyi hangi production projesine uyduğunu adlandıran bir kapanış paragrafı.
