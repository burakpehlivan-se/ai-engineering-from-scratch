---
name: issue-to-pr
description: Bir bulut sandbox'ında çalışan, derlemeyi yeniden üreten, testleri doğrulayan ve sıkı depo başına bütçelerle gözden geçirmeye hazır PR'lar açan asenkron bir GitHub issue-to-PR ajanı inşa et
version: 1.0.0
phase: 19
lesson: 16
tags: [capstone, async-agent, github, fargate, daytona, swe-bench, budget, safety]
---

`@agent fix this` etiketli issue'ları olan bir GitHub deposu verildiğinde, etiketlenen her issue'yu kapsamlı kimlik bilgileri ve sınırlı maliyetle gözden geçirmeye hazır bir PR'ye dönüştüren kendi barındırılan bir bulut ajanı gönder.

İnşa planı:

1. İnce-taneli belirteçli GitHub App: issue'lar rw, PR'lar yazma, içerikler rw, iş akışları okuma. Zorla-itme yok. Ana üzerinde dal koruması doğrudan yazmaları engeller.
2. Webhook alıcı (Lambda veya Fly.io) etiket / PR-yorum olaylarını filtreler ve SQS'ye kuyruğa alır.
3. Dağıtıcı, depo başına günlük $ ve PR-sayısı tavanlarını zorlar; izin verilen her iş için bir ECS Fargate görevi başlatır.
4. Ortam çıkarımı: dil + paket yöneticisi + çalışma zamanını depo içeriğinden tespit et. Yoksa bir Dockerfile'ı uçucu olarak sentezle.
5. Görev başına Daytona veya E2B sandbox. Depoyu yeni bir `git worktree` + ajan dalına klonla.
6. Ajan döngüsü (Claude Opus 4.7 veya GPT-5.4-Codex üzerinde mini-swe-agent veya SWE-agent v2). Araçlar: ripgrep, tree-sitter depo-haritası, read_file, edit_file, run_tests, git. Kapaklar: 20 dolar, 30 tur, 30 dakika.
7. Doğrula: sandbox'ta tam CI; jacoco / coverage.py ile kapsam deltası; delta < -%2 ise `needs-review` etiketle; CI kırmızıysa dur.
8. Gerekçe, fark özeti, iz URL'si, maliyet, turlarla GitHub API üzerinden PR aç.
9. Gözlemlenebilirlik: PR başına Langfuse izi; sırlar için günlük temizleme; depo başına bütçe panosu.
10. 30 tohumlu dahili issue üzerinde değerlendir; üç issue paylaşılan alt kümede Cursor Background Agents ve AWS Remote SWE Agents ile karşılaştır.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | 30 issue üzerinde geçme oranı | Uçtan uca başarı (CI yeşil + kapsam OK) |
| 20 | PR kalitesi | Fark boyutu, kapsam deltası, stil uyumu |
| 20 | Çözülen issue başına maliyet ve gecikme | $/PR ve duvar-saati/PR |
| 20 | Güvenlik | Kapsamlı belirteç, depo başına bütçe, zorla-itme yok, kimlik bilgisi hijyeni |
| 15 | Operatör UX | Gerekçe yorumları, yeniden deneme kolaylığı, @-bahsetme takibi |

Kesin redler:

- Zorla-itme yapabilen herhangi bir ajan. Sert dışlama.
- Bütçe kontrollerini atlayan dağıtıcılar. Kontrolden çıkan döngüler klasik başarısızlıktır.
- Sandbox'ta tam CI geçmeden açılan PR'lar.
- Sansürlenmemiş belirteçler veya PII içeren iz arşivleri.

Ret kuralları:

- Ana üzerinde dal koruması olmadan kurmayı reddet.
- Depo başına günlük bütçe (dolar ve PR sayısı) olmadan çalıştırmayı reddet.
- Başarısız çalıştırmaları otomatik olarak yeniden denemeyi reddet; tüm yeniden denemeler insan etiket yeniden uygulaması gerektirir.

Çıktı: GitHub App'i, webhook alıcıyı, dağıtıcı + bütçe defterini, Fargate görev tanımını, sandbox yaşam-döngüsü yöneticisini, mini-swe-agent döngüsünü, 30-issue değerlendirme çalıştırmasını, Cursor Background Agents ve AWS Remote SWE Agents ile yan yana karşılaştırmayı ve en önemli üç derleme-çıkarımı başarısızlığını ve her birini azaltan Dockerfile-sentez değişikliğini adlandıran bir yazıyı içeren bir depo.
