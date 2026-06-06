---
name: migration-agent
description: Belirleyici tarifleri bir ajan yedek döngüsüyle birleştiren, MigrationBench'i geçen ve bir başarısızlık taksonomisi yayınlayan depo-düzeyinde bir kod taşıma ajanı inşa et
version: 1.0.0
phase: 19
lesson: 09
tags: [capstone, code-migration, openrewrite, libcst, migrationbench, agent, sandbox]
---

Bir Java 8 veya Python 2 deposu verildiğinde, yeşil bir test paketi ve minimum kapsam regresyonu ile taşınmış bir dal (Java 17 veya Python 3.12'ye) üret. 50-depoluk MigrationBench alt kümesinde değerlendir.

İnşa planı:

1. Belirleyici geçiş: OpenRewrite (Java) veya libcst (Python) önce mekanik yeniden yazımları çalıştırır. Temiz bir farkla "tarif" commit'i olarak kaydet.
2. Daytona sandbox: hedef çalışma zamanı önceden yüklenmiş; dal başına derleme; salt-okunur kaynak bağlama.
3. Ajan döngüsü: Claude Opus 4.7 + GPT-5.4-Codex üzerinde LangGraph veya OpenAI Agents SDK. Araçlar: `run_build`, `read_file`, `edit_file`, `run_test`, `git_diff`. Başarısızlığı sınıflandır (bağımlılık, sözdizimi, test, derleme aracı), hedefli düzeltme uygula, yeniden çalıştır.
4. Bütçe kapakları: 30 dakika, 8 dolar, 20 tur. Herhangi birini aşma durdurur ve mevcut farkla `budget_exhausted` altında dosyalar.
5. Test + kapsam geçidi: derleme yeşil sonra testler yeşil; kapsam %2'den fazla düşmemelidir.
6. Tarif-commit + ajan commitleri + özet yorum ile PR aç.
7. Başarısızlık taksonomisi: depo başına etiket `{dep_upgrade_required, build_tool_drift, custom_annotation, test_flake, syntax_edge_case, budget_exhausted, coverage_regression}`.
8. MigrationBench üzerinde 50-depoluk çalıştırma; sınıf başına geçme oranı, depo başına maliyet ve kapsam-koruması yayınla; salt belirleyici temel çizgiyle karşılaştır.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | MigrationBench geçme oranı | 50-depoluk alt küme pass@1 |
| 20 | Test kapsamı koruması | Temel dala karşı ortalama kapsam deltası |
| 20 | Taşınan depo başına maliyet | Geçen çalıştırmalarda ortalama $/depo |
| 20 | Ajan / belirleyici araç entegrasyonu | OpenRewrite vs ajan tarafından işlenen düzeltmelerin kesri |
| 15 | Başarısızlık analizi yazısı | Örneklerle taksonomi tamlığı |

Kesin redler:

- Belirleyici geçişi atlayan hatlar. OpenRewrite mekanik %70-80'ini herhangi bir ajandan daha ucuza ve güvenilir şekilde halleder.
- %2 üzerinde kapsam regresyonlarını geçen olarak ele alma.
- Mekanik ve ajan-yazarlı değişiklikleri tek bir commit'te birleştiren PR'lar. Ayırmalıdır.
- Aynı 50 depoda eşleşmiş salt-belirleyici temel çizgi olmadan geçme oranı raporlama.

Ret kuralları:

- Temelin üzerine taşınmış bir dalı zorla-itmeyi (force-push) reddet. Her zaman yeni dal + PR.
- CI'sı sandbox'ta yeşile dönmemiş bir PR'ı açmayı reddet.
- Kurumsal depolarda açık değiştirme lisansı olmadan çalıştırmayı reddet.

Çıktı: İki katmanlı taşıma hattını, 50-depoluk MigrationBench çalıştırma günlüklerini, başarısızlık taksonomisi panosunu, eşleşmiş salt-belirleyici temel çizgi çalıştırmasını ve en yaygın üç başarısızlık sınıfını ve her birini ortadan kaldıracak tarif değişikliğini açıklayan bir yazıyı içeren bir depo.
