---
name: multi-agent-team
description: Mimar, paralel kodlayıcılar, gözden geçiren ve test eden ile çok-ajanlı bir yazılım ekibi inşa et; SWE-bench Pro'ya karşı ölç ve bir devir-sonrası (handoff) post-mortemi üret
version: 1.0.0
phase: 19
lesson: 10
tags: [capstone, multi-agent, swe-bench, langgraph, a2a, worktree, roles]
---

Bir GitHub issue URL'si ve bir paralellik düzeyi verildiğinde, birleştirmeye hazır bir PR üreten çok-ajanlı bir yazılım ekibi dağıt. 50 SWE-bench Pro issue'sunda değerlendir ve bir devir-sonrası başarısızlık histogramı yayınla.

İnşa planı:

1. Görev panosu: dosya-tabanlı (veya Redis) JSONL yazı tipi mesaj deposu. Mesaj türleri: plan_request, subtask, diff_ready, review_needed, review_feedback, approved, test_needed, test_passed, test_failed, replan_needed.
2. Mimar (Opus 4.7): issue'yu okur, bir plan yazar, açık arayüzlerle (dokunulan dosyalar, genel fonksiyonlar, test etkisi) alt görevlerin bir DAG'sini yayınlar.
3. N kodlayıcı (Sonnet 4.7): her biri bir alt görev iddia eder, yeni bir `git worktree add` + Daytona sandbox'ı başlatır, bağımsız olarak uygular.
4. Birleştirme koordinatörü: üç-yönlü birleştirme; yalnızca dosya-düzeyinde örtüşmede LLM-aracılı çatışma çözümü.
5. Gözden geçiren (GPT-5.4): birleştirilmiş farkı okur; yazdığı farkları onaylayamaz; ilgili kodlayıcıya yönlendirilen onay veya review_feedback yayar.
6. Test eden (Gemini 2.5 Pro): temiz bir sandbox'ta test paketini çalıştırır; test_passed veya test_failed'ı artefaktlarla yayar.
7. Devir muhasebesi: her çapraz-rol mesajı, yük boyutu ve modelle bir Langfuse span'i olur. Token büyütme = toplam_token / tek_ajan_temel_çizgi_token hesapla.
8. Belirgin bir hata sondası enjekte et (çalıştırmaların %10'u), gözden geçirenin yanlış-onay oranını ölçmek için.
9. 50 SWE-bench Pro issue'su üzerinde çalıştır; pass@1, duvar-saati vs tek-ajan temel çizgisi, rol başına token dökümü, devir-sonrası başarısızlık histogramı yayınla.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | SWE-bench Pro pass@1 | 50-issue alt kümesi pass@1 |
| 20 | Paralel hızlanma | Tek-ajan temel çizgisine karşı duvar-saati |
| 20 | İnceleme kalitesi | Enjekte edilen hata sondasında yanlış-onay oranı |
| 20 | Token verimliliği | Tek-ajan'a karşı çözülen issue başına toplam token |
| 15 | Koordinasyon mühendisliği | Birleştirme-çatışması çözümü, devir-sonrası başarısızlık histogramı |

Kesin redler:

- Yazdığı veya önerdiği farkları onaylayabilen gözden geçiren. Sert kısıtlama.
- Eşleşmiş tek-ajan temel çizgi çalıştırması olmadan raporlar. Çok-ajan *dolar başına* kazanmalı, yalnızca pass@1'de değil.
- Mesajların serbest-biçim dizeler olduğu görev panoları, yazı tipi A2A mesajları yerine.
- Çakışan farkları yeniden planlamaya geri yönlendirmek yerine sessizce düşüren birleştirme koordinatörleri.

Ret kuralları:

- Rol başına bütçe tavanları olmadan (token + dolar) çalıştırmayı reddet.
- Test eden temiz bir sandbox'ta doğrulamadan bir PR açmayı reddet.
- Tek bir çalıştırmada kodlayıcıları 8'in üzerine ölçeklendirmeyi reddet. Koordinasyon yükü bundan sonra baskın olur.

Çıktı: Görev panosu + rol işçilerini, 50-issue'lu SWE-bench Pro çalıştırma günlüğünü, eşleşmiş tek-ajan temel çizgi çalıştırmasını, rol-etiketli span'leri ve rol başına token dökümleri olan bir Langfuse panosunu, enjekte edilen hata sondası raporunu ve en sık bozulan üç devri ve her birini azaltan mesaj-şeması veya istem değişikliğini adlandıran bir post-mortemi içeren bir depo.
